"""Resonance wave 4: concrete source-backed subsets of 29 missing pair powers.

The authoritative 434-entry catalog is in arcane/catalog.json. A power here
is not a complete Resonance kit or a promise that a player can unlock Seq1:
every non-faithful conversion is explicitly PARTIAL with exact missing
mechanics. We do not target same-team players or run mod commands that have
not been checked for the installed 1.18.2 mod versions.
"""
from ..powers import apply, compound, mod, power
from .shared import active, combined, effect, mobs, periodic


HOSTILE = {"type": "origins:in_tag", "tag": "tarot:hostile"}
FALL = {"type": "origins:name", "name": "fall"}


def hit(name, action, cooldown=400):
    return power(name, "On a melee hit against a tagged hostile mob.", 
                 "origins:target_action_on_hit", cooldown=cooldown,
                 target_condition=HOSTILE, entity_action=action)


def pulse(radius, amount):
    """Native area effect restricted to tagged hostile mobs, never allies."""
    return {
        "type": "origins:area_of_effect", "radius": radius,
        "bientity_condition": {
            "type": "origins:target_condition", "condition": HOSTILE},
        "bientity_action": {
            "type": "origins:target_action",
            "action": {"type": "origins:damage", "amount": amount,
                       "source": {"name": "generic"}}}
    }


def cap(name, cooldown, duration, *actions):
    """One-shot activation of source effects. Does not emulate timed auras."""
    return active(name, "Primary-key source-backed temporary capstone preview.",
                  combined(*actions), cooldown, primary=True)


def register(add):
    # Fool + Hanged Man. Sin transfer and decoys need persistent shared Sin state.
    add("paper_martyr", 7, "Suffering Sight",
        active("Suffering Sight", "Reveal tagged hostile mobs within 10 blocks.",
               effect(mobs(10), "glowing", 100), 200, crouch=True),
        "partial", "Reveals mobs with Glowing rather than health/debuff readout; no 2-Sin transfer, damage or safe enemy-player targeting")
    add("paper_martyr", 3, "Suffering Sight II",
        active("Suffering Sight II", "Highlight the nearest hostile mob for 60 ticks.",
               effect(mobs(10, nearest=True), "glowing", 60), 200, crouch=True),
        "partial", "Glowing 60t is real; no 3-Sin transfer, player health/debuff display or enemy-player targeting")
    add("paper_martyr", 0, "The Paper Martyr",
        cap("The Paper Martyr", 18000, 700,
            apply("resistance", 700, 2),
            apply("strength", 700, 1),
            apply("fire_resistance", 700),
            effect(mobs(8), "weakness", 80)),
        "partial", "Resistance III approximates rather than equals 75% reduction; no flight, fall immunity, Sin conversion, decoys, damage nova, end teleport/heal, explosion or minion revival; 12000t low-HP cooldown not implemented")

    # World + Justice. The marked-player subsystem is not spoofed.
    add("marked_verdict", 2, "The Verdict",
        power("The Verdict", "Own kills give Absorption I and slow nearby hostile mobs.",
              "origins:self_action_on_kill", cooldown=1,
              entity_action=combined(apply("absorption", 600),
                                     effect(mobs(8), "slowness", 60))),
        "partial", "Requires a Marked Prey kill; Slowness does not pacify AI and enemy players excluded")
    add("marked_verdict", 0, "The Marked Verdict",
        cap("The Marked Verdict", 24000, 900,
            apply("strength", 900, 1),
            apply("speed", 900),
            effect(mobs(15), "slowness", 100, 1)),
        "partial", "Cannot mark a player within 50 blocks, prevent sprint/jump, auto-hit projectiles, freeze target or award team buffs on marked kills; Strength is not exact +100% damage")

    # Hermit + Chariot. The book-read trigger and stack resource are missing.
    condition_book_sprint = {"type": "origins:and", "conditions": [
        {"type": "origins:sprinting"},
        {"type": "origins:equipped_item", "equipment_slot": "offhand",
         "item_condition": {"type": "origins:ingredient",
                            "ingredient": {"tag": "tarot:books"}}}]}
    add("burning_archive", 4, "Scholar's Momentum",
        power("Scholar's Momentum", "Deal 25% more damage while sprinting with a book in offhand.",
              "origins:modify_damage_dealt",
              condition=condition_book_sprint,
              modifier=mod(0.25)),
        "partial", "The source requires a book read in the last 1200 ticks and sprint MELEE damage only; this uses equipped offhand book and may also modify non-melee damage")
    add("burning_archive", 0, "The Burning Archive",
        cap("The Burning Archive", 24000, 900,
            apply("strength", 900, 1),
            apply("speed", 900),
            effect(mobs(20), "glowing", 300)),
        "partial", "No 100-block player outlines/structure scan, armor-ignoring arrow, forced hostile-vs-hostile AI, precise +30% damage/+20% speed, ignite-on-hit, Burn stacks or end blast")

    # Death + Tower. Only caster kills are observable with native kill powers.
    add("crumbling_reaper", 3, "Collapse of the Living",
        power("Collapse of the Living", "Killing a mob pulses one damage to tagged hostile mobs nearby.",
              "origins:self_action_on_kill", cooldown=1,
              entity_action=pulse(3, 1)),
        "partial", "Source triggers on ANY enemy death within eight blocks; this triggers only on caster kills, without terrain cracks or enemy players")
    add("crumbling_reaper", 2, "Unstable Souls",
        compound("Unstable Souls",
            fall_retribution={
                "type": "origins:self_action_when_hit", "cooldown": 1,
                "damage_condition": FALL, "entity_action": pulse(3, 2)},
            soul_heal={
                "type": "origins:self_action_on_kill",
                "entity_action": {"type": "origins:heal", "amount": 2}}),
        "partial", "Fixed 2 damage rather than reflecting exact fall damage and no enemy-player reflection; heals on caster kills rather than full Soul Harvest rules")
    add("crumbling_reaper", 1, "Falling Tower's Reap",
        power("Falling Tower's Reap", "Kills grant Absorption I for 600 ticks.",
              "origins:self_action_on_kill", cooldown=1,
              entity_action=apply("absorption", 600)),
        "partial", "No slam linkage or execution threshold below 20% HP; Absorption I is not a stacking +1 resource")
    add("crumbling_reaper", 0, "The Crumbling Reaper",
        cap("The Crumbling Reaper", 24000, 600,
            apply("absorption", 600, 2),
            effect(mobs(15), "slowness", 600, 1),
            effect(mobs(10), "wither", 100)),
        "partial", "Cannot select/kill lowest-health targets every 60t or impose proper boss/player caps; no unstable ground, periodic 4 damage/sec, absorption-per-kill or persistent stack cap")

    # Magician + Strength: safe hostile-only knockdown, no through-wall reach.
    add("impossible_fist", 3, "Sealed Slam",
        hit("Sealed Slam",
            combined({"type": "origins:damage", "amount": 4,
                      "source": {"name": "generic"}},
                     apply("slowness", 60, 1)), 400),
        "partial", "A melee fallback rather than only teleport-arrival impact; no forced 3-block knockback or enemy-player damage; 400t guard is a conservative fallback without source cooldown")
    add("impossible_fist", 1, "Divine Door",
        active("Divine Door", "Primary key slows nearby hostile mobs and boosts self briefly.",
               combined(effect(mobs(15), "slowness", 60, 3),
                        apply("strength", 60, 1)), 1800, primary=True),
        "partial", "No Divine Hand pull or teleport choice, one-target 60t hard stun, exact +50% next-melee consumption or enemy-player targeting")
    add("impossible_fist", 0, "The Impossible Fist",
        cap("The Impossible Fist", 18000, 900,
            apply("strength", 900, 1),
            effect(mobs(15), "wither", 100, 1),
            effect(mobs(15), "slowness", 100, 1)),
        "partial", "Unrestricted phasing, halved armor, exact +30% damage, momentum stacks, through-wall melee and end shockwave omitted; initial debuffs target mobs only")

    # Emperor + Lovers: always self-only until server-trusted same-team allies.
    add("benevolent_crown", 2, "Emperor's Hymn",
        active("Emperor's Hymn", "Secondary key regenerates and speeds self, and slows tagged hostiles.",
               combined(apply("regeneration", 200),
                        apply("speed", 200),
                        effect(mobs(6), "slowness", 100)), 900),
        "partial", "No ally Regeneration/speed, exact 10% resistance or mob target reset; self-only support avoids healing enemies")
    add("benevolent_crown", 1, "Triage Decree",
        active("Triage Decree", "Secondary key heals self and slows nearest hostile mob.",
               combined({"type": "origins:heal", "amount": 2},
                        effect(mobs(6, nearest=True), "slowness", 60)), 400),
        "partial", "Does not combine team-aware Triage or inflict exact two damage on closest enemy; no enemy players")
    add("benevolent_crown", 0, "The Benevolent Crown",
        cap("The Benevolent Crown", 18000, 1200,
            apply("resistance", 1200),
            apply("regeneration", 1200, 1),
            effect(mobs(15), "slowness", 100)),
        "partial", "No persistent 15-block domain, ally regeneration and speed, sprint/jump whitelist, consort, passive invulnerability, death healing or exact +20% damage and resistance")

    # Devil + Judgement. No coerced player contracts or unintended item drops.
    add("binding_contract", 1, "Chaos Law",
        active("Chaos Law", "Primary key slows and weakens nearby hostile mobs for 160 ticks.",
               combined(effect(mobs(10), "slowness", 160, 1),
                        effect(mobs(10), "weakness", 160),
                        apply("resistance", 160)), 1800, primary=True),
        "partial", "No temporally gated 1-damage/Slowness retaliation against actual attackers; enemy players omitted")
    add("binding_contract", 0, "The Binding Contract",
        cap("The Binding Contract", 18000, 800,
            apply("strength", 800, 1),
            apply("fire_resistance", 800),
            apply("speed", 800),
            effect(mobs(15), "wither", 100, 1)),
        "partial", "No exact +20% speed, melee lifesteal/Wither, contract offers, freeze, minions, on-kill Absorption, +15% damage vulnerability or end Hunger; enemy players withheld")

    # Star + Empress. No unverified world-light mutation or unguarded PvP.
    add("starless_poison", 1, "Midnight Apocalypse",
        active("Midnight Apocalypse", "Primary blinds and poisons nearby tagged hostiles.",
               combined(effect(mobs(15), "blindness", 60),
                        effect(mobs(15), "poison", 60, 1)), 3600,
               primary=True),
        "partial", "No meteor strikes, light extinction or distinct poison-on-hit logic; enemy players excluded")
    add("starless_poison", 0, "The Starless Poison",
        cap("The Starless Poison", 24000, 800,
            apply("invisibility", 800),
            apply("speed", 800, 1),
            effect(mobs(30), "blindness", 60),
            effect(mobs(30), "poison", 100, 1)),
        "partial", "No 30-block world darkness, exact +20% damage, 60t repeating poison, poisoned bonus, attack visibility interruption, death cloud or end pulse; initial mob-only debuff")

    # Sun + Moon; do not indiscriminately grant healing to enemy players.
    add("eclipse", 0, "The Eclipse",
        cap("The Eclipse", 24000, 1200,
            apply("regeneration", 1200),
            effect(mobs(30, "undead"), "wither", 300, 1)),
        "partial", "Missing fixed 30-block sun field, moving 15-block moon aura, exact damage/healing drains, enemy-player rules, double loot and final pulse")

    # Temperance + Hierophant. Source effects restricted to tagged undead.
    still = {"type": "origins:sprinting", "inverted": True}
    add("walking_sanctuary", 4, "Consecrated Walk",
        periodic("Consecrated Walk", "While not sprinting, periodically weaken undead within three blocks.",
                 effect(mobs(3, "undead"), "wither", 60), 100,
                 condition=still),
        "partial", "Standing still for 100t is approximated by not sprinting; no persistent sanctified light zone or exact 1 damage/sec")
    add("walking_sanctuary", 2, "Mobile Sanctum",
        active("Mobile Sanctum", "Secondary key regenerates self and withers nearby undead.",
               combined(apply("regeneration", 200),
                        effect(mobs(3, "undead"), "wither", 200)),
               1200),
        "partial", "No Incorporeal activation coupling, spawn suppression, exact 2 damage/sec or same-team-only player healing")
    add("walking_sanctuary", 1, "Spectral White Angel",
        active("Spectral White Angel", "Primary key regenerates self and weakens undead.",
               combined(apply("regeneration", 300, 1),
                        effect(mobs(15, "undead"), "wither", 300, 1)),
               3600, primary=True),
        "partial", "No 15-block light field, phasing requirement, exact undead 3 damage/sec or ally Regeneration II")
    add("walking_sanctuary", 0, "The Walking Sanctuary",
        cap("The Walking Sanctuary", 24000, 1200,
            apply("regeneration", 1200, 1),
            effect(mobs(15, "undead"), "wither", 300, 1)),
        "partial", "No mobile anti-spawn domain, persistent phasing, ally-only heal, hunger recovery, reaction damage/Blindness when allies attacked or final 3-second enlarged pulse")

    # High Priestess + Wheel: no fabricated questions/inventory disclosures.
    add("loaded_dice", 3, "Prophetic Vision",
        active("Prophetic Vision", "Secondary key reveals nearest hostile mob within 30 blocks.",
               effect(mobs(30, nearest=True), "glowing", 100), 1800),
        "partial", "No Gaze activation coupling, green outline, random marked enemy or three banked positive Fate rolls")
    add("loaded_dice", 2, "Rolled Archive",
        active("Rolled Archive", "Secondary key highlights nearby hostile mobs for 100 ticks.",
               effect(mobs(30), "glowing", 100), 3600),
        "partial", "Does not answer yes/no questions, display target health, show a five-second path or safely target enemy players")
    add("loaded_dice", 0, "The Loaded Dice",
        cap("The Loaded Dice", 24000, 600,
            apply("luck", 1200, 2),
            effect(mobs(100), "glowing", 300)),
        "partial", "Luck III happens immediately instead of only if question is unused at end; no inventories, structure/ore/players scan, three yes/no questions, reroll-best-of-three, guaranteed criticals or consumed fate-changing question")
