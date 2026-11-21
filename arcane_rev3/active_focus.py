"""Opt-in, player-owned ACTIVE KEY focus for Origins/Apoli 1.4.1.

Many granted active_self powers share G/H. This creates invisible, synced
power tokens and a non-OP clickable menu so the user can focus ONE owned
ability without simultaneous activation of every other granted active.
Default behavior is unchanged (legacy all-key mode) until the player opts in.

Do NOT gate active_self on origins:scoreboard: that condition only evaluates
server-side, and old Origins processes active key conditions on the client.
Use origins:power (synced) with purely server-owned focus token sources;
server validates parent power possession before every selection. Untrusted
players can only use vanilla /trigger, not /power grant or /function.
"""
import hashlib
import json


FOCUS_SOURCE = "tarot_arcane:ability_focus"
FOCUS_ENABLED = "tarot_arcane:focus/enabled"


def token_id(code):
    if not isinstance(code, int) or code < 2 or code > 2_000_000_000:
        raise ValueError("Focus token codes must be safe positive trigger integers")
    return f"tarot_arcane:focus/token_{code}"


def _stable_code(focus_id):
    # Stable across catalog ordering, Python process hash seeds and added
    # source abilities. Collision causes a safe build failure, not re-keying
    # existing players to a new or unexpected ability.
    digest = hashlib.sha256(focus_id.encode("utf-8")).digest()
    return (int.from_bytes(digest[:8], "big") % 1_999_999_999) + 2


def _active_power_nodes(value, path=()):
    if not isinstance(value, dict):
        return
    kind = value.get("type")
    if kind == "origins:active_self":
        yield path, value
    elif kind == "origins:multiple":
        for key in sorted(value):
            child = value[key]
            if (key not in ("type", "name", "description", "condition", "hidden")
                    and isinstance(child, dict)):
                yield from _active_power_nodes(child, path + (key,))


def apply_active_focus(compiled):
    """In-place gated output JSON + stable selection inventory.

    This is called ONLY by full_build after compile_powers. It never changes
    manifest source status, handbook powers or compiled-power declarations.
    """
    entries = []
    codes = set()
    for ident in sorted(compiled):
        obj = compiled[ident]
        for path, active in _active_power_nodes(obj):
            focus_id = ident + ("#" + "/".join(path) if path else "")
            code = _stable_code(focus_id)
            if code in codes:
                raise ValueError(f"Active key stable-ID collision at {focus_id}")
            codes.add(code)
            token = token_id(code)

            legacy = {"type": "origins:power",
                      "power": FOCUS_ENABLED, "inverted": True}
            selected = {"type": "origins:power", "power": token}
            focus_gate = {"type": "origins:or",
                          "conditions": [legacy, selected]}
            original = active.get("condition")
            active["condition"] = (
                {"type": "origins:and", "conditions": [original, focus_gate]}
                if isinstance(original, dict) else focus_gate
            )
            source_name = obj.get("name", focus_id)
            extra = " / " + "/".join(path) if path else ""
            entries.append({
                "focus_id": focus_id, "source_id": ident, "code": code,
                "token": token, "label": str(source_name) + extra,
                "key": active.get("key", {}).get(
                    "key", "key.origins.primary_active"),
            })
    return entries


def _msg(message, color="aqua"):
    return "tellraw @s " + json.dumps(
        {"text": "[Tarot] " + message, "color": color},
        separators=(",", ":"), ensure_ascii=False)


def _clickable(label, trigger):
    return "tellraw @s " + json.dumps(
        {"text": label, "color": "aqua",
         "clickEvent": {"action": "run_command",
                        "value": "/trigger a_choose set " + str(trigger)},
         "hoverEvent": {"action": "show_text",
                        "contents": {"text": "Focus this owned power (no OP required)"}}},
        separators=(",", ":"), ensure_ascii=False)


def emit_focus(w, entries):
    """Server-only binding UI and client-synced power token definitions."""
    w.j("data/tarot_arcane/powers/focus/enabled.json", {
        "type": "origins:simple", "hidden": True,
        "name": "Arcane internal focus enabled",
        "description": "Internal selection flag; never a handbook ability",
    })
    for entry in entries:
        w.j("data/tarot_arcane/powers/focus/token_" +
            str(entry["code"]) + ".json", {
                "type": "origins:simple", "hidden": True,
                "name": "Arcane internal focused action token",
                "description": "Internal non-OP active key selection",
            })

    w.f("ui/focus/legacy",
        "power revokeall @s " + FOCUS_SOURCE,
        "scoreboard players set @s a_focus 0",
        "scoreboard players set @s a_ok 1",
        _msg("Legacy hotkeys restored; multiple equipped actives may share a key.", "yellow"))

    menu = [
        _msg("Choose one equipped active ability to prevent shared-key collisions."),
        _clickable("[Legacy hotkeys: allow all active powers]", 1),
        _msg("Only currently owned abilities appear; choosing does not grant new skills.", "gray"),
    ]
    choose = [
        "scoreboard players set @s a_ok 0",
        "execute if score @s a_choose matches 1 run function tarot_arcane:ui/focus/legacy",
    ]
    validate = ["scoreboard players set @s a_ok 0"]
    for entry in entries:
        code, ident, token = (
            entry["code"], entry["source_id"], entry["token"]
        )
        w.f(f"ui/focus/set/{code}",
            "power revokeall @s " + FOCUS_SOURCE,
            "power grant @s " + FOCUS_ENABLED + " " + FOCUS_SOURCE,
            "power grant @s " + token + " " + FOCUS_SOURCE,
            f"scoreboard players set @s a_focus {code}",
            _msg("Focused: " + entry["label"] +
                 ". Press the ability's existing Origins key.", "green"))

        menu.extend([
            "execute store success score @s a_has run power has @s " + ident,
            "execute if score @s a_has matches 1 run " +
            _clickable("[" + entry["label"] + "]", code),
        ])
        choose.extend([
            f"execute if score @s a_choose matches {code} "
            "store success score @s a_ok run power has @s " + ident,
            f"execute if score @s a_choose matches {code} "
            "if score @s a_ok matches 1 run function "
            f"tarot_arcane:ui/focus/set/{code}",
        ])
        validate.append(
            f"execute if score @s a_focus matches {code} "
            "store success score @s a_ok run power has @s " + ident)

    choose.append(
        "execute unless score @s a_ok matches 1 run " +
        _msg("That active ability is not currently owned.", "red"))

    validate.extend([
        "execute if score @s a_focus matches 2.. "
        "unless score @s a_ok matches 1 run function tarot_arcane:ui/focus/legacy",
        # A stale marker with no scoreboard choice can appear after
        # interrupted restore; reset to safe legacy rather than disabling
        # other active powers until an admin manually fixes the source.
        "execute if score @s a_focus matches 0 "
        "store success score @s a_has run power has @s " + FOCUS_ENABLED,
        "execute if score @s a_focus matches 0 "
        "if score @s a_has matches 1 run function tarot_arcane:ui/focus/legacy",
    ])

    w.f("ui/focus/menu", menu)
    w.f("ui/focus/choose", choose)
    w.f("ui/focus/validate", validate)
