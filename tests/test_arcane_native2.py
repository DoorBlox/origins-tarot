"""Native interaction batch contracts for Minecraft 1.18.2 / Origins 1.4.1."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from arcane_rev3.powers import norm, compile_powers
from arcane_rev3.full_build import build
from arcane_rev3.batches import native2

ROOT=Path(__file__).resolve().parents[1]
EXPECTED=[
 ("lovers",8,"Triage"),("hierophant",3,"Purify"),("justice",7,"Calm"),
 ("lovers",6,"Symbiosis"),("hierophant",9,"Consecrated Workspace"),
 ("hierophant",4,"Sanctified Ground II"),("tower",9,"Unstable Ground"),
 ("emperor",7,"Coin"),("fool",7,"Stage Magician"),
 ("fool",9,"Spiritual Overload"),("justice",1,"Compassionate Restraint II"),
 ("death",8,"Grave Dirt"),("lovers",7,"Blessing"),
 ("chariot",7,"Flame Burst"),("lovers",4,"Transmute")
]


class NativeInteractionUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers,cls.manifest,cls.kits=compile_powers(ROOT)
        cls.index={(m["pathway"],m["sequence"],norm(m["name"])):m
                   for m in cls.manifest if m["family"]=="individual"}

    def test_exact_source_ids_and_15_real_powers(self):
        captured=[]
        native2.register(lambda *args: captured.append(args))
        self.assertEqual(len(captured),15)
        self.assertEqual([tuple(args[:3]) for args in captured],EXPECTED)
        for slug,seq,name,power,*tail in captured:
            key=self.index[(slug,seq,norm(name))]
            self.assertEqual(key["status"],"partial",name)
            self.assertIn(key["power_id"],self.powers)
            self.assertIn(key["power_id"],self.kits[(slug,seq)])
            self.assertTrue(key["missing"])
            self.assertNotEqual(power["type"],"origins:simple")
            self.assertNotIn(power["type"],("origins:modify_healing",
                                             "origins:modify_insomnia_ticks"))
        self.assertGreaterEqual(len(self.powers),181)
        self.assertGreaterEqual(sum(e["status"]=="full" for e in self.manifest),69)
        self.assertGreaterEqual(sum(e["status"]=="partial" for e in self.manifest),112)
        self.assertLessEqual(sum(e["status"]=="blocked" for e in self.manifest),253)

    def test_native_interaction_schemas_and_exact_effects(self):
        checks=[
            ("lovers",8,"Triage","origins:action_on_entity_use"),
            ("hierophant",3,"Purify","origins:action_on_entity_use"),
            ("justice",7,"Calm","origins:action_on_entity_use"),
            ("lovers",6,"Symbiosis","origins:conditioned_attribute"),
            ("hierophant",9,"Consecrated Workspace","origins:multiple"),
            ("hierophant",4,"Sanctified Ground II","origins:modify_xp_gain"),
            ("lovers",7,"Blessing","origins:action_on_block_use"),
            ("tower",9,"Unstable Ground","origins:action_on_block_break"),
        ]
        for slug,seq,name,kind in checks:
            ident=self.index[(slug,seq,norm(name))]["power_id"]
            self.assertEqual(self.powers[ident]["type"],kind,name)
        self.assertEqual(self.powers["tarot:lovers/8_triage"]["bientity_action"]
                         ["action"]["amount"],2)
        self.assertEqual(self.powers["tarot:lovers/7_blessing"]["block_action"]["change"],7)
        self.assertEqual(self.powers["tarot:hierophant/9_consecrated_workspace"]
                         ["haste"]["condition"]["radius"],8)
        self.assertEqual(self.powers["tarot:hierophant/4_sanctified_ground_ii"]
                         ["condition"]["radius"],5)
        self.assertEqual(self.powers["tarot:lovers/6_symbiosis"]["modifier"]["value"],1.0)

    def test_right_click_skills_do_not_fabricate_cooldowns(self):
        for slug,seq,name in (("lovers",8,"Triage"),
                              ("hierophant",3,"Purify"),("justice",7,"Calm"),
                              ("emperor",7,"Coin")):
            p=self.powers[self.index[(slug,seq,norm(name))]["power_id"]]
            self.assertEqual(p["type"],"origins:action_on_entity_use")
            self.assertNotIn("cooldown",p)
        p=self.powers["tarot:emperor/7_coin"]
        self.assertEqual(p["item_condition"]["ingredient"]["item"],
                         "minecraft:gold_ingot")
        self.assertEqual(p["bientity_condition"]["condition"]["tag"],
                         "tarot:hostile")


class NativeInteractionPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.artifacts=build(output=Path(cls.tmp.name))
        cls.pack=ZipFile(cls.artifacts["only"])
    @classmethod
    def tearDownClass(cls):
        cls.pack.close()
        cls.tmp.cleanup()

    def test_transmute_guards_inventory_before_mutating(self):
        path="data/tarot_arcane/functions/abilities/lovers_transmute.mcfunction"
        script=self.pack.read(path).decode().splitlines()
        self.assertIn("scoreboard players set @s a_iron_count 0",script)
        query="execute store result score @s a_iron_count run clear @s minecraft:iron_ingot 0"
        self.assertIn(query,script)
        consume="execute if score @s a_iron_count matches 2.. run clear @s minecraft:iron_ingot 2"
        reward="execute if score @s a_iron_count matches 2.. run give @s minecraft:gold_ingot 1"
        self.assertIn(consume,script)
        self.assertIn(reward,script)
        self.assertLess(script.index(query),script.index(consume))
        self.assertLess(script.index(consume),script.index(reward))
        self.assertEqual(sum("give @s minecraft:gold_ingot" in line for line in script),1)
        self.assertFalse(any("clear @a" in line or "give @a" in line for line in script))
        power=json.loads(self.pack.read("data/tarot/powers/lovers/4_transmute.json"))
        self.assertEqual(power["cooldown"],12000)
        self.assertEqual(power["entity_action"]["command"],
                         "function tarot_arcane:abilities/lovers_transmute")

    def test_new_tag_variants_are_vanilla_and_both_variants_build(self):
        for kind in ("only","addon"):
            with ZipFile(self.artifacts[kind]) as pack:
                tags=json.loads(pack.read("data/tarot/tags/blocks/sanctified_ground.json"))
                for b in ("minecraft:stone_bricks","minecraft:mossy_stone_bricks",
                          "minecraft:cracked_stone_bricks","minecraft:stone_brick_stairs",
                          "minecraft:stone_brick_slab","minecraft:stone_brick_wall"):
                    self.assertIn(b,tags["values"])
                for slug,seq,name in EXPECTED:
                    item=next(m for m in json.loads(
                        Path(self.artifacts["manifest"]).read_text())["abilities"]
                        if m["family"]=="individual" and m["pathway"]==slug and
                        m["sequence"]==seq and norm(m["name"])==norm(name))
                    self.assertIn("data/tarot/powers/"+item["power_id"].split(":")[1]+".json",
                                  pack.namelist())
                self.assertIsNone(pack.testzip())
