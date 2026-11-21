"""Wave 6: all 110 Resonance source slots, persistent rescue safeguards."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.batches import individual6, resonance6
from arcane_rev3.full_build import (
    ROOT, RESCUE_COOLDOWNS, build, DEV_PREVIEW_SOURCE,
)
from arcane_rev3.model import PAIRS
from arcane_rev3.powers import compile_powers, norm


def registered(module):
    result = []
    module.register(lambda *args: result.append(args))
    return result


def walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


class WaveSixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers, cls.manifest, cls.kits = compile_powers(ROOT)
        cls.lookup = {
            (m["family"], m["pathway"], m["sequence"], norm(m["name"])): m
            for m in cls.manifest
        }

    def test_all_33_new_ability_definitions_are_catalog_matched_and_partial(self):
        for module, family, n in ((individual6, "individual", 21),
                                  (resonance6, "resonance", 12)):
            entries = registered(module)
            self.assertEqual(len(entries), n)
            for slug, seq, name, definition, status, missing in entries:
                with self.subTest(family=family,slug=slug,name=name):
                    m = self.lookup[(family, slug, seq, norm(name))]
                    self.assertEqual(m["status"], "partial")
                    self.assertEqual(status, "partial")
                    self.assertTrue(missing)
                    self.assertTrue(m["missing"].startswith(missing))
                    self.assertEqual(self.powers[m["power_id"]], definition)
                    self.assertIn(m["power_id"], self.kits[(slug, seq)])
                    self.assertNotEqual(definition["type"], "origins:simple")

    def test_counts_all_110_resonance_entries_are_meaningful_but_not_playable(self):
        self.assertEqual(len(self.manifest), 434)
        self.assertEqual(len(self.powers), 402)
        self.assertEqual({st: sum(m["status"] == st for m in self.manifest)
                         for st in ("full", "partial", "blocked")},
                         {"full": 73, "partial": 329, "blocked": 32})
        self.assertEqual(
            sum(m["family"] == "resonance" and m["status"] != "blocked"
                for m in self.manifest), 110)
        self.assertEqual(
            sum(m["family"] == "individual" and m["status"] != "blocked"
                for m in self.manifest), 260)
        self.assertEqual({p for _, _, p in PAIRS},
                         {m["pathway"] for m in self.manifest
                          if m["family"] == "resonance"})

    def test_rescue_powers_have_actual_7200_9600_12000_latches(self):
        ids = {
            "tarot:paper_martyr/1_martyr_s_substitute": ("a_cd_martyr", 7200),
            "tarot:marked_verdict/1_swift_judgment": ("a_cd_swift", 9600),
            "tarot:fool/1_history_substitution": ("a_cd_history", 7200),
            "tarot:world/1_hunter_s_substitution": ("a_cd_hunter", 9600),
            "tarot:death/4_undying": ("a_cd_undying", 12000),
        }
        self.assertEqual(len(RESCUE_COOLDOWNS), len(ids))
        for ident, (objective, cooldown) in ids.items():
            with self.subTest(ability=ident):
                p = self.powers[ident]
                self.assertEqual(p["type"], "origins:prevent_death")
                gate = p["condition"]
                if gate["type"] == "origins:and":
                    self.assertEqual(len(gate["conditions"]), 2)
                    gate = gate["conditions"][0]
                self.assertEqual(gate["type"], "origins:command")
                self.assertIn(
                    f"execute if score @s {objective} matches 0", gate["command"])
                self.assertEqual(gate["permission_level"], 2)
                actions = p["entity_action"]["actions"]
                self.assertEqual(actions[0]["command"],
                                 f"scoreboard players set @s {objective} {cooldown}")
                self.assertTrue(any(x["type"] == "origins:heal" for x in actions))
                self.assertEqual(objective in RESCUE_COOLDOWNS, True)
        undying = self.powers["tarot:death/4_undying"]
        self.assertEqual(undying["condition"]["conditions"][1]["chance"], 0.05)
        self.assertFalse(any(x.get("type") == "origins:random_teleport"
                             for x in undying["entity_action"]["actions"]))

    def test_decoys_have_bounded_auto_expiry_not_persistent_world_entities(self):
        for ident in ("tarot:paper_martyr/5_gathering_of_martyrs",
                      "tarot:paper_martyr/2_sacrificial_gathering"):
            p = self.powers[ident]
            commands = [v["command"] for v in walk(p)
                        if v.get("type") == "origins:execute_command"]
            decoys = [c for c in commands if "summon minecraft:area_effect_cloud" in c]
            self.assertEqual(len(decoys), 2)
            self.assertTrue(all("Duration:200" in c for c in decoys))
            self.assertTrue(all("tarot_arcane_decoy" in c for c in decoys))
            self.assertFalse(any("armor_stand" in c for c in commands))

    def test_gamepack_keeps_seq1_locked_and_reconciles_online_cooldown(self):
        with tempfile.TemporaryDirectory() as d:
            paths = build(output=Path(d))
            for variant in ("only", "addon"):
                with self.subTest(variant=variant), ZipFile(paths[variant]) as pack:
                    self.assertIsNone(pack.testzip())
                    load = pack.read(
                        "data/tarot_arcane/functions/load.mcfunction").decode()
                    tick = pack.read(
                        "data/tarot_arcane/functions/player/tick.mcfunction").decode()
                    alone = pack.read(
                        "data/tarot_arcane/functions/player/alone.mcfunction").decode()
                    for score in RESCUE_COOLDOWNS:
                        self.assertIn(f"scoreboard objectives add {score} dummy", load)
                        self.assertIn(
                            f"scoreboard players add @s {score} 0", tick)
                        self.assertIn(
                            f"scoreboard players remove @s {score} 1", tick)
                    self.assertIn("team=tarot_red", alone)
                    self.assertIn("team=tarot_blue", alone)
                    self.assertNotIn("@a[distance=0.01..8]", alone)
                    self.assertIn(
                        "Resonance is locked",
                        pack.read("data/tarot_arcane/functions/ascend/check_s2.mcfunction").decode())
                    for _, _, slug in PAIRS:
                        self.assertEqual(json.loads(pack.read(
                            f"data/tarot/origins/{slug}.json"))["powers"], [])
            with ZipFile(paths["resonance_preview"]) as preview:
                ids = [name for name in preview.namelist()
                       if "/dev/resonance/one/" in name]
                self.assertEqual(len(ids), 110)
                src = preview.read(
                    "data/tarot_arcane/functions/dev/resonance/clear.mcfunction"
                ).decode()
                self.assertIn(DEV_PREVIEW_SOURCE, src)


if __name__ == "__main__":
    unittest.main()
