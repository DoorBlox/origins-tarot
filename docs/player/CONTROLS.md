# Ability controls, keybinds, interactive books and Focus

[← Player handbook](README.md) · [Get started](START_HERE.md) · [All pathways](PATHWAYS.md) · [Troubleshooting](TROUBLESHOOTING.md)

## Table of contents
- [Get and navigate books](#get-and-navigate-books)
- [Bind your Origins keys](#bind-your-origins-keys)
- [Select your active ability with Focus](#select-your-active-ability-with-focus)
- [The Fool Spirit Vision example](#the-fool-spirit-vision-example)
- [Which powers need a key?](#which-powers-need-a-key)
- [Equip an ability kit](#equip-an-ability-kit)
- [Command reference](#command-reference)

## Get and navigate books

| Command | What it does |
|---|---|
| **/trigger a_book** | Gives the main Arcane Handbook with clickable contents, quests, all 22 pathways and weaknesses |
| **/trigger a_tome** | Gives your Pathway Tome: sequences, clickable ability names, effects, keys and cooldowns |
| **/trigger a_partner_tome** | Gives your linked partner's **read-only** Tome once you reach Sequence 4 |
| **/trigger a_focus_menu** | Gives an **Ability Focus** book showing your available kit slot numbers |

**Hold the written book and right-click it.** The datapack cannot pop open a book automatically. Click blue links to navigate to pages, [Contents] to jump back, and green links to submit safe player-owned commands.

## Bind your Origins keys

Open **Esc → Options → Controls → Key Binds → Origins**. Find **Primary Active Power** and **Secondary Active Power**. You might choose G and H, but these are configurable and **not** fixed controls.

All active key abilities use those Origins controls. You **cannot assign an arbitrary new keyboard key for every ability** with a vanilla datapack. Focus selects which of the currently equipped active abilities responds when several share one key.

## Select your active ability with Focus

1. Run **/trigger a_focus_menu** and open the **Ability Focus** book in inventory.
2. Click **Slot 1**, or another unlocked slot number. The server checks the slot's current assignment.
3. The server gives a new **kit-specific Focus book**. Open it.
4. Click an ability in the **table of contents**. Its page shows its name, effect and Primary/Secondary key.
5. Click **Select this ability**. The server checks that your player still owns the ability. No operator permission is needed.
6. Press the stated Origins key while meeting any required conditions, such as sneaking, nighttime, a valid target or a cooldown.

The Focus book lists **active key powers only**. Passive skills will not appear in that selection list. If you change or remove a kit, any stale selection is revalidated. **Allow shared hotkeys** restores the old behavior, which may activate multiple abilities at once.

## The Fool Spirit Vision example

- [Fool → Spirit Vision](pathways/fool.md#seq-9-spirit-vision) is available at Sequence 9.
- Set **Secondary Active Power**, for example to **H**.
- In the Focus books, choose your Fool Sequence 9 kit and **Spirit Vision**.
- **Hold Shift to sneak and press H** (or your actual Secondary key).
- Glowing is applied to entities within a **10-block sphere** for **2 seconds**, with a **5-second cooldown**. It can include yourself and teammates, not just enemies.

## Which powers need a key?

| What your Tome says | How it works |
|---|---|
| Primary / Secondary Origins key | Press the corresponding configured Origins key |
| Sneaking / at night / holding an item | Meet the condition, then use the indicated control |
| Triggers on hit / when hit / on kill | Happens automatically on that event |
| Automatic timed passive | Runs on the stated timed check |
| Passive or condition-driven | No separate hotkey |

## Equip an ability kit

At Sequences 9–5, your primary kits automatically equip in order. From Sequence 4, **/trigger a_slots** opens a clickable slot editor: **Edit slot N → pathway → unlocked Sequence**. You can only equip your original pathway or the one fixed linked partner. The server rejects duplicate kits, prematurely unlocked sequences and unrelated pathways.

A kit includes all its abilities. **Selecting a Focus ability does not edit the kit itself.** Your permanent Origin weakness always stays attached to your original Origin.

## Command reference

| Command | Use |
|---|---|
| **/trigger a_help** | Short player menu |
| **/trigger a_status** | Sequence, pathway, slot status |
| **/trigger a_slots** | Equip, clear and rearrange permitted slots |
| **/trigger a_kit set 1** | Inspect abilities in equipped slot 1 in chat |
| **/trigger a_roadmap** | Marks, next proof, cooldown and ritual |
| **/trigger a_hud set 2** | Enable private progress HUD |
| **/trigger a_hud set 3** | Disable private progress HUD |
| **/trigger a_ascend** | Attempt the next allowed ascension ritual |

These are ordinary non-OP **/trigger** commands; Command Aliases is optional. See [ascension](ASCENSION.md), [all pathway abilities](PATHWAYS.md) and [troubleshooting](TROUBLESHOOTING.md).

[↑ Table of contents](#table-of-contents) · [← Player handbook](README.md)
