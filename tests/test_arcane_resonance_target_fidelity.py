"""Multi-pathway faithful-targeting regressions for Rev3 source partials.

Only explicit vanilla combat teams are players; teamless and unrelated teams
are neutral. This source test does not assert in-game Minecraft acceptance.
"""
import unittest

from arcane_rev3.powers import compile_powers, norm
from arcane_rev3.team_policy import ROOT, team_names


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


class ResonanceTargetFidelityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiled, cls.manifest, cls.kits = compile_powers(ROOT)

    def get(self, pathway, name):
        rows = [r for r in self.manifest
                if r["pathway"] == pathway and norm(r["name"]) == norm(name)]
        self.assertEqual(len(rows), 1, (pathway, name))
        self.assertEqual(rows[0]["status"], "partial")
        return self.compiled[rows[0]["power_id"]], rows[0]

    def assert_effect(self, power, effect, ticks, radius, amp=0, *, ally=False):
        commands = [v["command"] for v in walk(power)
                    if v.get("type") == "origins:execute_command"]
        self.assertTrue(commands)
        for caster in team_names():
            targets = [caster] if ally else [t for t in team_names() if t != caster]
            for target in targets:
                distance = f"0.01..{radius}" if ally else f"..{radius}"
                expected = (f"execute if entity @s[team={caster}] at @s "
                            f"run effect give @a[team={target},distance={distance}] "
                            f"minecraft:{effect} {ticks // 20} {amp} true")
                self.assertIn(expected, commands)
        for command in commands:
            if "run effect give @a[" in command:
                self.assertIn("team=", command)
                self.assertNotIn("team=!", command)
            self.assertNotIn("team join ", command)
            self.assertNotIn("team add ", command)

    def test_other_team_aoe_is_scoped_and_not_global(self):
        cases = (
            ("marked_verdict", "Hunter's Stillness", "slowness", 60, 6, 0),
            ("burning_archive", "Star Read Reaper", "glowing", 100, 15, 0),
            ("burning_archive", "Insightful Flame", "slowness", 40, 2, 0),
            ("benevolent_crown", "Corrupt Symbiosis", "slowness", 100, 5, 0),
            ("starless_poison", "Night Venom", "poison", 60, 5, 0),
            ("paper_martyr", "Suffering Sight", "glowing", 100, 10, 0),
            ("paper_martyr", "Suffering Sight II", "glowing", 60, 10, 0),
            ("eclipse", "Lunar Sanctuary", "wither", 100, 10, 0),
            ("tower", "Falling Tower", "slowness", 100, 6, 1),
        )
        for slug, name, effect, ticks, radius, amp in cases:
            with self.subTest(ability=name):
                value, _ = self.get(slug, name)
                self.assert_effect(value, effect, ticks, radius, amp)

    def test_temporary_ally_support_is_team_only(self):
        cases = (
            ("benevolent_crown", "Corrupt Symbiosis", "regeneration", 100, 5),
            ("benevolent_crown", "Emperor's Hymn", "regeneration", 200, 6),
            ("benevolent_crown", "Emperor's Hymn", "speed", 200, 6),
        )
        for slug, name, effect, ticks, radius in cases:
            with self.subTest(ability=name, effect=effect):
                value, _ = self.get(slug, name)
                self.assert_effect(value, effect, ticks, radius, ally=True)

    def test_star_read_reaper_only_usable_at_night(self):
        value, _ = self.get("burning_archive", "Star Read Reaper")
        self.assertEqual(value.get("condition"),
                         {"type": "origins:daytime", "inverted": True})

    def test_all_mechanics_remain_truthfully_partial(self):
        self.assertEqual(len(self.manifest), 434)
        self.assertEqual(sum(r["status"] == "partial" for r in self.manifest), 361)
        self.assertEqual(sum(r["status"] == "full" for r in self.manifest), 73)
        self.assertEqual(sum(r["status"] == "blocked" for r in self.manifest), 0)


if __name__ == "__main__":
    unittest.main()
