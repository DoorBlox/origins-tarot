"""Server-only, player-scoped Arcane Rev3 codex and ascension roadmap.

All command targets are static and player-owned. Inspecting never grants
powers, changes progression, reveals another player's data or invokes /op.
The reference manual differentiates the intended Rev2 specification from the
compiled Rev3 subset and its explicit remaining omissions.
"""
import json

from .model import PATHWAYS
from progression.catalog import ACT_MARKS, CARDS, RITUALS

PREFIX = "tarot_arcane:"


def _j(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _f(name):
    return "function " + PREFIX + name


def _msg(message, color="aqua"):
    return "tellraw @s " + _j({"text": "[Tarot] " + message, "color": color})


def _click(label, trigger, color="aqua"):
    """No user-controlled commands. Never put /function or OP actions in UI."""
    if not trigger.startswith("a_") or any(x in trigger for x in ("@", "/", ";", "\n", "\r")):
        raise ValueError("Codex click must use a literal player trigger")
    return "tellraw @s " + _j({
        "text": label, "color": color, "underlined": True,
        "clickEvent": {"action": "run_command", "value": "/trigger " + trigger},
    })


def _score(name):
    return {"score": {"name": "*", "objective": name}}


def _text(line, color="aqua"):
    return "tellraw @s " + _j({
        "text": "[Tarot] " + str(line), "color": color,
    })


def _nodes(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from _nodes(item)
    elif isinstance(value, list):
        for item in value:
            yield from _nodes(item)


def how_to_use(power):
    """Describe only source-backed invocation; no unsupported gameplay claim."""
    kind = power.get("type", "")
    parts = []
    if kind in ("origins:active_self", "origins:fire_projectile"):
        key = power.get("key", {}).get("key", "")
        if key == "key.origins.primary_active":
            parts.append("Primary Origins key")
        elif key == "key.origins.secondary_active":
            parts.append("Secondary Origins key")
        else:
            parts.append("Origins active key")
    elif kind == "origins:action_over_time":
        parts.append("Automatic timed passive")
        if isinstance(power.get("interval"), int):
            parts.append("rechecks every " + str(power["interval"]) + " ticks")
    elif kind in ("origins:target_action_on_hit", "origins:self_action_on_hit"):
        parts.append("Triggers on a hit you deal")
    elif kind in ("origins:self_action_when_hit", "origins:attacker_action_when_hit"):
        parts.append("Triggers when you are hit")
    elif kind == "origins:self_action_on_kill":
        parts.append("Triggers on a kill")
    elif kind == "origins:action_on_entity_use":
        parts.append("Interact with an entity")
    elif kind == "origins:multiple":
        parts.append("Multiple automatic/conditional components")
    else:
        parts.append("Passive or condition-driven")

    conds = list(_nodes(power.get("condition", {})))
    if any(node.get("type") == "origins:sneaking"
           and not node.get("inverted", False) for node in conds):
        parts.append("while sneaking")
    if any(node.get("type") == "origins:daytime"
           and node.get("inverted") is True for node in conds):
        parts.append("at night")
    if any(node.get("type") == "origins:daytime"
           and not node.get("inverted", False) for node in conds):
        parts.append("during daylight")
    if isinstance(power.get("cooldown"), int) and power["cooldown"] > 0:
        ticks = power["cooldown"]
        parts.append("cooldown " + str(ticks) + " ticks (" +
                     str(ticks / 20).rstrip("0").rstrip(".") + " seconds)")
    return "; ".join(parts) + "."


def _acting_event(raw):
    if raw.startswith("kill:"):
        return "Defeat a " + raw.split(":", 1)[1].replace("_", " ")
    if raw.startswith("dimension:"):
        name = raw.split(":", 1)[1]
        return "Enter " + ("the Nether" if name == "the_nether" else name.replace("_", " "))
    if raw.startswith("consume:"):
        return "Consume " + raw.split(":", 1)[1].replace("_", " ")
    return {"trade": "Trade with a villager",
            "breed": "Breed animals"}.get(raw, "Complete " + raw.replace("_", " "))


def emit_player_codex(w, compiled, manifest, kits, innate, num):
    """Generate stable, bounded functions for all currently slottable kits."""
    if len(manifest) != 434 or len(num) != 22:
        raise ValueError("Refuse incomplete player codex")
    by_id = {row["power_id"]: row for row in manifest if row["power_id"]}
    if set(by_id) != set(compiled):
        raise ValueError("Player codex must match emitted source powers exactly")

    w.f("ui/codex/home",
        _msg("ABILITY CODEX | Choose an equipped Sequence kit.", "gold"),
        _msg("Seq9-5 kits auto-equip. Seq4-2 slots are editable. Every selected kit has its own abilities.", "yellow"),
        _msg("Open a kit to learn its abilities and activation controls.", "gray"),
        "execute unless score @s a_init matches 1 run " + _msg(
            "Choose a Tarot Origin to see your own kits.", "red"),
        "execute if score @s a_mode matches 2 run " + _msg(
            "Your current form cannot be changed from this menu.", "red"),
        [f"execute if score @s a_init matches 1 if score @s a_mode matches 0..1 "
         f"if score @s a_max matches {slot}.. run " +
         _click("[View slot " + str(slot) + " abilities]", "a_kit set " + str(slot), "green")
         for slot in range(1, 9)],
        _click("[My progression roadmap]", "a_roadmap", "yellow"),
        _click("[My slots]", "a_slots"),
        _click("[Back to guide]", "a_guide"))

    w.f("ui/codex/open",
        "scoreboard players set @s a_ok 0",
        "execute if score @s a_init matches 1 if score @s a_mode matches 0..1 "
        "if score @s a_kit matches 1..8 if score @s a_kit <= @s a_max "
        "run scoreboard players set @s a_ok 1",
        "execute if score @s a_ok matches 1 run scoreboard players operation @s a_view_slot = @s a_kit",
        [f"execute if score @s a_ok matches 1 if score @s a_view_slot matches {i} "
         f"run scoreboard players operation @s a_view_code = @s a_s{i}"
         for i in range(1, 9)],
        "execute if score @s a_ok matches 1 if score @s a_view_code matches 1.. "
        "run " + _f("ui/codex/show"),
        "execute if score @s a_ok matches 1 if score @s a_view_code matches 0 "
        "run " + _msg("This slot is empty. Use /trigger a_slots to equip a kit.", "yellow"),
        "execute if score @s a_ok matches 0 run " + _msg(
            "Only your unlocked slot numbers can be inspected. Seq1 is a locked test.", "red"))

    entries = [
        _msg("Inspecting your equipped kit; only its owned abilities are viewable.", "gray"),
    ]
    dispatch = [
        "scoreboard players set @s a_ok 0",
        "execute if score @s a_init matches 1 if score @s a_mode matches 0..1 "
        "if score @s a_view_slot <= @s a_max "
        "if score @s a_view_code matches 1.. if score @s a_detail matches 1.. "
        "run scoreboard players set @s a_ok 1",
        [f"execute if score @s a_view_slot matches {i} "
         f"unless score @s a_view_code = @s a_s{i} "
         "run scoreboard players set @s a_ok 0" for i in range(1, 9)],
        "execute unless score @s a_view_slot matches 1..8 "
        "run scoreboard players set @s a_ok 0",
        "execute if score @s a_ok matches 1 run " + _f("ui/codex/detail_dispatch"),
        "execute if score @s a_ok matches 0 run " + _msg(
            "That slot changed or is locked. Open the ability codex again.", "red"),
    ]
    details_dispatch = []
    for slug in PATHWAYS:
        for seq in range(9, 1, -1):
            code = num[slug] * 100 + seq
            fn = f"ui/codex/kit/{slug}_{seq}"
            entries.append(f"execute if score @s a_view_code matches {code} run " + _f(fn))
            kit_ids = list(kits.get((slug, seq), ()))
            if seq == 9 and slug in innate:
                kit_ids.append(innate[slug])
            if not kit_ids:
                raise ValueError(f"Empty playable kit {slug} Seq {seq}")
            shown = [_msg(f"{slug.replace('_', ' ').title()} | Sequence {seq} | "
                          f"{len(kit_ids)} ability entries", "gold"),
                     _msg("Click DETAILS to learn what each ability does and how to use it.", "gray")]
            if seq == 9 and slug == "fool":
                shown.append(_msg(
                    "Permanent identity drawback: Spiritual Expenditure (+25% sprint/glide exhaustion).",
                    "dark_red"))
            for index, ident in enumerate(kit_ids, 1):
                row = by_id[ident]
                implemented = compiled[ident]
                label = f"{index}. {row['name']} [DETAILS]"
                shown.append(_click(label, "a_detail set " + str(index), "aqua"))
                detail_fn = f"ui/codex/detail/{slug}_{seq}_{index}"
                shown_detail = [
                    _msg(row["name"], "gold"),
                    _text("What it does: " +
                          str(implemented.get("description", "See the effects of your equipped ability.")), "aqua"),
                    _text("How to use: " + how_to_use(implemented), "green"),
                ]
                shown_detail.extend([
                    _msg("Use /trigger a_kit set <your slot number> to reopen this kit.", "gray"),
                    _click("[Open Ability Codex]", "a_abilities"),
                    _click("[Ascension roadmap]", "a_roadmap", "yellow"),
                ])
                w.f(detail_fn, shown_detail)
                details_dispatch.append(
                    f"execute if score @s a_view_code matches {code} "
                    f"if score @s a_detail matches {index} run " + _f(detail_fn))
            shown.extend([
                _click("[My slots]", "a_slots"),
                _click("[Ascension roadmap]", "a_roadmap", "yellow"),
                _click("[Codex home]", "a_abilities")])
            w.f(fn, shown)
    w.f("ui/codex/show", entries)
    w.f("ui/codex/detail_dispatch", details_dispatch)
    w.f("ui/codex/detail_open", *dispatch)


def emit_roadmap(w):
    """Precise progression from real ACT_MARKS, RITUALS and CARDS; never grant."""
    w.f("ui/roadmap",
        "execute unless score @s a_init matches 1 run " +
        _msg("Select a Tarot origin before following the ascension roadmap.", "red"),
        "execute if score @s a_init matches 1 run tellraw @s " + _j([
            {"text": "[Tarot] ROADMAP | Your Sequence: ", "color": "gold"},
            _score("a_seq"), {"text": " | Acting marks: "}, _score("a_marks")]),
        "execute if score @s a_init matches 1 run tellraw @s " + _j([
            {"text": "[Tarot] Proof cooldown (ticks remaining): ", "color": "gray"},
            _score("a_actcd"), {"text": " | Combat timer: "}, _score("a_combat")]),
        "execute if score @s a_init matches 1 run tellraw @s " + _j([
            {"text": "[Tarot] Next acting phase (0=item, 1=event): ", "color": "gray"},
            _score("a_phase")]),
        "execute if score @s a_init matches 1 if score @s a_seq matches 2..9 "
        "run " + _f("ui/roadmap/tasks"),
        [f"execute if score @s a_init matches 1 if score @s a_seq matches {seq} "
         f"run " + _f(f"ui/roadmap/seq_{seq}") for seq in range(9, 1, -1)],
        "execute if score @s a_seq matches 1 run " +
        _msg("Sequence 1 is an OP-only Resonance preview; ordinary gameplay does not unlock it.", "red"),
        "execute if score @s a_init matches 1 run " +
        _msg("Ritual altar: STAND ON a lectern with crying obsidian directly below it.", "yellow"),
        "execute if score @s a_init matches 1 run " +
        _msg("Must be grounded, not gliding, and out of combat. Offerings are consumed only on success.", "yellow"),
        "execute if score @s a_init matches 1 if score @s a_seq matches 3..9 run " +
        _click("[Attempt ascension at altar]", "a_ascend", "green"),
        "execute if score @s a_init matches 1 run " +
        _click("[All Sequence milestones]", "a_stages", "light_purple"),
        "execute if score @s a_init matches 1 run " +
        _click("[See abilities I have equipped]", "a_abilities"),
        _click("[Main guide]", "a_guide"))

    # A separate high-level overview lets players plan all future non-Seq1
    # offerings, without exposing any admin transition or editing progress.
    milestones = [_msg("COMPLETE PROGRESSION MAP (normal gameplay ends at Sequence 2)", "gold")]
    for seq in range(9, 1, -1):
        line = f"Sequence {seq} to {seq-1}: {ACT_MARKS[seq]} marks"
        if seq == 2:
            line += " | LOCKED: Sequence 1 is not available yet"
        else:
            line += " | " + ", ".join(
                f"{count} {item.replace('_', ' ')}"
                for item, count in RITUALS[seq].items())
            if seq == 5:
                line += " | fixed partner and 6 slots"
            elif seq in (4, 3):
                line += " | one new editable slot"
        milestones.append(_msg(line, "red" if seq == 2 else "yellow"))
    milestones.extend([
        _msg("All steps additionally require the lectern-on-crying-obsidian altar, grounding and no combat.", "gray"),
        _click("[My next exact task]", "a_roadmap", "green"),
        _click("[Guide]", "a_guide")])
    w.f("ui/stages", milestones)

    tasks = [_msg("Earn acting marks by alternating a pathway item and an action.", "aqua")]
    for card in CARDS:
        base = f"execute if score @s a_path matches {card['id']} "
        tasks.append(base + "if score @s a_phase matches 0 run " + _msg(
            f"NEXT PROOF: Have {card['acting_item'].replace('_', ' ')} in your inventory.",
            "green"))
        tasks.append(base + "if score @s a_phase matches 1 run " + _msg(
            "NEXT PROOF: " + _acting_event(card["acting_event"]) + ".", "green"))
    tasks.append(_msg("Acting rewards are passive advancement events (not a command). Each accepted proof adds one mark and starts a 2400-tick / 2-minute cooldown.", "gray"))
    w.f("ui/roadmap/tasks", tasks)

    for seq in range(9, 1, -1):
        lines = [
            _msg(f"Sequence {seq} to {seq-1}: need {ACT_MARKS[seq]} acting marks.", "gold")
        ]
        if seq == 2:
            lines.extend([
                _msg("LOCKED: Seq2 to Seq1 Resonance is not enabled for normal SMP players.", "red"),
                _msg("Keep your Sequence 2 progression; do not use OP test functions on the SMP.", "red")
            ])
        else:
            items = list(RITUALS[seq].items())
            lines.append(_msg(
                "Ritual offerings (carried in your inventory): " +
                " and ".join(f"{count} {item.replace('_', ' ')}" for item, count in items),
                "yellow"))
            if seq == 5:
                lines.append(_msg(
                    "Next: Sequence 4 unlocks your fixed second pathway and six slots. "
                    "The sixth slot starts empty; equip it from /trigger a_slots.", "light_purple"))
            elif seq in (4, 3):
                lines.append(_msg(
                    f"Next: Sequence {seq-1} unlocks another editable slot; choose a kit from either unlocked pathway.",
                    "light_purple"))
            else:
                lines.append(_msg(
                    "Next: your next Sequence kit is auto-equipped; existing source powers are preserved.",
                    "green"))
        w.f(f"ui/roadmap/seq_{seq}", lines)


def generate_player_manual(manifest, compiled, kits, innate):
    """All 434 abilities, source-labelled and distinguishable from handbook intent."""
    source_full = sum(row["status"] == "full" for row in manifest)
    source_partial = sum(row["status"] == "partial" for row in manifest)
    b = chr(96)
    lines = [
        "# Arcane Rev3 Player Ability Reference",
        "",
        "Generated from the authoritative Rev2 ability catalog and the compiled Rev3 source.",
        "**This file describes source implementations, not verified Minecraft gameplay.**",
        f"Catalog: **{len(manifest)}** abilities | **{source_full}** source-full | "
        f"**{source_partial}** PARTIAL.",
        "",
        "## Start here",
        "",
        "- In Minecraft use /trigger a_guide (or /tarot guide with Command Aliases).",
        "- Use /trigger a_abilities to open one of your EQUIPPED Sequence kits.",
        "- Click [DETAILS] for how to activate the ability, current fallback and its remaining gaps.",
        "- Use /trigger a_roadmap for your current acting proof, marks, offerings, ritual altar and next unlock.",
        "- At Sequence 4 choose a second pathway's kits using the eight editable slots.",
        "- Sequence 1 Resonance remains LOCKED during normal gameplay; source entries below are not permission to unlock them.",
        "- Non-Tarot players, teammates, neutral players and enemy teams follow explicit server targeting policy.",
        "",
        "## The full specification versus what the datapack does",
        "",
        "**Actual in-game (compiled source)** = the current gameplay description, pending runtime verification.",
        "**How to use** = source-backed trigger, cooldown and conditions where known.",
        "**Still missing** = features the handbook requires but the datapack cannot yet fully reproduce.",
        "**Original intent** = Rev2 handbook text for comparison; it is not a promise of working gameplay.",
        "",
    ]
    by_key = {(r["family"], r["pathway"], r["sequence"]): []
              for r in manifest}
    for row in manifest:
        by_key[(row["family"], row["pathway"], row["sequence"])].append(row)
    for family, title in (("individual", "22 individual Major Arcana pathways"),
                          ("resonance", "11 paired Resonances (Seq1 locked)")):
        lines.extend(["## " + title, ""])
        seen_paths = []
        for row in manifest:
            if row["family"] == family and row["pathway"] not in seen_paths:
                seen_paths.append(row["pathway"])
        for slug in seen_paths:
            lines.extend(["### " + slug.replace("_", " ").title(), ""])
            for seq in range(9, -1, -1):
                entries = by_key.get((family, slug, seq), [])
                if not entries:
                    continue
                lines.extend(["#### Sequence " + str(seq), ""])
                for row in entries:
                    power_id = row["power_id"]
                    power = compiled.get(power_id, {}) if power_id else {}
                    status = row["status"].upper()
                    pinned = (family == "individual" and seq == 9 and
                              innate.get(slug) == power_id)
                    lines.extend([
                        "- **" + row["name"] + "** — " + status +
                        ("; immutable Origin drawback" if pinned else "") +
                        " | " + b + (power_id or "unimplemented") + b,
                        "  - Actual in-game (compiled source): " +
                        str(power.get("description", "No executable implementation.")),
                        "  - How to use: " + how_to_use(power) if power else
                        "  - How to use: Blocked; no functional trigger.",
                    ])
                    if row["status"] == "partial":
                        lines.append("  - Still missing: " + row["missing"])
                    if row["status"] == "blocked":
                        lines.append("  - Still missing: " + row["missing"])
                    lines.append("  - Original intent (Rev2): " + str(row["source"]))
                    for detail in row.get("details", []):
                        lines.append("    - " + str(detail))
                lines.append("")
    lines.extend([
        "---",
        "Never confuse an installed, source-compiled power with a full 1.18.2 loader/gameplay test.",
        "For SMP upgrades, back up the entire world and restore as a unit if necessary.",
        "",
    ])
    return "\n".join(lines)
