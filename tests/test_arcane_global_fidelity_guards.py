"""Global 434-definition safety and truthful fidelity inventory regressions.

No broad harmful player selector and no fabricated "full" status.
"""
import re
import unittest

from arcane_rev3.powers import compile_powers
from arcane_rev3.team_policy import ROOT, team_names
from tools.arcane_fidelity_report import build_inventory

HARMFUL = {
    "slowness", "weakness", "wither", "poison", "blindness",
    "mining_fatigue", "nausea", "hunger", "levitation",
    "instant_damage", "darkness", "fatal_poison",
}

PLAYER_COMMAND = re.compile(
    r"execute if entity @s\[team=([^\]]+)\] at @s "
    r"run effect give @a\[team=([^,]+),distance=\.\.(\d+)\] "
    r"minecraft:([a-z_]+) \d+ \d+ true"
)
EFFECT_SELECTOR = re.compile(
    r"effect give (@[ae]\[[^\]]+\]) minecraft:([a-z_]+)"
)


def walk(node):
    if isinstance(node, dict):
        yield node
        for val in node.values():
            yield from walk(val)
    elif isinstance(node, list):
        for val in node:
            yield from walk(val)


class GlobalFidelityGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiled, cls.manifest, _ = compile_powers(ROOT)

    def test_all_command_based_negative_player_effects_are_safe(self):
        for ident, power in self.compiled.items():
            for node in walk(power):
                if node.get("type") != "origins:execute_command":
                    continue
                command = node["command"]
                self.assertNotIn("\n", command, ident)
                for selector, effect in EFFECT_SELECTOR.findall(command):
                    if effect not in HARMFUL:
                        continue
                    if selector.startswith("@e["):
                        # Hostile/undead entity type tags exclude players.
                        self.assertTrue(
                            "type=#tarot:hostile" in selector or
                            "type=#tarot:undead" in selector,
                            (ident, command))
                        continue
                    self.assertTrue(selector.startswith("@a["), (ident, command))
                    match = PLAYER_COMMAND.fullmatch(command)
                    self.assertIsNotNone(match, (ident, command))
                    source, target, radius, actual_effect = match.groups()
                    self.assertIn(source, team_names(), ident)
                    self.assertIn(target, team_names(), ident)
                    self.assertNotEqual(source, target, (ident, command))
                    self.assertGreaterEqual(int(radius), 1)
                    self.assertLessEqual(int(radius), 64)
                    self.assertEqual(effect, actual_effect)
                    self.assertNotIn("team join", command)

    def test_all_361_partials_have_concrete_ids_and_disclosed_gaps(self):
        report = build_inventory(ROOT)
        self.assertEqual(report["counts"], {
            "catalog": 434, "full": 73, "partial": 361, "blocked": 0
        })
        items = report["items"]
        self.assertEqual(len(items), 361)
        self.assertEqual(len({row["power_id"] for row in items}), 361)
        for row in items:
            self.assertTrue(row["missing"].strip())
            self.assertIn(row["power_id"], self.compiled)
            self.assertTrue(row["categories"])

    def test_fidelity_worklist_is_deterministic_and_sorted(self):
        first = build_inventory(ROOT)
        second = build_inventory(ROOT)
        self.assertEqual(first, second)
        self.assertEqual(first["items"],
                         sorted(first["items"],
                                key=lambda r: (r["family"], r["pathway"],
                                               -r["sequence"], r["power_id"])))
        self.assertTrue(all(isinstance(n, int) and n >= 0
                            for n in first["category_counts"].values()))
        self.assertGreater(sum(first["category_counts"].values()), 361,
                           "Overlapping missing-mechanic categories are allowed")


if __name__ == "__main__":
    unittest.main()
