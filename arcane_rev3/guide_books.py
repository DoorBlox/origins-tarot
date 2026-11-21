"""Minecraft Java 1.18.2 written-book guide, without any custom client mod.

Uses legacy written_book NBT, not 1.20.5+ item components. Books require
players to open them from inventory; vanilla datapacks cannot forcibly open
the book GUI. Book navigation uses safe change_page click events. No book
grants powers, alters player slots or requests elevated permissions.
"""
import json
import textwrap

from progression.catalog import CARDS, ACT_MARKS, RITUALS
from .player_codex import how_to_use, player_effect_text


def _text(value, color="black", bold=False):
    return {"text": value, "color": color, "bold": bold}


def _jump(label, page):
    return {"text": label, "color": "dark_blue", "underlined": True,
            "clickEvent": {"action": "change_page", "value": str(page)}}


def _action(label, trigger):
    """Book actions may run ONLY explicit player-owned triggers, never admin."""
    accepted = {
        "a_slots", "a_focus_menu", "a_roadmap",
        "a_tome", "a_partner_tome", "a_book", "a_status",
        "a_hud set 2", "a_hud set 3",
    }
    if trigger not in accepted:
        raise ValueError("Unsafe tutorial action")
    return {"text": label, "color": "dark_green", "underlined": True,
            "clickEvent": {"action": "run_command",
                           "value": "/trigger " + trigger}}


def _page(title, lines, *, home=1, prev=None, next_=None):
    """Short, legible pages; stable 1-based page destinations."""
    parts = [_text(title + "\n", "dark_purple", True),
             _text("\n".join(lines), "black")]
    parts.append(_text("\n\n"))
    if home is not None:
        parts.append(_jump("[Index]", home))
    if prev is not None:
        parts.extend([_text(" "), _jump("< Back", prev)])
    if next_ is not None:
        parts.extend([_text(" "), _jump("Next >", next_)])
    return {"text": "", "extra": parts}


def _short(value, limit=175):
    """Truncate only display text, never silently claim full functionality."""
    value = " ".join(str(value).split())
    if len(value) <= limit:
        return value
    return value[:limit-3].rsplit(" ", 1)[0] + "..."


def _event(value):
    if value.startswith("kill:"):
        return "Defeat " + value[5:].replace("_", " ")
    if value.startswith("dimension:"):
        return "Enter " + ("the Nether" if value.endswith("the_nether") else value[10:].replace("_", " "))
    if value.startswith("consume:"):
        return "Eat " + value[8:].replace("_", " ")
    return {"trade": "Trade with villager", "breed": "Breed animals"}.get(
        value, value.replace("_", " "))


def general_pages():
    """Index, how-to, milestone pages and all 22 pathway acting quests."""
    pages = []
    pages.append(_page("ARCANE REV3", [
        "THE TAROT HANDBOOK",
        "22 Major Arcana",
        "Select a page using the arrows.",
        "This book is read-only.",
        "Sequence 1 is not yet",
        "available for ascension."
    ], home=None, next_=2))
    pages.append(_page("START PLAYING", [
        "1. Select a Tarot Origin.",
        "2. Start at Sequence 9.",
        "3. Check your active keybinds.",
        "4. Open your Pathway Tome for abilities.",
        "5. Complete acting proofs.",
        "6. Ascend at a ritual altar."
    ], prev=1, next_=3))
    pages.append(_page("ABILITIES", [
        "Use /trigger a_tome to obtain",
        "your own pathway's Tome.",
        "Use /trigger a_abilities to",
        "get your Pathway Tome.",
        "Use /trigger a_roadmap for",
        "your personal mark count."
    ], prev=2, next_=4))
    pages.append(_page("ACTING PROOFS", [
        "Alternate two proof tasks:",
        "Item held in inventory;",
        "then pathway-specific event.",
        "Each accepted proof adds",
        "one mark. Cooldown: 120s.",
        "Check your pathway page.",
    ], prev=3, next_=5))
    pages.append(_page("RITUAL ALTAR", [
        "Stand on a lectern.",
        "Place crying obsidian",
        "directly under the lectern.",
        "Be on ground, no combat,",
        "not flying with Elytra.",
        "Carry required items.",
        "Then /trigger a_ascend"
    ], prev=4, next_=6))
    pages.append(_page("SEQUENCES", [
        "9-5: kits auto equip.",
        "Sequence 4: second path.",
        "4: six editable slots.",
        "3: seven editable slots.",
        "2: eight editable slots.",
        "1: LOCKED for normal SMP.",
        "Your first Origin drawback",
        "cannot be swapped away."
    ], prev=5, next_=7))
    pages.append(_page("SLOTS", [
        "At Seq4-2, slots can equip",
        "either linked pathway.",
        "One slot = one whole kit.",
        "No duplicates or locked",
        "Sequence kits allowed.",
        "/trigger a_slots",
        "/trigger a_abilities"
    ], prev=6, next_=8))
    pages.append(_page("HOW TO UPGRADE", [
        "Backup entire SMP world,",
        "including playerdata and",
        "scoreboard.dat, before a",
        "new Arcane Rev3 ZIP.",
        "Keep ONLY one Rev3 pack.",
        "Do not mix legacy V2/V3.",
        "Seq1 still locked."
    ], prev=7, next_=9))
    # Pages 9-16 are the eight non-Seq1 progression transitions.
    for seq in range(9, 1, -1):
        locked = seq == 2
        offerings = {} if locked else RITUALS[seq]
        items = [f"{n} x {item.replace('_', ' ')}" for item, n in offerings.items()]
        pages.append(_page(f"SEQUENCE {seq} > {seq-1}", [
            f"{ACT_MARKS[seq]} acting marks needed",
            *items[:2],
            "Sequence 1 is LOCKED." if locked else "Altar: lectern on crying obsidian",
            "Normal SMP cannot" if locked else "Grounded, out of combat.",
            "unlock Resonance." if locked else "Consumes offerings on success.",
        ], prev=len(pages), next_=len(pages)+2))
    # Pages 17-38: all 22 individual pathway acting quests.
    for card in CARDS:
        pages.append(_page(card["name"], [
            f"Primary path: {card['slug']}",
            "Alternating proof tasks:",
            f"Item: {card['acting_item'].replace('_', ' ')}",
            "Event: " + _event(card["acting_event"]),
            "2 min cooldown per proof.",
            "At Seq4, partner unlocks.",
            "For abilities: /trigger a_tome",
        ], prev=len(pages), next_=(len(pages)+2 if card is not CARDS[-1] else None)))
    # Read-only tutorial pages with optional vanilla-trigger shortcuts:
    # clickable triggers never confer OP or bypass existing kit validation.
    tutorials = [
        ("SET UP POWERS", [
            "1. Select a Tarot Origin.",
            "2. Seq9-5 kits equip automatically.",
            "3. Open your Pathway Tome.",
            "4. Bind Origins keys in Controls.",
            "5. At Seq4 use the slot menu.",
            "6. Equip an unlocked kit.",
            "7. Inspect abilities in Tome.",
        ], "a_tome"),
        ("SLOT EQUIPMENT", [
            "At Sequence 4 you get a",
            "fixed linked second pathway.",
            "Open /trigger a_slots.",
            "Choose Edit slot, pathway,",
            "then an UNLOCKED Sequence.",
            "One slot equips a whole kit.",
            "No duplicates or locked kits.",
            "Seq4/3/2: 6/7/8 slots.",
        ], "a_slots"),
        ("FOCUS AND KEYS", [
            "Client Controls > Key Binds",
            "> Origins: Primary & Secondary.",
            "Some active powers share keys.",
            "Use /trigger a_focus_menu",
            "to choose the owned action.",
            "Passive powers work on their",
            "specified event/condition.",
            "Read Tome for each cooldown.",
        ], "a_focus_menu"),
        ("PROGRESS DISPLAY", [
            "Use /trigger a_hud set 2",
            "to show your PRIVATE HUD.",
            "It shows Sequence, marks,",
            "next item/event, and cooldown.",
            "Use /trigger a_hud set 3",
            "to hide it again.",
            "For exact next ritual",
            "use /trigger a_roadmap.",
        ], "a_hud set 2"),
    ]
    for index, (title, lines, trigger) in enumerate(tutorials):
        n = len(pages)
        page = _page(title, lines, prev=n,
                     next_=(n+2 if index < len(tutorials)-1 else None))
        page["extra"].extend([_text("\n"), _action("[OPEN PLAYER MENU]", trigger)])
        pages.append(page)
    # Ensure no dangling forward arrow from final tutorial page.
    pages[-1]["extra"] = [
        part for part in pages[-1]["extra"]
        if not (isinstance(part, dict) and part.get("text") == "Next >")
    ]
    # Main-page jump links avoid clicking through 38 sequential pages.
    pages[0]["extra"].extend([
        _text("\n\n"),
        _jump("[Getting Started]", 2), _text("\n"),
        _jump("[Ascension Costs]", 9), _text("\n"),
        _jump("[All 22 Pathways]", 17), _text("\n"),
        _jump("[Power Setup Tutorial]", 39),
    ])
    if len(pages) > 100:
        raise ValueError("Minecraft books allow at most 100 pages")
    return pages


def pathway_pages(slug, compiled, manifest, kits):
    """Compact, source-honest overview of every Seq9..2 ability of one pathway."""
    card = next((c for c in CARDS if c["slug"] == slug), None)
    if card is None:
        raise ValueError("Unknown Arcana")
    rows = [r for r in manifest if r["family"] == "individual"
            and r["pathway"] == slug and r["sequence"] >= 2]
    pages = [_page(card["name"].upper(), [
        "YOUR PATHWAY TOME",
        f"Primary acting item:",
        card["acting_item"].replace("_", " "),
        "Event: " + _event(card["acting_event"]),
        "Each proof: +1 mark, 120s CD.",
        "Sequence 1 is not unlocked.",
        "Turn pages to learn your",
        "abilities and how to use them."
    ], home=None, next_=2)]
    for seq in range(9, 1, -1):
        chunk = [r for r in rows if r["sequence"] == seq]
        pages.append(_page(f"SEQUENCE {seq}", [
            "Your pathway abilities:",
            *[r["name"] for r in chunk],
            "Turn pages to read what",
            "each ability does."
        ], prev=len(pages), next_=len(pages)+2))
        for row in chunk:
            power = compiled.get(row["power_id"], {})
            summary = _short(player_effect_text(power), 135)
            usage = _short(how_to_use(power), 105)
            lines = [
                row["name"],
                "What it does: " + summary,
                "How to use: " + usage,
            ]
            pages.append(_page("ABILITY DETAILS", lines,
                               prev=len(pages), next_=len(pages)+2))
    # Contents page shortcuts to each source-kit Sequence section, even
    # when each section has a different number of ability detail pages.
    target = 2
    for seq in range(9, 1, -1):
        chunk = [r for r in rows if r["sequence"] == seq]
        pages[0]["extra"].extend([_text("\n"), _jump(f"[Sequence {seq}]", target)])
        target += 1 + len(chunk)
    # Repair the last forward link so it does not point beyond this book.
    last = pages[-1]
    last["extra"] = [
        part for part in last["extra"]
        if not (isinstance(part, dict) and part.get("text") == "Next >")
    ]
    if len(pages) > 100:
        raise ValueError("Pathway abilities exceed book page limit")
    return pages


def book_nbt(title, pages, marker):
    """Literal old 1.18.2 NBT written_book; JSON page strings are double escaped."""
    if len(pages) > 100 or not pages:
        raise ValueError("Expected between 1 and 100 book pages")
    if marker not in ("tarotArcaneGuide:1b", "tarotArcaneTome:1b",
                      "tarotArcanePartnerTome:1b"):
        raise ValueError("Unrecognized book inventory marker")
    page_strings = [json.dumps(json.dumps(p, ensure_ascii=True), ensure_ascii=True)
                    for p in pages]
    return ("{" + marker + ",title:" + json.dumps(title) +
            ',author:"Tarot Club",generation:0,pages:[' +
            ",".join(page_strings) + "]}")


def emit_books(w, compiled, manifest, kits):
    """Give one guide/tome per player, without destroying inventory slots.

    /trigger is processed as the player by tick.mcfunction; on 1.18.2 a
    vanilla written book has to be opened by right-clicking it in hand.
    """
    from .model import PATHWAYS

    guide = book_nbt("Arcane Rev3 Handbook", general_pages(),
                     marker="tarotArcaneGuide:1b")
    w.f("ui/book/give",
        "execute store result score @s a_probe run clear @s minecraft:written_book{tarotArcaneGuide:1b} 0",
        "execute if score @s a_probe matches 0 run give @s minecraft:written_book" +
        guide + " 1",
        "tellraw @s " + json.dumps({
            "text": "[Tarot] Open the Arcane Handbook from your inventory. "
                    "If you already have it, no duplicate is given.",
            "color": "gold"}, separators=(",", ":")))

    w.f("ui/book/tome",
        "execute unless score @s a_init matches 1 run tellraw @s " +
        json.dumps({"text": "[Tarot] Select a Tarot Origin before requesting your pathway tome.",
                    "color": "red"}, separators=(",", ":")),
        [f"execute if score @s a_init matches 1 if score @s a_path matches {card['id']} "
         f"run function tarot_arcane:ui/book/path/{card['slug']}"
         for card in CARDS])

    w.f("ui/book/partner",
        "execute unless score @s a_init matches 1 run tellraw @s " +
        json.dumps({"text": "[Tarot] Select an Origin first.", "color": "red"}),
        "execute unless score @s a_seq matches ..4 run tellraw @s " +
        json.dumps({"text": "[Tarot] Your linked partner becomes available at Sequence 4.",
                    "color": "yellow"}),
        [f"execute if score @s a_init matches 1 if score @s a_seq matches ..4 "
         f"if score @s a_partner matches {card['id']} "
         f"run function tarot_arcane:ui/book/path_partner/{card['slug']}"
         for card in CARDS])

    for card in CARDS:
        slug = card["slug"]
        pages = pathway_pages(slug, compiled, manifest, kits)
        nbt = book_nbt(card["name"] + " Tome", pages,
                       marker="tarotArcaneTome:1b")
        # One book per player at a time; its contents are fixed for the
        # chosen primary pathway. If the pathway changes, the player must
        # store or discard the old book and request the appropriate new one.
        w.f(f"ui/book/path/{slug}",
            "execute store result score @s a_probe run clear @s minecraft:written_book{tarotArcaneTome:1b} 0",
            "execute if score @s a_probe matches 0 run give @s minecraft:written_book" +
            nbt + " 1",
            "tellraw @s " + json.dumps({
                "text": "[Tarot] Open your Pathway Tome in hand. "
                        "Use /trigger a_book for the general handbook.",
                "color": "aqua"}, separators=(",", ":")))
        partner_nbt = book_nbt(card["name"] + " Partner Tome", pages,
                               marker="tarotArcanePartnerTome:1b")
        w.f(f"ui/book/path_partner/{slug}",
            "execute store result score @s a_probe run clear @s minecraft:written_book{tarotArcanePartnerTome:1b} 0",
            "execute if score @s a_probe matches 0 run give @s minecraft:written_book" +
            partner_nbt + " 1",
            "tellraw @s " + json.dumps({
                "text": "[Tarot] Open your partner's Tome in hand. "
                        "Read-only; does not equip or unlock powers.",
                "color": "aqua"}, separators=(",", ":")))
