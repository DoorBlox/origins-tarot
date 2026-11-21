"""Bounded, source-owned Hanged Man Sin resource for Fabric/Origins 1.18.2.

The vanilla damage_taken scoreboard gives a cumulative statistic, not the
original damage-source callback. We sample its positive delta each online
tick and store 25% in the same statistic units (10 points ~= 1 health).
Normal cap 160 units ~= 16HP; capstone safety ceiling 800 units ~= 80HP.
Approximate area damage/healing never targets teammates or neutral players.
Do not claim exact damage-source identities, arbitrary dynamic damage or
vanilla player NBT mutation.
"""

from .team_policy import team_names


SIN_SCORES = (
    "a_sin", "a_sin_seen", "a_sin_delta", "a_sin_gain",
    "a_sin_idle", "a_sin_started", "a_sin_owned", "a_sin_capown",
    "a_sin_hp", "a_sin_over", "a_sin_form", "a_sin_mod",
    "a_sin_burden", "a_trinity_hits", "a_trinity_win", "a_seen_deaths",
)


def _mobs(effect, seconds, amplifier, radius):
    assert effect in {"wither", "weakness", "slowness"}
    assert 1 <= seconds <= 20 and 0 <= amplifier <= 3
    assert radius in (8, 10, 15)
    return (f"execute at @s run effect give "
            f"@e[type=#tarot:hostile,distance=..{radius}] "
            f"minecraft:{effect} {seconds} {amplifier} true")


def _team_effects(effect, seconds, amplifier, radius, root):
    """No unassigned or unlisted team can ever be a negative target."""
    assert effect in {"weakness", "slowness"}
    assert radius in (8, 10, 15) and 1 <= seconds <= 20
    teams = team_names(root)
    return [
        f"execute if entity @s[team={source}] at @s run effect give "
        f"@a[team={target},distance=..{radius}] minecraft:{effect} "
        f"{seconds} {amplifier} true"
        for source in teams for target in teams if target != source
    ]


def emit_sin(w, prefix, root):
    """Write fixed server-side functions; called by full_build.emit_player."""
    def F(name):
        return "function " + prefix + "sin/" + name

    w.f("sin/start",
        "scoreboard players set @s a_sin_started 1",
        "scoreboard players set @s a_sin 0",
        "scoreboard players set @s a_sin_idle 0",
        "scoreboard players operation @s a_sin_seen = @s a_dmg_taken")

    w.f("sin/clear",
        "scoreboard players set @s a_sin 0",
        "scoreboard players set @s a_sin_started 0",
        "scoreboard players set @s a_sin_idle 0",
        "scoreboard players set @s a_sin_form 0",
        "scoreboard players set @s a_trinity_hits 0",
        "scoreboard players set @s a_trinity_win 0",
        "scoreboard players operation @s a_sin_seen = @s a_dmg_taken")

    w.f("sin/tick",
        "execute unless score @s a_sin_started matches 1 run " + F("start"),
        "scoreboard players operation @s a_sin_delta = @s a_dmg_taken",
        "scoreboard players operation @s a_sin_delta -= @s a_sin_seen",
        "execute if score @s a_sin_delta matches 1.. run " + F("on_hit"),
        "scoreboard players operation @s a_sin_seen = @s a_dmg_taken",
        "execute if score @s a_sin_delta matches ..0 if score @s a_sin matches 1.. run scoreboard players add @s a_sin_idle 1",
        "execute if score @s a_sin matches 1.. if score @s a_sin_idle matches 200.. run " + F("dissipate"),
        "execute if score @s a_sin matches 1.. store result score @s a_sin_hp run data get entity @s Health 1",
        "execute if score @s a_sin matches 1.. if score @s a_sin_hp matches ..7 run " + F("burst"))

    w.f("sin/on_hit",
        "scoreboard players set @s a_sin_idle 0",
        "scoreboard players operation @s a_sin_gain = @s a_sin_delta",
        "scoreboard players operation @s a_sin_gain /= #4 a_const",
        "execute if score @s a_sin_gain matches ..0 run scoreboard players set @s a_sin_gain 1",
        "scoreboard players operation @s a_sin += @s a_sin_gain",
        "execute unless score @s a_sin_form matches 1.. if score @s a_sin matches 161.. run scoreboard players set @s a_sin 160",
        "execute if score @s a_sin_form matches 1.. if score @s a_sin matches 801.. run scoreboard players set @s a_sin 800")

    w.f("sin/dissipate",
        "execute store success score @s a_sin_burden run power has @s tarot:hanged_man/5_burden_bearer",
        "execute if score @s a_sin_burden matches 1 run effect give @s minecraft:regeneration 3 0 true",
        "scoreboard players set @s a_sin 0",
        "scoreboard players set @s a_sin_idle 200")

    w.f("sin/burst",
        "execute store success score @s a_sin_over run power has @s tarot:hanged_man/1_sin_overflow",
        "execute if score @s a_sin_over matches 1 run " + F("burst_overflow"),
        "execute unless score @s a_sin_over matches 1 run " + F("burst_basic"))

    w.f("sin/burst_basic",
        _mobs("weakness", 4, 0, 8),
        "execute if score @s a_sin matches 1..39 run " + _mobs("wither", 3, 0, 8),
        "execute if score @s a_sin matches 40..99 run " + _mobs("wither", 3, 1, 8),
        "execute if score @s a_sin matches 100.. run " + _mobs("wither", 3, 2, 8),
        _team_effects("weakness", 4, 0, 8, root),
        # Tiered regeneration is intentionally NOT advertised as exact 50%
        # of stored Sin; the 1.18.2 datapack lacks arbitrary heal-by-score.
        "execute if score @s a_sin matches 1.. run effect give @s minecraft:regeneration 3 0 true",
        "scoreboard players set @s a_sin 0",
        "scoreboard players set @s a_sin_idle 0")

    w.f("sin/burst_overflow",
        _mobs("weakness", 3, 1, 10),
        _mobs("slowness", 3, 1, 10),
        "execute if score @s a_sin matches 1..99 run " + _mobs("wither", 3, 0, 10),
        "execute if score @s a_sin matches 100.. run " + _mobs("wither", 3, 1, 10),
        _team_effects("weakness", 3, 1, 10, root),
        _team_effects("slowness", 3, 1, 10, root),
        "execute if score @s a_sin matches 1.. run effect give @s minecraft:regeneration 4 1 true",
        "scoreboard players set @s a_sin 0",
        "scoreboard players set @s a_sin_idle 0")

    # Trio counts THREE hits inside a fixed 100t interval, not three
    # independently identified damage sources: documented PARTIAL.
    w.f("sin/trinity_hit",
        "execute unless score @s a_trinity_win matches 1.. run scoreboard players set @s a_trinity_hits 0",
        "execute unless score @s a_trinity_win matches 1.. run scoreboard players set @s a_trinity_win 100",
        "scoreboard players add @s a_trinity_hits 1",
        "execute if score @s a_trinity_hits matches 3.. run " + F("trinity_proc"))
    w.f("sin/trinity_proc",
        "effect give @s minecraft:resistance 3 1 true",
        "effect give @s minecraft:instant_health 1 0 true",
        "scoreboard players set @s a_trinity_hits 0",
        "scoreboard players set @s a_trinity_win 0")

    # Capstone window 1200t, no automatic world edits / griefable explosion.
    w.f("sin/form_start",
        "scoreboard players set @s a_sin_form 1200",
        'title @s actionbar {"text":"[Tarot] Weight of Sin: 60s","color":"dark_red"}')
    w.f("sin/form_tick",
        "execute store success score @s a_sin_capown run power has @s tarot:hanged_man/0_weight_of_sin_made_manifest",
        "execute unless score @s a_sin_capown matches 1 run scoreboard players set @s a_sin_form 0",
        "execute if score @s a_sin_capown matches 1 run scoreboard players remove @s a_sin_form 1",
        "execute if score @s a_sin_capown matches 1 if score @s a_sin_form matches 1.. run " + F("nova_check"),
        "execute if score @s a_sin_capown matches 1 if score @s a_sin_form matches 0 run " + F("form_expire"))
    w.f("sin/nova_check",
        "scoreboard players operation @s a_sin_mod = @s a_sin_form",
        "scoreboard players operation @s a_sin_mod %= #80 a_const",
        "execute if score @s a_sin matches 1.. if score @s a_sin_mod matches 0 run " + F("nova"))
    w.f("sin/nova",
        _mobs("weakness", 4, 0, 8),
        _team_effects("weakness", 4, 0, 8, root))
    w.f("sin/form_expire",
        _mobs("wither", 4, 1, 15),
        _mobs("weakness", 5, 1, 15),
        _team_effects("weakness", 5, 1, 15, root),
        "effect give @s minecraft:regeneration 10 1 true",
        "effect give @s minecraft:resistance 15 0 true",
        "scoreboard players set @s a_sin 0",
        "scoreboard players set @s a_sin_idle 0")

    w.f("sin/status",
        'execute if score @s a_sin matches 1.. run title @s actionbar '
        '{"text":"[Tarot] Stored Sin: ","color":"dark_red",'
        '"extra":[{"score":{"name":"*","objective":"a_sin"}}]}')
