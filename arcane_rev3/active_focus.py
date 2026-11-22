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
                "description": str(active.get("description") or obj.get("description") or ""),
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


def _book_nbt(title, pages, marker, extra_nbt=""):
    """1.18.2 written-book pages; each page is a JSON component stored as SNBT."""
    if not 1 <= len(pages) <= 100:
        raise ValueError("Focus book exceeds 1.18.2 page limits")
    page_strings = [json.dumps(json.dumps(page, ensure_ascii=True), ensure_ascii=True)
                    for page in pages]
    return ("{" + marker + extra_nbt + ",title:" + json.dumps(title) +
            ',author:"Tarot Club",generation:0,pages:[' +
            ",".join(page_strings) + "]}")


def _part(label, *, page=None, trigger=None):
    obj = {"text": label, "color": "dark_blue", "underlined": True}
    if page is not None:
        obj["clickEvent"] = {"action": "change_page", "value": str(page)}
    if trigger is not None:
        obj["color"] = "dark_green"
        obj["clickEvent"] = {"action": "run_command", "value": "/trigger " + trigger}
    return obj


def _trim(value, length=125):
    value = " ".join(str(value).split())
    return value if len(value) <= length else value[:length-3].rsplit(" ", 1)[0] + "..."


def focus_index_pages(count):
    """Index exposes available slot NUMBERS, never the global ability catalogue."""
    if not isinstance(count, int) or not 1 <= count <= 8:
        raise ValueError("Invalid available slot count")
    pages = []
    for first in range(1, count + 1, 4):
        parts = [
            {"text": "ABILITY FOCUS\n", "color": "dark_purple", "bold": True},
            {"text": "Open one of your equipped slots:\n\n", "color": "black"},
        ]
        for slot in range(first, min(count + 1, first + 4)):
            parts.extend([_part("[Slot " + str(slot) + "]",
                                trigger="a_focus_kit set " + str(slot)),
                          {"text": "\n", "color": "black"}])
        parts.extend([{"text": "\n", "color": "black"},
                      _part("[Allow shared hotkeys]", trigger="a_choose set 1"),
                      {"text": "\n", "color": "black"},
                      {"text": "Open the selected slot book to pick an active power.",
                       "color": "dark_gray"}])
        if first > 1:
            parts.extend([{"text": "\n", "color": "black"},
                          _part("[Back]", page=len(pages))])
        if first + 4 <= count:
            parts.extend([{"text": "  ", "color": "black"},
                          _part("[Next]", page=len(pages)+2)])
        pages.append({"text": "", "extra": parts})
    return pages


def focus_kit_pages(entries, kits):
    """Each kit's book contains ONLY its activatable entries, not locked kits."""
    pages_by_kit = {}
    by_source = {}
    for entry in entries:
        by_source.setdefault(entry["source_id"], []).append(entry)
    from .model import PATHWAYS
    for key, power_ids in sorted(kits.items()):
        if key[0] not in PATHWAYS or key[1] < 2 or key[1] > 9:
            continue  # Resonance and locked Sequence 1/0 are not player-editable kits.
        owned = [entry for ident in power_ids for entry in by_source.get(ident, [])]
        if not owned:
            continue
        pages = []
        for i, entry in enumerate(owned):
            control = ("Primary key" if entry["key"] == "key.origins.primary_active"
                       else "Secondary key")
            parts = [
                {"text": "FOCUS | " + key[0].replace("_", " ").title() +
                         " S" + str(key[1]) + "\n", "color": "dark_purple", "bold": True},
                {"text": "\n" + entry["label"] + "\n", "color": "black", "bold": True},
                {"text": control + "\n", "color": "dark_gray"},
                {"text": _trim(entry.get("description", ""), 135) + "\n\n",
                 "color": "black"},
                _part("[Select this ability]", trigger="a_choose set " +
                      str(entry["code"])),
                {"text": "\n\n", "color": "black"},
            ]
            if i > 0:
                parts.append(_part("[Back]", page=i))
            if i + 1 < len(owned):
                parts.extend([{"text": "  ", "color": "black"},
                              _part("[Next]", page=i+2)])
            pages.append({"text": "", "extra": parts})
        if len(pages) > 100:
            raise ValueError("Focus kit has over 100 active abilities")
        pages_by_kit[key] = pages
    return pages_by_kit


def emit_focus(w, entries, kits):
    """Generate 1.18.2 focus books with server-gated kit and ability selection."""
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
        _msg("Shared hotkeys enabled; multiple equipped active abilities may activate.", "yellow"))

    # Do not give multiple copies on repeated menu requests, or expose
    # unavailable kits in a giant chat list. A newly unlocked slot count
    # receives a different index book without deleting earlier books.
    for count in range(1, 9):
        marker = "tarotArcaneFocusIndex:1b"
        extra = ",tarotFocusSlotCount:" + str(count)
        nbt = _book_nbt("Ability Focus", focus_index_pages(count), marker, extra)
        query = "minecraft:written_book{" + marker + extra + "}"
        w.f("ui/focus/index/" + str(count),
            "execute store success score @s a_has run clear @s " + query + " 0",
            "execute unless score @s a_has matches 1 run give @s minecraft:written_book" + nbt + " 1")

    menu = [
        "execute if score @s a_init matches 1 if score @s a_max matches 1..8 "
        "run scoreboard players set @s a_ok 1",
    ]
    menu.extend(
        f"execute if score @s a_init matches 1 if score @s a_max matches {n} "
        f"run function tarot_arcane:ui/focus/index/{n}"
        for n in range(1, 9))
    w.f("ui/focus/menu", menu)

    # Kit selection is resolved from the player's current, server-managed
    # a_sN slot code and maximum slot count, never from book-supplied paths.
    select = ["scoreboard players set @s a_focus_lookup 0"]
    for slot in range(1, 9):
        select.append(
            f"execute if score @s a_init matches 1 if score @s a_max matches {slot}.. "
            f"if score @s a_focus_kit matches {slot} "
            f"run scoreboard players operation @s a_focus_lookup = @s a_s{slot}")
    for (slug, seq), pages in focus_kit_pages(entries, kits).items():
        from .model import PATHWAYS
        slot_code = (PATHWAYS.index(slug) + 1) * 100 + seq
        name = slug + "_s" + str(seq)
        marker = "tarotArcaneFocusKit:1b"
        extra = ",tarotArcaneFocusKitId:" + json.dumps(name)
        book = _book_nbt("Focus: " + slug.replace("_", " ").title() +
                         " S" + str(seq), pages, marker, extra)
        query = "minecraft:written_book{" + marker + extra + "}"
        w.f("ui/focus/book/" + name,
            "execute store success score @s a_has run clear @s " + query + " 0",
            "execute unless score @s a_has matches 1 run give @s minecraft:written_book" + book + " 1")
        select.append(
            f"execute if score @s a_focus_lookup matches {slot_code} "
            f"run function tarot_arcane:ui/focus/book/{name}")
    select.append(
        "execute if score @s a_focus_lookup matches 0 run " +
        _msg("This slot is empty or not unlocked.", "red"))
    w.f("ui/focus/open_kit", select)

    choose = [
        "scoreboard players set @s a_ok 0",
        "execute if score @s a_choose matches 1 run function tarot_arcane:ui/focus/legacy",
    ]
    validate = ["scoreboard players set @s a_ok 0"]
    for entry in entries:
        code, ident, token = entry["code"], entry["source_id"], entry["token"]
        w.f(f"ui/focus/set/{code}",
            "power revokeall @s " + FOCUS_SOURCE,
            "power grant @s " + FOCUS_ENABLED + " " + FOCUS_SOURCE,
            "power grant @s " + token + " " + FOCUS_SOURCE,
            f"scoreboard players set @s a_focus {code}",
            _msg("Focused: " + entry["label"] +
                 ". Press the corresponding Origins active key.", "green"))
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
        _msg("That ability is not currently equipped.", "red"))
    validate.extend([
        "execute if score @s a_focus matches 2.. "
        "unless score @s a_ok matches 1 run function tarot_arcane:ui/focus/legacy",
        "execute if score @s a_focus matches 0 "
        "store success score @s a_has run power has @s " + FOCUS_ENABLED,
        "execute if score @s a_focus matches 0 "
        "if score @s a_has matches 1 run function tarot_arcane:ui/focus/legacy",
    ])
    w.f("ui/focus/choose", choose)
    w.f("ui/focus/validate", validate)
