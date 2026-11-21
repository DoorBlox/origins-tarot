"""End-to-end structural contracts for the 22-pathway Rev3 datapack build."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.full_build import build, alias, NUM, PATHWAYS, PAIRS
from arcane_rev3.powers import compile_powers


class CompleteCatalogTests(unittest.TestCase):
    def test_434_accounted_for_without_fake_powers(self):
        root = Path(__file__).resolve().parents[1]
        powers, manifest, kits = compile_powers(root)
        self.assertEqual(len(manifest), 434)
        self.assertTrue(0 < len(powers) < len(manifest))
        self.assertEqual(len({(x["family"], x["pathway"], x["sequence"], x["name"]) for x in manifest}),434)
        self.assertTrue(all(x["status"] in ("full","partial","blocked") for x in manifest))
        self.assertTrue(all(x["status"]!="blocked" for x in manifest if x["power_id"]))
        self.assertTrue(all(x["status"]=="blocked" and x["power_id"] is None
                            for x in manifest if not x["power_id"]))
        self.assertTrue(all(p["type"]!="origins:simple" for p in powers.values()))
        self.assertTrue(all(x["missing"] for x in manifest if x["status"]!="full"))
        self.assertIn("tarot:fool/9_spirit_vision", powers)
        self.assertIn("tarot:fool/9_clown_s_mischief", powers)

    def test_batch_two_native_effects_are_source_traced(self):
        from arcane_rev3.powers import norm
        root=Path(__file__).resolve().parents[1]
        powers,manifest,kits=compile_powers(root)
        expected={
            ("empress",9,"Mirror Veil"),
            ("emperor",4,"Fallen Aura"),
            ("wheel_of_fortune",9,"Fate's Current"),
            ("justice",4,"Emotional Push"),
            ("justice",9,"Patient Observation"),
            ("hanged_man",7,"Shadow Cloak"),
            ("sun",7,"Solar Flare"),
            ("sun",5,"Purify"),
            ("world",4,"Historical Recall"),
            ("tower",4,"Impact"),
            ("star",2,"Conceal"),
            ("hermit",1,"Prying Eyes"),
            ("sun",1,"Beacon of Faith II"),
        }
        for slug,seq,name in expected:
            key=next((m for m in manifest if m["family"]=="individual"
                      and m["pathway"]==slug and m["sequence"]==seq
                      and norm(m["name"])==norm(name)),None)
            self.assertIsNotNone(key,(slug,seq,name))
            self.assertEqual(key["status"],"partial" if name!="Solar Flare" else "full")
            self.assertIn(key["power_id"],powers)
            self.assertTrue(key["missing"] if key["status"]=="partial" else True)

    def test_fates_current_exact_six_equal_1_of_6_outcomes(self):
        root=Path(__file__).resolve().parents[1]
        powers,_,_=compile_powers(root)
        current=powers["tarot:wheel_of_fortune/9_fate_s_current"]
        self.assertEqual(current["type"],"origins:action_over_time")
        self.assertEqual(current["interval"],1800)
        choices=current["entity_action"]
        self.assertEqual(choices["type"],"origins:choice")
        self.assertEqual(len(choices["actions"]),6)
        self.assertEqual([a["weight"] for a in choices["actions"]],[1]*6)
        self.assertEqual({a["element"]["effect"]["effect"].split(":")[1]
                          for a in choices["actions"]},
                         {"speed","haste","absorption","hunger","slowness","mining_fatigue"})

    def test_undead_only_solar_flare_never_targets_regular_players(self):
        root=Path(__file__).resolve().parents[1]
        powers,_,_=compile_powers(root)
        flare=powers["tarot:sun/7_solar_flare"]
        self.assertEqual(flare["type"],"origins:attacker_action_when_hit")
        conditional=flare["entity_action"]
        self.assertEqual(conditional["type"],"origins:if_else")
        self.assertEqual(conditional["condition"]["tag"],"tarot:undead")
        self.assertEqual(conditional["if_action"]["chance"],0.2)
        self.assertEqual(conditional["if_action"]["action"]["effect"]["duration"],40)

    def test_alias_is_nonop_and_player_scoped(self):
        doc=alias()
        self.assertEqual((doc["schemaVersion"],doc["commandMode"],doc["command"],doc["permission"]),
                         (1,"COMMAND_CUSTOM","tarot",0))
        actions=[]
        def walk(item):
            self.assertEqual(item["permission"],0)
            actions.extend(item.get("actions",[]))
            for child in item.get("children",[]): walk(child)
        for child in doc["children"]:walk(child)
        actions.extend(doc["actions"])
        self.assertGreater(len(actions),1700)
        self.assertTrue(all(a["commandType"]=="CLIENT" and
                            a["command"].startswith("trigger a_") and
                            all(s not in a["command"].lower() for s in (" op ", "execute", "@a", "@e"))
                            for a in actions))


class FullBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.artifacts=build(output=Path(cls.tmp.name))
        cls.z=ZipFile(cls.artifacts["only"])
    @classmethod
    def tearDownClass(cls):
        cls.z.close()
        cls.tmp.cleanup()

    def test_full_pack_has_22_origin_choices_and_18_gliders(self):
        names=set(self.z.namelist())
        layer=json.loads(self.z.read("data/origins/origin_layers/origin.json"))
        self.assertEqual(layer["origins"], ["tarot:"+p for p in PATHWAYS])
        self.assertTrue(layer["replace"])
        for name in PATHWAYS:
            origin=json.loads(self.z.read(f"data/tarot/origins/{name}.json"))
            self.assertFalse(any("9_" in p for p in origin["powers"]),
                             "Sequence powers must remain revocable on slot change")
        gliders=sum("tarot:"+name+"/wings" in json.loads(
            self.z.read(f"data/tarot/origins/{name}.json"))["powers"] for name in PATHWAYS)
        self.assertEqual(gliders,18)
        for _,_,pair in PAIRS:
            self.assertEqual(json.loads(self.z.read(f"data/tarot/origins/{pair}.json"))["powers"],[])

    def test_every_generated_json_valid_and_files_referenced(self):
        names=set(self.z.namelist())
        self.assertIsNone(self.z.testzip())
        self.assertEqual(json.loads(self.z.read("pack.mcmeta"))["pack"]["pack_format"],9)
        for path in names:
            if path.endswith(".json"):
                with self.subTest(path=path):json.loads(self.z.read(path))
        for path in names:
            if path.endswith(".mcfunction"):
                txt=self.z.read(path).decode()
                for command in txt.splitlines():
                    if "function tarot_arcane:" in command:
                        tail=command.split("function tarot_arcane:")[1].split()[0]
                        self.assertIn("data/tarot_arcane/functions/"+tail+".mcfunction",names,
                                      path+" "+tail)

    def test_progression_and_slot_invariants(self):
        names=set(self.z.namelist())
        init=self.z.read("data/tarot_arcane/functions/player/init/fool.mcfunction").decode()
        self.assertIn("scoreboard players set @s a_partner 13",init)
        self.assertIn("scoreboard players set @s a_s1 109",init)
        s=self.z.read("data/tarot_arcane/functions/slot/assign.mcfunction").decode()
        self.assertIn("a_rpath = @s a_partner",s)
        self.assertIn("a_rseq >= @s a_seq",s)
        self.assertIn("a_rcode = @s a_s8",s)
        self.assertIn("a_mode matches 1",s)
        asc=self.z.read("data/tarot_arcane/functions/ascend/commit_s5.mcfunction").decode()
        self.assertIn("scoreboard players set @s a_s6 0",asc)
        self.assertIn("scoreboard players set @s a_mode 1",asc)
        self.assertIn("scoreboard players set @s a_max 6",asc)
        s1=self.z.read("data/tarot_arcane/functions/ascend/check_s2.mcfunction").decode()
        self.assertIn("Resonance is locked",s1)
        self.assertNotIn("clear @s",s1)
        self.assertIn("power revokeall @s tarot_arcane:slot_grants",
                      self.z.read("data/tarot_arcane/functions/powers/refresh.mcfunction").decode())
        self.assertIn("data/tarot_arcane/advancements/acting/fool_a.json",names)
        self.assertIn("data/tarot_arcane/advancements/acting/fool_b.json",names)

    def test_unimplemented_kits_denied_and_identity_drawback_kept(self):
        bad = self.z.read("data/tarot_arcane/functions/slot/assign.mcfunction").decode()
        self.assertIn("a_probe matches 0 run scoreboard players set @s a_ok 0", bad)
        origin = json.loads(self.z.read("data/tarot/origins/fool.json"))
        self.assertIn("tarot:fool/identity_spiritual_expenditure", origin["powers"])
        disadvantage = json.loads(
            self.z.read("data/tarot/powers/fool/identity_spiritual_expenditure.json"))
        self.assertEqual(disadvantage["type"], "origins:modify_exhaustion")
        self.assertEqual(disadvantage["modifier"]["value"], 0.25)
        self.assertEqual(
            {part["type"] for part in disadvantage["condition"]["conditions"]},
            {"origins:sprinting", "origins:fall_flying"})

    def test_one_ascension_only_per_player_command(self):
        """A player with banked marks and offerings cannot auto-chain levels."""
        checks=self.z.read("data/tarot_arcane/functions/ascend/check.mcfunction").decode().splitlines()
        self.assertIn("scoreboard players operation @s a_start_seq = @s a_seq",checks)
        self.assertIn("scoreboard players set @s a_marks_ok 0",checks)
        for seq in range(9,1,-1):
            dispatch="run function tarot_arcane:ascend/check_s"+str(seq)
            lines=[line for line in checks if dispatch in line]
            self.assertEqual(len(lines),1,"exactly one dispatch per original sequence")
            self.assertIn(f"if score @s a_start_seq matches {seq}",lines[0])
            self.assertNotIn(f"if score @s a_seq matches {seq}",lines[0])
        self.assertTrue(any("a_marks_ok matches 0 run tellraw" in line for line in checks),
                        "inventory errors must not also report acting mark failure")

    def test_unavailable_seq_two_to_one_does_not_consume_offerings(self):
        s = self.z.read("data/tarot_arcane/functions/ascend/check_s2.mcfunction").decode()
        self.assertIn("Resonance is locked",s)
        self.assertNotIn("clear @s",s)
        self.assertNotIn("scoreboard players remove @s a_marks",s)

    def test_rollback_persists_until_explicit_admin_resume(self):
        """Rollback must remain effective across ticks, relogs and manual refresh."""
        names=set(self.z.namelist())
        self.assertIn("data/tarot_arcane/functions/admin/resume_player.mcfunction", names)
        rollback=self.z.read("data/tarot_arcane/functions/admin/rollback_player.mcfunction").decode()
        self.assertIn("scoreboard players set @s a_paused 1",rollback)
        self.assertIn("power revokeall @s tarot_arcane:slot_grants",rollback)
        resume=self.z.read("data/tarot_arcane/functions/admin/resume_player.mcfunction").decode()
        self.assertIn("scoreboard players set @s a_paused 0",resume)
        self.assertIn("function tarot_arcane:powers/refresh",resume)
        tick=self.z.read("data/tarot_arcane/functions/player/tick.mcfunction").decode()
        self.assertIn("unless score @s a_paused matches 1",tick)
        self.assertIn("execute unless score @s a_init matches 1 unless score @s a_paused matches 1",tick)
        refresh=self.z.read("data/tarot_arcane/functions/powers/refresh.mcfunction").decode()
        reconcile=self.z.read("data/tarot_arcane/functions/powers/reconcile.mcfunction").decode()
        for code in (refresh,reconcile):
            for line in code.splitlines():
                if "power grant @s" in line or "function tarot_arcane:kits/" in line:
                    self.assertIn("unless score @s a_paused matches 1",line)
        init=self.z.read("data/tarot_arcane/functions/player/init/fool.mcfunction").decode()
        self.assertIn("scoreboard players set @s a_paused 0",init)

    def test_combat_lock_uses_1182_supported_statistics(self):
        """The player_hurt_entity advancement trigger is only in newer MC versions."""
        names=set(self.z.namelist())
        self.assertNotIn("data/tarot_arcane/advancements/events/combat_dealt.json",names)
        load=self.z.read("data/tarot_arcane/functions/load.mcfunction").decode()
        self.assertIn("scoreboard objectives add a_dmg_dealt minecraft.custom:minecraft.damage_dealt",load)
        self.assertIn("scoreboard objectives add a_dmg_taken minecraft.custom:minecraft.damage_taken",load)
        for obj in ("a_seen_dealt", "a_seen_taken",
                    "a_seen_bow", "a_seen_crossbow", "a_seen_trident"):
            self.assertIn(f"scoreboard objectives add {obj} dummy",load)
        for obj, weapon in (("a_bow","bow"), ("a_crossbow","crossbow"),
                            ("a_trident","trident")):
            self.assertIn(f"scoreboard objectives add {obj} minecraft.used:minecraft.{weapon}",load)
        stat=self.z.read("data/tarot_arcane/functions/player/combat_stats.mcfunction").decode()
        self.assertIn("if score @s a_dmg_dealt > @s a_seen_dealt",stat)
        self.assertIn("if score @s a_dmg_taken > @s a_seen_taken",stat)
        self.assertEqual(stat.count("run scoreboard players set @s a_combat 200"),5)
        for weapon in ("bow","crossbow","trident"):
            self.assertIn(f"if score @s a_{weapon} > @s a_seen_{weapon}",stat)
            self.assertIn(f"scoreboard players operation @s a_seen_{weapon} = @s a_{weapon}",stat)
        self.assertIn("scoreboard players operation @s a_seen_dealt = @s a_dmg_dealt",stat)
        self.assertIn("scoreboard players operation @s a_seen_taken = @s a_dmg_taken",stat)
        tick=self.z.read("data/tarot_arcane/functions/player/tick.mcfunction").decode()
        self.assertIn("function tarot_arcane:player/combat_stats",tick)
        init=self.z.read("data/tarot_arcane/functions/player/init/fool.mcfunction").decode()
        self.assertIn("scoreboard players operation @s a_seen_dealt = @s a_dmg_dealt",init)
        self.assertIn("scoreboard players operation @s a_seen_taken = @s a_dmg_taken",init)
        for weapon in ("bow","crossbow","trident"):
            self.assertIn(f"scoreboard players operation @s a_seen_{weapon} = @s a_{weapon}",init)
        for path in names:
            if "/advancements/" in path and path.endswith(".json"):
                advancement=json.loads(self.z.read(path))
                triggers={criterion.get("trigger") for criterion in advancement.get("criteria",{}).values()}
                self.assertNotIn("minecraft:player_hurt_entity",triggers,path)

    def test_player_ui_shows_arcana_names_instead_of_opaque_codes(self):
        names=set(self.z.namelist())
        render="data/tarot_arcane/functions/ui/slot_render.mcfunction"
        self.assertIn(render,names)
        fn=self.z.read(render).decode()
        self.assertIn("scoreboard players operation @s a_view_path = @s a_view_code",fn)
        self.assertIn("scoreboard players operation @s a_view_path /= #100 a_const",fn)
        self.assertIn("scoreboard players operation @s a_view_seq %= #100 a_const",fn)
        self.assertIn("if score @s a_view_code matches 0",fn)
        self.assertIn("The Fool",fn)
        self.assertIn("The Hanged Man",fn)
        self.assertEqual(sum("if score @s a_view_path matches " in l
                             for l in fn.splitlines()),22)
        root=self.z.read("data/tarot_arcane/functions/ui/slots.mcfunction").decode()
        self.assertNotIn("Kit code:",root)
        self.assertIn("function tarot_arcane:ui/slot_8",root)
        for slot in range(1,9):
            child=self.z.read(f"data/tarot_arcane/functions/ui/slot_{slot}.mcfunction").decode()
            self.assertIn(f"scoreboard players set @s a_view_slot {slot}",child)
            self.assertIn(f"scoreboard players operation @s a_view_code = @s a_s{slot}",child)
            self.assertIn("function tarot_arcane:ui/slot_render",child)
        primary=self.z.read("data/tarot_arcane/functions/ui/status_primary.mcfunction").decode()
        partner=self.z.read("data/tarot_arcane/functions/ui/status_partner.mcfunction").decode()
        for label in ("The Fool","The Hanged Man","The World","The Emperor"):
            self.assertIn(label,primary)
            self.assertIn(label,partner)
        status=self.z.read("data/tarot_arcane/functions/ui/status.mcfunction").decode()
        self.assertIn("Partner unlocks at Sequence 4",status)
        self.assertIn("function tarot_arcane:ui/status_primary",status)

    def test_no_java_kubejs_or_elevated_actions(self):
        self.assertTrue(all(not path.lower().endswith((".java",".js",".jar"))
                            for path in self.z.namelist()))
        for path in self.z.namelist():
            if path.endswith(".mcfunction"):
                commands=self.z.read(path).decode().splitlines()
                for command in commands:
                    # tellraw JSON is inert text, never a command token. A UI
                    # phrase like "auto-fill" must not trip the /fill safety gate.
                    executable = command.split("tellraw @s ",1)[0]
                    self.assertNotIn("op @",executable)
                    self.assertNotIn("setblock ",executable)
                    self.assertNotIn("fill ",executable)
                    self.assertNotIn("power clear ",executable)

    def test_report_accuracy_and_no_unearned_claims(self):
        x=json.loads(Path(self.artifacts["manifest"]).read_text())
        self.assertEqual(x["summary"]["specified"],434)
        self.assertEqual(x["summary"]["compiled"]+
                         x["summary"]["blocked"],434)
        self.assertEqual(x["summary"]["full"]+
                         x["summary"]["partial"], x["summary"]["compiled"])
        self.assertEqual(x["summary"]["live_minecraft_test"],"NOT RUN")
