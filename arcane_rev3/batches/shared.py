"""Common vanilla-Minecraft 1.18.2-safe builders for handbook skill batches.

Commands are hard-coded at build time. No player input is interpolated into any
execute_command effect; non-OP players still only use the /trigger alias bridge.
"""
from ..powers import power


def cmd(command):
    if any(c in command for c in ("\n", "\r", ";")):
        raise ValueError("commands must remain single, static, non-chained lines")
    return {"type": "origins:execute_command", "permission_level": 2,
            "command": command}


def players(radius):
    return f"@a[distance=..{radius}]"


def mobs(radius, tag="hostile", nearest=False):
    suffix = ",sort=nearest,limit=1" if nearest else ""
    return f"@e[type=#tarot:{tag},distance=..{radius}{suffix}]"


def effect(selector, effect_name, ticks, amplifier=0):
    if ticks < 20 or ticks % 20:
        raise ValueError("vanilla effect command durations must be whole seconds")
    return cmd("execute at @s run effect give "
               f"{selector} minecraft:{effect_name} {ticks // 20} {amplifier} true")


def combined(*actions):
    return {"type": "origins:and", "actions": list(actions)}


def active(name, desc, action, cooldown, *, primary=False, crouch=False):
    result = power(name, desc, "origins:active_self", cooldown=cooldown,
                   hud_render={"should_render": True},
                   key={"key": "key.origins.primary_active" if primary
                        else "key.origins.secondary_active"},
                   entity_action=action)
    if crouch:
        result["condition"] = {"type": "origins:sneaking"}
    return result


def periodic(name, desc, action, interval, *, condition=None):
    result = power(name, desc, "origins:action_over_time",
                   interval=interval, entity_action=action)
    if condition:
        result["condition"] = condition
    return result
