"""First 23 non-placeholder Resonance abilities across all 11 Rev2 pair forms.

These are compiled and source-audited but NEVER equipped by the release-locked
Seq1 runtime. No fake 10/10-kit readiness is implied by this registry.
"""
from ..powers import power, apply, mod, compound
from ..team_policy import nearby_ally_condition
from .shared import active, periodic, effect, mobs, players, combined, cmd


def attribute(name, value, operation="multiply_total"):
    return {"type":"origins:attribute",
            "modifier":{**mod(value,operation),
                        "attribute":"minecraft:generic."+name}}


def damage_taken(value, damage_condition=None, condition=None):
    result={"type":"origins:modify_damage_taken","modifier":mod(value)}
    if damage_condition:result["damage_condition"]=damage_condition
    if condition:result["condition"]=condition
    return result


def damage_dealt(value, tag):
    return {"type":"origins:modify_damage_dealt",
            "target_condition":{"type":"origins:in_tag","tag":"tarot:"+tag},
            "modifier":mod(value)}


def attacked_by(tag):
    return {"type":"origins:attacker",
            "entity_condition":{"type":"origins:in_tag","tag":"tarot:"+tag}}


def night():
    return {"type":"origins:daytime","inverted":True}


def register(add):
    # SEQUENCE 9: one bona fide implementation for each of 11 paired forms.
    add("paper_martyr",9,"Burdened Beginning",
        compound("Burdened Beginning",
            sight=active("Burdened Sight","Crouch + secondary glows every entity in ten blocks for 100t.",
                         cmd("execute at @s run effect give @e[distance=..10] minecraft:glowing 5 0 true"),
                         100,crouch=True),
            cap={"type":"origins:disable_regen",
                 "condition":{"type":"origins:health","comparison":">","compare_to":16}}),
        "partial","Sin storage at 25%, 8-HP Sin cap and sharing with Spirit Vision are not implemented")
    add("marked_verdict",9,"Cold Judgment",
        compound("Cold Judgment",
            arrow={"type":"origins:modify_projectile_damage","modifier":mod(0.25)},
            guard=damage_taken(-0.12,attacked_by("hostile"),
                               {"type":"origins:sprinting","inverted":True}),
            compassion=damage_dealt(-0.70,"passive")),
        "partial","The mob reduction covers tagged hostiles only; vanilla nonhostile attackers and unprovoked enemy players are omitted")
    add("burning_archive",9,"Scholar's Fire",
        compound("Scholar's Fire",
            learning={"type":"origins:modify_xp_gain","modifier":mod(0.35)},
            immunity={"type":"origins:fire_immunity"},
            momentum={"type":"origins:modify_damage_dealt",
                      "condition":{"type":"origins:sprinting"},"modifier":mod(0.15)}))
    add("crumbling_reaper",9,"Grave Ruin",
        compound("Grave Ruin",
            stone={"type":"origins:modify_break_speed",
                   "block_condition":{"type":"origins:in_tag","tag":"tarot:natural_stone"},
                   "modifier":mod(0.30)},
            grave=damage_taken(-0.25,attacked_by("undead")),
            blast=damage_taken(-0.60,{"type":"origins:name","name":"explosion"}),
            falling=damage_taken(0.75,{"type":"origins:name","name":"fall"})),
        "partial","Explosion reduction is only tied to the named explosion source, not every explosion damage type")
    add("impossible_fist",9,"Traveler's Might",
        compound("Traveler's Might",
            speed=attribute("movement_speed",0.12),
            fall=damage_taken(-0.70,{"type":"origins:name","name":"fall"}),
            armor=attribute("armor",3.0,"addition"),
            jump={"type":"origins:modify_jump","modifier":mod(0.20)}))
    near_teammate=nearby_ally_condition(8)
    shield={"type":"origins:or","conditions":[
        {"type":"origins:equipped_item","equipment_slot":slot,
         "item_condition":{"type":"origins:ingredient",
                           "ingredient":{"item":"minecraft:shield"}}}
        for slot in ("mainhand","offhand")]}
    alone={"type":"origins:scoreboard","objective":"a_alone_time",
           "comparison":">","compare_to":600}
    add("benevolent_crown",9,"Sovereign's Care",
        compound("Sovereign's Care",
            armor=attribute("armor",3.0,"addition"),
            knockback=attribute("knockback_resistance",0.40,"addition"),
            together={"type":"origins:conditioned_attribute","tick_rate":20,
                      "condition":near_teammate,
                      "modifier":{**mod(0.05),"attribute":"minecraft:generic.movement_speed"}},
            burden={"type":"origins:conditioned_attribute","tick_rate":20,
                    "condition":shield,
                    "modifier":{**mod(-0.25),"attribute":"minecraft:generic.movement_speed"}},
            exhaustion={"type":"origins:modify_exhaustion","condition":shield,
                        "modifier":mod(0.50)},
            lonely={"type":"origins:modify_exhaustion","condition":alone,
                    "modifier":mod(0.35)},
            lonely_mining={"type":"origins:modify_break_speed","condition":alone,
                           "modifier":mod(-0.15)}),
        "partial","Lacks +25% self-healing; teammate detection only covers configured vanilla combat teams; shield penalty and loneliness modifiers can compound")
    add("binding_contract",9,"Hellborn Verdict",
        compound("Hellborn Verdict",
            immunity={"type":"origins:fire_immunity"},
            armor=attribute("armor",2.0,"addition"),
            knockback=attribute("knockback_resistance",0.45,"addition"),
            retaliation={"type":"origins:attacker_action_when_hit","cooldown":280,
                         "damage_condition":attacked_by("hostile"),
                         "entity_action":apply("slowness",60)},
            taboo={"type":"origins:prevent_item_use",
                   "item_condition":{"type":"origins:ingredient",
                                     "ingredient":{"items":[
                                         "minecraft:golden_apple",
                                         "minecraft:enchanted_golden_apple",
                                         "minecraft:ender_pearl"]}}}),
        "partial","Missing hostile enemy-player retaliation; basic debuff and food/pearl bans are real")
    add("starless_poison",9,"Sleepless Grace",
        compound("Sleepless Grace",
            vision={"type":"origins:night_vision"},
            pace=attribute("movement_speed",0.10),
            poison={"type":"origins:effect_immunity","effects":["minecraft:poison"]},
            night_pace={"type":"origins:conditioned_attribute",
                        "condition":night(),"tick_rate":20,
                        "modifier":{**mod(0.15),
                                    "attribute":"minecraft:generic.movement_speed"}},
            sleep={"type":"origins:prevent_sleep","message":"The stars deny rest.",
                   "set_spawn_point":True},
            sunny_arrows={"type":"origins:modify_projectile_damage",
                          "condition":{"type":"origins:exposed_to_sun"},
                          "modifier":mod(0.25)}),
        "partial","Sunny projectile bonus includes non-arrow projectiles, and 10%+15% movement modifiers may stack multiplicatively")
    add("eclipse",9,"Unshadowed Sanguine",
        compound("Unshadowed Sanguine",
            undead=damage_dealt(0.40,"undead"),
            vision={"type":"origins:night_vision"},
            glow=periodic("Permanent Glow","Regain Glowing every 40 ticks.",
                          apply("glowing",90),40),
            flesh={"type":"origins:prevent_item_use",
                   "item_condition":{"type":"origins:and","conditions":[
                       {"type":"origins:food"},
                       {"type":"origins:not","condition":{
                           "type":"origins:ingredient",
                           "ingredient":{"tag":"tarot:meat"}}}]}}),
        "partial","Nighttime Wither resistance omitted; nonmeat is blocked rather than eaten without restoring hunger")
    add("walking_sanctuary",9,"Wraith's Prayer",
        compound("Wraith's Prayer",
            veil={"type":"origins:invisibility",
                  "condition":{"type":"origins:and","conditions":[
                      {"type":"origins:sneaking"},
                      {"type":"origins:brightness","comparison":"<=","compare_to":0.27}]}},
            falling=damage_taken(-0.60,{"type":"origins:name","name":"fall"}),
            heal=periodic("Prayer","Regeneration to players within 8 blocks every 800t.",
                          effect(players(8),"regeneration",80),800),
            chest={"type":"origins:restrict_armor",
                   "chest":{"type":"origins:ingredient","ingredient":{"items":[
                       "minecraft:iron_chestplate",
                       "minecraft:diamond_chestplate",
                       "minecraft:netherite_chestplate"]}}},
            fasting={"type":"origins:prevent_item_use",
                     "item_condition":{"type":"origins:ingredient",
                                       "ingredient":{"tag":"tarot:meat"}}}),
        "partial","Darkness brightness approximates light <=7; chestplate restrictions and fasting may overlap older identity drawbacks")
    effects=("speed","haste","absorption","hunger","slowness","mining_fatigue")
    add("loaded_dice",9,"Fated Reader",
        compound("Fated Reader",
            learning={"type":"origins:modify_xp_gain","modifier":mod(0.35)},
            luck=attribute("luck",1.0,"addition"),
            luck_defense=damage_taken(-0.50,condition={"type":"origins:chance","chance":0.15}),
            book_penalty={"type":"origins:modify_break_speed",
                 "modifier":mod(-0.20),
                 "condition":{"type":"origins:equipped_item",
                     "equipment_slot":"offhand",
                     "item_condition":{"type":"origins:ingredient",
                                       "ingredient":{"tag":"tarot:books"}},
                     "inverted":True}},
            fate=periodic("Fate's Current","One of six equal boon or curse draws each 1800t.",
                          {"type":"origins:choice","actions":[
                              {"weight":1,"element":apply(x,100)} for x in effects]},1800)),
        "partial","Temporary fate effects last 100t by default, source does not specify durations; negative outcomes always present")
    # SEQUENCE 8: each registered effect is real; scripted remainder disclosed.
    add("burning_archive",8,"Combat Insight",
        power("Combat Insight","20% chance on taking damage: Resistance I and Speed I for 40t.",
              "origins:self_action_when_hit",cooldown=1,
              entity_action={"type":"origins:chance","chance":0.20,
                             "action":combined(apply("resistance",40),apply("speed",40))}))
    add("impossible_fist",8,"Sleight of Fist",
        compound("Sleight of Fist",
            fall_guard=damage_taken(-1.0,{"type":"origins:name","name":"fall"},
                                    {"type":"origins:chance","chance":0.30}),
            punch={"type":"origins:modify_damage_dealt",
                   "condition":{"type":"origins:equipped_item",
                       "equipment_slot":"mainhand",
                       "item_condition":{"type":"origins:empty"}},
                   "modifier":mod(2.0,"addition")}),
        "partial","30% fall damage save does not teleport; unarmed bonus may stack with earlier pathway's bonus")
    passive={"type":"origins:command",
             "command":"execute at @s if entity @e[type=#tarot:passive,distance=..4]",
             "comparison":">=","compare_to":1}
    add("benevolent_crown",8,"Unbound Symbiosis",
        compound("Unbound Symbiosis",
            curse={"type":"origins:effect_immunity","effects":["minecraft:weakness"],
                   "condition":{"type":"origins:health","comparison":"<","compare_to":12}},
            health={"type":"origins:conditioned_attribute","tick_rate":20,
                    "condition":passive,
                    "modifier":{**mod(1.0,"addition"),
                                "attribute":"minecraft:generic.max_health"}}))
    add("binding_contract",8,"Fallen Question",
        compound("Fallen Question",
            resistance={"type":"origins:self_action_when_hit","cooldown":1,
                        "entity_action":{"type":"origins:chance","chance":0.10,
                                         "action":apply("strength",40)}},
            question={"type":"origins:action_on_entity_use",
                      "condition":{"type":"origins:sneaking"},
                      "bientity_condition":{"type":"origins:target_condition",
                                           "condition":{"type":"origins:in_tag",
                                                        "tag":"tarot:hostile"}},
                      "bientity_action":{"type":"origins:target_action",
                                         "action":apply("weakness",60)}}),
        "partial","Enemy-player targeting and 400t right-click cooldown are unavailable")
    add("walking_sanctuary",8,"Madness Consecrate",
        power("Madness Consecrate","10% chance when hit to gain Speed I 60 ticks.",
              "origins:self_action_when_hit",cooldown=1,
              entity_action={"type":"origins:chance","chance":0.10,
                             "action":apply("speed",60)}),
        "partial","Requires extra 1200t Consecrate on block/place whose exact behavior is not represented")
    add("loaded_dice",8,"Deduction Machine",
        power("Deduction Machine","20% chance on kill to gain one experience point.",
              "origins:self_action_on_kill",
              entity_action={"type":"origins:chance","chance":0.20,
                             "action":cmd("experience add @s 1 points")}),
        "partial","10% damage chance to reset Fate's Current is not implemented")
    add("starless_poison",8,"Lullaby Whisper",
        active("Lullaby Whisper","Sneak and secondary: Slowness I 60t to tagged hostiles within five blocks.",
               effect(mobs(5),"slowness",60),1200,crouch=True),
        "partial","Missing 60t charge and Whisper passive-mob AI, plus enemy-player targets")
    add("eclipse",8,"Holy Tamer",
        active("Holy Tamer","Crouch and secondary: self heals two health points.",
               {"type":"origins:heal","amount":2},600,crouch=True),
        "partial","Tame passive-mob ability is not implemented and its cooldown is independent")
    # SEQUENCE 7: additional native combination powers.
    add("starless_poison",7,"Nightmare Fire",
        compound("Nightmare Fire",
            night_xp={"type":"origins:self_action_on_kill","condition":night(),
                      "entity_action":{"type":"origins:chance","chance":0.20,
                                       "action":cmd("experience add @s 1 points")}},
            flame={"type":"origins:target_action_on_hit","cooldown":1,
                   "target_condition":{"type":"origins:in_tag","tag":"tarot:hostile"},
                   "entity_action":{"type":"origins:chance","chance":0.10,
                                    "action":{"type":"origins:set_on_fire","duration":1}}}),
        "partial","Enemy-player targets omitted, 20t fire duration approximates one second; the two procs are independent")
    add("binding_contract",7,"Predator's Calm",
        compound("Predator's Calm",
            kill={"type":"origins:self_action_on_kill",
                  "entity_action":apply("speed",60)},
            calm={"type":"origins:action_on_entity_use",
                  "bientity_condition":{"type":"origins:target_condition",
                                       "condition":{"type":"origins:in_tag","tag":"tarot:hostile"}},
                  "bientity_action":{"type":"origins:target_action",
                                     "action":apply("slowness",60)}}),
        "partial","Enemy-player target and right-click cooldown absent; kill Speed I 60t works")
    add("eclipse",7,"Solar Drain",
        compound("Solar Drain",
            flare={"type":"origins:attacker_action_when_hit",
                   "damage_condition":attacked_by("undead"),"cooldown":1,
                   "entity_action":{"type":"origins:chance","chance":0.20,
                                    "action":apply("blindness",40)}},
            drain={"type":"origins:self_action_on_hit","cooldown":100,
                   "entity_action":{"type":"origins:heal","amount":1}}),
        "partial","1 HP melee drain can trigger on allied targets because melee-hit team filtering is unresolved")
    add("loaded_dice",7,"Index of Luck",
        attribute("luck",1.0,"addition"),
        "partial","May raise combined Luck above required +2 cap when paired with Fated Reader and earlier kits")
