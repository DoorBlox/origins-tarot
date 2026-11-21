"""2026-11-22 REAL-server regression: 49 decoder errors + 2 bad functions.

Unlike earlier static checks, this inspects the *emitted dev ZIPs* and
the actual nested data type position, not only top-level Origins power IDs.
Confirmed environment: Minecraft Java 1.18.2, Origins 1.4.1, Apoli 2.3.3.
"""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.compat_141 import adapt_141, chance_predicate, REQUIRED_COOLDOWN_TYPES
from arcane_rev3.full_build import build, NUM

ROOT = Path(__file__).resolve().parents[1]


def nodes(obj, context="power"):
    if isinstance(obj, list):
        for element in obj:
            yield from nodes(element, context)
    elif isinstance(obj, dict):
        yield context, obj
        for key, value in obj.items():
            if isinstance(value, (list, dict)):
                if key in ("condition", "entity_condition"):
                    sub = "item_condition" if context == "item_condition" else "entity_condition"
                elif key == "item_condition":
                    sub = "item_condition"
                elif key == "block_condition":
                    sub = "block_condition"
                elif key == "damage_condition":
                    sub = "damage_condition"
                elif key in ("entity_action", "action", "rising_action",
                             "falling_action", "actor_action", "target_action"):
                    sub = "entity_action"
                else:
                    sub = context
                yield from nodes(value, sub)


class RealServer141Regression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.paths = build(output=Path(cls.tmp.name))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_all_402_rendered_powers_reject_none_of_nine_observed_errors(self):
        for variant in ("only", "addon"):
            with self.subTest(variant=variant), ZipFile(self.paths[variant]) as z:
                names = [x for x in z.namelist()
                         if x.startswith("data/tarot/powers/") and x.endswith(".json")]
                self.assertGreaterEqual(len(names), 402 + 22)
                for name in names:
                    power = json.loads(z.read(name))
                    for context, obj in nodes(power):
                        kind = obj.get("type")
                        if kind is None:
                            continue
                        self.assertNotIn(kind, {"origins:random_teleport",
                            "origins:submerged", "origins:not"},
                            (name, context))
                        if context == "entity_condition":
                            self.assertNotEqual(kind, "origins:chance",
                                                (name, context))
                        if context == "item_condition" and kind == "origins:ingredient":
                            ing = obj.get("ingredient", {})
                            self.assertFalse("items" in ing, (name, ing))
                        if context == "power" and kind in REQUIRED_COOLDOWN_TYPES:
                            self.assertIsInstance(obj.get("cooldown"), int,
                                                  (name, kind))
                            self.assertGreater(obj["cooldown"], 0, (name, kind))
                        if context == "power" and kind == "origins:invisibility":
                            self.assertIsInstance(obj.get("render_armor"),
                                                  bool, name)

    def test_registered_predicates_match_all_adapted_chance_conditions(self):
        for variant in ("only", "addon"):
            with ZipFile(self.paths[variant]) as z:
                pred = {x for x in z.namelist()
                        if x.startswith("data/tarot_arcane/predicates/chance/")}
                self.assertTrue(pred)
                for name in (x for x in z.namelist()
                             if x.startswith("data/tarot/powers/") and x.endswith(".json")):
                    for ctx, value in nodes(json.loads(z.read(name))):
                        if value.get("type") == "origins:predicate" and (
                                value.get("predicate", "").startswith(
                                    "tarot_arcane:chance/")):
                            basis = value["predicate"].split("/")[-1]
                            target = "data/tarot_arcane/predicates/chance/" + basis + ".json"
                            self.assertIn(target, pred, name)
                            meta = json.loads(z.read(target))
                            self.assertEqual(meta["condition"],
                                             "minecraft:random_chance")
                            self.assertAlmostEqual(meta["chance"],
                                                   int(basis) / 1_000_000)

    def test_22_origin_owned_sync_functions_replace_unparseable_origin_has(self):
        for variant in ("only", "addon"):
            with self.subTest(variant=variant), ZipFile(self.paths[variant]) as z:
                contents = "\n".join(
                    z.read(n).decode() for n in z.namelist()
                    if n.endswith(".mcfunction"))
                self.assertNotIn("origin has origin", contents)
                for slug, num in NUM.items():
                    origin = json.loads(z.read(f"data/tarot/origins/{slug}.json"))
                    self.assertIn("tarot:"+slug+"/runtime_sync", origin["powers"])
                    native = json.loads(z.read(
                        f"data/tarot/powers/{slug}/runtime_sync.json"))
                    self.assertEqual(native["type"], "origins:action_over_time")
                    self.assertEqual(native["interval"], 20)
                    self.assertEqual(native["entity_action"]["command"],
                                     f"function tarot_arcane:player/sync/{slug}")
                    self.assertEqual(native["entity_action"]["permission_level"], 2)
                    sync = z.read(
                        f"data/tarot_arcane/functions/player/sync/{slug}.mcfunction"
                    ).decode()
                    self.assertIn(f"function tarot_arcane:player/init/{slug}", sync)
                    self.assertIn(f"unless score @s a_path matches {num}", sync)
                    self.assertNotIn("origin set", sync)
                self.assertIn("execute as @a", z.read(
                    "data/tarot_arcane/functions/tick.mcfunction").decode())

    def test_explicit_safe_bounded_teleport_instead_of_nonexistent_action(self):
        p = {"type": "origins:active_self", "cooldown": 200,
             "entity_action": {"type": "origins:random_teleport",
                 "area_width": 8, "area_height": 3,
                 "attempts": 20, "loaded_chunks_only": True}}
        v, chances, changes = adapt_141(p)
        self.assertFalse(chances)
        self.assertIn("bounded_overworld_surface_blink",
                      ",".join(changes))
        act = v["entity_action"]
        self.assertEqual(act["type"], "origins:execute_command")
        self.assertEqual(act["permission_level"], 2)
        self.assertEqual(act["command"],
                         "execute at @s if dimension minecraft:overworld "
                         "run spreadplayers ~ ~ 0 8 false @s")
        for bad in (0, -1, 17, "50"):
            with self.subTest(width=bad):
                p["entity_action"]["area_width"] = bad
                with self.assertRaises(ValueError):
                    adapt_141(p)

    def test_random_condition_preserves_probability_and_never_grants_invincibility(self):
        power = {"type": "origins:prevent_death", "condition":
            {"type": "origins:and", "conditions": [
                {"type": "origins:chance", "chance": 0.05},
                {"type": "origins:command", "command": "execute if score @s cd matches 0",
                 "comparison": ">=", "compare_to": 1}]}}
        adapted, chances, changes = adapt_141(power)
        self.assertEqual(chances, {50_000})
        self.assertEqual(adapted["condition"]["conditions"][0],
                         {"type":"origins:predicate",
                          "predicate":"tarot_arcane:chance/50000"})
        self.assertEqual(chance_predicate(50_000)["chance"], 0.05)
        self.assertEqual(adapted["condition"]["conditions"][1],
                         power["condition"]["conditions"][1])
        self.assertFalse(any(x.get("type") == "origins:chance"
                             for c, x in nodes(adapted) if c == "entity_condition"))
        self.assertEqual(power["condition"]["conditions"][0]["type"],
                         "origins:chance")

    def test_item_inversion_does_not_turn_into_positive_condition(self):
        value = {"type":"origins:prevent_item_use",
                 "item_condition":{"type":"origins:not",
                   "condition":{"type":"origins:ingredient",
                                "ingredient":{"item":"minecraft:beef"}}}}
        out, _, _ = adapt_141(value)
        self.assertEqual(out["item_condition"]["type"], "origins:ingredient")
        self.assertEqual(out["item_condition"]["inverted"], True)
        self.assertEqual(out["item_condition"]["ingredient"]["item"],
                         "minecraft:beef")
        other, _, _ = adapt_141({
            "type":"origins:prevent_item_use",
            "item_condition":{"type":"origins:ingredient",
                "ingredient":{"items":["minecraft:bow", "minecraft:crossbow"]}}})
        self.assertEqual(other["item_condition"]["type"], "origins:or")
        self.assertEqual(len(other["item_condition"]["conditions"]), 2)

    def test_missing_cooldown_is_explicit_not_client_default(self):
        src = {"type": "origins:self_action_on_kill",
               "entity_action": {"type": "origins:heal", "amount": 2}}
        compiled, _, log = adapt_141(src)
        self.assertEqual(compiled["cooldown"], 20)
        self.assertIn("power:missing_cooldown_20_ticks", log)
        self.assertNotIn("cooldown", src)


if __name__ == "__main__":
    unittest.main()
