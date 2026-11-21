# Arcane Rev3 — first actual Origins 1.4.1 runtime acceptance

**Evidence date: 2026-11-22.** The owner supplied the Arcane-enabled startup log plus a screenshot showing the enabled ONLY_DEV ZIP and working clickable /trigger a_help. The genuine server is Minecraft Java 1.18.2, Fabric Loader 0.20.1, Origins 1.4.1 and Apoli 2.3.3. This replaces the prior no-datapack baseline; do NOT commit raw logs containing user identifiers or network endpoints.

## What was actually observed BEFORE code corrections

- **PASS (limited):** the ONLY_DEV ZIP was found/enabled, the server reached Done (11.971s), the player selected tarot:moon and /trigger a_help displayed the interactive Tarot menu. There was NO repeat Terralith OutOfMemoryError in this particular startup.
- **FAIL:** two essential mcfunctions failed parsing: tarot_arcane:player/detect and player/verify. This Apoli 2.3.3 server rejected origin has origin command syntax, so a visible help menu does NOT prove scoreboard state, path initialization, slot grants or progress.
- **FAIL:** 44 power/subpower decoder errors: **13** missing required hit/kill cooldown fields, **12** unknown origins:random_teleport entity actions, **7** unknown origins:chance **entity conditions** (distinct from valid chance meta actions), **6** invalid ingredient items arrays, **2** unsupported origins:not item conditions, **2** unknown origins:submerged entity conditions, and **2** missing render_armor for invisibility.
- **FAIL (downstream):** five parent Origin drawback references could not register because corresponding power definitions were skipped: devil, moon, judgement, chariot and temperance.
- Total **51 ERROR observations**: two functions + 44 decoder errors + five downstream references. The log reports 580 registered powers and 44 origins; this does NOT mean all authored 402 powers are valid or that 44 may simply be subtracted from 580.

## Fix — merged PR #44

See https://github.com/DoorBlox/origins-tarot/pull/44 merged as eef3392080448021e0736c41f03e5a7de004984d after all four exact-head workflow checks passed.

- Adds arcane_rev3/compat_141.py, a scoped correction for the nine observed error categories in the **generated ZIP**. Required event cooldowns default to a conservative 20 ticks; invisibility specifies render_armor false; submerged and item inverted are translated to old-supported condition shapes; item arrays become OR conditions. Unsupported random teleport is replaced with an Overworld-only, bounded, at-most-16-block **surface blink** using vanilla /spreadplayers. Chance entity conditions become true per-event vanilla minecraft:random_chance loot predicates accessed via origins:predicate, without turning death saves into unlimited immortality.
- Replaces invalid origin has origin functions with **22 hidden native action_over_time powers**, each owned by its selected Origin and calling player/sync/PATH. This initializes/repairs the correct path without granting players OP or forcibly selecting an Origin. New code still needs actual server runtime verification.
- New tests/test_arcane_real_server_141.py examines **both ZIP variants**, all nested power/subpower types, random predicate registrations, item negation, radius bounds, minimum event cooldowns, runtime score sync and command safety.
- Source inventory is **unchanged: 402/434 compiled (73 source-full, 329 explicitly partial; 32 individual blocked), 110/110 Resonance source-compiled.** These are authoring counts, NOT a count of gameplay-verified effects.

## Required next isolated server test

1. Stop the test server and back up the already generated world. In world/datapacks replace the old Arcane_Rev3_22_Origins_ONLY_DEV_1.18.2.zip with the **new** ZIP of the same name from the successful PR #44 GitHub Actions Arcane workflow; do not leave multiple copies or combine ONLY and ADDON variants.
2. Restart fully. Run /datapack list and inspect the NEW latest.log for Failed to load function, There was a problem reading power file/sub-power, unregistered power and origin errors.
3. As a non-OP Tarot Origin (the chosen tarot:moon works), test /trigger a_help, /trigger a_status and /trigger a_slots. A test OP can inspect scoreboard a_init=1 and a_path of that player; do NOT make the player OP. Verify basic Seq9 power registration rather than just text-only help.
4. Confirm the previously missing permanent parent penalties now register; then exercise scoped friendly/opponent/teamless PvP, one corrected action, keybind and cooldown. Only after a successful load test continue with the opt-in OP-only Seq1 progression test.
5. Provide the NEW Arcane-enabled latest.log and observed PASS/FAIL of registration and initialization. A clean source CI run is NOT a Minecraft acceptance.

The owner has explicitly accepted intentional offline authentication and earlier first-worldgen Terralith OOM as development caveats. Keep risks visible but do not insist on reversing those decisions. **Current post-fix real Minecraft acceptance: NOT RUN.** No live SMP deployment or source-number inflation.
