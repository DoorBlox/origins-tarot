"""Arcane artifact discovery: do not mistake the legacy main build for Rev3."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ArcaneArtifactDiscoveryTests(unittest.TestCase):
    def test_arcane_workflow_builds_on_main_push(self):
        flow = (ROOT / ".github/workflows/arcane-full.yml").read_text()
        self.assertIn("      - main\n", flow)
        self.assertIn("      - 'feat/arcane-rev3-*'", flow)
        self.assertIn("python3 -m arcane_rev3.full_build", flow)

    def test_build_sha_is_packaged_with_explicit_dev_artifact(self):
        flow = (ROOT / ".github/workflows/arcane-full.yml").read_text()
        self.assertIn("output/ARCANE_REV3_BUILD_SHA.txt", flow)
        self.assertIn('"${GITHUB_SHA}"', flow)
        self.assertIn("tarot-arcane-rev3-22-origin-dev-not-production", flow)
        self.assertNotIn("name: tarot-club-datapacks", flow)


if __name__ == "__main__":
    unittest.main()
