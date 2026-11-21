"""Wave 4 Resonance regression: meaningful effects but NO player activation."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.batches import resonance4
from arcane_rev3.full_build import build
from arcane_rev3.powers import compile_powers, norm

ROOT = Path(__file__).resolve().parents[1]
PAIRS = {
    "paper_martyr", "marked_verdict", "burning_archive", "crumbling_reaper",
    "impossible_fist", "benevolent_crown", "binding_contract",
    "starless_poison", "eclipse", "walking_sanctuary", "loaded_dice",
}
CAPSTONE_COOLDOWNS = {
    "paper_martyr": 18000, "marked_verdict": 24000,
    "burning_archive": 24000, "crumbling_reaper": 24000,
    "impossible_fist": 18000, "benevolent_crown": 18000,
    "binding_contract": 18000, "starless_poison": 24000,
    "eclipse": 24000, "walking_sanctuary": 24000,
    "loaded_dice": 24000,
}


def registered():
    found = []
    resonance4.register(lambda *args: found.append(args))
    return found


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


class ResonanceWaveFourTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers, cls.manifest, cls.kits = compile_powers(ROOT)
        cls.entries = registered()
        cls.lookup = {
            (m["family"], m["pathway"], m["sequence"], norm(m["name"])): m
            for m in cls.manifest
        }

    def test_source_exact_29_new_powers_and_11_capstones(self):
        self.assertEqual(len(self.entries), 29)
        seen = set()
        capstones = {}
        for slug, seq, name, definition, accuracy, missing in self.entries:
            with self.subTest(slug=slug, seq=seq, name=name):
                self.assertIn(slug, PAIRS)
                key = ("resonance", slug, seq, norm(name))
                self.assertNotIn(key, seen)
                seen.add(key)
                record = self.lookup[key]
                self.assertEqual(record["status"], "partial")
                self.assertEqual(accuracy, "partial")
                self.assertTrue(missing)
                self.assertEqual(record["missing"], missing)
                self.assertIn(record["power_id"], self.powers)
                self.assertIn(record["power_id"], self.kits[(slug, seq)])
                self.assertNotEqual(definition["type"], "origins:simple")
                if seq == 0:
                    capstones[slug] = definition
        self.assertEqual(set(capstones), PAIRS)
        for slug, definition in capstones.items():
            with self.subTest(capstone=slug):
                self.assertEqual(definition["type"], "origins:active_self")
                self.assertEqual(definition["cooldown"], CAPSTONE_COOLDOWNS[slug])
                self.assertEqual(definition["key"]["key"], "key.origins.primary_active")
                self.assertGreaterEqual(len(definition["entity_action"]["actions"]), 2)

    def test_counts_account_for_434_without_fake_full_status(self):
        self.assertEqual(len(self.powers), 337)
        self.assertEqual(len(self.manifest), 434)
        status = {kind: sum(m["status"] == kind for m in self.manifest)
                  for kind in ("full", "partial", "blocked")}
        self.assertEqual(status, {"full": 73, "partial": 264, "blocked": 97})
        self.assertEqual(sum(m["family"] == "resonance" and
                             m["status"] != "blocked" for m in self.manifest), 98)

    def test_no_unguarded_ally_effects_or_fake_op_commands(self):
        for slug, seq, name, definition, *_ in self.entries:
            with self.subTest(name=name):
                for obj in objects(definition):
                    if obj.get("type") == "origins:area_of_effect":
                        self.assertEqual(
                            obj["bientity_condition"]["condition"]["tag"],
                            "tarot:hostile")
                    if obj.get("type") == "origins:execute_command":
                        command = obj["command"]
                        self.assertEqual(obj["permission_level"], 2)
                        if "@a" in command:
                            # Generated cross-team effect is allowed only with
                            # an explicit caster team AND a known target team.
                            self.assertIn("execute if entity @s[team=", command)
                            self.assertIn("@a[team=", command)
                            self.assertNotIn("@a[distance=", command)
                        self.assertNotIn("op ", command)
                        self.assertNotIn("deop ", command)
                        self.assertNotIn(";", command)

    def test_two_pack_variants_do_not_unlock_resonance(self):
        with tempfile.TemporaryDirectory() as directory:
            artifacts = build(output=Path(directory))
            for variant in ("only", "addon"):
                with self.subTest(variant=variant), ZipFile(artifacts[variant]) as z:
                    self.assertIsNone(z.testzip())
                    for slug, seq, name, *_ in self.entries:
                        record = self.lookup[
                            ("resonance", slug, seq, norm(name))]
                        path = ("data/tarot/powers/" +
                                record["power_id"].split(":")[1] + ".json")
                        self.assertIn(path, z.namelist())
                        self.assertNotEqual(json.loads(z.read(path))["type"],
                                            "origins:simple")
                    for slug in PAIRS:
                        origin = json.loads(z.read(
                            f"data/tarot/origins/{slug}.json"))
                        self.assertTrue(origin["unchoosable"])
                        self.assertEqual(origin["powers"], [])
                    gate = z.read(
                        "data/tarot_arcane/functions/ascend/check_s2.mcfunction"
                    ).decode()
                    self.assertIn("Resonance is locked", gate)
                    self.assertNotIn("clear @s", gate)


if __name__ == "__main__":
    unittest.main()
