# Player troubleshooting and FAQ

[← Player handbook](README.md) · [Controls](CONTROLS.md) · [Ascension](ASCENSION.md) · [Server safety](SERVER_SETUP.md)

## Table of contents
- [The Focus menu floods chat](#the-focus-menu-floods-chat)
- [My ability key does nothing](#my-ability-key-does-nothing)
- [My book does not open](#my-book-does-not-open)
- [I cannot find a specific ability](#i-cannot-find-a-specific-ability)
- [My partner's powers are missing](#my-partners-powers-are-missing)
- [I did not receive an acting mark](#i-did-not-receive-an-acting-mark)
- [Ascension fails](#ascension-fails)
- [I cannot reach Sequence 1](#i-cannot-reach-sequence-1)
- [What evidence should I send the admin?](#what-evidence-should-i-send-the-admin)

## The Focus menu floods chat

That is the old chat-based Focus implementation. The new **/trigger a_focus_menu** gives a small written-book index instead. If the chat still floods, your server probably hasn't installed the latest Arcane Rev3 build. See [server update safety](SERVER_SETUP.md).

## My ability key does nothing

Verify **Options → Controls → Key Binds → Origins** Primary/Secondary keys. Check that the kit is equipped with **/trigger a_slots**. Use the Focus book to choose the desired active power. Read its page for sneaking, nighttime, held-item, target or cooldown conditions. Some skills are **passive** and will never activate on pressing G or H.

## My book does not open

The command puts a book in your inventory but cannot open it. **Select the written book, hold it, right-click.** If your inventory is full, free a slot before retrying. The book's links work inside the vanilla written-book GUI.

## I cannot find a specific ability

The **Pathway Tome** shows the primary pathway's normal Sequence 9–2 abilities for reference, including higher levels you haven't unlocked yet. The **Focus book** only lists **active** abilities in a *currently equipped* kit. Automatic passives will not be focus choices. Click a numbered slot, then the kit-specific book, then the ability.

## My partner's powers are missing

A linked partner appears only after **Sequence 4**, and a partner Tome is **read-only**. Use **/trigger a_slots** to actually equip an eligible partner kit into an unlocked slot. You cannot choose an unrelated pathway.

## I did not receive an acting mark

Proofs alternate **item, event, item, event** and each successful proof starts a 120-second cooldown. Run **/trigger a_roadmap** to see whether your next step is ITEM or EVENT and how long remains. An item proof is just possession, not consumption.

## Ascension fails

Check required marks, offerings, a **lectern directly above crying obsidian**, standing on the lectern, on ground, not in combat for 10 seconds and not Elytra-gliding. Run **/trigger a_roadmap**. Only successful allowed rituals consume offerings.

## I cannot reach Sequence 1

This is intentional. Normal Sequence 1/0 and Resonance are **locked**. Do not use an operator-only test transition or its separate preview pack on a regular SMP.

## What evidence should I send the admin?

Include your **Origin, Sequence, current slot, attempted ability, keybinds/condition, installed Arcane build SHA**, error text and what happened. The operator can compare against the [SMP upgrade runbook](../ARCANE_SMP_UPGRADE_PREFLIGHT.md). Never delete playerdata or scoreboard.dat to hide missing powers.

[↑ Table of contents](#table-of-contents) · [← Player handbook](README.md)
