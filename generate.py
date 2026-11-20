"""The Tarot Club: 22 Arcana Origins for Minecraft 1.18.2 / Origins 1.4.1.
No runtime dependencies: datapack uses only published origins/apoli power/action types.
"""
from __future__ import annotations
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
DST = ROOT/'output'
DST.mkdir(exist_ok=True)
ZIP = DST/'The_Tarot_Club_22_Arcana_1.18.2.zip'
ZIP_ONLY = DST/'The_Tarot_Club_22_Arcana_Only_1.18.2.zip'

# The game's Major Arcana list, NOT the novel's distinct 22 Standard Pathways.
CARDS = [
('fool','The Fool','minecraft:totem_of_undying','Klein Moretti','Fool','Canon',
 'Careful, compassionate, theatrical; triumphs by preparation rather than brute force.',
 'Cautious trickster and escape artist who manipulates the fight without dominating it.'),
('magician','The Magician','minecraft:ender_pearl','Fors Wall','Door','Canon',
 'Helpful, imaginative, comfort-loving writer, reluctant to take unnecessary risks.',
 'Portal traveler with a reliable short-range escape and vertical mobility.'),
('high_priestess','The High Priestess','minecraft:amethyst_shard','Original card archetype','White Tower / Hermit','Original',
 'Observant, enigmatic, patient; carries forbidden insight with uncomfortable certainty.',
 'Knowledge and enemy revelation, balanced by fragility.'),
('empress','The Empress','minecraft:rose_bush','Franca Roland','Demoness','Canon (Book Two)',
 'Expressive, brave, resourceful; turns precarious circumstances into possibilities.',
 'Mirror-themed witch of toxins, beauty, misdirection and vulnerability.'),
('emperor','The Emperor','minecraft:golden_helmet','Original card archetype','Black Emperor','Original',
 'Proud, calculating, disciplined; seeks absolute order even at a personal cost.',
 'Grounded tank who controls crowds and resists retaliation.'),
('hierophant','The Hierophant','minecraft:enchanting_table','Original card archetype','White Tower / Sun','Original',
 'Reverent scholar and counselor; rewards planning, ritual and shared knowledge.',
 'Stationary support scholar who sees the enemy and grants blessings.'),
('lovers','The Lovers','minecraft:pink_tulip','Original card archetype','Mother / Visionary','Original',
 'Empathic mediator; values connection, promises and sacrifice.',
 'Support guardian whose healing also benefits enemies if carelessly used.'),
('chariot','The Chariot','minecraft:blaze_rod','Lumian Lee','Red Priest','Canon (Book Two)',
 'Defiant, sly, courageous and protective; channels unrest into action.',
 'High-mobility warlock whose powerful assault demands food and restraint.'),
('strength','Strength','minecraft:iron_axe','Original card archetype','Twilight Giant','Original',
 'Steadfast, courageous, protective; meets danger directly.',
 'Unflying juggernaut with immense health but slower movement.'),
('hermit','The Hermit','minecraft:enchanted_book','Cattleya','Hermit','Canon',
 'Brilliant, experienced and guarded; still yearns for belonging.',
 'Fragile investigator who marks enemies and commands star-bolts.'),
('wheel_of_fortune','Wheel of Fortune','minecraft:clock','Original card archetype','Wheel of Fortune','Original',
 'Impulsive, curious and dangerously optimistic; accepts risk as a principle.',
 'True random fate-roll with both boons and punishing outcomes.'),
('justice','Justice','minecraft:emerald','Audrey Hall','Visionary','Canon',
 'Compassionate, intelligent and composed; listens before judging.',
 'Mental restraint and group support, but weak direct melee damage.'),
('hanged_man','The Hanged Man','minecraft:trident','Alger Wilson','Tyrant, later Hanged Man','Canon',
 'Strategic, ambitious and suspicious; commands the storm with discipline.',
 'Storm-call that slows foes, keen in water, vulnerable in direct combat.'),
('death','Death','minecraft:bone','Original card archetype','Death','Original',
 'Solemn, reflective and merciful in finality; sees every ending as a beginning.',
 'Soul-harvesting survivor who recovers by defeating threats.'),
('temperance','Temperance','minecraft:glass_bottle','Sharron','Chained','Canon (Book Two)',
 'Quiet, reserved, self-controlled; refuses to be ruled by desire.',
 'Wraith tactician who fades from sight but suffers a frail body.'),
('devil','The Devil','minecraft:nether_wart','Original card archetype','Abyss','Original',
 'Charismatic and manipulative; every gift has an ugly hidden price.',
 'A risky infernal bargain: short power spikes, hunger and sunlight curses.'),
('tower','The Tower','minecraft:cracked_stone_bricks','Original card archetype','Tyrant / Red Priest','Original',
 'Catastrophic, uncompromising and unpredictable; breaks the safe path.',
 'Disaster-themed crowd-control specialist who pays for recklessness.'),
('star','The Star','minecraft:nether_star','Leonard Mitchell','Darkness','Canon',
 'Casual and poetic, yet perceptive and brave when it counts.',
 'Nightwatcher who obscures enemies and thrives beyond daylight.'),
('moon','The Moon','minecraft:glistering_melon_slice','Emlyn White','Moon','Canon',
 'Proud, eccentric and sheltered; gradually learns responsibility.',
 'Sanguine medicine and nocturnal mastery, weakened beneath the sun.'),
('sun','The Sun','minecraft:sunflower','Derrick Berg','Sun','Canon',
 'Sincere, loyal and hopeful; carries light to dark places.',
 'Purifying defender whose radiance falters away from sunlight.'),
('judgement','Judgement','minecraft:iron_sword','Xio Derecha','Justiciar','Canon',
 'Principled, determined and stern but kind; values a fair sentence.',
 'Grounded arbiter who marks targets and stands her ground.'),
('world','The World','minecraft:compass','Klein Moretti as Gehrman Sparrow','Fool','Canon (same person as Fool)',
 'Cold-seeming, daring and ruthlessly efficient; secretly protective.',
 'Aggressive hunter persona of Klein: enemy marks, precision and evasion.'),
]

GLIDERS = {c[0] for c in CARDS} - {'emperor','hierophant','strength','judgement'}

KEY_G={'key':'key.origins.primary_active'}
KEY_V={'key':'key.origins.secondary_active'}

def fx(name, seconds, level=1):
    assert seconds > 0 and level > 0
    return {'effect':'minecraft:'+name,'duration':round(seconds*20),'amplifier':level-1,'show_particles':True}

def apply(*effects):
    return {'type':'origins:apply_effect',**({'effect':effects[0]} if len(effects)==1 else {'effects':list(effects)})}

def group(*actions):
    return {'type':'origins:and','actions':list(actions)} if len(actions)>1 else actions[0]

def hunger(v=1.0):
    return {'type':'origins:exhaust','amount':v}

def heal(v):
    return {'type':'origins:heal','amount':v}

def push(up=0.65, forward=0):
    return {'type':'origins:add_velocity','x':0,'y':up,'z':forward,'space':'local_horizontal'} if forward else {'type':'origins:add_velocity','y':up}

def aoe(rad,*effects):
    return {'type':'origins:area_of_effect','radius':rad,'bientity_action':{
      'type':'origins:target_action','action':apply(*effects)},'include_target':False}

def arcane_ray(dist,*effects):
    return {'type':'origins:raycast','distance':dist,'block':True,'entity':True,
         'bientity_action':{'type':'origins:target_action','action':apply(*effects)}}

def effect_power(name, description, action, cd, key='primary'):
    return {'type':'origins:active_self','name':name,'description':description,'cooldown':cd,
     'hud_render':{'should_render':True,'bar_index':2 if key=='primary' else 3},
     'key':KEY_G if key=='primary' else KEY_V,'entity_action':action}

def projectile(name,description,entity,cd,key='secondary',count=1,speed=1.5):
    return {'type':'origins:fire_projectile','name':name,'description':description,
      'entity_type':'minecraft:'+entity,'cooldown':cd,'count':count,'speed':speed,
      'divergence':3.0 if count>1 else 0.2,'tag':'{pickup:0b}' if entity in ('arrow','spectral_arrow') else '{}',
      'hud_render':{'should_render':True,'bar_index':3 if key=='secondary' else 2},
      'key':KEY_V if key=='secondary' else KEY_G}

def launch(name,description,cd,speed=0.8,key='secondary'):
    return {'type':'origins:launch','name':name,'description':description,
      'cooldown':cd,'speed':speed,'sound':'minecraft:entity.phantom.flap',
      'hud_render':{'should_render':True,'bar_index':3 if key=='secondary' else 2},
      'key':KEY_V if key=='secondary' else KEY_G}

def stat(name,desc,attr,value,op='addition',ptype='origins:attribute'):
    return {'type':ptype,'name':name,'description':desc,'modifier':{
     'attribute': 'minecraft:generic.'+attr,'name':name,'value':value,'operation':op}}

def mod_damage(name,desc,value,taken=False,cond=None):
    o={'type':'origins:modify_damage_taken' if taken else 'origins:modify_damage_dealt',
      'name':name,'description':desc,'modifier':{'name':name,'operation':'multiply_total','value':value}}
    if cond: o['condition']=cond
    return o

def passive(name,desc,type_,**kw):
    return {'type':type_,'name':name,'description':desc,**kw}

def triggered(name,desc,period,effect,condition):
    return {'type':'origins:action_over_time','name':name,'description':desc,
       'interval':period,'entity_action':apply(effect),'condition':condition}

def xp(name,desc,frac):
    return {'type':'origins:modify_xp_gain','name':name,'description':desc,
            'modifier':{'name':name,'operation':'multiply_total','value':frac}}

def onhit(name,desc,effect,cooldown):
    return {'type':'origins:target_action_on_hit','name':name,'description':desc,
        'entity_action':apply(effect),'cooldown':cooldown,
        'hud_render':{'should_render':False}}

def kill_heal(name,desc,amount,cooldown):
    return {'type':'origins:self_action_on_kill','name':name,'description':desc,
        'entity_action':heal(amount),'cooldown':cooldown,
        'hud_render':{'should_render':False}}

def wing(name):
    return {'type':'origins:elytra_flight','name':name,
      'description':'Built-in Elytra gliding, even without an Elytra item. Jump while falling to unfold your astral wings. This is gliding, not creative flight.',
      'render_elytra':True}

sun={'type':'origins:exposed_to_sun'}
no_sun={'type':'origins:exposed_to_sun','inverted':True}
wet={'type':'origins:submerged_in','fluid':'minecraft:water'}
not_wet={'type':'origins:submerged_in','fluid':'minecraft:water','inverted':True}

# One primary, one secondary, passive(s), weakness(es). 20 TPS. Player AoE affects ANY nearby
# living entity except self: intentional double-edged effect; see guide for PVP/PVE notes.
BUILD = {
'fool': [
 effect_power('Gray Fog Masquerade','G: Hide yourself for 6s, gain Speed I for 6s; costs hunger.',group(apply(fx('invisibility',6),fx('speed',6)),hunger(2)),420),
 effect_power('Marionette Thread','V: Sightline curse on one target within 14 blocks: heavy slowness and glowing.',group(arcane_ray(14,fx('slowness',5,3),fx('glowing',6)),hunger(1.2)),340,'secondary'),
 onhit('Seer Instinct','Every 14s, your next successful melee hit briefly weakens its target.',fx('weakness',4),280),
 stat('Price: Frail Body','Drawback: Your cautious body has one fewer heart.', 'max_health',-2),
 ],
'magician':[
 projectile('Doorstep','G: Throw a summoned ender pearl to travel through space. The normal ender-pearl damage still applies.','ender_pearl',420,'primary',1,1.3),
 launch('Traveler\'s Updraft','V: Leap upward into an Elytra glide; 24s cooldown.',480,0.9),
 stat('Traveler\'s Stride','Travelers move 10% faster on land.','movement_speed',0.10,'multiply_total'),
 mod_damage('Price: Untrained Duelist','Drawback: You deal 12% less melee damage.',-0.12),
 ],
'high_priestess':[
 effect_power('Unsealed Sight','G: Illuminate nearby living creatures with Glowing for 9s; may reveal allies.',group(aoe(14,fx('glowing',9)),hunger(1.5)),300),
 effect_power('Foreknowledge','V: Gain Night Vision and Resistance I for 10s.',group(apply(fx('night_vision',10),fx('resistance',10)),hunger(1)),460,'secondary'),
 xp('Arcane Literacy','Gain 25% more experience from orbs.', 0.25),
 stat('Price: Mortal Shell','Drawback: 2 hearts fewer maximum health.', 'max_health',-4),
 ],
'empress':[
 effect_power('Mirror Plague','G: Afflict nearby living entities with Poison I and Slowness I. Allies are not protected.',group(aoe(6,fx('poison',4),fx('slowness',5)),hunger(2.2)),450),
 effect_power('Glass Reflection','V: Vanish for 6s and gain Speed II for 5s.',group(apply(fx('invisibility',6),fx('speed',5,2)),hunger(2)),500,'secondary'),
 stat('Witch\'s Grace','Movement is 8% faster.','movement_speed',0.08,'multiply_total'),
 mod_damage('Price: Cracked Mirror','Drawback: Take 16% more damage from attacks.',0.16,True),
 ],
'emperor':[
 effect_power('Imperial Decree','G: Slowness II and Weakness I to nearby creatures. Everyone nearby pays for disobedience.',group(aoe(7,fx('slowness',6,2),fx('weakness',6)),hunger(2.5)),420),
 effect_power('Royal Bulwark','V: Resistance II for 8s; movement slows during the decree.',group(apply(fx('resistance',8,2),fx('slowness',6)),hunger(2.3)),520,'secondary'),
 stat('Armored Sovereign','Permanent +3 armor points.','armor',3),
 stat('Price: Weight of Law','Drawback: Your speed is reduced by 12%. No astral wings.','movement_speed',-0.12,'multiply_total'),
 ],
'hierophant':[
 effect_power('Sacred Reading','G: Reveal nearby living beings and give yourself Haste II for 12s.',group(aoe(12,fx('glowing',8)),apply(fx('haste',12,2)),hunger(1.5)),460),
 effect_power('Shared Blessing','V: Grant Regeneration I for 6s to everyone within 6 blocks, including enemies; heal yourself by 1 heart.',group(aoe(6,fx('regeneration',6)),heal(2),hunger(2)),600,'secondary'),
 xp('Ritual Scholar','You learn 35% faster from experience orbs.',0.35),
 stat('Price: Ascetic Discipline','Drawback: 2 fewer hearts; no astral wings.','max_health',-4),
 ],
'lovers':[
 effect_power('Promise of Hearts','G: Regeneration II to living entities within 7 blocks, friend or foe. A tactical choice.',group(aoe(7,fx('regeneration',6,2)),hunger(2)),500),
 effect_power('Sacrificial Vow','V: Gain Absorption II for 10s but Weakness I for 6s; costs hunger.',group(apply(fx('absorption',10,2),fx('weakness',6)),hunger(1.8)),460,'secondary'),
 stat('Light of Togetherness','A modest +1 heart of resilience.','max_health',2),
 mod_damage('Price: Reluctant Fighter','Drawback: You deal 17% less melee damage.',-0.17),
 ],
'chariot':[
 effect_power('War March','G: Strength II and Speed II for 9s, at a serious hunger cost.',group(apply(fx('strength',9,2),fx('speed',9,2)),hunger(4.5)),500),
 projectile('Ironblood Volley','V: Fire three non-retrievable arrows in a rapid volley.','arrow',320,'secondary',3,1.7),
 passive('Flame Within','Fire cannot burn a veteran of the Red Priest.','origins:fire_immunity'),
 triggered('Price: Drowned Flame','Drawback: While submerged in water, you suffer Slowness II.',20,fx('slowness',3,2),wet),
 ],
'strength':[
 effect_power('Lionheart','G: Strength II and Resistance II for 8s; you also become slow for 7s.',group(apply(fx('strength',8,2),fx('resistance',8,2),fx('slowness',7)),hunger(3.0)),560),
 effect_power('Earthshaker','V: Stagger nearby creatures with Slowness III and Weakness I.',group(aoe(5,fx('slowness',5,3),fx('weakness',5)),hunger(2.5)),400,'secondary'),
 stat('Giant Blood','Permanent +3 hearts.','max_health',6),
 stat('Iron Hide','Additional +2 armor points.','armor',2),
 stat('Price: Mountain\'s Burden','Drawback: Move 16% slower. You cannot glide without an item.','movement_speed',-0.16,'multiply_total'),
 ],
'hermit':[
 effect_power('Eyes of Mystery Prying','G: Mark a creature at sightline range 18 with Glowing and Weakness II.',group(arcane_ray(18,fx('glowing',11),fx('weakness',6,2)),hunger(1.5)),300),
 projectile('Astral Scriptorium','V: Manifest two spectral arrows of starlight.','spectral_arrow',380,'secondary',2,1.5),
 xp('Hidden Scholarship','Gain 30% more experience from orbs.',0.30),
 stat('Price: Forbidden Knowing','Drawback: 1 fewer heart.','max_health',-2),
 ],
'wheel_of_fortune':[
 effect_power('Fate\'s Sixfold Cast','G: Roll one of six equal outcomes: Speed II, Strength II, Regeneration II, Blindness, Hunger II, or Poison I.',group({'type':'origins:choice','actions':[
    {'weight':1,'element':apply(fx('speed',12,2))},
    {'weight':1,'element':apply(fx('strength',9,2))},
    {'weight':1,'element':apply(fx('regeneration',7,2))},
    {'weight':1,'element':apply(fx('blindness',5))},
    {'weight':1,'element':apply(fx('hunger',12,2))},
    {'weight':1,'element':apply(fx('poison',6))},
 ]},hunger(1)),280),
 effect_power('Borrowed Luck','V: Risk a second, milder gamble (either Resistance I or Slowness II).',{'type':'origins:choice','actions':[
 {'weight':3,'element':apply(fx('resistance',9))},
 {'weight':2,'element':apply(fx('slowness',9,2))}]},380,'secondary'),
 stat('Fortune\'s Step','Permanent +7% walking speed.','movement_speed',0.07,'multiply_total'),
 mod_damage('Price: Unstable Odds','Drawback: Receive 12% more damage.',0.12,True),
 ],
'justice':[
 effect_power('Psychological Stillness','G: Calm living entities within 8 blocks with Weakness II and Slowness I.',group(aoe(8,fx('weakness',6,2),fx('slowness',4)),hunger(1.7)),380),
 effect_power('Therapist\'s Shelter','V: Regeneration II for nearby living beings including foes; grant yourself Absorption I.',group(aoe(6,fx('regeneration',7,2)),apply(fx('absorption',12)),hunger(2)),600,'secondary'),
 stat('Measured Heart','A calm mind grants +1 heart.','max_health',2),
 mod_damage('Price: Pacifist Heart','Drawback: Melee attacks inflict 20% less damage.',-0.20),
 ],
'hanged_man':[
 effect_power('Tempest Canticle','G: The air thickens; Slowness II on nearby living entities while you gain Resistance I.',group(aoe(7,fx('slowness',7,2)),apply(fx('resistance',7)),hunger(2.5)),480),
 projectile('Sea-Lord\'s Javelin','V: Fire two swift spectral bolts.','spectral_arrow',300,'secondary',2,1.7),
 stat('Experienced Sailor','You travel 9% faster across land.','movement_speed',0.09,'multiply_total'),
 onhit('Sea Pressure','Successful strikes briefly slow victims, 11s internal cooldown.',fx('slowness',3),220),
 stat('Price: Unsteady Flesh','Drawback: One fewer heart.','max_health',-2),
 ],
'death':[
 effect_power('Grave Quietus','G: Send out an aura of Wither I for 4s, affecting everyone nearby.',group(aoe(5,fx('wither',4)),hunger(2.2)),500),
 effect_power('Return from the Brink','V: Regeneration II and Resistance I for 7s; costs a heavy portion of hunger.',group(apply(fx('regeneration',7,2),fx('resistance',7)),hunger(3)),620,'secondary'),
 kill_heal('Harvest the Departed','Recover one heart whenever you defeat a creature, at most once per 8s.',2,160),
 triggered('Price: Dawn\'s Reminder','Drawback: In direct sunlight, you suffer Weakness I.',20,fx('weakness',3),sun),
 ],
'temperance':[
 effect_power('Wraith Form','G: Invisibility and Resistance I for 6s, but self-inflicted Weakness for 6s.',group(apply(fx('invisibility',6),fx('resistance',6),fx('weakness',6)),hunger(1.6)),430),
 effect_power('Quiet Possession','V: Fix the target you face with Slowness III and Weakness II.',group(arcane_ray(12,fx('slowness',5,3),fx('weakness',5,2)),hunger(1.5)),450,'secondary'),
 passive('Eyes Behind Glass','Permanent Night Vision.','origins:night_vision',strength=1.0),
 stat('Price: Hollow Body','Drawback: 2 fewer hearts.','max_health',-4),
 ],
'devil':[
 effect_power('Forbidden Bargain','G: Strength III and Speed II for 7s, but suffer Poison I and exhausting hunger.',group(apply(fx('strength',7,3),fx('speed',7,2),fx('poison',4)),hunger(5)),600),
 effect_power('Tempting Whispers','V: Nearby beings suffer Weakness II and Hunger I; this affects allies.',group(aoe(7,fx('weakness',6,2),fx('hunger',8)),hunger(1.6)),380,'secondary'),
 passive('Infernal Heritage','You do not burn in fire.','origins:fire_immunity'),
 triggered('Price: Sun-Searing Bargain','Drawback: Direct sunlight inflicts Weakness II.',20,fx('weakness',3,2),sun),
 ],
'tower':[
 effect_power('Collapse of Certainty','G: Nearby targets become blind for 3s and slow for 5s. You are not protected from retaliation.',group(aoe(8,fx('blindness',3),fx('slowness',5)),hunger(2.5)),480),
 launch('Rising Ruin','V: Violent skyward launch, usable before gliding.',420,1.1),
 stat('Shatterer','Your melee blows are 9% stronger.','attack_damage',0.09,'multiply_total'),
 mod_damage('Price: Glass Foundation','Drawback: You take 20% more damage.',0.2,True),
 ],
'star':[
 effect_power('Midnight Poetry','G: Blindness and Slowness I to nearby targets, revealing the advantage of darkness.',group(aoe(8,fx('blindness',4),fx('slowness',5)),hunger(1.6)),420),
 effect_power('Nightwatcher\'s Refuge','V: Invisibility and Night Vision for 8s.',group(apply(fx('invisibility',8),fx('night_vision',8)),hunger(2)),480,'secondary'),
 passive('Sleepless Gaze','You see clearly in darkness.','origins:night_vision',strength=1.0),
 triggered('Price: Morning Sorrow','Drawback: Direct sunlight gives Slowness I.',20,fx('slowness',3),sun),
 ],
'moon':[
 effect_power('Scarlet Medicine','G: Regeneration II for 9s, but must spend substantial energy.',group(apply(fx('regeneration',9,2)),hunger(2.5)),480),
 effect_power('Blood Moon Awakening','V: Strength II and Night Vision at night or indoors; in direct sun, only Resistance I.',{'type':'origins:if_else','condition':no_sun,
 'if_action':group(apply(fx('strength',8,2),fx('night_vision',8)),hunger(2)),
 'else_action':group(apply(fx('resistance',6)),hunger(2))},480,'secondary'),
 passive('Sanguine Eyes','Permanent Night Vision.','origins:night_vision',strength=1.0),
 triggered('Price: Crimson Daylight','Drawback: In direct sun, you are weakened.',20,fx('weakness',3),sun),
 ],
'sun':[
 effect_power('Unshadowed Pulse','G: Glowing on nearby creatures and Strength I for yourself. Allies are visible too.',group(aoe(10,fx('glowing',10)),apply(fx('strength',8)),hunger(2)),420),
 effect_power('Radiant Shelter','V: Regeneration II, Resistance I, and brief illumination (Night Vision).',group(apply(fx('regeneration',7,2),fx('resistance',7),fx('night_vision',9)),hunger(2.8)),540,'secondary'),
 passive('Vessel of Dawn','Fire has no power over you.','origins:fire_immunity'),
 triggered('Price: Lightless Heart','Drawback: Whenever you are away from sunlight, you suffer Slowness I.',20,fx('slowness',3),no_sun),
 ],
'judgement':[
 effect_power('Sentence Pronounced','G: Target you are looking at becomes Slowness III and Glowing.',group(arcane_ray(12,fx('slowness',6,3),fx('glowing',8)),hunger(1.6)),380),
 effect_power('Writ of Protection','V: Resistance II and Strength I for 7s. You must stand your ground.',group(apply(fx('resistance',7,2),fx('strength',7),fx('slowness',6)),hunger(2.2)),500,'secondary'),
 stat('Marshal\'s Plate','Gain +3 armor points.','armor',3),
 stat('Price: Heavy Duty','Drawback: Move 10% slower; no astral wings.','movement_speed',-0.10,'multiply_total'),
 ],
'world':[
 effect_power('Hunting Notice','G: Mark a target within 16 blocks with Glowing and Weakness II.',group(arcane_ray(16,fx('glowing',12),fx('weakness',6,2)),hunger(1)),260),
 effect_power('Faceless Withdrawal','V: Vanish for 5s with Speed II and Absorption I, costing hunger.',group(apply(fx('invisibility',5),fx('speed',6,2),fx('absorption',9)),hunger(2.7)),480,'secondary'),
 mod_damage('Bounty Hunter','You strike 10% harder in melee.',0.10),
 stat('Price: Mortal Hunter','Drawback: One fewer heart.','max_health',-2),
 ],
}

# Check the data model itself before generating any user-facing files.
assert len(CARDS)==22 and set(BUILD)=={c[0] for c in CARDS}
assert len(GLIDERS)==18
assert all(len(BUILD[c[0]])>=4 for c in CARDS)


from passive_v2 import apply_v2
BUILD = apply_v2(BUILD)

def jtxt(obj): return json.dumps(obj,ensure_ascii=False,indent=2)+'\n'

def make():
    contents={'pack.mcmeta':jtxt({'pack':{'pack_format':9,'description':'The Tarot Club | Passive-first V2 Alpha | 1.18.2'}})}
    contents['data/origins/origin_layers/origin.json']=jtxt({'replace':False,'origins':['tarot:'+c[0] for c in CARDS]})
    docs=['# The Tarot Club — 22 Major Arcana Origins', '',
     '**Minecraft 1.18.2 • Fabric • Origins 1.4.1 • pack_format 9**', '',
     'Fan-made reinterpretations of *Lord of the Mysteries* and *Circle of Inevitability* concepts for a Minecraft multiplayer server; not an official adaptation.',
     '', '## Installation (Pterodactyl / play.hosting)', '',
     '1. Back up your test world or final SMP before making changes.',
     '2. Stop the Minecraft server. Do **not** put this ZIP in `/mods`.',
     '3. Upload **only one of the two ZIP versions** into `<world-name>/datapacks/` (for your current test world: `tarot-world-test/datapacks/`).',
     '4. Start server; run `datapack list` and confirm this pack is enabled. If server already running, `reload` is possible, but a stop/start is safer for the initial install.',
     '5. Run `origin set <player> origins:origin tarot:fool` to test the Fool; replace `fool` with any ID below.',
     '6. Once verified, transfer the ZIP to the **final** world\'s `datapacks` folder. Each world has its own datapacks.',
     '', 'These are server-side datapack JSON files: players only need the same Origins mod and Fabric API as the server. No KubeJS script or other custom Origins addon is required.',
     '', '### Elytra and controls', '',
     f'**{len(GLIDERS)} / 22 cards have a real Origins built-in Elytra-flight power**. Wings are rendered using the normal Elytra appearance. You do not need to equip an Elytra; this is **gliding**, not creative flight. Start falling, then press Jump again to enter glide mode. Firework rockets can still be used in normal Elytra flight.',
     'Primary ability: `key.origins.primary_active` (normally **G**). Secondary ability: `key.origins.secondary_active` (normally **V**). Change keys under Minecraft Controls if needed.',
     'The power screen lists each benefit and drawback with its cooldown.',
     '', '### Design and PvP warnings', '',
     '- The 22 tarot cards are not canonically the 22 Standard Pathways. Card names are member codenames; this pack combines canon members with original card concepts.',
     '- The Fool and the World represent two personae of the **same** character, Klein Moretti, but are deliberately distinct playable builds.',
     '- The Empress and Chariot references are Book Two / *Circle of Inevitability* spoilers.',
     '- **Area-of-effect abilities affect all nearby living targets, including teammates, villagers, pets, and enemy players.** This deliberate cost matters in SMP battles; use cautiously.',
     '- **V2 ALPHA:** passive traits and unique drawbacks are new and have not been tested on this server. Keep the working V1 ZIP for rollback.',
     '- Lunar-cycle-only effects and team-only soul bonds require optional scripting and are not implemented here.',
     '- **16 out of 22? No:** exactly 18 wings, four grounded cards (Emperor, Hierophant, Strength, Judgement).',
     '- No admin command execution, item duplication, terrain destruction, or KubeJS privileges are used by this datapack.',
     '- This pack appends all 22 cards to the existing Origins selection layer (`replace:false`). It will not replace existing vanilla or other custom Origins.',
     '- The pack has been structurally checked; **live in-game behavior has not been tested in your server**. Begin with your temporary test world, inspect the server log, and test abilities one by one.',
     '', '## The 22 cards — personalities, powers, weaknesses', '',
    ]
    for idx,(slug,title,icon,character,pathway,status,personality,role) in enumerate(CARDS):
       base=f'data/tarot/powers/{slug}'
       ids=[]
       powers=BUILD[slug]
       for pi,power in enumerate(powers):
           filepath=f'{base}/'+(['primary','secondary','passive','drawback','extra_1','extra_2'][pi] if pi<6 else f'extra_{pi}')+'.json'
           contents[filepath]=jtxt(power)
           ids.append('tarot:'+slug+'/'+filepath.rsplit('/',1)[-1][:-5])
       if slug in GLIDERS:
           filepath=f'{base}/wings.json'
           contents[filepath]=jtxt(wing(f'{title}: Astral Wings'))
           ids.append('tarot:'+slug+'/wings')
       origin={'powers':ids,'icon':icon,'name':title,'description':role+' Inspired by '+character+' ('+status+').',
             'impact':3,'order':idx}
       contents[f'data/tarot/origins/{slug}.json']=jtxt(origin)
       flight='**Built-in Elytra glide**' if slug in GLIDERS else '**Grounded (no built-in glide)**'
       docs.extend([f'### {idx:02d} — {title} (`tarot:{slug}`)', '',
           f'- **Lore basis:** {character}; {pathway} pathway influence. **{status}**.',
           f'- **Personality:** {personality}',
           f'- **Playstyle:** {role}',
           f'- **Primary (G):** {powers[0]["name"]} — {powers[0]["description"]} Cooldown: {powers[0]["cooldown"]/20:g}s.',
           f'- **Secondary (V):** {powers[1]["name"]} — {powers[1]["description"]} Cooldown: {powers[1]["cooldown"]/20:g}s.',
           f'- **Special traits:** '+ '; '.join(p['name']+' — '+p['description'] for p in powers[2:] if not p['name'].lower().startswith(('price:','drawback:','curse:','burden:'))),
           f'- **Weakness:** '+ '; '.join(p['description'] for p in powers[2:] if p['name'].lower().startswith(('price:','drawback:','curse:','burden:'))),
           f'- **Movement:** {flight}.',
           '',])
    docs.extend([
      '## How to make and modify a custom Origin', '',
      'Each origin is a JSON under `data/tarot/origins/<id>.json`. The `powers` array references power JSONs stored under `data/tarot/powers/<id>/*.json`.',
      'The layer `data/origins/origin_layers/origin.json` appends our 22 origin IDs. You can tweak numbers (durations are in ticks; 20 ticks = 1 second) by editing the JSON and zipping the datapack again with `pack.mcmeta` at the archive root.',
      '', 'Example origin (trimmed):', '', '```json',
      jtxt({'powers':['tarot:fool/primary','tarot:fool/secondary','tarot:fool/passive','tarot:fool/drawback','tarot:fool/wings'],
        'icon':'minecraft:totem_of_undying','name':'The Fool','description':'A careful trickster.'}).rstrip(),
      '```', '',
      'Example custom power (trimmed):', '', '```json',
      jtxt({'type':'origins:active_self','name':'Veil of Fog',
      'description':'Invisibility for 6 seconds, with a cooldown.',
      'entity_action':{'type':'origins:apply_effect','effect':fx('invisibility',6)},
      'cooldown':420,'key':KEY_G,'hud_render':{'should_render':True,'bar_index':2}}).rstrip(),
      '```', '',
      '## Inspiring examples to learn from', '',
     '- The Origins developer example repository shows complete custom Origins (`aerum_origin`, `deepling_origin`, `salamander_origin`), changing powers (`elytrian_boost`) and even adding a whole second selection layer (`second_layer`): https://github.com/apace100/origins-example-packs',
     '- Origins++ showcases a large roster of more than 100 playable Origins; examine its designs as balance inspiration, not as a technical dependency: https://modrinth.com/mod/origins-plus-plus',
     '- Origins: Starborne is an example of a themed 1.18.2-era custom Origin: https://www.curseforge.com/minecraft/mc-mods/origins-starborne',
     '- To go beyond JSON powers, custom textures need an optional resource pack; truly novel mechanics may require a Java mod or script integration. This pack deliberately stays within built-in powers for compatibility.', '',
     '## Canon/source boundaries and references', '',
      'Core Origins 1.4.1 documentation: https://origins.readthedocs.io/en/1.4.1/',
      'Example packs from Origins developers: https://github.com/apace100/origins-example-packs',
      'List of Tarot Club members and their actual pathways: https://lordofmysteries.wiki.gg/wiki/Tarot_Club/List_of_Members',
      '22 Standard Pathways: https://lordofmysteries.wiki.gg/wiki/Pathways',
      'Tarot Major Arcana: https://lordofmysteries.wiki.gg/wiki/Tarot_Cards',
      'Character personality/reference articles: https://lordofmysteries.wiki.gg/wiki/Klein_Moretti ; https://lordofmysteries.wiki.gg/wiki/Audrey_Hall ; https://lordofmysteries.wiki.gg/wiki/Alger_Wilson ; https://lordofmysteries.wiki.gg/wiki/Derrick_Berg ; https://lordofmysteries.wiki.gg/wiki/Fors_Wall ; https://lordofmysteries.wiki.gg/wiki/Cattleya ; https://lordofmysteries.wiki.gg/wiki/Emlyn_White',
      'This is fan-created gameplay translation, not a claim that these skills or original personas are canonical.', '',
      '## Testing checklist', '',
      '1. All 22 cards appear in origin selection.',
      '2. Switch between two origins with the server command; confirm G and V actions and cooldowns.',
      '3. For wings, drop from a ledge and press jump again; verify gliding works with and without chest armor.',
      '4. Test exposed-to-sun weaknesses, submerged-in-water weakness, team AoE, and no-flight cards.',
      '5. Check after death/respawn, server restart, Nether travel, and returning to the Overworld.',
      '6. Watch console and RAM on 3GB play.hosting; no new dependencies are required.',
      '',
    ])
    # Remove any stray typo/inconsistent sample annotation, consciously retained "18 / 22" everywhere.
    docs=[x for x in docs if not x.startswith('- **16 out of 22?')]
    contents['ARCANA_GUIDE.md']='\n'.join(docs)+'\n'
    with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for filename,data in contents.items(): z.writestr(filename,data)
    contents_only=dict(contents)
    contents_only['data/origins/origin_layers/origin.json']=jtxt({'replace':True,'origins':['tarot:'+c[0] for c in CARDS]})
    with zipfile.ZipFile(ZIP_ONLY,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for filename,data in contents_only.items(): z.writestr(filename,data)
    print('BUILT',ZIP,ZIP.stat().st_size,'ONLY',ZIP_ONLY.stat().st_size,'JSON',sum(n.endswith('.json') for n in contents),'wings',len(GLIDERS))
    return ZIP

if __name__=='__main__': make()