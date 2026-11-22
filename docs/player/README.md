# Arcane Rev3 — Complete Player Handbook

**Minecraft Java 1.18.2 · Fabric · Origins 1.4.1**. Choose one of 22 Origins, ascend from Sequence 9 toward Sequence 2, and use interactive in-game books to understand your abilities. **This is the Arcane Rev3 developer/test pack, not legacy Tarot V2/V3.**

> Source changes do not automatically update an SMP. The latest Arcane ZIP has not passed complete live multiplayer acceptance. Ask the server administrator before upgrading an existing world.

## Table of contents

1. [Start here — first five minutes](START_HERE.md)
2. [Keybinds, interactive books, and Focus](CONTROLS.md)
3. [Sequences, acting marks, and rituals](ASCENSION.md)
4. [All pathways, partners, and permanent weaknesses](PATHWAYS.md)
5. [All current normal-pathway abilities](#all-22-pathways)
6. [Troubleshooting and common questions](TROUBLESHOOTING.md)
7. [Server upgrade and rollback safety](SERVER_SETUP.md)

## All 22 pathways

Choose any pathway for **direct Sequence links, named individual abilities, current effects, how-to-use instructions, and permanent weaknesses**:

- [The Fool](pathways/fool.md)
- [The Magician](pathways/magician.md)
- [The High Priestess](pathways/high_priestess.md)
- [The Empress](pathways/empress.md)
- [The Emperor](pathways/emperor.md)
- [The Hierophant](pathways/hierophant.md)
- [The Lovers](pathways/lovers.md)
- [The Chariot](pathways/chariot.md)
- [Strength](pathways/strength.md)
- [The Hermit](pathways/hermit.md)
- [Wheel of Fortune](pathways/wheel_of_fortune.md)
- [Justice](pathways/justice.md)
- [The Hanged Man](pathways/hanged_man.md)
- [Death](pathways/death.md)
- [Temperance](pathways/temperance.md)
- [The Devil](pathways/devil.md)
- [The Tower](pathways/tower.md)
- [The Star](pathways/star.md)
- [The Moon](pathways/moon.md)
- [The Sun](pathways/sun.md)
- [Judgement](pathways/judgement.md)
- [The World](pathways/world.md)

## In-game shortcuts

- `/trigger a_book` — interactive main Handbook.
- `/trigger a_tome` — your Pathway Tome.
- `/trigger a_partner_tome` — partner's read-only Tome from Sequence 4.
- `/trigger a_focus_menu` — interactive Focus book for your equipped slot abilities.
- `/trigger a_slots` — edit your kit slots.
- `/trigger a_roadmap` — your next task, marks, offerings, and ascension.
- `/trigger a_hud set 2` — show personal HUD; `/trigger a_hud set 3` hides it.

Books must be **held and right-clicked**; safe hyperlinks navigate inside the vanilla book UI. No optional Command Aliases setup is required for these vanilla triggers.

## Sources

This reference is generated from the **player-facing ability text emitted by the Arcane Rev3 build**, plus the canonical [progression catalogue](../../progression/catalog.py) and [partner model](../../arcane_rev3/model.py). It intentionally excludes inaccessible Seq1/0 Resonance and developer-only diagnostic labels. See the [developer tracker](https://github.com/DoorBlox/origins-tarot/issues/20) for release gates.
