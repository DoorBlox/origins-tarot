# Arcane Rev3 — Player Guide and Ascension Roadmap

**Minecraft Java 1.18.2 • Fabric • Origins 1.4.1 • Arcane V2 Rev3**

This guide is about **Arcane Rev3**, not the legacy Tarot V2 pack or the separate older V3. There are **434 source-defined abilities: 73 source-full and 361 PARTIAL**. The 110 paired Resonance entries exist in source, but **Sequence 1 is LOCKED for normal SMP play**. Source compilation is not proof of every Minecraft mechanic working.

## New default: the in-game written books (no Command Aliases)

The preferred way to read explanations in Minecraft 1.18.2 is the vanilla **written-book GUI**:

1. Use **`/trigger a_book`** to receive the **Arcane Handbook**. New Tarot players are also given this book when they awaken. Hold it and **right-click**; use the clickable page index to jump to controls, quests and Sequence 9→2 materials.
2. Use **`/trigger a_tome`** or **`/trigger a_abilities`** to receive your **Pathway Tome**, covering Sequence kit pages, every ability's real implementation, controls, and missing mechanics. Open the book in hand and select a Sequence using the index.
3. At **Sequence 4**, use **`/trigger a_partner_tome`** to receive the linked second-path Tome. This is a read-only reference: it doesn't equip locked abilities.
4. To see your own **live progress**, type **`/trigger a_hud set 2`** (opt-in actionbar) or use **`/trigger a_roadmap`** for live acting marks, cooldown, next task and ritual status. Turn the HUD off using **`/trigger a_hud set 3`**, or toggle with **`/trigger a_hud set 1`**.
5. **`/trigger a_slots`** and **`/trigger a_focus_menu`** remain chat interactions for modifying slots and focus. Written books are static and cannot display realtime scores or instantly open themselves by a datapack command.

**You have not configured Command Aliases? That's fine.** All commands above are vanilla player `/trigger` commands, usable without OP privileges. The optional `tarot.json` shortcut file is not necessary. For any book, keep it in your inventory and right-click to open: datapacks cannot directly force the book GUI to open.

The HUD is **private and opt-in**, because a single server-wide bossbar cannot reliably render each player's separate Sequence/mark values. It updates about every two seconds and displays your Sequence, current marks/threshold, whether the next acting proof is ITEM or EVENT, and remaining proof-cooldown ticks. It does not change your XP, stats or progression.

## Quick start — find and understand your abilities

1. Select a Tarot Origin. You start at **Sequence 9** with **one automatically equipped Sequence kit**.
2. Use **/trigger a_book** (or **/trigger a_guide**) to receive the written Handbook. Open it in your hand; **/trigger a_help** gives brief chat shortcuts.
3. Use **/trigger a_tome** (or **/trigger a_abilities**) for a written Pathway Tome. Click a Sequence in the book to read each ability and its limitations.
4. Type **/tarot roadmap**, or **/trigger a_roadmap**, to see your next acting proof, required marks, offerings, altar conditions and next Sequence unlock.
5. Use the clickable buttons in chat; non-OP players can navigate with vanilla triggers. To inspect directly, use **/trigger a_kit set 1** then **/trigger a_detail set 1**. With Command Aliases, **/tarot kit 1** and **/tarot detail 1** also work.

Other commands: **/tarot status**, **/tarot slots**, **/tarot focus**, **/tarot ascend**, and **/tarot slot auto**. Bind the Origins Primary and Secondary active keys in Controls → Key Binds; key names vary by client setup. The optional Focus menu selects a currently owned active ability, or restores legacy shared-key behavior.

## Reading the ability codex

| Field | Meaning |
|---|---|
| Name / FULL / PARTIAL | **Source-level** implementation status, not a multiplayer certification |
| Currently in game (compiled source) | What this build actually attempts to do |
| How to use | Active key or passive event, cooldown and relevant conditions when inferable |
| Limitations | Precise Rev2 mechanics still missing |
| Permanent Origin drawback | A choice-dependent drawback that survives slot swaps |

**One slot holds one entire (pathway, Sequence) kit**, not one power. At Sequence 9 some abilities are intrinsic Origin drawbacks; these cannot be removed by editing slots.

For **all 434 abilities** including future kits and the 110 unplayable-normal-gameplay Resonance entries, the latest Arcane GitHub Actions build includes **Arcane_Rev3_Player_Ability_Reference.md**. This generated manual lists actual source behavior, how to use it, its remaining limitations, and the original Rev2 handbook description. Future and locked abilities appear as **reference only**. The codex in-game shows **your equipped kits** and revalidates ownership whenever you open details.

Some complex handbook features need unavailable event hooks, custom client visuals or world-edit mechanics. A PARTIAL ability might apply a real short buff or debuff rather than provide the full disguise, AI minion, special attack, persistent light field or percentage-based resource described in the lore.

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
| 2 → 1 | 5 | **LOCKED in ordinary gameplay** | Resonance developer test only |

**The ritual altar:** stand grounded **on a lectern** with **crying obsidian directly beneath the lectern**. You must not be Elytra-gliding or in combat (combat timer must be zero). Carry the stated offerings and acting marks, then use **/tarot ascend** or **/trigger a_ascend**. Failure messages indicate missing marks, materials, or the altar/grounded/combat requirement. The current logic checks inventory first and only consumes the specified offerings on successful progression.

**Sequence 2 → 1 is not available to normal SMP players**, even if you have enough marks and materials. Do not run the OP-only developer transition on your primary SMP.

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
- **PvP ability didn't hit a player?** Harmful AoE is restricted to explicit, distinct vanilla scoreboard teams. Unlisted, teamless, neutral and allied players are not automatic targets; some partial abilities still omit player targeting.
- **An effect differs from lore?** Read the PARTIAL **Limitations** field and the generated reference; do not assume the original full mechanic exists.
- **Old missing power ID or broken save?** Do **not** delete playerdata or scoreboard objectives. Use [the safe SMP upgrade and rollback guide](ARCANE_SMP_UPGRADE_PREFLIGHT.md).

## Safe incremental SMP upgrades

Development can continue while you play, but GitHub source merges **do not automatically update your SMP**. New PRs have a fail-closed static compatibility gate comparing previous/candidate ZIP power IDs, Origin IDs, functions, scoreboard criteria, initializer encodings and grant sources. Passing it **does not prove real playerdata migration**.

Before each update, **stop the server and back up the entire world, especially playerdata, scoreboard.dat and the existing ZIP**. Prefer installing the candidate on a world clone first; never run old V2/V3 Tarot and Rev3 packs simultaneously. Verify **/datapack list**, startup logs, a real player relog, slot/power ownership, death/respawn, and a rollback drill. If the new pack changes a persistent data contract, a tested explicit migration is required rather than simply replacing the ZIP.

Maintainers: [canonical handoff](../CHATGPT_HANDOFF.md), [release tracker #20](https://github.com/DoorBlox/origins-tarot/issues/20), [SMP upgrade runbook](ARCANE_SMP_UPGRADE_PREFLIGHT.md), [Rev3 progression](HandbookRev3.txt), and [Rev2 abilities](HandbookRev2.txt).
