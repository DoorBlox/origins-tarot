"""Rev3 team-proximity conditions must not treat enemies as teammates.

HandbookRev2, Lovers Seq9 Linked Hearts and Benevolent Crown Seq9
Sovereign's Care explicitly require a nearby same-team player. A teamless,
opposing-team or unrelated spectator must not activate these self buffs.
"""
import unittest

from arcane_rev3.powers import compile_powers, norm
from arcane_rev3.team_policy import ROOT, nearby_ally_condition, team_names


class TeamProximityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers, cls.manifest, _ = compile_powers(ROOT)

    def _ability(self, pathway, name):
        matches = [
            row for row in self.manifest
            if row["pathway"] == pathway and norm(row["name"]) == norm(name)
        ]
        self.assertEqual(len(matches), 1)
        return self.powers[matches[0]["power_id"]], matches[0]

    def test_condition_requires_allowlisted_same_team_other_player(self):
        condition = nearby_ally_condition(8)
        self.assertEqual(condition["type"], "origins:or")
        self.assertEqual(len(condition["conditions"]), len(team_names()))
        commands = [x["command"] for x in condition["conditions"]]
        expected = [
            f"execute if entity @s[team={team}] at @s "
            f"if entity @a[team={team},distance=0.01..8]"
            for team in team_names()
        ]
        self.assertEqual(commands, expected)
        for entry in condition["conditions"]:
            self.assertEqual(entry["type"], "origins:command")
            self.assertEqual(entry["comparison"], ">=")
            self.assertEqual(entry["compare_to"], 1)
            self.assertNotIn("team=!", entry["command"])
            self.assertNotIn("@a[distance=", entry["command"])
            self.assertNotIn("team join ", entry["command"])

    def test_radius_validation_fails_closed(self):
        for invalid in (0, -1, 65, 8.0, True, "8", "8] run op @a"):
            with self.subTest(radius=invalid):
                with self.assertRaises(ValueError):
                    nearby_ally_condition(invalid)

    def test_linked_hearts_needs_teammate_not_arbitrary_player(self):
        power, manifest = self._ability("lovers", "Linked Hearts")
        self.assertEqual(power["condition"], nearby_ally_condition(8))
        self.assertEqual(power["type"], "origins:action_over_time")
        self.assertEqual(power["interval"], 500)
        self.assertEqual(manifest["status"], "partial")
        self.assertNotIn("Any nearby player triggers", manifest["missing"])
        self.assertIn("paired ally healing", manifest["missing"])

    def test_sovereigns_care_team_gates_speed_bonus(self):
        power, manifest = self._ability("benevolent_crown", "Sovereign's Care")
        self.assertEqual(
            power["together"]["condition"], nearby_ally_condition(8)
        )
        self.assertEqual(power["together"]["tick_rate"], 20)
        self.assertEqual(power["together"]["modifier"]["value"], 0.05)
        self.assertEqual(manifest["status"], "partial")
        self.assertNotIn("nearby ANY player", manifest["missing"])
        self.assertIn("self-healing", manifest["missing"])

    def test_no_unsafe_arbitrary_player_proximity_in_these_powers(self):
        for pathway, name in (
            ("lovers", "Linked Hearts"),
            ("benevolent_crown", "Sovereign's Care"),
        ):
            with self.subTest(ability=name):
                power, _ = self._ability(pathway, name)
                self.assertNotIn(
                    "@a[distance=0.01..8]", str(power),
                    "This would count an unlisted or opponent player as an ally",
                )


if __name__ == "__main__":
    unittest.main()
