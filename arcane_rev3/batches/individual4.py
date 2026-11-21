"""Third Rev2 individual ability batch: native, conservative, team-safe effects.

The handbook remains the source of names and mechanics. A partial record
must state what is omitted, especially enemy players, timing or ally logic.
No command accepts player-controlled input, modifies SMP worlds, or uses
KubeJS. No power is claimed to have passed real 1.18.2 runtime acceptance.
"""
from ..powers import power, apply, mod
from .shared import active, periodic, effect, mobs, combined
from .resonance import night


HOSTILE = {"type": "origins:in_tag", "tag": "tarot:hostile"}
UNDEAD = {"type": "origins:in_tag", "tag": "tarot:undead"}
FALL = {"type": "origins:name", "name": "fall"}


def hostile_area_damage(radius, amount):
    """Only tagged hostile mobs; 1.18.2 Origins bi-entity damage, not /damage."""
    return {
        "type": "origins:area_of_effect", "radius": radius,
        "bientity_condition": {
            "type": "origins:target_condition", "condition": HOSTILE},
        "bientity_action": {
            "type": "origins:target_action",
            "action": {"type": "origins:damage", "amount": amount,
                       "source": {"name": "generic"}}},
    }


def fate_roll(positive_only=False):
    names = ("speed", "haste", "absorption") if positive_only else (
        "speed", "haste", "absorption", "hunger", "slowness",
        "mining_fatigue")
    return {"type": "origins:choice", "actions": [
        {"weight": 1, "element": apply(x, 200)} for x in names]}


def register(add):
    add("strength", 7, "Master's Grip",
        power("Master's Grip", "Projectile damage is reduced 25%.",
              "origins:modify_projectile_damage", modifier=mod(-0.25)),
        "partial", "Source concerns bows only; this also affects other projectiles and does not bypass a separate bow-use restriction")
    add("temperance", 9, "Mirror Passage",
        power("Mirror Passage", "Sneak with empty chest in low light to phase through leaves and cobwebs.",
              "origins:phasing", render_type="blindness",
              block_condition={"type": "origins:or", "conditions": [
                  {"type": "origins:in_tag", "tag": "minecraft:leaves"},
                  {"type": "origins:block", "block": "minecraft:cobweb"}]},
              condition={"type": "origins:and", "conditions": [
                  {"type": "origins:sneaking"},
                  {"type": "origins:brightness", "comparison": "<=",
                   "compare_to": 0.267},
                  {"type": "origins:equipped_item", "equipment_slot": "chest",
                   "item_condition": {"type": "origins:empty"}}]}),
        "partial", "Brightness threshold approximates light level 4 and may depend on ambient lighting; phasing collision requires game verification")
    add("temperance", 7, "Beast Form",
        active("Beast Form", "Secondary key grants a 200t attack buff.",
               apply("strength", 200), 1200, crouch=True),
        "partial", "Strength I adds 3 melee points, rather than exactly 2; source crouch-right-click with empty hands is not implemented")
    add("temperance", 1, "Abomination",
        active("Abomination", "Primary key: 300t Resistance I and Slowness III.",
               combined(apply("resistance", 300),
                        apply("slowness", 300, 2)), 2400, primary=True),
        "partial", "Exact +6 armor, 30% damage resistance, half speed and extended Wraith's Veil are absent; potion levels approximate combat/movement tradeoff")
    add("wheel_of_fortune", 8, "Clockwork",
        power("Clockwork", "10% on being hit: immediately roll Fate's six boons/curses.",
              "origins:self_action_when_hit", cooldown=1,
              entity_action={"type": "origins:chance", "chance": 0.10,
                             "action": fate_roll()}),
        "partial", "An immediate six-way roll does not reset the existing 1800t Fate's Current timer")
    add("wheel_of_fortune", 5, "Winning Streak",
        power("Winning Streak", "A kill immediately grants a random positive Fate boon.",
              "origins:self_action_on_kill", cooldown=1,
              entity_action=fate_roll(positive_only=True)),
        "partial", "Source banks a guaranteed positive result for the NEXT Fate's Current; this triggers immediately instead")
    add("wheel_of_fortune", 3, "Chaos Step",
        power("Chaos Step", "On fall damage, 20% chance to teleport to a safe nearby block.",
              "origins:self_action_when_hit", cooldown=1,
              damage_condition=FALL,
              entity_action={"type": "origins:chance", "chance": 0.20,
                             "action": {"type": "origins:random_teleport",
                                        "area_width": 3,
                                        "area_height": 2,
                                        "attempts": 12,
                                        "loaded_chunks_only": True}}),
        "partial", "The random safe landing may change height up to 2 blocks and isn't a guaranteed horizontal 3-block dodge")
    add("emperor", 6, "Corrupt Ground",
        active("Corrupt Ground", "Sneak + secondary slows nearby hostile mobs.",
               effect(mobs(4), "slowness", 100), 1200, crouch=True),
        "partial", "Does not place a persistent 5x5 600t terrain zone; enemy-player targeting and right-click-on-ground trigger omitted")
    add("sun", 1, "White Angel",
        active("White Angel", "Primary key regenerates self and withers undead in 15 blocks.",
               combined(apply("regeneration", 300),
                        effect(mobs(15, "undead"), "wither", 300, 1)),
               3600, primary=True),
        "partial", "No 15-block light field or exact 4 damage/sec; other same-team allies are not healed")
    add("judgement", 9, "Verdict's Weight",
        power("Verdict's Weight", "10% chance on kill to slow nearby tagged hostiles.",
              "origins:self_action_on_kill", cooldown=1,
              entity_action={"type": "origins:chance", "chance": 0.10,
                             "action": effect(mobs(4), "slowness", 40)}),
        "partial", "Slowness I 40t does not force hostile mobs to flee; enemy players omitted")
    add("judgement", 1, "Order",
        active("Order", "Primary key: Slowness II and Weakness II 160t to nearby hostile mobs.",
               combined(effect(mobs(8), "slowness", 160, 1),
                        effect(mobs(8), "weakness", 160, 1)),
               1800, primary=True),
        "partial", "Cannot include enemy players without teammate exclusion; next melee stun 40t not implemented")
    add("devil", 1, "Chaos Unleashed",
        active("Chaos Unleashed", "Primary key: Slowness II and Weakness I 160t to hostile mobs.",
               combined(effect(mobs(10), "slowness", 160, 1),
                        effect(mobs(10), "weakness", 160)),
               1800, primary=True),
        "partial", "Next-hit +50% and Wither II effects omitted; enemy players excluded for team safety")
    add("tower", 3, "Shockwave",
        power("Shockwave", "Land from 4+ blocks to deal two damage to nearby hostile mobs.",
              "origins:action_on_land",
              condition={"type": "origins:fall_distance",
                         "comparison": ">=", "compare_to": 4},
              entity_action=hostile_area_damage(3, 2)),
        "partial", "Uses cube-shaped native area rather than exact sphere and excludes enemy players until team comparison is verified")
    add("chariot", 1, "Meteor",
        active("Meteor", "Primary key ignites hostile mobs within three blocks and grants brief fire resistance.",
               combined(effect(mobs(3), "wither", 100),
                        apply("fire_resistance", 100)), 2400, primary=True),
        "partial", "Wither is a non-identical damage-over-time fallback; 15-block dash, path ignition, invulnerability and enemy-player targeting absent")
    add("lovers", 0, "The Garden",
        active("The Garden", "Primary key heals and speeds self while slowing nearby hostile mobs for 90s.",
               combined(apply("regeneration", 1800, 1),
                        apply("speed", 1800),
                        effect(mobs(15), "slowness", 1800)),
               24000, primary=True),
        "partial", "Ally-only 15-block Regeneration II and +10% speed, true mob pacification, passive immortality and enemy players are not implemented; individual Seq0 not player-granted in Rev3")
    add("hermit", 5, "Star Read",
        active("Star Read", "Secondary key at night makes hostile mobs within 15 blocks glow.",
               effect(mobs(15), "glowing", 100), 1200),
        "partial", "The key is not night-locked, and health/name readout and safe enemy-player targeting are absent")
    add("star", 3, "Terror",
        periodic("Terror", "At night, occasionally slow hostile mobs within five blocks.",
                 {"type": "origins:chance", "chance": 0.10,
                  "action": effect(mobs(5), "slowness", 40)}, 40,
                 condition=night()),
        "partial", "Slowness does not force AI fleeing and enemy players are omitted; chance repeats every 40t rather than on entry")
    add("high_priestess", 1, "All-Knowing Gaze",
        active("All-Knowing Gaze", "Primary key grants 300t Glowing to entities within 30 blocks.",
               effect("@e[distance=..30]", "glowing", 300), 1800,
               primary=True),
        "partial", "No health-bar overlay, directional info or one-shot +50% next attack; no scripted target information")
    near_player = {"type": "origins:command",
                   "command": "execute at @s if entity @a[distance=0.01..8]",
                   "comparison": ">=", "compare_to": 1}
    add("lovers", 9, "Shared Refuge",
        periodic("Shared Refuge", "Self gains Resistance I 40t every 600t near another player.",
                 apply("resistance", 40), 600, condition=near_player),
        "partial", "Checks any nearby player rather than same-team ally; buff applies only to self")
