"""Operator-gated, fail-closed Seq2 -> Seq1 development transition.

A 110/110 source-compiled Resonance is NOT a 110/110 handbook-complete
Resonance. All player gameplay remains gated without OP test permission.
These tests verify only generated functions/schema; not an actual 1.18.2
Minecraft server, packet/keybind, source replay or permission runtime.
"""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.full_build import (
    IDENTITY_DRAWBACK_NAMES, PARTNER_IDENTITY_SOURCE,
    RESONANCE_SOURCE, SOURCE, build,
)
from arcane_rev3.model import PAIRS
from arcane_rev3.model import PATHWAYS, PARTNER
from arcane_rev3.powers import compile_powers
from progression.catalog import ACT_MARKS, RITUALS


ROOT = Path(__file__).resolve().parents[1]


class Seq1DevelopmentTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiled, cls.manifest, cls.kits = compile_powers(ROOT)
        cls.tmp = tempfile.TemporaryDirectory()
        cls.artifacts = build(output=Path(cls.tmp.name))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def read(self, pack, function):
        return pack.read(
            "data/tarot_arcane/functions/" + function + ".mcfunction"
        ).decode()

    def test_all_pairs_compile_ten_unique_power_definitions(self):
        self.assertEqual(len(PAIRS), 11)
        for primary, secondary, pair in PAIRS:
            with self.subTest(pair=pair):
                values = [ident for seq in range(9, -1, -1)
                          for ident in self.kits.get((pair, seq), [])]
                self.assertEqual(len(values), 10)
                self.assertEqual(len(set(values)), 10)
                self.assertTrue(all(x in self.compiled for x in values))

    def test_default_no_permission_cannot_spend_ritual_items(self):
        for variant in ("only", "addon"):
            with self.subTest(variant=variant), ZipFile(
                    self.artifacts[variant]) as pack:
                gate = self.read(pack, "ascend/check_s2")
                self.assertIn("unless score @s a_rtest matches 1", gate)
                self.assertIn("Resonance is locked", gate)
                self.assertIn("if score @s a_rtest matches 1", gate)
                self.assertIn("function tarot_arcane:ascend/check_s2_dev", gate)
                self.assertNotIn("clear @s", gate)
                self.assertNotIn("scoreboard players remove", gate)

                load = self.read(pack, "load")
                self.assertIn("scoreboard objectives add a_rtest dummy", load)
                for primary in PATHWAYS:
                    init = self.read(pack, f"player/init/{primary}")
                    self.assertIn("scoreboard players set @s a_rtest 0", init)
                enabled = self.read(pack, "admin/enable_seq1_dev")
                self.assertIn("a_seq matches 2", enabled)
                self.assertIn("a_mode matches 1", enabled)
                self.assertIn("unless score @s a_paused matches 1", enabled)
                self.assertNotIn("power grant", enabled)
                disabled = self.read(pack, "admin/disable_seq1_dev")
                self.assertIn("a_mode matches 0..1", disabled)
                self.assertIn("mode matches 2", disabled)

                alias = json.loads(Path(self.artifacts["alias"]).read_text())
                self.assertNotIn("enable_seq1", json.dumps(alias))
                self.assertNotIn("disable_seq1", json.dumps(alias))
                # Both direct operator admin functions must be distinct from
                # the clickable player-only /trigger menu.
                for name in pack.namelist():
                    if not (name.endswith(".mcfunction") and
                            "/functions/ui/" in name):
                        continue
                    ui = pack.read(name).decode()
                    self.assertNotIn("enable_seq1_dev", ui)
                    self.assertNotIn("disable_seq1_dev", ui)

    def test_test_ritual_checks_then_spends_exact_offer_and_marks(self):
        first, second = tuple(RITUALS[2].items())
        item1, count1 = first
        item2, count2 = second
        for variant in ("only", "addon"):
            with self.subTest(variant=variant), ZipFile(
                    self.artifacts[variant]) as pack:
                check = self.read(pack, "ascend/check_s2_dev")
                self.assertIn(f"clear @s minecraft:{item1} 0", check)
                self.assertIn(f"clear @s minecraft:{item2} 0", check)
                self.assertNotIn(f"clear @s minecraft:{item1} {count1}", check)
                self.assertIn("a_seq matches 2", check)
                self.assertIn("a_mode matches 1", check)
                self.assertIn("a_rtest matches 1", check)
                self.assertIn("a_ok matches 1 run function tarot_arcane:ascend/commit_s2_dev", check)
                commit = self.read(pack, "ascend/commit_s2_dev")
                self.assertIn(f"clear @s minecraft:{item1} {count1}", commit)
                self.assertIn(f"clear @s minecraft:{item2} {count2}", commit)
                self.assertIn(f"scoreboard players remove @s a_marks {ACT_MARKS[2]}", commit)
                self.assertIn("scoreboard players set @s a_seq 1", commit)
                self.assertIn("scoreboard players set @s a_mode 2", commit)
                self.assertIn("scoreboard players set @s a_max 0", commit)
                for n in range(1, 9):
                    self.assertIn(
                        f"scoreboard players set @s a_s{n} 0", commit)
                self.assertIn("function tarot_arcane:powers/refresh", commit)

    def test_op_enabled_resonance_contains_ten_powers_and_secondary_identity(self):
        self.assertEqual(len(IDENTITY_DRAWBACK_NAMES), 21)
        for variant in ("only", "addon"):
            with self.subTest(variant=variant), ZipFile(
                    self.artifacts[variant]) as pack:
                refresh = self.read(pack, "powers/refresh")
                reconcile = self.read(pack, "powers/reconcile")
                for source in (SOURCE, RESONANCE_SOURCE,
                               PARTNER_IDENTITY_SOURCE):
                    self.assertIn(f"power revokeall @s {source}", refresh)
                for first, second, pair in PAIRS:
                    expected = [ident for seq in range(9, -1, -1)
                                for ident in self.kits[(pair, seq)]]
                    for primary, partner in ((first, second), (second, first)):
                        with self.subTest(pair=pair, primary=primary):
                            grant = self.read(pack, f"resonance/{primary}/grant")
                            granted = [line for line in grant.splitlines()
                                       if line.startswith("power grant @s tarot:")]
                            # Ten kit powers PLUS exactly one partner identity.
                            self.assertEqual(len(granted), 11)
                            self.assertEqual(granted[:10], [
                                f"power grant @s {ident} {RESONANCE_SOURCE}"
                                for ident in expected])
                            if partner == "fool":
                                ident = "tarot:fool/identity_spiritual_expenditure"
                            else:
                                # From the primary Origin's pinned Seq9 drawback.
                                ident = next(
                                    x for x in self.compiled
                                    if x.startswith(f"tarot:{partner}/9_")
                                    and self.compiled[x]["name"] ==
                                    IDENTITY_DRAWBACK_NAMES[partner])
                            self.assertEqual(granted[-1],
                                f"power grant @s {ident} {PARTNER_IDENTITY_SOURCE}")
                            repair = self.read(pack, f"resonance/{primary}/repair")
                            self.assertEqual(
                                sum("power has @s " in x for x in repair.splitlines()),
                                11)
                            for code in (refresh, reconcile):
                                lines = [x for x in code.splitlines()
                                         if f"resonance/{primary}/" in x]
                                self.assertEqual(len(lines), 1)
                                self.assertIn("if score @s a_mode matches 2", lines[0])
                                self.assertIn("if score @s a_rtest matches 1", lines[0])
                                self.assertIn("unless score @s a_paused matches 1", lines[0])
                                self.assertIn("if score @s a_path matches ", lines[0])
                                self.assertIn("if score @s a_partner matches ", lines[0])
                # Old slot grants are not eligible in resonance mode.
                for line in refresh.splitlines():
                    if "function tarot_arcane:kits/" in line:
                        self.assertIn("a_mode matches 0..1", line)

    def test_admin_pause_resume_is_source_scoped_and_no_auto_trigger(self):
        for variant in ("only", "addon"):
            with self.subTest(variant=variant), ZipFile(
                    self.artifacts[variant]) as pack:
                pause = self.read(pack, "admin/rollback_player")
                resume = self.read(pack, "admin/resume_player")
                for source in (SOURCE, RESONANCE_SOURCE,
                               PARTNER_IDENTITY_SOURCE):
                    self.assertIn("power revokeall @s " + source, pause)
                self.assertIn("scoreboard players set @s a_paused 1", pause)
                self.assertIn("scoreboard players set @s a_paused 0", resume)
                self.assertIn("function tarot_arcane:powers/refresh", resume)
                self.assertNotIn("scoreboard players set @s a_rtest 0", resume)
                self.assertNotIn("scoreboard players set @s a_seq 2", resume)
                self.assertIn("player/periodic",
                              self.read(pack, "player/tick"))
                for name in pack.namelist():
                    if "dev/resonance/" in name:
                        self.fail(f"Manual preview leaked into normal pack: {name}")


if __name__ == "__main__":
    unittest.main()
