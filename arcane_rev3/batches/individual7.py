"""Wave 7: 32 handbook-matched individual abilities with playable native subsets.

These are *PARTIAL* translations. Where the original requires event hooks,
client skin/model interception, NPC inventory changes or persistent regions,
we provide safe bounded effects, never claim the original script exists.
Damage to enemy players uses the vanilla-team allowlist, not broad @a.
"""
from ..powers import power, apply, mod, xp, compound
from ..team_policy import ally_effect, enemy_effect
from .shared import active, periodic, combined, effect, mobs, cmd
from .resonance6 import timed_decoy
from .resonance4 import pulse
from .resonance import night


HOSTILE = {"type": "origins:in_tag", "tag": "tarot:hostile"}


def mobile(width):
    return {"type": "origins:random_teleport",
            "area_width": width, "area_height": 3,
            "attempts": 20, "loaded_chunks_only": True}


def capped(name, cooldown, *actions):
    return active(name, "Primary-key time-bounded source-based preview.",
                  combined(*actions), cooldown, primary=True)


def book_condition():
    return {"type": "origins:equipped_item", "equipment_slot": "offhand",
            "item_condition": {"type": "origins:ingredient",
                               "ingredient": {"tag": "tarot:books"}}}


def register(add):
    disguise = active("Full Faceless Disguise",
        "Primary in no-combat state grants 2400t of self invisibility.",
        apply("invisibility", 2400), 6000, primary=True)
    disguise["condition"] = {"type": "origins:command",
        "command": "execute if score @s a_combat matches 0",
        "comparison": ">=", "compare_to": 1, "permission_level": 2}
    add("fool", 9, "Full Faceless Disguise", disguise, "partial",
        "Invisibility substitutes for random online player skin, name and model; does not preserve 2400-2880t randomness, break on attack, or integrate SkinShifter 1.0 command without exact jar verification")
    borrowed = active("Borrowed Face",
        "Secondary while out of combat: 1800t Invisibility and 60t Speed II.",
        combined(apply("invisibility", 1800),
                 apply("speed", 60, 1)), 2400)
    borrowed["condition"] = disguise["condition"]
    add("fool", 6, "Borrowed Face", borrowed, "partial",
        "Does not swap names with closest player or restore skins at expiry; Speed II activates now, rather than at the end. SkinShifter 1.0 integration unverified")
    add("fool", 2, "Fools' Gathering",
        active("Fools' Gathering",
               "Secondary creates two 200t smoke decoys and briefly slows hostiles.",
               combined(timed_decoy(-1), timed_decoy(1),
                        effect(mobs(5), "slowness", 100)), 6000),
        "partial", "Two harmless visual smoke-cloud decoys replace 4HP Vex-like independent ally minions; no attacking hostile mobs or enemy players")

    add("magician", 1, "Waypoint",
        active("Waypoint", "Secondary makes a bounded safe local teleport.",
               mobile(12), 3600),
        "partial", "Local safe teleport cannot record three visited location coordinates, create a group-usable 200t doorway, or revisit marked coordinates")
    add("magician", 0, "All Paths Converge",
        capped("All Paths Converge", 18000,
               apply("invisibility", 900), apply("speed", 900, 1),
               mobile(12)),
        "partial", "45s stealth plus bounded relocation replaces unrestricted block phasing and personal door history; no persistent visited-location storage, phase collision or place/break restrictions")

    add("high_priestess", 9, "Marginalia",
        power("Marginalia", "Gain 5% bonus XP while holding a book offhand.",
              "origins:modify_xp_gain",
              condition=book_condition(), modifier=mod(0.05)),
        "partial", "Generic XP gain with book replaces 5% enchanting XP refund and per-minute +1 Looting, no enchantment hook")
    add("high_priestess", 3, "Sage's Insight",
        active("Sage's Insight", "Secondary grants short Night Vision and Luck I.",
               combined(apply("night_vision", 160),
                        apply("luck", 160)), 1200),
        "partial", "No 5% on-block-break ore detection, nearest-ore search or ore-guiding particle line; dark exploration convenience only")
    add("high_priestess", 2, "Borrowed Knowledge",
        active("Borrowed Knowledge",
               "Secondary temporarily grants self Haste I and Luck I for 1200t.",
               combined(apply("haste", 1200),
                        apply("luck", 1200)), 6000),
        "partial", "Fixed whitelisted Haste/Luck substitutes for copying a nearby player's arbitrary passive; no other player's attributes or data accessed")

    add("empress", 8, "Whisper",
        active("Whisper", "Crouch + secondary briefly weakens nearby tagged hostiles.",
               effect(mobs(6), "weakness", 200), 1200, crouch=True),
        "partial", "Does not turn clicked passive mobs hostile to the nearest other player, change AI targets, or affect nonconsenting neutral mobs")
    add("empress", 2, "Mirror Passage",
        active("Mirror Passage", "Secondary safely teleports within ten blocks.",
               combined(mobile(10),
                        apply("invisibility", 40)), 3600),
        "partial", "Random safe short blink replaces direct portal-through-glass, without raycast, precision aim or collision through glass")

    add("hierophant", 0, "The Sanctum",
        capped("The Sanctum", 24000,
               apply("regeneration", 600),
               effect(mobs(16, "undead"), "wither", 300, 1),
               ally_effect("regeneration", 600, 16)),
        "partial", "600t one-shot self/ally regen plus undead Wither substitutes for permanent one-world 16-block sanctum; no bed/book anchor, spawn prevention, persistent zone, exact undead damage/sec or hunger recovery")

    add("chariot", 2, "Storm Call",
        active("Storm Call", "Secondary creates local Storm-themed speed and wetness buffs.",
               combined(apply("water_breathing", 600),
                        apply("speed", 600),
                        effect(mobs(20), "slowness", 100),
                        enemy_effect("slowness", 100, 20)), 6000),
        "partial", "Local 600t water-breathing/speed and safe hostile slow replace actual 20-block rain weather zone. No global weather manipulation or world mutation")

    add("hermit", 6, "Scroll",
        active("Scroll", "Sneak + secondary prints your current coordinates in chat.",
               cmd('tellraw @s [{"text":"[Scroll] Coordinates: "},{"nbt":"Pos","entity":"@s","interpret":false}]'),
               1200, crouch=True),
        "partial", "Shows current coordinate NBT to owner in chat rather than serializing a protected paper item coordinate tag; no paper consumption or item NBT mutation")
    add("hermit", 4, "Forbidden Insight",
        power("Forbidden Insight", "5% XP gain bonus while holding a book offhand.",
              "origins:modify_xp_gain",
              condition=book_condition(), modifier=mod(0.05)),
        "partial", "Does not boost actual enchanting-table power by 5% or enforce level-30 requirement; book-conditioned XP bonus is a transparent alternative")
    add("hermit", 1, "Emperor's Library",
        compound("Emperor's Library",
            activate=active("Emperor's Library",
                "Primary gives 300t Haste and Luck for scholarly focus.",
                combined(apply("haste", 300),
                         apply("luck", 300)), 3600, primary=True),
            focused_arrow=power("Emperor's Library: Arrow Focus",
                "50% extra projectile damage while Luck is active.",
                "origins:modify_projectile_damage",
                condition={"type": "origins:status_effect",
                           "effect": "minecraft:luck"},
                modifier=mod(0.5))),
        "partial", "No copied enchantment level up to 5; 300t self Luck/Haste and 50% all-projectile modifier is broader than arrows and can be enabled by outside Luck sources")

    reel = [
        (200, apply("speed", 200)),
        (200, apply("haste", 200)),
        (200, apply("absorption", 200, 1)),
        (150, apply("luck", 200)),
        (150, apply("slowness", 100)),
        (1, combined({"type": "origins:heal", "amount": 20},
                     apply("strength", 1200, 1),
                     apply("speed", 1200, 1),
                     apply("regeneration", 1200, 1),
                     apply("resistance", 1200, 1),
                     apply("absorption", 1200, 3))),
    ]
    add("wheel_of_fortune", 0, "Slot of Fate",
        active("Slot of Fate", "Primary spins a single weighted Fate reel.",
               {"type": "origins:choice", "actions": [
                   {"weight": weight, "element": action}
                   for weight, action in reel]}, 24000, primary=True),
        "partial", "One weighted roll, not three 20/20/20/15/15/10 reels or matching combos; rare jackpot fallback healing/buffs but no five banked positive Fate rolls, instant kill of nearby hostile/enemy player, or global fortune changes")

    add("justice", 8, "Mind Read",
        active("Mind Read", "Crouch + secondary reveals configured enemies nearby.",
               enemy_effect("glowing", 40, 6), 200, crouch=True),
        "partial", "Shows team-filtered Glowing for nearby opponents, not clicked player's exact health/chat information; teammates and teamless people aren't exposed")
    add("justice", 0, "The Mindscape",
        capped("The Mindscape", 24000,
               apply("resistance", 600, 1),
               effect(mobs(20), "slowness", 600, 2),
               effect(mobs(20), "weakness", 600, 1),
               enemy_effect("slowness", 600, 20, 2),
               enemy_effect("weakness", 600, 20, 1)),
        "partial", "600t enemy slowing and resistance substitute for full AI freeze and attack suppression; no jump/sprint whitelist, symmetric damage cancel or explicit player contracts")

    add("death", 0, "The Final Harvest",
        capped("The Final Harvest", 24000,
               apply("absorption", 1200, 2),
               effect(mobs(10), "wither", 600, 1),
               enemy_effect("weakness", 600, 10)),
        "partial", "No 60t periodic lowest-health enemy execution, boss/player health caps or stackable absorption per kill; timed Wither/Absorption substitutes")

    add("devil", 0, "Descent",
        compound("Descent",
            activate=capped("Descent", 18000,
                apply("strength", 800, 1),
                apply("fire_resistance", 800),
                apply("speed", 800),
                effect(mobs(15), "wither", 100, 1),
                enemy_effect("wither", 100, 15, 1)),
            strike=power("Descent: Corrupting Hit",
                "While under Strength, strike tagged hostiles with Wither.",
                "origins:target_action_on_hit", cooldown=40,
                condition={"type": "origins:status_effect",
                           "effect": "minecraft:strength"},
                target_condition=HOSTILE,
                entity_action=apply("wither", 100))),
        "partial", "Basic 800t strength/fire-resistance/speed and hostile Wither replace full 40s descent; no true lifesteal, kill-linked minions, contracts, increased incoming damage or end Hunger; Strength from other sources may enable strike")

    add("tower", 8, "Charge",
        active("Charge", "Crouch + secondary grants Haste I for 60t.",
               apply("haste", 60), 600, crouch=True),
        "partial", "Mining buff substitutes for crouch-right-click stone priming 60t and breaking one block; does not edit the world or claim safe block ownership")
    add("tower", 5, "Collapse",
        active("Collapse", "Secondary grants Haste II and slows tagged hostiles.",
               combined(apply("haste", 100, 1),
                        effect(mobs(3), "slowness", 100)), 1200),
        "partial", "No 3x3 stone block break, world destruction, protection-plugin bypass or terrain persistence; safe mining-themed Haste/Slowness fallback")
    add("tower", 0, "The Fall",
        capped("The Fall", 24000,
               apply("resistance", 600, 1),
               apply("strength", 600, 1),
               effect(mobs(15), "slowness", 200, 1),
               enemy_effect("slowness", 200, 15, 1)),
        "partial", "600t survivability/offense replaces falling-catastrophe AoE, dangerous terrain destruction and repeated slams; does not create rubble or exact 4/6 damage ticks")

    add("star", 1, "Sleepless Vigil II",
        periodic("Sleepless Vigil II", "Nightly Haste I as a vigilant sleep substitute.",
                 apply("haste", 100), 100, condition=night()),
        "partial", "Does not extend phantom insomnia threshold from 5 to 7 Minecraft days; Haste at night is a separate gameplay consolation and may stack with prior Night Vision")

    potion = {"type": "origins:equipped_item", "equipment_slot": "mainhand",
              "item_condition": {"type": "origins:ingredient",
                  "ingredient": {"item": "minecraft:potion"}}}
    add("moon", 9, "Pharmacist",
        periodic("Pharmacist", "Holding potion slowly regenerates self.",
                 apply("regeneration", 80), 200, condition=potion),
        "partial", "Holding a generic potion triggers Regen instead of multiplying healing from consumed potions by 25%; no potion-use event hook")
    add("moon", 0, "The Scarlet Feast",
        capped("The Scarlet Feast", 24000,
               {"type": "origins:heal", "amount": 4},
               apply("regeneration", 600, 1),
               apply("speed", 600),
               effect(mobs(10), "wither", 100, 1),
               enemy_effect("weakness", 100, 10)),
        "partial", "Self heal/regen and enemy debuff replace original Scarlet capstone life-drain mechanics; no blood resource, potion healing scalar or executed mob resurrection")

    add("sun", 6, "Witness",
        active("Witness", "Secondary marks tagged hostiles and configured opponents.",
               combined(effect(mobs(10, nearest=True), "glowing", 200),
                        enemy_effect("glowing", 200, 10)), 1200),
        "partial", "Does not read clicked player's exact health for 1200t; 200t team-safe Glowing reveals targets without inventory or private NBT inspection")

    add("judgement", 0, "The Absolute Law",
        capped("The Absolute Law", 24000,
               apply("resistance", 600, 1),
               effect(mobs(15), "slowness", 600, 1),
               effect(mobs(15), "weakness", 600, 1),
               enemy_effect("slowness", 600, 15, 1),
               enemy_effect("weakness", 600, 15, 1)),
        "partial", "600t resistance and negative effects replace exact-law absolute crowd control; no full AI freeze, enemy-player attack blocking or typed legal rule engine")

    bow = {"type": "origins:equipped_item", "equipment_slot": "mainhand",
           "item_condition": {"type": "origins:ingredient",
                              "ingredient": {"item": "minecraft:bow"}}}
    add("world", 9, "Predator's Patience",
        power("Predator's Patience", "10% projectile damage bonus while holding bow and not sprinting.",
              "origins:modify_projectile_damage", modifier=mod(0.10),
              condition={"type": "origins:and", "conditions": [
                  bow, {"type": "origins:sprinting", "inverted": True}]}),
        "partial", "Flat 10% bonus replaces stationary ramp +5%/60t to +30%, does not measure motionless duration or reserve an exact first shot")
    add("world", 6, "Borrowed Face",
        active("Borrowed Face", "Secondary makes self invisible for 600t.",
               apply("invisibility", 600), 2400),
        "partial", "Short invisibility substitutes for copying a real player's name/skin/model for 600t; no verified SkinShifter 1.0 API, no selected target or safe restoration")
    add("world", 3, "Small Miracle",
        active("Small Miracle", "Secondary gives emergency health and Absorption.",
               combined({"type": "origins:heal", "amount": 4},
                        apply("absorption", 200, 1)), 9600),
        "partial", "A bounded 2-heart emergency heal+Absorption replaces inherited bespoke miracle/lucky death-protection logic; not true lethal cancellation")
    add("world", 0, "The Perfect Prey",
        capped("The Perfect Prey", 24000,
               apply("strength", 900, 1),
               apply("speed", 900, 1),
               effect(mobs(15, nearest=True), "glowing", 200),
               enemy_effect("glowing", 200, 15)),
        "partial", "900t self buffs and hostile/opponent Glowing replace selected player mark within 50 blocks, trail tracking, guaranteed next-projectile hit/crit and kill-reward detection")
