"""Build an isolated *Fool Seq9 only* test pack; no V3 or KubeJS dependency.

This is not the 434-ability Arcane V2 release. Do NOT install on the live SMP.
"""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


PACK_NAME = 'Arcane_V2_Rev3_Fool_Seq9_ONLY_1.18.2.zip'


def _j(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + '\n'


def _func(*lines):
    return '\n'.join(lines) + '\n'


def _effect(name, ticks):
    return {'type': 'origins:apply_effect', 'effect': {'effect': 'minecraft:' + name,
                                                    'duration': ticks, 'amplifier': 0,
                                                    'show_particles': False}}


def _files():
    files = {}
    def j(path, value):
        files[path] = _j(value)
    def f(path, *lines):
        files['data/tarot_arcane/functions/' + path + '.mcfunction'] = _func(*lines)

    j('pack.mcmeta', {'pack': {'pack_format': 9,
                             'description': 'Arcane V2 Rev3 - Fool Seq9 test ONLY; not the SMP release'}})
    j('data/minecraft/tags/functions/load.json', {'values': ['tarot_arcane:load']})
    j('data/minecraft/tags/functions/tick.json', {'values': ['tarot_arcane:tick']})
    j('data/origins/origin_layers/origin.json', {'replace': True, 'origins': ['tarot:fool']})
    j('data/tarot/origins/fool.json', {
        'powers': ['tarot:fool/wings', 'tarot:fool/9_spiritual_expenditure'],
        'icon': 'minecraft:totem_of_undying', 'name': 'The Fool (Arcane Rev3 Seq9 alpha)',
        'description': 'Test origin. Spirit Vision is slotted dynamically; other abilities are not yet built.',
        'impact': 3, 'order': 0,
    })
    j('data/tarot/powers/fool/wings.json', {
        'type': 'origins:elytra_flight', 'render_elytra': True,
        'name': 'Astral Wings', 'description': 'Fool innately glides with Elytra-style wings.',
    })
    j('data/tarot/powers/fool/9_spiritual_expenditure.json', {
        'type': 'origins:modify_exhaustion', 'name': 'Spiritual Expenditure',
        'description': 'Sprinting and Elytra flight produce 25% more exhaustion.',
        'modifier': {'name': 'Tarot Spiritual Expenditure', 'value': 0.25,
                     'operation': 'multiply_total'},
        'condition': {'type': 'origins:or', 'conditions': [
            {'type': 'origins:sprinting'}, {'type': 'origins:fall_flying'},
        ]},
    })
    j('data/tarot/powers/fool/9_spirit_vision.json', {
        'type': 'origins:active_self', 'name': 'Spirit Vision',
        'description': 'Sneak + secondary key. Glow all entities within 10 blocks for 2s; 5s cooldown.',
        'cooldown': 100, 'hud_render': {'should_render': True},
        'key': {'key': 'key.origins.secondary_active'},
        'condition': {'type': 'origins:sneaking'},
        'entity_action': {'type': 'origins:area_of_effect', 'radius': 10,
                          'include_target': True,
                          'bientity_action': {'type': 'origins:target_action',
                                              'action': _effect('glowing', 40)}},
    })

    f('load', *[f'scoreboard objectives add {name} {kind}' for name, kind in [
        ('ta_init', 'dummy'), ('ta_seq', 'dummy'), ('ta_mode', 'dummy'),
        ('ta_max', 'dummy'), ('ta_probe', 'dummy'), ('ta_has', 'dummy'),
        ('ta_clock', 'dummy'), ('ta_help', 'trigger'), ('ta_status', 'trigger'),
        ('ta_slots', 'trigger'),
    ]])
    f('tick', 'execute as @a at @s run function tarot_arcane:player/tick')
    f('player/tick',
      'scoreboard players enable @s ta_help',
      'scoreboard players enable @s ta_status',
      'scoreboard players enable @s ta_slots',
      'execute store success score @s ta_probe run origin has origin @s origins:origin tarot:fool',
      'execute if score @s ta_probe matches 1 unless score @s ta_init matches 1 run function tarot_arcane:player/init_fool',
      'execute if score @s ta_probe matches 0 if score @s ta_init matches 1 run function tarot_arcane:player/cleanup',
      'execute if score @s ta_help matches 1.. run function tarot_arcane:ui/help',
      'execute if score @s ta_status matches 1.. run function tarot_arcane:ui/status',
      'execute if score @s ta_slots matches 1.. run function tarot_arcane:ui/slots',
      'scoreboard players set @s ta_help 0',
      'scoreboard players set @s ta_status 0',
      'scoreboard players set @s ta_slots 0',
      'scoreboard players add @s ta_clock 1',
      'execute if score @s ta_clock matches 60.. run function tarot_arcane:player/reconcile')
    f('player/init_fool',
      'scoreboard players set @s ta_init 1',
      'scoreboard players set @s ta_seq 9',
      'scoreboard players set @s ta_mode 0',
      'scoreboard players set @s ta_max 1',
      'scoreboard players set @s ta_clock 0',
      'power revokeall @s tarot_slot',
      'power grant @s tarot:fool/9_spirit_vision tarot_slot',
      'tellraw @s '+json.dumps({'text':'[Tarot] Fool Sequence 9 activated. Sneak + V for Spirit Vision. /tarot slots', 'color':'aqua'}))
    f('player/cleanup',
      'power revokeall @s tarot_slot',
      'scoreboard players set @s ta_init 0',
      'scoreboard players set @s ta_seq 0')
    f('player/reconcile',
      'scoreboard players set @s ta_clock 0',
      'execute if score @s ta_probe matches 1 if score @s ta_init matches 1 if score @s ta_seq matches 9 store success score @s ta_has run power has @s tarot:fool/9_spirit_vision',
      'execute if score @s ta_probe matches 1 if score @s ta_init matches 1 if score @s ta_seq matches 9 if score @s ta_has matches 0 run power grant @s tarot:fool/9_spirit_vision tarot_slot')
    f('ui/help', 'tellraw @s '+json.dumps({'text':'[Tarot] Rev3 TEST: /tarot status, /tarot slots. Fool Seq9 only; no slot editing yet.', 'color':'gold'}))
    f('ui/status',
      'execute unless score @s ta_init matches 1 run tellraw @s '+json.dumps({'text':'[Tarot] Select Fool to begin this alpha.', 'color':'yellow'}),
      'execute if score @s ta_init matches 1 run tellraw @s '+json.dumps([
          {'text':'[Tarot] Fool | Sequence ', 'color':'gold'},
          {'score':{'name':'*','objective':'ta_seq'}},
          {'text':' | Mode: SINGLE | Alpha only', 'color':'gray'}]))
    f('ui/slots',
      'execute unless score @s ta_init matches 1 run tellraw @s '+json.dumps({'text':'[Tarot] Select Fool to see slots.', 'color':'yellow'}),
      'execute if score @s ta_init matches 1 run tellraw @s '+json.dumps({'text':'[Tarot] SLOTS (1/1): [1] Fool 9. Slot editing unlocks at Seq4, not implemented in alpha.', 'color':'aqua'}))
    return files


def _alias():
    def action(objective):
        return {'command': 'trigger ' + objective, 'commandType': 'CLIENT'}
    return {
        'schemaVersion': 1, 'commandMode': 'COMMAND_CUSTOM', 'command': 'tarot',
        'permission': 0, 'actions': [action('ta_help')],
        'children': [
            {'child': name, 'type': 'literal', 'permission': 0,
             'actions': [action('ta_' + name)]}
            for name in ('help', 'status', 'slots')
        ],
    }


def build(output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / PACK_NAME
    alias_path = output_dir / 'tarot.json'
    with ZipFile(zip_path, 'w', compression=ZIP_DEFLATED) as archive:
        for name, content in sorted(_files().items()):
            archive.writestr(name, content.encode('utf-8'))
    alias_path.write_text(_j(_alias()), encoding='utf-8')
    return {'pack': zip_path, 'alias': alias_path}


if __name__ == '__main__':
    paths = build(Path('output'))
    for name, path in paths.items():
        print(name, path)
