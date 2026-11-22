"""Generate linkable, player-readable Arcane Rev3 reference from the compiled player manual.

Usage: python -m arcane_rev3.full_build && python tools/build_player_wiki.py
Check: python tools/build_player_wiki.py --check
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path
from arcane_rev3.model import PARTNER
from progression.catalog import CARDS, ACT_MARKS, RITUALS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "player"
T = chr(96)
def code(s): return T + s + T
def anchor(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
def event(s):
    if s.startswith("kill:"): return "Defeat " + s[5:].replace("_"," ")
    if s.startswith("consume:"): return "Consume " + s[8:].replace("_"," ")
    if s.startswith("dimension:"): return "Enter the Nether" if s.endswith("the_nether") else "Enter " + s[10:].replace("_"," ")
    return {"trade":"Trade with a villager","breed":"Breed animals"}.get(s,s)

def parse(path):
    data = {}
    cur = None
    seq = None
    power = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("### "):
            name = line[4:].strip()
            slug = name.lower().removeprefix("the ").replace(" ","_")
            cur = {"name":name,"sequences":{},"weakness":None}
            data[slug] = cur; seq = None; power = None
        elif line.startswith("#### Sequence "):
            seq = int(line[14:]); cur["sequences"][seq] = []; power = None
        elif line.startswith("- **") and cur is not None and seq is not None:
            match = re.match(r"^- \*\*(.+?)\*\*(?: \(permanent Origin trait\))?$",line)
            if not match: raise ValueError("Unknown ability row " + line)
            power = {"name":match.group(1),"effect":"","usage":""}
            cur["sequences"][seq].append(power)
            if "(permanent Origin trait)" in line: cur["weakness"] = power
        elif line.startswith("  - What it does: ") and power:
            power["effect"] = line[18:].strip()
        elif line.startswith("  - How to use: ") and power:
            power["usage"] = line[16:].strip()
    data["fool"]["weakness"] = {"name":"Spiritual Expenditure",
        "effect":"Sprinting and Elytra flight use 25% more exhaustion."}
    if set(data) != {c["slug"] for c in CARDS}: raise ValueError("Expected 22 pathways")
    for slug,v in data.items():
        if set(v["sequences"]) != set(range(2,10)): raise ValueError("Missing Sequence in " + slug)
        if not v["weakness"]: raise ValueError("Missing weakness in " + slug)
        for powers in v["sequences"].values():
            if not powers or any(not x["effect"] or not x["usage"] for x in powers):
                raise ValueError("Incomplete compiled text in " + slug)
    return data

def page(card, data):
    slug=card["slug"]; partner=PARTNER[slug]
    pname=next(c["name"] for c in CARDS if c["slug"]==partner)
    weak=data["weakness"]
    lines=["# " + card["name"] + " — Arcane Rev3","",
      "[All pathways](../PATHWAYS.md) · [Player handbook](../README.md) · [Controls](../CONTROLS.md) · [Ascension](../ASCENSION.md)","",
      "> Compiled, current-build effect descriptions. Normal playable progression is Sequence 9–2. Higher-level skills shown here still require unlocking their kits. Actual SMP runtime acceptance remains pending.","",
      "## At a glance","",
      "| Property | Value |","|---|---|",
      "| Specialty | " + card["focus"].title() + " |",
      "| Partner from Sequence 4 | ["+pname+"]("+partner+".md) |",
      "| Gliding | "+("Built-in Elytra" if card["glider"] else "No built-in Elytra")+" |",
      "| Acting item | "+card["acting_item"].replace("_"," ")+" |",
      "| Acting event | "+event(card["acting_event"])+" |",
      "| Permanent weakness | ["+weak["name"]+"](#permanent-weakness) |",
      "","## Table of contents","",
      "- [Permanent weakness](#permanent-weakness)",
      "- [Using your keys and Focus](#using-your-keys-and-focus)"]
    for seq in range(9,1,-1):lines.append(f"- [Sequence {seq}](#sequence-{seq})")
    lines+=["","## Permanent weakness","",
      "**"+weak["name"]+":** "+weak["effect"],"",
      "This is attached to your original Origin and persists when you edit Sequence slots. Read the individual ability conditions below for other situational penalties.","",
      "## Using your keys and Focus","",
      "Configure Primary/Secondary Active Power in Options → Controls → Key Binds → Origins. G and H are suggestions, not fixed keys. Use "+code("/trigger a_focus_menu")+" → choose an equipped slot → open its Focus book → click an active ability → Select this ability. Passives activate without a key. [Detailed controls](../CONTROLS.md).",""]
    for seq in range(9,1,-1):
        powers=data["sequences"][seq]
        lines+=["## Sequence "+str(seq),"","[↑ Contents](#table-of-contents) · [Ascension guide](../ASCENSION.md)","","**Jump to an ability:**"]
        for power in powers:
            lines.append("- ["+power["name"]+"](#seq-"+str(seq)+"-"+anchor(power["name"])+")")
        lines.append("")
        for power in powers:
            lines+=['<a id="seq-'+str(seq)+"-"+anchor(power["name"])+'"></a>',
                "### "+power["name"],"",
                "**What it does:** "+power["effect"],"",
                "**How to use:** "+power["usage"],"",
                "[↑ Sequence "+str(seq)+"](#sequence-"+str(seq)+") · [↑ Contents](#table-of-contents)",""]
    lines+=["---","",
       "Next: ["+pname+" (your linked partner)]("+partner+".md) · [All pathways](../PATHWAYS.md) · [Common issues](../TROUBLESHOOTING.md).",
       "","This reference is built from the same current source-compiled player descriptions used for in-game Tomes; it does not promise scripted/lore effects that are not present. Sequence 1/0 remain inaccessible in normal play.",""]
    return "\n".join(lines)

def home():
    lines=["# Arcane Rev3 — Complete Player Handbook","",
     "**Minecraft Java 1.18.2 · Fabric · Origins 1.4.1**. Choose one of 22 Origins, ascend from Sequence 9 toward Sequence 2, and use interactive in-game books to understand your abilities. **This is the Arcane Rev3 developer/test pack, not legacy Tarot V2/V3.**","",
     "> Source changes do not automatically update an SMP. The latest Arcane ZIP has not passed complete live multiplayer acceptance. Ask the server administrator before upgrading an existing world.","",
     "## Table of contents","",
     "1. [Start here — first five minutes](START_HERE.md)",
     "2. [Keybinds, interactive books, and Focus](CONTROLS.md)",
     "3. [Sequences, acting marks, and rituals](ASCENSION.md)",
     "4. [All pathways, partners, and permanent weaknesses](PATHWAYS.md)",
     "5. [All current normal-pathway abilities](#all-22-pathways)",
     "6. [Troubleshooting and common questions](TROUBLESHOOTING.md)",
     "7. [Server upgrade and rollback safety](SERVER_SETUP.md)","",
     "## All 22 pathways","",
     "Choose any pathway for **direct Sequence links, named individual abilities, current effects, how-to-use instructions, and permanent weaknesses**:",""]
    for c in CARDS:lines.append("- ["+c["name"]+"](pathways/"+c["slug"]+".md)")
    lines+=["","## In-game shortcuts","",
      "- "+code("/trigger a_book")+" — interactive main Handbook.",
      "- "+code("/trigger a_tome")+" — your Pathway Tome.",
      "- "+code("/trigger a_partner_tome")+" — partner's read-only Tome from Sequence 4.",
      "- "+code("/trigger a_focus_menu")+" — interactive Focus book for your equipped slot abilities.",
      "- "+code("/trigger a_slots")+" — edit your kit slots.",
      "- "+code("/trigger a_roadmap")+" — your next task, marks, offerings, and ascension.",
      "- "+code("/trigger a_hud set 2")+" — show personal HUD; "+code("/trigger a_hud set 3")+" hides it.","",
      "Books must be **held and right-clicked**; safe hyperlinks navigate inside the vanilla book UI. No optional Command Aliases setup is required for these vanilla triggers.","",
      "## Sources","",
      "This reference is generated from the **player-facing ability text emitted by the Arcane Rev3 build**, plus the canonical [progression catalogue](../../progression/catalog.py) and [partner model](../../arcane_rev3/model.py). It intentionally excludes inaccessible Seq1/0 Resonance and developer-only diagnostic labels. See the [developer tracker](https://github.com/DoorBlox/origins-tarot/issues/20) for release gates.",""]
    return "\n".join(lines)

def paths_index(data):
    lines=["# Choose your Arcana","",
      "[Player handbook](README.md) · [Start here](START_HERE.md) · [Controls](CONTROLS.md)","",
      "Click a name for **all normal Sequence 9–2 abilities**, how they work, acting requirements and the permanent weakness. Linked partners become available at Sequence 4.","",
      "| Origin | Linked partner | Permanent weakness | Glider |","|---|---|---|---|"]
    names={c["slug"]:c["name"] for c in CARDS}
    for c in CARDS:
        slug=c["slug"]; p=PARTNER[slug]
        lines.append("| ["+c["name"]+"](pathways/"+slug+".md) | ["+names[p]+"](pathways/"+p+".md) | ["+data[slug]["weakness"]["name"]+"](pathways/"+slug+".md#permanent-weakness) | "+("Yes" if c["glider"] else "No")+" |")
    lines+=["","[Back to the player handbook](README.md)",""]
    return "\n".join(lines)

def ascension():
    lines=["# Acting marks, rituals, and ascension","",
      "[Player handbook](README.md) · [All pathways](PATHWAYS.md) · [Keybinds](CONTROLS.md)","",
      "## Table of contents","",
      "- [Sequence milestones](#sequence-milestones)",
      "- [How acting marks work](#how-acting-marks-work)",
      "- [All 22 acting tasks](#all-22-acting-tasks)",
      "- [Ritual offering requirements](#ritual-offering-requirements)",
      "- [How to ascend](#how-to-ascend)","",
      "## Sequence milestones","",
      "| Sequence | Available equipment |","|---|---|",
      "| 9 | One auto-equipped primary kit |",
      "| 8–5 | Primary kits accumulate automatically |",
      "| 4 | Fixed partner unlocks, six editable kit slots |",
      "| 3 | Seven editable slots |",
      "| 2 | Eight editable slots; normal progression stops here |",
      "| 1–0 | Not available through ordinary ascension |","",
      "## How acting marks work","",
      "Acting alternates **ITEM → EVENT → ITEM** for your permanent *primary* pathway even if your partner is unlocked. An item proof means having the listed item in inventory; it does not consume it. Each accepted proof gives one mark and starts a **2,400 tick (120 second)** cooldown. Run "+code("/trigger a_roadmap")+" to see the next task, timer and ritual requirements.","",
      "## All 22 acting tasks","",
      "| Pathway | Item in inventory | Required event |","|---|---|---|"]
    for c in CARDS:
        lines.append("| ["+c["name"]+"](pathways/"+c["slug"]+".md) | "+c["acting_item"].replace("_"," ")+" | "+event(c["acting_event"])+" |")
    lines+=["","## Ritual offering requirements","",
      "| Sequence → next | Marks required | Items for successful ritual |","|---|---:|---|"]
    for seq in range(9,1,-1):
        items=" + ".join(f"{n} × {item.replace('_',' ')}" for item,n in RITUALS[seq].items())
        if seq == 2: items="**Locked in normal play; no offerings consumed**"
        lines.append(f"| {seq} → {seq-1} | {ACT_MARKS[seq]} | {items} |")
    lines+=["","## How to ascend","",
      "Stand **on a lectern with crying obsidian directly beneath it**, be grounded (not gliding), out of combat for **200 ticks / 10 seconds**, carry the correct offerings, and have sufficient acting marks. Then type "+code("/trigger a_ascend")+". Successful rituals consume the listed offerings; locked Sequence 1 does not.","",
      "Sequence 1, Sequence 0 and the corresponding Resonance suites remain unavailable via ordinary play. Do not try the operator-only developer preview on a regular SMP.","",
      "[↑ Table of contents](#table-of-contents) · [Player handbook](README.md)",""]
    return "\n".join(lines)

def create_docs(data):
    files={OUT/"README.md":home(),OUT/"PATHWAYS.md":paths_index(data),
           OUT/"ASCENSION.md":ascension()}
    for c in CARDS:files[OUT/"pathways"/(c["slug"]+".md")]=page(c,data[c["slug"]])
    return files

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--reference",type=Path,default=ROOT/"output"/"Arcane_Rev3_Player_Ability_Reference.md")
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    if not args.reference.is_file():ap.error("Build first using python -m arcane_rev3.full_build")
    docs=create_docs(parse(args.reference))
    for path,text in docs.items():
        result=text.rstrip()+"\n"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8")!=result:
                raise SystemExit("Stale generated wiki: "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(result,encoding="utf-8")
    print(("Verified" if args.check else "Generated")+" "+str(len(docs))+" linked player pages.")

if __name__=="__main__":
    main()
