"""Behavior contracts + generated 1.18.2 pack integration tests (TDD)."""
import io
import json
import re
import unittest
from pathlib import Path
from zipfile import ZipFile

from progression import model
from progression import build
from progression.catalog import CARDS, RITUALS, PAIRS


class AscensionModelTests(unittest.TestCase):
    def test_primary_starts_at_sequence_nine(self):
        p = model.State.new('fool')
        self.assertEqual((p.primary, p.primary_seq, p.active, p.secondary), ('fool', 9, 'fool', None))

    def test_can_only_ascend_after_acting_and_ritual(self):
        p = model.State.new('justice')
        with self.assertRaises(model.RuleError):
            p.ascend(has_altar=True, has_ingredients=True)
        p = p.add_acting(1)
        with self.assertRaises(model.RuleError):
            p.ascend(has_altar=False, has_ingredients=True)
        with self.assertRaises(model.RuleError):
            p.ascend(has_altar=True, has_ingredients=False)
        self.assertEqual(p.ascend(has_altar=True, has_ingredients=True).primary_seq, 8)

    def test_secondary_requires_seq4_dimensions_and_four_trial_acts(self):
        p = model.State.new('fool')
        for seq in (9, 8, 7, 6, 5):
            p = p.add_acting(model.ACT_MARKS[seq]).ascend(True, True)
        self.assertEqual(p.primary_seq, 4)
        with self.assertRaises(model.RuleError):
            p.begin_trial('magician')
        p = p.visit('nether').visit('end')
        with self.assertRaises(model.RuleError):
            p.begin_trial('fool')
        p = p.begin_trial('magician')
        with self.assertRaises(model.RuleError):
            p.unlock_second(True, True)
        p = p.add_trial_acting(4)
        p = p.unlock_second(True, True)
        self.assertEqual((p.secondary, p.secondary_seq, p.active), ('magician', 9, 'fool'))
        with self.assertRaises(model.RuleError):
            p.begin_trial('star')

    def test_switch_is_one_full_origin_and_keeps_each_sequence(self):
        p = model.State(primary='fool', secondary='magician', primary_seq=3, secondary_seq=8)
        switched = p.swap('magician', at_altar=False, combat=False, flying=False, grounded=True, cooldown=0)
        self.assertEqual(switched.active, 'magician')
        self.assertEqual(switched.active_seq, 8)
        self.assertEqual(switched.primary_seq, 3)
        self.assertEqual(switched.secondary_seq, 8)
        with self.assertRaises(model.RuleError):
            switched.swap('fool', at_altar=False, combat=False, flying=False, grounded=True, cooldown=1200)
        with self.assertRaises(model.RuleError):
            switched.swap('fool', at_altar=False, combat=True, flying=False, grounded=True, cooldown=0)
        with self.assertRaises(model.RuleError):
            switched.swap('fool', at_altar=False, combat=False, flying=True, grounded=False, cooldown=0)
        with self.assertRaises(model.RuleError):
            switched.swap('fool', at_altar=False, combat=False, flying=False, grounded=False, cooldown=0)

    def test_sequence_four_requires_altar_and_three_allows_portable(self):
        p = model.State(primary='justice', secondary='moon', primary_seq=4, secondary_seq=9)
        with self.assertRaises(model.RuleError):
            p.swap('moon', at_altar=False, combat=False, flying=False, grounded=True, cooldown=0)
        self.assertEqual(p.swap('moon', at_altar=True, combat=False, flying=False, grounded=True, cooldown=0).active, 'moon')

    def test_stability_penalties_and_meditation(self):
        p=model.State(primary='star',stability=15)
        p=p.add_acting(2)
        self.assertEqual(p.stability,23)
        with self.assertRaises(model.RuleError):p.ascend(True,True)
        with self.assertRaises(model.RuleError):p.meditate(False,True,0)
        with self.assertRaises(model.RuleError):p.meditate(True,False,0)
        p=p.meditate(True,True,0)
        self.assertEqual(p.stability,53)
        p=p.ascend(True,True)
        self.assertEqual(p.stability,41)

    def test_ascend_dispatch_freezes_original_sequence(self):
        z=ZipFile(build.build_all(Path(__file__).resolve().parent.parent)['only'])
        text=z.read('data/tarot_progress/functions/ascend/validate.mcfunction').decode()
        self.assertIn('scoreboard players operation @s tc_reqseq = @s tc_curseq',text)
        self.assertNotIn('if score @s tc_curseq matches 8 if score @s tc_marks',text)
        z.close()

    def test_echo_resonance_only_at_high_sequences(self):
        p = model.State(primary='fool', secondary='magician', primary_seq=2, secondary_seq=9)
        self.assertEqual(p.echo, 'magician')
        self.assertIsNone(p.resonance)
        p = model.State(primary='fool', secondary='magician', primary_seq=1, secondary_seq=9)
        self.assertEqual(p.resonance, 'hidden_door')
        self.assertEqual(p.swap('magician',True,False,False,True,0).echo, None)
        self.assertEqual(p.swap('magician',True,False,False,True,0).resonance, None)


class AscensionBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parent.parent
        cls.artifacts = build.build_all(root)
        cls.only = ZipFile(cls.artifacts['only'])
        cls.addon = ZipFile(cls.artifacts['addon'])

    @classmethod
    def tearDownClass(cls):
        cls.only.close(); cls.addon.close()

    def test_all_22_cards_and_eighteen_gliders_remain(self):
        self.assertEqual(len(CARDS), 22)
        for z in (self.only, self.addon):
            for card in CARDS:
                name = card['slug']
                origin = json.loads(z.read(f'data/tarot/origins/{name}.json'))
                self.assertEqual(len([i for i in origin['powers'] if i.endswith('/wings')]), 1 if card['glider'] else 0)
                self.assertTrue(any('primary' in p for p in origin['powers']))
                self.assertTrue(any('drawback' in p for p in origin['powers']))
            layer = json.loads(z.read('data/origins/origin_layers/origin.json'))
            self.assertEqual(len(layer['origins']),22)

    def test_zip_contains_load_tick_functions_and_all_referenced_functions(self):
        for z in (self.only, self.addon):
            names = set(z.namelist())
            self.assertIn('data/minecraft/tags/functions/load.json',names)
            self.assertIn('data/minecraft/tags/functions/tick.json',names)
            for path in names:
                if path.endswith('.mcfunction'):
                    content = z.read(path).decode()
                    for func in re.findall(r'\bfunction\s+(tarot_progress:[\w/]+)', content):
                        target = 'data/tarot_progress/functions/'+func.split(':')[1]+'.mcfunction'
                        self.assertIn(target, names, f'{path} -> {func}')

    def test_all_json_decodes_and_vanilla_format_9(self):
        for z in (self.only, self.addon):
            self.assertIsNone(z.testzip())
            self.assertEqual(json.loads(z.read('pack.mcmeta'))['pack']['pack_format'],9)
            for path in z.namelist():
                if path.endswith('.json'):
                    with self.subTest(path=path): json.loads(z.read(path))

    def test_22_distinct_quest_tracks_and_ritual_thresholds(self):
        self.assertEqual(len(RITUALS),9)
        self.assertEqual(len(set(c['slug'] for c in CARDS)),22)
        for card in CARDS:
            slug = card['slug']
            self.assertIn(f'data/tarot_progress/advancements/acting/{slug}_a.json', self.only.namelist())
            self.assertIn(f'data/tarot_progress/advancements/acting/{slug}_b.json', self.only.namelist())
            for name in ('a','b'):
                doc=json.loads(self.only.read(f'data/tarot_progress/advancements/acting/{slug}_{name}.json'))
                self.assertTrue(doc['criteria'])
                self.assertIn('rewards', doc)
                self.assertIn('function',doc['rewards'])

    def test_no_false_duplicate_full_origin_layer(self):
        data=self.only.read('data/tarot_progress/functions/swap/dispatch.mcfunction').decode()
        self.assertIn('tc_combat',data)
        self.assertIn('tc_swapcd',data)
        self.assertIn('FallFlying',data)
        self.assertNotIn('power clear @s',data)
        self.assertIn('function tarot_progress:powers/refresh', ''.join(self.only.read(n).decode() for n in self.only.namelist() if n.startswith('data/tarot_progress/functions/swap/') and n.endswith('.mcfunction')))
        self.assertIn('power revokeall @s tarot_progress:tier',self.only.read('data/tarot_progress/functions/powers/refresh.mcfunction').decode())

    def test_tier_echo_resonance_powers_are_actual_json_files(self):
        for card in CARDS:
            slug=card['slug']
            for seq in (8,7,6,5,0):
                path=f'data/tarot_progress/powers/tier/{slug}/s{seq}.json'
                self.assertIn(path,self.only.namelist())
            self.assertIn(f'data/tarot_progress/powers/echo/{slug}.json',self.only.namelist())
        for pair in PAIRS:
            self.assertIn(f'data/tarot_progress/powers/resonance/{pair[2]}.json',self.only.namelist())

    def test_1182_only_no_post_118_commands(self):
        for name in self.only.namelist():
            if name.endswith('.mcfunction'):
                text=self.only.read(name).decode()
                self.assertNotIn('if dimension ',text)
                self.assertNotIn('execute unless if ',text)
                self.assertNotIn('execute if items ',text)

    def test_no_admin_exec_or_destructive_block_actions(self):
        for p in self.only.namelist():
            if p.endswith('.mcfunction'):
                txt=self.only.read(p).decode()
                self.assertNotIn('op @',txt)
                self.assertNotIn('setblock ',txt)
                self.assertNotIn('fill ',txt)
                self.assertNotIn('kill @',txt)

if __name__=='__main__':unittest.main()
