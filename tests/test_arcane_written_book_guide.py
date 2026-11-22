"""Minecraft 1.18.2 player-safe written guide books: structural contracts."""
import json
import re
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.full_build import build
from arcane_rev3.powers import compile_powers
from arcane_rev3.guide_books import general_pages, pathway_pages, book_nbt
from progression.catalog import CARDS, RITUALS


def function(archive, path):
    return archive.read(f"data/tarot_arcane/functions/{path}.mcfunction").decode()


class BookContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.data = build(output=Path(cls.tmp.name))

    def test_safe_book_triggers_exist_and_are_reset_for_both_variants(self):
        for variant in ("only", "addon"):
            with ZipFile(self.data[variant]) as z:
                load = function(z, "load")
                tick = function(z, "player/tick")
                for name in ("a_book", "a_tome", "a_partner_tome"):
                    self.assertIn(f"scoreboard objectives add {name} trigger", load)
                    self.assertIn(f"scoreboard players enable @s {name}", tick)
                    self.assertIn(f"scoreboard players set @s {name} 0", tick)
                    self.assertIn(f"if score @s {name} matches 1..", tick)
                self.assertIn("a_book", function(z, "ui/help"))
                self.assertIn("a_tome", function(z, "ui/help"))

    def test_general_guide_has_page_navigation_and_real_unlocks(self):
        pages = general_pages()
        self.assertGreaterEqual(len(pages), 10)
        self.assertLessEqual(len(pages), 100)
        flatten = json.dumps(pages)
        self.assertIn("change_page", flatten)
        self.assertIn("LOCKED", flatten)
        self.assertIn("Sequence 4", flatten)
        for card in CARDS:
            self.assertIn(card["name"], flatten)
        for seq in range(9, 2, -1):
            for item in RITUALS[seq]:
                self.assertIn(item.replace("_", " "), flatten)
        self.assertNotIn("nether star", flatten)  # blocked Seq1 offering is hidden
        for page in pages:
            self.assertLess(len(json.dumps(page)), 4000)

    def test_setup_tutorial_is_in_book_and_uses_only_player_triggers(self):
        pages = general_pages()
        text = json.dumps(pages)
        for phrase in ("SET UP POWERS", "FOCUS AND KEYS",
                       "SLOT EQUIPMENT", "PROGRESS DISPLAY",
                       "/trigger a_slots", "/trigger a_focus_menu",
                       "/trigger a_hud set 2"):
            self.assertIn(phrase, text)
        actions = [
            part["clickEvent"]["value"]
            for page in pages for part in page.get("extra", [])
            if part.get("clickEvent", {}).get("action") == "run_command"
        ]
        self.assertGreaterEqual(len(actions), 3)
        self.assertTrue(all(a.startswith("/trigger a_") for a in actions))
        self.assertTrue(all("/function " not in a for a in actions))

    def test_pathway_books_cover_source_abilities_honestly(self):
        compiled, manifest, kits = compile_powers(Path(__file__).resolve().parents[1])
        for card in CARDS:
            with self.subTest(pathway=card["slug"]):
                pages = pathway_pages(card["slug"], compiled, manifest, kits)
                body = json.dumps(pages, ensure_ascii=False)
                self.assertLessEqual(len(pages), 100)
                self.assertIn("What it does", body)
                self.assertIn("How to use", body)
                self.assertNotIn("PARTIAL", body)
                self.assertNotIn("Missing:", body)
                self.assertIn("Sequence", body)
                for row in manifest:
                    if (row["family"] == "individual" and
                            row["pathway"] == card["slug"] and row["sequence"] >= 2):
                        self.assertIn(row["name"], body)
                self.assertNotIn("power grant", body)
                self.assertNotIn("scoreboard players set", body)

    def test_commands_are_non_op_and_do_not_override_inventory_items(self):
        with ZipFile(self.data["only"]) as z:
            give = function(z, "ui/book/give")
            self.assertIn("minecraft:written_book{", give)
            self.assertIn("tarotArcaneGuide:1b", give)
            self.assertIn("clear @s", give)
            self.assertIn(" 0", give)  # probe only, no removal
            self.assertNotIn("item replace", give)
            self.assertNotIn("clear @s minecraft:written_book{tarotArcaneGuide:1b} 1", give)
            self.assertNotIn("op @s", give)
            partner = function(z, "ui/book/partner")
            self.assertIn("a_seq matches ..4", partner)
            self.assertIn("a_partner matches", partner)
            for card in CARDS:
                self.assertIn(f"ui/book/path_partner/{card['slug']}", partner)
                path = function(z, f"ui/book/path_partner/{card['slug']}")
                self.assertIn("tarotArcanePartnerTome:1b", path)
            tome = function(z, "ui/book/tome")
            for card in CARDS:
                self.assertIn(f"if score @s a_path matches {card['id']}", tome)
                self.assertIn(f"ui/book/path/{card['slug']}", tome)
                path = function(z, f"ui/book/path/{card['slug']}")
                self.assertIn("minecraft:written_book{", path)
                self.assertNotIn("power grant", path)

    def test_book_commands_are_player_trigger_only(self):
        with ZipFile(self.data["only"]) as z:
            for path in z.namelist():
                if "/ui/book/" not in path or not path.endswith(".mcfunction"):
                    continue
                src = z.read(path).decode()
                for cmd in re.findall(r'\\?"value\\?":\\?"(/[^"\\]+)', src):
                    self.assertTrue(cmd.startswith("/trigger a_"), (path, cmd))
                self.assertNotIn("/function tarot_arcane:admin/", src)

    def test_individual_opt_in_actionbar_hud_not_shared_bossbar(self):
        for variant in ("only", "addon"):
            with ZipFile(self.data[variant]) as z:
                load = function(z, "load")
                tick = function(z, "player/tick")
                self.assertIn("scoreboard objectives add a_hud trigger", load)
                self.assertIn("scoreboard objectives add a_hud_on dummy", load)
                self.assertIn("scoreboard objectives add a_hud_timer dummy", load)
                self.assertIn("scoreboard players enable @s a_hud", tick)
                self.assertIn("if score @s a_hud matches 1..", tick)
                self.assertIn("ui/hud/toggle", tick)
                self.assertIn("ui/hud/tick", tick)
                self.assertNotIn("bossbar add", tick)
                toggle = function(z, "ui/hud/toggle")
                self.assertIn("a_hud_on", toggle)
                self.assertIn("a_hud matches 3", toggle)
                display = function(z, "ui/hud/render")
                self.assertIn("title @s actionbar", display)
                self.assertIn("a_seq", display)
                self.assertIn("a_marks", display)
                self.assertIn("a_phase", display)
                for seq in range(9, 1, -1):
                    self.assertIn("a_seq matches " + str(seq), display)

    def test_without_commandaliases_book_actions_work_with_vanilla_trigger(self):
        with ZipFile(self.data["only"]) as z:
            tick = function(z, "player/tick")
            for trigger in ("a_book", "a_tome", "a_partner_tome", "a_hud"):
                self.assertIn("scoreboard players enable @s " + trigger, tick)
            help_text = function(z, "ui/help")
            for trigger in ("a_book", "a_tome", "a_partner_tome", "a_hud"):
                self.assertIn(trigger, help_text)

    def test_player_books_hide_developer_status_without_misrepresenting_effects(self):
        compiled, manifest, kits = compile_powers(Path(__file__).resolve().parents[1])
        for card in CARDS:
            pages = pathway_pages(card["slug"], compiled, manifest, kits)
            rendered = json.dumps(pages, ensure_ascii=False)
            for jargon in ("PARTIAL", "FULL SOURCE", "PARTIAL SOURCE",
                           "Missing:", "Current source abilities:",
                           "source-full", "Source-full", "compiled source"):
                self.assertNotIn(jargon, rendered, (card["slug"], jargon))
            self.assertIn("How to use", rendered)
            self.assertIn("What it does", rendered)
        general = json.dumps(general_pages(), ensure_ascii=False)
        self.assertNotIn("Partial powers", general)
        self.assertNotIn("developer", general.lower())

    def test_player_chat_and_manual_hide_diagnostic_labels(self):
        with ZipFile(self.data["only"]) as z:
            for name in z.namelist():
                if not name.startswith("data/tarot_arcane/functions/ui/"):
                    continue
                if not name.endswith(".mcfunction"):
                    continue
                content = z.read(name).decode()
                for jargon in ("[FULL]", "[PARTIAL]", " | FULL",
                               " | PARTIAL", "Currently in game (compiled source)",
                               "Limitations:", "Source-full", "OP-only Resonance test",
                               "incomplete powers remain PARTIAL"):
                    self.assertNotIn(jargon, content, (name, jargon))
        manual = self.data["player_manual"].read_text(encoding="utf8")
        for jargon in ("source-full", "PARTIAL", "Still missing:",
                       "Original intent", "compiled source", "power_id",
                       "source implementations"):
            self.assertNotIn(jargon, manual)
        self.assertIn("How to use", manual)
        self.assertIn("What it does", manual)
        self.assertIn("Sequence 1", manual)
        # Developer diagnostics are retained separately, not suppressed.
        dev = self.data["developer_ability_report"].read_text(encoding="utf8")
        self.assertIn("PARTIAL", dev)
        self.assertIn("Still missing", dev)

    def test_alias_has_book_and_tome(self):
        alias = json.loads(self.data["alias"].read_text())
        labels = {c["child"] for c in alias["children"]}
        self.assertTrue({"book", "tome", "partner-tome"}.issubset(labels))

    def test_book_jumps_do_not_point_outside_contents(self):
        compiled, manifest, kits = compile_powers(Path(__file__).resolve().parents[1])
        all_books = [general_pages()] + [
            pathway_pages(c["slug"], compiled, manifest, kits) for c in CARDS
        ]
        for pages in all_books:
            for page in pages:
                for obj in page["extra"]:
                    action = obj.get("clickEvent", {})
                    if action.get("action") == "change_page":
                        self.assertGreaterEqual(int(action["value"]), 1)
                        self.assertLessEqual(int(action["value"]), len(pages))

    def test_all_pathways_expose_clickable_ability_contents_and_weaknesses(self):
        compiled, manifest, kits = compile_powers(Path(__file__).resolve().parents[1])
        for card in CARDS:
            pages = pathway_pages(card["slug"], compiled, manifest, kits)
            links = [(part["text"], int(part["clickEvent"]["value"]))
                     for page in pages for part in page.get("extra", [])
                     if part.get("clickEvent", {}).get("action") == "change_page"]
            self.assertTrue(any("Weakness" in label for label, _ in links), card["slug"])
            self.assertTrue(any("Sequence 9" in label for label, _ in links), card["slug"])
            self.assertTrue(any("Sequence 2" in label for label, _ in links), card["slug"])
            self.assertTrue(any("Ability list" in label for label, _ in links), card["slug"])
            body = json.dumps(pages, ensure_ascii=False)
            self.assertIn("YOUR WEAKNESS", body)
            self.assertIn("What it does:", body)
            self.assertIn("How to use:", body)
            self.assertNotIn("PARTIAL", body)

    def test_handbook_has_clickable_all_pathway_index_and_explains_drawbacks(self):
        pages = general_pages()
        links = [(part["text"], int(part["clickEvent"]["value"]))
                 for page in pages for part in page.get("extra", [])
                 if part.get("clickEvent", {}).get("action") == "change_page"]
        for card in CARDS:
            self.assertTrue(any(card["name"] in name for name, _ in links),
                            card["name"])
        for page in pages:
            flattened = json.dumps(page)
            if "PERMANENT WEAKNESS" in flattened:
                self.assertIn("ACTING TASKS", flattened)
        self.assertGreaterEqual(sum("PERMANENT WEAKNESS" in json.dumps(p)
                                    for p in pages), 22)

    def test_book_nbt_does_not_use_modern_item_component_syntax(self):
        nbt = book_nbt("Test", [{"text": "Hello"}], marker="tarotArcaneGuide:1b")
        self.assertIn('pages:[', nbt)
        self.assertIn("author:", nbt)
        self.assertNotIn("[written_book_content=", nbt)
        self.assertNotIn("minecraft:written_book[", nbt)


if __name__ == "__main__":
    unittest.main()
