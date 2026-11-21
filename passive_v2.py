"""Passive-first V2 alpha powers for all 22 Arcana; Minecraft 1.18.2, Origins 1.4.1."""
from __future__ import annotations

def p(name, desc, kind, **kwargs):
    # Origins 1.4.1 / Apoli 2.3.3 rejects invisibility without this
    # required serializer field. Preserve V2's intentionally visible armor.
    if kind == 'origins:invisibility':
        kwargs.setdefault('render_armor', True)
    return dict(type=kind, name=name, description=desc, **kwargs)
def mod(value, operation='multiply_total', name='Tarot V2'):
    return dict(value=value, operation=operation, name=name)
def attr(name, desc, a, value, cond=None, op='multiply_total'):
    fields={'modifier':dict(mod(value,op,name),attribute='minecraft:generic.'+a)}
    if cond: fields['condition']=cond
    return p(name,desc,'origins:conditioned_attribute' if cond else 'origins:attribute',**fields)
def fx(name, seconds, level=1):
    return dict(effect='minecraft:'+name, duration=int(seconds*20), amplifier=level-1, show_particles=False)
def eff(name,seconds,level=1):
    return dict(type='origins:apply_effect',effect=fx(name,seconds,level))
def every(name,desc,interval,action,condition=None):
    d=dict(interval=int(interval*20),entity_action=action)
    if condition:d['condition']=condition
    return p(name,desc,'origins:action_over_time',**d)
def tick(name,desc,interval,what,duration,condition=None,level=1):
    return every(name,desc,interval,eff(what,duration,level),condition)
def onhit(name,desc,what,duration,cooldown):
    return p(name,desc,'origins:target_action_on_hit',entity_action=eff(what,duration),cooldown=int(cooldown*20),hud_render={'should_render':False})
def retaliate(name,desc,what,duration,cooldown):
    return p(name,desc,'origins:attacker_action_when_hit',entity_action=eff(what,duration),cooldown=int(cooldown*20),hud_render={'should_render':False})
def whenhit(name,desc,what,duration,cooldown):
    return p(name,desc,'origins:self_action_when_hit',entity_action=eff(what,duration),cooldown=int(cooldown*20),hud_render={'should_render':False})
def onkill(name,desc,action,cooldown):
    return p(name,desc,'origins:self_action_on_kill',entity_action=action,cooldown=int(cooldown*20),hud_render={'should_render':False})
def damage(name,desc,value,taken=False,condition=None,damage_condition=None,bientity_condition=None):
    d=dict(modifier=mod(value))
    if condition:d['condition']=condition
    if damage_condition:d['damage_condition']=damage_condition
    if bientity_condition:d['bientity_condition']=bientity_condition
    return p(name,desc,'origins:modify_damage_taken' if taken else 'origins:modify_damage_dealt',**d)
def ranged(name,desc,value):
    return p(name,desc,'origins:modify_projectile_damage',modifier=mod(value))
def xp(name,desc,value):
    return p(name,desc,'origins:modify_xp_gain',modifier=mod(value))
def exhaust(name,desc,value,condition=None):
    d=dict(modifier=mod(value))
    if condition:d['condition']=condition
    return p(name,desc,'origins:modify_exhaustion',**d)
def mine(name,desc,value,condition=None,block=None):
    d=dict(modifier=mod(value))
    if condition:d['condition']=condition
    if block:d['block_condition']=block
    return p(name,desc,'origins:modify_break_speed',**d)
def regen(name,desc,seconds,condition=None):
    return every(name,desc,seconds,{'type':'origins:heal','amount':1},condition)
def AND(*conds):return {'type':'origins:and','conditions':list(conds)}
def OR(*conds):return {'type':'origins:or','conditions':list(conds)}
def NOT(cond):return dict(cond,inverted=not cond.get('inverted',False))
def ITEM(name):return {'type':'origins:ingredient','ingredient':{'item':'minecraft:'+name}}
def HAND(name):return {'type':'origins:equipped_item','equipment_slot':'offhand','item_condition':ITEM(name)}
def SOURCE(name):return {'type':'origins:name','name':name}
def TARGET(name):return {'type':'origins:target_condition','condition':{'type':'origins:entity_type','entity_type':'minecraft:'+name}}
SUN={'type':'origins:exposed_to_sun'}
NIGHT={'type':'origins:daytime','inverted':True}
RAIN={'type':'origins:in_rain'}
WATER={'type':'origins:submerged_in','fluid':'minecraft:water'}
SNEAK={'type':'origins:sneaking'}
SPRINT={'type':'origins:sprinting'}
NETHER={'type':'origins:dimension','dimension':'minecraft:the_nether'}
BOOK=OR(HAND('book'),HAND('enchanted_book'))
MEAT={'type':'origins:ingredient','ingredient':{'tag':'origins:meat'}}
NEAR_LECTERN={'type':'origins:block_in_radius','radius':3,'block_condition':{'type':'origins:block','block':'minecraft:lectern'}}
DARK={'type':'origins:brightness','comparison':'<=','compare_to':7}

V2={
 'fool':[
  every('Spirit Vision','While sneaking, reveal nearby living beings for two seconds every eight seconds. The glow may be visible to others.',8,{'type':'origins:area_of_effect','radius':10,'bientity_action':{'type':'origins:target_action','action':eff('glowing',2)}},SNEAK),
  exhaust('Price: Spiritual Expenditure','Sprinting consumes 40% more hunger; careful preparation is essential.',0.40,SPRINT),
  p('Clown Reflex','Jump 15% higher.','origins:modify_jump',modifier=mod(0.15)),
  damage('Clown Balance','Take 35% less fall damage.',-0.35,True,damage_condition=SOURCE('fall')),
  whenhit('Danger Premonition','After being struck, gain Speed I for three seconds; 45-second cooldown.','speed',3,45),
 ],
 'magician':[
  attr('Wayfarer','Move 12% faster on land.','movement_speed',0.12),
  tick('Price: Moon Ravings','When exposed to the nighttime sky, periodically suffer Mining Fatigue I. Full-moon detection is not implemented.',5,'mining_fatigue',6,AND(NIGHT,{'type':'origins:exposed_to_sky'})),
  p('Traveler Jump','Jump 20% higher.','origins:modify_jump',modifier=mod(0.20)),
  damage('Safe Arrival','Take 70% less fall damage.',-0.70,True,damage_condition=SOURCE('fall')),
  whenhit('Door Instinct','An ambush gives brief Resistance I, once every 120 seconds.','resistance',4,120),
 ],
 'high_priestess':[
  xp('Reader Aptitude','Gain 35% more experience from orbs.',0.35),
  mine('Price: Unprepared Ritual','Mine 20% slower unless a book is held in your offhand.',-0.20,NOT(BOOK)),
  mine('Ritual Focus','Mine 25% faster with a book in your offhand.',0.25,BOOK),
  ranged('Calculated Arrows','Ranged attacks deal 15% more damage.',0.15),
  p('Low-Light Reading','Holding a book grants night vision.','origins:night_vision',strength=1.0,condition=BOOK),
 ],
 'empress':[
  onhit('Witch Venom','Melee strikes inflict Poison I for three seconds, at most once every 12 seconds.','poison',3,12),
  damage('Price: Exposed Reflection','Sunlight makes incoming projectiles 25% more dangerous.',0.25,True,condition=SUN,damage_condition={'type':'origins:projectile'}),
  p('Mirror Veil','Sneaking in dim light makes your body invisible. Armor may still show.','origins:invisibility',condition=AND(SNEAK,DARK)),
  attr('Witch Grace','Movement speed is 10% faster.','movement_speed',0.10),
  p('Venom Immunity','Immune to Poison.','origins:effect_immunity',effects=['minecraft:poison']),
 ],
 'emperor':[
  attr('Sovereign Plate','Gain three armor points.','armor',3,op='addition'),
  attr('Price: Weight of the Crown','Holding a shield in the offhand slows you by 25%.','movement_speed',-0.25,HAND('shield')),
  attr('Iron Edict','Resist 40% of knockback.','knockback_resistance',0.40,op='addition'),
  retaliate('Distorted Authority','Attacks on you slow the aggressor for two seconds every 14 seconds.','slowness',2,14),
  exhaust('Heavy Armor Tax','Sprinting consumes 45% more exhaustion.',0.45,SPRINT),
 ],
 'hierophant':[
  xp('Scripture and Study','Earn 40% more XP from orbs.',0.40),
  p('Price: Sacred Dietary Vow','Cannot eat meat or fish.','origins:prevent_item_use',item_condition=MEAT),
  tick('Consecrated Study','Gain Haste I pulses when within three blocks of a lectern.',5,'haste',6,NEAR_LECTERN),
  every('Quiet Benediction','Every 40 seconds, nearby living creatures receive Regeneration I, including enemies.',40,{'type':'origins:area_of_effect','radius':5,'bientity_action':{'type':'origins:target_action','action':eff('regeneration',4)}}),
  exhaust('Measured Routine','Exhaustion is 15% lower.',-0.15),
 ],
 'lovers':[
  every('Shared Pulse','Every 30 seconds nearby living creatures receive Regeneration I, including enemies.',30,{'type':'origins:area_of_effect','radius':6,'bientity_action':{'type':'origins:target_action','action':eff('regeneration',4)}}),
  p('Price: Sacrificial Healing','At seven hunger shanks or fewer, you stop regenerating naturally.','origins:disable_regen',condition={'type':'origins:food_level','comparison':'<=','compare_to':14}),
  regen('Mother Embrace','Recover half a heart every 30 seconds when well-fed.',30,{'type':'origins:food_level','comparison':'>=','compare_to':18}),
  attr('Compassionate Steps','Move 8% faster.','movement_speed',0.08),
 ],
 'chariot':[
  p('Flame Within','Immune to fire damage.','origins:fire_immunity'),
  tick('Price: Extinguished Fury','Underwater, suffer Weakness I.',3,'weakness',4,WATER),
  damage('Hunter Momentum','Sprinting melee hits deal 15% more damage.',0.15,condition=SPRINT),
  onkill('War Rush','Kills grant Speed I for eight seconds; cooldown 18 seconds.',eff('speed',8),18),
  tick('Drenched Powder','Underwater, suffer Mining Fatigue I.',3,'mining_fatigue',4,WATER),
 ],
 'strength':[
  damage('Giants Grip','Melee attacks deal 18% more damage.',0.18),
  p('Price: Heavy Swimmer','Swim 45% slower.','origins:modify_swim_speed',modifier=mod(-0.45)),
  attr('Steel Frame','Gain two armor points.','armor',2,op='addition'),
  attr('Immovable','Resist 55% of knockback.','knockback_resistance',0.55,op='addition'),
  mine('Quarry Hands','Mine stone 35% faster.',0.35,block={'type':'origins:block','block':'minecraft:stone'}),
  p('Price: Clumsy Bowhand','Cannot use bows or crossbows.','origins:prevent_item_use',item_condition=OR(ITEM('bow'),ITEM('crossbow'))),
 ],
 'hermit':[
  xp('Mystery Prying','Earn 35% more experience.',0.35),
  tick('Price: Forbidden Knowledge','At level 30 or above, suffer Mining Fatigue until you spend experience.',4,'mining_fatigue',5,{'type':'origins:xp_levels','comparison':'>=','compare_to':30}),
  ranged('Astral Calculation','Deal 20% more projectile damage.',0.20),
  p('Occult Night Sight','Permanent night vision.','origins:night_vision',strength=1.0),
  mine('Prepared Investigator','Holding an enchanted book in your offhand boosts mining speed 20%.',0.20,HAND('enchanted_book')),
 ],
 'wheel_of_fortune':[
  attr('Fortunate Soul','Luck increases by one where vanilla uses it.','luck',1,op='addition'),
  every('Price: Fate Debt','Every 90 seconds a random fate roll yields one of three boons or three punishments.',90,{'type':'origins:choice','actions':[{'weight':1,'element':eff(x,12)} for x in ('speed','haste','absorption','hunger','slowness','mining_fatigue')]}),
  xp('Fortunes Bounty','Gain 10% more XP.',0.10),
  damage('Surprising Protection','Take 10% less damage from ordinary attacks.',-0.10,True),
 ],
 'justice':[
  retaliate('Emotional Recoil','Attackers receive Weakness I for four seconds; cooldown 18 seconds.','weakness',4,18),
  damage('Price: Compassionate Restraint','Deal 70% less damage to villagers.',-0.70,bientity_condition=TARGET('villager')),
  damage('Patient Observation','When sneaking, incoming damage is reduced by 12%.',-0.12,True,condition=SNEAK),
  every('Therapists Presence','Nearby entities receive Regeneration I every 45 seconds, including foes.',45,{'type':'origins:area_of_effect','radius':5,'bientity_action':{'type':'origins:target_action','action':eff('regeneration',4)}}),
  tick('Clear Head','Sneaking refreshes brief Night Vision.',3,'night_vision',4,SNEAK),
 ],
 'hanged_man':[
  tick('Sea Lords Lungs','Underwater, continuously refresh Water Breathing.',3,'water_breathing',4,WATER),
  exhaust('Price: Drought of the Sailor','Exhaustion doubles in the Nether.',1.0,NETHER),
  p('Sailors Speed','Swim 35% faster.','origins:modify_swim_speed',modifier=mod(0.35)),
  attr('Storm Companion','In rain, move 20% faster.','movement_speed',0.20,RAIN),
  ranged('Sea Lords Trident','Projectiles deal 20% more damage.',0.20),
 ],
 'death':[
  onkill('Soul Harvest','Recover one heart when you defeat an entity; cooldown 10 seconds.',{'type':'origins:heal','amount':2},10),
  p('Price: Severed Vitality','Natural food regeneration is disabled; seek healing from kills, potions or allies.','origins:disable_regen'),
  damage('Grave Affinity','Take 20% less damage from undead enemies.',-0.20,True,bientity_condition={'type':'origins:actor_condition','condition':{'type':'origins:entity_group','group':'undead'}}),
  p('Grave Sight','Permanent night vision.','origins:night_vision',strength=1.0),
  onhit('Reapers Chill','Successful hits slow enemies for three seconds; cooldown 10 seconds.','slowness',3,10),
 ],
 'temperance':[
  p('Wraith Veil','Crouching in dim lighting gives invisibility. Held items and armor may remain visible.','origins:invisibility',condition=AND(SNEAK,DARK)),
  p('Price: Unstable Manifestation','High-defense chestplates are forbidden.','origins:restrict_armor',chest={'type':'origins:armor_value','comparison':'>','compare_to':5}),
  damage('Ethereal Landing','Take 60% less fall damage.',-0.60,True,damage_condition=SOURCE('fall')),
  attr('Silent Crossing','Move 20% faster while sneaking.','movement_speed',0.20,SNEAK),
  p('Wraith Resistance','Immune to Slowness.','origins:effect_immunity',effects=['minecraft:slowness']),
 ],
 'devil':[
  p('Hellborn','Immune to fire.','origins:fire_immunity'),
  p('Price: Rejected Grace','Cannot eat golden apples or enchanted golden apples.','origins:prevent_item_use',item_condition=OR(ITEM('golden_apple'),ITEM('enchanted_golden_apple'))),
  onhit('Corrupting Claws','Hits inflict Wither I for two seconds, cooldown 16 seconds.','wither',2,16),
  attr('Desperate Malice','When below 40% health, attack damage rises 15%.','attack_damage',0.15,{'type':'origins:relative_health','comparison':'<=','compare_to':0.4}),
 ],
 'tower':[
  damage('Ruin Proof','Take 60% less explosion damage.',-0.60,True,damage_condition=SOURCE('explosion')),
  damage('Price: Falling Tower','Fall damage is 75% higher.',0.75,True,damage_condition=SOURCE('fall')),
  mine('Cracked Foundations','Mine stone 30% faster.',0.30,block={'type':'origins:block','block':'minecraft:stone'}),
  onhit('Unstable Strike','Hits slow the enemy for two seconds, cooldown 13 seconds.','slowness',2,13),
 ],
 'star':[
  p('Sleepless Sight','Permanent night vision.','origins:night_vision',strength=1.0),
  p('Price: True Sleeplessness','Cannot sleep, but beds can still set your spawn.','origins:prevent_sleep',message='A Sleepless never rests under the Evernight.',set_spawn_point=True),
  attr('Nightwatch Stride','Move 15% faster at night.','movement_speed',0.15,NIGHT),
  p('Undisturbed Mind','Immune to Blindness.','origins:effect_immunity',effects=['minecraft:blindness']),
 ],
 'moon':[
  p('Sanguine Sight','Permanent night vision.','origins:night_vision',strength=1.0),
  p('Price: Blood Diet','Cannot eat non-meat foods; all items in Origins meat tag are allowed.','origins:prevent_item_use',item_condition=AND({'type':'origins:food'},NOT(MEAT))),
  regen('Bloods Renewal','At night, heal half a heart every 30 seconds.',30,NIGHT),
  attr('Nocturnal Blood','Move 15% faster at night.','movement_speed',0.15,NIGHT),
 ],
 'sun':[
  damage('Unshadowed','Deal 40% more damage to undead.',0.40,bientity_condition={'type':'origins:target_condition','condition':{'type':'origins:entity_group','group':'undead'}}),
  p('Price: Beacon of Faith','Always Glow, revealing yourself to other players.','origins:self_glow',use_teams=False,red=1.0,green=0.87,blue=0.23),
  p('Inner Radiance','Permanent night vision, even underground.','origins:night_vision',strength=1.0),
  p('Sun Fires','Fire cannot harm you.','origins:fire_immunity'),
  p('Purification','Immune to Poison.','origins:effect_immunity',effects=['minecraft:poison']),
 ],
 'judgement':[
  attr('Law Weight','Gain two armor points.','armor',2,op='addition'),
  p('Price: No Unlawful Escape','Cannot use ender pearls or chorus fruit.','origins:prevent_item_use',item_condition=OR(ITEM('ender_pearl'),ITEM('chorus_fruit'))),
  attr('Hold the Line','Resist 45% knockback.','knockback_resistance',0.45,op='addition'),
  retaliate('Retaliatory Sentence','Attackers are slowed for three seconds; cooldown 14 seconds.','slowness',3,14),
  damage('Calm Stance','Take 12% less damage while not sprinting.',-0.12,True,condition=NOT(SPRINT)),
 ],
 'world':[
  ranged('Cold Precision','Ranged projectiles deal 25% more damage.',0.25),
  p('Price: Infamous Hunter','Cannot interact with villagers to trade.','origins:prevent_entity_use',bientity_condition=TARGET('villager')),
  onhit('Marked Prey','Hits mark targets with Glowing for six seconds, cooldown 10 seconds.','glowing',6,10),
  onkill('Hunters Tempo','Kills grant Speed I for eight seconds, cooldown 18 seconds.',eff('speed',8),18),
 ],
}

def apply_v2(original):
    assert set(original)==set(V2),'V2 rules must cover every card'
    for slug,powers in V2.items():
        assert len(powers)>=4 and any(p['name'].startswith('Price:') for p in powers), slug
    return {slug:original[slug][:2]+V2[slug] for slug in original}
