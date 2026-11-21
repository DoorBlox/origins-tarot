"""Regression for the TWO remaining errors in the second real MC 1.18.2 log.

At 03:16:06 Origins 1.4.1 rejected:
- tarot:temperance/9_unstable_manifestation -> chest.ingredient
- tarot:walking_sanctuary/9_wraith_s_prayer_chest -> chest.ingredient
The invalid list is under a restrict_armor slot, NOT a key literally named
'item_condition', so old static checks accidentally missed both definitions.
"""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.compat_141 import adapt_141
from arcane_rev3.full_build import build


ROOT = Path(__file__).resolve().parents[1]
ARMOR_SLOTS = ("head", "chest", "legs", "feet")
FAILED_POWER_FILES = (
    "data/tarot/powers/temperance/9_unstable_manifestation.json",
    "data/tarot/powers/walking_sanctuary/9_wraith_s_prayer.json",
)


def each_dict(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from each_dict(item)
    elif isinstance(value, list):
        for item in value:
            yield from each_dict(item)


class RestrictArmorCompat141Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.artifacts = build(output=Path(cls.tmp.name))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_all_emitted_ingredients_use_valid_1182_item_or_tag(self):
        for variant in ("only", "addon"):
            with self.subTest(variant=variant), ZipFile(self.artifacts[variant]) as z:
                files = [name for name in z.namelist()
                         if name.startswith("data/tarot/powers/")
                         and name.endswith(".json")]
                self.assertGreater(len(files), 402)
                for name in files:
                    for obj in each_dict(json.loads(z.read(name))):
                        if obj.get("type") != "origins:ingredient":
                            continue
                        ing = obj.get("ingredient")
                        self.assertIsInstance(ing, dict, (variant, name, obj))
                        self.assertEqual(
                            sum(x in ing for x in ("item", "tag")), 1,
                            (variant, name, ing))
                        self.assertNotIn("items", ing, (variant, name, ing))

    def test_both_actual_failed_powers_retain_valid_armor_restrictions(self):
        for variant in ("only", "addon"):
            with self.subTest(variant=variant), ZipFile(self.artifacts[variant]) as z:
                for path in FAILED_POWER_FILES:
                    with self.subTest(file=path):
                        self.assertIn(path, z.namelist())
                        value = json.loads(z.read(path))
                        restrictions = [x for x in each_dict(value)
                                        if x.get("type") == "origins:restrict_armor"]
                        self.assertGreaterEqual(len(restrictions), 1, path)
                        for restriction in restrictions:
                            for slot in ARMOR_SLOTS:
                                if slot not in restriction:
                                    continue
                                condition = restriction[slot]
                                self.assertIsInstance(condition, dict)
                                self.assertIn(condition.get("type"), (
                                    "origins:ingredient", "origins:or",
                                    "origins:and"))
                                for nested in each_dict(condition):
                                    if nested.get("type") == "origins:ingredient":
                                        ing = nested["ingredient"]
                                        self.assertTrue("item" in ing or "tag" in ing,
                                                        (path, slot, ing))
                                        self.assertNotIn("items", ing)

    def test_direct_chest_armor_list_is_or_not_an_ignored_items_array(self):
        raw = {"type": "origins:restrict_armor",
               "chest": {"type": "origins:ingredient",
                         "ingredient": {"items": [
                             "minecraft:iron_chestplate",
                             "minecraft:diamond_chestplate",
                             "minecraft:netherite_chestplate"]}}}
        cooked, rates, changes = adapt_141(raw)
        self.assertFalse(rates)
        self.assertIn("item_condition:ingredient_items_to_or", changes)
        chest = cooked["chest"]
        self.assertEqual(chest["type"], "origins:or")
        self.assertEqual([part["ingredient"]["item"]
                          for part in chest["conditions"]],
                         raw["chest"]["ingredient"]["items"])
        self.assertEqual(raw["chest"]["type"], "origins:ingredient")

    def test_nested_multiple_restrict_armor_and_all_four_slots(self):
        raw = {
            "type": "origins:multiple",
            "armor": {"type": "origins:restrict_armor",
                      slot: {"type": "origins:ingredient",
                             "ingredient": {"items": ["minecraft:iron_boots",
                                                      "minecraft:diamond_boots"]}}
                      for slot in ARMOR_SLOTS},
            "other": {"type": "origins:ingredient",
                      "ingredient": {"item": "minecraft:stone"}}}
        cooked, _, _ = adapt_141(raw)
        for slot in ARMOR_SLOTS:
            self.assertEqual(cooked["armor"][slot]["type"], "origins:or")
            self.assertEqual(
                len(cooked["armor"][slot]["conditions"]), 2)
        self.assertEqual(cooked["other"], raw["other"])

    def test_no_incorrect_armor_conversion_of_unrelated_chest_property(self):
        # Context-aware adaptation, not a blanket rewrite of any 'chest' key.
        raw = {"type": "example:unknown_power",
               "chest": {"type": "origins:ingredient",
                         "ingredient": {"items": ["minecraft:diamond"]}}}
        cooked, _, _ = adapt_141(raw)
        self.assertEqual(cooked, raw)


if __name__ == "__main__":
    unittest.main()
