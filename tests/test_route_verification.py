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

    def test_valid_local_route_passes(self):
        (self.root / "docs").mkdir()
        (self.root / "docs/info.html").write_text("ok", encoding="utf-8")
        result = self.verify('<a href="docs/info.html">Local</a>')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
