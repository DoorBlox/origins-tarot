"""Minecraft 1.18.2 vanilla-team PvP targeting is opt-in and fail closed."""
import json
import re
import tempfile
import unittest
from pathlib import Path

from arcane_rev3.powers import compile_powers
from arcane_rev3.team_policy import (
    ROOT, ally_effect, enemy_effect, player_effect, team_names,
)


class TeamPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers, cls.manifest, cls.kits = compile_powers(ROOT)

    def test_explicit_allowlisted_teams_and_neutral_unassigned(self):
        teams = team_names()
        self.assertEqual(
            teams, ("tarot_red", "tarot_blue", "tarot_green", "tarot_gold"))
        config = json.loads((ROOT / "arcane" / "teams.json").read_text())
        self.assertEqual(
            config["unassigned_players"], "neutral_no_player_damage_or_debuffs")
        self.assertEqual(config["mode"], "explicit_vanilla_teams")

    def test_enemy_effect_has_only_cross_team_commands(self):
        teams = team_names()
        a = enemy_effect("slowness", 160, 10, 1)
        self.assertEqual(a["type"], "origins:and")
        self.assertEqual(len(a["actions"]), len(teams) * (len(teams) - 1))
        for source in teams:
            for target in teams:
                found = [act["command"] for act in a["actions"]
                         if (f"@s[team={source}]" in act["command"]
                             and f"@a[team={target},distance=..10]"
                             in act["command"])]
                self.assertEqual(len(found), int(source != target))
                if found:
                    self.assertEqual(
                        found[0], f"execute if entity @s[team={source}] at @s "
                                  f"run effect give @a[team={target},distance=..10] "
                                  "minecraft:slowness 8 1 true")
        for v in a["actions"]:
            self.assertEqual(v["type"], "origins:execute_command")
            self.assertEqual(v["permission_level"], 2)
            self.assertNotIn("team join", v["command"])
            self.assertNotIn("team=!", v["command"])
            self.assertNotIn("@a[distance=", v["command"])
            self.assertNotIn("minecraft.selector", v["command"])

    def test_ally_effect_affects_only_own_team_not_self(self):
        a = ally_effect("regeneration", 200, 15)
        self.assertEqual(len(a["actions"]), len(team_names()))
        for source in team_names():
            matches = [v["command"] for v in a["actions"]
                       if f"@s[team={source}]" in v["command"]]
            self.assertEqual(matches, [
                f"execute if entity @s[team={source}] at @s run effect give "
                f"@a[team={source},distance=0.01..15] "
                "minecraft:regeneration 10 0 true"
            ])

    def test_reject_invalid_team_names_and_unsafe_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "arcane").mkdir()
            file = root / "arcane" / "teams.json"
            base = {
                "mode": "explicit_vanilla_teams",
                "unassigned_players": "neutral_no_player_damage_or_debuffs",
                "teams": ["tarot_red", "tarot_blue"]
            }
            for bad in (
                ["tarot_red", "tarot_red"],
                ["tarot_red", "red] run op @a"],
                ["tarot_red", ""],
                ["tarot_red"],
                ["tarot_red", "tarot_blue"] * 5,
            ):
                with self.subTest(teams=bad):
                    file.write_text(json.dumps({**base, "teams": bad}))
                    with self.assertRaises(ValueError):
                        team_names(root)
            file.write_text(json.dumps(base))
            for name in ("speed\nop @a", ";", "minecraft:poison"):
                with self.subTest(effect=name):
                    with self.assertRaises(ValueError):
                        player_effect(name, 100, 5, root=root)
            with self.assertRaises(ValueError):
                player_effect("poison", 101, 5, root=root)
            with self.assertRaises(ValueError):
                player_effect("poison", 100, 1000, root=root)

    def test_modified_combat_definitions_have_team_routed_actions(self):
        targets = {
            "tarot:judgement/1_order": ("slowness", "weakness"),
            "tarot:devil/1_chaos_unleashed": ("slowness", "weakness"),
            "tarot:strength/0_the_giant_s_decay": ("wither", "slowness"),
            "tarot:star/0_the_starless_sky": ("blindness", "slowness"),
            "tarot:impossible_fist/0_the_impossible_fist": ("wither", "slowness"),
            "tarot:starless_poison/0_the_starless_poison": ("blindness", "poison"),
        }
        def walk(node):
            if isinstance(node, dict):
                if node.get("type") == "origins:execute_command":
                    yield node["command"]
                for value in node.values():
                    yield from walk(value)
            elif isinstance(node, list):
                for value in node:
                    yield from walk(value)
        for ident, effects in targets.items():
            with self.subTest(ability=ident):
                self.assertIn(ident, self.powers)
                commands = list(walk(self.powers[ident]))
                for effect in effects:
                    self.assertEqual(
                        sum("run effect give @a[team=" in c and
                            f"minecraft:{effect}" in c for c in commands),
                        len(team_names()) * (len(team_names()) - 1))
        for ident in ("tarot:sun/0_the_eternal_day",
                      "tarot:benevolent_crown/0_the_benevolent_crown"):
            with self.subTest(ally_ability=ident):
                self.assertIn(ident, self.powers)
                commands = list(walk(self.powers[ident]))
                self.assertGreaterEqual(
                    sum("distance=0.01.." in c and
                        "@s[team=" in c for c in commands),
                    len(team_names()))

    def test_no_pvp_teams_automatically_created_by_the_builder(self):
        from arcane_rev3.full_build import build
        from zipfile import ZipFile
        with tempfile.TemporaryDirectory() as temp:
            paths = build(output=Path(temp))
            for label in ("only", "addon"):
                with ZipFile(paths[label]) as z:
                    functions = "\n".join(z.read(name).decode()
                        for name in z.namelist() if name.endswith(".mcfunction"))
                    self.assertNotIn("team add ", functions)
                    self.assertNotIn("team join ", functions)
                    self.assertNotIn("team modify ", functions)
                    self.assertIn("Resonance is locked", functions)


if __name__ == "__main__":
    unittest.main()
