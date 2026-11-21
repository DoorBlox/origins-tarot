"""Rev2-grounded, backward-compatible magic/combat source fidelity tests.

No new power IDs or scoreboard objectives; intentionally keeps the three
abilities PARTIAL until unimplemented client/game hooks have runtime evidence.
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


class MagicControlFidelityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers, cls.manifest, _ = compile_powers(ROOT)

    def get(self, pathway, sequence, name):
        matches = [
            row for row in self.manifest
            if row["pathway"] == pathway
            and row["sequence"] == sequence
            and norm(row["name"]) == norm(name)
        ]
        self.assertEqual(len(matches), 1, (pathway, sequence, name))
        row = matches[0]
        self.assertEqual(row["status"], "partial")
        return self.powers[row["power_id"]], row

    def test_magician_star_chart_crouch_and_night_both_required(self):
        obj, row = self.get("magician", 7, "Star Chart")
        self.assertEqual(obj["type"], "origins:active_self")
        self.assertEqual(obj["cooldown"], 1200)
        self.assertEqual(obj["condition"], {
            "type": "origins:and",
            "conditions": [
                {"type": "origins:sneaking"},
                {"type": "origins:daytime", "inverted": True},
            ],
        })
        self.assertIn("particle line", row["missing"])
        self.assertNotIn("night-only", row["missing"])

    def test_infernal_verdict_melee_applies_all_three_native_debuffs(self):
        obj, row = self.get("binding_contract", 4, "Infernal Verdict")
        self.assertEqual(obj["type"], "origins:target_action_on_hit")
        self.assertEqual(obj["cooldown"], 320)
        self.assertEqual(obj["target_condition"], {
            "type": "origins:in_tag", "tag": "tarot:hostile"
        })
        effects = [node["effect"] for node in walk(obj["entity_action"])
                   if node.get("type") == "origins:apply_effect"]
        actual = {(d["effect"], d["duration"]) for d in effects}
        self.assertIn(("minecraft:wither", 40), actual)
        self.assertIn(("minecraft:slowness", 40), actual)
        self.assertIn(("minecraft:glowing", 80), actual)
        self.assertIn("enemy players", row["missing"])
        self.assertNotIn("only Wither", row["missing"])

    def test_haunting_plague_affects_listed_enemy_players_not_neutrals(self):
        obj, row = self.get("starless_poison", 5, "Haunting Plague")
        self.assertEqual(obj["type"], "origins:active_self")
        self.assertEqual(obj["cooldown"], 900)
        commands = [node["command"] for node in walk(obj)
                    if node.get("type") == "origins:execute_command"]
        for caster in team_names():
            for opponent in team_names():
                if caster == opponent:
                    continue
                for effect in ("blindness", "poison"):
                    cmd = (f"execute if entity @s[team={caster}] at @s "
                           f"run effect give @a[team={opponent},distance=..6] "
                           f"minecraft:{effect} 3 0 true")
                    self.assertIn(cmd, commands)
        self.assertTrue(all("run effect give @a[" not in c or "team=" in c
                            for c in commands))
        self.assertTrue(all("team join " not in c and "team=!" not in c
                            for c in commands))
        self.assertIn("on-hit", row["missing"])
        self.assertNotIn("enemy players omitted", row["missing"])

    def test_id_catalog_and_partial_fidelity_are_preserved(self):
        self.assertEqual(len(self.manifest), 434)
        self.assertEqual(sum(x["status"] == "full" for x in self.manifest), 73)
        self.assertEqual(sum(x["status"] == "partial" for x in self.manifest), 361)


if __name__ == "__main__":
    unittest.main()
