"""Wave 3 catalog fidelity, behavior gates and locked Resonance regression."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.batches import individual4, resonance3
from arcane_rev3.full_build import build
from arcane_rev3.powers import compile_powers, norm


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_INDIVIDUAL = {
    "strength": {"Master's Grip"},
    "temperance": {"Mirror Passage", "Beast Form", "Abomination"},
    "wheel_of_fortune": {"Clockwork", "Winning Streak", "Chaos Step"},
    "emperor": {"Corrupt Ground"},
    "sun": {"White Angel"},
    "judgement": {"Verdict's Weight", "Order"},
    "devil": {"Chaos Unleashed"},
    "tower": {"Shockwave"},
    "chariot": {"Meteor"},
    "lovers": {"The Garden", "Shared Refuge"},
    "hermit": {"Star Read"},
    "star": {"Terror"},
    "high_priestess": {"All-Knowing Gaze"},
}
EXPECTED_RESONANCE = {
    "starless_poison": {"Poison Conceal", "Shadow Whisper"},
    "binding_contract": {"Law of Hell"},
    "burning_archive": {"Reaper's Library", "Burning Lecture"},
    "eclipse": {"Moonshadow", "Lunar Sanctuary", "Solar Drain"},
    "walking_sanctuary": {"Beast Contract"},
    "impossible_fist": {"Star Chart Grip"},
    "benevolent_crown": {"Linked Crown"},
    "loaded_dice": {"Cross-Reference Clockwork"},
}


def entries(module):
    result = []
    module.register(lambda *args: result.append(args))
    return result


class WaveThreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers, cls.manifest, cls.kits = compile_powers(ROOT)
        cls.lookup = {(m["family"], m["pathway"], m["sequence"], norm(m["name"])): m
                      for m in cls.manifest}

    def test_33_new_source_abilities_and_exact_manifest(self):
        self.assertEqual(len(entries(individual4)), 19)
        self.assertEqual(len(entries(resonance3)), 12)
        for family, module, expected in (
            ("individual", individual4, EXPECTED_INDIVIDUAL),
            ("resonance", resonance3, EXPECTED_RESONANCE),
        ):
            seen = {}
            for slug, seq, name, value, *status in entries(module):
                seen.setdefault(slug, set()).add(name)
                m = self.lookup[(family, slug, seq, norm(name))]
                self.assertIsNotNone(m["power_id"])
                self.assertIn(m["power_id"], self.powers)
                self.assertIn(m["power_id"], self.kits[(slug, seq)])
                self.assertNotEqual(value["type"], "origins:simple")
                self.assertEqual(m["status"], status[0] if status else "full")
                if m["status"] == "partial":
                    self.assertTrue(status[1] and m["missing"], (slug, name))
            self.assertEqual(seen, expected)
        self.assertEqual(len(self.powers), 301)
        self.assertEqual(len(self.manifest), 434)
        self.assertEqual({k: sum(m["status"] == k for m in self.manifest)
                          for k in ("full", "partial", "blocked")},
                         {"full": 73, "partial": 228, "blocked": 133})
        self.assertEqual(sum(m["family"] == "resonance" and
                             m["status"] != "blocked" for m in self.manifest), 92)

    def test_targeted_damage_is_hostile_only(self):
        item = self.powers["tarot:tower/3_shockwave"]
        self.assertEqual(item["type"], "origins:action_on_land")
        area = item["entity_action"]
        self.assertEqual(area["type"], "origins:area_of_effect")
        self.assertEqual(area["bientity_condition"]["condition"]["tag"], "tarot:hostile")
        self.assertEqual(area["bientity_action"]["action"]["amount"], 2)

    def test_retaliation_excludes_allied_players(self):
        power = self.powers["tarot:binding_contract/3_law_of_hell"]
        self.assertEqual(power["type"], "origins:attacker_action_when_hit")
        self.assertEqual(power["damage_condition"]["entity_condition"]["tag"],
                         "tarot:hostile")
        self.assertIn("enemy players", next(
            m["missing"] for m in self.manifest
            if m["power_id"] == "tarot:binding_contract/3_law_of_hell"))

    def test_fate_random_and_phasing_are_real_native_actions(self):
        chance = self.powers["tarot:wheel_of_fortune/8_clockwork"]["entity_action"]
        self.assertEqual(chance["chance"], 0.10)
        self.assertEqual(len(chance["action"]["actions"]), 6)
        portal = self.powers["tarot:temperance/9_mirror_passage"]
        self.assertEqual(portal["type"], "origins:phasing")
        self.assertEqual(portal["condition"]["type"], "origins:and")
        self.assertEqual(portal["block_condition"]["type"], "origins:or")

    def test_fixed_commands_never_grant_operators_or_attack_unfiltered_players(self):
        for module in (individual4, resonance3):
            for _, _, name, p, *_ in entries(module):
                todo = [p]
                while todo:
                    value = todo.pop()
                    if isinstance(value, dict):
                        todo.extend(v for v in value.values()
                                    if isinstance(v, (dict, list)))
                        if value.get("type") == "origins:execute_command":
                            command = value["command"]
                            self.assertEqual(value["permission_level"], 2)
                            self.assertNotIn("\n", command)
                            self.assertNotIn("op ", command)
                            self.assertNotIn("@a[distance=", command
                                if any(f"minecraft:{bad}" in command for bad in
                                       ("wither", "poison", "weakness", "slowness"))
                                else "")
                    elif isinstance(value, list):
                        todo.extend(value)

    def test_both_variants_include_new_powers_without_unlocking_resonance(self):
        with tempfile.TemporaryDirectory() as folder:
            output = build(output=Path(folder))
            for variant in ("only", "addon"):
                with self.subTest(variant=variant), ZipFile(output[variant]) as archive:
                    self.assertIsNone(archive.testzip())
                    for family, module in (
                        ("individual", individual4), ("resonance", resonance3)):
                        for slug, seq, name, *_ in entries(module):
                            m = self.lookup[(family, slug, seq, norm(name))]
                            power_path = ("data/tarot/powers/" +
                                          m["power_id"].split(":")[1] + ".json")
                            self.assertIn(power_path, archive.namelist())
                            self.assertNotEqual(
                                json.loads(archive.read(power_path))["type"],
                                "origins:simple")
                    for slug in EXPECTED_RESONANCE:
                        origin = json.loads(archive.read(f"data/tarot/origins/{slug}.json"))
                        self.assertTrue(origin["unchoosable"])
                        self.assertEqual(origin["powers"], [])
                    s2 = archive.read(
                        "data/tarot_arcane/functions/ascend/check_s2.mcfunction").decode()
                    self.assertIn("Resonance is locked", s2)
                    self.assertNotIn("clear @s", s2)


if __name__ == "__main__":
    unittest.main()
