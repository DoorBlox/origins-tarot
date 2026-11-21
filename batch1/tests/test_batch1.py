"""Structural checks, NOT proof of loaded Fabric/Origins/KubeJS runtime."""
import json,re,unittest
from pathlib import Path
from zipfile import ZipFile
BASE=Path(__file__).resolve().parents[1]
PACK=BASE/'datapack'
JS=BASE/'kubejs/server_scripts/tarot'
POW=PACK/'data/tarot/powers/fool'
REQUIRED={
'9_spirit_vision','9_clowns_mischief','9_spiritual_overload','9_full_faceless_disguise',
'8_tricksters_favor','7_stage_magician','6_borrowed_face','5_puppet_string',
'4_tricksters_escape','3_fools_bounty','2_fools_gathering',
'1_history_substitution','1_paper_figurine_substitute','0_legend_of_the_fool'}
SCRIPTED={'spiritual_overload','full_faceless_disguise','tricksters_favor',
'stage_magician','borrowed_face','puppet_string','tricksters_escape',
'fools_bounty','fools_gathering','history_substitution',
'paper_figurine_substitute','legend_of_the_fool'}
class Batch1Files(unittest.TestCase):
 def test_pack_and_origin_identity(self):
  pack=json.loads((PACK/'pack.mcmeta').read_text())
  self.assertEqual(pack['pack']['pack_format'],9)
  origin=json.loads((PACK/'data/tarot/origins/fool.json').read_text())
  self.assertEqual(origin['powers'],['tarot:meta/origin_marker_fool','tarot:fool/identity_spiritual_expenditure','tarot:fool/wings'])
  self.assertFalse(any('/9_' in x for x in origin['powers']))
  self.assertEqual(len(json.loads((PACK/'data/origins/origin_layers/origin.json').read_text())['origins']),1)
 def test_14_complete_json_powers_not_placeholders(self):
  powers={p.stem for p in POW.glob('[0-9]*_*.json')}
  self.assertEqual(powers,REQUIRED)
  for p in POW.glob('*.json'):
   j=json.loads(p.read_text())
   self.assertTrue(j['type'].startswith('origins:'))
   self.assertNotEqual(j['type'],'origins:simple')
   self.assertTrue(j.get('description'))
 def test_25_percent_spiritual_expenditure(self):
  obj=json.loads((POW/'identity_spiritual_expenditure.json').read_text())
  self.assertEqual(obj['modifier']['value'],0.25)
  self.assertEqual(obj['condition']['type'],'origins:sprinting')
 def test_required_shared_tags(self):
  tags=list((PACK/'data/tarot/tags').rglob('*.json'))
  self.assertEqual(len(tags),11)
  for item in tags:
   j=json.loads(item.read_text())
   self.assertTrue(j['values'])
   self.assertTrue(all(x.startswith('minecraft:') for x in j['values']))
 def test_twelve_scripted_handlers_plus_shared(self):
  for name in SCRIPTED:
   f=JS/'fool'/(name+'.js')
   self.assertTrue(f.is_file(),name)
   content=f.read_text()
   self.assertTrue('global.TarotFool.register' in content)
   self.assertNotIn('TODO: implement',content)
  self.assertTrue((JS/'fool'/'00_shared.js').exists())
  self.assertTrue((JS/'fool'/'clowns_mischief.js').exists())
  self.assertTrue((JS/'fool'/'spirit_vision.js').exists())
 def test_sequence_registry_references_powers(self):
  text=(JS/'slot_system/registry.js').read_text()
  ids=set(re.findall(r"['\"]([0-9]_[a-z0-9_]+)['\"]",text))
  self.assertEqual(ids,REQUIRED)
 def test_datapack_function_references(self):
  for path in PACK.rglob('*.json'):
   obj=json.loads(path.read_text())
   if path.parts[-3:-1]==('powers','fool') or '/powers/fool/' in str(path):
    pass
  self.assertTrue((PACK/'data/tarot_batch1/functions/chosen/fool.mcfunction').exists())
  self.assertTrue((PACK/'data/tarot_batch1/functions/request/g.mcfunction').exists())
  self.assertTrue((PACK/'data/tarot_batch1/functions/request/v.mcfunction').exists())
 def test_no_wildcards_or_origin_swaps(self):
  for p in JS.rglob('*.js'):
   body=p.read_text()
   self.assertNotIn('origin set @s',body)
   self.assertNotIn('power revoke @s tarot:*',body)
 def test_readme_exists(self):
  self.assertTrue((BASE/'README_BATCH_1.md').exists())
if __name__=='__main__': unittest.main()
