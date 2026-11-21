"""25 handbook-traced individual abilities with bounded, disclosed native subsets.

No new Java/Fabric/KubeJS dependency. These tests independently check
catalog-key identities, truthful PARTIAL status, target safety and build
integration; runtime acceptance still requires an actual Minecraft server.
"""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.powers import compile_powers, norm
from arcane_rev3.full_build import build

ROOT = Path(__file__).resolve().parents[1]
NEW = (
    ("magician", 3, "Shortcut"),
    ("magician", 1, "Astral Lock"),
    ("high_priestess", 7, "Index"),
    ("high_priestess", 6, "Cross-Reference"),
    ("emperor", 9, "Decree of the Sovereign"),
    ("hierophant", 7, "Consecrate"),
    ("hierophant", 6, "Contract"),
    ("hermit", 2, "Sage’s Counsel"),
    ("justice", 9, "Calming Presence"),
    ("justice", 2, "Discern"),
    ("justice", 1, "Author’s Edit"),
    ("death", 2, "Consul"),
    ("death", 1, "Reap"),
    ("temperance", 4, "Puppet"),
    ("devil", 5, "Desire"),
    ("devil", 3, "Blather"),
    ("tower", 7, "Fault Line"),
    ("moon", 8, "Tame"),
    ("moon", 6, "Brew"),
    ("moon", 3, "Summon"),
    ("moon", 2, "Life"),
    ("moon", 1, "Pharmacist II"),
    ("judgement", 8, "Posse"),
    ("judgement", 3, "Chaos Hunter"),
    ("judgement", 2, "Balance"),
)
KNOWN_BLOCKED = (
    ("hierophant", 1, "Dietary Expansion"),
    ("hanged_man", 9, "Sin-Bearing"),
    ("hanged_man", 5, "Burden Bearer"),
    ("hanged_man", 3, "Trinity"),
    ("hanged_man", 1, "Sin Overflow"),
    ("hanged_man", 1, "Depraved Dependent"),
    ("hanged_man", 0, "Weight of Sin Made Manifest"),
)


class Wave8CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers, cls.manifest, cls.kits = compile_powers(ROOT)
        cls.index = {
            (x["pathway"], x["sequence"], norm(x["name"])): x
            for x in cls.manifest if x["family"] == "individual"
        }

    def test_25_unique_new_source_entries_are_real_and_disclosed(self):
        self.assertEqual(len(set(NEW)), 25)
        self.assertEqual(len(self.index), 324)
        for slug, seq, name in NEW:
            key = slug, seq, norm(name)
            with self.subTest(ability=key):
                item = self.index[key]
                self.assertEqual(item["status"], "partial")
                self.assertIsNotNone(item["power_id"])
                self.assertIn(item["power_id"], self.powers)
                self.assertTrue(item["missing"].strip())
                self.assertNotEqual(self.powers[item["power_id"]]["type"],
                                    "origins:simple")
                self.assertIn(item["power_id"], self.kits[(slug, seq)])

    def test_remaining_unimplemented_entries_are_not_falsely_completed(self):
        for slug, seq, name in KNOWN_BLOCKED:
            with self.subTest(name=name):
                item = self.index[(slug, seq, norm(name))]
                self.assertEqual(item["status"], "blocked")
                self.assertIsNone(item["power_id"])

    def test_exact_source_total_after_wave8(self):
        self.assertEqual(len(self.manifest), 434)
        self.assertEqual(len(self.powers), 427)
        self.assertEqual(sum(x["status"] == "blocked" for x in self.manifest), 7)
        self.assertEqual(sum(x["status"] == "full" for x in self.manifest), 73)
        self.assertEqual(sum(x["status"] == "partial" for x in self.manifest), 354)
        self.assertTrue(all(x["status"] != "blocked"
                            for x in self.manifest if x["family"] == "resonance"))

    def test_environment_and_pvp_safety(self):
        for slug, seq, name in NEW:
            key = slug, seq, norm(name)
            power_id = self.index[key]["power_id"]
            src = json.dumps(self.powers[power_id])
            with self.subTest(ability=name):
                self.assertNotIn("op @", src)
                self.assertNotIn("team join ", src)
                self.assertNotIn("kill @a", src)
                self.assertNotIn("execute as @a run damage", src)
                self.assertNotIn("summon minecraft:zombie", src)
                self.assertNotIn("setblock", src)
                self.assertNotIn("fill ", src)
                self.assertNotIn("origins:simple", src)
                self.assertNotIn("remorphed ", src)
                self.assertNotIn("skinshifter ", src)
                self.assertNotIn("minecraft:player_hurt_entity", src)

    def test_specific_behaviors_preserve_purposeful_subsets(self):
        cases = {
            ("magician", 3, "Shortcut"): "origins:modify_break_speed",
            ("emperor", 9, "Decree of the Sovereign"):
                "origins:action_over_time",
            ("justice", 9, "Calming Presence"):
                "origins:action_over_time",
            ("moon", 8, "Tame"): "origins:action_on_entity_use",
            ("judgement", 3, "Chaos Hunter"): "origins:modify_damage_dealt",
            ("moon", 1, "Pharmacist II"): "origins:action_over_time",
        }
        for key, kind in cases.items():
            with self.subTest(ability=key):
                item = self.index[(key[0], key[1], norm(key[2]))]
                self.assertEqual(self.powers[item["power_id"]]["type"], kind)
        emperor = self.powers[
            self.index[("emperor", 9, norm("Decree of the Sovereign"))]["power_id"]]
        self.assertIn("hero_of_the_village", json.dumps(emperor))
        self.assertIn("minecraft:shield", json.dumps(emperor))

    def test_both_dev_zip_variants_include_all_new_powers(self):
        with tempfile.TemporaryDirectory() as temp:
            artifacts = build(ROOT, output=Path(temp))
            for variant in ("only", "addon"):
                with self.subTest(variant=variant), ZipFile(artifacts[variant]) as z:
                    for slug, seq, name in NEW:
                        item = self.index[(slug, seq, norm(name))]
                        path = "data/" + item["power_id"].replace(":", "/powers/", 1) + ".json"
                        self.assertIn(path, z.namelist(), path)
                        obj = json.loads(z.read(path))
                        self.assertTrue(obj.get("type", "").startswith("origins:"))
                        self.assertTrue(obj.get("name"))
            manifest = json.loads(Path(artifacts["manifest"]).read_text())
            self.assertEqual(manifest["summary"]["compiled"], 427)
            self.assertEqual(manifest["summary"]["blocked"], 7)


if __name__ == "__main__":
    unittest.main()
