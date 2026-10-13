"""Offline regression tests for the root portal's route allowlist."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
MANIFESTS = (
    "aift.repo.json", ".aift/repo.json", ".aift/capabilities.json",
    ".aift/events.json", ".aift/manual.json", ".aift/services.json",
)
BASE_LINKS = (
    'https://github.com/AIFreedomTrustFederation/AIFT-Forge',
    'https://aifreedomtrustfederation.github.io/AIFT-Forge/',
)


class RouteIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        command = self.root / '.aift/commands/verify.sh'
        command.parent.mkdir(parents=True)
        shutil.copyfile(REPO / '.aift/commands/verify.sh', command)
        for filename in MANIFESTS:
            target = self.root / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps({"repo": "aifreedomtrustfederation.github.io"}))

    def verify(self, *links):
        (self.root / 'index.html').write_text(''.join(f'<a href="{link}">route</a>' for link in links))
        return subprocess.run(
            ['sh', '.aift/commands/verify.sh'], cwd=self.root,
            text=True, capture_output=True, check=False,
        )

    def test_canonical_pair_passes(self):
        self.assertEqual(self.verify(*BASE_LINKS).returncode, 0)

    def test_third_party_destination_fails(self):
        result = self.verify(*BASE_LINKS, 'https://untrusted.example/phishing')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unapproved external route', result.stderr)

    def test_other_organization_repository_fails(self):
        result = self.verify(*BASE_LINKS, 'https://github.com/OtherOrg/Impersonation')
        self.assertNotEqual(result.returncode, 0)

    def test_nested_github_path_fails(self):
        result = self.verify(*BASE_LINKS, 'https://github.com/AIFreedomTrustFederation/AIFT-Forge/issues')
        self.assertNotEqual(result.returncode, 0)

    def test_nested_pages_path_fails(self):
        result = self.verify(*BASE_LINKS, 'https://aifreedomtrustfederation.github.io/AIFT-Forge/redirect')
        self.assertNotEqual(result.returncode, 0)

    def test_scheme_relative_external_route_fails(self):
        result = self.verify(*BASE_LINKS, '//untrusted.example/phishing')
        self.assertNotEqual(result.returncode, 0)

    def test_encoded_project_path_fails(self):
        result = self.verify(*BASE_LINKS, 'https://github.com/AIFreedomTrustFederation/%2e%2e')
        self.assertNotEqual(result.returncode, 0)

    def test_external_route_with_query_fails(self):
        result = self.verify(*BASE_LINKS, 'https://github.com/AIFreedomTrustFederation/AIFT-Forge?redirect=evil')
        self.assertNotEqual(result.returncode, 0)

    def test_unpaired_route_still_fails(self):
        result = self.verify(BASE_LINKS[0])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('route pairs differ', result.stderr)


if __name__ == '__main__':
    unittest.main()
