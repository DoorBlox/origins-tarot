"""Regression from the owner's 2026-11-22 SMP log (legacy V2 artifact).

Origins 1.4.1 / Apoli 2.3.3 requires explicit render_armor on
origins:invisibility. The source handbook deliberately permits visible armor.
"""
import json
import unittest
from zipfile import ZipFile

import generate


class LegacyV2ArmorLoadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generate.make()
        cls.files = (generate.ZIP, generate.ZIP_ONLY)

    def test_empress_and_temperance_old_loader_power_ids(self):
        for archive in self.files:
            with self.subTest(archive=archive.name), ZipFile(archive) as zipfile:
                for path in (
                    "data/tarot/powers/empress/extra_1.json",
                    "data/tarot/powers/temperance/passive.json",
                ):
                    with self.subTest(path=path):
                        power = json.loads(zipfile.read(path))
                        self.assertEqual(power["type"], "origins:invisibility")
                        self.assertIs(power["render_armor"], True)
                        self.assertIn("condition", power)

    def test_every_legacy_invisibility_has_explicit_141_armor_field(self):
        for archive in self.files:
            with ZipFile(archive) as zipfile:
                count = 0
                for path in zipfile.namelist():
                    if not path.startswith("data/tarot/powers/") or not path.endswith(".json"):
                        continue
                    power = json.loads(zipfile.read(path))
                    if power.get("type") == "origins:invisibility":
                        count += 1
                        self.assertIn("render_armor", power, (archive.name, path))
                        self.assertIsInstance(power["render_armor"], bool)
                self.assertGreaterEqual(count, 2)


if __name__ == "__main__":
    unittest.main()
