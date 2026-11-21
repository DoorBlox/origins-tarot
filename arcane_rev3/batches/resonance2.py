"""Rev2 Resonance wave 2: 28 additional native, explicitly partial pair abilities.

Only effects that have an executable vanilla/Origins 1.4.1 translation are
emitted. Enemy-player debuffs and unsafe entity-AI hooks are withheld.
Every missing element is disclosed in the 434-entry manifest.
"""
from ..powers import power, apply, mod, compound
from ..team_policy import enemy_effect, ally_effect
from .shared import active, periodic, effect, mobs, players, combined, cmd
from .resonance import attacked_by, night


def hit(name, effect_name, duration, *, cooldown=200, amplifier=0, tag="hostile"):
    return power(name, f"Melee hit tagged {tag} mobs with {effect_name}.",
        "origins:target_action_on_hit",cooldown=cooldown,
        target_condition={"type":"origins:in_tag","tag":f"tarot:{tag}"},
        entity_action=apply(effect_name,duration,amplifier))


def close_target(radius,eff,ticks,amp=0):
    return effect(mobs(radius),eff,ticks,amp)


def onkill(action,*,cooldown=400):
    return {"type":"origins:self_action_on_kill","cooldown":cooldown,
            "entity_action":action}


def register(add):
    add("marked_verdict",8,"Paper Sentence",
        compound("Paper Sentence",
            weak={"type":"origins:target_action_on_hit","cooldown":200,
                  "target_condition":{"type":"origins:in_tag","tag":"tarot:hostile"},
                  "entity_action":combined(apply("slowness",40),apply("weakness",40))}),
        "partial","Melee debuff fallback only; paper dagger projectile, 3 damage, paper consumption and enemy-player targeting are absent")
    add("marked_verdict",7,"Hunter's Calm",
        periodic("Hunter's Calm","When still and holding bow, slow nearby tagged hostiles.",
            close_target(6,"slowness",60),interval=60,
            condition={"type":"origins:and","conditions":[
                {"type":"origins:sprinting","inverted":True},
                {"type":"origins:equipped_item","equipment_slot":"mainhand",
                 "item_condition":{"type":"origins:ingredient",
                                   "ingredient":{"item":"minecraft:bow"}}}]}),
        "partial","Predator's Patience charge is not sped up; does not check truly motionless status or affect enemy players")
    add("marked_verdict",5,"Puppet's Sentence",
        active("Puppet's Sentence","Sneak + secondary slows and highlights nearest hostile mob.",
            combined(effect(mobs(8,nearest=True),"slowness",80,1),
                     effect(mobs(8,nearest=True),"glowing",80)),400,crouch=True),
        "partial","No enemy-player coordinate reveal, no separate 40t duration for players, no red outline client rendering")
    add("marked_verdict",4,"Marked Judgment",
        hit("Marked Judgment","weakness",120),
        "partial","Only hostile mobs are targetable; direction indicator and Marked Prey linkage not implemented")
    add("marked_verdict",3,"Hunter's Stillness",
        periodic("Hunter's Stillness","Holding a bow while not sprinting slows nearby hostile mobs.",
            combined(close_target(6,"slowness",60),
                     enemy_effect("slowness",60,6)),interval=100,
            condition={"type":"origins:and","conditions":[
                {"type":"origins:sprinting","inverted":True},
                {"type":"origins:equipped_item","equipment_slot":"mainhand",
                 "item_condition":{"type":"origins:ingredient",
                                   "ingredient":{"item":"minecraft:bow"}}}]}),
        "partial","Not fully motionless (only no sprint); periodic 100t pulse differs from on-entry; player Slowness only to listed opposing teams")
    add("burning_archive",7,"Astrologer's Trail",
        periodic("Astrologer's Trail","While sprinting, ignite tagged hostile mobs within two blocks.",
            cmd("execute at @s as @e[type=#tarot:hostile,distance=..2] "
                "run data merge entity @s {Fire:40s}"),40,
            condition={"type":"origins:sprinting"}),
        "partial","Star Chart positioning omitted, no persistent trail and no enemy-player ignition")
    add("burning_archive",6,"Recorded Plot",
        power("Recorded Plot","20% chance on kill to gain one XP level.",
            "origins:self_action_on_kill",
            entity_action={"type":"origins:chance","chance":0.20,
                           "action":cmd("execute if entity @s[level=..29] "
                                        "run experience add @s 1 levels")}),
        "partial","Recorded Step coordinate scroll unavailable; level 30 cap is a conservative fallback")
    star_read_reaper = active("Star Read Reaper",
        "At night illuminate tagged hostiles and listed enemy teams in 15 blocks.",
        combined(effect(mobs(15),"glowing",100),
                 enemy_effect("glowing",100,15)),600)
    star_read_reaper["condition"] = night()
    add("burning_archive",5,"Star Read Reaper",
        star_read_reaper,
        "partial","Reap next-hit +30% and 60t ignition remain absent; night-locked Glowing substitutes for real health/name readout on mobs and listed enemy teams")
    add("burning_archive",3,"Insightful Flame",
        periodic("Insightful Flame","While sprinting slow hostile mobs within two blocks.",
            combined(close_target(2,"slowness",40),
                     enemy_effect("slowness",40,2)),40,
            condition={"type":"origins:sprinting"}),
        "partial","No persistent flame trail, exact +1 damage or health readout; nearby listed enemy teams receive the same bounded Slowness while sprinting")
    heads={"type":"origins:or","conditions":[
        {"type":"origins:block","block":f"minecraft:{x}"} for x in
        ("skeleton_skull","wither_skeleton_skull","zombie_head","player_head")]}
    add("crumbling_reaper",8,"Grave Dirt + Fault Line",
        power("Grave Dirt + Fault Line","Right-click a skull or head to gain one XP point.",
            "origins:action_on_block_use",hands=["main_hand"],
            block_condition=heads,entity_action=cmd("experience add @s 1 points")),
        "partial","Fault Line's 5% break-above event is not implemented; skull activation cooldown 1200t not enforced")
    add("crumbling_reaper",7,"Spirit Shockwave",
        active("Spirit Shockwave","Crouch + secondary reveals undead within 10 blocks for 100t.",
            effect(mobs(10,"undead"),"glowing",100),600,crouch=True),
        "partial","Requires 60t crouch charge; fall-triggered 2-damage shockwave is omitted")
    add("crumbling_reaper",6,"Guide's Foundation",
        compound("Guide's Foundation",
            undead_heal={"type":"origins:self_action_on_kill",
                         "bientity_condition":{"type":"origins:target_condition",
                                              "condition":{"type":"origins:in_tag","tag":"tarot:undead"}},
                         "entity_action":{"type":"origins:heal","amount":1}},
            pick_guard={"type":"origins:modify_damage_taken",
                        "damage_condition":{"type":"origins:name","name":"fall"},
                        "condition":{"type":"origins:equipped_item","equipment_slot":"mainhand",
                            "item_condition":{"type":"origins:ingredient",
                                              "ingredient":{"tag":"minecraft:pickaxes"}}},
                        "modifier":mod(-0.20)}),
        "partial","Undead heal only triggers for caster's own kills, not all nearby undead deaths")
    add("benevolent_crown",7,"Coin's Blessing",
        power("Coin's Blessing","Gold ingot right-click slows tagged hostile mobs.",
            "origins:action_on_entity_use",
            item_condition={"type":"origins:ingredient",
                            "ingredient":{"item":"minecraft:gold_ingot"}},
            bientity_condition={"type":"origins:target_condition",
                                "condition":{"type":"origins:in_tag","tag":"tarot:hostile"}},
            bientity_action={"type":"origins:target_action","action":apply("slowness",100)}),
        "partial","Does not force AI pacification or auto-grow crops; native right-click lacks the 600t cooldown")
    add("benevolent_crown",6,"Corrupt Symbiosis",
        active("Corrupt Symbiosis","Secondary key Slowness I to tagged hostiles within five blocks.",
            combined(close_target(5,"slowness",100),
                     enemy_effect("slowness",100,5),
                     ally_effect("regeneration",100,5)),1200),
        "partial","No persistent 5x5 ground field or passive health-max Symbiosis; listed teammates get one-shot Regen and listed enemy teams a bounded slow")
    add("benevolent_crown",5,"Decree of Nature",
        active("Decree of Nature","Secondary key Slowness II to tagged hostiles in six blocks.",
            close_target(6,"slowness",100,1),900),
        "partial","Cannot force hostile mob AI to target the Emperor or affect enemy players")
    add("binding_contract",6,"Devil's Verdict",
        compound("Devil's Verdict",
            claw={"type":"origins:target_action_on_hit","cooldown":400,
                  "target_condition":{"type":"origins:in_tag","tag":"tarot:hostile"},
                  "entity_action":apply("wither",40)},
            punishment=onkill(close_target(4,"slowness",40),cooldown=400)),
        "partial","Enemy players are excluded to protect teammates; kill pulse affects hostile mobs only")
    add("binding_contract",5,"Desire's Discipline",
        active("Desire's Discipline","Secondary key slows closest tagged hostile mob 60t.",
            effect(mobs(5,nearest=True),"slowness",60,1),600,crouch=True),
        "partial","Does not reveal held item of a player; cannot stun next melee hit or target enemy players")
    add("binding_contract",4,"Infernal Verdict",
        power("Infernal Verdict",
            "Melee hits on tagged hostiles inflict Wither 40t, Slowness I 40t and Glowing 80t.",
            "origins:target_action_on_hit", cooldown=320,
            target_condition={"type": "origins:in_tag", "tag": "tarot:hostile"},
            entity_action=combined(
                apply("wither", 40), apply("slowness", 40),
                apply("glowing", 80))),
        "partial", "The source demands red Glowing (client color unsupported) and marked player targets; enemy players still omitted, no verified cross-team on-hit predicate")
    add("starless_poison",6,"Soul Thread",
        power("Soul Thread","While night, 10% chance on hit to gain Resistance I 40t.",
            "origins:self_action_when_hit",cooldown=1,
            condition=night(),
            entity_action={"type":"origins:chance","chance":0.10,
                           "action":apply("resistance",40)}),
        "partial","Thread's Slowness debuff and 400t active cooldown are not implemented")
    add("starless_poison",5,"Haunting Plague",
        active("Haunting Plague",
            "Secondary blinds and poisons nearby tagged hostiles and listed enemy teams.",
            combined(close_target(6,"blindness",60),
                     close_target(6,"poison",60),
                     enemy_effect("blindness",60,6),
                     enemy_effect("poison",60,6)),900),
        "partial","Witch's Venom on-hit Poison80/Hunger40 component is not included; area pulses are not per-hit targeting, and neutral/unlisted players remain excluded")
    add("starless_poison",4,"Night Venom",
        periodic("Night Venom","At night periodically poison tagged hostiles in five blocks.",
            combined(close_target(5,"poison",60),
                     enemy_effect("poison",60,5)),120,
            condition=night()),
        "partial","Nightwatch conditional bonus damage to poisoned targets omitted; only listed opposing combat teams receive the nighttime Poison pulse")
    add("eclipse",5,"Purify Scarlet",
        active("Purify Scarlet","Secondary cleanses self and grants Regeneration I 100t.",
            combined({"type":"origins:clear_effect","effect":"minecraft:poison"},
                     {"type":"origins:clear_effect","effect":"minecraft:wither"},
                     {"type":"origins:clear_effect","effect":"minecraft:blindness"},
                     apply("regeneration",100)),1200),
        "partial","Cannot give Scarlet +50% potion healing for 200t; targeting allied players within four blocks is not implemented")
    add("eclipse",4,"Sunrise",
        power("Sunrise","On hitting an undead mob, heal two health points.",
            "origins:self_action_on_hit",cooldown=100,
            bientity_condition={"type":"origins:target_condition",
                                "condition":{"type":"origins:in_tag","tag":"tarot:undead"}},
            entity_action={"type":"origins:heal","amount":2}),
        "partial","Half-heart drain from target and 40t fire are missing; healing only occurs for undead personally hit")
    add("walking_sanctuary",6,"Rot Sanctum",
        compound("Rot Sanctum",
            hunger={"type":"origins:target_action_on_hit","cooldown":300,
                    "target_condition":{"type":"origins:in_tag","tag":"tarot:hostile"},
                    "entity_action":apply("hunger",40)},
            sanctified={"type":"origins:modify_xp_gain","modifier":mod(0.05),
                        "condition":{"type":"origins:on_block",
                                     "block_condition":{"type":"origins:in_tag",
                                                        "tag":"tarot:sanctified_ground"}}}),
        "partial","Enemy players excluded from melee Hunger; sanctuary reward only triggers while standing directly on block")
    add("walking_sanctuary",5,"Incorporeal Hymn",
        active("Incorporeal Hymn","Secondary grants self Invisibility and Regeneration to players nearby.",
            combined(apply("invisibility",60),
                     effect(players(8),"regeneration",100)),1200),
        "partial","Leaves/cobweb phasing and 3-block periodic regeneration during phased state are not available")
    add("loaded_dice",5,"Ritual Winning",
        active("Ritual Winning","Secondary heals nearby players and increases Luck for 200 ticks.",
            combined(effect(players(3),"regeneration",100),
                     effect(players(3),"luck",200)),900),
        "partial","Luck also benefits enemy players; Misfortune -60% incoming damage proc is not represented")
    add("loaded_dice",4,"Fated Deduction",
        power("Fated Deduction","30% chance after kill to gain one XP level.",
            "origins:self_action_on_kill",
            entity_action={"type":"origins:chance","chance":0.30,
                           "action":cmd("execute if entity @s[level=..29] run experience add @s 1 levels")}),
        "partial","Does not guarantee the next Fate's Current is positive; level cap 30 is a fallback")
    add("impossible_fist",5,"Doorstep Slam",
        active("Doorstep Slam","Secondary attempts an eight-block forward teleport and gives Strength I.",
            combined(cmd("execute at @s positioned ^ ^ ^8 if block ~ ~ ~ minecraft:air "
                         "if block ~ ~1 ~ minecraft:air run tp @s ~ ~ ~"),
                     apply("strength",60)),300),
        "partial","No landing raycast and 60t next-melee +10%/Slowness20 targeted buff; Strength I is only an approximation")
