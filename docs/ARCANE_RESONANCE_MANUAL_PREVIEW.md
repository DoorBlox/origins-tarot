# Arcane V2 Rev3 — Manual Resonance Preview (OP-only, development only)

**Not a gameplay release.** This is an opt-in third, separate datapack built from the current code's compiled Resonance entries. It is for the owner to test gameplay effects while Seq1 is temporarily fail-closed. The **final game design remains all ten Seq9–0 Resonance kits activating together at Sequence 1**.

## What the three ZIPs do

- Arcane_Rev3_22_Origins_ONLY_DEV_1.18.2.zip: standalone 22-path developer datapack.
- Arcane_Rev3_22_Origins_ADDON_DEV_1.18.2.zip: 22-path addon variant for existing Origins stacks.
- **Arcane_Rev3_Resonance_Manual_Preview_TEST_ONLY_1.18.2.zip:** ONLY manual functions, no power JSON, no Origin layer, no load/tick hooks, no command alias and **no automatic activation**. Install this alongside ONE of the two Arcane developer variants in a **disposable, backed-up 1.18.2 test world**. Do not install both ONLY and ADDON variants together.

The preview requires installed Origins 1.4.1 to load the other datapack's power JSON. The exact mod collection (Pehkui, ReMorphed, SkinShifter, Extra Keybinds, LuckPerms, etc.) has not passed combined runtime acceptance.

## How an OP test player invokes it

Run from the chat of a player who has selected one of the 22 Tarot Origins. These functions require operator access through vanilla /function; they are **not exposed through /tarot aliases or /trigger**.

```mcfunction
/function tarot_arcane:dev/resonance/list
/function tarot_arcane:dev/resonance/paper_martyr
/function tarot_arcane:dev/resonance/one/paper_martyr/9_burdened_beginning
/function tarot_arcane:dev/resonance/clear
```

Replace `paper_martyr` with one of the 11 pair IDs from the list function. For one-power tests, replace the final ability ID with the compiled resource ID segment (for example, `9_burdened_beginning`). The source register and generated ability manifest determine valid names; blocked entries have no grant function.

- Pair preview grants only **compiled** powers from Seq9 through Seq0 for that pair, with explicit count (e.g. 9/10). Missing source entries are not created or silently replaced.
- A single-power function first revokes all prior manual-preview powers, then grants just that one power, avoiding collisions between multiple active keybindings during isolated tests.
- Preview grants use `tarot_arcane:resonance_manual_preview` as their **own source**. Clearing revokes only that source: it does not erase `tarot_arcane:slot_grants` or permanent Origin identity drawbacks.
- Pair commands require a player with `a_init=1` and refuse a currently administratively paused player. Single-power commands remain explicitly OP-only; use an isolated tester rather than bypassing an admin pause.
- Normal Seq2→1 ritual/progression **remains locked** in the base developer datapacks and consumes no ritual materials. This is a temporary safety gate, not the intended final design.

## Important limitations

Manual preview powers may **stack with already equipped individual kits**, and multiple active abilities can share Origins primary/secondary keys. Therefore use single-power functions when testing specific cooldowns, damage, PvP, Sin-like behavior or duration. This is not a faithful substitute for the ultimate one-way Resonance mode transition.

No server persistence cleanup runs automatically from this preview ZIP; **run `/function tarot_arcane:dev/resonance/clear` before uninstalling it or returning to normal play.** Keep a backed-up test world and note whether preview source persists after relog/death.

For each test record: Minecraft and mod jar versions, exact command, expected handbook behavior, observed result, log errors, and **PASS / FAIL / NOT RUN**. Focus especially on the difference between native effects and clearly documented `partial` limitations. Do not treat passing Python tests as gameplay success.

Once all 110 entries have meaningful verified implementations and core transition/identity/teammate protection is safe, replace the development gate with the handbook's required full Sequence1 activation. Do not ship this preview ZIP in production.
