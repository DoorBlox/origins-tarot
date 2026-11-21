"""In-game non-OP ability codex and real Rev3 ascension roadmap contracts.

Use real emitted ZIPs instead of comparing source code strings alone.
"""
import json
import re
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.full_build import build, NUM
from arcane_rev3.model import PATHWAYS
from arcane_rev3.powers import compile_powers
from progression.catalog import ACT_MARKS, CARDS, RITUALS


def read(z, function):
    return z.read("data/tarot_arcane/functions/" + function + ".mcfunction").decode()


class PlayerGuidePackContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.artifacts = build(output=Path(cls.tmp.name))
        cls.powers, cls.manifest, cls.kits = compile_powers(
            Path(__file__).resolve().parents[1])

    def test_both_variants_have_non_op_guide_and_codex_triggers(self):
        for variant in ("only", "addon"):
            with self.subTest(variant=variant), ZipFile(self.artifacts[variant]) as z:
                load = read(z, "load")
                tick = read(z, "player/tick")
                for trigger in ("a_guide", "a_abilities", "a_roadmap", "a_stages", "a_kit", "a_detail"):
                    self.assertIn("scoreboard objectives add " + trigger + " trigger", load)
                    self.assertIn("scoreboard players enable @s " + trigger, tick)
                    self.assertIn("scoreboard players set @s " + trigger + " 0", tick)
                    self.assertIn("if score @s " + trigger + " matches 1..", tick)
                help_menu = read(z, "ui/help")
                for label in ("a_guide", "a_abilities", "a_roadmap"):
                    self.assertIn(label, help_menu)

    def test_can_open_any_equipped_single_or_dual_pathway_kit(self):
        with ZipFile(self.artifacts["only"]) as z:
            opener = read(z, "ui/codex/open")
            self.assertIn("a_init matches 1", opener)
            self.assertIn("a_kit matches 1..8", opener)
            self.assertIn("a_kit <= @s a_max", opener)
            self.assertIn("ui/codex/show", opener)
            show = read(z, "ui/codex/show")
            self.assertIn("a_view_code", show)
            for slug in PATHWAYS:
                for seq in range(9, 1, -1):
                    with self.subTest(slug=slug, seq=seq):
                        code = NUM[slug] * 100 + seq
                        fn = "ui/codex/kit/" + slug + "_" + str(seq)
                        self.assertIn("data/tarot_arcane/functions/" + fn + ".mcfunction", z.namelist())
                        self.assertIn(
                            f"if score @s a_view_code matches {code} run function tarot_arcane:{fn}",
                            show)
                        slot = read(z, fn)
                        self.assertIn("Sequence " + str(seq), slot)
                        self.assertIn("a_detail set", slot)

    def test_detail_cannot_read_other_people_or_unassigned_abilities(self):
        with ZipFile(self.artifacts["only"]) as z:
            detail = read(z, "ui/codex/detail_open")
            self.assertIn("a_init matches 1", detail)
            self.assertIn("a_view_slot", detail)
            self.assertIn("a_view_code", detail)
            self.assertIn("a_s1", detail)
            self.assertIn("a_s8", detail)
            self.assertIn("a_ok matches 1", detail)
            self.assertIn("a_detail matches 1..", detail)
            self.assertNotIn("@p", detail)
            self.assertNotIn("power grant", detail)
            self.assertNotIn("scoreboard players set @a", detail)

    def test_every_equipped_ability_has_a_name_how_to_use_and_limitations(self):
        with ZipFile(self.artifacts["only"]) as z:
            all_function_names = set(z.namelist())
            for row in self.manifest:
                if row["family"] != "individual" or row["sequence"] < 2:
                    continue
                path = row["pathway"]
                sequence = row["sequence"]
                # Some innate drawbacks are permanently granted by the Origin,
                # rather than removable via the current slot's SOURCE.
                kit_fn = "ui/codex/kit/" + path + "_" + str(sequence)
                ui = read(z, kit_fn)
                if row["status"] != "blocked":
                    self.assertIn(row["name"], ui, (path, sequence, row["name"]))
                self.assertIn("DETAILS", ui)
            details = [n for n in all_function_names
                       if n.startswith("data/tarot_arcane/functions/ui/codex/detail/")
                       and n.endswith(".mcfunction")]
            self.assertGreaterEqual(len(details), 225)
            merged_text = "\n".join(read(z, name[
                len("data/tarot_arcane/functions/"):-len(".mcfunction")])
                for name in details)
            for fragment in ("What it does", "How to use"):
                self.assertIn(fragment, merged_text)
            for forbidden in ("Currently in game (compiled source)", "Limitations:",
                              "[PARTIAL]", "[FULL]", "Source-full"):
                self.assertNotIn(forbidden, merged_text)

    def test_roadmap_uses_actual_quest_ritual_and_blocks_seq1(self):
        with ZipFile(self.artifacts["addon"]) as z:
            roadmap = read(z, "ui/roadmap")
            self.assertIn("a_seq", roadmap)
            self.assertIn("a_marks", roadmap)
            self.assertIn("a_phase", roadmap)
            self.assertIn("a_actcd", roadmap)
            self.assertIn("a_combat", roadmap)
            self.assertIn("a_ascend", roadmap)
            self.assertIn("crying obsidian", roadmap)
            self.assertIn("a_stages", roadmap)
            stages = read(z, "ui/stages")
            for seq in range(9, 1, -1):
                self.assertIn("Sequence " + str(seq), stages)
                self.assertIn(str(ACT_MARKS[seq]) + " marks", stages)
            self.assertIn("LOCKED", stages)
            for seq in range(9, 1, -1):
                step = read(z, "ui/roadmap/seq_" + str(seq))
                self.assertIn("Sequence " + str(seq), step)
                self.assertIn(str(ACT_MARKS[seq]) + " acting marks", step)
                if seq > 2:
                    for item, count in RITUALS[seq].items():
                        self.assertIn(str(count), step)
                        self.assertIn(item.replace("_", " "), step)
                else:
                    self.assertIn("LOCKED", step)
                    self.assertNotIn("a_ascend", step)
            task = read(z, "ui/roadmap/tasks")
            for card in CARDS:
                self.assertIn(card["acting_item"].replace("_", " "), task)
            self.assertIn("a_phase matches 0", task)
            self.assertIn("a_phase matches 1", task)

    def test_join_and_ascension_show_next_step_navigation(self):
        with ZipFile(self.artifacts["only"]) as z:
            for card in CARDS:
                init = read(z, "player/init/" + card["slug"])
                self.assertIn("/trigger a_guide", init)
                self.assertIn("/trigger a_abilities", init)
            for seq in range(9, 2, -1):
                commit = read(z, "ascend/commit_s" + str(seq))
                self.assertIn("/trigger a_abilities", commit)
                self.assertIn("/trigger a_roadmap", commit)

    def test_all_chat_clicks_stay_player_scoped(self):
        with ZipFile(self.artifacts["only"]) as z:
            for name in z.namelist():
                if not name.endswith(".mcfunction"):
                    continue
                if "/ui/codex/" not in name and "/ui/roadmap" not in name:
                    continue
                text = z.read(name).decode()
                values = re.findall(r'"value":"([^"]+)"', text)
                for cmd in values:
                    self.assertTrue(cmd.startswith("/trigger a_"),
                                    (name, cmd))
                    self.assertNotIn("/function", cmd)
                    self.assertNotIn("/op ", cmd)

    def test_434_ability_manual_is_generated_with_truthful_source_gaps(self):
        path = self.artifacts["player_manual"]
        content = path.read_text(encoding="utf8")
        self.assertIn("Arcane Rev3 Player Ability Reference", content)
        self.assertIn("434", content)
        self.assertIn("Sequence 1", content)
        self.assertIn("Resonance", content)
        self.assertIn("What it does", content)
        self.assertIn("How to use", content)
        self.assertNotIn("Still missing", content)
        self.assertNotIn("PARTIAL", content)
        self.assertNotIn("source-full", content)
        for entry in self.manifest:
            self.assertIn(entry["name"], content)

    def test_alias_keeps_existing_commands_and_adds_guide(self):
        alias = json.loads(self.artifacts["alias"].read_text())
        labels = {p["child"] for p in alias["children"]}
        self.assertTrue({"help", "ascend", "status", "slots", "slot",
                         "guide", "abilities", "roadmap", "stages", "kit"}.issubset(labels))


if __name__ == "__main__":
    unittest.main()
