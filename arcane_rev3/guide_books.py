"""Minecraft Java 1.18.2 written-book guide, without any custom client mod.

Uses legacy written_book NBT, not 1.20.5+ item components. Books require
players to open them from inventory; vanilla datapacks cannot forcibly open
the book GUI. Book navigation uses safe change_page click events. No book
grants powers, alters player slots or requests elevated permissions.
"""
import json
import textwrap

from progression.catalog import CARDS, ACT_MARKS, RITUALS
from .player_codex import how_to_use


def _text(value, color="black", bold=False):
    return {"text": value, "color": color, "bold": bold}


def _jump(label, page):
    return {"text": label, "color": "dark_blue", "underlined": True,
            "clickEvent": {"action": "change_page", "value": str(page)}}


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
        "Seq1 is LOCKED in normal SMP.",
        "Partial powers are not complete."
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
        "inspect equipped kits in chat.",
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
        "4: fixed second path unlocks.",
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
        offerings = RITUALS[seq]
        items = [f"{n} x {item.replace('_', ' ')}" for item, n in offerings.items()]
        locked = seq == 2
        pages.append(_page(f"SEQUENCE {seq} > {seq-1}", [
            f"{ACT_MARKS[seq]} acting marks needed",
            *items[:2],
            "Sequence 1 is LOCKED." if locked else "Altar: lectern on crying obsidian",
            "Normal SMP cannot" if locked else "Grounded, out of combat.",
            "unlock Resonance." if locked else "Consumes offerings on success.",
        ], prev=len(pages), next_=len(pages)+2))
    # Pages 17-38: all 22 individual pathway acting quests.
    for card in CARDS:
        pages.append(_page(card["name"].upper(), [
            f"Primary path: {card['slug']}",
            "Alternating proof tasks:",
            f"Item: {card['acting_item'].replace('_', ' ')}",
            "Event: " + _event(card["acting_event"]),
            "2 min cooldown per proof.",
            "At Seq4, partner unlocks.",
            "For abilities: /trigger a_tome",
        ], prev=len(pages), next_=(len(pages)+2 if card is not CARDS[-1] else None)))
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
        "Seq1 remains LOCKED.",
        "Powers can be PARTIAL.",
        "Turn pages for ability notes."
    ], home=None, next_=2)]
    for seq in range(9, 1, -1):
        chunk = [r for r in rows if r["sequence"] == seq]
        pages.append(_page(f"SEQUENCE {seq}", [
            "Current source abilities:",
            *[r["name"] + " [" + r["status"].upper() + "]"
              for r in chunk],
            "Turn pages for each power.",
        ], prev=len(pages), next_=len(pages)+2))
        for row in chunk:
            power = compiled.get(row["power_id"], {})
            summary = _short(power.get("description", "No source description."), 115)
            usage = _short(how_to_use(power), 90)
            lines = [
                row["name"],
                row["status"].upper() + " SOURCE",
                "Current: " + summary,
                "Use: " + usage,
            ]
            if row["status"] == "partial":
                lines.append("Missing: " + _short(row["missing"], 110))
            pages.append(_page("ABILITY DETAILS", lines,
                               prev=len(pages), next_=len(pages)+2))
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
    if marker not in ("tarotArcaneGuide:1b", "tarotArcaneTome:1b"):
        raise ValueError("Unrecognized book inventory marker")
    page_strings = [json.dumps(json.dumps(p, ensure_ascii=True), ensure_ascii=True)
                    for p in pages]
    return ("{" + marker + ",title:" + json.dumps(title) +
            ',author:"Tarot Club",generation:0,pages:[' +
            ",".join(page_strings) + "]}")
