# Arcane Rev3 — third observed server reload (2026-11-22)

This is a **privacy-sanitized record** of the owner's reload excerpt at 05:33:42–05:33:43, following the earlier startup at 05:23:15. The earlier start showed **Arcane ONLY_DEV missing**, automatically enabled a legacy Tarot V2 ZIP, failed two `origins:invisibility` powers for missing `render_armor`, and on player login found a saved Moon Seq9 power ID that was not registered. The owner then changed datapack files and ran `/reload`.

## New evidence: significant structural improvement

- **PASS (limited):** `Reloading!`, `Loaded 7 recipes`, `Loaded 1188 advancements`, `Finished loading powers... 842 powers`, `Finished loading origins... 44 origins`, `Read 1 layers`; Command Aliases reloaded.
- The owner-supplied **05:33 reload excerpt contains NO** `There was a problem reading power file`, `contained unregistered power`, `Error reading data field`, or malformed mcfunction errors. This is **positive evidence of registry loading**, not a complete authoritative error-free log: the snippet ends before player reconnects or functional checks.
- 44 origins are **consistent with** 11 previous base Origins + 22 Arcana choices + 11 paired Resonance identities, but **counts cannot independently prove which file or SHA was loaded**, all 434 abilities work, or that multiple Tarot packs are absent.
- Brigadier ambiguity messages for `teleport`, old ReMorphed, SkinShifter, Walkers, Pehkui and statistics were observed before and are not a Tarot decoder failure. Do not modify old mod configs on that basis alone.
- **NOT RUN/NOT EVIDENCED:** `/datapack list`, exact inner ZIP/commit, fresh full server restart, real non-OP `/trigger a_status` and `a_slots`, missing Moon power after logout/login, death/respawn, persisted `a_*` scores, all 11 Resonance pairs, selected ability cooldowns, teammate/enemy/neutral PvP and backups/rollback. The previous `Could not get power type from id 'tarot:moon/9_sanguine_sight_vision'` was at player login, so its **absence from a reload-only excerpt does not prove it was resolved**.

## Safe next operator checks

1. **Do not reset a live world or delete playerdata.** Take a complete save backup first. Run `/datapack list` and ensure only ONE intended `Arcane_Rev3_22_Origins_ONLY_DEV_1.18.2.zip` or `ADDON_DEV` version is active, with no legacy V2/V3 Tarot pack and no outer GitHub Actions ZIP.
2. Reconnect with the existing Moon test player; check server log for `Could not get power type from id` and try non-OP `/trigger a_help`, `/trigger a_status`, `/trigger a_slots`. Record Sequence 9 and expected kit; repeat after a safe restarted clone.
3. Preserve runtime error evidence; no regeneration of saved powers or migration without the exact old/new pack IDs and a rollback drill.
4. Review the local read-only tooling `python -m scripts.arcane_smp_preflight --world /path/to/world --json` in PR #57. Its eligible-for-test result is **not** production authorization.

**Status: reload registry loading PROVISIONAL PASS; full SMP compatibility and save persistence NOT VERIFIED.** The latest source still contains **73 source-full + 361 PARTIAL** ability definitions. Never mark all abilities or the normal Seq1 journey as complete on registry counts.
