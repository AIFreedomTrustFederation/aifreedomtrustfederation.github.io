"""Regression tests for the dependency-free federation route verifier."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / ".aift/commands/verify.sh"
MANIFESTS = (
    "aift.repo.json",
    ".aift/repo.json",
    ".aift/capabilities.json",
    ".aift/events.json",
    ".aift/manual.json",
    ".aift/services.json",
)
VALID_LINKS = (
    '<a href="https://github.com/AIFreedomTrustFederation/VPS">Repository</a>',
    '<a href="https://aifreedomtrustfederation.github.io/VPS/">Project</a>',
)


class RouteVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        verifier = self.root / ".aift/commands/verify.sh"
        verifier.parent.mkdir(parents=True)
        shutil.copyfile(VERIFIER, verifier)
        for name in MANIFESTS:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"repo": "aifreedomtrustfederation.github.io"}), encoding="utf-8")

    def verify(self, *links):
        (self.root / "index.html").write_text("<html><body>" + "\n".join(VALID_LINKS + links) + "</body></html>", encoding="utf-8")
        return subprocess.run(["sh", ".aift/commands/verify.sh"], cwd=self.root, capture_output=True, text=True, timeout=10)

    def test_valid_https_pairs_pass(self):
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("1 paired public project routes", result.stdout)

    def test_protocol_relative_external_url_fails(self):
        result = self.verify('<a href="//attacker.example">Unverified external destination</a>')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("protocol-relative", result.stderr)

    def test_protocol_relative_url_with_query_fails(self):
        result = self.verify('<a href="//attacker.example?token=abc">External</a>')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_https_without_authority_fails(self):
        result = self.verify('<a href="https:relative">Malformed HTTPS</a>')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_non_https_url_fails(self):
        result = self.verify('<a href="http://attacker.example">Insecure</a>')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_local_path_traversal_fails(self):
        result = self.verify('<a href="../outside">Traversal</a>')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_page_pair_fails(self):
        result = self.verify('<a href="https://github.com/AIFreedomTrustFederation/Another">Another</a>')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_external_base_href_cannot_retarget_local_routes(self):
        # A <base> in <head> changes how browsers resolve relative hrefs.
        (self.root / "docs").mkdir()
        (self.root / "docs/info.html").write_text("ok", encoding="utf-8")
        html = (
            '<html><head><base href="https://untrusted.example/"></head><body>'
            + "\n".join(VALID_LINKS)
            + '<a href="docs/info.html">Local</a></body></html>'
        )
        (self.root / "index.html").write_text(html, encoding="utf-8")
        result = subprocess.run(["sh", ".aift/commands/verify.sh"], cwd=self.root, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("base href", result.stderr)

    def test_protocol_relative_base_href_is_rejected(self):
        result = self.verify('<base href="//untrusted.example/">')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("base href", result.stderr)

    def test_base_target_without_href_preserves_routes(self):
        result = self.verify('<base target="_self">')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_valid_local_route_passes(self):
        (self.root / "docs").mkdir()
        (self.root / "docs/info.html").write_text("ok", encoding="utf-8")
        result = self.verify('<a href="docs/info.html">Local</a>')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_crossed_card_destinations_fail_even_when_global_sets_match(self):
        html = """<html><body>
        <article><a href="https://github.com/AIFreedomTrustFederation/VPS">Repository</a>
        <a href="https://aifreedomtrustfederation.github.io/booksmith-ai/">Project</a></article>
        <article><a href="https://github.com/AIFreedomTrustFederation/booksmith-ai">Repository</a>
        <a href="https://aifreedomtrustfederation.github.io/VPS/">Project</a></article>
        </body></html>"""
        (self.root / "index.html").write_text(html, encoding="utf-8")
        result = subprocess.run(["sh", ".aift/commands/verify.sh"], cwd=self.root, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("article 1 route pair mismatch", result.stderr)

    def test_missing_card_destination_fails_despite_global_pair(self):
        html = """<html><body>
        <article><a href="https://github.com/AIFreedomTrustFederation/VPS">Repository</a></article>
        <article><a href="https://aifreedomtrustfederation.github.io/VPS/">Project</a></article>
        </body></html>"""
        (self.root / "index.html").write_text(html, encoding="utf-8")
        result = subprocess.run(["sh", ".aift/commands/verify.sh"], cwd=self.root, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("article 1 route pair mismatch", result.stderr)

    def test_empty_article_card_fails_despite_valid_global_pair(self):
        html = """<html><body>
        <article><a href="https://github.com/AIFreedomTrustFederation/VPS">Repository</a>
        <a href="https://aifreedomtrustfederation.github.io/VPS/">Project</a></article>
        <article><h2>Broken project</h2><p>No destinations</p></article>
        </body></html>"""
        (self.root / "index.html").write_text(html, encoding="utf-8")
        result = subprocess.run(["sh", ".aift/commands/verify.sh"], cwd=self.root, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("article 2 route pair mismatch", result.stderr)

    def test_matching_card_destinations_pass(self):
        html = """<html><body>
        <article><a href="https://github.com/AIFreedomTrustFederation/VPS">Repository</a>
        <a href="https://aifreedomtrustfederation.github.io/VPS/">Project</a></article>
        <article><a href="https://github.com/AIFreedomTrustFederation/booksmith-ai">Repository</a>
        <a href="https://aifreedomtrustfederation.github.io/booksmith-ai/">Project</a>
        <a href="https://docs.example.org/help">Documentation</a></article>
        </body></html>"""
        (self.root / "index.html").write_text(html, encoding="utf-8")
        result = subprocess.run(["sh", ".aift/commands/verify.sh"], cwd=self.root, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("2 paired public project routes", result.stdout)


if __name__ == "__main__":
    unittest.main()
