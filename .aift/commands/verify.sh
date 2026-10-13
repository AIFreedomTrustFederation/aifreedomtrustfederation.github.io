#!/usr/bin/env sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$repo_root"

python3 - <<'PY'
from html.parser import HTMLParser
import json
import re
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
    if parsed.username is not None or parsed.password is not None:
        fail(f"credentials embedded in route: {link}")
    if parsed.scheme or parsed.netloc:
        if parsed.scheme != "https":
            fail(f"non-HTTPS route: {link}")
        if parsed.netloc not in ("github.com", "aifreedomtrustfederation.github.io"):
            fail(f"unapproved external route: {link}")
        if parsed.query or parsed.fragment:
            fail(f"non-canonical route: {link}")
        parts = [part for part in parsed.path.split("/") if part]
        name = parts[-1] if parts else ""
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", name) or name in (".", ".."):
            fail(f"invalid project name in route: {link}")
        if parsed.netloc == "github.com":
            if (len(parts) != 2 or parts[0] != "AIFreedomTrustFederation"
                    or parsed.path not in (f"/AIFreedomTrustFederation/{name}",
                                           f"/AIFreedomTrustFederation/{name}/")):
                fail(f"unexpected repository route: {link}")
            repositories.add(name)
        else:
            if len(parts) != 1 or parsed.path not in (f"/{name}", f"/{name}/"):
                fail(f"unexpected Pages route: {link}")
            pages.add(name)
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
