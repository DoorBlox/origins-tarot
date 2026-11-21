"""Rev2 bulk compilation: 38 real abilities, per-item source trace and safe selectors."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.batches import support, control, mobility
from arcane_rev3.full_build import build, IDENTITY_DRAWBACK_NAMES
from arcane_rev3.powers import compile_powers, norm

ROOT = Path(__file__).resolve().parents[1]

BATCHES = {
    support: [
        ("high_priestess", 5, "Ritual Circle"),
        ("hierophant", 9, "Quiet Benediction"),
        ("hierophant", 5, "Hymn"),
        ("justice", 9, "Therapist's Presence"),
        ("chariot", 3, "Rally"),
        ("justice", 3, "Shared Dream"),
        ("death", 7, "Spirit Sense"),
        ("star", 7, "Nightmare"),
        ("moon", 1, "Beauty"),
        ("hierophant", 1, "White Angel"),
        ("lovers", 1, "Shared Refuge II"),
        ("death", 1, "Grave Affinity II"),
        ("lovers", 3, "Requiem"),
        ("lovers", 9, "Separation Anxiety"),
    ],
    control: [
        ("lovers", 5, "Nature's Grasp"),
        ("lovers", 2, "Withering"),
        ("temperance", 2, "Bane"),
        ("tower", 2, "Cataclysm"),
        ("star", 5, "Haunt"),
        ("star", 1, "Misfortune"),
        ("empress", 1, "Petrifying Gaze"),
        ("emperor", 1, "Abolish"),
        ("star", 8, "Lullaby"),
        ("fool", 5, "Puppet String"),
        ("fool", 4, "Trickster's Escape"),
        ("fool", 1, "Paper Figurine Substitute"),
        ("hanged_man", 6, "Flesh Creek"),
        ("hanged_man", 2, "Profane Aura"),
        ("devil", 6, "Devil's Mark"),
        ("hermit", 7, "Hex"),
        ("judgement", 7, "Question"),
    ],
    mobility: [
        ("magician", 9, "Threshold Step"),
        ("magician", 5, "Doorstep"),
        ("magician", 4, "Sealed Room"),
        ("temperance", 1, "Wraith's Veil II"),
        ("temperance", 5, "Incorporeal"),
        ("hanged_man", 8, "Shadow Whisper"),
        ("strength", 8, "Iron Fist"),
    ],
}


class BulkAbilityUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiled, cls.manifest, cls.kits = compile_powers(ROOT)
        cls.index = {(m["pathway"], m["sequence"], norm(m["name"])): m
                     for m in cls.manifest if m["family"] == "individual"}

    def test_registered_count_names_and_source_trace(self):
        self.assertEqual([len(x) for x in BATCHES.values()], [14, 17, 7])
        expected = set()
        for module, cards in BATCHES.items():
            actual = []
            module.register(lambda slug, seq, name, value, *more: actual.append(
                (slug, seq, name, value, more)))
            self.assertEqual(len(actual), len(cards), module)
            self.assertEqual([(a,b,c) for a,b,c,_,_ in actual], cards)
            for slug, seq, name, value, accuracy in actual:
                key = (slug,seq,norm(name))
                self.assertNotIn(key,expected)
                expected.add(key)
                item = self.index.get(key)
                self.assertIsNotNone(item,key)
                self.assertNotEqual(item["status"],"blocked",key)
                self.assertEqual(item["power_id"] is not None,True,key)
                self.assertIn(item["power_id"],self.compiled)
                self.assertIn(item["power_id"],self.kits[(slug,seq)])
                self.assertTrue(value["type"].startswith("origins:"))
                self.assertNotEqual(value["type"],"origins:simple")
                self.assertEqual(item["status"], accuracy[0] if accuracy else "full")
                if item["status"]=="partial":
                    self.assertTrue(item["missing"])
        self.assertEqual(len(expected),38)
        self.assertGreaterEqual(len(self.compiled),166)
        self.assertLessEqual(sum(x["status"]=="blocked" for x in self.manifest),268)
        self.assertGreaterEqual(sum(x["status"]=="full" for x in self.manifest),69)
        self.assertGreaterEqual(sum(x["status"]=="partial" for x in self.manifest),97)

    def test_positive_aoe_uses_players_and_negative_aoe_uses_hostile_tag(self):
        safe = ("@e[type=#tarot:hostile,", "@e[type=#tarot:undead,")
        for module, triples in BATCHES.items():
            recorded=[]
            module.register(lambda slug,seq,name,value,*rest: recorded.append((slug,name,value)))
            for slug,name,value in recorded:
                stack=[value]
                while stack:
                    item=stack.pop()
                    if isinstance(item,list):
                        stack.extend(item)
                    if not isinstance(item,dict):
                        continue
                    stack.extend(x for x in item.values() if isinstance(x,(dict,list)))
                    if item.get("type") != "origins:execute_command":
                        continue
                    command=item["command"]
                    self.assertNotIn("\n",command)
                    self.assertEqual(item["permission_level"],2)
                    self.assertNotIn(" @p",command)
                    self.assertNotIn(" @r",command)
                    # Never expose unbounded target selectors or unguarded
                    # offensive player targeting to an ordinary /tarot user.
                    if "minecraft:" in command and any(
                        ("minecraft:"+effect) in command for effect in
                        ("slowness", "wither", "weakness", "blindness", "mining_fatigue")
                    ):
                        self.assertTrue(any(tag in command for tag in safe),
                                        (slug,name,command))
                    self.assertTrue(
                        command.startswith("execute at @s run effect ") or
                        command.startswith("execute at @s positioned ^ ^ ^8 ") or
                        command == "experience add @s 1 points",
                        (slug,name,command))

    def test_single_target_uses_are_native_and_do_not_fake_cooldowns(self):
        for slug,seq,name in (("devil",6,"Devil's Mark"),
                              ("hermit",7,"Hex"),("judgement",7,"Question")):
            key = self.index[(slug,seq,norm(name))]
            p = self.compiled[key["power_id"]]
            self.assertEqual(p["type"],"origins:action_on_entity_use")
            self.assertEqual(p["bientity_condition"]["condition"]["tag"],
                             "tarot:hostile")
            self.assertNotIn("cooldown",p)
            self.assertEqual(key["status"],"partial")

    def test_alone_penalty_is_real_and_persistent(self):
        self.assertEqual(IDENTITY_DRAWBACK_NAMES["lovers"],"Separation Anxiety")
        p=self.compiled["tarot:lovers/9_separation_anxiety"]
        self.assertEqual(p["type"],"origins:multiple")
        self.assertEqual(p["exhaustion"]["modifier"]["value"],0.35)
        self.assertEqual(p["mining"]["modifier"]["value"],-0.15)
        for subpower in ("mining","exhaustion"):
            self.assertEqual(p[subpower]["condition"]["type"],"origins:scoreboard")
            self.assertEqual(p[subpower]["condition"]["objective"],"a_alone_time")
            self.assertEqual(p[subpower]["condition"]["compare_to"],600)


class BulkGeneratorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.artifacts=build(output=Path(cls.tmp.name))
        cls.pack=ZipFile(cls.artifacts["only"])
    @classmethod
    def tearDownClass(cls):
        cls.pack.close()
        cls.tmp.cleanup()

    def read(self, name):
        return self.pack.read("data/tarot_arcane/functions/"+name+".mcfunction").decode()

    def test_alone_timer_runs_per_player_and_caps_without_overflow(self):
        tick=self.read("player/tick")
        self.assertIn("function tarot_arcane:player/alone",tick)
        self.assertIn("scoreboard players add @s a_alone_time 0",tick)
        alone=self.read("player/alone")
        self.assertIn("execute at @s if entity @a[distance=0.01..8]",alone)
        self.assertIn("execute at @s unless entity @a[distance=0.01..8]",alone)
        self.assertIn("scoreboard players set @s a_alone_time 601",alone)
        self.assertIn("scoreboard players add @s a_alone_time 1",alone)
        for slug in ("fool","lovers"):
            init=self.read("player/init/"+slug)
            self.assertIn("scoreboard players set @s a_alone_time 0",init)

    def test_lovers_native_drawback_is_not_reslottable(self):
        origin=json.loads(self.pack.read("data/tarot/origins/lovers.json"))
        self.assertIn("tarot:lovers/9_separation_anxiety",origin["powers"])
        kit=self.read("kits/lovers/s9")
        self.assertNotIn("separation_anxiety",kit)
        data=json.loads(Path(self.artifacts["manifest"]).read_text())
        entry=next(e for e in data["abilities"] if
                   e["family"]=="individual" and e["name"]=="Separation Anxiety")
        self.assertEqual(entry["status"],"partial")
        self.assertIn("same-team",entry["missing"])
        self.assertGreaterEqual(data["summary"]["compiled"],166)
        self.assertLessEqual(data["summary"]["blocked"],268)

    def test_all_bulk_power_paths_resolve_in_both_packs(self):
        for variant in ("only","addon"):
            with ZipFile(self.artifacts[variant]) as pack:
                for entries in BATCHES.values():
                    for slug,seq,name in entries:
                        canon=next(item for item in json.loads(
                            Path(self.artifacts["manifest"]).read_text())["abilities"]
                            if item["family"]=="individual" and
                            item["pathway"]==slug and item["sequence"]==seq and
                            norm(item["name"])==norm(name))
                        path="data/tarot/powers/"+canon["power_id"].split(":")[1]+".json"
                        self.assertIn(path,pack.namelist())
                        self.assertTrue(json.loads(pack.read(path))["type"].startswith("origins:"))
