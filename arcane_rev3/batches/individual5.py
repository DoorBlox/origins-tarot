"""Rev2 individual wave 5: source-traced partial native gameplay, no fake stubs.

Every approximation is recorded in the 434-entry manifest. The source is the
Rev2 handbook. Hostile AOE never targets players (allied or enemy) until the
actual scoreboard-team comparator is implemented and accepted. No world
mutation or command requiring privileges is exposed to an ordinary user.
"""
from ..powers import apply, compound, mod, power
from .shared import active, combined, cmd, effect, mobs, periodic
from ..team_policy import enemy_effect, ally_effect


HOSTILE = {"type": "origins:in_tag", "tag": "tarot:hostile"}


def area(radius, *actions):
    return {"type": "origins:area_of_effect", "radius": radius,
            "bientity_condition": {"type": "origins:target_condition",
                                   "condition": HOSTILE},
            "bientity_action": {"type": "origins:target_action",
                                "action": combined(*actions)}}


def shield():
    return {"type": "origins:or", "conditions": [
        {"type": "origins:equipped_item", "equipment_slot": slot,
         "item_condition": {"type": "origins:ingredient",
                            "ingredient": {"item": "minecraft:shield"}}}
        for slot in ("mainhand", "offhand")]}


def primary(name, cooldown, *actions):
    return active(name, "Primary-key partial manifestation of this pathway.",
                  combined(*actions), cooldown, primary=True)


def register(add):
    add("fool", 8, "Trickster's Favor",
        power("Trickster's Favor",
              "10% when a hostile hits you: gain Speed II briefly.",
              "origins:self_action_when_hit", cooldown=200,
              damage_condition={"type": "origins:attacker",
                                "entity_condition": HOSTILE},
              entity_action={"type": "origins:chance", "chance": 0.1,
                             "action": apply("speed", 40, 1)}),
        "partial", "No LivingChangeTargetEvent or AI redirection to nearest other target within 6 blocks; no enemy-player acquisition trigger")
    add("magician", 2, "Planar Step",
        active("Planar Step", "Secondary key: safely teleport up to four blocks forward into clear air.",
               cmd("execute at @s positioned ^ ^ ^4 if block ~ ~ ~ minecraft:air "
                   "if block ~ ~1 ~ minecraft:air unless block ~ ~-1 ~ minecraft:air "
                   "run tp @s ~ ~ ~"), 3600),
        "partial", "Requires phasing through up to four solid blocks; direct destination is checked for air and ground, but lacks collision raycast, pitch clamp and source-specific failure messaging")
    add("high_priestess", 0, "The Archive",
        primary("The Archive", 24000,
                effect("@a[distance=..500]", "glowing", 400),
                apply("night_vision", 400)),
        "partial", "Player glow at 500 blocks and self Night Vision only; no inventory inspection, structure/ore scan or three yes/no questions")
    add("empress", 4, "Aura of Despair",
        periodic("Aura of Despair", "10% every 40t: slow tagged hostiles within 5 blocks.",
                 {"type": "origins:chance", "chance": 0.1,
                  "action": effect(mobs(5), "slowness", 40)}, 40),
        "partial", "Slowness does not force hostiles to flee and excludes enemy players; source fear effect is not faithfully approximated")
    add("empress", 1, "Apocalypse's Herald",
        primary("Apocalypse's Herald", 3600,
                area(10, {"type": "origins:damage", "amount": 6,
                          "source": {"name": "generic"}},
                     {"type": "origins:set_on_fire", "duration": 3})),
        "partial", "Single radius-10 pulse instead of five meteor trajectories over 160t; no enemy-player damage, particle meteors, terrain changes or per-impact target selection")
    add("emperor", 2, "Entropy Field",
        active("Entropy Field", "Secondary key grants Resistance I for 100t.",
               apply("resistance", 100), 3600),
        "partial", "Affects all damage types rather than halving projectiles crossing a five-block radius; no persistent area field")
    add("emperor", 0, "The Emperor's Domain",
        primary("The Emperor's Domain", 18000,
                apply("resistance", 1200),
                apply("strength", 1200),
                effect(mobs(15), "slowness", 200, 1)),
        "partial", "No 3-block no-entry enforcement, all-player sprint/jump restrictions, /tarot allow exception list, exact +15% damage and -15% damage taken, enemy-player knockback or persistent domain")
    add("hierophant", 2, "Sanctuary",
        active("Sanctuary", "Secondary key weakens and slows tagged hostile mobs for 200t.",
               combined(effect(mobs(5), "slowness", 200, 1),
                        effect(mobs(5), "weakness", 200)), 6000),
        "partial", "Weakness and Slowness do not prevent hostile entry; no persistent zone or enemy-player boundary logic")
    near_player = {"type": "origins:command",
                   "command": "execute at @s if entity @a[distance=0.01..8]",
                   "comparison": ">=", "compare_to": 1}
    add("lovers", 9, "Linked Hearts",
        periodic("Linked Hearts", "Near another player, heal self one health point every 500t.",
                 {"type": "origins:heal", "amount": 1},
                 500, condition=near_player),
        "partial", "Any nearby player triggers the self-heal (not same-team only); no paired ally healing or +10% speed on both players")
    add("chariot", 9, "Trail of Embers",
        periodic("Trail of Embers", "While sprinting, ignite tagged hostile mobs within two blocks.",
                 area(2, {"type": "origins:set_on_fire", "duration": 2}),
                 300, condition={"type": "origins:sprinting"}),
        "partial", "No persistent sprint trail or particles; nearby mob ignition pulses every 300t rather than on crossing; enemy players excluded")
    add("chariot", 8, "Taunt",
        active("Taunt", "Crouch + secondary slows and highlights nearest hostile mob.",
               combined(effect(mobs(6, nearest=True), "slowness", 60),
                        effect(mobs(6, nearest=True), "glowing", 60)),
               400, crouch=True),
        "partial", "Does not force hostile mob AI to target the Chariot for 60t, uses key rather than crouch-right-click and excludes enemy players")
    add("chariot", 0, "The Battlefield",
        primary("The Battlefield", 18000,
                apply("strength", 900, 1),
                apply("speed", 900),
                effect(mobs(20), "weakness", 100),
                enemy_effect("weakness", 100, 20)),
        "partial", "No forced hostility among entities, exact +30% melee/+20% speed or 100t ignite-on-hit; Weakness reaches only listed opponent teams")
    add("strength", 9, "Grounded Slam",
        power("Grounded Slam", "After a >=3 block landing, slow nearby tagged hostiles.",
              "origins:action_on_land",
              condition={"type": "origins:fall_distance",
                         "comparison": ">=", "compare_to": 3},
              entity_action=effect(mobs(2), "slowness", 20)),
        "partial", "Source requires +10% on the player's NEXT melee strike and applies Slowness on that strike; only fall-triggered nearby mob Slowness is provided")
    add("strength", 6, "Dawnlight",
        active("Dawnlight", "Sneak + secondary grants Night Vision for 200t.",
               apply("night_vision", 200), 1200, crouch=True),
        "partial", "Does not enforce 60t continuous crouch charge or place 200t light-level-8 field within three blocks")
    add("strength", 3, "Silver Blade",
        power("Silver Blade", "Deal 10% additional melee damage to tagged hostile mobs.",
              "origins:modify_damage_dealt",
              target_condition=HOSTILE, modifier=mod(0.1)),
        "partial", "10% outgoing melee damage approximates 10% armor penetration; enemy players excluded pending team comparison")
    add("strength", 1, "Divine Hand",
        primary("Divine Hand", 1800,
                effect(mobs(15, nearest=True), "slowness", 60, 4),
                apply("strength", 60, 1)),
        "partial", "Cannot actually pull target, safely stun an enemy player, or enforce exactly +50% on the NEXT melee; Strength II over 60t is a multiple-hit fallback")
    add("strength", 0, "The Giant's Decay",
        primary("The Giant's Decay", 24000,
                effect(mobs(15), "wither", 600, 1),
                effect(mobs(15), "slowness", 600, 1),
                enemy_effect("wither", 600, 15, 1),
                enemy_effect("slowness", 600, 15, 1),
                apply("strength", 600, 1)),
        "partial", "Cannot halve armor or apply exact +30% damage only to affected targets; 600t fallback debuffs and listed-team-only PvP replace unspecified durations")
    add("hermit", 0, "The Unseen",
        primary("The Unseen", 24000,
                effect("@a[distance=..100]", "glowing", 900),
                apply("night_vision", 900)),
        "partial", "No 200-block structure reveal or 2x armor-ignoring critical arrow; glowing all players is source-intended informational effect")
    add("justice", 6, "Suggestion",
        active("Suggestion", "Secondary weakens the nearest tagged hostile mob within six blocks.",
               effect(mobs(6, nearest=True), "weakness", 100), 600),
        "partial", "Weakness does not clear target AI against Justice; enemy-player targets withheld until team checks are verified")
    add("devil", 2, "Blood Price",
        active("Blood Price", "Spend up to four health points for Strength II 200t.",
               combined({"type": "origins:damage", "amount": 4,
                          "source": {"name": "magic"}},
                        apply("strength", 200, 1)), 3600),
        "partial", "The four-point damage cost may interact with resistance/armor and can be lethal; exact unmitigated two-heart payment and once-per-window guarantees need runtime validation")
    add("tower", 1, "Falling Tower",
        primary("Falling Tower", 2400,
                {"type": "origins:add_velocity", "y": 1.25, "x": 0,
                 "z": 0, "space": "world"},
                effect(mobs(6), "slowness", 100, 1)),
        "partial", "Launch is not verified to reach eight blocks; no landing-synchronized slam, exact ten damage or enemy-player targeting; AoE Slowness fires at activation")
    add("moon", 5, "Scarlet",
        active("Scarlet", "Secondary gives Regeneration I for 200t.",
               apply("regeneration", 200), 1200),
        "partial", "Passive regeneration is not +50% instant potion healing, and it can increase total healing from unrelated causes")
    dark = {"type": "origins:brightness", "comparison": "<=",
            "compare_to": 0.267}
    add("sun", 9, "Inner Light",
        periodic("Inner Light", "When not sprinting in darkness, give self Night Vision.",
                 apply("night_vision", 200), 100,
                 condition={"type": "origins:and", "conditions": [
                     dark, {"type": "origins:sprinting", "inverted": True}]}),
        "partial", "Not sprinting is not 100t stillness; visual Night Vision is not a three-block world light-level-8 field")
    add("judgement", 5, "Discipline",
        active("Discipline", "Secondary grants Strength I for 20t.",
               apply("strength", 20), 600),
        "partial", "A short melee buff is not a targeted 20t stun on NEXT melee hit, and can affect multiple hits")
    add("world", 5, "Puppet String",
        active("Puppet String", "Crouch + secondary slows nearest tagged hostile mob.",
               effect(mobs(8, nearest=True), "slowness", 80, 1),
               400, crouch=True),
        "partial", "World source only specifies cooldown and both hostile mobs/enemy players; inherited Fool control also includes player tracking and next-hit damage, none are implemented")
    add("star", 0, "The Starless Sky",
        primary("The Starless Sky", 24000,
                apply("invisibility", 800),
                apply("speed", 800, 1),
                effect(mobs(30), "blindness", 100),
                effect(mobs(30), "slowness", 100),
                enemy_effect("blindness", 100, 30),
                enemy_effect("slowness", 100, 30)),
        "partial", "No light-extinguish, persistent field, exact +20% damage or invisibility break; team-safe PvP is a one-shot pulse, unassigned players neutral")
    add("sun", 0, "The Eternal Day",
        primary("The Eternal Day", 24000,
                apply("regeneration", 2400),
                apply("night_vision", 2400),
                effect(mobs(30, "undead"), "wither", 300, 1),
                ally_effect("regeneration", 2400, 30),
                ally_effect("night_vision", 2400, 30)),
        "partial", "Same-team allies receive healing/vision once, but no persistent no-spawn zone, exact undead 6 damage/sec or enemy-player damage")
    add("temperance", 0, "The Unbound",
        primary("The Unbound", 24000,
                {"type": "origins:clear_effect"},
                apply("invisibility", 500),
                apply("speed", 500, 1)),
        "partial", "Clears good effects as well as debuffs; no 15-block positive-effect stripping on enemy players, block phasing, x2 speed, armor hiding or invisibility break")
    add("empress", 0, "The Mirror World",
        primary("The Mirror World", 18000,
                apply("invisibility", 500),
                apply("resistance", 500, 2),
                apply("fire_resistance", 500)),
        "partial", "Resistance III does not provide invulnerability; no flight, armor hiding, entry-coordinate return, or exit poison/wither to enemies; all player-targeting omitted")
    add("fool", 0, "The Legend of The Fool",
        primary("The Legend of The Fool", 18000,
                apply("resistance", 700, 2),
                apply("fire_resistance", 700),
                apply("strength", 700, 1),
                apply("speed", 700, 1)),
        "partial", "No exact 75% reduction, timed creative flight, true fall immunity, 50% outgoing damage, on-hit debuffs, decoys, loot doubling, end teleport/heal or lower low-health cooldown; effects are a basic source-themed subset")
