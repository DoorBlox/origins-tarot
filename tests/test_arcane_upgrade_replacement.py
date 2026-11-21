"""Regression tests for Arcane Rev3 independently slotted upgrade replacement."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.full_build import build
from arcane_rev3.powers import compile_powers
from arcane_rev3.upgrade_policy import (
    SLOT_SOURCE, REPLACEMENTS, apply_replacement_conditions,
)


class UpgradeReplacementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers, cls.manifest, cls.kits = compile_powers(
            Path(__file__).resolve().parents[1]
        )

    def test_eight_exact_single_effect_upgrades_have_source_scoped_gate(self):
        self.assertEqual(len(REPLACEMENTS), 8)
        self.assertEqual(len({pair[0] for pair in REPLACEMENTS}), 8)
        for lower, upper in REPLACEMENTS:
            with self.subTest(lower=lower):
                self.assertIn(lower, self.powers)
                self.assertIn(upper, self.powers)
                old = self.powers[lower]
                self.assertNotEqual(old["type"], "origins:multiple")
                gate = old["condition"]
                if gate["type"] == "origins:and":
                    self.assertEqual(len(gate["conditions"]), 2)
                    gate = gate["conditions"][1]
                self.assertEqual(gate, {
                    "type": "origins:power",
                    "power": upper,
                    "source": SLOT_SOURCE,
                    "inverted": True,
                })

    def test_original_conditions_are_preserved_in_conjunction(self):
        for lower in (
            "tarot:devil/9_desperate_malice",
            "tarot:wheel_of_fortune/9_fate_intervenes",
            "tarot:hierophant/9_sanctified_ground",
        ):
            with self.subTest(lower=lower):
                value = self.powers[lower]
                self.assertEqual(value["condition"]["type"], "origins:and")
                old, upgrade_gate = value["condition"]["conditions"]
                self.assertNotEqual(old["type"], "origins:power")
                self.assertEqual(upgrade_gate["source"], SLOT_SOURCE)

    def test_replacement_application_idempotent_and_fail_closed(self):
        snapshot = copy.deepcopy(self.powers)
        apply_replacement_conditions(snapshot)
        self.assertEqual(snapshot, self.powers)
        with self.assertRaises(ValueError):
            apply_replacement_conditions({
                k: copy.deepcopy(v) for k, v in self.powers.items()
                if k != "tarot:moon/4_shaman"
            })

    def test_unrelated_identity_drawbacks_and_composite_power_untouched(self):
        for ident in (
            "tarot:lovers/9_separation_anxiety",
            "tarot:judgement/9_law_s_weight",
            "tarot:star/9_nightwatch",
        ):
            with self.subTest(ident=ident):
                value = self.powers[ident]
                self.assertNotIn("origins:power", json.dumps(value))

    def test_no_grant_changes_and_resonance_still_blocked(self):
        self.assertEqual(len(self.powers), 301)
        self.assertEqual(sum(x["status"] == "full" for x in self.manifest), 73)
        self.assertEqual(sum(x["status"] == "partial" for x in self.manifest), 228)
        self.assertEqual(sum(x["status"] == "blocked" for x in self.manifest), 133)
        for lower, upper in REPLACEMENTS:
            self.assertIn(lower, [x for seq in self.kits.values() for x in seq])
            self.assertIn(upper, [x for seq in self.kits.values() for x in seq])

    def test_both_generated_pack_variants_gate_old_effects(self):
        with tempfile.TemporaryDirectory() as d:
            artifacts = build(output=Path(d))
            for variant in ("only", "addon"):
                with self.subTest(variant=variant), ZipFile(artifacts[variant]) as z:
                    self.assertIsNone(z.testzip())
                    for lower, upper in REPLACEMENTS:
                        path = "data/tarot/powers/" + lower.split(":")[1] + ".json"
                        old = json.loads(z.read(path))
                        self.assertIn(upper, json.dumps(old["condition"]))
                    block = z.read(
                        "data/tarot_arcane/functions/ascend/check_s2.mcfunction"
                    ).decode()
                    self.assertIn("Resonance", block)
                    self.assertNotIn("clear @s", block)


if __name__ == "__main__":
    unittest.main()
