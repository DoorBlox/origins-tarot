"""Private, opt-in actionbar display for each Arcane player's progression.

Vanilla global bossbars cannot safely display per-player sequence/marks for an
arbitrary number of SMP players. The actionbar instead resolves scoreboard
values using @s, with no shared display or fake objectives. Rendering every
40 ticks is intentionally lower-frequency and toggleable by non-OP players.
"""
import json
from progression.catalog import ACT_MARKS


def _json(phase, seq, required):
    return json.dumps([
        {"text": "[Tarot] ", "color": "light_purple"},
        {"text": "Seq ", "color": "gold"},
        {"score": {"name": "*", "objective": "a_seq"}, "color": "yellow"},
        {"text": " | Marks ", "color": "gray"},
        {"score": {"name": "*", "objective": "a_marks"}, "color": "green"},
        {"text": f"/{required} | Next: {phase}", "color": "aqua"},
        {"text": " | Proof cooldown ", "color": "gray"},
        {"score": {"name": "*", "objective": "a_actcd"}, "color": "yellow"},
        {"text": "t", "color": "gray"},
    ], separators=(",", ":"))


def emit_progress_hud(w):
    w.f("ui/hud/toggle",
        "scoreboard players add @s a_hud_on 0",
        "scoreboard players set @s a_ok 0",
        "execute if score @s a_hud matches 1 if score @s a_hud_on matches 0 run scoreboard players set @s a_ok 1",
        "execute if score @s a_hud matches 1 if score @s a_hud_on matches 1 run scoreboard players set @s a_ok 2",
        "execute if score @s a_hud matches 2 run scoreboard players set @s a_ok 1",
        "execute if score @s a_hud matches 3 run scoreboard players set @s a_ok 2",
        "execute if score @s a_ok matches 1 run scoreboard players set @s a_hud_on 1",
        "execute if score @s a_ok matches 2 run scoreboard players set @s a_hud_on 0",
        "execute if score @s a_ok matches 2 run title @s actionbar {\"text\":\"\"}",
        "execute if score @s a_ok matches 1 run tellraw @s {\"text\":\"[Tarot] Private progress HUD ON. /trigger a_hud set 3 to hide.\",\"color\":\"green\"}",
        "execute if score @s a_ok matches 2 run tellraw @s {\"text\":\"[Tarot] Progress HUD OFF. /trigger a_hud set 2 to show.\",\"color\":\"yellow\"}")
    w.f("ui/hud/tick",
        "execute unless score @s a_hud_on matches 1 run scoreboard players set @s a_hud_timer 0",
        "execute if score @s a_hud_on matches 1 run scoreboard players add @s a_hud_timer 1",
        "execute if score @s a_hud_on matches 1 if score @s a_hud_timer matches 40.. run function tarot_arcane:ui/hud/render",
        "execute if score @s a_hud_timer matches 40.. run scoreboard players set @s a_hud_timer 0")
    commands = []
    for seq in range(9, 1, -1):
        for phase, label in ((0, "ITEM"), (1, "EVENT")):
            commands.append(
                f"execute if score @s a_seq matches {seq} "
                f"if score @s a_phase matches {phase} "
                "run title @s actionbar " + _json(label, seq, ACT_MARKS[seq]))
    commands.append(
        'execute if score @s a_seq matches 1 run title @s actionbar '
        '{"text":"[Tarot] Sequence 1 (developer test only)","color":"red"}')
    w.f("ui/hud/render", commands)
