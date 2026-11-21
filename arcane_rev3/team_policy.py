"""Fail-closed team-aware player effects for Minecraft 1.18.2.

The server's vanilla /team scoreboard is authoritative, NOT a LuckPerms
permission group or Origin card. No auto-join or global team mutation occurs.

For each configured caster team, issue only commands against distinct
allowlisted opponent teams. Unassigned players and players in other Minecraft
teams are neutral. This avoids both friendly fire and accidental punishment
of staff/spectator groups. Admins configure membership outside the datapack.

These helpers generate static Origins 1.4.1 execute_command entity actions.
They are intentionally *not* generic open-ended command composition.
"""
import json
import re
from pathlib import Path

from .batches.shared import cmd


ROOT = Path(__file__).resolve().parent.parent
_VALID_TEAM = re.compile(r"[A-Za-z0-9_.-]{1,16}\Z")
_VALID_EFFECT = re.compile(r"[a-z_]{2,48}\Z")


def team_names(root=ROOT):
    raw = json.loads((Path(root) / "arcane" / "teams.json").read_text(encoding="utf8"))
    if raw.get("mode") != "explicit_vanilla_teams":
        raise ValueError("Arcane team mode must stay explicit_vanilla_teams")
    names = raw["teams"]
    if not isinstance(names, list) or not 2 <= len(names) <= 8:
        raise ValueError("Arcane requires 2..8 explicit vanilla scoreboard teams")
    if any(not isinstance(t, str) or not _VALID_TEAM.fullmatch(t) for t in names):
        raise ValueError("Unsafe team name for a vanilla selector")
    if len(names) != len(set(names)):
        raise ValueError("Duplicate vanilla scoreboard teams")
    if raw.get("unassigned_players") != "neutral_no_player_damage_or_debuffs":
        raise ValueError("Unassigned players must not become automatic enemies")
    return tuple(names)


def player_effect(effect, duration, radius, amplifier=0, *, allies=False, root=ROOT):
    """Emit static player-targeted effect actions safe for listed team pairs.

    Only potion effects; positive actions target allies *except caster* and
    negatives target explicit other-team members. Radius is within 64 blocks,
    never globally applied. Effects are in whole seconds, like shared.effect.
    """
    if not isinstance(effect, str) or not _VALID_EFFECT.fullmatch(effect):
        raise ValueError("Unsafe status-effect identifier")
    if type(duration) is not int or duration < 20 or duration > 2400 or duration % 20:
        raise ValueError("Duration must be 20..2400 whole ticks")
    if type(radius) is not int or not 1 <= radius <= 64:
        raise ValueError("Nearby distance must be 1..64 blocks")
    if type(amplifier) is not int or not 0 <= amplifier <= 4:
        raise ValueError("Potion amplifier must be a small positive integer")

    teams = team_names(root)
    actions = []
    for source in teams:
        targets = (source,) if allies else (t for t in teams if t != source)
        for target in targets:
            selector = f"@a[team={target},distance={'0.01..' if allies else '..'}{radius}]"
            command = (
                f"execute if entity @s[team={source}] at @s "
                f"run effect give {selector} minecraft:{effect} "
                f"{duration // 20} {amplifier} true"
            )
            actions.append(cmd(command))
    return {"type": "origins:and", "actions": actions}


def enemy_effect(effect, duration, radius, amplifier=0, *, root=ROOT):
    return player_effect(effect, duration, radius, amplifier, root=root)


def ally_effect(effect, duration, radius, amplifier=0, *, root=ROOT):
    return player_effect(effect, duration, radius, amplifier, allies=True, root=root)
