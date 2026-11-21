# Arcane Rev3 — second real Minecraft runtime check (22 Nov 2026)

Owner provided the full server log and client command transcript after PR #44. Fabric 1.18.2, Origins 1.4.1, Apoli 2.3.3. DO NOT upload raw log/player addresses.

## Actual results from the second test

- **PASS:** No previous player/detect or player/verify function parsing failures. Player awoke as Moon at Sequence 9. Non-OP /trigger a_help, /trigger a_status and /trigger a_slots worked. Moon status showed Seq9, Slot 1 = The Moon Seq9, 0 acting marks, and partner unlocking at Seq4.
- **PASS (limited):** Startup completed as Done (11.043s), registering **644 powers and 44 origins**. These include base/subpowers and do NOT prove all authored Tarot abilities are faithful or that every power has been played.
- **FAIL (two Apoli decoder errors):** tarot:temperance/9_unstable_manifestation and tarot:walking_sanctuary/9_wraith_s_prayer_chest (inside walking_sanctuary/9_wraith_s_prayer) each failed at **chest.ingredient** because the Ingredient object used an old-version-invalid items array rather than item or tag.
- **FAIL (downstream one reference):** Origin tarot:temperance referenced the skipped permanent power tarot:temperance/9_unstable_manifestation.
- **Unrelated:** CraftedCore's optional Patreon network fetch error did not prevent server startup. No Terralith OOM in this restart; offline authentication remains intentional per owner.

## Cause and remediation — PR #46

The previous Apoli 2.3.3 adapter normalized multi-item ingredients only when encountered under a property literally called item_condition. However, origins:restrict_armor and origins:conditioned_restrict_armor use the four **head, chest, legs and feet fields directly as ItemConditions**.

[PR #46](https://github.com/DoorBlox/origins-tarot/pull/46) adapts these fields **only when their parent is an armor-restriction power**, preserving original forbidden armor items. Invalid ingredient.items arrays now become origins:or with valid single-item conditions. It does NOT rewrite unrelated properties called chest.

- Added tests **first**: tests/test_arcane_141_armor_ingredient.py checks the two actual offending JSON outputs in both ONLY and ADDON ZIPs, ALL output origins:ingredient fields, nested origins:multiple, four armor slots, and unrelated chest properties.
- RED evidence: exact pre-fix source head bb2a94ad9d34ad02a351b7988e67e63a2e92b82e failed eight assertions on GitHub CI, including the exact Walking Sanctuary item list.
- GREEN evidence: source head 58c793b98220c18d00eabdffafdbca50e584f59f passed all four workflow checks.
- Source inventory unchanged: **402/434 compiled** (73 source-full, 329 partial), **32 individual blocked**, 110/110 Resonance source-defined. These are NOT game-verified counts.

## Next acceptance test

1. Stop and back up the existing generated test world. Replace the old Arcane_Rev3_22_Origins_ONLY_DEV_1.18.2.zip with the new ONLY_DEV ZIP built from exact merged PR #46; do not keep two packs or mix ONLY and ADDON.
2. Restart and inspect latest.log for chest.ingredient errors, orphaned temperance power, and other power/function parser errors. Run /datapack list.
3. Non-OP player: repeat /trigger a_help, /trigger a_status, /trigger a_slots. Inspect Seq9 Moon kit and relog persistence. Test the forbidden armor sets on a disposable OP test character, not on live players.
4. Only after a clean loader test should the team-safe PvP, individual cooldowns, death/relog, keybind, morph and OP-only Sequence1 Resonance development transition be accepted.

**Status:** Second pre-PR46 runtime PARTIAL PASS / remaining two power FAILs. PR46 source fix CI PASS; **post-PR46 Minecraft runtime NOT RUN**. This is not a production release.
