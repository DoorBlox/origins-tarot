"""Arcane wave 5: thirty individual plus six Resonance meaningful power subsets."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.batches import individual5, resonance5
from arcane_rev3.full_build import build
from arcane_rev3.powers import compile_powers, norm


ROOT = Path(__file__).resolve().parents[1]
INDIVIDUAL = {
    "fool": 2,
    "magician": 1,
    "high_priestess": 1,
    "empress": 3,
    "emperor": 2,
    "hierophant": 1,
    "lovers": 1,
    "chariot": 3,
    "strength": 5,
    "hermit": 1,
    "justice": 1,
    "devil": 1,
    "tower": 1,
    "moon": 1,
    "sun": 2,
    "judgement": 1,
    "world": 1,
    "star": 1,
    "temperance": 1,
}
RESONANCE = {
    "paper_martyr": 2,
    "marked_verdict": 1,
    "impossible_fist": 1,
    "walking_sanctuary": 1,
    "eclipse": 1,
}


def register(module):
    result = []
    module.register(lambda *args: result.append(args))
    return result


def walk(value):
    if isinstance(value, dict):
        yield value
        for sub in value.values():
            yield from walk(sub)
    elif isinstance(value, list):
        for sub in value:
            yield from walk(sub)


class WaveFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers, cls.manifest, cls.kits = compile_powers(ROOT)
        cls.lookup = {
            (m["family"], m["pathway"], m["sequence"], norm(m["name"])): m
            for m in cls.manifest
        }

    def test_36_catalog_matched_non_placeholder_effects(self):
        for family, module, expected, target in (
            ("individual", individual5, INDIVIDUAL, 30),
            ("resonance", resonance5, RESONANCE, 6),
        ):
            entries = register(module)
            self.assertEqual(len(entries), target)
            found = {}
            for slug, seq, name, definition, accuracy, missing in entries:
                with self.subTest(family=family, name=name):
                    found[slug] = found.get(slug, 0) + 1
                    record = self.lookup[(family, slug, seq, norm(name))]
                    self.assertEqual(record["status"], "partial")
                    self.assertEqual(accuracy, "partial")
                    # The compiler appends an explicit enemy-player safety
                    # disclosure to retaliatory powers; preserve that warning.
                    self.assertTrue(record["missing"].startswith(missing))
                    if definition["type"] == "origins:attacker_action_when_hit":
                        self.assertIn("different-team target filter", record["missing"])
                    self.assertIn(record["power_id"], self.powers)
                    self.assertIn(record["power_id"], self.kits[(slug, seq)])
                    self.assertNotEqual(definition["type"], "origins:simple")
                    self.assertTrue(any(
                        obj.get("type") in (
                            "origins:apply_effect", "origins:action_on_land",
                            "origins:damage", "origins:modify_damage_dealt",
                            "origins:set_on_fire", "origins:heal", "origins:area_of_effect",
                            "origins:execute_command", "origins:add_velocity")
                        for obj in walk(definition)) or
                        definition["type"] in (
                            "origins:modify_damage_dealt", "origins:action_on_land",
                            "origins:action_on_entity_use",
                            "origins:self_action_when_hit",
                            "origins:attacker_action_when_hit"))
            self.assertEqual(found, expected)

    def test_counts_and_resonance_still_fail_closed(self):
        self.assertEqual(len(self.manifest), 434)
        self.assertEqual(len(self.powers), 402)
        self.assertEqual(
            {status: sum(m["status"] == status for m in self.manifest)
             for status in ("full", "partial", "blocked")},
            {"full": 73, "partial": 329, "blocked": 32})
        self.assertEqual(
            sum(m["family"] == "resonance" and m["status"] != "blocked"
                for m in self.manifest), 110)

    def test_area_effects_explicitly_exclude_player_targets(self):
        for module in (individual5, resonance5):
            for slug, seq, name, value, *_ in register(module):
                with self.subTest(name=name):
                    for x in walk(value):
                        if x.get("type") == "origins:area_of_effect":
                            self.assertEqual(
                                x["bientity_condition"]["condition"]["tag"],
                                "tarot:hostile")
                        if x.get("type") == "origins:execute_command":
                            self.assertEqual(x.get("permission_level"), 2)
                            line = x["command"]
                            self.assertNotIn("\n", line)
                            self.assertNotIn(" op ", " " + line)
                            self.assertNotIn(" deop ", " " + line)
                            self.assertNotIn(" kill ", " " + line)

    def test_capstones_and_installed_mods_remain_not_granted(self):
        with tempfile.TemporaryDirectory() as temp:
            paths = build(output=Path(temp))
            for label in ("only", "addon"):
                with self.subTest(label=label), ZipFile(paths[label]) as z:
                    self.assertIsNone(z.testzip())
                    for family, module in (
                        ("individual", individual5),
                        ("resonance", resonance5),
                    ):
                        for slug, seq, name, *_ in register(module):
                            m = self.lookup[(family, slug, seq, norm(name))]
                            p = "data/tarot/powers/" + m["power_id"].split(":")[1] + ".json"
                            self.assertIn(p, z.namelist())
                            self.assertNotEqual(json.loads(z.read(p))["type"],
                                                "origins:simple")
                    for slug in RESONANCE:
                        origin = json.loads(z.read(f"data/tarot/origins/{slug}.json"))
                        self.assertEqual(origin["powers"], [])
                        self.assertTrue(origin["unchoosable"])
                    gate = z.read(
                        "data/tarot_arcane/functions/ascend/check_s2.mcfunction"
                    ).decode()
                    self.assertIn("Resonance is locked", gate)
                    self.assertNotIn("clear @s", gate)


if __name__ == "__main__":
    unittest.main()
