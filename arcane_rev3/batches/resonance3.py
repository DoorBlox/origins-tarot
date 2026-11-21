"""Rev2 Resonance wave 3: twelve executable, source-traced partial powers.

These definitions are intentionally NOT granted by any pair Origin, sequence
transition or slot. The Seq2->Seq1 ritual must remain fail-closed until the
whole 110-ability kit and world/runtime acceptance are complete.
"""
from ..powers import power, apply, mod, compound
from ..team_policy import ally_effect, enemy_effect
from .shared import active, periodic, effect, mobs, combined, cmd
from .resonance import attacked_by, night


HOSTILE = {"type": "origins:in_tag", "tag": "tarot:hostile"}


def roll_positive():
    return {"type": "origins:choice", "actions": [
        {"element": apply(name, 200), "weight": 1}
        for name in ("speed", "haste", "absorption")]}


def register(add):
    add("starless_poison", 3, "Poison Conceal",
        power("Poison Conceal", "While invisible, melee hits poison and reveal hostile mobs.",
              "origins:target_action_on_hit", cooldown=1,
              condition={"type": "origins:invisible"},
              target_condition=HOSTILE,
              entity_action=combined(apply("poison", 80, 1),
                                     apply("glowing", 40))),
        "partial", "Cannot restrict to only the first invisibility attack or preserve invisibility on hit; enemy players omitted")
    add("starless_poison", 2, "Shadow Whisper",
        compound("Shadow Whisper",
            retaliate={"type": "origins:attacker_action_when_hit",
                "cooldown": 1,
                "damage_condition": attacked_by("hostile"),
                "entity_action": combined(apply("blindness", 20),
                                          apply("poison", 40))},
            escape={"type": "origins:self_action_when_hit",
                "cooldown": 1, "damage_condition": attacked_by("hostile"),
                "entity_action": apply("speed", 40)}),
        "partial", "Only triggers after actual hostile-mob hits rather than AI targeting; 2 retaliatory damage and enemy-player targets omitted")
    add("binding_contract", 3, "Law of Hell",
        power("Law of Hell", "Hostile attackers receive Slowness II; those below half health also get Wither I.",
              "origins:attacker_action_when_hit", cooldown=1,
              entity_action=combined(
                  apply("slowness", 40, 1),
                  {"type": "origins:if_else",
                   "condition": {"type": "origins:relative_health",
                                 "comparison": "<", "compare_to": 0.5},
                   "if_action": apply("wither", 60)})),
        "partial", "Source also deals immediate 2 damage; event triggers when hit, not on all attacks and excludes enemy-player retaliation")
    add("burning_archive", 2, "Reaper's Library",
        power("Reaper's Library", "Gain an additional XP point on kills.",
              "origins:self_action_on_kill", cooldown=1,
              entity_action=cmd("experience add @s 1 points")),
        "partial", "Burn stack (+5% melee up to three, consumed on critical) not implemented")
    add("burning_archive", 1, "Burning Lecture",
        power("Burning Lecture", "Melee hits ignite tagged hostile mobs for five seconds.",
              "origins:target_action_on_hit", cooldown=1,
              target_condition=HOSTILE,
              entity_action={"type": "origins:set_on_fire", "duration": 5}),
        "partial", "Requires Emperor's Library activation to enable 100t melee burn; arrow burn 60t, 3600t cooldown and enemy players omitted")
    add("eclipse", 3, "Moonshadow",
        power("Moonshadow", "Gain Night Vision during daylight.",
              "origins:night_vision",
              condition={"type": "origins:daytime"}),
        "partial", "Nighttime five-block through-wall vision not available in this passive")
    lunar = active("Lunar Sanctuary",
        "Secondary key at night gives self a small heal and damages nearby undead over time.",
        combined({"type": "origins:heal", "amount": 2},
                 effect(mobs(10, "undead"), "wither", 100),
                 enemy_effect("wither", 100, 10)), 3600)
    lunar["condition"] = night()
    add("eclipse", 2, "Lunar Sanctuary", lunar, "partial",
        "No persistent 15-block sanctified zone, exact 1-heart-per-40t drain or its proportional self-healing; nightly listed enemy-team Wither is only a timed fallback")
    add("eclipse", 1, "Solar Drain",
        active("Solar Drain", "Primary key self-regenerates and withers undead within 15 blocks.",
               combined(apply("regeneration", 300),
                        effect(mobs(15, "undead"), "wither", 300, 1)),
               3600, primary=True),
        "partial", "Exact 1 HP/sec heal, undead +2 damage/sec, light field and full White Angel coupling omitted")
    add("walking_sanctuary", 7, "Beast Contract",
        active("Beast Contract", "Sneak + secondary grants a 200t melee buff.",
               apply("strength", 200), 1200, crouch=True),
        "partial", "Contract health-visibility link for 12000t missing; Strength I is +3 melee, not exactly +2")
    add("impossible_fist", 7, "Star Chart Grip",
        power("Star Chart Grip", "Projectile damage is reduced by 25%.",
              "origins:modify_projectile_damage", modifier=mod(-0.25)),
        "partial", "Star Chart's structure guidance unavailable; penalty affects non-bow projectiles and does not override item-use restrictions")
    shield = {"type": "origins:or", "conditions": [
        {"type": "origins:equipped_item", "equipment_slot": slot,
         "item_condition": {"type": "origins:ingredient",
                            "ingredient": {"item": "minecraft:shield"}}}
        for slot in ("mainhand", "offhand")]}
    add("benevolent_crown", 4, "Linked Crown",
        compound("Linked Crown",
            protection={"type": "origins:modify_damage_taken",
                        "modifier": mod(-0.05), "condition": shield},
            repair=periodic("Linked Crown Repair",
                            "Heal self 1 HP every 200t while holding a shield.",
                            combined({"type": "origins:heal", "amount": 1},
                                     ally_effect("regeneration", 80, 8)),
                            200, condition=shield)),
        "partial", "Allies within 8 blocks receive bounded Regeneration I every 200t while shield held, not exact +5% damage reduction or half-heart instant heal; unlisted and teamless players remain neutral")
    add("loaded_dice", 6, "Cross-Reference Clockwork",
        power("Cross-Reference Clockwork", "On kill, immediately grant one positive Fate boon.",
              "origins:self_action_on_kill", cooldown=1,
              entity_action=roll_positive()),
        "partial", "Cross-Reference lapis reduction, 10% damage reset and next-Fate positive banking are not implemented")
