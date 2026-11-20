"""Build two self-contained V3 packs from the latest generated V2 source trees.

Minecraft Java 1.18.2 (pack_format 9), Origins 1.4.1. Python stdlib only.
V3 deliberately uses ONE full Origins layer and command-granted tier/echo powers.
"""
from __future__ import annotations
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from .catalog import CARDS, ACT_MARKS, RITUALS, SECOND_OFFERING, PAIRS

NAMESPACE='tarot_progress'
CMD='tarot_progress:'
TIER_SOURCE='tarot_progress:tier'
ECHO_SOURCE='tarot_progress:echo'
RESONANCE_SOURCE='tarot_progress:resonance'
OBJECTIVES=['tc_clock','tc_init','tc_primary','tc_secondary','tc_slot','tc_current',
 'tc_pseq','tc_sseq','tc_curseq','tc_pm','tc_sm','tc_marks','tc_phase','tc_tphase',
 'tc_trial','tc_tm','tc_actcd','tc_swapcd','tc_combat','tc_visit_n','tc_visit_e',
 'tc_ra','tc_rb','tc_ok','tc_probe','tc_hasres','tc_reqseq','tc_stab','tc_medcd',
 'tc_ascend','tc_unlock','tc_meditate',
 'tc_trialcmd','tc_swap','tc_status','tc_help','tc_cards']
TRIGGERS={'tc_ascend','tc_unlock','tc_trialcmd','tc_swap','tc_status','tc_help','tc_cards','tc_meditate'}


def j(obj):return (json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def js(obj):return json.dumps(obj,ensure_ascii=False,separators=(',',':'))
def tell(message,color='gold'):
    return 'tellraw @s '+js({'text':'[Tarot] '+message,'color':color})
def name_score(objective):return {'score':{'name':'*','objective':objective}}
def function(name):return f'function {CMD}{name}'
def selector_range(obj,n):return f'if score @s {obj} matches {n}'
def score_matches(obj,lo,hi=None):
    if hi is None:return f'if score @s {obj} matches {lo}'
    return f'if score @s {obj} matches {lo}..{hi}'
def altar():return 'if block ~ ~-1 ~ minecraft:lodestone if block ~ ~-2 ~ minecraft:crying_obsidian'
def secure():return 'if score @s tc_combat matches 0 if entity @s[nbt={OnGround:1b}] unless entity @s[nbt={FallFlying:1b}]'

class Writer:
    def __init__(self,contents):self.data=contents
    def func(self,name,*lines):
        ls=[]
        for line in lines:
            if isinstance(line,(tuple,list)):ls.extend(line)
            elif line is not None:ls.append(line)
        self.data[f'data/{NAMESPACE}/functions/{name}.mcfunction']=('\n'.join(ls)+'\n').encode('utf-8')
    def json(self,sub,obj):self.data[f'data/{NAMESPACE}/{sub}.json']=j(obj)


def quest(event):
    if event.startswith('kill:'):
        return {'trigger':'minecraft:player_killed_entity','conditions':{'entity':{'type':'minecraft:'+event.split(':')[1]}}}
    if event=='trade':return {'trigger':'minecraft:villager_trade'}
    if event=='breed':return {'trigger':'minecraft:bred_animals'}
    if event.startswith('dimension:'):
        return {'trigger':'minecraft:changed_dimension','conditions':{'to':'minecraft:'+event.split(':')[1]}}
    if event.startswith('consume:'):
        return {'trigger':'minecraft:consume_item','conditions':{'item':{'items':['minecraft:'+event.split(':')[1]]}}}
    raise ValueError('Unknown quest '+event)


def acting(w):
    # Players receive marks from two card-specific event triggers, alternating A and B.
    # Revocation enables future completion; 2-minute shared cooldown and stage gates
    # prevent spam and power-leveling while AFK.
    for card in CARDS:
        slug,num=card['slug'],card['id']
        event_a={'trigger':'minecraft:inventory_changed','conditions':{'items':[{'items':['minecraft:'+card['acting_item']]}]}}
        event_b=quest(card['acting_event'])
        for phase,criterion in (('a',event_a),('b',event_b)):
            w.json(f'advancements/acting/{slug}_{phase}',{
                'criteria':{'act':criterion},'rewards':{'function':f'{CMD}acting/event/{slug}_{phase}'}})
            pp=0 if phase=='a' else 1
            w.func(f'acting/event/{slug}_{phase}',
                   f'execute if score @s tc_init matches 1 if score @s tc_actcd matches 0 if score @s tc_current matches {num} if score @s tc_phase matches {pp} if score @s tc_curseq matches 1..9 run {function("acting/award_active_"+phase)}',
                   f'execute if score @s tc_init matches 1 if score @s tc_actcd matches 0 if score @s tc_trial matches {num} if score @s tc_tphase matches {pp} if score @s tc_tm matches ..3 run {function("acting/award_trial_"+phase)}',
                   f'advancement revoke @s only {CMD}acting/{slug}_{phase}')

    for phase in 'ab':
        pp=1 if phase=='a' else 0
        w.func('acting/award_active_'+phase,
               'execute if score @s tc_slot matches 1 run scoreboard players add @s tc_pm 1',
               'execute if score @s tc_slot matches 2 run scoreboard players add @s tc_sm 1',
               'execute if score @s tc_pm matches 21.. run scoreboard players set @s tc_pm 20',
               'execute if score @s tc_sm matches 21.. run scoreboard players set @s tc_sm 20',
               f'scoreboard players set @s tc_phase {pp}',
               'scoreboard players set @s tc_actcd 2400',
               'scoreboard players add @s tc_stab 4',
               'execute if score @s tc_stab matches 101.. run scoreboard players set @s tc_stab 100',
               tell('Acting accepted! One digestion mark earned. Return to the altar to advance.','green'))
        w.func('acting/award_trial_'+phase,
               'scoreboard players add @s tc_tm 1',
               f'scoreboard players set @s tc_tphase {pp}',
               'scoreboard players set @s tc_actcd 2400',
               'scoreboard players add @s tc_stab 2',
               'execute if score @s tc_stab matches 101.. run scoreboard players set @s tc_stab 100',
               tell('Second Awakening trial: acting proof accepted (+1 of 4).','aqua'))
    # Combat flags are an independent set of advancements. A reliable client-server
    # damage event prevents switching and rituals for 10 seconds (not skill cooldowns).
    for kind,criterion in [('take',{'trigger':'minecraft:entity_hurt_player'}),
                           ('deal',{'trigger':'minecraft:player_hurt_entity'})]:
        w.json(f'advancements/events/combat_{kind}',{
            'criteria':{'hurt':criterion},'rewards':{'function':f'{CMD}events/combat_{kind}'}})
        w.func(f'events/combat_{kind}',
               'scoreboard players set @s tc_combat 200',
               f'advancement revoke @s only {CMD}events/combat_{kind}')
    for dim,name in [('the_nether','n'),('the_end','e')]:
        w.json(f'advancements/events/visit_{name}',{'criteria':{'travel':{
            'trigger':'minecraft:changed_dimension','conditions':{'to':'minecraft:'+dim}}},
            'rewards':{'function':f'{CMD}events/visit_{name}'}})
        w.func(f'events/visit_{name}',f'scoreboard players set @s tc_visit_{name} 1',
               tell(f'{dim.replace("the_", "").title()} fragment witnessed.','aqua'))


def p(name,desc,kind,**kw):return {'type':kind,'name':name,'description':desc,**kw}
def mod(value,op='multiply_total'):return {'name':'Tarot Ascension','value':value,'operation':op}
def move(name,desc,val):return p(name,desc,'origins:attribute',modifier=dict(mod(val),attribute='minecraft:generic.movement_speed'))
def armour(name,desc,val):return p(name,desc,'origins:attribute',modifier=dict(mod(val,'addition'),attribute='minecraft:generic.armor'))
def attack(name,desc,val):return p(name,desc,'origins:attribute',modifier=dict(mod(val),attribute='minecraft:generic.attack_damage'))
def xp(name,desc,val):return p(name,desc,'origins:modify_xp_gain',modifier=mod(val))
def mining(name,desc,val):return p(name,desc,'origins:modify_break_speed',modifier=mod(val))
def projectile(name,desc,val):return p(name,desc,'origins:modify_projectile_damage',modifier=mod(val))
def exhaust(name,desc,val):return p(name,desc,'origins:modify_exhaustion',modifier=mod(val))
def speed_swim(name,desc,val):return p(name,desc,'origins:modify_swim_speed',modifier=mod(val))
def luck(name,desc,val):return p(name,desc,'origins:attribute',modifier=dict(mod(val,'addition'),attribute='minecraft:generic.luck'))
def knock(name,desc,val):return p(name,desc,'origins:attribute',modifier=dict(mod(val,'addition'),attribute='minecraft:generic.knockback_resistance'))
def apply(name,seconds,ampl=0):return {'type':'origins:apply_effect','effect':{'effect':'minecraft:'+name,'duration':seconds*20,'amplifier':ampl,'show_particles':False}}
def on_hit_self(name,desc,effect,duration,cooldown):
    return p(name,desc,'origins:self_action_when_hit',entity_action=apply(effect,duration),cooldown=cooldown*20,hud_render={'should_render':False})
def on_hit_target(name,desc,effect,duration,cooldown):
    return p(name,desc,'origins:target_action_on_hit',entity_action=apply(effect,duration),cooldown=cooldown*20,hud_render={'should_render':False})
def attacker(name,desc,effect,duration,cooldown):
    return p(name,desc,'origins:attacker_action_when_hit',entity_action=apply(effect,duration),cooldown=cooldown*20,hud_render={'should_render':False})
def death_heal(name,desc,amount,cooldown):
    return p(name,desc,'origins:self_action_on_kill',entity_action={'type':'origins:heal','amount':amount},cooldown=cooldown*20,hud_render={'should_render':False})
def reduce_damage(name,desc,value):return p(name,desc,'origins:modify_damage_taken',modifier=mod(value))


def tier_power(card,sequence):
    name,focus=card['name'],card['focus']
    if sequence==8:
        title=f'{name}: First Digestion'
        return {'scout':move,'travel':move,'scholar':xp,'stealth':move,'tank':armour,'support':xp,
                'combat':attack,'sea':speed_swim,'night':move,'miner':mining,'luck':luck}[focus](
                    title,'Your first Ascension yields a modest permanent specialization.',
                    1 if focus in ('tank','luck') else (0.07 if focus in ('scholar','miner') else 0.055))
    if sequence==7:
        title=f'{name}: Practiced Instinct'
        return {'scout':on_hit_self(title,'A danger reflex grants Speed I for 3s every 90s.','speed',3,90),
                'travel':exhaust(title,'Long journeys use 12% less exhaustion.',-0.12),
                'scholar':mining(title,'Ritual craft makes mining 12% faster.',0.12),
                'stealth':on_hit_self(title,'A hit triggers short Speed I every 85s.','speed',3,85),
                'tank':knock(title,'Resist another 10% knockback.',0.10),
                'support':exhaust(title,'Work efficiently with 12% less exhaustion.',-0.12),
                'combat':on_hit_target(title,'Attacks briefly slow enemies every 70s.','slowness',2,70),
                'sea':speed_swim(title,'Swim 12% faster.',0.12),
                'night':on_hit_self(title,'Danger triggers Resistance I for 3s every 90s.','resistance',3,90),
                'miner':mining(title,'Dig 12% faster.',0.12),
                'luck':xp(title,'Gain 8% more experience.',0.08)}[focus]
    if sequence==6:
        title=f'{name}: Mid-Sequence Mastery'
        return {'scout':projectile,'travel':move,'scholar':xp,'stealth':projectile,
                'tank':armour,'support':exhaust,'combat':attack,'sea':speed_swim,
                'night':xp,'miner':mining,'luck':luck}[focus](
                    title,'Your pathway grows noticeably more reliable in everyday play.',
                    1 if focus in ('tank','luck') else (-0.08 if focus=='support' else 0.09))
    if sequence==5:
        title=f'{name}: Ritual Tempering'
        return {'scout':exhaust,'travel':exhaust,'scholar':xp,'stealth':exhaust,
                'tank':knock,'support':exhaust,'combat':attack,'sea':exhaust,
                'night':exhaust,'miner':mining,'luck':xp}[focus](
                    title,'Your mastered acting method improves a second dimension of survival.',
                    0.1 if focus in ('tank','miner','combat') else (-0.12 if focus in ('scout','travel','stealth','support','sea','night') else 0.12))
    if sequence==0:
        return luck('Apotheosis: '+name,'A rare prestige milestone: +1 Luck (no creative flight, immunity, or admin powers).',1)
    raise ValueError('Only passive milestone tiers 8,7,6,5 and 0 have power files')


def echo_power(card):
    name,focus=card['name'],card['echo']
    title=f'Echo of {name}'
    return {'scout':projectile,'travel':move,'scholar':xp,'stealth':move,'tank':armour,
            'support':exhaust,'combat':attack,'sea':speed_swim,'night':move,
            'miner':mining,'luck':luck}[focus](
            title,'A deliberately reduced passive borrowed from the INACTIVE Arcana; the other Origin is not fully equipped.',
            1 if focus in ('tank','luck') else (-0.05 if focus=='support' else 0.06))


def resonance_power(name):
    title='Resonance: '+name.replace('_',' ').title()
    desc='A limited high-sequence hybrid echo. Does not combine full Origin loadouts.'
    known={
      'hidden_door':on_hit_self(title,desc+' Ambushes grant brief Resistance I every 90s.','resistance',3,90),
      'calamity':on_hit_target(title,desc+' Hits apply Poison I for 3s every 22s.','poison',3,22),
      'midnight_requiem':death_heal(title,desc+' Kills restore one heart every 30s.',2,30),
      'absolute_decree':attacker(title,desc+' Attackers receive Slowness I for 4s every 24s.','slowness',4,24),
      'eclipse':reduce_damage(title,desc+' Incoming damage is reduced by 8%.',-0.08),
      'forbidden_library':xp(title,desc+' Earn 15% extra XP.',0.15),
      'gentle_heart':exhaust(title,desc+' Spend 12% less exhaustion.',-0.12),
      'storm_gate':speed_swim(title,desc+' Swim 15% faster.',0.15),
      'one_soul':projectile(title,desc+' Deal 12% more projectile damage.',0.12),
      'ruinborn':reduce_damage(title,desc+' Take 8% less generic damage.',-0.08),
      'shadow_pact':attack(title,desc+' Deal 10% more melee damage.',0.10),
      'fated_vision':luck(title,desc+' Gain +1 Luck.',1),
      'unbound_resonance':move(title,desc+' Other combinations get a modest 3% speed bonus.',0.03),
    }
    return known[name]


def write_powers(w):
    for c in CARDS:
        for seq in (8,7,6,5,0):
            w.json(f'powers/tier/{c["slug"]}/s{seq}',tier_power(c,seq))
        w.json(f'powers/echo/{c["slug"]}',echo_power(c))
    for *_,name in PAIRS:w.json('powers/resonance/'+name,resonance_power(name))
    w.json('powers/resonance/unbound_resonance',resonance_power('unbound_resonance'))


def core(w):
    load=[]
    for name in OBJECTIVES:
        kind='trigger' if name in TRIGGERS else 'dummy'
        load.append(f'scoreboard objectives add {name} {kind}')
    load += ['scoreboard players set #clock tc_clock 0',
             'tellraw @a '+js({'text':'[Tarot] Ascension V3 datapack loaded. Run /trigger tc_help.','color':'dark_aqua'})]
    w.func('load',load)
    w.json('tags/functions/_unused',{'values':[]}) if False else None
    w.data['data/minecraft/tags/functions/load.json']=j({'replace':False,'values':[CMD+'load']})
    w.data['data/minecraft/tags/functions/tick.json']=j({'replace':False,'values':[CMD+'tick']})
    w.func('tick',
           'scoreboard players add #clock tc_clock 1',
           'scoreboard players remove @a[scores={tc_actcd=1..}] tc_actcd 1',
           'scoreboard players remove @a[scores={tc_swapcd=1..}] tc_swapcd 1',
           'scoreboard players remove @a[scores={tc_combat=1..}] tc_combat 1',
           'scoreboard players remove @a[scores={tc_medcd=1..}] tc_medcd 1',
           'execute if score #clock tc_clock matches 20.. run '+function('tick/slow'))
    slow=['scoreboard players set #clock tc_clock 0',
          'scoreboard players add @a tc_init 0',
          f'execute as @a[scores={{tc_init=0}}] at @s run {function("register/scan")}',
          'scoreboard players enable @a tc_ascend',
          'scoreboard players enable @a tc_trialcmd',
          'scoreboard players enable @a tc_unlock',
          'scoreboard players enable @a tc_swap',
          'scoreboard players enable @a tc_status',
          'scoreboard players enable @a tc_help',
          'scoreboard players enable @a tc_cards',
          'scoreboard players enable @a tc_meditate',
          'execute as @a[scores={tc_init=1,tc_stab=..20}] run effect give @s minecraft:weakness 3 0 true']
    endpoints={'tc_ascend':'ascend/dispatch','tc_trialcmd':'trial/start_dispatch',
               'tc_unlock':'trial/unlock_dispatch','tc_swap':'swap/dispatch',
               'tc_status':'info/status','tc_help':'info/help','tc_cards':'info/cards',
               'tc_meditate':'meditate/dispatch'}
    for obj,fun in endpoints.items():
        slow.append(f'execute as @a[scores={{{obj}=1..}}] at @s run {function(fun)}')
        slow.append(f'scoreboard players set @a[scores={{{obj}=1..}}] {obj} 0')
    w.func('tick/slow',slow)
    scan=[]
    for card in CARDS:
        slug,num=card['slug'],card['id']
        scan += [f'execute if score @s tc_init matches 0 store result score @s tc_probe run origin has origin @s origins:origin tarot:{slug}',
                 f'execute if score @s tc_init matches 0 if score @s tc_probe matches 1 run {function("register/"+slug)}']
        register=[
            'scoreboard players set @s tc_init 1',
            f'scoreboard players set @s tc_primary {num}',
            f'scoreboard players set @s tc_current {num}',
            'scoreboard players set @s tc_secondary 0',
            'scoreboard players set @s tc_slot 1',
            'scoreboard players set @s tc_pseq 9',
            'scoreboard players set @s tc_sseq 9',
            'scoreboard players set @s tc_curseq 9',
            'scoreboard players set @s tc_pm 0',
            'scoreboard players set @s tc_sm 0',
            'scoreboard players set @s tc_phase 0',
            'scoreboard players set @s tc_tphase 0',
            'scoreboard players set @s tc_trial 0',
            'scoreboard players set @s tc_tm 0',
            'scoreboard players set @s tc_actcd 0',
            'scoreboard players set @s tc_swapcd 0',
            'scoreboard players set @s tc_combat 0',
            'scoreboard players set @s tc_stab 100',
            'scoreboard players set @s tc_medcd 0',
            'scoreboard players set @s tc_visit_n 0',
            'scoreboard players set @s tc_visit_e 0',
            function('powers/refresh'),
            tell(f'{card["name"]} chosen. Sequence 9. Your two acting tasks: carry {card["acting_item"].replace("_"," ")} and {card["acting_event"].replace(":"," ").replace("_"," ")}.','aqua'),
            tell('Alternate tasks every 2 minutes; then /trigger tc_ascend at a ritual altar. See /trigger tc_help.','green')]
        w.func('register/'+slug,register)
    w.func('register/scan',scan)

    w.func('info/help',
       tell('PATH OF ASCENSION | Levels 9 down to 0. One full Arcana equipped at a time.','light_purple'),
       tell('/trigger tc_status  - see levels, marks, secondary and cooldown.','aqua'),
       tell('/trigger tc_cards   - list the numbered Arcana for your secondary trial.','aqua'),
       tell('/trigger tc_ascend  - spend acting marks + ritual items, at the altar.','aqua'),
       tell('/trigger tc_trialcmd set N  - begin Second Awakening after primary S4, Nether+End visits.','aqua'),
       tell('/trigger tc_unlock  - after four alternating trial acts, pay at altar.','aqua'),
       tell('/trigger tc_swap set 1  OR  /trigger tc_swap set 2  - swap when permitted.','aqua'),
       tell('/trigger tc_meditate  - spend 4 amethyst at the altar to restore stability.','aqua'),
       tell('ALTAR: stand on a LODESTONE directly above CRYING OBSIDIAN. No flight or combat.','yellow'),
       tell('S3 enables portable swaps, S2 a minor Echo, S1 a Resonance, S0 prestige.','yellow'))
    w.func('info/status',
       'tellraw @s '+js([{'text':'[Tarot] Primary card ID: ','color':'gold'},name_score('tc_primary'),
                          {'text':' | Sequence '},name_score('tc_pseq'),{'text':' | Acting '},name_score('tc_pm')]),
       'tellraw @s '+js([{'text':'[Tarot] Secondary card ID: ','color':'aqua'},name_score('tc_secondary'),
                          {'text':' | Sequence '},name_score('tc_sseq'),{'text':' | Acting '},name_score('tc_sm')]),
       'tellraw @s '+js([{'text':'[Tarot] Active slot: ','color':'light_purple'},name_score('tc_slot'),
                          {'text':' | Active Sequence '},name_score('tc_curseq'),
                          {'text':' | Acting cooldown (ticks) '},name_score('tc_actcd')]),
       'tellraw @s '+js([{'text':'[Tarot] Second Awakening trial ID: ','color':'green'},name_score('tc_trial'),
                          {'text':' | Proofs '},name_score('tc_tm'),{'text':'/4 | Nether '},name_score('tc_visit_n'),
                          {'text':' | End '},name_score('tc_visit_e')]),
       'tellraw @s '+js([{'text':'[Tarot] Stability: ','color':'yellow'},name_score('tc_stab'),{'text':' / 100 | Meditation cooldown: '},name_score('tc_medcd')]),
       'tellraw @s '+js([{'text':'[Tarot] Switch cooldown (ticks): ','color':'gray'},name_score('tc_swapcd'),
                          {'text':' | Combat lock (ticks): '},name_score('tc_combat')]))
    for i in range(0,22,6):
        group=CARDS[i:i+6]
        w.func(f'info/cards_{i//6}',tell(' | '.join(f'{c["id"]}: {c["name"]}' for c in group),'aqua'))
    w.func('info/cards',[function(f'info/cards_{i}') for i in range(4)])
    w.func('admin/rollback_player',
            f'power revokeall @s {TIER_SOURCE}',
            f'power revokeall @s {ECHO_SOURCE}',
            f'power revokeall @s {RESONANCE_SOURCE}',
            tell('V3 bonus powers revoked. V2 base Arcana stays selected; progression scores are preserved.','yellow'))
    w.func('admin/rollback_all','execute as @a run '+function('admin/rollback_player'))


    w.func('meditate/dispatch',
       'scoreboard players set @s tc_ok 0',
       f'execute if score @s tc_init matches 1 if score @s tc_medcd matches 0 if score @s tc_stab matches ..99 {secure()} {altar()} run scoreboard players set @s tc_ok 1',
       'execute if score @s tc_ok matches 1 run '+function('meditate/check'),
       'execute if score @s tc_ok matches 0 run '+tell('Meditation denied. Stand on the altar with stability below 100, out of combat and after cooldown.','red'))
    w.func('meditate/check',
       'execute store result score @s tc_ra run clear @s minecraft:amethyst_shard 0',
       'execute if score @s tc_ra matches 4.. run '+function('meditate/commit'),
       'execute if score @s tc_ra matches ..3 run '+tell('Meditation costs four amethyst shards.','red'))
    w.func('meditate/commit',
       'clear @s minecraft:amethyst_shard 4',
       'scoreboard players add @s tc_stab 30',
       'execute if score @s tc_stab matches 101.. run scoreboard players set @s tc_stab 100',
       'scoreboard players set @s tc_medcd 6000',
       tell('Meditation complete. Stability restored by up to 30; five-minute cooldown.','green'))


def ascend(w):
    # Generic checks and scratch scores: no deductions until both item counts are verified.
    w.func('ascend/dispatch',
       'scoreboard players set @s tc_ok 0',
       f'execute if score @s tc_init matches 1 if score @s tc_curseq matches 1..9 if score @s tc_stab matches 25.. {secure()} {altar()} run scoreboard players set @s tc_ok 1',
       f'execute if score @s tc_ok matches 1 run {function("ascend/validate")}',
       'execute if score @s tc_ok matches 0 run '+tell('Advance denied. Need Sequence 1-9, stability 25+, ritual altar, grounded and out of combat.','red'))
    check=['scoreboard players set @s tc_marks 0',
           'execute if score @s tc_slot matches 1 run scoreboard players operation @s tc_marks = @s tc_pm',
           'execute if score @s tc_slot matches 2 run scoreboard players operation @s tc_marks = @s tc_sm',
           'scoreboard players set @s tc_ok 0',
           'scoreboard players operation @s tc_reqseq = @s tc_curseq']
    for seq,marks in ACT_MARKS.items():
        check.append(f'execute if score @s tc_reqseq matches {seq} if score @s tc_marks matches {marks}.. run {function("ascend/check_s"+str(seq))}')
    check += ['execute if score @s tc_ok matches 0 run '+tell('Not enough acting marks. Alternate your Arcana-specific tasks; use /trigger tc_status and /trigger tc_help.','red')]
    w.func('ascend/validate',check)
    for seq,needs in RITUALS.items():
        assert len(needs)==2
        (a,na),(b,nb)=list(needs.items())
        w.func(f'ascend/check_s{seq}',
            'scoreboard players set @s tc_ok 1',
            f'execute store result score @s tc_ra run clear @s minecraft:{a} 0',
            f'execute store result score @s tc_rb run clear @s minecraft:{b} 0',
            f'execute if score @s tc_ra matches {na}.. if score @s tc_rb matches {nb}.. run {function("ascend/commit_s"+str(seq))}',
            'execute unless score @s tc_ra matches '+str(na)+'.. run '+tell(f'Ritual needs {na}x {a.replace("_"," ")}.','red'),
            'execute unless score @s tc_rb matches '+str(nb)+'.. run '+tell(f'Ritual needs {nb}x {b.replace("_"," ")}.','red'))
        w.func(f'ascend/commit_s{seq}',
            f'clear @s minecraft:{a} {na}',
            f'clear @s minecraft:{b} {nb}',
            f'execute if score @s tc_slot matches 1 run scoreboard players remove @s tc_pm {ACT_MARKS[seq]}',
            f'execute if score @s tc_slot matches 2 run scoreboard players remove @s tc_sm {ACT_MARKS[seq]}',
            'execute if score @s tc_slot matches 1 run scoreboard players remove @s tc_pseq 1',
            'execute if score @s tc_slot matches 2 run scoreboard players remove @s tc_sseq 1',
            'scoreboard players remove @s tc_curseq 1',
            'scoreboard players remove @s tc_stab 12',
            function('powers/refresh'),
            tell(f'Digestion succeeded! Sequence {seq} -> {seq-1}. '+
                 ('You may begin Second Awakening.' if seq==5 else 'Portable swapping unlocked.' if seq==4 else 'Arcana Echo unlocked.' if seq==3 else 'Resonance unlocked.' if seq==2 else 'Apotheosis prestige reached!' if seq==1 else 'Your pathway grows stronger.'),'green'))


def trial(w):
    w.func('trial/start_dispatch',
       'scoreboard players set @s tc_ok 0',
       f'execute if score @s tc_init matches 1 if score @s tc_pseq matches ..4 if score @s tc_secondary matches 0 if score @s tc_trial matches 0 if score @s tc_visit_n matches 1 if score @s tc_visit_e matches 1 if score @s tc_trialcmd matches 1..22 {secure()} {altar()} run scoreboard players set @s tc_ok 1',
       'execute if score @s tc_trialcmd = @s tc_primary run scoreboard players set @s tc_ok 0',
       'execute if score @s tc_ok matches 1 run '+function('trial/start_commit'),
       'execute if score @s tc_ok matches 0 run '+tell('Trial denied: primary S4 or higher, Nether+End visits, free secondary slot, different card ID, and the ritual altar required.','red'))
    w.func('trial/start_commit',
       'scoreboard players operation @s tc_trial = @s tc_trialcmd',
       'scoreboard players set @s tc_tm 0',
       'scoreboard players set @s tc_tphase 0',
       tell('Second Awakening begun. Perform the chosen card\'s two alternating Acting challenges four times total.','aqua'),
       tell('Then bring 16 amethyst shards, 4 ender pearls, 1 ghast tear to the altar and /trigger tc_unlock.','aqua'))
    w.func('trial/unlock_dispatch',
       'scoreboard players set @s tc_ok 0',
       f'execute if score @s tc_init matches 1 if score @s tc_trial matches 1..22 if score @s tc_secondary matches 0 if score @s tc_tm matches 4.. {secure()} {altar()} run scoreboard players set @s tc_ok 1',
       f'execute if score @s tc_ok matches 1 run {function("trial/unlock_check")}',
       'execute if score @s tc_ok matches 0 run '+tell('Unlock denied: finish four trial Acting proofs, remain grounded/out of combat, and return to altar.','red'))
    check=[]
    for i,(item,n) in enumerate(SECOND_OFFERING.items()):
        obj='tc_ra' if i==0 else 'tc_rb' if i==1 else 'tc_marks'
        check.append(f'execute store result score @s {obj} run clear @s minecraft:{item} 0')
    conditions=' '.join(f'if score @s {obj} matches {n}..' for obj,n in zip(('tc_ra','tc_rb','tc_marks'),SECOND_OFFERING.values()))
    w.func('trial/unlock_check',*check,
       'scoreboard players set @s tc_ok 0',
       'execute '+conditions+' run scoreboard players set @s tc_ok 1',
       'execute if score @s tc_ok matches 1 run '+function('trial/unlock_commit'),
       'execute if score @s tc_ok matches 0 run '+tell('Unlock needs 16 amethyst shards, 4 ender pearls and 1 ghast tear.','red'))
    w.func('trial/unlock_commit',
       *[f'clear @s minecraft:{k} {v}' for k,v in SECOND_OFFERING.items()],
       'scoreboard players operation @s tc_secondary = @s tc_trial',
       'scoreboard players set @s tc_trial 0',
       'scoreboard players set @s tc_tm 0',
       'scoreboard players set @s tc_sseq 9',
       'scoreboard players set @s tc_sm 0',
       tell('Secondary Arcana unlocked at Sequence 9! Use /trigger tc_swap set 2 at the altar.','green'))


def swapping(w):
    # All conditions are server-side. Not a second Origin layer, which would stack full buffs.
    # Minecraft 1.18.2 has NO execute-if-dimension; visit milestones use advancements.
    w.func('swap/dispatch',
       'scoreboard players set @s tc_ok 0',
       f'execute if score @s tc_init matches 1 if score @s tc_secondary matches 1..22 if score @s tc_swap matches 1..2 unless score @s tc_swap = @s tc_slot if score @s tc_pseq matches ..3 if score @s tc_swapcd matches 0 {secure()} run scoreboard players set @s tc_ok 1',
       f'execute if score @s tc_init matches 1 if score @s tc_secondary matches 1..22 if score @s tc_swap matches 1..2 unless score @s tc_swap = @s tc_slot if score @s tc_pseq matches 4 if score @s tc_swapcd matches 0 {secure()} {altar()} run scoreboard players set @s tc_ok 1',
       'execute if score @s tc_ok matches 1 run '+function('swap/perform'),
       'execute if score @s tc_ok matches 0 run '+tell('Swap denied: unlock second card; S4 needs altar; S3 allows portable swaps. Must be grounded, out of combat, cooldown zero.','red'))
    w.func('swap/perform',
       'execute if score @s tc_swap matches 1 run '+function('swap/primary'),
       'execute if score @s tc_swap matches 2 run '+function('swap/secondary'))
    for slot,obj,seqobj in [(1,'tc_primary','tc_pseq'),(2,'tc_secondary','tc_sseq')]:
        lines=[]
        for card in CARDS:
            lines.append(f'execute if score @s {obj} matches {card["id"]} run origin set @s origins:origin tarot:{card["slug"]}')
        lines += [f'scoreboard players set @s tc_slot {slot}',
                  f'scoreboard players operation @s tc_current = @s {obj}',
                  f'scoreboard players operation @s tc_curseq = @s {seqobj}',
                  'scoreboard players set @s tc_swapcd 12000',
                  'scoreboard players remove @s tc_stab 4',
                  'execute if score @s tc_stab matches ..0 run scoreboard players set @s tc_stab 0',
                  function('powers/refresh'),
                  tell('Attunement changed. Old Arcana passives removed; new Arcana activated. Switch cooldown: 10 online minutes.','green')]
        w.func('swap/'+('primary' if slot==1 else 'secondary'),lines)


def powers(w):
    w.func('powers/refresh',
       f'power revokeall @s {TIER_SOURCE}',
       f'power revokeall @s {ECHO_SOURCE}',
       f'power revokeall @s {RESONANCE_SOURCE}',
       *[f'execute if score @s tc_current matches {c["id"]} run {function("powers/tier/"+c["slug"])}' for c in CARDS],
       f'execute if score @s tc_curseq matches ..2 if score @s tc_secondary matches 1..22 if score @s tc_slot matches 1 run {function("powers/echo_secondary")}',
       f'execute if score @s tc_curseq matches ..2 if score @s tc_secondary matches 1..22 if score @s tc_slot matches 2 run {function("powers/echo_primary")}',
       f'execute if score @s tc_curseq matches ..1 if score @s tc_secondary matches 1..22 run {function("powers/resonance")}' )
    for card in CARDS:
        slug=card['slug']
        w.func('powers/tier/'+slug,
               *[f'execute if score @s tc_curseq matches ..{seq} run power grant @s {CMD}tier/{slug}/s{seq} {TIER_SOURCE}' for seq in (8,7,6,5,0)])
    for side,obj in [('secondary','tc_secondary'),('primary','tc_primary')]:
        w.func('powers/echo_'+side,
               *[f'execute if score @s {obj} matches {c["id"]} run power grant @s {CMD}echo/{c["slug"]} {ECHO_SOURCE}' for c in CARDS])
    commands=['scoreboard players set @s tc_hasres 0']
    names={c['slug']:c['id'] for c in CARDS}
    for a,b,name in PAIRS:
        ids=names[a],names[b]
        for left,right in [ids,ids[::-1]]:
            cond=f'if score @s tc_primary matches {left} if score @s tc_secondary matches {right}'
            commands.append(f'execute {cond} run power grant @s {CMD}resonance/{name} {RESONANCE_SOURCE}')
            commands.append(f'execute {cond} run scoreboard players set @s tc_hasres 1')
    commands.append(f'execute if score @s tc_hasres matches 0 run power grant @s {CMD}resonance/unbound_resonance {RESONANCE_SOURCE}')
    w.func('powers/resonance',commands)


def build_variant(root:Path,variant:str):
    assert variant in ('only','addon')
    source=root/'datapacks'/variant
    if not (source/'pack.mcmeta').is_file():
        raise FileNotFoundError(f'{source} missing; build existing V2 trees before packaging V3')
    contents={f.relative_to(source).as_posix():f.read_bytes() for f in source.rglob('*') if f.is_file()}
    base_roster=[f'data/tarot/origins/{c["slug"]}.json' for c in CARDS]
    if any(path not in contents for path in base_roster):
        raise ValueError('V2 base is missing one or more Arcana; build aborted')
    layer=json.loads(contents['data/origins/origin_layers/origin.json'])
    if len(layer['origins'])!=22 or layer.get('replace') is not (variant=='only'):
        raise ValueError('Unexpected V2 origin layer configuration')
    source_wings=sum(f'tarot:{c["slug"]}/wings' in json.loads(contents[f'data/tarot/origins/{c["slug"]}.json'])['powers'] for c in CARDS)
    if source_wings!=18:raise ValueError('V2 base has unexpected glider count')
    contents['pack.mcmeta']=j({'pack':{'pack_format':9,'description':'The Tarot Club | V3 Path of Ascension | MC 1.18.2'}})
    w=Writer(contents)
    core(w)
    acting(w)
    ascend(w)
    trial(w)
    swapping(w)
    powers(w)
    write_powers(w)
    if (root/'docs/ASCENSION.md').exists():
        contents['ASCENSION_GUIDE.md']=(root/'docs/ASCENSION.md').read_bytes()
    path=root/'output'/f'The_Tarot_Club_V3_Ascension_{variant.upper()}_1.18.2.zip'
    path.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(path,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(contents.items()):z.writestr(name,data)
    return path

def build_all(root:Path):
    root=Path(root)
    result={variant:build_variant(root,variant) for variant in ('only','addon')}
    return result

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Build Minecraft 1.18.2 V3 Path of Ascension ZIPs')
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent.parent)
    args=parser.parse_args()
    for kind,archive in build_all(args.root).items():
        print(kind,archive,archive.stat().st_size)
