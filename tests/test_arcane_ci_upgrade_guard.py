"""Failing-first PR/base Arcane upgrade-safety regressions (source-only)."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from scripts.arcane_ci_upgrade_guard import compare_arcane_zips


def write_pack(path, *, power="9_identity", criterion="dummy",
               identity=True, slot=1909, source="tarot_arcane:slot_grants",
               remove_function=False, other_identity=False, destructive=False):
    with ZipFile(path, "w") as z:
        z.writestr("pack.mcmeta", json.dumps({"pack": {"pack_format": 9}}))
        z.writestr("data/origins/origin_layers/origin.json", json.dumps({
            "replace": True, "origins": ["tarot:moon"]
        }))
        z.writestr("data/tarot/origins/moon.json", json.dumps({
            "powers": (["tarot:moon/9_identity"] if identity else []) +
                (["tarot:moon/9_other"] if other_identity else []),
            "name": "Moon",
        }))
        for name in {"9_identity", power}:
            z.writestr(f"data/tarot/powers/moon/{name}.json",
                       json.dumps({"type": "origins:simple"}))
        z.writestr("data/tarot_arcane/functions/load.mcfunction",
                   f"scoreboard objectives add a_seq {criterion}\n"
                   "scoreboard objectives add a_path dummy\n"
                   "scoreboard objectives add a_s1 dummy\n"
                   + ("scoreboard objectives remove a_seq\n" if destructive else ""))
        z.writestr("data/tarot_arcane/functions/player/init/moon.mcfunction",
                   "scoreboard players set @s a_path 19\n"
                   "scoreboard players set @s a_partner 20\n"
                   "scoreboard players set @s a_seq 9\n"
                   f"scoreboard players set @s a_s1 {slot}\n")
        if not remove_function:
            z.writestr("data/tarot_arcane/functions/powers/grant.mcfunction",
                       f"power grant @s tarot:moon/9_identity {source}\n")


class ArcaneUpgradeSafetyTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.previous = Path(t.name) / "old.zip"
        self.candidate = Path(t.name) / "new.zip"
        write_pack(self.previous)

    def compare(self, **kwargs):
        write_pack(self.candidate, **kwargs)
        return compare_arcane_zips(self.previous, self.candidate)

    def test_same_build_is_safe_to_compare_but_not_gameplay_certified(self):
        r = self.compare()
        self.assertTrue(r["static_compatibility"], r["blockers"])
        self.assertEqual(r["blockers"], [])
        self.assertFalse(r["gameplay_accepted"])
        self.assertFalse(r["playerdata_migrated"])

    def test_additive_power_does_not_break_old_ids(self):
        r = self.compare(power="8_new_ability")
        self.assertTrue(r["static_compatibility"], r["blockers"])

    def test_cannot_remove_previously_saved_origin_power_id(self):
        write_pack(self.candidate, power="8_new")
        # Preserve an otherwise valid archive; remove ONLY one persisted
        # power ID. Missing mandatory metadata must not mask this regression.
        with ZipFile(self.candidate) as z:
            members = {name: z.read(name) for name in z.namelist()
                       if name != "data/tarot/powers/moon/9_identity.json"}
        with ZipFile(self.candidate, "w") as z:
            for name, payload in members.items():
                z.writestr(name, payload)
        r = compare_arcane_zips(self.previous, self.candidate)
        self.assertIn("removed_power_ids", r["blockers"])
        self.assertFalse(r["static_compatibility"])

    def test_change_objective_criteria_fails_closed(self):
        r = self.compare(criterion="trigger")
        self.assertIn("scoreboard_objective_changed", r["blockers"])

    def test_change_starting_slot_encoding_is_migration_risk(self):
        r = self.compare(slot=2009)
        self.assertIn("player_initializer_changed", r["blockers"])

    def test_remove_immutable_origin_identity_fails_closed(self):
        r = self.compare(identity=False)
        self.assertIn("pinned_origin_power_removed", r["blockers"])

    def test_remove_named_function_still_used_by_legacy_players_fails(self):
        r = self.compare(remove_function=True)
        self.assertIn("function_id_removed", r["blockers"])

    def test_rewriting_existing_power_grant_source_needs_migration(self):
        r = self.compare(source="tarot_arcane:other_source")
        self.assertIn("grant_source_changed", r["blockers"])

    def test_dangerous_cleanup_commands_fail_before_release(self):
        r = self.compare(destructive=True)
        self.assertIn("destructive_scoreboard_command", r["blockers"])

    def test_does_not_modify_any_archive_during_check(self):
        write_pack(self.candidate)
        old, new = self.previous.read_bytes(), self.candidate.read_bytes()
        compare_arcane_zips(self.previous, self.candidate)
        self.assertEqual(old, self.previous.read_bytes())
        self.assertEqual(new, self.candidate.read_bytes())


class CIWiringTests(unittest.TestCase):
    def test_pr_build_compares_base_main_both_zip_variants(self):
        flow = (Path(__file__).resolve().parents[1] /
                ".github/workflows/arcane-full.yml").read_text()
        self.assertIn("github.event.pull_request.base.sha", flow)
        self.assertIn("scripts.arcane_ci_upgrade_guard", flow)
        self.assertIn("baseline_source", flow)
        self.assertIn("--previous baseline_source/output/Arcane_Rev3_22_Origins_ONLY_DEV_1.18.2.zip", flow)
        self.assertIn("--previous baseline_source/output/Arcane_Rev3_22_Origins_ADDON_DEV_1.18.2.zip", flow)


if __name__ == "__main__":
    unittest.main()
