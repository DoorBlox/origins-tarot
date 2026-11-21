"""Rev2 bulk batch B: 17 fail-closed crowd-control and retaliation powers.

Hostile targets use the exact vanilla entity-type tag and never @a; enemy-player
targeting stays withheld pending a tested scoreboard-team comparison.
"""
from ..powers import power, apply, compound
from .shared import active, periodic, effect, mobs, combined, cmd


def single_target_use(name, description, tag, effect_name, ticks, *, crouch=False):
    """Native 1.4.1 right-click effect, without pretending unsupported CD works."""
    out = power(name, description, "origins:action_on_entity_use",
                bientity_condition={"type":"origins:target_condition",
                                    "condition":{"type":"origins:in_tag","tag":f"tarot:{tag}"}},
                bientity_action={"type":"origins:target_action",
                                 "action":apply(effect_name,ticks)})
    if crouch:
        out["condition"] = {"type":"origins:sneaking"}
    return out


def register(add):
    add("lovers", 5, "Nature's Grasp",
        active("Nature's Grasp", "Secondary key slows hostile mobs within four blocks.",
               effect(mobs(4), "slowness", 60, 1), 900),
        "partial", "Enemy players are omitted to protect teammates; hostile mobs receive Slowness II for 60t")
    add("lovers", 2, "Withering",
        active("Withering", "Secondary key applies Wither I 60t to nearby hostile mobs.",
               effect(mobs(5), "wither", 60), 3600),
        "partial", "Source also requires enemy players within five blocks; they are omitted for team safety")
    add("temperance", 2, "Bane",
        active("Bane", "Secondary key applies Weakness II 100t to hostile mobs in five blocks.",
               effect(mobs(5), "weakness", 100, 1), 3600),
        "partial", "Enemy players within five blocks are omitted pending verified ally filtering")
    add("tower", 2, "Cataclysm",
        active("Cataclysm", "Secondary key applies Mining Fatigue I 200t to hostile mobs.",
               effect(mobs(5), "mining_fatigue", 200), 3600),
        "partial", "Enemy players within five blocks are omitted pending ally filtering")
    add("star", 5, "Haunt",
        active("Haunt", "Secondary key blinds the nearest hostile mob within six blocks for 60t.",
               effect(mobs(6, nearest=True), "blindness", 60), 900),
        "partial", "Source also targets enemy players; only tagged hostile mobs are selectable")
    add("star", 1, "Misfortune",
        active("Misfortune", "Primary key cripples nearby hostile mobs for 160t.",
               combined(effect(mobs(10), "weakness", 160, 1),
                        effect(mobs(10), "slowness", 160, 1),
                        effect(mobs(10), "blindness", 60)), 1800, primary=True),
        "partial", "Enemy players are omitted; hostile mobs receive all three Rev2 debuffs")
    add("empress", 1, "Petrifying Gaze",
        active("Petrifying Gaze", "Sneak + secondary key slows nearby hostile mobs.",
               effect(mobs(6), "slowness", 60, 1), 1200, crouch=True),
        "partial", "Missing 60-tick sneak charge and enemy-player targeting; Slowness II on hostile mobs is real")
    # Fixed vanilla commands remove common positive effects without changing
    # terrain or executing any player-supplied command. Modded status effects
    # are outside the enumerated set and remain a documented limitation.
    good_effects = (
        "speed", "strength", "haste", "regeneration", "resistance",
        "fire_resistance", "water_breathing", "invisibility",
        "night_vision", "absorption", "jump_boost", "luck", "saturation",
        "conduit_power", "dolphins_grace", "hero_of_the_village",
    )
    clearing = [cmd("execute at @s run effect clear "
                    f"{mobs(8)} minecraft:{name}") for name in good_effects]
    add("emperor", 1, "Abolish",
        active("Abolish", "Primary key dispels standard boons and weakens hostile mobs within eight blocks.",
               combined(*(clearing + [
                   effect(mobs(8), "slowness", 100, 1),
                   effect(mobs(8), "weakness", 100)])), 1800, primary=True),
        "partial", "Only 16 vanilla positive effects are cleared; modded effects and enemy players are not included")
    add("star", 8, "Lullaby",
        active("Lullaby", "Crouch + secondary key slows hostile mobs within five blocks.",
               effect(mobs(5), "slowness", 60), 1200, crouch=True),
        "partial", "Requires 60-tick crouch charge and enemy-player targeting; action currently fires immediately")
    add("fool", 5, "Puppet String",
        active("Puppet String", "While crouched, secondary key slows nearest hostile mob within eight blocks.",
               effect(mobs(8, nearest=True), "slowness", 80, 1), 400, crouch=True),
        "partial", "Missing player coordinates/no-sprinting effects, next mob attack damage, and safe enemy-player targeting")
    add("fool", 4, "Trickster's Escape",
        periodic("Trickster's Escape", "Below 8 HP, periodically gain Speed II 60t.",
                 apply("speed", 60, 1), 600,
                 condition={"type":"origins:health","comparison":"<","compare_to":8}),
        "partial", "Original checks every 20t with a 600t cooldown and spawns decoy; periodic fallback lacks decoy and can delay activation")
    add("fool", 1, "Paper Figurine Substitute",
        power("Paper Figurine Substitute",
              "25% chance when a hostile mob hits to gain Speed II for 40t, with 6000t cooldown.",
              "origins:self_action_when_hit", cooldown=6000,
              damage_condition={"type":"origins:attacker",
                                "entity_condition":{"type":"origins:in_tag","tag":"tarot:hostile"}},
              entity_action={"type":"origins:chance","chance":0.25,
                             "action":apply("speed",40,1)}),
        "partial", "Decoy armor stand is not created; enemy-player hits intentionally excluded; no lethal damage cancellation")
    add("hanged_man", 6, "Flesh Creek",
        power("Flesh Creek", "20% chance when damaged to heal four health points.",
              "origins:self_action_when_hit", cooldown=1,
              entity_action={"type":"origins:chance","chance":0.20,
                             "action":{"type":"origins:heal","amount":4}}),
        "partial", "Rev2 marks heal as non-Sin; this implementation cannot prevent counting it toward scripted Sin resource")
    add("hanged_man", 2, "Profane Aura",
        compound("Profane Aura",
                 retaliation={"type":"origins:attacker_action_when_hit",
                              "cooldown":100,
                              "damage_condition":{"type":"origins:attacker",
                                                  "entity_condition":{"type":"origins:in_tag","tag":"tarot:hostile"}},
                              "entity_action":{"type":"origins:chance","chance":0.10,
                                               "action":apply("weakness",60)}},
                 kill_pulse={"type":"origins:self_action_on_kill",
                             "cooldown":100,
                             "entity_action":effect(mobs(5), "slowness", 40)}),
        "partial", "Enemy-player retaliation omitted; kill pulse targets tagged hostiles only, not all nearby entities")
    add("devil", 6, "Devil's Mark",
        single_target_use("Devil's Mark", "Right-click hostile mob to apply Wither I 40t.",
                          "hostile", "wither", 40),
        "partial", "Enemy-player targets omitted; vanilla 1.4.1 action_on_entity_use lacks built-in 400t cooldown")
    add("hermit", 7, "Hex",
        single_target_use("Hex", "Right-click hostile mob to apply Weakness I for 60t.",
                          "hostile", "weakness", 60),
        "partial", "Enemy-player targets omitted; exact 600t cooldown requires separate resource and is not enforced")
    add("judgement", 7, "Question",
        single_target_use("Question", "Crouch-right-click a hostile mob for Weakness I 60t.",
                          "hostile", "weakness", 60, crouch=True),
        "partial", "Enemy-player targets omitted; exact 400t cooldown is not enforced by this 1.4.1 power type")
