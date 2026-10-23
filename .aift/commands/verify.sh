#!/usr/bin/env sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$repo_root"

python3 - <<'PY'
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

ROOT = Path.cwd().resolve()
EXPECTED_REPO = "aifreedomtrustfederation.github.io"
MANIFESTS = (
    Path("aift.repo.json"),
    Path(".aift/repo.json"),
    Path(".aift/capabilities.json"),
    Path(".aift/events.json"),
    Path(".aift/manual.json"),
    Path(".aift/services.json"),
)


def fail(message: str) -> None:
    raise SystemExit(f"verification failed: {message}")


for path in MANIFESTS:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"{path}: {error}")
    identity = manifest.get("repo", manifest.get("name"))
    if identity != EXPECTED_REPO:
        fail(f"{path}: repository identity is {identity!r}")


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.base_hrefs: list[str | None] = []
        self.active_content: list[str] = []
        self.cards: list[list[str]] = []
        self.active_card: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        # The root index is a static router: executable content can override
        # otherwise valid hrefs without appearing in the link inventory.
        if tag == "script":
            self.active_content.append("script element")
        if any(name.startswith("on") for name, _ in attrs):
            self.active_content.append("inline event handler")
        if tag == "meta" and (attributes.get("http-equiv") or "").strip().lower() == "refresh":
            self.active_content.append("meta refresh")
        if tag == "article":
            self.active_card = []
            self.cards.append(self.active_card)
        elif tag == "base":
            attributes = dict(attrs)
            if "href" in attributes:
                self.base_hrefs.append(attributes["href"])
        elif tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)
                if self.active_card is not None:
                    self.active_card.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == "article":
            self.active_card = None


parser = LinkParser()
try:
    parser.feed(Path("index.html").read_text(encoding="utf-8"))
except (OSError, UnicodeError) as error:
    fail(f"index.html: {error}")

if parser.base_hrefs:
    fail("index.html contains a base href that overrides validated local routes")

if parser.active_content:
    fail("index.html contains active navigation that bypasses validated routes: "
         + ", ".join(sorted(set(parser.active_content))))

if not parser.links:
    fail("index.html contains no routes")

repositories: set[str] = set()
pages: set[str] = set()
for link in parser.links:
    parsed = urlparse(link)
    if parsed.username is not None or parsed.password is not None:
        fail(f"credentials embedded in route: {link}")
    if parsed.netloc and not parsed.scheme:
        fail(f"protocol-relative route is not allowed: {link}")
    if parsed.scheme:
        if parsed.scheme != "https":
            fail(f"non-HTTPS route: {link}")
        if not parsed.netloc:
            fail(f"HTTPS route has no host: {link}")
        if parsed.netloc == "github.com":
            parts = [part for part in parsed.path.split("/") if part]
            if len(parts) == 2 and parts[0] == "AIFreedomTrustFederation":
                repositories.add(parts[1])
        elif parsed.netloc == "aifreedomtrustfederation.github.io":
            parts = [part for part in parsed.path.split("/") if part]
            if parts:
                pages.add(parts[0])
        continue

    path = PurePosixPath(parsed.path)
    if path.is_absolute() or ".." in path.parts:
        fail(f"unsafe local route: {link}")
    target = (ROOT / path).resolve()
    if ROOT not in target.parents and target != ROOT:
        fail(f"route escapes repository: {link}")
    if not target.exists():
        fail(f"missing local route: {link}")

# Global route-set equality cannot detect links swapped between cards.
# Verify each project card directs readers to its own repository and Pages site.
for card_number, card_links in enumerate(parser.cards, start=1):
    card_repositories: list[str] = []
    card_pages: list[str] = []
    for link in card_links:
        parsed = urlparse(link)
        parts = [part for part in parsed.path.split("/") if part]
        if parsed.scheme != "https":
            continue  # The global validator rejects unsafe schemes and local paths.
        if parsed.netloc == "github.com" and len(parts) == 2 and parts[0] == "AIFreedomTrustFederation":
            card_repositories.append(parts[1])
        elif parsed.netloc == "aifreedomtrustfederation.github.io" and parts:
            card_pages.append(parts[0])
    if len(card_repositories) != 1 or len(card_pages) != 1 or card_repositories[0] != card_pages[0]:
        fail(
            f"article {card_number} route pair mismatch: "
            f"repositories={card_repositories}, Pages={card_pages}"
        )

if repositories != pages:
    missing_pages = sorted(repositories - pages)
    missing_repositories = sorted(pages - repositories)
    fail(
        "route pairs differ; "
        f"missing Pages routes={missing_pages}, "
        f"missing repository routes={missing_repositories}"
    )

print(
    f"Verified {len(MANIFESTS)} federation manifests and "
    f"{len(repositories)} paired public project routes."
)
PY

find . -type f -name '*.sh' -not -path './.git/*' -exec sh -n {} +
