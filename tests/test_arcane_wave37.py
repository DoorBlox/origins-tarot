"""Rev2 wave 2: 28 pair and nine individual effects, with release-lock assertions."""
import json
import re
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from arcane_rev3.batches import resonance2, individual3
from arcane_rev3.powers import compile_powers, norm
from arcane_rev3.full_build import build
from arcane_rev3.team_policy import team_names

ROOT=Path(__file__).resolve().parents[1]
RES={
 "marked_verdict":["Paper Sentence","Hunter's Calm","Puppet's Sentence","Marked Judgment","Hunter's Stillness"],
 "burning_archive":["Astrologer's Trail","Recorded Plot","Star Read Reaper","Insightful Flame"],
 "crumbling_reaper":["Grave Dirt + Fault Line","Spirit Shockwave","Guide's Foundation"],
 "benevolent_crown":["Coin's Blessing","Corrupt Symbiosis","Decree of Nature"],
 "binding_contract":["Devil's Verdict","Desire's Discipline","Infernal Verdict"],
 "starless_poison":["Soul Thread","Haunting Plague","Night Venom"],
 "eclipse":["Purify Scarlet","Sunrise"],
 "walking_sanctuary":["Rot Sanctum","Incorporeal Hymn"],
 "loaded_dice":["Ritual Winning","Fated Deduction"],
 "impossible_fist":["Doorstep Slam"],
}
IND={
 "chariot":["Reap"], "strength":["Bulwark","Twilight Blade"],
 "death":["Guide","Grave Whisper"],"judgement":["Verdict"],
 "moon":["Sanguine Resilience"],"lovers":["Nature's Step"],"sun":["Sanctify"],
}

class SecondWaveSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers,cls.manifest,cls.kits=compile_powers(ROOT)
        cls.index={(m["family"],m["pathway"],m["sequence"],norm(m["name"])):m
                   for m in cls.manifest}

    def test_28_resonance_plus_nine_individual_exactly_mapped(self):
        self.assertEqual(sum(map(len,RES.values())),28)
        self.assertEqual(sum(map(len,IND.values())),9)
        allnew=[]
        for family,module,expect in (("resonance",resonance2,RES),
                                     ("individual",individual3,IND)):
            values=[]
            module.register(lambda *args: values.append(args))
            self.assertEqual(len(values),sum(map(len,expect.values())))
            found={slug:set() for slug in expect}
            for slug,seq,name,power,*rest in values:
                self.assertIn(slug,expect)
                found[slug].add(name)
                item=self.index.get((family,slug,seq,norm(name)))
                self.assertIsNotNone(item,(slug,seq,name))
                self.assertEqual(item["status"],"partial",(slug,seq,name))
                self.assertTrue(item["missing"])
                self.assertIn(item["power_id"],self.powers)
                self.assertIn(item["power_id"],self.kits[(slug,seq)])
                self.assertEqual(rest[0],"partial")
                self.assertTrue(power["type"].startswith("origins:"))
                self.assertNotEqual(power["type"],"origins:simple")
                allnew.append(item["power_id"])
            self.assertEqual(found,{slug:set(names) for slug,names in expect.items()})
        self.assertEqual(len(allnew),37)
        self.assertEqual(len(set(allnew)),37)
        self.assertGreaterEqual(len(self.powers),402)
        self.assertEqual(sum(m["status"]=="full" for m in self.manifest),73)
        self.assertGreaterEqual(sum(m["status"]=="partial" for m in self.manifest),329)
        self.assertLessEqual(sum(m["status"]=="blocked" for m in self.manifest),32)

    def test_offensive_command_effects_do_not_target_player_selector(self):
        allnew=[]
        for module in (resonance2,individual3):
            module.register(lambda *args: allnew.append(args[3]))
        for power in allnew:
            stack=[power]
            while stack:
                node=stack.pop()
                if isinstance(node,list):
                    stack.extend(node)
                elif isinstance(node,dict):
                    stack.extend(x for x in node.values() if isinstance(x,(dict,list)))
                    if node.get("type")=="origins:execute_command":
                        command=node["command"]
                        self.assertEqual(node["permission_level"],2)
                        self.assertNotIn("\n",command)
                        is_hostile_effect=any("minecraft:"+effect in command for effect in
                              ("slowness","weakness","wither","poison","blindness","mining_fatigue"))
                        if is_hostile_effect:
                            is_mob = ("@e[type=#tarot:hostile" in command or
                                      "@e[type=#tarot:undead" in command)
                            # Player harm requires an explicitly configured
                            # DIFFERENT team: no teammate, neutral or
                            # teamless collateral, and bounded range.
                            match = re.fullmatch(
                                r"execute if entity @s\[team=([^\]]+)\] at @s "
                                r"run effect give @a\[team=([^,]+),distance=\.\.(\d+)\] "
                                r"minecraft:[a-z_]+ \d+ \d+ true", command)
                            safe_enemy = bool(
                                match and match.group(1) in team_names() and
                                match.group(2) in team_names() and
                                match.group(1) != match.group(2) and
                                1 <= int(match.group(3)) <= 64
                            )
                            self.assertTrue(is_mob or safe_enemy, command)
                            self.assertNotIn(" @a[distance=", command)
                        # Unlike unrestricted @a, explicitly scoped ally
                        # effects are allowed for a confirmed source rule.
                        self.assertNotIn(" op ",command)

    def test_cooldowns_and_safety_fail_closed_examples(self):
        skills=self.powers
        twilight=skills["tarot:strength/2_twilight_blade"]
        self.assertEqual(twilight["cooldown"],3600)
        self.assertEqual(twilight["target_condition"]["tag"],"tarot:hostile")
        reaper=skills["tarot:death/9_grave_whisper"]
        self.assertEqual(reaper["entity_action"]["chance"],0.10)
        self.assertEqual(reaper["bientity_condition"]["condition"]["tag"],"tarot:undead")
        self.assertEqual(skills["tarot:lovers/1_nature_s_step"]["cooldown"],2400)


class SecondWavePackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.artifacts=build(output=Path(cls.tmp.name))
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_both_variants_contain_new_powers_but_still_lock_seq1(self):
        data=json.loads(Path(self.artifacts["manifest"]).read_text())
        self.assertGreaterEqual(data["summary"]["compiled"],402)
        self.assertLessEqual(data["summary"]["blocked"],32)
        newpower_ids=set()
        for module in (resonance2,individual3):
            items=[]
            module.register(lambda *args: items.append(args))
            for slug,seq,name,*_ in items:
                match=[item for item in data["abilities"]
                       if item["pathway"]==slug and item["sequence"]==seq
                          and norm(item["name"])==norm(name)]
                self.assertEqual(len(match),1)
                newpower_ids.add(match[0]["power_id"])
        self.assertEqual(len(newpower_ids),37)
        for variant in ("only","addon"):
            with ZipFile(self.artifacts[variant]) as pack:
                paths=set(pack.namelist())
                self.assertIsNone(pack.testzip())
                for identifier in newpower_ids:
                    path="data/tarot/powers/"+identifier.split(":")[1]+".json"
                    self.assertIn(path,paths)
                    self.assertNotEqual(json.loads(pack.read(path))["type"],"origins:simple")
                for slug in RES:
                    origin=json.loads(pack.read(f"data/tarot/origins/{slug}.json"))
                    self.assertEqual(origin["powers"],[])
                    self.assertTrue(origin["unchoosable"])
                asc=pack.read("data/tarot_arcane/functions/ascend/check_s2.mcfunction").decode()
                self.assertIn("Resonance is locked",asc)
                self.assertNotIn("clear @s",asc)
                self.assertNotIn("scoreboard players set @s a_mode 2",asc)
