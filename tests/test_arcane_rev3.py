"""Rev 3 behavior and Minecraft 1.18.2 datapack contracts."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.model import State, InvalidSlot, PAIRS, PATHWAYS
from arcane_rev3.build import build


class Rev3StateTests(unittest.TestCase):
    def test_complete_exact_pairing(self):
        self.assertEqual(len(PATHWAYS), 22)
        self.assertEqual(len(PAIRS), 11)
        self.assertEqual(set().union(*(set(pair[:2]) for pair in PAIRS)), set(PATHWAYS))

    def test_single_pathway_autofills_and_reaches_seq_four(self):
        state = State.start("fool")
        self.assertEqual((state.mode, state.maximum, state.slots), ("single", 1, (("fool", 9),)))
        for _ in range(5):
            state = state.ascend()
        self.assertEqual((state.sequence, state.mode, state.secondary, state.maximum), (4, "slot", "hanged_man", 6))
        self.assertEqual(state.slots[:5], (("fool", 9), ("fool", 8), ("fool", 7), ("fool", 6), ("fool", 5)))
        self.assertEqual(state.slots[5], None)

    def test_slot_validation_and_no_duplicates(self):
        state = State.start("fool")
        for _ in range(5):
            state = state.ascend()
        with self.assertRaises(InvalidSlot):
            state.assign(7, "fool", 4)
        with self.assertRaises(InvalidSlot):
            state.assign(6, "magician", 9)
        with self.assertRaises(InvalidSlot):
            state.assign(6, "hanged_man", 3)
        with self.assertRaises(InvalidSlot):
            state.assign(6, "fool", 9)
        chosen = state.assign(6, "hanged_man", 4)
        self.assertEqual(chosen.slots[5], ("hanged_man", 4))
        self.assertEqual(chosen.clear(6).slots[5], None)
        self.assertEqual(chosen.swap(1, 6).slots[0], ("hanged_man", 4))

    def test_slot_growth_and_resonance_transition(self):
        state = State.start("fool")
        for _ in range(5):
            state = state.ascend()
        self.assertEqual((state.ascend().sequence, state.ascend().maximum), (3, 7))
        state = state.ascend().ascend()
        self.assertEqual((state.sequence, state.maximum), (2, 8))
        self.assertEqual(len(state.slots), 8)
        state = state.ascend()
        self.assertEqual(state.mode, "resonance")
        self.assertEqual(state.slots, ())
        self.assertEqual(state.active_kits(), tuple(("paper_martyr", seq) for seq in range(9, -1, -1)))
        self.assertEqual(state.ascend().active_kits(), state.active_kits())
        with self.assertRaises(InvalidSlot):
            state.assign(1, "fool", 9)

    def test_reset_and_auto_are_player_local(self):
        state = State.start("fool")
        for _ in range(5):
            state = state.ascend()
        customized = state.assign(6, "hanged_man", 9)
        self.assertEqual(customized.reset().slots[5], None)
        self.assertEqual(customized.clear(1).auto().slots[0], ("fool", 9))


class Rev3BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.paths = build(Path(cls.tempdir.name))
        cls.zip = ZipFile(cls.paths["pack"])

    @classmethod
    def tearDownClass(cls):
        cls.zip.close()
        cls.tempdir.cleanup()

    def test_fool_only_sandbox_pack(self):
        names = set(self.zip.namelist())
        self.assertEqual(json.loads(self.zip.read("pack.mcmeta"))["pack"]["pack_format"], 9)
        self.assertIn("data/tarot/origins/fool.json", names)
        self.assertNotIn("data/tarot/origins/magician.json", names)
        self.assertIn("data/tarot/powers/fool/9_spirit_vision.json", names)
        self.assertIn("data/tarot/powers/fool/9_spiritual_expenditure.json", names)
        self.assertTrue(all("kubejs" not in path.lower() for path in names))
        for path in names:
            if path.endswith(".json"):
                json.loads(self.zip.read(path))

    def test_spirit_vision_and_exhaustion_exactly_match_handbook(self):
        power = json.loads(self.zip.read("data/tarot/powers/fool/9_spirit_vision.json"))
        self.assertEqual(power["cooldown"], 100)
        self.assertEqual(power["condition"]["type"], "origins:sneaking")
        self.assertEqual(power["key"]["key"], "key.origins.secondary_active")
        self.assertEqual(power["entity_action"]["radius"], 10)
        self.assertTrue(power["entity_action"]["include_target"])
        self.assertEqual(power["entity_action"]["bientity_action"]["action"]["effect"]["duration"], 40)
        exhaustion = json.loads(self.zip.read("data/tarot/powers/fool/9_spiritual_expenditure.json"))
        self.assertEqual(exhaustion["modifier"]["value"], 0.25)
        self.assertEqual({part["type"] for part in exhaustion["condition"]["conditions"]},
                         {"origins:sprinting", "origins:fall_flying"})

    def test_slot_grant_source_and_nonop_trigger(self):
        init = self.zip.read("data/tarot_arcane/functions/player/init_fool.mcfunction").decode()
        self.assertIn("power grant @s tarot:fool/9_spirit_vision tarot_slot", init)
        self.assertNotIn("power clear", init)
        tick = self.zip.read("data/tarot_arcane/functions/player/tick.mcfunction").decode()
        self.assertIn("scoreboard players enable @s ta_slots", tick)
        self.assertIn("origin has origin @s origins:origin tarot:fool", tick)
        alias = json.loads(Path(self.paths["alias"]).read_text())
        root = alias["customCommand"]
        self.assertEqual((root["parent"], root["permission"]), ("tarot", 0))
        self.assertTrue(all(action["commandType"] == "CLIENT"
                            and action["command"].startswith("trigger ta_")
                            for action in root["actions"] + [
                                act for child in root["children"] for act in child["actions"]
                            ]))
        self.assertEqual({child["child"] for child in root["children"]},
                         {"help", "status", "slots"})

    def test_no_fake_abilities_and_no_forbidden_commands(self):
        for path in self.zip.namelist():
            text = self.zip.read(path).decode("utf-8")
            self.assertNotIn('"type": "origins:simple"', text)
            self.assertNotIn("kubejs:", text.lower())
            if path.endswith(".mcfunction"):
                for forbidden in ("op @", "setblock ", "fill ", "power clear ", "execute if dimension "):
                    self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
