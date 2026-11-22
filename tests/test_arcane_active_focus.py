"""Source-verified, opt-in active ability selector for 1.18.2 Origins.

Multiple Rev3 active powers share primary/secondary keys; a focused mode
must not trigger other equipped active sources. Important: scoreboard
entity conditions cannot be evaluated client-side for Active Self in old
Origins, so use *synced source-owned power tokens* as the client gate.
Legacy behavior must remain the default until the player opts in.
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.active_focus import (
    FOCUS_SOURCE, FOCUS_ENABLED, apply_active_focus, token_id
)
from arcane_rev3.powers import compile_powers
from arcane_rev3.full_build import build, alias


ROOT = Path(__file__).resolve().parents[1]


def active_nodes(power):
    if not isinstance(power, dict):
        return
    kind = power.get("type")
    if kind == "origins:active_self":
        yield power
    elif kind == "origins:multiple":
        for key, item in power.items():
            if key not in ("condition", "name", "description", "type") and isinstance(item, dict):
                yield from active_nodes(item)


class ActiveFocusContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiled, cls.manifest, cls.kits = compile_powers(ROOT)

    def test_focus_ids_stable_and_unique_even_after_new_catalog_order(self):
        a = copy.deepcopy(self.compiled)
        b = dict(reversed(list(copy.deepcopy(self.compiled).items())))
        one = apply_active_focus(a)
        two = apply_active_focus(b)
        self.assertGreaterEqual(len(one), 30)
        self.assertEqual([x["focus_id"] for x in one],
                         [x["focus_id"] for x in two])
        self.assertEqual(len({x["code"] for x in one}), len(one))
        self.assertTrue(all(2 <= x["code"] <= 2_000_000_000 for x in one))
        self.assertEqual(len({x["token"] for x in one}), len(one))
        self.assertTrue(all(x["token"] == token_id(x["code"]) for x in one))
        self.assertEqual(len(self.compiled), 434)
        self.assertEqual(len(self.manifest), 434)

    def test_all_active_self_nodes_are_opt_in_gated_without_losing_conditions(self):
        originals = copy.deepcopy(self.compiled)
        changed = copy.deepcopy(self.compiled)
        entries = apply_active_focus(changed)
        self.assertTrue(entries)
        for ident, before in originals.items():
            nodes_before = list(active_nodes(before))
            nodes_after = list(active_nodes(changed[ident]))
            self.assertEqual(len(nodes_before), len(nodes_after), ident)
            for old, new in zip(nodes_before, nodes_after):
                original_cond = old.get("condition")
                gate = new.get("condition")
                self.assertIsInstance(gate, dict, ident)
                if original_cond is not None:
                    self.assertEqual(gate["type"], "origins:and")
                    self.assertEqual(gate["conditions"][0], original_cond)
                    gate = gate["conditions"][1]
                self.assertEqual(gate["type"], "origins:or")
                self.assertEqual(len(gate["conditions"]), 2)
                legacy, focused = gate["conditions"]
                self.assertEqual(legacy["type"], "origins:power")
                self.assertEqual(legacy["power"], FOCUS_ENABLED)
                self.assertTrue(legacy["inverted"])
                self.assertEqual(focused["type"], "origins:power")
                self.assertTrue(focused["power"].startswith("tarot_arcane:focus/token_"))
                self.assertNotIn("origins:scoreboard", json.dumps(gate),
                                 "Client key powers cannot read server-only scoreboard conditions")
        self.assertEqual(sum(len(list(active_nodes(x))) for x in changed.values()),
                         len(entries))

    def test_generated_focus_menu_is_owned_nonop_with_no_new_admin_privileges(self):
        with tempfile.TemporaryDirectory() as d:
            out = build(ROOT, output=Path(d))
            for variant in ("only", "addon"):
                with self.subTest(variant=variant), ZipFile(out[variant]) as z:
                    paths = set(z.namelist())
                    self.assertIn("data/tarot_arcane/powers/focus/enabled.json", paths)
                    power = json.loads(z.read("data/tarot_arcane/powers/focus/enabled.json"))
                    self.assertEqual(power["type"], "origins:simple")
                    self.assertTrue(power["hidden"])
                    menu = z.read("data/tarot_arcane/functions/ui/focus/menu.mcfunction").decode()
                    choose = z.read("data/tarot_arcane/functions/ui/focus/choose.mcfunction").decode()
                    validate = z.read("data/tarot_arcane/functions/ui/focus/validate.mcfunction").decode()
                    tick = z.read("data/tarot_arcane/functions/player/tick.mcfunction").decode()
                    load = z.read("data/tarot_arcane/functions/load.mcfunction").decode()
                    self.assertIn("scoreboard objectives add a_focus dummy", load)
                    self.assertIn("scoreboard objectives add a_choose trigger", load)
                    self.assertIn("scoreboard objectives add a_focus_menu trigger", load)
                    self.assertIn("a_focus_menu matches 1..", tick)
                    self.assertIn("a_choose matches 1..", tick)
                    self.assertIn("scoreboard players set @s a_focus 0", z.read(
                        "data/tarot_arcane/functions/player/init/moon.mcfunction").decode())
                    for text in (menu, choose, validate):
                        self.assertNotIn("op @", text)
                        self.assertNotIn("team join", text)
                        self.assertNotIn("execute as @a", text)
                        self.assertNotIn("setblock ", text)
                    self.assertIn("run power has @s tarot:", choose)
                    self.assertIn(FOCUS_SOURCE, z.read(
                        "data/tarot_arcane/functions/ui/focus/legacy.mcfunction").decode())
                    self.assertIn("minecraft:written_book{", menu)
                    self.assertIn("a_focus matches", validate)
                    self.assertIn("ui/focus/validate", z.read(
                        "data/tarot_arcane/functions/powers/refresh.mcfunction").decode())
                    self.assertIn("ui/focus/validate", z.read(
                        "data/tarot_arcane/functions/powers/reconcile.mcfunction").decode())
                    self.assertIn("power revokeall @s " + FOCUS_SOURCE, z.read(
                        "data/tarot_arcane/functions/admin/rollback_player.mcfunction").decode())
                    token_powers = [p for p in paths
                                    if p.startswith("data/tarot_arcane/powers/focus/token_")
                                    and p.endswith(".json")]
                    self.assertGreaterEqual(len(token_powers), 30)

    def test_alias_exposes_focus_without_new_admin_or_client_required(self):
        cmd = alias()
        focus = next(x for x in cmd["children"] if x["child"] == "focus")
        self.assertEqual(focus["permission"], 0)
        self.assertEqual(focus["actions"][0]["command"], "trigger a_focus_menu")
        legacy = next(x for x in focus["children"] if x["child"] == "legacy")
        self.assertEqual(legacy["actions"][0]["command"], "trigger a_choose set 1")

    def test_source_counts_unchanged_and_focus_not_fabricated_as_ability(self):
        _, manifest, _ = compile_powers(ROOT)
        self.assertEqual(len(manifest), 434)
        self.assertEqual(sum(m["status"] == "partial" for m in manifest), 361)
        self.assertEqual(sum(m["status"] == "full" for m in manifest), 73)
        self.assertEqual(sum(m["status"] == "blocked" for m in manifest), 0)
        self.assertFalse(any("focus/token" in (x["power_id"] or "")
                             for x in manifest))


if __name__ == "__main__":
    unittest.main()
