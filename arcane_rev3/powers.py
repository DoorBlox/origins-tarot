"""Source-traced, non-placeholder Origins powers for the standalone Rev3 builder.

Every compiled ability has its own concrete JSON effect. Unsupported [S] abilities
remain catalog entries, *not* fake no-op powers. The catalog is the Rev2 handbook.
"""
import json
import re
import unicodedata
from pathlib import Path


def norm(name):
    name = unicodedata.normalize("NFKD", name).replace("’", "'")
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def mod(value, operation="multiply_total"):
    return {"name": "Arcane V2 Rev3", "value": value, "operation": operation}


def power(name, desc, kind, **fields):
    return {"type": kind, "name": name, "description": desc, **fields}


def attr(name, value, attribute, desc=""):
    return power(name, desc or name, "origins:attribute",
                 modifier={**mod(value, "addition" if attribute in ("armor", "knockback_resistance", "luck") else "multiply_total"),
                           "attribute": "minecraft:generic." + attribute})


def xp(name, value):
    return power(name, name, "origins:modify_xp_gain", modifier=mod(value))


def velocity(name, value):
    return attr(name, value, "movement_speed")


def phys(name, value):
    return attr(name, value, "attack_damage")


def armour(name, value):
    return attr(name, value, "armor")


def knock(name, value):
    return attr(name, value, "knockback_resistance")


def projectile(name, value):
    return power(name, name, "origins:modify_projectile_damage", modifier=mod(value))


def apply(effect, duration, amplifier=0):
    return {"type": "origins:apply_effect",
            "effect": {"effect": "minecraft:" + effect, "duration": duration,
                       "amplifier": amplifier, "show_particles": False}}


def compound(name, **subpowers):
    return power(name, name, "origins:multiple", **subpowers)


def current_catalog(root):
    p = root / "arcane" / "catalog.json"
    catalog = json.loads(p.read_text(encoding="utf-8"))
    total = sum(len(level["abilities"]) for family in ("individual", "resonance")
                for card in catalog[family] for level in card["sequences"])
    if len(catalog["individual"]) != 22 or len(catalog["resonance"]) != 11 or total != 434:
        raise ValueError("Rev2 catalog incomplete: expected 22 + 11, 434 named abilities")
    return catalog


def compile_powers(root):
    """Returns compiled powers, list of all statuses, and per-kit grant identifiers."""
    catalog = current_catalog(root)
    entries = {}
    for family in ("individual", "resonance"):
        for card in catalog[family]:
            for level in card["sequences"]:
                for entry in level["abilities"]:
                    key = (card["slug"], level["sequence"], norm(entry["name"]))
                    if key in entries:
                        raise ValueError("duplicate ability " + str(key))
                    entries[key] = (card, entry, family)
    compiled = {}
    accurate = {}
    notes = {}
    def add(slug, seq, name, value, accuracy="full", missing=""):
        key = (slug, seq, norm(name))
        if key not in entries:
            raise ValueError("ability not in authoritative handbook: " + str(key))
        if accuracy not in ("full", "partial") or (accuracy == "partial" and not missing):
            raise ValueError("partial implementation requires disclosed missing details")
        card, entry, family = entries[key]
        if family not in ("individual","resonance"):
            raise ValueError("unknown catalog family")
        if not value.get("type", "").startswith("origins:") or value["type"] == "origins:simple":
            raise ValueError("invalid or fake power")
        ident = "tarot:" + slug + "/" + str(seq) + "_" + entry["slug"]
        if ident in compiled:
            raise ValueError("duplicate compiled power")
        value = dict(value)
        # Rev3 targeting: negative retaliation may only hit hostile mobs or
        # enemy players. Origins 1.4.1 cannot compare arbitrary scoreboard
        # teams inside attacker_action_when_hit; apply a fail-closed hostile
        # mob filter instead of accidentally debuffing friendly players.
        # Sun's Solar Flare has its own stricter undead-only condition.
        if value["type"] == "origins:attacker_action_when_hit" and not (
            slug == "sun" and seq == 7 and norm(name) == norm("Solar Flare")
        ):
            if "damage_condition" in value:
                raise ValueError("retaliation already has damage filter: " + ident)
            value["damage_condition"] = {
                "type": "origins:attacker",
                "entity_condition": {"type": "origins:in_tag", "tag": "tarot:hostile"},
            }
            accuracy = "partial"
            missing = (missing + "; " if missing else "") + (
                "enemy players are not debuffed until a reliable different-team "
                "target filter is implemented in the permitted datapack runtime"
            )
        value["name"] = name
        value["description"] = value.get("description", "") or entry["description"][:180]
        compiled[ident] = value
        accurate[key] = accuracy
        if missing:
            notes[key] = missing
    # Review and reuse real, version-scoped native implementations from the
    # archived PR7. They do not carry server scripts or KubeJS.
    templates = json.loads((root / "arcane" / "templates.json").read_text(encoding="utf-8"))
    for template in templates:
        add(template["slug"], template["sequence"], template["name"],
            template["power"], template["accuracy"], template.get("missing", ""))
    # Exact or conservative datapack implementations; no arbitrary enemy scans.
    # Fool Sequence 9 strictly follows the 2026 Rev2/Rev3 specifications.
    add("fool", 9, "Spirit Vision", power("Spirit Vision",
        "Sneak + secondary key: Glowing I, 10 blocks, 40 ticks; 100t cooldown.",
        "origins:active_self", cooldown=100, hud_render={"should_render":True},
        key={"key":"key.origins.secondary_active"}, condition={"type":"origins:sneaking"},
        entity_action={"type":"origins:execute_command",
             # Vanilla distance selectors are spherical in 1.18.2.
             # The fixed power action is server-trusted, not a /tarot alias.
             "permission_level":2,
             "command":"execute at @s run effect give @e[distance=..10] minecraft:glowing 2 0 true"}))
    add("fool", 9, "Clown's Mischief", power("Clown's Mischief",
        "20% chance to blind attacker for 20 ticks; 100t cooldown.",
        "origins:attacker_action_when_hit", cooldown=100,
        entity_action={"type":"origins:chance","chance":0.2,"action":apply("blindness",20)}))
    add("high_priestess", 9, "Reader's Aptitude", xp("Reader's Aptitude",0.35))
    add("high_priestess", 9, "Scripted Insight", projectile("Scripted Insight",0.20),
        "partial", "Must only apply while not sprinting; pending condition")
    add("emperor", 9, "Sovereign's Plate", compound("Sovereign's Plate",
        armor={"type":"origins:attribute","modifier":{**mod(3,"addition"),"attribute":"minecraft:generic.armor"}},
        knockback={"type":"origins:attribute","modifier":{**mod(0.4,"addition"),"attribute":"minecraft:generic.knockback_resistance"}}))
    add("hierophant", 9, "Scripture and Study", xp("Scripture and Study",0.40))
    add("strength", 9, "Steel Frame", armour("Steel Frame",2))
    add("hermit", 9, "Mystery Prying", xp("Mystery Prying",0.35),
        "partial", "Cave-specific XP bonus not yet gated")
    add("wheel_of_fortune", 9, "Gentle Fortune", compound("Gentle Fortune",
        experience={"type":"origins:modify_xp_gain","modifier":mod(0.10)},
        luck={"type":"origins:attribute","modifier":{**mod(1,"addition"),"attribute":"minecraft:generic.luck"}}))
    add("justice", 9, "Emotional Recoil", power("Emotional Recoil","Attacker gets Weakness I for 80 ticks (360t CD).",
        "origins:attacker_action_when_hit", entity_action=apply("weakness",80),cooldown=360))
    add("death",9,"Soul Harvest",power("Soul Harvest","Heal 2 HP on kill (200t CD).",
        "origins:self_action_on_kill",entity_action={"type":"origins:heal","amount":2},cooldown=200),
        "partial","Kill target must be hostile mob or enemy player")
    add("devil",9,"Hellborn",power("Hellborn","Complete fire immunity.","origins:fire_immunity"))
    add("judgement",9,"Law's Weight",compound("Law's Weight",
        armor={"type":"origins:attribute","modifier":{**mod(2,"addition"),"attribute":"minecraft:generic.armor"}},
        knockback={"type":"origins:attribute","modifier":{**mod(0.45,"addition"),"attribute":"minecraft:generic.knockback_resistance"}}))
    add("world",9,"Cold Precision",projectile("Cold Precision",0.25))
    add("star",9,"Sleepless",power("Sleepless","Night vision without sleeping.","origins:night_vision"),
        "partial","Blindness and Darkness duration reductions not supported in this passive")
    add("sun",9,"Beacon of Faith",power("Beacon of Faith",
        "Permanent Glowing while active.", "origins:action_over_time",
        interval=40, entity_action=apply("glowing",90)))
    add("magician",9,"Wayfarer's Instinct",power("Wayfarer's Instinct",
        "Jump 20% higher, except while submerged.", "origins:modify_jump",
        modifier=mod(0.20), condition={"type":"origins:submerged","inverted":True}))
    add("chariot",9,"War Rush",power("War Rush","Gain Speed I 160t on kill; 360t CD.",
        "origins:self_action_on_kill",entity_action=apply("speed",160),cooldown=360))
    add("moon",9,"Blood's Renewal",power("Blood's Renewal",
        "At night heal 1 HP once per 600 ticks.", "origins:action_over_time",
        interval=600,condition={"type":"origins:daytime","inverted":True},
        entity_action={"type":"origins:heal","amount":1}))
    add("sun",9,"Inner Radiance",compound("Inner Radiance",
        night={"type":"origins:night_vision"}, fire={"type":"origins:fire_immunity"}))
    add("devil",9,"Desperate Malice",power("Desperate Malice",
        "+18% attack damage below 40% health.","origins:conditioned_attribute",
        modifier={**mod(0.18),"attribute":"minecraft:generic.attack_damage"},
        condition={"type":"origins:relative_health","comparison":"<","compare_to":0.4},
        tick_rate=20))
    add("empress",9,"Witch's Grace",compound("Witch's Grace",
        speed={"type":"origins:attribute","modifier":{**mod(0.10),"attribute":"minecraft:generic.movement_speed"}},
        poison={"type":"origins:effect_immunity","effects":["minecraft:poison"]}))
    add("hanged_man",9,"Graze the Soul",power("Graze the Soul",
        "On kill heal 2 HP and gain Resistance I for 60 ticks; CD 120t.",
        "origins:self_action_on_kill", cooldown=120,
        entity_action={"type":"origins:and","actions":[{"type":"origins:heal","amount":2},apply("resistance",60)]}),
        "partial","Only hostile mob or enemy player kills must count")

    # Additional native 1.4.1 powers. These are real mechanics, with any
    # unsupplied sub-effects explicitly classified as partial.
    add("magician",9,"Traveler's Body",compound("Traveler's Body",
        pace={"type":"origins:attribute","modifier":{**mod(0.12),"attribute":"minecraft:generic.movement_speed"}},
        fall={"type":"origins:modify_damage_taken",
              "damage_condition":{"type":"origins:name","name":"fall"},
              "modifier":mod(-0.7)}))
    book={"type":"origins:equipped_item","equipment_slot":"offhand",
          "item_condition":{"type":"origins:ingredient","ingredient":{"tag":"tarot:books"}}}
    add("high_priestess",9,"Dependent on Rituals",power("Dependent on Rituals",
        "Without an offhand book, mining is 20% slower.","origins:modify_break_speed",
        modifier=mod(-0.20),condition={**book,"inverted":True}))
    add("high_priestess",9,"Ritual Focus",power("Ritual Focus",
        "Offhand book grants 25% faster mining.","origins:modify_break_speed",
        modifier=mod(0.25),condition=book),"partial","Low-light vision not yet included")
    add("emperor",9,"Distorted Authority",power("Distorted Authority",
        "Attackers receive Slowness I for 40 ticks; 280t cooldown.",
        "origins:attacker_action_when_hit",entity_action=apply("slowness",40),cooldown=280))
    shield={"type":"origins:or","conditions":[
        {"type":"origins:equipped_item","equipment_slot":slot,
         "item_condition":{"type":"origins:ingredient","ingredient":{"item":"minecraft:shield"}}}
        for slot in ("mainhand","offhand")]}
    add("emperor",9,"Imperial Presence",power("Imperial Presence",
        "Shield in hand reduces incoming damage by 10%.",
        "origins:modify_damage_taken",condition=shield,modifier=mod(-0.10)))
    add("emperor",9,"Weight of the Crown",compound("Weight of the Crown",
        pace={"type":"origins:conditioned_attribute",
              "condition":shield,"tick_rate":20,
              "modifier":{**mod(-0.25),"attribute":"minecraft:generic.movement_speed"}},
        fatigue={"type":"origins:modify_exhaustion",
                 "condition":{"type":"origins:sprinting"},
                 "modifier":mod(0.50)}),
        "partial","Sprint exhaustion should apply only while armored")
    add("hierophant",9,"Sacred Dietary Vow",power("Sacred Dietary Vow",
        "Cannot consume meat or fish from the tarot:meat tag.",
        "origins:prevent_item_use",
        item_condition={"type":"origins:ingredient","ingredient":{"tag":"tarot:meat"}}))
    add("chariot",9,"Hunter's Momentum",power("Hunter's Momentum",
        "While sprinting, melee attacks deal 15% more damage.",
        "origins:modify_damage_dealt",modifier=mod(0.15),
        condition={"type":"origins:sprinting"}))
    add("chariot",9,"Pyromaniac",compound("Pyromaniac",
        fire={"type":"origins:fire_immunity"},
        power={"type":"origins:action_over_time","interval":20,
               "condition":{"type":"origins:on_fire"},
               "entity_action":apply("strength",40)}))
    add("chariot",9,"Extinguished Fury",power("Extinguished Fury",
        "Rain or submersion applies Weakness and Mining Fatigue.",
        "origins:action_over_time",interval=20,
        condition={"type":"origins:or","conditions":[
            {"type":"origins:in_rain"},{"type":"origins:submerged"}]},
        entity_action={"type":"origins:and","actions":[apply("weakness",50),apply("mining_fatigue",50)]}))
    add("chariot",6,"Plot",power("Plot","20% chance per kill to gain one XP level.",
        "origins:self_action_on_kill",
        entity_action={"type":"origins:chance","chance":0.20,
                       "action":{"type":"origins:execute_command","command":"experience add @s 1 levels"}}))
    add("strength",9,"Giant's Grip",compound("Giant's Grip",
        strength={"type":"origins:attribute","modifier":{**mod(0.18),"attribute":"minecraft:generic.attack_damage"}},
        knockback={"type":"origins:attribute","modifier":{**mod(0.55,"addition"),"attribute":"minecraft:generic.knockback_resistance"}}))
    add("strength",9,"Quarry Hands",power("Quarry Hands",
        "Natural stone breaks 35% faster.","origins:modify_break_speed",
        block_condition={"type":"origins:in_tag","tag":"tarot:natural_stone"},
        modifier=mod(0.35)))
    add("strength",9,"The Giant Sinks",compound("The Giant Sinks",
        swim={"type":"origins:modify_swim_speed","modifier":mod(-0.45)},
        weapons={"type":"origins:prevent_item_use",
                 "item_condition":{"type":"origins:ingredient",
                                   "ingredient":{"items":["minecraft:bow","minecraft:crossbow"]}}}))
    add("hermit",9,"Astral Calculation",compound("Astral Calculation",
        projectile={"type":"origins:modify_projectile_damage","modifier":mod(0.20)},
        vision={"type":"origins:night_vision",
                "condition":{"type":"origins:brightness","comparison":"<=","compare_to":0.25}}))
    add("hermit",9,"Prepared Investigator",power("Prepared Investigator",
        "Mine 20% faster with book or clock offhand.",
        "origins:modify_break_speed",modifier=mod(0.20),
        condition={"type":"origins:or","conditions":[
            book,{"type":"origins:equipped_item","equipment_slot":"offhand",
                  "item_condition":{"type":"origins:ingredient","ingredient":{"item":"minecraft:clock"}}}]}))
    add("wheel_of_fortune",9,"Fate Intervenes",power("Fate Intervenes",
        "15% chance to halve incoming damage.","origins:modify_damage_taken",
        condition={"type":"origins:chance","chance":0.15},modifier=mod(-0.5)))
    add("wheel_of_fortune",6,"Calamity",power("Calamity",
        "10% chance to inflict Weakness I for 40 ticks on attacker.","origins:attacker_action_when_hit",
        cooldown=1,entity_action={"type":"origins:chance","chance":0.10,
                                  "action":apply("weakness",40)}))
    add("death",9,"Severed Vitality",power("Severed Vitality",
        "Natural regeneration is disabled.","origins:disable_regen"))
    add("temperance",9,"Wraith's Veil",power("Wraith's Veil",
        "Sneaking grants invisibility, even without darkness gate.","origins:invisibility",
        condition={"type":"origins:sneaking"}),"partial","Light level must be <= 7")
    add("temperance",9,"Ethereal Landing",compound("Ethereal Landing",
        fall={"type":"origins:modify_damage_taken",
              "damage_condition":{"type":"origins:name","name":"fall"},"modifier":mod(-0.6)},
        slow={"type":"origins:effect_immunity","effects":["minecraft:slowness"]}))
    add("temperance",9,"Unstable Manifestation",power("Unstable Manifestation",
        "Cannot wear iron, diamond, or netherite chestplates.",
        "origins:restrict_armor",chest={"type":"origins:ingredient",
            "ingredient":{"items":["minecraft:iron_chestplate","minecraft:diamond_chestplate","minecraft:netherite_chestplate"]}}))
    add("temperance",6,"Rot",power("Rot",
        "Melee hits apply Hunger I for 40 ticks; cooldown 300t.",
        "origins:target_action_on_hit",entity_action=apply("hunger",40),cooldown=300),
        "partial","Hitting a teammate or passive must not apply this negative effect")
    add("devil",9,"Infernal Vitality",power("Infernal Vitality",
        "Heal one HP every 80 ticks while burning.","origins:action_over_time",
        interval=80,condition={"type":"origins:on_fire"},
        entity_action={"type":"origins:heal","amount":1}))
    add("devil",8,"Fallen Grace",power("Fallen Grace",
        "10% chance when hit to gain Strength I for 40 ticks.",
        "origins:self_action_when_hit",cooldown=1,
        entity_action={"type":"origins:chance","chance":0.10,
                       "action":apply("strength",40)}))
    add("devil",1,"Infernal Vitality II",power("Infernal Vitality II",
        "Heal one HP per 60 ticks while on fire.","origins:action_over_time",
        interval=60,condition={"type":"origins:on_fire"},
        entity_action={"type":"origins:heal","amount":1}))
    add("tower",9,"Cracked Foundations",power("Cracked Foundations",
        "Mine natural stone 30% faster.","origins:modify_break_speed",
        block_condition={"type":"origins:in_tag","tag":"tarot:natural_stone"},
        modifier=mod(0.30)))
    add("tower",9,"Ruin-Proof",power("Ruin-Proof",
        "60% less explosion damage.","origins:modify_damage_taken",
        damage_condition={"type":"origins:name","name":"explosion"},
        modifier=mod(-0.60)),"partial","Other explosion damage-source variants not included")
    add("tower",9,"Falling Tower",compound("Falling Tower",
        falling={"type":"origins:modify_damage_taken",
                 "damage_condition":{"type":"origins:name","name":"fall"},
                 "modifier":mod(0.75)},
        knockback={"type":"origins:attribute",
                   "modifier":{**mod(-0.20,"addition"),"attribute":"minecraft:generic.knockback_resistance"}}),
        "partial","Knockback taken cannot be modeled exactly by negative resistance")
    add("star",9,"Evernight's Patience",power("Evernight's Patience",
        "Night reduces exhaustion by 20%.","origins:modify_exhaustion",
        condition={"type":"origins:daytime","inverted":True},modifier=mod(-0.20)))
    add("star",9,"True Sleeplessness",power("True Sleeplessness",
        "Cannot sleep, but beds still set spawn point.","origins:prevent_sleep",
        message="Your vigilance forbids sleep.",set_spawn_point=True))
    add("star",9,"Nightwatch",compound("Nightwatch",
        movement={"type":"origins:conditioned_attribute","tick_rate":20,
                  "condition":{"type":"origins:daytime","inverted":True},
                  "modifier":{**mod(0.15),"attribute":"minecraft:generic.movement_speed"}},
        combat={"type":"origins:modify_damage_dealt",
                "condition":{"type":"origins:daytime","inverted":True},
                "target_condition":{"type":"origins:in_tag","tag":"tarot:undead"},
                "modifier":mod(0.15)}))
    add("moon",9,"Sanguine Sight",compound("Sanguine Sight",
        vision={"type":"origins:night_vision"},
        movement={"type":"origins:conditioned_attribute","tick_rate":20,
                  "condition":{"type":"origins:daytime","inverted":True},
                  "modifier":{**mod(0.15),"attribute":"minecraft:generic.movement_speed"}}))
    add("moon",7,"Blood Drain",power("Blood Drain",
        "Melee hits heal 1 HP, 100t cooldown.",
        "origins:self_action_on_hit",cooldown=100,
        entity_action={"type":"origins:heal","amount":1}),
        "partial","Target must be hostile mob or enemy player")
    add("sun",9,"Unshadowed",power("Unshadowed",
        "Melee damage to undead increased by 40%.","origins:modify_damage_dealt",
        target_condition={"type":"origins:in_tag","tag":"tarot:undead"},modifier=mod(0.40)),
        "partial","Projectile and other damage types do not benefit")
    add("judgement",9,"Retaliatory Sentence",power("Retaliatory Sentence",
        "Attackers suffer Slowness I for 60 ticks; 280t CD.",
        "origins:attacker_action_when_hit",entity_action=apply("slowness",60),cooldown=280))
    add("judgement",9,"No Unlawful Escape",power("No Unlawful Escape",
        "Ender pearls and chorus fruits cannot be used.","origins:prevent_item_use",
        item_condition={"type":"origins:ingredient",
                        "ingredient":{"items":["minecraft:ender_pearl","minecraft:chorus_fruit"]}}))
    add("world",9,"Hunter's Tempo",power("Hunter's Tempo",
        "Gain Speed I for 160t after kill; 360t CD.","origins:self_action_on_kill",
        entity_action=apply("speed",160),cooldown=360))
    add("world",9,"Terrifying Reputation",power("Terrifying Reputation",
        "Villagers refuse right-click interactions.","origins:prevent_entity_use",
        bientity_condition={"type":"origins:target_condition",
                            "condition":{"type":"origins:entity_type","entity_type":"minecraft:villager"}}),
        "partial","Wandering trader and alternate trade UIs may remain accessible")


    # Additional Rev2 powers implemented or explicitly marked partial when
    # pure datapack rules cannot enforce the source's PvP/team restrictions.
    hostile={"type":"origins:in_tag","tag":"tarot:hostile"}
    add("high_priestess",8,"Deduction",power("Deduction",
        "20% chance after any kill to earn one experience level, capped at level 30.",
        "origins:self_action_on_kill",entity_action={
            "type":"origins:chance","chance":0.2,
            "action":{"type":"origins:execute_command",
                      "command":"execute if entity @s[level=..29] run experience add @s 1 levels"}}))
    add("empress",9,"Exposed Reflection",power("Exposed Reflection",
        "Sunlight makes incoming projectile damage 25% stronger.",
        "origins:modify_damage_taken",modifier=mod(0.25),
        condition={"type":"origins:exposed_to_sun"},
        damage_condition={"type":"origins:projectile"}))
    add("empress",9,"Reflected Beauty",power("Reflected Beauty",
        "Bright surroundings trigger Nausea I on the attacker for 40 ticks.",
        "origins:attacker_action_when_hit",cooldown=400,
        condition={"type":"origins:brightness","comparison":">=","compare_to":0.8},
        entity_action=apply("nausea",40)),
        "partial","Brightness >= 0.8 approximates light level 12 and lacks dynamic team protection")
    add("empress",9,"Witch's Venom",power("Witch's Venom",
        "Poison I for 60 ticks when hitting a hostile mob; 240t cooldown.",
        "origins:target_action_on_hit",cooldown=240,
        target_condition=hostile,entity_action=apply("poison",60)),
        "partial","Enemy players must also be poisoned; player targeting is gated until dynamic team checks are available")
    add("empress",7,"Black Fire",power("Black Fire",
        "10% chance to ignite a hostile mob for 20 ticks on hit.",
        "origins:target_action_on_hit",cooldown=1,
        target_condition=hostile,entity_action={"type":"origins:chance",
                    "chance":0.10,"action":{"type":"origins:set_on_fire","duration":1}}),
        "partial","Enemy players not yet targeted; origin fire duration measured in seconds, approximate one second")
    add("hierophant",9,"Sanctified Ground",power("Sanctified Ground",
        "Receive 5% more XP while standing on sanctified blocks.",
        "origins:modify_xp_gain",modifier=mod(0.05),
        condition={"type":"origins:on_block",
                   "block_condition":{"type":"origins:in_tag","tag":"tarot:sanctified_ground"}}))
    add("emperor",3,"Frenzy",power("Frenzy",
        "At low health, occasionally gain Speed and Haste for 100 ticks.",
        "origins:action_over_time",interval=600,
        condition={"type":"origins:health","comparison":"<","compare_to":8},
        entity_action={"type":"origins:and","actions":[apply("speed",100),apply("haste",100)]}),
        "partial","Checks on 600-tick interval rather than immediately on crossing below 8 health")
    add("emperor",1,"Iron Decree",power("Iron Decree",
        "Holding a shield reduces damage taken by 15%.",
        "origins:modify_damage_taken",modifier=mod(-0.15),condition=shield),
        "partial","Stacks with existing Imperial Presence; desired effect replaces 10% with 15%")
    add("strength",4,"Hunter's Bane",power("Hunter's Bane",
        "15% more melee damage against undead.",
        "origins:modify_damage_dealt",target_condition={
            "type":"origins:in_tag","tag":"tarot:undead"},modifier=mod(0.15)),
        "partial","Demon-type opponents beyond the undead tag are not included")
    add("hermit",9,"Forbidden Knowledge",power("Forbidden Knowledge",
        "At XP 30+ without a book in the offhand, gain Mining Fatigue I.",
        "origins:action_over_time",interval=40,
        condition={"type":"origins:and","conditions":[
            {"type":"origins:xp_levels","comparison":">=","compare_to":30},
            {**book,"inverted":True}]},
        entity_action=apply("mining_fatigue",80)))
    add("hermit",3,"Omen",power("Omen",
        "10% chance on hit received to gain Speed I for 60 ticks.",
        "origins:self_action_when_hit",cooldown=1,
        entity_action={"type":"origins:chance","chance":0.10,
                       "action":apply("speed",60)}),
        "partial","Triggers when hit rather than when merely targeted")
    add("hanged_man",9,"Shadow of Degeneration",compound("Shadow of Degeneration",
        defense={"type":"origins:action_over_time","interval":20,
                 "condition":{"type":"origins:brightness","comparison":"<=","compare_to":0.467},
                 "entity_action":apply("resistance",50)},
        speed={"type":"origins:conditioned_attribute","tick_rate":20,
               "condition":{"type":"origins:brightness","comparison":"<=","compare_to":0.467},
               "modifier":{**mod(0.05),"attribute":"minecraft:generic.movement_speed"}}),
        "partial","Footstep silence unsupported and brightness approximates light <=7")
    add("death",9,"Reaper's Touch",power("Reaper's Touch",
        "Undead melee victims receive Weakness I 60 ticks; CD 200.",
        "origins:target_action_on_hit",cooldown=200,
        target_condition={"type":"origins:in_tag","tag":"tarot:undead"},
        entity_action=apply("weakness",60)))
    add("devil",9,"Sacred Rejection",power("Sacred Rejection",
        "Golden apples cannot be eaten.",
        "origins:prevent_item_use",
        item_condition={"type":"origins:ingredient",
                        "ingredient":{"items":["minecraft:golden_apple","minecraft:enchanted_golden_apple"]}}),
        "partial","Instant Healing and regeneration from healing potions should be halved")
    add("devil",9,"Corrupting Claws",power("Corrupting Claws",
        "Hostile mobs receive Wither I 40 ticks on hit; 320t cooldown.",
        "origins:target_action_on_hit",cooldown=320,
        target_condition=hostile,entity_action=apply("wither",40)),
        "partial","Enemy players omitted pending same-team safety")
    add("tower",9,"Unstable Strike",power("Unstable Strike",
        "Hostile mobs hit receive Slowness I 20 ticks; 260t cooldown.",
        "origins:target_action_on_hit",cooldown=260,
        target_condition=hostile,entity_action=apply("slowness",20)),
        "partial","Must also apply to enemy players while never hitting allies")
    add("moon",9,"Blood Diet",power("Blood Diet",
        "Cannot eat foods outside the tarot:meat item tag.",
        "origins:prevent_item_use",item_condition={"type":"origins:and","conditions":[
            {"type":"origins:food"},
            {"type":"origins:not","condition":{"type":"origins:ingredient",
                                            "ingredient":{"tag":"tarot:meat"}}}]}),
        "partial","Blocks eating nonmeat instead of allowing consumption with zero hunger restoration")
    add("sun",9,"Purification",power("Purification",
        "Every 900 ticks cleanse Poison and Weakness.",
        "origins:action_over_time",interval=900,
        entity_action={"type":"origins:and","actions":[
            {"type":"origins:clear_effect","effect":"minecraft:poison"},
            {"type":"origins:clear_effect","effect":"minecraft:weakness"}]}))
    add("sun",8,"Holy Light",power("Holy Light",
        "While sneaking, periodically heal two health points.",
        "origins:action_over_time",interval=600,
        condition={"type":"origins:sneaking"},
        entity_action={"type":"origins:heal","amount":2}),
        "partial","Source requires a continuous 60-tick crouch charge and a 600-tick ability cooldown")
    add("judgement",9,"Hold the Line",power("Hold the Line",
        "While not sprinting, damage taken is reduced by 12%.",
        "origins:modify_damage_taken",modifier=mod(-0.12),
        condition={"type":"origins:sprinting","inverted":True}),
        "partial","Also reduces non-melee attacks; original applies only to melee")
    add("world",9,"Marked Prey",power("Marked Prey",
        "Melee hitting a hostile mob marks it with Glowing for 120 ticks.",
        "origins:target_action_on_hit",cooldown=200,
        target_condition=hostile,entity_action=apply("glowing",120)),
        "partial","Enemy player targeting withheld until team safety is implemented")
    add("chariot",1,"Burning Wrath",power("Burning Wrath",
        "While burning, melee damage increases by 20%.",
        "origins:modify_damage_dealt",condition={"type":"origins:on_fire"},
        modifier=mod(0.20)))
    add("magician",9,"Full Moon Ravings",power("Full Moon Ravings",
        "Outdoors every 1200 ticks suffer Nausea I for 100 ticks.",
        "origins:action_over_time",interval=1200,
        condition={"type":"origins:exposed_to_sky"},
        entity_action=apply("nausea",100)),
        "partial","Full-moon phase and night-time gate not yet enforced")


    # Rev2 individual powers, batch 2. All additions are reviewed against
    # HandbookRev2.txt and use actual Apoli/Origins actions (never no-op stubs).
    # A "partial" result explicitly retains the unsupported remainder.
    add("empress", 9, "Mirror Veil", power("Mirror Veil",
        "Sneaking in dim light out of direct sun makes the Empress invisible, armor visible.",
        "origins:invisibility", render_armor=True,
        condition={"type":"origins:and","conditions":[
            {"type":"origins:sneaking"},
            {"type":"origins:brightness","comparison":"<=","compare_to":0.2615},
            {"type":"origins:exposed_to_sun","inverted":True}]}),
        "partial", "Brightness <=0.2615 approximates light <=7 in Nether but can include light8 in Overworld")
    add("emperor", 4, "Fallen Aura", power("Fallen Aura",
        "Hit retaliation: Slowness I 60t and Weakness I 20t; 280t cooldown.",
        "origins:attacker_action_when_hit", cooldown=280,
        entity_action={"type":"origins:and","actions":[apply("slowness",60),
                                                        apply("weakness",20)]}),
        "partial", "PvP team checks not yet verified; may proc alongside Distorted Authority")
    add("wheel_of_fortune", 9, "Fate's Current", power("Fate's Current",
        "Every 1800t get one equal-weight boon or curse: Speed, Haste, Absorption, Hunger, Slowness or Mining Fatigue.",
        "origins:action_over_time", interval=1800,
        entity_action={"type":"origins:choice","actions":[
            {"element":apply(effect,100),"weight":1}
            for effect in ("speed","haste","absorption","hunger","slowness","mining_fatigue")]}),
        "partial", "Rev2 does not specify buff/curse durations; developer alpha uses 100 ticks; Lucky Break and Winning Streak rerolls pending")
    add("justice", 9, "Patient Observation", power("Patient Observation",
        "12% less incoming damage while not sprinting.",
        "origins:modify_damage_taken", modifier=mod(-0.12),
        condition={"type":"origins:sprinting","inverted":True}),
        "partial", "Source limits reduction to mobs and adds a periodic reveal; generic damage reduction is broader")
    add("justice", 4, "Emotional Push", power("Emotional Push",
        "On being hit, inflict Weakness I on attacker for 100t; 360t cooldown.",
        "origins:attacker_action_when_hit", cooldown=360,
        entity_action=apply("weakness",100)),
        "partial", "No team-safe PvP retaliation filter; may also overlap Emotional Recoil")
    add("hanged_man", 7, "Shadow Cloak", compound("Shadow Cloak",
        resistance={"type":"origins:action_over_time","interval":20,
                    "condition":{"type":"origins:brightness","comparison":"<=","compare_to":0.5},
                    "entity_action":apply("resistance",50)},
        pace={"type":"origins:conditioned_attribute","tick_rate":20,
              "condition":{"type":"origins:brightness","comparison":"<=","compare_to":0.5},
              "modifier":{**mod(0.05),"attribute":"minecraft:generic.movement_speed"}}),
        "partial", "Silent footsteps unavailable; overlaps Seq9 shadow bonuses when both equipped")
    add("sun", 7, "Solar Flare", power("Solar Flare",
        "20% chance to blind an undead attacker for 40 ticks.",
        "origins:attacker_action_when_hit", cooldown=1,
        entity_action={"type":"origins:if_else",
            "condition":{"type":"origins:in_tag","tag":"tarot:undead"},
            "if_action":{"type":"origins:chance","chance":0.20,
                         "action":apply("blindness",40)}}))
    add("sun", 5, "Purify", power("Purify",
        "Secondary key cleanses self Poison, Wither and Blindness; 900t cooldown.",
        "origins:active_self", cooldown=900,
        key={"key":"key.origins.secondary_active"}, hud_render={"should_render":True},
        entity_action={"type":"origins:and","actions":[
            {"type":"origins:clear_effect","effect":"minecraft:poison"},
            {"type":"origins:clear_effect","effect":"minecraft:wither"},
            {"type":"origins:clear_effect","effect":"minecraft:blindness"}]}),
        "partial", "Rev2 also allows targeting an allied player within four blocks; self-only until same-team check is implemented")
    add("world", 4, "Historical Recall", power("Historical Recall",
        "Hits on hostile mobs apply Glowing for 160t; 200t cooldown.",
        "origins:target_action_on_hit", cooldown=200,
        target_condition={"type":"origins:in_tag","tag":"tarot:hostile"},
        entity_action=apply("glowing",160)),
        "partial", "Enemy players omitted to avoid friendly-fire; may stack with Marked Prey on hit")
    add("tower", 4, "Impact", power("Impact",
        "Hit hostile mobs with Slowness I for 40 ticks; cooldown 260.",
        "origins:target_action_on_hit", cooldown=260,
        target_condition={"type":"origins:in_tag","tag":"tarot:hostile"},
        entity_action=apply("slowness",40)),
        "partial", "Enemy players excluded; source specifies upgrade rather than separately stacking with Unstable Strike")
    add("star", 2, "Conceal", power("Conceal",
        "Every 3600 ticks become invisible for 100 ticks.",
        "origins:action_over_time", interval=3600,
        entity_action=apply("invisibility",100)),
        "partial", "Rev2 does not specify activation trigger; implementation uses an automatic periodic proc")
    add("hermit", 1, "Prying Eyes", power("Prying Eyes",
        "Night Vision while in extremely low light.",
        "origins:night_vision",
        condition={"type":"origins:brightness","comparison":"<=","compare_to":0.07}),
        "partial", "Brightness threshold approximates light<=3 in Overworld and is too strict for Nether ambient light")
    add("sun", 1, "Beacon of Faith II", power("Beacon of Faith II",
        "Glowing for all entities within 20 blocks, refreshed every 40 ticks.",
        "origins:action_over_time", interval=40,
        entity_action={"type":"origins:area_of_effect","radius":20,
                       "include_target":True,
                       "bientity_action":{"type":"origins:target_action",
                                          "action":apply("glowing",80)}}),
        "partial", "Exact always-on visual glow semantics and team visibility differ from periodic Glowing effects")

    # The fixed primary identity penalties must be native, not removable
    # by unequipping the player's Sequence 9 slot at Sequence 4.
    add("justice", 9, "Compassionate Restraint", power(
        "Compassionate Restraint",
        "70% less damage against passive mobs (villagers/pets included in tarot:passive).",
        "origins:modify_damage_dealt",
        target_condition={"type":"origins:in_tag","tag":"tarot:passive"},
        modifier=mod(-0.70)),
        "partial", "Original also requires 30% less damage against unprovoked enemy players; provocation and team rules are unavailable")
    add("hanged_man", 9, "Weight of Sin", power(
        "Weight of Sin",
        "Natural regeneration stops above 8 hearts (16 health points).",
        "origins:disable_regen",
        condition={"type":"origins:health","comparison":">","compare_to":16}),
        "partial", "Rev2 temporary regen-cap unlocks by kills, Healing potions or remaining motionless in darkness are not implemented")


    # Rev2 sequence upgrade batch: faithfully model independent bonuses where
    # possible. Upgrades which should replace an earlier slotted kit are
    # PARTIAL until a nonstacking, upgrade-aware slot policy exists.
    add("devil", 4, "Demon Form", power("Demon Form",
        "When below half health, gain 18% attack damage.",
        "origins:conditioned_attribute",tick_rate=20,
        modifier={**mod(0.18),"attribute":"minecraft:generic.attack_damage"},
        condition={"type":"origins:relative_health","comparison":"<","compare_to":0.5}),
        "partial", "Can stack with Seq9 Desperate Malice, which the upgrade should replace")
    add("tower", 1, "Ruin-Proof II", power("Ruin-Proof II",
        "Reduce explosion damage by 80%.",
        "origins:modify_damage_taken",
        damage_condition={"type":"origins:name","name":"explosion"},
        modifier=mod(-0.8)),
        "partial", "May stack with Ruin-Proof and not cover every explosion damage source variant")
    add("wheel_of_fortune", 4, "Misfortune", power("Misfortune",
        "15% chance to reduce incoming damage by 60%.",
        "origins:modify_damage_taken",
        condition={"type":"origins:chance","chance":0.15},
        modifier=mod(-0.6)),
        "partial", "Rev2 upgrade replaces Fate Intervenes; if both are slotted the chance may stack")
    add("judgement", 1, "Law's Weight II", power("Law's Weight II",
        "Increase knockback resistance by 0.60.",
        "origins:attribute",
        modifier={**mod(0.60,"addition"),
                  "attribute":"minecraft:generic.knockback_resistance"}),
        "partial", "Rev2 upgrades +45% to +60%, not additive; this standalone bonus stacks if both slots equipped")
    add("star", 4, "Nightwatch II", compound("Nightwatch II",
        speed={"type":"origins:conditioned_attribute","tick_rate":20,
               "condition":{"type":"origins:brightness","comparison":"<=","compare_to":0.467},
               "modifier":{**mod(0.15),"attribute":"minecraft:generic.movement_speed"}},
        combat={"type":"origins:modify_damage_dealt",
                "condition":{"type":"origins:brightness","comparison":"<=","compare_to":0.467},
                "target_condition":{"type":"origins:in_tag","tag":"tarot:undead"},
                "modifier":mod(0.15)}),
        "partial", "Overlaps Nightwatch night buffs when both slots equipped; brightness threshold approximates light<=7")
    add("empress", 5, "Plague Touch", power("Plague Touch",
        "Hostile hit applies Poison I 80 ticks and Hunger I 40 ticks; 240t cooldown.",
        "origins:target_action_on_hit", cooldown=240,
        target_condition={"type":"origins:in_tag","tag":"tarot:hostile"},
        entity_action={"type":"origins:and","actions":[
            apply("poison",80),apply("hunger",40)]}),
        "partial", "Enemy players excluded pending team checks; overlaps Seq9 Witch's Venom rather than replacing it")

    # Parallel handbook-backed workstreams: 14 support/identity, 17 control,
    # and 7 mobility/stealth powers. Each retains its own source audit label.
    from .batches import support, control, mobility
    from .batches import native2
    for workstream in (support, control, mobility, native2):
        workstream.register(add)
    # Resonance powers now compile into real JSON and manifest records.
    # Full-build intentionally never grants them until all 10 per pair exist.
    from .batches import resonance
    resonance.register(add)
    # Manifest includes all 434, but only installed concrete effects count as implemented.
    manifest=[]
    kits={}
    for (slug,seq,normalized),(card,entry,family) in entries.items():
        ident="tarot:"+slug+"/"+str(seq)+"_"+entry["slug"]
        key=(slug,seq,normalized)
        status=accurate.get(key,"blocked")
        manifest.append({
            "family":family,"pathway":slug,"sequence":seq,
            "name":entry["name"],"power_id":ident if status!="blocked" else None,
            "flag":entry["flag"],"status":status,
            "missing":notes.get(key,"Needs exact scripting, client integration, or verified Origins 1.4.1 translation" if status=="blocked" else ""),
            "source":entry["description"],"details":entry.get("details",[]),
        })
        if status!="blocked":
            kits.setdefault((slug,seq),[]).append(ident)
    if len(manifest)!=434 or any(a["power_id"] not in compiled for a in manifest if a["power_id"]):
        raise AssertionError("manifest integrity")
    return compiled, manifest, kits
