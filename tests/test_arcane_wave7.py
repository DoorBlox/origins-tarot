"""Wave 7: 32 non-placeholder source-fidelity substitutes, safely marked partial."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.batches import individual7
from arcane_rev3.full_build import build
from arcane_rev3.powers import compile_powers, norm


ROOT = Path(__file__).resolve().parents[1]
CAPSTONES = {
    "magician": "All Paths Converge",
    "hierophant": "The Sanctum",
    "wheel_of_fortune": "Slot of Fate",
    "justice": "The Mindscape",
    "death": "The Final Harvest",
    "devil": "Descent",
    "tower": "The Fall",
    "moon": "The Scarlet Feast",
    "judgement": "The Absolute Law",
    "world": "The Perfect Prey",
}
EXPECTED_COUNTS = {
    "fool": 3, "magician": 2, "high_priestess": 3,
    "empress": 2, "hierophant": 1, "chariot": 1,
    "hermit": 3, "wheel_of_fortune": 1, "justice": 2,
    "death": 1, "devil": 1, "tower": 3, "star": 1,
    "moon": 2, "sun": 1, "judgement": 1, "world": 4,
}


def registered():
    found = []
    individual7.register(lambda *args: found.append(args))
    return found


def objects(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from objects(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from objects(v)


class IndividualSevenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers, cls.manifest, cls.kits = compile_powers(ROOT)
        cls.lookup = {
            (x["family"], x["pathway"], x["sequence"], norm(x["name"])): x
            for x in cls.manifest
        }
        cls.entries = registered()

    def test_all_32_catalog_exact_and_disclosed_partial(self):
        self.assertEqual(len(self.entries), 32)
        counts = {}
        for slug, seq, name, definition, status, missing in self.entries:
            with self.subTest(slug=slug, seq=seq, name=name):
                counts[slug] = counts.get(slug, 0) + 1
                record = self.lookup[("individual", slug, seq, norm(name))]
                self.assertEqual(record["status"], "partial")
                self.assertEqual(status, "partial")
                self.assertTrue(missing)
                self.assertTrue(record["missing"].startswith(missing))
                self.assertIn(record["power_id"], self.powers)
                self.assertIn(record["power_id"], self.kits[(slug, seq)])
                self.assertNotEqual(definition["type"], "origins:simple")
        self.assertEqual(counts, EXPECTED_COUNTS)

    def test_402_ability_status_and_complete_source_resonance(self):
        self.assertEqual(len(self.manifest), 434)
        self.assertEqual(len(self.powers), 402)
        self.assertEqual(
            {s: sum(m["status"] == s for m in self.manifest)
             for s in ("full", "partial", "blocked")},
            {"full": 73, "partial": 329, "blocked": 32})
        self.assertEqual(
            sum(x["family"] == "resonance" and x["status"] != "blocked"
                for x in self.manifest), 110)

    def test_all_ten_important_capstones_remain_primary_key_and_bounded(self):
        for slug, name in CAPSTONES.items():
            with self.subTest(capstone=name):
                matches = [x for x in self.entries
                           if x[0] == slug and x[1] == 0 and x[2] == name]
                self.assertEqual(len(matches), 1)
                power = matches[0][3]
                active = power if power["type"] == "origins:active_self" else (
                    power.get("activate") if power["type"] == "origins:multiple" else None)
                self.assertIsNotNone(active)
                self.assertEqual(active["type"], "origins:active_self")
                self.assertGreaterEqual(active["cooldown"], 18000)
                self.assertLessEqual(active["cooldown"], 24000)
                self.assertEqual(active["key"]["key"], "key.origins.primary_active")

    def test_fate_reel_is_weighted_and_does_not_change_world_or_players(self):
        luck = self.powers["tarot:wheel_of_fortune/0_slot_of_fate"]
        self.assertEqual(luck["type"], "origins:active_self")
        choice = luck["entity_action"]
        self.assertEqual(choice["type"], "origins:choice")
        self.assertEqual(len(choice["actions"]), 6)
        weights = [v["weight"] for v in choice["actions"]]
        self.assertEqual(weights, [200, 200, 200, 150, 150, 1])
        self.assertEqual(sum(weights), 901)

    def test_stealth_is_combat_limited_and_targeted_commands_guarded(self):
        disguise = self.powers["tarot:fool/9_full_faceless_disguise"]
        self.assertEqual(disguise["condition"]["command"],
                         "execute if score @s a_combat matches 0")
        self.assertEqual(disguise["cooldown"], 6000)
        for slug, seq, name, definition, *_ in self.entries:
            with self.subTest(name=name):
                for node in objects(definition):
                    if node.get("type") != "origins:execute_command":
                        continue
                    line = node["command"]
                    self.assertEqual(node.get("permission_level"), 2)
                    self.assertNotIn("\n", line)
                    self.assertNotIn(" op ", " "+line)
                    self.assertNotIn(" kill ", " "+line)
                    self.assertNotIn(" setblock ", " "+line)
                    self.assertNotIn(" fill ", " "+line)
                    if "effect give @a[" in line:
                        self.assertIn("execute if entity @s[team=", line)
                        self.assertIn("run effect give @a[team=", line)

    def test_both_zip_variants_do_not_accidentally_unlock_seq1(self):
        with tempfile.TemporaryDirectory() as folder:
            artifacts = build(output=Path(folder))
            for label in ("only", "addon"):
                with self.subTest(variant=label), ZipFile(artifacts[label]) as z:
                    self.assertIsNone(z.testzip())
                    for slug, seq, name, *_ in self.entries:
                        manifest = self.lookup[
                            ("individual", slug, seq, norm(name))]
                        path = "data/tarot/powers/" + manifest["power_id"].split(":")[1] + ".json"
                        self.assertIn(path, z.namelist())
                        self.assertNotEqual(json.loads(z.read(path))["type"],
                                            "origins:simple")
                    gate = z.read(
                        "data/tarot_arcane/functions/ascend/check_s2.mcfunction"
                    ).decode()
                    self.assertIn("unless score @s a_rtest matches 1", gate)
                    self.assertIn("Resonance is locked", gate)


if __name__ == "__main__":
    unittest.main()
