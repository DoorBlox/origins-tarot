"""SMP archive detection and migration checks: synthetic only, never mutate worlds."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from scripts.arcane_smp_preflight import audit_world, compare_upgrade, inspect_pack


def pack(path, *, kind="arcane", extra_powers=()):
    layer = {"replace": True, "origins": ["tarot:moon"]}
    description = "Arcane V2 Rev3 22-pathway DEV build; INCOMPLETE, TEST ONLY" if kind == "arcane" else "The Tarot Club | Passive-first V2 Alpha | 1.18.2"
    with ZipFile(path, "w") as z:
        z.writestr("pack.mcmeta", json.dumps({"pack": {"pack_format": 9, "description": description}}))
        z.writestr("data/origins/origin_layers/origin.json", json.dumps(layer))
        z.writestr("data/tarot/origins/moon.json", json.dumps({"powers": ["tarot:moon/9_blood_diet"]}))
        z.writestr("data/tarot/powers/moon/9_blood_diet.json", '{"type":"origins:prevent_item_use"}')
        for name in extra_powers:
            z.writestr(f"data/tarot/powers/moon/{name}.json", '{"type":"origins:action_over_time"}')
        if kind == "arcane":
            z.writestr("data/tarot_arcane/functions/load.mcfunction", "say Hello from Arcane\\n")
        else:
            z.writestr("data/tarot/powers/moon/passive.json", '{"type":"origins:night_vision"}')


class SMPPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.world = Path(self.tmp.name) / "world"
        self.dp = self.world / "datapacks"
        self.dp.mkdir(parents=True)

    def test_detects_real_source_family_not_just_filename(self):
        pack(self.dp / "misleading.zip", kind="legacy")
        d = inspect_pack(self.dp / "misleading.zip")
        self.assertEqual(d["family"], "legacy_tarot")
        self.assertFalse(d["is_arcane_rev3"])
        self.assertEqual(d["pack_format"], 9)

    def test_server_log_scenario_blocks_old_tarot_pack(self):
        pack(self.dp / "The_Tarot_Club_22_Arcana_Only_1.18.2.zip", kind="legacy")
        report = audit_world(self.world)
        self.assertFalse(report["can_test_arcane"])
        self.assertFalse(report["ready_for_smp"])
        self.assertIn("arcane_missing", report["blockers"])
        self.assertIn("legacy_tarot_present", report["blockers"])

    def test_conflicting_old_and_new_packs_fail_closed(self):
        pack(self.dp / "legacy.zip", kind="legacy")
        pack(self.dp / "Arcane_Rev3_22_Origins_ONLY_DEV_1.18.2.zip", kind="arcane")
        report = audit_world(self.world)
        self.assertFalse(report["can_test_arcane"])
        self.assertIn("multiple_tarot_packs", report["blockers"])

    def test_fresh_single_arcane_dev_is_only_test_eligible(self):
        pack(self.dp / "Arcane_Rev3_22_Origins_ONLY_DEV_1.18.2.zip", kind="arcane")
        report = audit_world(self.world)
        self.assertTrue(report["can_test_arcane"])
        self.assertFalse(report["ready_for_smp"])  # no actual acceptance evidence
        self.assertEqual(report["blockers"], [])
        self.assertEqual(report["pack_family"], "arcane_rev3")

    def test_upgrade_keeps_old_id_set_or_blocks(self):
        old = Path(self.tmp.name) / "old.zip"
        new = Path(self.tmp.name) / "new.zip"
        pack(old, extra_powers=("slot_retained",))
        pack(new, extra_powers=("other_ability",))
        result = compare_upgrade(old, new)
        self.assertIn("tarot:moon/slot_retained", result["removed_power_ids"])
        self.assertFalse(result["id_continuity"])
        pack(new, extra_powers=("other_ability", "slot_retained"))
        self.assertTrue(compare_upgrade(old, new)["id_continuity"])

    def test_cannot_claim_v2_to_rev3_migration(self):
        legacy = Path(self.tmp.name) / "legacy.zip"
        current = Path(self.tmp.name) / "rev3.zip"
        pack(legacy, kind="legacy")
        pack(current, kind="arcane")
        result = compare_upgrade(legacy, current)
        self.assertFalse(result["id_continuity"])
        self.assertIn("cross_family_migration_unsupported", result["blockers"])

    def test_read_only_audit_never_changes_contents(self):
        path = self.dp / "Arcane_Rev3_22_Origins_ONLY_DEV_1.18.2.zip"
        pack(path)
        before = path.read_bytes()
        state_before = sorted(p.relative_to(self.world) for p in self.world.rglob("*"))
        audit_world(self.world)
        self.assertEqual(before, path.read_bytes())
        self.assertEqual(state_before, sorted(p.relative_to(self.world) for p in self.world.rglob("*")))


if __name__ == "__main__":
    unittest.main()
