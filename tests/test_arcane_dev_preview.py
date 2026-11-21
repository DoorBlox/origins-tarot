"""The separate operator-only Resonance preview must not bypass live Rev3."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.full_build import (
    DEV_PREVIEW_SOURCE, SOURCE, build,
)
from arcane_rev3.model import PAIRS
from arcane_rev3.powers import compile_powers

ROOT = Path(__file__).resolve().parents[1]


class ManualResonancePreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.artifacts = build(output=Path(cls.tmp.name))
        cls.powers, cls.manifest, cls.kits = compile_powers(ROOT)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_optional_preview_is_separate_and_has_no_autorun_hooks(self):
        self.assertIn("resonance_preview", self.artifacts)
        self.assertNotEqual(SOURCE, DEV_PREVIEW_SOURCE)
        with ZipFile(self.artifacts["resonance_preview"]) as z:
            names = set(z.namelist())
            self.assertIsNone(z.testzip())
            self.assertEqual(json.loads(z.read("pack.mcmeta"))["pack"]["pack_format"], 9)
            self.assertNotIn("data/minecraft/tags/functions/load.json", names)
            self.assertNotIn("data/minecraft/tags/functions/tick.json", names)
            self.assertFalse(any("/powers/" in p or "/origins/" in p for p in names))
            self.assertEqual(len(names), 1 + 1 + 1 + 11 + 11 + 110)

    def test_each_pair_grants_only_its_actual_compiled_powers(self):
        live = {m["power_id"] for m in self.manifest
                if m["family"] == "resonance" and m["status"] != "blocked"}
        self.assertEqual(len(live), 110)
        with ZipFile(self.artifacts["resonance_preview"]) as z:
            for _, _, slug in PAIRS:
                with self.subTest(pair=slug):
                    path = f"data/tarot_arcane/functions/dev/resonance/execute/{slug}.mcfunction"
                    text = z.read(path).decode()
                    expected = [ident for seq in range(9, -1, -1)
                                for ident in self.kits.get((slug, seq), [])]
                    self.assertTrue(expected)
                    self.assertEqual(
                        [line for line in text.splitlines()
                         if line.startswith("power grant @s ")],
                        [f"power grant @s {ident} {DEV_PREVIEW_SOURCE}"
                         for ident in expected])
                    self.assertTrue(set(expected).issubset(live))
                    self.assertIn(f"power revokeall @s {DEV_PREVIEW_SOURCE}", text)
                    self.assertNotIn(SOURCE, text)
                    entry = z.read(
                        f"data/tarot_arcane/functions/dev/resonance/{slug}.mcfunction"
                    ).decode()
                    self.assertIn("a_init matches 1", entry)
                    self.assertIn("a_paused matches 1", entry)

    def test_individual_power_preview_does_not_share_ordinary_slot_source(self):
        with ZipFile(self.artifacts["resonance_preview"]) as z:
            for _, _, slug in PAIRS:
                ids = [ident for seq in range(9, -1, -1)
                       for ident in self.kits.get((slug, seq), [])]
                for ident in ids:
                    with self.subTest(id=ident):
                        basename = ident.split("/")[-1]
                        path = (f"data/tarot_arcane/functions/dev/resonance/"
                                f"one/{slug}/{basename}.mcfunction")
                        lines = z.read(path).decode().splitlines()
                        self.assertEqual(
                            lines[0], f"power revokeall @s {DEV_PREVIEW_SOURCE}")
                        self.assertEqual(
                            lines[1], f"power grant @s {ident} {DEV_PREVIEW_SOURCE}")

    def test_preview_cleanup_only_removes_preview_source(self):
        with ZipFile(self.artifacts["resonance_preview"]) as z:
            clear = z.read(
                "data/tarot_arcane/functions/dev/resonance/clear.mcfunction"
            ).decode()
            self.assertIn("power revokeall @s " + DEV_PREVIEW_SOURCE, clear)
            self.assertNotIn("power revokeall @s " + SOURCE, clear)
            self.assertNotIn("scoreboard players set", clear)
        for name in ("only", "addon"):
            with self.subTest(variant=name), ZipFile(self.artifacts[name]) as z:
                self.assertFalse(any(
                    "/dev/resonance/" in path for path in z.namelist()))
                block = z.read(
                    "data/tarot_arcane/functions/ascend/check_s2.mcfunction"
                ).decode()
                self.assertIn("Resonance is locked", block)
                for path in z.namelist():
                    if not path.endswith(".mcfunction"):
                        continue
                    self.assertNotIn(DEV_PREVIEW_SOURCE, z.read(path).decode())
        alias = json.loads(Path(self.artifacts["alias"]).read_text())
        self.assertNotIn("dev/resonance", json.dumps(alias))


if __name__ == "__main__":
    unittest.main()
