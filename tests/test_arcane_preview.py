"""Structural and progression isolation checks for Arcane handbook test builds."""
import json,re,unittest
from pathlib import Path
from zipfile import ZipFile
from arcane import preview
from progression.catalog import CARDS

ROOT=Path(__file__).resolve().parent.parent

class ArcanePreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog,cls.templates=preview.validate(ROOT)
        cls.zips={variant:ZipFile(path) for variant,path in preview.build(ROOT).items()}
    @classmethod
    def tearDownClass(cls):
        for archive in cls.zips.values():archive.close()
    def test_source_complete_and_traceable(self):
        self.assertEqual(len(self.catalog["individual"]),22)
        self.assertEqual(len(self.catalog["resonance"]),11)
        powers=[a for card in self.catalog["individual"]+self.catalog["resonance"]
                for seq in card["sequences"] for a in seq["abilities"]]
        self.assertEqual(len(powers),434)
        self.assertEqual({a["flag"] for a in powers},{"D","D/S","S"})
        self.assertTrue(all({s["sequence"] for s in c["sequences"]}==set(range(10))
                            for c in self.catalog["individual"]+self.catalog["resonance"]))
    def test_22_nonplaceholder_native_powers_and_partial_disclosures(self):
        self.assertEqual(len(self.templates),22)
        self.assertEqual({x["slug"] for x in self.templates},{c["slug"] for c in CARDS})
        self.assertEqual(sum(x["accuracy"]=="partial" for x in self.templates),6)
        for t in self.templates:
            self.assertNotEqual(t["power"]["type"],"origins:simple")
            if t["accuracy"]=="partial":self.assertTrue(t["missing"])
    def test_both_variants_validate_and_keep_wings(self):
        for variant,z in self.zips.items():
            self.assertIsNone(z.testzip())
            self.assertEqual(json.loads(z.read("pack.mcmeta"))["pack"]["pack_format"],9)
            layer=json.loads(z.read("data/origins/origin_layers/origin.json"))
            self.assertIs(layer["replace"],variant=="only")
            self.assertEqual(len(layer["origins"]),22)
            self.assertEqual(sum(
                f"tarot:{c['slug']}/wings" in json.loads(
                    z.read(f"data/tarot/origins/{c['slug']}.json"))["powers"]
                for c in CARDS),18)
            for f in z.namelist():
                if f.endswith(".json"):json.loads(z.read(f))
    def test_ownership_and_sequence_locks(self):
        for z in self.zips.values():
            ref=z.read("data/tarot_progress/functions/powers/refresh.mcfunction").decode()
            self.assertIn("power revokeall @s tarot_arcane:sequence",ref)
            self.assertEqual(ref.count("run function tarot_arcane:grant/"),22)
            for c in CARDS:
                text=z.read(f"data/tarot_arcane/functions/grant/{c['slug']}.mcfunction").decode()
                self.assertIn("tc_curseq matches ..",text)
                for resource in re.findall(r"power grant @s (tarot:[a-z0-9_/]+) tarot_arcane:sequence",text):
                    self.assertIn("data/tarot/powers/"+resource.split(":",1)[1]+".json",z.namelist())
    def test_no_bypass_fusions_or_team_hazard(self):
        for z in self.zips.values():
            status=json.loads(z.read("ARCANE_PREVIEW_STATUS.json"))
            self.assertEqual(status["specified_entries"],434)
            self.assertEqual(len(status["compiled_entries"]),22)
            self.assertIs(status["resonance_forms_live"],False)
            self.assertEqual(status["second_arcana_unlock_sequence"],4)
            for key in status["compiled_entries"]:
                slug,seq,suffix=key.split(":")
                raw=z.read(f"data/tarot/powers/{slug}/{seq}_{suffix}.json").decode()
                for bad in ("minecraft:player","origins:execute_command","origins:area_of_effect","origins:creative_flight"):
                    self.assertNotIn(bad,raw)
    def test_required_tags(self):
        tags=preview.read_json(ROOT/"arcane/tags.json")
        self.assertEqual(len(tags),8)
        for z in self.zips.values():
            for name,values in tags.items():
                path=f"data/tarot/tags/{name}.json"
                self.assertEqual(json.loads(z.read(path))["values"],["minecraft:"+v for v in values])

if __name__=="__main__":unittest.main()
