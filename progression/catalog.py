"""Playable Major Arcana, acting tests, ascension offerings and curated resonance.

Card ID is a Tarot alias, NOT necessarily the actual Beyonder pathway name.
"""
from __future__ import annotations

ACT_MARKS = {9: 1, 8: 2, 7: 2, 6: 3, 5: 3, 4: 4, 3: 4, 2: 5, 1: 6}
RITUALS = {
    9: {'amethyst_shard': 6, 'lapis_lazuli': 8},
    8: {'copper_ingot': 12, 'glow_ink_sac': 2},
    7: {'gold_ingot': 8, 'ender_pearl': 2},
    6: {'blaze_powder': 6, 'ghast_tear': 1},
    5: {'diamond': 4, 'amethyst_shard': 16},
    4: {'netherite_scrap': 1, 'ender_eye': 2},
    3: {'ancient_debris': 2, 'phantom_membrane': 4},
    2: {'nether_star': 1, 'ender_pearl': 8},
    1: {'nether_star': 2, 'enchanted_golden_apple': 1},
}
SECOND_OFFERING = {'amethyst_shard': 16, 'ender_pearl': 4, 'ghast_tear': 1}

# slugs, titles, pathway labels, class specialty, inventory acting item, second acting event,
# echo specialty, and whether current V2 has built-in Elytra gliding.
ROWS = [
 ('fool','The Fool','Klein / Seer–Clown','scout','compass','kill:spider','scout',True),
 ('magician','The Magician','Fors / Door','travel','ender_pearl','dimension:the_nether','travel',True),
 ('high_priestess','The High Priestess','Original / White Tower–Hermit','scholar','book','trade','scholar',True),
 ('empress','The Empress','Franca / Demoness','stealth','spider_eye','kill:spider','stealth',True),
 ('emperor','The Emperor','Original / Black Emperor','tank','shield','kill:pillager','tank',False),
 ('hierophant','The Hierophant','Original / ritual scholar','scholar','lectern','trade','scholar',False),
 ('lovers','The Lovers','Original / Mother–Visionary','support','wheat','breed','support',True),
 ('chariot','The Chariot','Lumian / Red Priest','combat','flint_and_steel','kill:blaze','combat',True),
 ('strength','Strength','Original / Twilight Giant','combat','iron_pickaxe','kill:zombie','tank',False),
 ('hermit','The Hermit','Cattleya / Hermit','scholar','lapis_lazuli','trade','scholar',True),
 ('wheel_of_fortune','Wheel of Fortune','Original / Monster','luck','rabbit_foot','kill:skeleton','luck',True),
 ('justice','Justice','Audrey / Visionary','support','honey_bottle','trade','support',True),
 ('hanged_man','The Hanged Man','Alger / Tyrant','sea','kelp','kill:drowned','sea',True),
 ('death','Death','Original / Death','night','bone','kill:skeleton','night',True),
 ('temperance','Temperance','Sharron / Chained–Wraith','stealth','glass_bottle','kill:spider','stealth',True),
 ('devil','The Devil','Original / Abyss','combat','blaze_powder','kill:ghast','combat',True),
 ('tower','The Tower','Original / catastrophe','miner','tnt','kill:creeper','miner',True),
 ('star','The Star','Leonard / Darkness–Sleepless','night','clock','kill:phantom','night',True),
 ('moon','The Moon','Emlyn / Moon–Sanguine','night','redstone','consume:cooked_beef','night',True),
 ('sun','The Sun','Derrick / Sun','combat','torch','kill:zombie','support',True),
 ('judgement','Judgement','Xio / Justiciar','tank','iron_bars','kill:pillager','tank',False),
 ('world','The World','Gehrman Sparrow / Fool','scout','crossbow','kill:pillager','scout',True),
]
CARDS = [dict(id=i, slug=slug, name=name, lore=lore, focus=focus, acting_item=item,
              acting_event=event, echo=echo, glider=glider)
         for i,(slug,name,lore,focus,item,event,echo,glider) in enumerate(ROWS,1)]
ID_TO_SLUG = {c['id']:c['slug'] for c in CARDS}
SLUG_TO_ID = {c['slug']:c['id'] for c in CARDS}

# LORE affinity (not a claim that arbitrary pathway switches are canonical).
PAIRS = [
 ('fool','magician','hidden_door'),
 ('chariot','empress','calamity'),
 ('star','death','midnight_requiem'),
 ('emperor','judgement','absolute_decree'),
 ('sun','moon','eclipse'),
 ('high_priestess','hermit','forbidden_library'),
 ('lovers','justice','gentle_heart'),
 ('magician','hanged_man','storm_gate'),
 ('fool','world','one_soul'),
 ('strength','tower','ruinborn'),
 ('temperance','devil','shadow_pact'),
 ('fool','wheel_of_fortune','fated_vision'),
]
assert len(CARDS)==22 and len(SLUG_TO_ID)==22
assert len(RITUALS)==len(ACT_MARKS)==9
