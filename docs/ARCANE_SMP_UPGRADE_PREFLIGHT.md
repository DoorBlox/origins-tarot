# Arcane Rev3 — safe SMP replacement and rollback (Minecraft 1.18.2)

**Status: development / NOT yet approved as a stable SMP release.** This is
an operator runbook, not a migration tool. Even four green GitHub checks
cannot prove exact Origins/Apoli power decoding, saved-player compatibility,
multiplayer PvP safety or future upgrades. Keep this guard while playing
with a development pack.

## Which GitHub Actions artifact?

- **WRONG for Arcane:** [Build and validate Tarot Club origins](https://github.com/DoorBlox/origins-tarot/actions/workflows/datapack.yml), e.g. run [#44955564896](https://github.com/DoorBlox/origins-tarot/actions/runs/44955564896) → `tarot-club-datapacks` → `The_Tarot_Club_22_Arcana_Only_1.18.2.zip`. This is the old, separate V2 passive pack, not the newer progression system.
- **Correct TEST build:** [Build Arcane V2 Rev3 22-Origin Dev Pack](https://github.com/DoorBlox/origins-tarot/actions/workflows/arcane-full.yml) → `tarot-arcane-rev3-22-origin-dev-not-production` → extract **outer** GitHub artifact ZIP, then choose **one** inner pack: `Arcane_Rev3_22_Origins_ONLY_DEV_1.18.2.zip` (22 Tarot choices replace regular Origins) **or** `Arcane_Rev3_22_Origins_ADDON_DEV_1.18.2.zip` (adds Tarot choices). Read `ARCANE_REV3_BUILD_SHA.txt` in newer builds for the exact commit.
- `Arcane_Rev3_Resonance_Manual_Preview_TEST_ONLY_1.18.2.zip` is an OP-only **standalone disposable-world preview**, not a companion pack to place on SMP. Ordinary Sequence1 remains locked.
- `tarot.json` is a Command Aliases 1.0.1 configuration file, not a datapack ZIP. Place it under the corresponding server's `config/commandaliases/` only after saving the previous configuration. Non-OP `/trigger a_help` remains the fallback without aliases.

## Incremental Rev3-to-Rev3 upgrades while playing

- Your current working Rev3 build can remain installed while development continues in GitHub. **New source commits do not change your live SMP** until you personally install a newer inner ZIP and restart/reload. Playing now does not force a world reset, but it does not guarantee every future migration will be possible.
- As of PR #58, every future Arcane gameplay PR is checked against the exact base-commit build with **both** inner ZIP variants. `python3 -m scripts.arcane_ci_upgrade_guard --previous OLD_REV3.zip --candidate NEW_REV3.zip` reports static compatibility and fails closed if an existing power/origin/function ID, scoreboard objective criterion, pinned Origin power, player initializer mapping, or grant source is removed or changed unexpectedly. It does **not** edit a world. It does not certify actual saved-player NBT or progression migration.
- Each release candidate requires **four CI checks**, an explicit *static upgrade PASS* and a backed-up clone-world restore/relog test. A new development artifact from the `Build Arcane V2 Rev3 22-Origin Dev Pack` workflow is not automatically production-approved. Preserve the **exact** previous working ZIP, `level.dat`, `scoreboard.dat`, `playerdata/`, `data/`, and mod/server configuration before installing an updated candidate.
- If an update needs to change persisted IDs, objective types or path encoding, first implement and validate a separately versioned migration/rollback; do not bypass the comparison or clear players' saved data.
- The **26** recently improved partial abilities are still PARTIAL. No update should claim the remaining 361 definitions are game-complete or automatically grant Seq1 Resonance.

## Before altering the world

1. Stop the server cleanly. Make a **full, verified, restorable backup** of the entire world including `level.dat`, `scoreboard.dat`, `playerdata/`, `advancements/`, `stats/`, `data/` and `datapacks/`, plus current server config, previous Tarot ZIP(s), installed mod versions, relevant permission storage and Command Aliases config. Prefer a world clone on an isolated server first.
2. Your `server.properties` `level-name` identifies the world folder (the supplied log names `tarot_world`). Keep all backup data out of GitHub, particularly raw logs and player identities.
3. Remove old `The_Tarot_Club_22_Arcana_Only_1.18.2.zip`/older V3/previous Rev3 developer ZIPs from the **active world datapacks directory**, **after backing them up**. **Never run legacy V2/V3 and Rev3 together.** They reuse the `tarot:` namespace but have incompatible progression/state contracts. Do **not** remove world/player/scoreboard data to resolve missing powers.
4. Copy **exactly one** Rev3 `ONLY_DEV` or `ADDON_DEV` inner ZIP, intact, to `<world>/datapacks/`. Do not copy the outer Actions artifact. Check that the inner ZIP has `pack.mcmeta` at archive root. To inspect installed files safely before rebooting, run:

```bash
python3 -m scripts.arcane_smp_preflight --world /path/to/tarot_world --json
```

This scanner reads filenames and archive metadata only; it does not touch the world or certify release readiness. Exit code 0 means **eligible for isolated test**, never **SMP-ready**. It reports missing Arcane, legacy overlap, multiple Tarot ZIPs, wrong pack format and accidental upload of the outer Actions artifact. If comparing two **Rev3** builds, provide `--previous-pack /path/to/old.zip --candidate-pack /path/to/new.zip`: any removed power/origin ID fails, but passing cannot prove player NBT or scoreboard persistence.

## After install/restart (capture results)

1. Restart the Fabric 1.18.2 server using the existing known-compatible Java 17, Origins 1.4.1 / Apoli 2.3.3 and modpack. `Done` by itself is **not** acceptance.
2. Check the **new** `latest.log` for `Missing data pack`, `There was a problem reading power file tarot:`, `contained unregistered power`, and `Could not get power type from id`. A single missing power reference is a **failed state/load gate**, not a reason to erase a save. Run `/datapack list` and ensure the intended Rev3 pack, not legacy V2, is active.
3. As a real non-OP player, test `/trigger a_help`, `/trigger a_status`, `/trigger a_slots`, Sequence 9 awakening, ability/cooldown, relog, server restart and respawn. Test the focus menu only if intentionally opted in. Check that no normal player can enable Seq1 or access OP functions.
4. On a backed-up clone with disposable accounts, test an ally, a listed opposing team and a neutral player with harmful and positive AoE; then test slot grant/revoke, pause/resume and old installed mod command paths. Observe CPU/tick/load behavior and any Terralith/C2ME OOM on newly generated chunks. Record **PASS / FAIL / NOT RUN** by case, not "works" on a successful startup alone.

## Important: player state and rollback

- **V2 or older V3 → Rev3 is NOT an automatically supported migration.** These lines use different scoreboard objectives (`tc_*` vs `a_*`) and may contain old Origins power identifiers. Existing progression cannot be assumed to carry over. Even Rev3→later Rev3 updates must be tested for source IDs, conditions, slot persistence and serialized player powers before production replacement.
- The owner's supplied log for legacy V2 run #44955564896 says **Arcane ZIP missing**, legacy V2 auto-loaded, Empress/Temperance `origins:invisibility` rejected for missing `render_armor`, and saved Moon `tarot:moon/9_sanguine_sight_vision` was unregistered. A source fix for V2's invisibility serializer does **not** make V2 into Rev3. The Moon error may disappear after restoring the correct Rev3 archive, but is **not** proven fixed until the subsequent client login.
- If an install introduces errors, **stop and restore the complete consistent backup**—world, scoreboard, playerdata and the correct previously working pack(s). Do **not** blindly revert only the ZIP after playing under a changed schema; a partially migrated save may contain incompatible power IDs. Never manually delete saved player powers, OP privileges, or scoreboard objectives to hide failures.
- The actual server was configured in intentionally offline/insecure mode; no authentication by username occurs. This is an accepted owner development choice, **not** secure authentication for an untrusted public SMP. Restrict direct network access appropriately. The earlier fresh-world Terralith heap OOM was owner-acknowledged as a development caveat, not proof it cannot recur.

**Promote from test to real SMP only when the correct latest Rev3 ZIP loads cleanly, persistent progress survives reload/death/relog, team-safe PvP is actually observed and a full restore drill succeeds.** Incomplete ability mechanics remain explicitly PARTIAL and Sequence1 stays fail-closed.
