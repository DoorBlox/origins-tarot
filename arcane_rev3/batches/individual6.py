"""Twenty-one remaining individual slots with source-traced bounded substitutes.

Includes three real, cooldown-latched native prevent-death mechanics, one
snowball projectile, conditional water walking and Fate reroll workarounds.
All are PARTIAL and not yet gameplay validated. Unsupported client/model,
structure/AI events are NOT claimed to work.
"""
from ..powers import power, apply, mod, compound
from ..team_policy import enemy_effect, ally_effect
from .shared import active, periodic, combined, effect, mobs, cmd
from .rescue import save
from .resonance import night


BAD = {"type": "origins:or", "conditions": [
    {"type": "origins:status_effect", "effect": "minecraft:" + name}
    for name in ("hunger", "slowness", "mining_fatigue")]}


def roll_positive():
    return {"type": "origins:choice", "actions": [
        {"element": apply(name, 100), "weight": 1}
        for name in ("speed", "haste", "absorption")]}


def reroll(chance):
    return {"type": "origins:chance", "chance": chance,
            "action": combined(
                *[{"type": "origins:clear_effect", "effect": "minecraft:" + name}
                  for name in ("hunger", "slowness", "mining_fatigue")],
                roll_positive())}


def register(add):
    add("fool", 1, "History Substitution",
        save("History Substitution", "a_cd_history", 7200, 20, 12,
             speed=2, invisible=True),
        "partial", "7200-online-tick native lethal prevention, 12-block random safe teleport and full heal with Invis/Speed II; exact away-from-attacker placement, disguise/lore shadow and test-world damage cancellation need verification")
    add("world", 1, "Hunter's Substitution",
        save("Hunter's Substitution", "a_cd_hunter", 9600, 3, 8),
        "partial", "On lethal, heals to roughly two hearts and random-teleports within eight blocks, once per 9600 online ticks; exact attacker-relative placement/return not implemented")
    add("death", 4, "Undying",
        save("Undying", "a_cd_undying", 12000, 1, 0, chance=0.05),
        "partial", "5% chance on lethal, heals from half-heart to about one heart, with persistent 12000-online-tick cooldown; needs actual death-event game verification")

    add("magician", 7, "Star Chart",
        active("Star Chart", "Crouch + secondary at night: Night Vision and Luck.",
               combined(apply("night_vision", 100),
                        apply("luck", 100)), 1200, crouch=True),
        "partial", "Does not raycast/locate nearest structure or draw a 100t directional particle line; night-only and world-navigation feedback absent")
    add("magician", 6, "Recorded Step",
        active("Recorded Step", "Crouch + secondary safely relocates up to six blocks.",
               {"type": "origins:random_teleport",
                "area_width": 6, "area_height": 3, "attempts": 20,
                "loaded_chunks_only": True}, 1200, crouch=True),
        "partial", "One-shot local repositioning replaces two-stage clicked-block 1200t location memory/return; does not store visited coordinates or enforce max 30 block distance")
    add("empress", 6, "Thread",
        active("Thread", "Secondary slows tagged hostiles and configured enemy players within 6 blocks.",
               combined(effect(mobs(6,nearest=True), "slowness", 40),
                        enemy_effect("slowness", 40, 6)), 400),
        "partial", "Pulses opponent players instead of right-click targeting a specific player; teamless/unlisted players neutral")
    add("emperor", 5, "Decree",
        active("Decree", "Secondary gives nearby tagged hostiles and opponents Weakness.",
               combined(effect(mobs(6), "weakness", 100),
                        enemy_effect("weakness", 100, 6)), 900),
        "partial", "Weakness only, not a 100t forced enemy AI aggro/taunt toward Emperor; no player command control")
    add("wheel_of_fortune", 9, "Debt of Fate",
        power("Debt of Fate",
              "While a Fate curse is active, lose 5% outgoing damage.",
              "origins:modify_damage_dealt",
              condition=BAD, modifier=mod(-0.05)),
        "partial", "The original mandatory inclusion of bad outcomes is already present in Fate's Current six-way rolls; this adds a tangible extra curse while Hunger, Slowness or Mining Fatigue is active, including outside Fate rolls")
    add("wheel_of_fortune", 9, "Lucky Break",
        periodic("Lucky Break",
                 "Every 1800t while cursed, 10% chance to clear bad effects and gain boon.",
                 reroll(0.10), 1800, condition=BAD),
        "partial", "One periodic 10% reroll opportunity, not an immediate reroll on Fate's Current bad roll; clears preexisting similar debuffs regardless of source")
    add("wheel_of_fortune", 2, "Fate's Favor",
        active("Fate's Favor",
               "Secondary: reroll an active Fate-like curse into a positive boon.",
               combined(*[{"type": "origins:clear_effect",
                           "effect": "minecraft:" + name}
                          for name in ("hunger", "slowness", "mining_fatigue")],
                        roll_positive()), 6000),
        "partial", "Not restricted to a bad Fate's Current specifically, nor exactly one saved reroll; can remove matching debuffs from other causes")
    add("wheel_of_fortune", 1, "Lucky Break II",
        periodic("Lucky Break II",
                 "20% per 1800t while cursed: clear bad effects and gain boon.",
                 reroll(0.20), 1800, condition=BAD),
        "partial", "20% periodic opportunity is not an immediate Fate's Current reroll and may coexist with Lucky Break; pair will need replacement/nonstack review")
    add("wheel_of_fortune", 1, "Wheel's Turn",
        active("Wheel's Turn",
               "Primary: Luck II, Resistance I 300t and brief hostile Weakness.",
               combined(apply("luck", 300, 1),
                        apply("resistance", 300),
                        effect(mobs(5), "weakness", 100),
                        enemy_effect("weakness", 100, 5)), 3600, primary=True),
        "partial", "No inversion of positive/negative six Fate rolls, 50% damage reflection, or causal link to Fate's Current; defensive 300t substitute")
    add("death", 5, "Gate",
        active("Gate", "Secondary safely relocates within six blocks.",
               {"type": "origins:random_teleport",
                "area_width": 6, "area_height": 3, "attempts": 20,
                "loaded_chunks_only": True}, 12000),
        "partial", "Safe escape replaces Nether portal; no dimension change, block placement, persistence or 3x3 terrain damage")
    add("death", 3, "Ferry",
        compound("Ferry",
            activate=active("Ferry", "Secondary: 100t Speed to enable water walking.",
                            apply("speed", 100), 1200),
            walk={"type": "origins:walk_on_fluid",
                  "fluid": "minecraft:water",
                  "condition": {"type": "origins:status_effect",
                                "effect": "minecraft:speed"}}),
        "partial", "Walks on water during any active Speed status, not only a 100t right-click-water Ferry charge; source cooldown is preserved on primary activation but potion Speed can enable early")
    add("temperance", 3, "Silence",
        power("Silence", "Sneaking grants native invisibility to player model.",
              "origins:invisibility",
              condition={"type": "origins:sneaking"},
              render_armor=True, render_outline=False),
        "partial", "Sneaking invisibility is a stealth replacement; does not actually remove footstep sounds or suppress sound/game events")
    add("sun", 3, "Radiance",
        periodic("Radiance",
                 "In dim light while not sprinting, grant nearby same-team allies Night Vision.",
                 combined(apply("night_vision", 100),
                          ally_effect("night_vision", 100, 5)),
                 100, condition={"type": "origins:and", "conditions": [
                     {"type": "origins:brightness",
                      "comparison": "<=", "compare_to": 0.267},
                     {"type": "origins:sprinting", "inverted": True}]}),
        "partial", "Night Vision is client visual light, not the 5-block real light field; not sprinting does not enforce 100t standing still")
    paper = {"type": "origins:equipped_item", "equipment_slot": "mainhand",
             "item_condition": {"type": "origins:ingredient",
                                "ingredient": {"item": "minecraft:paper"}}}
    dagger = active("Paper Dagger",
                    "Primary holding paper: consume one and slow nearest hostile.",
                    combined(cmd("clear @s minecraft:paper 1"),
                             effect(mobs(6,nearest=True), "slowness", 40)), 200,
                    primary=True)
    dagger["condition"] = paper
    add("world", 8, "Paper Dagger", dagger,
        "partial", "Consumes one paper from inventory and affects nearest tagged hostile but is NOT an actual 3-damage thrown dagger/projectile; enemy players not individually struck")
    add("world", 7, "Air Cannon",
        power("Air Cannon", "Primary fires one fast non-griefing snowball.",
              "origins:fire_projectile", entity_type="minecraft:snowball",
              cooldown=160, count=1, interval=0,
              speed=2.7, divergence=0.0,
              hud_render={"should_render": True},
              key={"key": "key.origins.primary_active"}),
        "partial", "Actual ranged snowball projectile has zero direct damage, no 4/3 damage split, knockback, 14-block range limit or Marked Prey linkage; no fire, piercing or block changes")
    add("world", 2, "Mystery Step",
        active("Mystery Step", "Secondary makes bounded random safe reposition.",
               {"type": "origins:random_teleport",
                "area_width": 8, "area_height": 3, "attempts": 20,
                "loaded_chunks_only": True}, 4800),
        "partial", "Source specifies 4800t cooldown but inherits a mystery-location/stealth teleport mechanic not present in this local safe fallback")
    add("high_priestess", 4, "Foresight",
        power("Foresight",
              "While not sprinting, projectiles deal 10% more damage.",
              "origins:modify_projectile_damage",
              condition={"type": "origins:sprinting", "inverted": True},
              modifier=mod(0.10)),
        "partial", "First-shot after 300t projectile silence and Scripted Insight source synergy missing; this affects any projectile while not sprinting")
    add("star", 9, "Sleepless Vigil",
        power("Sleepless Vigil", "Night Vision at night as a sleepless alertness replacement.",
              "origins:night_vision", condition=night()),
        "partial", "Does not change five-day phantom spawning threshold; native Origins 1.4.1 has no confirmed insomnia tick modifier")
