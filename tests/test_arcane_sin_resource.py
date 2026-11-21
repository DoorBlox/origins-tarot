"""Hanged Man Sin: model-first, gameplay-scope and generated MC 1.18.2 contracts.

The source handbook requests exact per-hit 25% retained damage, 16HP
cap, 200 online-tick decay, 8HP trigger, team-safe burst, Trinity and
1200t capstone. The old runtime can sample damage_taken scoreboard but not
read per-source metadata or deal an arbitrary dynamic HP amount. Those gaps
MUST remain PARTIAL in the generated manifest.
"""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.full_build import build
from arcane_rev3.powers import compile_powers, norm
from arcane_rev3.sin_engine import SIN_SCORES

ROOT = Path(__file__).resolve().parents[1]
NAMES = (
    ("hanged_man", 9, "Sin-Bearing"),
    ("hanged_man", 5, "Burden Bearer"),
    ("hanged_man", 3, "Trinity"),
    ("hanged_man", 1, "Sin Overflow"),
    ("hanged_man", 1, "Depraved Dependent"),
    ("hanged_man", 0, "Weight of Sin Made Manifest"),
)


class SinEngineContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers, cls.manifest, cls.kits = compile_powers(ROOT)
        cls.lookup = {(m["pathway"], m["sequence"], norm(m["name"])): m
                      for m in cls.manifest if m["family"] == "individual"}
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = build(output=Path(cls.temp.name))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_six_real_sourced_sin_abilities_are_partial_not_placeholders(self):
        for slug, seq, name in NAMES:
            with self.subTest(name=name):
                m = self.lookup[slug, seq, norm(name)]
                self.assertEqual(m["status"], "partial")
                self.assertTrue(m["missing"])
                self.assertIn(m["power_id"], self.kits[slug, seq])
                self.assertIn(m["power_id"], self.powers)
                self.assertNotEqual(self.powers[m["power_id"]]["type"],
                                    "origins:simple")

    def test_expected_source_coverage_and_one_dietary_blocker(self):
        self.assertEqual(len(self.manifest), 434)
        self.assertEqual(len(self.powers), 433)
        self.assertEqual(sum(m["status"] == "full" for m in self.manifest), 73)
        self.assertEqual(sum(m["status"] == "partial" for m in self.manifest), 360)
        remaining = [m for m in self.manifest if m["status"] == "blocked"]
        self.assertEqual([(x["pathway"], x["sequence"], x["name"])
                          for x in remaining],
                         [("hierophant", 1, "Dietary Expansion")])
        self.assertEqual(sum(x["family"] == "resonance"
                             and x["status"] != "blocked"
                             for x in self.manifest), 110)

    def test_resource_store_uses_source_safe_scoreboards(self):
        self.assertEqual(len(SIN_SCORES), len(set(SIN_SCORES)))
        self.assertTrue(all(len(x) <= 16 for x in SIN_SCORES))
        for variant in ("only", "addon"):
            with ZipFile(self.output[variant]) as z:
                tick = z.read("data/tarot_arcane/functions/sin/tick.mcfunction").decode()
                on_hit = z.read("data/tarot_arcane/functions/sin/on_hit.mcfunction").decode()
                self.assertIn("a_dmg_taken", tick)
                self.assertIn("a_sin_seen", tick)
                self.assertIn("a_sin_idle matches 200..", tick)
                self.assertIn("a_sin_hp matches ..7", tick)
                self.assertIn("a_sin_delta", on_hit)
                self.assertIn("#4 a_const", on_hit)
                self.assertIn("a_sin matches 161..", on_hit)
                self.assertIn("a_sin_form matches 1..", on_hit)

    def test_burst_is_only_hostile_and_explicit_opponent_teams(self):
        for variant in ("only", "addon"):
            with ZipFile(self.output[variant]) as z:
                for file in ("burst_basic", "burst_overflow", "nova", "form_expire"):
                    text = z.read(
                        f"data/tarot_arcane/functions/sin/{file}.mcfunction"
                    ).decode()
                    self.assertNotIn("kill @a", text)
                    self.assertNotIn("execute as @a", text)
                    self.assertNotIn("op @", text)
                    self.assertNotIn("team join", text)
                    self.assertNotIn("fill ", text)
                    self.assertNotIn("setblock ", text)
                    self.assertNotIn("damage @a", text)
                    self.assertNotIn("@a[distance=..", text)
                    for line in text.splitlines():
                        if "effect give @a[" in line:
                            self.assertIn("if entity @s[team=tarot_", line)
                            self.assertIn("@a[team=tarot_", line)
                    if file != "form_expire":
                        self.assertIn("tarot:hostile", text)

    def test_revocation_pause_and_death_do_not_leave_residual_sin(self):
        for variant in ("only", "addon"):
            with ZipFile(self.output[variant]) as z:
                tick = z.read("data/tarot_arcane/functions/player/tick.mcfunction").decode()
                init = z.read("data/tarot_arcane/functions/player/init/hanged_man.mcfunction").decode()
                clear = z.read("data/tarot_arcane/functions/sin/clear.mcfunction").decode()
                for token in ("a_deaths", "a_seen_deaths", "sin/clear",
                              "a_sin_started", "power has @s tarot:hanged_man/9_sin_bearing",
                              "a_paused"):
                    self.assertIn(token, tick)
                self.assertIn("a_sin_started 0", init)
                for score in ("a_sin", "a_sin_started", "a_sin_form",
                              "a_sin_idle", "a_trinity_hits", "a_trinity_win"):
                    self.assertIn(f"@s {score} 0", clear)
                self.assertIn("a_sin_seen = @s a_dmg_taken", clear)

    def test_sin_permanent_burden_and_trinity_are_gated_to_power_ownership(self):
        b = self.powers["tarot:hanged_man/5_burden_bearer"]
        self.assertEqual(b["type"], "origins:modify_damage_taken")
        self.assertEqual(b["condition"]["type"], "origins:scoreboard")
        self.assertEqual(b["condition"]["objective"], "a_sin")
        self.assertAlmostEqual(b["modifier"]["value"], -0.10)
        tri = self.powers["tarot:hanged_man/3_trinity"]
        self.assertEqual(tri["cooldown"], 1)
        self.assertIn("sin/trinity_hit", json.dumps(tri))
        overflow = self.powers["tarot:hanged_man/1_sin_overflow"]
        self.assertIn("a_sin", json.dumps(overflow))

    def test_capstone_has_1200t_duration_14400t_cooldown_and_limited_debuff(self):
        p = self.powers["tarot:hanged_man/0_weight_of_sin_made_manifest"]
        self.assertEqual(p["type"], "origins:multiple")
        self.assertEqual(p["activate"]["type"], "origins:active_self")
        self.assertEqual(p["activate"]["cooldown"], 14400)
        self.assertEqual(p["activate"]["key"]["key"], "key.origins.primary_active")
        self.assertIn("sin/form_start", json.dumps(p["activate"]))
        self.assertEqual(p["reduction"]["type"], "origins:modify_damage_taken")
        self.assertAlmostEqual(p["reduction"]["modifier"]["value"], -0.75)
        for variant in ("only", "addon"):
            with ZipFile(self.output[variant]) as z:
                start = z.read("data/tarot_arcane/functions/sin/form_start.mcfunction").decode()
                tick = z.read("data/tarot_arcane/functions/sin/form_tick.mcfunction").decode()
                self.assertIn("a_sin_form 1200", start)
                self.assertIn("#80 a_const", tick)
                self.assertIn("sin/form_expire", tick)
                self.assertIn("power has @s tarot:hanged_man/0_weight_of_sin_made_manifest", tick)

    def test_trinity_three_hit_window_is_bounded_and_resets(self):
        for variant in ("only", "addon"):
            with ZipFile(self.output[variant]) as z:
                hit = z.read("data/tarot_arcane/functions/sin/trinity_hit.mcfunction").decode()
                proc = z.read("data/tarot_arcane/functions/sin/trinity_proc.mcfunction").decode()
                tick = z.read("data/tarot_arcane/functions/player/tick.mcfunction").decode()
                self.assertIn("a_trinity_win 100", hit)
                self.assertIn("a_trinity_hits matches 3..", hit)
                self.assertIn("resistance 3 1", proc)
                self.assertIn("a_trinity_hits 0", proc)
                self.assertIn("a_trinity_win 1..", tick)


if __name__ == "__main__":
    unittest.main()
