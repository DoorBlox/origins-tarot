# Arcane Rev3 — Player Guide and Ascension Roadmap

**Minecraft Java 1.18.2 • Fabric • Origins 1.4.1 • Arcane V2 Rev3**

This guide is for **Arcane Rev3**. Choose one of the 22 Major Arcana, learn your abilities in the Pathway Tome, complete acting tasks and ascend from Sequence 9 toward Sequence 2. Sequence 1 cannot currently be unlocked in ordinary SMP gameplay.

## New default: the in-game written books (no Command Aliases)

The preferred way to read explanations in Minecraft 1.18.2 is the vanilla **written-book GUI**:

1. Use **`/trigger a_book`** to receive the **Arcane Handbook**. New Tarot players are also given this book when they awaken. Hold it and **right-click**; use the clickable page index to jump to controls, quests and Sequence 9→2 materials.
2. Use **`/trigger a_tome`** or **`/trigger a_abilities`** to receive your **Pathway Tome**. Open it to see abilities, effects, activation controls and cooldowns, organized by Sequence.
3. At **Sequence 4**, use **`/trigger a_partner_tome`** to receive the linked second-path Tome. This is a read-only reference: it doesn't equip locked abilities.
4. To see your own **live progress**, type **`/trigger a_hud set 2`** (opt-in actionbar) or use **`/trigger a_roadmap`** for live acting marks, cooldown, next task and ritual status. Turn the HUD off using **`/trigger a_hud set 3`**, or toggle with **`/trigger a_hud set 1`**.
5. **`/trigger a_slots`** remains the live chat slot editor. **`/trigger a_focus_menu` now gives an Ability Focus written book** listing only your available slot numbers. Right-click it, choose an equipped slot, then open the matching kit book to see only that kit’s active abilities and click the ability you want to focus. Book listings are generated for kits; the server checks current ownership and slot assignment before granting a kit book or accepting a focus selection. As with other books, the datapack cannot open the GUI automatically.

**You have not configured Command Aliases? That's fine.** All commands above are vanilla player `/trigger` commands, usable without OP privileges. The optional `tarot.json` shortcut file is not necessary. For any book, keep it in your inventory and right-click to open: datapacks cannot directly force the book GUI to open.

The HUD is **private and opt-in**, because a single server-wide bossbar cannot reliably render each player's separate Sequence/mark values. It updates about every two seconds and displays your Sequence, current marks/threshold, whether the next acting proof is ITEM or EVENT, and remaining proof-cooldown ticks. It does not change your XP, stats or progression.

## Quick start — find and understand your abilities

1. Select a Tarot Origin. You start at **Sequence 9** with **one automatically equipped Sequence kit**.
2. Use **/trigger a_book** (or **/trigger a_guide**) to receive the written Handbook. Open it in your hand; **/trigger a_help** gives brief chat shortcuts.
3. Use **/trigger a_tome** (or **/trigger a_abilities**) for your Pathway Tome. Click a Sequence in the book to read what each ability does and how to use it.
4. Type **/tarot roadmap**, or **/trigger a_roadmap**, to see your next acting proof, required marks, offerings, altar conditions and next Sequence unlock.
5. Use the clickable buttons in chat; non-OP players can navigate with vanilla triggers. To inspect directly, use **/trigger a_kit set 1** then **/trigger a_detail set 1**. With Command Aliases, **/tarot kit 1** and **/tarot detail 1** also work.

Other commands: **/tarot status**, **/tarot slots**, **/tarot focus**, **/tarot ascend**, and **/tarot slot auto**. Bind the Origins Primary and Secondary active keys in Controls → Key Binds; key names vary by client setup. The Ability Focus book selects a currently owned active ability or restores legacy shared-key behavior. Focus does not assign new keyboard keys: configure the two Origins active keys under Controls → Key Binds. Passive abilities activate automatically and do not appear as selectable actions.

## Reading your ability Tome

The Tome shows each ability's **name**, **what it does**, and **how to use it**, including activation keys, relevant conditions and cooldowns. Use the Sequence links to browse abilities for your pathway.

**One slot equips a full pathway/Sequence kit**, not a single power. Your starting Origin may also have a permanent trait or drawback that remains active when you change slots.

The downloadable **Arcane_Rev3_Player_Ability_Reference.md** groups the pathways and abilities into one reading guide. Resonance information is clearly marked as not yet accessible through ordinary ascension. Use the in-game Tome to see your own pathway.

The game describes the effects available in the current build. If something behaves differently than expected, check your active keys, equipped kit and requirements, then report it to the server administrator.

## Acting marks: the two repeating tasks

The first task is to **have the acting item in your inventory**. The second task is to **perform the listed action**. Tasks alternate item → action → item, using the player's **primary** pathway even after a partner unlocks. A successful task awards **one acting mark** and starts a **2,400-tick (120-second) cooldown**. The roadmap shows your next task and countdown. Item proof does not consume the item; ascension ritual offerings are consumed only upon success.

| Primary Arcana | Item task | Action task |
|---|---|---|
| Fool | Compass | Kill spider |
| Magician | Ender pearl | Enter the Nether |
| High Priestess | Book | Trade with villager |
| Empress | Spider eye | Kill spider |
| Emperor | Shield | Kill pillager |
| Hierophant | Lectern | Trade with villager |
| Lovers | Wheat | Breed animals |
| Chariot | Flint and steel | Kill blaze |
| Strength | Iron pickaxe | Kill zombie |
| Hermit | Lapis lazuli | Trade with villager |
| Wheel of Fortune | Rabbit's foot | Kill skeleton |
| Justice | Honey bottle | Trade with villager |
| Hanged Man | Kelp | Kill drowned |
| Death | Bone | Kill skeleton |
| Temperance | Glass bottle | Kill spider |
| Devil | Blaze powder | Kill ghast |
| Tower | TNT | Kill creeper |
| Star | Clock | Kill phantom |
| Moon | Redstone | Consume cooked beef |
| Sun | Torch | Kill zombie |
| Judgement | Iron bars | Kill pillager |
| World | Crossbow | Kill pillager |

## Full ascension roadmap

These exact counts are from the current progression catalog. Marks and required inventory offerings are deducted when a ritual succeeds.

| Sequence → next | Acting marks required | Offerings | New unlock |
|---|---:|---|---|
| 9 → 8 | 1 | 6 amethyst shards + 8 lapis lazuli | 2 auto-filled kits |
| 8 → 7 | 2 | 12 copper ingots + 2 glow ink sacs | 3 auto-filled kits |
| 7 → 6 | 2 | 8 gold ingots + 2 ender pearls | 4 auto-filled kits |
| 6 → 5 | 3 | 6 blaze powder + 1 ghast tear | 5 auto-filled kits |
| 5 → 4 | 3 | 4 diamonds + 16 amethyst shards | Fixed partner pathway, 6 slots (sixth empty) |
| 4 → 3 | 4 | 1 netherite scrap + 2 eyes of ender | 7 editable slots |
| 3 → 2 | 4 | 2 ancient debris + 4 phantom membranes | 8 editable slots |
| 2 → 1 | — | **Not available yet** | Resonance is not unlocked in ordinary gameplay |

**The ritual altar:** stand grounded **on a lectern** with **crying obsidian directly beneath the lectern**. You must not be Elytra-gliding or in combat (combat timer must be zero). Carry the stated offerings and acting marks, then use **/tarot ascend** or **/trigger a_ascend**. Failure messages indicate missing marks, materials, or the altar/grounded/combat requirement. The current logic checks inventory first and only consumes the specified offerings on successful progression.

**Sequence 2 → 1 is not available in ordinary gameplay.**

## Slots and your second pathway

**Sequence 9–5:** All currently unlocked kits from your first pathway are automatically equipped in Sequence order. You can inspect them with the ability codex.

**Sequence 4–2:** Your fixed partner pathway unlocks automatically. You can mix unlocked kits from either pathway, within 6, then 7, then 8 slots. New slots begin empty. Each selected Sequence kit equips **all abilities of that level**. You cannot duplicate a kit, equip locked levels, or choose unrelated Arcana.

Use **/tarot slots**, then **[Edit slot N]**. Choose your primary or partner and an unlocked Sequence; use **[View abilities in slot N]** to inspect what the slot does. You can also use:

- **/tarot slot N tarot:pathway S** — assign a complete unlocked pathway/Sequence kit
- **/tarot slot N clear** — empty one slot
- **/tarot slot swap N M** — reorder two slots
- **/tarot slot auto** — refill with primary pathway kits
- **/tarot reset** — invoke the existing auto/reset-slot behavior; **not** a playerdata wipe

These changes do not remove permanent identity drawbacks. The exact allowed pairings come from the [Rev3 handbook](HandbookRev3.txt) rather than any arbitrary combinations.

## Troubleshooting in-game

- **Ability missing?** Open **/trigger a_status** and **/trigger a_slots**; confirm the kit is equipped and not administratively paused.
- **Ability won't activate?** Inspect it via **/trigger a_abilities**. Check Origins keybinds, sneaking/night conditions, cooldown, target rules and optional **/trigger a_focus_menu**.
- **Can't earn a mark?** Acting tasks alternate item and action, with 120 seconds between accepted proofs. Check **/trigger a_roadmap** for your next phase.
- **Ascension fails?** Verify that the *feet → lectern → crying obsidian* block stack is correct, you're grounded/out of combat, and both required offerings are in inventory. Sequence 1 is locked.
- **PvP ability didn't hit a player?** Friendly-fire restrictions protect allies and neutral players. Read the ability description for its valid targets.
- **An effect differs from the description?** Note the ability name, what happened, and the conditions, then report it to an administrator.
- **Old missing power ID or broken save?** Do **not** delete playerdata or scoreboard objectives. Use [the safe SMP upgrade and rollback guide](ARCANE_SMP_UPGRADE_PREFLIGHT.md).

## Safe incremental SMP upgrades

Development can continue while you play, but GitHub source merges **do not automatically update your SMP**. New PRs have a fail-closed static compatibility gate comparing previous/candidate ZIP power IDs, Origin IDs, functions, scoreboard criteria, initializer encodings and grant sources. Passing it **does not prove real playerdata migration**.

Before each update, **stop the server and back up the entire world, especially playerdata, scoreboard.dat and the existing ZIP**. Prefer installing the candidate on a world clone first; never run old V2/V3 Tarot and Rev3 packs simultaneously. Verify **/datapack list**, startup logs, a real player relog, slot/power ownership, death/respawn, and a rollback drill. If the new pack changes a persistent data contract, a tested explicit migration is required rather than simply replacing the ZIP.

Maintainers: [canonical handoff](../CHATGPT_HANDOFF.md), [release tracker #20](https://github.com/DoorBlox/origins-tarot/issues/20), [SMP upgrade runbook](ARCANE_SMP_UPGRADE_PREFLIGHT.md), [Rev3 progression](HandbookRev3.txt), and [Rev2 abilities](HandbookRev2.txt).
