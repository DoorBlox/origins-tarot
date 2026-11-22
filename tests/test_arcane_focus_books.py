"""Regression: paginated owned-only book focus flow for Minecraft 1.18.2."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.full_build import build
from arcane_rev3.powers import compile_powers
from arcane_rev3.active_focus import apply_active_focus, focus_kit_pages


def function(z, name):
    return z.read("data/tarot_arcane/functions/" + name + ".mcfunction").decode()


class FocusBookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiled, cls.manifest, cls.kits = compile_powers(Path(__file__).resolve().parents[1])
        cls.entries = apply_active_focus(cls.compiled)

    def test_each_kit_book_contains_only_owned_kit_active_powers(self):
        book_sets = focus_kit_pages(self.entries, self.kits)
        self.assertTrue(book_sets)
        for (path, seq), pages in book_sets.items():
            self.assertTrue(1 <= len(pages) <= 100)
            rendered = json.dumps(pages)
            allowed = {e["code"] for e in self.entries
                       if e["source_id"] in self.kits[(path, seq)]}
            for page in pages:
                for part in page["extra"]:
                    click = part.get("clickEvent", {})
                    if click.get("action") == "run_command":
                        self.assertTrue(click["value"].startswith("/trigger a_choose set "))
                        self.assertIn(int(click["value"].split()[-1]), allowed)
            self.assertNotIn("PARTIAL", rendered)
            self.assertNotIn("/function ", rendered)

    def test_focus_flow_is_book_based_and_filters_owned_slot_server_side(self):
        with tempfile.TemporaryDirectory() as temp:
            builds = build(output=Path(temp))
            for variant in ("only", "addon"):
                with ZipFile(builds[variant]) as z:
                    menu = function(z, "ui/focus/menu")
                    self.assertIn("ui/focus/index/1", menu)
                    self.assertIn("minecraft:written_book{", function(z, "ui/focus/index/1"))
                    self.assertNotIn("run tellraw @s", menu)
                    self.assertIn("tarotArcaneFocusIndex:1b", function(z, "ui/focus/index/1"))
                    self.assertIn("a_focus_kit", function(z, "load"))
                    tick = function(z, "player/tick")
                    self.assertIn("scoreboard players enable @s a_focus_kit", tick)
                    self.assertIn("ui/focus/open_kit", tick)
                    lookup = function(z, "ui/focus/open_kit")
                    self.assertIn("a_init matches 1", lookup)
                    self.assertIn("a_focus_kit matches", lookup)
                    self.assertIn("a_max matches", lookup)
                    self.assertIn("a_s1", lookup)
                    self.assertIn("a_focus_lookup", lookup)
                    self.assertIn("a_focus_lookup matches", lookup)
                    self.assertIn("tarot_arcane:ui/focus/book/", lookup)
                    self.assertNotIn("power grant", lookup)
                    books = [n for n in z.namelist()
                             if "/ui/focus/book/" in n and n.endswith(".mcfunction")]
                    self.assertGreater(len(books), 20)
                    for name in books:
                        src = z.read(name).decode()
                        self.assertIn("minecraft:written_book{", src)
                        self.assertNotIn("power grant", src)
                        self.assertNotIn("execute as @a", src)
                        self.assertNotIn("setblock", src)
                    choose = function(z, "ui/focus/choose")
                    self.assertIn("store success score @s a_ok run power has @s", choose)
                    self.assertIn("a_focus matches", function(z, "ui/focus/validate"))
                    self.assertIn("power revokeall @s tarot_arcane:ability_focus",
                                  function(z, "ui/focus/legacy"))

    def test_focus_book_has_legacy_and_only_vanilla_trigger_clicks(self):
        with tempfile.TemporaryDirectory() as temp:
            builds = build(output=Path(temp))
            with ZipFile(builds["only"]) as z:
                menus = [z.read(n).decode() for n in z.namelist()
                         if "/ui/focus/" in n and n.endswith(".mcfunction")]
                self.assertTrue(any("/trigger a_choose set 1" in src for src in menus))
                self.assertTrue(any("/trigger a_focus_kit set 1" in src for src in menus))
                self.assertTrue(any("/trigger a_choose set " in src for src in menus))
                self.assertFalse(any('"/op ' in src or '"/function ' in src for src in menus))


if __name__ == "__main__":
    unittest.main()
