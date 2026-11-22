"""Navigation integrity and coverage for the generated player wiki."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from progression.catalog import CARDS

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "player"


class PlayerWikiTests(unittest.TestCase):
    def test_22_pathways_have_all_normal_sequences_and_weakness(self):
        for card in CARDS:
            path = DOCS / "pathways" / (card["slug"] + ".md")
            with self.subTest(pathway=card["slug"]):
                self.assertTrue(path.is_file(), path)
                body = path.read_text(encoding="utf-8")
                self.assertIn("## Permanent weakness", body)
                self.assertIn("## Table of contents", body)
                self.assertIn("**What it does:**", body)
                self.assertIn("**How to use:**", body)
                self.assertIn("a_focus_menu", body)
                self.assertIn("[All pathways](../PATHWAYS.md)", body)
                for seq in range(2, 10):
                    self.assertIn(f"## Sequence {seq}", body)
                self.assertNotIn("PARTIAL SOURCE", body)
                self.assertNotIn("power_id:", body)

    def test_player_guides_exist_and_use_real_crosslinks(self):
        for name in ("README.md", "START_HERE.md", "CONTROLS.md",
                     "ASCENSION.md", "PATHWAYS.md", "TROUBLESHOOTING.md",
                     "SERVER_SETUP.md"):
            with self.subTest(guide=name):
                page = DOCS / name
                self.assertTrue(page.is_file())
                body = page.read_text(encoding="utf-8")
                if name != "PATHWAYS.md":
                    self.assertIn("## Table of contents", body)
                self.assertIn("README.md", body if name != "README.md"
                              else body + "README.md")

    def test_every_relative_markdown_link_resolves(self):
        paths = sorted(DOCS.rglob("*.md"))
        self.assertEqual(len(paths), 29)  # 7 guides + 22 pathways.
        for path in paths:
            body = path.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)]+)\)", body):
                if "://" in target or target.startswith("#"):
                    continue
                target_file = target.split("#", 1)[0]
                with self.subTest(path=str(path.relative_to(ROOT)), link=target):
                    self.assertTrue((path.parent / target_file).is_file(),
                                    f"{path}: broken link {target}")

    def test_active_details_link_to_specific_fool_ability(self):
        guide = (DOCS / "CONTROLS.md").read_text(encoding="utf-8")
        fool = (DOCS / "pathways" / "fool.md").read_text(encoding="utf-8")
        self.assertIn("pathways/fool.md#seq-9-spirit-vision", guide)
        self.assertIn('<a id="seq-9-spirit-vision"></a>', fool)
        self.assertIn("Spiritual Expenditure", fool)


if __name__ == "__main__":
    unittest.main()
