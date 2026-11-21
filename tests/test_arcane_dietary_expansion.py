"""Hierophant fish-only dietary carveout keeps the ORIGINAL pinned identity.

On Seq9 the permanent Sacred Dietary Vow prevents ALL meat/fish.
If the Seq1 Dietary Expansion power is explicitly granted from Arcane's
slot source, fish becomes edible while nonfish meat stays permanently banned.
Rev3's ordinary Seq1 Resonance mechanics are separate, so source coverage
does not imply that an individual Seq1 kit is player-equipable in normal mode.
"""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.powers import compile_powers, norm
from arcane_rev3.full_build import build
from arcane_rev3.upgrade_policy import SLOT_SOURCE


ROOT = Path(__file__).resolve().parents[1]
VOW = "tarot:hierophant/9_sacred_dietary_vow"
UPGRADE = "tarot:hierophant/1_dietary_expansion"
FISH = {
    "cod", "cooked_cod", "salmon", "cooked_salmon",
    "tropical_fish", "pufferfish",
}


class HierophantDietaryExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers, cls.manifest, cls.kits = compile_powers(ROOT)

    def test_final_source_coverage_is_honest_and_has_no_blocked_catalog_entries(self):
        self.assertEqual(len(self.powers), 434)
        self.assertEqual(len(self.manifest), 434)
        self.assertEqual(sum(m["status"] == "blocked" for m in self.manifest), 0)
        self.assertEqual(sum(m["status"] == "full" for m in self.manifest), 73)
        self.assertEqual(sum(m["status"] == "partial" for m in self.manifest), 361)
        self.assertTrue(all(m["power_id"] for m in self.manifest))
        self.assertTrue(all(m["missing"] for m in self.manifest
                            if m["status"] == "partial"))

    def test_fish_and_nonfish_tags_are_exact_disjoint_partition_of_meat(self):
        tags = json.loads((ROOT / "arcane/tags.json").read_text())
        fish = set(tags["items/fish"])
        banned = set(tags["items/nonfish_meat"])
        original = set(tags["items/meat"])
        self.assertEqual(fish, FISH)
        self.assertFalse(fish & banned)
        self.assertEqual(fish | banned, original)
        self.assertTrue(banned)
        self.assertEqual(len(fish) + len(banned), len(original))

    def test_seq9_vow_stays_pinned_and_always_bans_nonfish_meat(self):
        original = self.powers[VOW]
        self.assertEqual(original["type"], "origins:multiple")
        self.assertEqual(original["nonfish"]["type"], "origins:prevent_item_use")
        self.assertEqual(original["nonfish"]["item_condition"],
                         {"type": "origins:ingredient",
                          "ingredient": {"tag": "tarot:nonfish_meat"}})
        self.assertNotIn("condition", original["nonfish"],
                         "Nonfish identity cannot be disabled by a source upgrade")
        self.assertIn(VOW, self.kits[("hierophant", 9)],
                      "The compiler must retain the identity before the full builder pins it")

    def test_fish_ban_is_active_without_upgrade_and_inverse_when_granted(self):
        vow = self.powers[VOW]
        fish_ban = vow["fish"]
        self.assertEqual(fish_ban["type"], "origins:prevent_item_use")
        self.assertEqual(fish_ban["item_condition"]["ingredient"]["tag"],
                         "tarot:fish")
        self.assertEqual(fish_ban["condition"], {
            "type": "origins:power", "power": UPGRADE,
            "source": SLOT_SOURCE, "inverted": True,
        })
        expansion = self.powers[UPGRADE]
        self.assertEqual(expansion["type"], "origins:prevent_item_use")
        self.assertEqual(expansion["item_condition"]["ingredient"]["tag"],
                         "tarot:nonfish_meat")
        m = next(m for m in self.manifest if m["pathway"] == "hierophant"
                 and m["sequence"] == 1 and norm(m["name"]) == norm("Dietary Expansion"))
        self.assertEqual(m["status"], "partial")
        self.assertIn("Seq1", m["missing"])
        self.assertIn(UPGRADE, self.kits[("hierophant", 1)])

    def test_generated_both_variants_pin_original_and_include_fish_carveout(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = build(ROOT, output=Path(tmp))
            for variant in ("only", "addon"):
                with self.subTest(variant=variant), ZipFile(output[variant]) as z:
                    origin = json.loads(z.read("data/tarot/origins/hierophant.json"))
                    self.assertIn(VOW, origin["powers"])
                    original = json.loads(z.read(
                        "data/tarot/powers/hierophant/9_sacred_dietary_vow.json"))
                    expansion = json.loads(z.read(
                        "data/tarot/powers/hierophant/1_dietary_expansion.json"))
                    self.assertEqual(original["type"], "origins:multiple")
                    self.assertEqual(original["fish"]["condition"]["power"], UPGRADE)
                    self.assertEqual(expansion["type"], "origins:prevent_item_use")
                    for tag in ("fish", "nonfish_meat"):
                        path = "data/tarot/tags/items/" + tag + ".json"
                        self.assertIn(path, z.namelist())
                        self.assertTrue(json.loads(z.read(path))["values"])
                    kit = z.read(
                        "data/tarot_arcane/functions/kits/hierophant/s9.mcfunction").decode()
                    self.assertNotIn(VOW, kit)
            manifest = json.loads(Path(output["manifest"]).read_text())
            self.assertEqual(manifest["summary"]["compiled"], 434)
            self.assertEqual(manifest["summary"]["blocked"], 0)


if __name__ == "__main__":
    unittest.main()
