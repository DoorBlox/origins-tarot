"""Per-player cooldown bounded native Origins 1.4.1 lethal saves.

The origins:prevent_death type has NO built-in cooldown. An unguarded power
would accidentally grant immortality. Use persisted per-player vanilla
scoreboard cooldowns declared/decremented in full_build.py. Timers represent
ONLINE ticks and persist across a player relog. No OP granted to the player.
"""
from ..powers import power, apply
from .shared import cmd, combined
from ..full_build import RESCUE_COOLDOWNS


def save(name, score, cooldown, heal, radius, *, speed=0, invisible=False,
         chance=None, target_action=None):
    if score not in RESCUE_COOLDOWNS:
        raise ValueError(f"Unknown persisted rescue cooldown: {score}")
    if not 1200 <= cooldown <= 24000:
        raise ValueError("Rescue must be at least a minute apart")
    gate = {"type": "origins:command",
            "command": f"execute if score @s {score} matches 0",
            "comparison": ">=", "compare_to": 1,
            "permission_level": 2}
    if chance is not None:
        if not 0 < chance < 1:
            raise ValueError("Invalid chance")
        gate = {"type": "origins:and", "conditions": [
            gate, {"type": "origins:chance", "chance": chance}]}
    actions = [
        cmd(f"scoreboard players set @s {score} {cooldown}"),
        {"type": "origins:random_teleport", "area_width": radius,
         "area_height": 3, "attempts": 20, "loaded_chunks_only": True},
        {"type": "origins:heal", "amount": heal},
    ]
    if invisible:
        actions.append(apply("invisibility", 60))
    if speed:
        actions.append(apply("speed", 60, speed-1))
    if target_action:
        actions.append(target_action)
    return power(
        name,
        "On lethal damage, save yourself at most once per persistent cooldown.",
        "origins:prevent_death",
        condition=gate,
        entity_action=combined(*actions))
