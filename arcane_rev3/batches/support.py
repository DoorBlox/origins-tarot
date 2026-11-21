"""Rev2 bulk batch A: 14 healing, sensing and fixed identity effects."""
from ..powers import power, apply, mod, compound
from .shared import active, periodic, effect, mobs, players, combined, cmd


def register(add):
    add("high_priestess", 5, "Ritual Circle",
        active("Ritual Circle", "Secondary key heals all players within three blocks for 100t.",
               effect(players(3), "regeneration", 100), 900),
        "partial", "Required persistent 3-block ritual marker is not created; player targeting and Regeneration duration are implemented")
    add("hierophant", 9, "Quiet Benediction",
        periodic("Quiet Benediction", "Regeneration I 80t to players within eight blocks every 800t.",
                 effect(players(8), "regeneration", 80), 800))
    add("hierophant", 5, "Hymn",
        active("Hymn", "Secondary key gives players within eight blocks Regeneration I for 100t.",
               effect(players(8), "regeneration", 100), 1200))
    add("justice", 9, "Therapist's Presence",
        periodic("Therapist's Presence", "Players within six blocks receive Regeneration I 80t every 900t.",
                 effect(players(6), "regeneration", 80), 900))
    add("chariot", 3, "Rally",
        power("Rally", "On kill give players within eight blocks Speed I 100t; 600t cooldown.",
              "origins:self_action_on_kill", cooldown=600,
              entity_action=effect(players(8), "speed", 100)))
    add("justice", 3, "Shared Dream",
        active("Shared Dream", "Crouch + secondary grants Night Vision to players within eight blocks for 200t.",
               effect(players(8), "night_vision", 200), 1200, crouch=True),
        "partial", "Requires 60 consecutive crouching ticks before activation; current active key works immediately")
    add("death", 7, "Spirit Sense",
        active("Spirit Sense", "Crouch + secondary reveals undead mobs in ten blocks for 100t.",
               effect(mobs(10, "undead"), "glowing", 100), 600, crouch=True),
        "partial", "Rev2 requires charging while crouched for 60t, not merely crouching at activation")
    add("star", 7, "Nightmare",
        power("Nightmare", "At night, 20% chance on kill to earn one experience point.",
              "origins:self_action_on_kill",
              condition={"type": "origins:daytime", "inverted": True},
              entity_action={"type": "origins:chance", "chance": 0.20,
                             "action": cmd("experience add @s 1 points")}))
    add("moon", 1, "Beauty",
        active("Beauty", "Primary key heals self and slows nearby hostile mobs.",
               combined(effect(mobs(10), "slowness", 160),
                        apply("regeneration", 200)), 2400, primary=True),
        "partial", "Cannot clear mob AI aggro or pacify enemy players; same-team ally healing is not implemented")
    add("hierophant", 1, "White Angel",
        active("White Angel", "Primary key grants self Regeneration II and withers undead nearby.",
               combined(effect(mobs(15, "undead"), "wither", 300),
                        apply("regeneration", 300, 1)), 3600, primary=True),
        "partial", "No temporary level-15 light zone; Wither does not equal exact 3 damage/sec, and allies do not receive Regeneration II")
    add("lovers", 1, "Shared Refuge II",
        periodic("Shared Refuge II", "Periodic Resistance I and Regeneration I pulse for 40 ticks.",
                 combined(apply("resistance", 40), apply("regeneration", 40)), 600),
        "partial", "Original does not specify the triggering event or cadence; uses 600t periodic self-only pulse")
    add("death", 1, "Grave Affinity II",
        power("Grave Affinity II", "Reduce incoming damage from undead by 35%.",
              "origins:modify_damage_taken",
              damage_condition={"type": "origins:attacker",
                                "entity_condition": {"type":"origins:in_tag","tag":"tarot:undead"}},
              modifier=mod(-0.35)),
        "partial", "Rev2 upgrades Grave Affinity from 25% to 35%; can stack with the older sequence's damage reduction")
    add("lovers", 3, "Requiem",
        power("Requiem", "Regeneration I after killing a passive mob.",
              "origins:self_action_on_kill",
              bientity_condition={"type":"origins:target_condition",
                                  "condition":{"type":"origins:in_tag","tag":"tarot:passive"}},
              entity_action=apply("regeneration", 60)),
        "partial", "Only detects passive mobs personally killed by the caster, not all deaths of passive mobs within eight blocks")
    alone={"type": "origins:scoreboard", "objective":"a_alone_time",
           "comparison":">", "compare_to":600}
    add("lovers", 9, "Separation Anxiety",
        compound("Separation Anxiety",
                 exhaustion={"type":"origins:modify_exhaustion",
                             "modifier":mod(0.35),"condition":alone},
                 mining={"type":"origins:modify_break_speed",
                         "modifier":mod(-0.15),"condition":alone}),
        "partial", "Alone timer starts after 600t without any nearby players, not only without same-team players; exact team-aware check is unavailable")
