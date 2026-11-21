"""Regression: Rev2 ally support and enemy AoE obey Rev3 combat team policy.

This suite tests exact emitted static selectors, durations and compatibility,
without treating a Python build as Minecraft 1.18.2 runtime acceptance.
"""
import unittest

from arcane_rev3.powers import compile_powers, norm
from arcane_rev3.team_policy import ROOT, team_names


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)


class TeamSupportWaveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers, cls.manifest, _ = compile_powers(ROOT)

    def power(self, family, pathway, name):
        rows = [row for row in self.manifest
                if row["family"] == family
                and row["pathway"] == pathway
                and norm(row["name"]) == norm(name)]
        self.assertEqual(len(rows), 1, (family, pathway, name))
        self.assertEqual(rows[0]["status"], "partial")
        return self.powers[rows[0]["power_id"]], rows[0]

    def assert_team_effect(self, power, effect, radius, ticks, amp=0, *, ally=True):
        self.assertEqual(ticks % 20, 0)
        commands = [node["command"] for node in walk(power)
                    if node.get("type") == "origins:execute_command"]
        for src in team_names():
            targets = (src,) if ally else (t for t in team_names() if t != src)
            for target in targets:
                dist = f"0.01..{radius}" if ally else f"..{radius}"
                expected = (f"execute if entity @s[team={src}] at @s "
                            f"run effect give @a[team={target},distance={dist}] "
                            f"minecraft:{effect} {ticks // 20} {amp} true")
                self.assertIn(expected, commands)
        self.assertTrue(all("team join " not in c and "team add " not in c
                            and "team=!" not in c for c in commands))
        unsafe = [c for c in commands
                  if "run effect give @a[" in c and "team=" not in c]
        self.assertEqual(unsafe, [], "No unfiltered player buff/debuff")

    def test_allied_regeneration_is_actually_team_scoped(self):
        cases = (
            ("individual", "lovers", "Nature's Step", 8, 200, 0),
            ("individual", "sun", "White Angel", 15, 300, 0),
            ("individual", "lovers", "The Garden", 15, 1800, 1),
            ("resonance", "walking_sanctuary", "Ghost Blessing", 8, 80, 0),
            ("resonance", "walking_sanctuary", "Mobile Sanctum", 3, 200, 0),
            ("resonance", "walking_sanctuary", "Spectral White Angel", 15, 300, 1),
            ("resonance", "walking_sanctuary", "The Walking Sanctuary", 15, 1200, 1),
            ("resonance", "benevolent_crown", "Linked Crown", 8, 80, 0),
        )
        for family, pathway, name, radius, ticks, amp in cases:
            with self.subTest(ability=name):
                definition, _ = self.power(family, pathway, name)
                self.assert_team_effect(
                    definition, "regeneration", radius, ticks, amp)

    def test_garden_speed_boost_excludes_opponents_and_neutrals(self):
        definition, _ = self.power("individual", "lovers", "The Garden")
        self.assert_team_effect(definition, "speed", 15, 1800)

    def test_aoe_enemy_effects_include_only_listed_other_teams(self):
        cases = (
            ("individual", "emperor", "Corrupt Ground", "slowness", 4, 100),
            ("individual", "empress", "Aura of Despair", "slowness", 5, 40),
            ("individual", "judgement", "Verdict's Weight", "slowness", 4, 40),
            ("individual", "hermit", "Star Read", "glowing", 15, 100),
            ("individual", "star", "Terror", "slowness", 5, 40),
        )
        for family, pathway, name, effect, radius, ticks in cases:
            with self.subTest(ability=name):
                definition, row = self.power(family, pathway, name)
                self.assert_team_effect(definition, effect, radius, ticks,
                                        ally=False)
                self.assertIn("partial", row["status"])

    def test_star_read_requires_night(self):
        definition, _ = self.power("individual", "hermit", "Star Read")
        self.assertEqual(definition["condition"],
                         {"type": "origins:daytime", "inverted": True})

    def test_no_source_count_inflation_or_false_full_fidelity(self):
        self.assertEqual(len(self.manifest), 434)
        self.assertEqual(sum(r["status"] == "full" for r in self.manifest), 73)
        self.assertEqual(sum(r["status"] == "partial" for r in self.manifest), 361)
        self.assertEqual(sum(r["status"] == "blocked" for r in self.manifest), 0)


if __name__ == "__main__":
    unittest.main()
