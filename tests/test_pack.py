"""Reproducible tests for both 1.18.2 Origins datapack variants (not live game tests)."""
import json
import unittest
import zipfile
from pathlib import Path
import generate

class DatapackContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generate.make()
        cls.zips = {
            "addon": Path("output/The_Tarot_Club_22_Arcana_1.18.2.zip"),
            "only": Path("output/The_Tarot_Club_22_Arcana_Only_1.18.2.zip"),
        }
        cls.cards = [card[0] for card in generate.CARDS]

    def test_zip_integrity(self):
        for p in self.zips.values():
            self.assertTrue(p.is_file())
            with zipfile.ZipFile(p) as z:
                self.assertIsNone(z.testzip())

    def test_major_arcana_card_count(self):
        self.assertEqual(len(self.cards), 22)
        self.assertEqual(len(set(self.cards)), 22)

    def test_valid_json_and_pack_format(self):
        for p in self.zips.values():
            with zipfile.ZipFile(p) as z:
                self.assertEqual(json.loads(z.read("pack.mcmeta"))["pack"]["pack_format"], 9)
                for n in z.namelist():
                    if n.endswith(".json"):
                        with self.subTest(zip=p.name, file=n):
                            json.loads(z.read(n))

    def test_origin_selection_variant_semantics(self):
        for variant, p in self.zips.items():
            with zipfile.ZipFile(p) as z:
                layer = json.loads(z.read("data/origins/origin_layers/origin.json"))
                self.assertEqual(layer["origins"], [f"tarot:{s}" for s in self.cards])
                self.assertIs(layer["replace"], variant == "only")

    def test_all_origin_powers_resolve_and_are_described(self):
        for p in self.zips.values():
            with zipfile.ZipFile(p) as z:
                names = set(z.namelist())
                for slug in self.cards:
                    origin = json.loads(z.read(f"data/tarot/origins/{slug}.json"))
                    self.assertGreaterEqual(len(origin["powers"]), 4)
                    self.assertEqual(len(origin["powers"]), len(set(origin["powers"])))
                    for power in origin["powers"]:
                        namespace, name = power.split(":", 1)
                        self.assertEqual(namespace, "tarot")
                        path = f"data/{namespace}/powers/{name}.json"
                        self.assertIn(path, names)
                        content = json.loads(z.read(path))
                        self.assertTrue(content.get("name"))
                        self.assertTrue(content.get("description"))

    def test_both_abilities_have_the_right_keys_and_cooldowns(self):
        with zipfile.ZipFile(self.zips["only"]) as z:
            for slug in self.cards:
                p = json.loads(z.read(f"data/tarot/powers/{slug}/primary.json"))
                s = json.loads(z.read(f"data/tarot/powers/{slug}/secondary.json"))
                self.assertEqual(p["key"]["key"], "key.origins.primary_active")
                self.assertEqual(s["key"]["key"], "key.origins.secondary_active")
                self.assertGreater(p["cooldown"], 0)
                self.assertGreater(s["cooldown"], 0)
                self.assertNotEqual(p["name"], s["name"])

    def test_exactly_eighteen_native_gliders(self):
        with zipfile.ZipFile(self.zips["only"]) as z:
            gliders = []
            for slug in self.cards:
                origin = json.loads(z.read(f"data/tarot/origins/{slug}.json"))
                if f"tarot:{slug}/wings" in origin["powers"]:
                    power = json.loads(z.read(f"data/tarot/powers/{slug}/wings.json"))
                    self.assertEqual(power["type"], "origins:elytra_flight")
                    self.assertIs(power["render_elytra"], True)
                    gliders.append(slug)
            self.assertEqual(set(gliders), generate.GLIDERS)
            self.assertEqual(len(gliders), 18)

    def test_all_origins_have_drawbacks(self):
        with zipfile.ZipFile(self.zips["only"]) as z:
            for slug in self.cards:
                self.assertIn(f"data/tarot/powers/{slug}/drawback.json", z.namelist())

    def test_six_equiprobable_fate_outcomes(self):
        with zipfile.ZipFile(self.zips["only"]) as z:
            power = json.loads(z.read("data/tarot/powers/wheel_of_fortune/primary.json"))
            choice = power["entity_action"]["actions"][0]
            self.assertEqual(choice["type"], "origins:choice")
            self.assertEqual(len(choice["actions"]), 6)
            self.assertEqual({i["weight"] for i in choice["actions"]}, {1})
            effects = [i["element"]["effect"]["effect"] for i in choice["actions"]]
            self.assertEqual(len(effects), len(set(effects)))

    def test_documentation_covers_all_cards(self):
        with zipfile.ZipFile(self.zips["only"]) as z:
            guide = z.read("ARCANA_GUIDE.md").decode("utf-8")
            for slug in self.cards:
                self.assertIn(f"`tarot:{slug}`", guide)
            self.assertIn("18 / 22", guide)

    def test_no_admin_commands_or_block_mutations(self):
        disallowed = ['"origins:execute_command"', '"origins:change_block"', '"origins:modify_block"']
        with zipfile.ZipFile(self.zips["only"]) as z:
            for name in z.namelist():
                if "/powers/" in name and name.endswith(".json"):
                    payload = z.read(name).decode("utf-8")
                    for forbidden in disallowed:
                        self.assertNotIn(forbidden, payload)

if __name__ == "__main__":
    unittest.main()
