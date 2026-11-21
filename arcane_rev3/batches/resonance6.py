"""Resonance wave 6: twelve remaining source slots, real but PARTIAL substitutes.

Owner approved bounded datapack substitutions for unsupported scripted Sin,
entity AI, contracts, portals, phasing callbacks and clairvoyance. Each
substitute has observable effects and discloses every lost core mechanism.
None makes the Sequence 1 ritual automatically playable or game-verified.
"""
from ..powers import power, apply, mod, compound
from ..team_policy import enemy_effect, ally_effect
from .shared import active, periodic, combined, effect, mobs, cmd
from .rescue import save
from .resonance4 import pulse


def timed_decoy(offset, seconds=10):
    """Two harmless particle decoys: automatically expired cloud entities.

    No permanent armor stands, mob AI, loot/scoreboard mutation or world edits.
    A fixed, small count and Origins key cooldown prevent entity buildup.
    """
    if offset not in (-1, 1) or seconds != 10:
        raise ValueError("Only bounded two-cloud decoys are allowed")
    return cmd(
        f'execute at @s positioned ^{offset} ^ ^ run summon minecraft:area_effect_cloud ~ ~ ~ '
        '{Duration:200,WaitTime:0,Radius:0.05f,Particle:"minecraft:smoke",Tags:["tarot_arcane_decoy"]}'
    )


def register(add):
    add("paper_martyr", 5, "Gathering of Martyrs",
        active("Gathering of Martyrs",
               "Secondary: two 200t smoke decoys and short hostile debuffs.",
               combined(timed_decoy(-1), timed_decoy(1),
                        effect(mobs(3), "weakness", 100),
                        enemy_effect("weakness", 100, 3)), 6000),
        "partial", "Two temporary visual clouds replace independent 4HP, 1-damage AI figurines; no Sin storage, death-triggered 4-damage detonation, hostile pursuit or entity-targeted minion AI")
    add("paper_martyr", 4, "Burdened Trickster",
        power("Burdened Trickster", "When hit, temporarily gain Absorption II.",
              "origins:self_action_when_hit", cooldown=1200,
              entity_action=apply("absorption", 100, 1)),
        "partial", "Absorption II is a defensive substitute for the source's Sin cap 12HP and 2-Sin-per-decoy/detonation; no persistent shared Sin or upgraded decoy mechanics")
    add("paper_martyr", 2, "Sacrificial Gathering",
        active("Sacrificial Gathering",
               "Secondary: two timed decoys and immediate mob-only impact.",
               combined(timed_decoy(-1), timed_decoy(1),
                        pulse(4, 4),
                        enemy_effect("slowness", 100, 4)),
               6000),
        "partial", "No independent figurine AI, 3-Sin payload, delayed detonation for exactly 6 damage, or enemy-player direct damage; safe immediate 4-damage hostile-mob pulse and opponent slow")
    add("paper_martyr", 1, "Martyr's Substitute",
        save("Martyr's Substitute", "a_cd_martyr", 7200, 20, 12,
             speed=2, invisible=True,
             target_action=effect(mobs(10), "weakness", 100)),
        "partial", "Bounded 7200-online-tick lethal save, safe nearby teleport, 20HP heal, 60t invisibility and Speed II; NO stored Sin shadow, post-shadow explosion or 3 added Sin. Needs actual in-game cancellation/teleport test")
    add("marked_verdict", 1, "Swift Judgment",
        save("Swift Judgment", "a_cd_swift", 9600, 4, 8,
             target_action=effect(mobs(8, nearest=True), "slowness", 40, 4)),
        "partial", "Once per 9600 online ticks, prevent death and relocate within safe radius; freezes nearest tagged hostile instead of the precise attacking enemy player; no true damage-source binding")
    add("crumbling_reaper", 5, "Gate Collapse",
        active("Gate Collapse",
               "Secondary: safe short-range escape and Fire Resistance.",
               combined({"type": "origins:random_teleport",
                         "area_width": 6, "area_height": 3,
                         "attempts": 20, "loaded_chunks_only": True},
                        apply("fire_resistance", 100)), 12000),
        "partial", "Safe mobility replacement rather than a Nether portal or 3x3 terrain break; no block edits, permanent structure or cross-dimension transfer")
    lucky = {"type": "origins:status_effect", "effect": "minecraft:luck"}
    add("crumbling_reaper", 4, "Falling Harvest",
        compound("Falling Harvest",
            prepare={"type": "origins:action_on_land",
                     "condition": {"type": "origins:fall_distance",
                                   "comparison": ">=", "compare_to": 3},
                     "entity_action": apply("luck", 200)},
            consume={"type": "origins:self_action_on_kill",
                     "cooldown": 200, "condition": lucky,
                     "entity_action": combined(
                         {"type": "origins:heal", "amount": 8},
                         pulse(3, 2),
                         {"type": "origins:clear_effect",
                          "effect": "minecraft:luck"})}),
        "partial", "Fall from 3+ blocks arms a 200t Luck marker; caster's next kill heals 4 hearts and pulses two mob-only damage; no enemy-player AoE, mark can be overwritten by unrelated Luck and cooldown starts on kill")
    add("impossible_fist", 4, "Doorstep Punch",
        power("Doorstep Punch",
              "While under Speed, deal 15% more outgoing damage.",
              "origins:modify_damage_dealt",
              condition={"type": "origins:status_effect",
                         "effect": "minecraft:speed"},
              modifier=mod(0.15)),
        "partial", "Speed is a conservative teleport-momentum proxy, not an exact post-teleport one-hit window; bonus also applies to non-melee damage while Speed is active")
    add("impossible_fist", 2, "Giant's Shortcut",
        active("Giant's Shortcut",
               "Primary: two damage to nearby tagged hostiles and opponent Slow.",
               combined(pulse(2, 2),
                        enemy_effect("slowness", 40, 2)),
               2400, primary=True),
        "partial", "Manual shockwave replaces phase-exit callback and exact 20% CURRENT health damage; opponent players get only Slowness, not damage")
    shield = {"type": "origins:or", "conditions": [
        {"type": "origins:equipped_item", "equipment_slot": slot,
         "item_condition": {"type": "origins:ingredient",
                            "ingredient": {"item": "minecraft:shield"}}}
        for slot in ("mainhand", "offhand")]}
    add("benevolent_crown", 3, "Shared Domain",
        periodic("Shared Domain",
                 "Holding shield: regenerate self and listed same-team allies nearby.",
                 combined(apply("regeneration", 100),
                          ally_effect("regeneration", 100, 5)),
                 100, condition=shield),
        "partial", "Shield posture substitutes for standing in persistent Corrupt Ground; no region ownership, enemy exclusion wall, or regeneration for unlisted players")
    add("binding_contract", 2, "Contract Enforcement",
        active("Contract Enforcement",
               "Secondary: a consensual-free self buff and hostile control burst.",
               combined(apply("resistance", 200),
                        effect(mobs(6), "weakness", 200, 1),
                        enemy_effect("weakness", 200, 6, 1)), 3600),
        "partial", "No forced player dialogue, acceptance/refusal, equipment/item drops or inventory mutation; a 3600t self-defense/hostile-weakening substitute with team-only PvP")
    add("loaded_dice", 1, "Loaded Answer",
        active("Loaded Answer",
               "Primary: 200t Luck II and highlight nearest tagged hostile.",
               combined(apply("luck", 200, 1),
                        effect(mobs(10,nearest=True), "glowing", 100)),
               12000, primary=True),
        "partial", "Luck II / Glowing is a safe 12000t fate-reading substitute, not three typed yes/no event predicates or fate-changing guarantees; no enemy-player detection")
