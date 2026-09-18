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

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


parser = LinkParser()
try:
    parser.feed(Path("index.html").read_text(encoding="utf-8"))
except (OSError, UnicodeError) as error:
    fail(f"index.html: {error}")

if not parser.links:
    fail("index.html contains no routes")

repositories: set[str] = set()
pages: set[str] = set()
for link in parser.links:
    parsed = urlparse(link)
    if parsed.scheme:
        if parsed.scheme != "https":
            fail(f"non-HTTPS route: {link}")
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
