"""Compile all newly translated Resonance abilities without granting incomplete kits."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from arcane_rev3.batches import resonance
from arcane_rev3.model import PAIRS
from arcane_rev3.powers import compile_powers, norm
from arcane_rev3.full_build import build

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "paper_martyr": {9:"Burdened Beginning"},
    "marked_verdict": {9:"Cold Judgment"},
    "burning_archive": {9:"Scholar's Fire",8:"Combat Insight"},
    "crumbling_reaper": {9:"Grave Ruin"},
    "impossible_fist": {9:"Traveler's Might",8:"Sleight of Fist"},
    "benevolent_crown": {9:"Sovereign's Care",8:"Unbound Symbiosis"},
    "binding_contract": {9:"Hellborn Verdict",8:"Fallen Question",7:"Predator's Calm"},
    "starless_poison": {9:"Sleepless Grace",8:"Lullaby Whisper",7:"Nightmare Fire"},
    "eclipse": {9:"Unshadowed Sanguine",8:"Holy Tamer",7:"Solar Drain"},
    "walking_sanctuary": {9:"Wraith's Prayer",8:"Madness Consecrate"},
    "loaded_dice": {9:"Fated Reader",8:"Deduction Machine",7:"Index of Luck"},
}

class ResonanceSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.powers,cls.manifest,cls.kits = compile_powers(ROOT)
        cls.index = {(m["family"],m["pathway"],m["sequence"],norm(m["name"])):m
                     for m in cls.manifest}

    def test_23_source_traced_powers_across_11_pairs(self):
        self.assertEqual(len(EXPECTED),11)
        entries=[]
        resonance.register(lambda *args: entries.append(args))
        self.assertEqual(len(entries),23)
        self.assertEqual(len({(s,q,norm(n)) for s,q,n,*_ in entries}),23)
        self.assertEqual({p for _,_,p in PAIRS},set(EXPECTED))
        expected={(slug,seq,norm(name)) for slug,levels in EXPECTED.items()
                  for seq,name in levels.items()}
        self.assertEqual({(slug,seq,norm(name)) for slug,seq,name,*_ in entries},expected)
        for slug,seq,name,power,*rest in entries:
            key=self.index[("resonance",slug,seq,norm(name))]
            self.assertEqual(key["family"],"resonance")
            self.assertIn(key["power_id"],self.powers)
            self.assertIn(key["power_id"],self.kits[(slug,seq)])
            self.assertNotEqual(power["type"],"origins:simple")
            self.assertEqual(key["status"],rest[0] if rest else "full")
            if key["status"]=="partial":self.assertTrue(key["missing"])
        self.assertGreaterEqual(len(self.powers),204)
        self.assertGreaterEqual(sum(x["status"]=="full" for x in self.manifest),73)
        self.assertGreaterEqual(sum(x["status"]=="partial" for x in self.manifest),131)
        self.assertLessEqual(sum(x["status"]=="blocked" for x in self.manifest),230)

    def test_resonance_coverage_in_source_is_not_player_unlock(self):
        for slug,levels in EXPECTED.items():
            self.assertTrue(any((slug,seq) in self.kits for seq in levels))
            for seq in levels:
                self.assertGreater(len(self.kits[(slug,seq)]),0)


class ResonancePackReleaseGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.artifacts=build(output=Path(cls.tmp.name))
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_both_pack_variants_keep_partial_resonance_unselectable(self):
        manifest=json.loads(Path(self.artifacts["manifest"]).read_text())
        self.assertGreaterEqual(manifest["summary"]["compiled"],204)
        self.assertLessEqual(manifest["summary"]["blocked"],230)
        self.assertEqual(manifest["summary"]["resonance"],"FAIL-CLOSED until complete")
        for variant in ("only","addon"):
            with ZipFile(self.artifacts[variant]) as pack:
                names=set(pack.namelist())
                self.assertIsNone(pack.testzip())
                origin_layer=json.loads(pack.read("data/origins/origin_layers/origin.json"))
                self.assertEqual(len(origin_layer["origins"]),22)
                self.assertTrue(all(not name.endswith(("/"+slug)) for name in
                                    origin_layer["origins"] for slug in EXPECTED))
                for slug,seqs in EXPECTED.items():
                    origin=json.loads(pack.read(f"data/tarot/origins/{slug}.json"))
                    self.assertEqual(origin["powers"],[])
                    self.assertTrue(origin["unchoosable"])
                    for seq,name in seqs.items():
                        match=[m for m in manifest["abilities"]
                               if m["family"]=="resonance" and m["pathway"]==slug
                               and m["sequence"]==seq and norm(m["name"])==norm(name)]
                        self.assertEqual(len(match),1,(slug,seq,name))
                        p=match[0]
                        self.assertIsNotNone(p["power_id"])
                        path="data/tarot/powers/"+p["power_id"].split(":")[1]+".json"
                        self.assertIn(path,names)
                        self.assertTrue(json.loads(pack.read(path))["type"].startswith("origins:"))
                        self.assertNotIn(f"data/tarot_arcane/functions/kits/{slug}/s{seq}.mcfunction",names)
                asc=pack.read("data/tarot_arcane/functions/ascend/check_s2.mcfunction").decode()
                self.assertIn("Resonance is locked",asc)
                self.assertNotIn("clear @s",asc)
                self.assertNotIn("scoreboard players set @s a_mode 2",asc)

    def test_no_resonance_grants_in_any_function(self):
        for variant in ("only","addon"):
            with ZipFile(self.artifacts[variant]) as pack:
                for file in pack.namelist():
                    if not file.endswith(".mcfunction"):continue
                    content=pack.read(file).decode()
                    for slug in EXPECTED:
                        self.assertNotIn("power grant @s tarot:"+slug+"/",content,
                                         (variant,file,slug))
