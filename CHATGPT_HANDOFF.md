# HANDOFF — Tarot Club / Arcane V2 Rev3 (datapack-only)

> **READ THIS FIRST IN A NEW CHAT.** This file is a durable engineering checkpoint, **not** proof of current GitHub state. First query the live `main` branch, open PRs, CI, and issue [#20](https://github.com/DoorBlox/origins-tarot/issues/20), then read the authoritative handbooks. Do not ask the owner to re-explain the project.

**Latest source development milestone (2026-11-22):** [PR #47](https://github.com/DoorBlox/origins-tarot/pull/47) adds **25** previously blocked individual powers in `arcane_rev3/batches/individual8.py`, all with genuine native gameplay subsets and detailed PARTIAL disclosures. Expected source manifest **434 specified / 427 compiled = 73 source-full + 354 explicitly partial / 7 blocked (six Hanged Sin/damage-state entries plus Hierophant Dietary Expansion)**, Resonance still **110/110 source definitions**. Moon "Pharmacist" is source-gated by Pharmacist II to avoid double pulses. Tests now treat historical wave counts as monotonic floors, and `tests/test_arcane_individual8.py` checks current exact totals and BOTH developer ZIP variants. **Do not mark PR47 merged until four exact-head green workflows and diff review.** First real MC test after PR44 verified Moon Seq9 help/status/slots; PR46 repaired two remaining armor decoder errors in code, but owner explicitly defers the minor follow-up server retest until more source development. **All newer abilities and PR46 loader fix remain NOT RUNTIME VERIFIED; no production release.** Query current main, PRs and issue #20 before continuing.

## 1. Mission and owner's standing instructions

Build **the entire Arcane V2 Rev3 Tarot Club experience** for Minecraft Java 1.18.2/Fabric/Origins: all 22 Major Arcana pathways, 434 handbook abilities (324 individual + 110 Resonance), 11 fixed paired Resonances, honest progression and slots, identity drawbacks, fair team-aware targeting and an accessible non-OP `/tarot` UX. The owner wants **fast, substantial, parallelized batches**, not one ability or PR at a time. Proactively implement, test, open PRs and merge sound source changes without stopping for repetitive permission requests. User has explicitly authorized repository edits and merges.

**Hard constraints that authorization does not erase:**

- **NO KubeJS, no custom Java/Fabric mod**, and do not silently change the chosen datapack-only architecture. Handbook KubeJS examples are *ideas*, not permission to install KubeJS. Vanilla data packs, scoreboard functions, Origins/Apoli 1.4.1 powers and existing approved mods are the constraints.
- **No live SMP install/deployment/world mutation** from a source-code merge. Do not touch hosted player saves, scoreboard.dat, datapacks, configs or admin permissions without a separately grounded deployment/test request and safety verification. Develop in GitHub; keep releases explicitly test-only until actual 1.18.2 runtime acceptance.
- Never invent completed abilities or dummy powers. If a source mechanic cannot be faithfully reproduced, implement a real *subset* only when meaningful and label it **partial** with `missing`; otherwise leave it **blocked**. Do not equate compiled JSON or green Python tests with in-game functionality.
- **Do not harm teammates**. Official Rev3 target rule is tagged hostile mobs plus explicitly configured different-team enemy players, excluding own team and neutral/unlisted players; positive effects should target self/own team. PR #37 introduced allowlisted vanilla scoreboard team targeting for selected powers, but other partial effects still need audit. Never add unfiltered harmful @a selectors.
- Keep player-facing `/tarot`/`/trigger` permission 0 and player-scoped; administrative pause/recovery separate and OP/console-only. LuckPerms may help permission management but doesn't create aliases or replace the vanilla `/trigger` fallback.
- **Preserve the working V2/V3 code paths.** "Tarot Club V3 Path of Ascension" in `progression/` is a different, older runtime/pack from Arcane **V2 Rev3** in `arcane_rev3/full_build.py`. Don't conflate them, don't install their ZIPs together, and don't assume migration of legacy `tc_*` state. The README's "Current: V3" refers to that separate older line.
- Respect copyright: handbook lore is project source; don't add third-party music/art or copyrighted text outside the supplied material.

## 2. Sources of truth, in precedence order

1. `docs/HandbookRev3.txt` — controlling progression rules, slot structure, fixed pairings, activation at Sequence 1; explicitly *supersedes Rev2's mechanical framework*.
2. `docs/HandbookRev2.txt` — exact descriptions of all 434 abilities, per-ability numbers/cooldowns/target restrictions, tags and native-vs-scripted classifications.
3. `arcane/catalog.json` — structured 434-entry source catalog, with `individual` / `resonance` families. Consult real descriptions; never guess an ability from its name.
4. **Actual source:** `arcane_rev3/full_build.py`, `arcane_rev3/powers.py`, `arcane_rev3/batches/*.py`, `arcane/templates.json`, `arcane_rev3/model.py`.
5. **Generated truth:** `output/arcane_ability_manifest.json` produced from the build. The manifest, not a hand-edited dashboard or prose, settles compiled/full/partial/blocked figures.
6. `docs/ARCANE_REV3_DEVELOPMENT.md` — detailed engineering history/limitations; [issue #20](https://github.com/DoorBlox/origins-tarot/issues/20) — current blocking backlog; this handoff — continuity/startup rules.
7. `README.md` and `docs/ASCENSION.md` are mostly about existing V2 and the older **V3 Path of Ascension**, not this new production-ready Arcane Rev3 pack.

**Version notes — 2026-11-22 real server log & configs supersede old PDF estimates:** Minecraft 1.18.2, Fabric Loader **0.20.1**, Java **17**, Origins **1.4.1 / Apoli 2.3.3**, Fabric API **0.77.0+1.18.2**, Fabric Permissions API **0.3.1**, LuckPerms **5.3.86**, ReMorphed **4.2**, SkinShifter **1.3**, Pehkui **3.8.3**, Extra Keybinds **0.5.0**, Command Aliases **1.0.1 build 66**, CraftedCore/Walkers **5.8.1**, C2ME **0.2.0+alpha.7.40**. Uploaded config files inspected; ReMorphed **4.2 predates v7.1 permission system** and SkinShifter **1.3 predates v3.0 LuckPerms support**. **NO KubeJS/custom Java/Immersive Portals.** Four allowlisted vanilla combat teams red/blue/green/gold, unassigned neutral. Inspect [actual server baseline](docs/ARCANE_VERIFIED_SERVER_BASELINE_2026-11-22.md) and [mod matrix](docs/ARCANE_MOD_INTEGRATION_MATRIX.md). **Startup reached Done but had serious Java heap OOM from terralith:spire and OFFLINE/INSECURE mode; preflight is NOT clean.**

## 3. Baseline snapshot (verified after #26)

| Metric | Verified at snapshot | What it means |
|---|---:|---|
| Catalog entries | **434** | 324 individual + 110 Resonance |
| Compiled power definitions | **241** | Real JSON generated; some intentionally partial |
| `full` | **73** | Source translation complete in code; **not** game-tested |
| `partial` | **168** | Useful compiled subset, limitations in manifest `missing` |
| `blocked` | **193** | No compiled faithful/meaningful native power |
| Resonance definitions compiled | **51 / 110** | 23 in wave 1, 28 in wave 2; **none equipable** |
| Individual definitions compiled | **190 / 324** | Remaining individual blocked: **134** |
| Full test suite | **96 tests passed** | GitHub Arcane full-build CI on #26 PR head |
| Separate Arcane tests | **21 passed** | `test_arcane_full.py` on same PR |
| Live 1.18.2 game test | **NOT RUN** | Neither non-OP parser nor PvP/ability behavior verified |
| Live SMP deployment | **NOT DONE** | GitHub source changes only |

**Exact CI evidence:** PR #26 commit `dbedcff595ef9c948c2625749aac8b397b8e53da`, four green workflows: [full Rev3 build](https://github.com/DoorBlox/origins-tarot/actions/runs/44933076045), [isolated Fool alpha](https://github.com/DoorBlox/origins-tarot/actions/runs/44933075894), [V3 Ascension](https://github.com/DoorBlox/origins-tarot/actions/runs/44933075930), [V2 origins](https://github.com/DoorBlox/origins-tarot/actions/runs/44933075910). The `main` push additionally passed the V3 and original-origins workflows; the two Arcane-specific workflows are configured on PR/feature branches, not normal `main` pushes. Do not state "four main checks" if only two run on `main`.

**Never silently retain these counts after changing code.** Rebuild, inspect manifest, run all regressions and update this file and issue #20.

## 3a. Milestone — PR #28 source-scoped upgrade replacement (2026-11-22)

- **Merged** [PR #28](https://github.com/DoorBlox/origins-tarot/pull/28), squash SHA `7f51a2683098572437bb4da9dbe71fea5201e81c`, after four exact-head PR workflow successes at `b9941ddc453ca995f8fed8636af632f6ccd36fac`.
- Added `arcane_rev3/upgrade_policy.py` and `tests/test_arcane_upgrade_replacement.py`; `compile_powers` now applies eight source-scoped non-stacking power conditions. The old bonus stays slotted but is inactive when its matching upgrade is granted by `tarot_arcane:slot_grants`. Lower-tier effects automatically resume on unslot/pause/recovery. Previous conditions are preserved.
- Covered Moon Blood's Renewal → Shaman; Sun Unshadowed → Unshadowed II; World Cold Precision → Cold Precision II; Tower Ruin-Proof → Ruin-Proof II; Wheel Fate Intervenes → Misfortune; Devil Desperate Malice → Demon Form; Empress Witch's Venom → Plague Touch; Hierophant Sanctified Ground → Sanctified Ground II.
- **Intentionally not suppressed**: mandatory identity drawbacks, composite powers such as Judgement Law's Weight (+2 armor), and abilities with differing trigger scopes like Star Nightwatch. Additional upgrades must be audited for preserving unrelated effects.
- Expected manifest remains **434 specified / 241 compiled / 73 full / 168 partial / 193 blocked** because this was a correctness fix, not new ability coverage. These source-completeness labels do not establish in-game compatibility.
- Runtime check of Apoli 1.4.1 `origins:power` source filter, reload, and slot transitions **NOT RUN** on a Minecraft server. No release and no live SMP installation.

## 3b. Milestone — new ability batch and confirmed installed mods (2026-11-22)

- Merged [PR #30](https://github.com/DoorBlox/origins-tarot/pull/30) at `a45377cc2a1d33f2f514221c63db3624ef977317`, with all four PR workflows green at exact head `a41f1ac6301fe3876a21db12803a310d13377d80`.
- 19 individually registered powers added in `individual4.py`, 12 new Resonance powers in `resonance3.py`. `tests/test_arcane_wave3.py` tests catalog IDs, statuses, ZIP contents, target safety and locked Sequence 1.
- Current coverage **434 specified / 272 compiled / 73 full / 199 partial / 162 blocked**; **209/324 individual** and **63/110 Resonance** compiled. The 63 Resonance abilities are not selectable/granted, nor is Sequence1 unlocked.
- The user's supplied **tarotmc(1).pdf** pages 22–25 confirms the selected installed modpack; they additionally confirm LuckPerms. The installed-mod matrix is now `docs/ARCANE_MOD_INTEGRATION_MATRIX.md`. Existing-mod commands/configs are permitted where confirmed, but avoid fabricated APIs, arbitrary OP permissions, KubeJS or a new Java mod.
- **Historical #30 to-do, superseded by #37–#40.** Team filter, parent drawback and 110 Resonance source entries have since been implemented; latest source counts are in section 3e. Gameplay acceptance remains NOT RUN.

## 3c. Implementation waves #32 and #33 — 2026-11-22

- Merged [PR #32](https://github.com/DoorBlox/origins-tarot/pull/32) at `3e35a0974f6160e337a76b7f9f85a07fa991ba23`. Added `arcane_rev3/batches/resonance4.py` (29 explicitly partial powers, **all eleven Seq0 Resonance capstone prototypes**) and `tests/test_arcane_resonance4.py`. All four exact-head PR workflows green at `b2effd5196fdbdbd14665c182d4efad0327df1f7`.
- Merged [PR #33](https://github.com/DoorBlox/origins-tarot/pull/33) at `fa2f7ad91a6f4e3cf16840cbd5c67c448390d272`. Added `individual5.py` (30) and `resonance5.py` (6) with `tests/test_arcane_wave5.py`. All four exact-head PR workflows green at `c2238fbfa33b09e4db7b7462542bb6cbe8d9e404`. First CI run correctly caught a test mismatch because the compiler adds a PvP safety disclosure to retaliation; fixed without weakening the disclosure.
- Current manifest counts: **434 specified**, **337 compiled = 73 full + 264 partial**, **97 blocked** (**85 individual**, **12 Resonance**); 239/324 individual and 98/110 Resonance compiled. **Source-defined is NOT in-game verified.** Many `partial` entries retain substantial missing core mechanics (AI/decoys, Sin, dynamic player disguises, persistent fields, damage precision and team-aware PvP).
- **Temporary Seq1 lock vs intended design:** The owner clarified that previous discussions emphasized partial effects, not a permanent Resonance lock. Rev3 REQUIRES all ten Resonance kits active at Sequence 1; current Seq2→1 fail-closed gate is an unfinished-alpha safety measure, NOT a design decision. Do not silently keep it forever. Do not unlock incomplete Resonance in the live SMP; make an explicitly opt-in isolated preview if needed for owner acceptance, then complete end-to-end transition, identity drawbacks, power ownership, relog/rollback and remove gate in release.
- **Installed mods:** The owner confirms Pehkui 3.7.11, Origins Extra Keybinds 0.2.0, Command Aliases 1.0.1, ReMorphed 4.0 + Woodwalkers 5.4 + CraftedCore 5.1, SkinShifter 1.0, LambDynamicLights, Fabric API, LuckPerms and **Fabric Permissions API already installed**. No Immersive Portals. See `docs/ARCANE_MOD_INTEGRATION_MATRIX.md` for supported project docs, and note ReMorphed 4.0's actual use of modern permission nodes still unverified. No KubeJS or custom Java mod.
- **Communicate blockers immediately:** The owner requests direct notice whenever a mod API is missing, a feature needs a different approximation, a mod dependency may be necessary, or a gameplay/test decision requires input. Do not burden them with repetitive questions; propose concrete alternatives, give status, and continue other safe work.

## 3d. OP-only manual Resonance developer preview — PR #35

- **Merged [PR #35](https://github.com/DoorBlox/origins-tarot/pull/35)** at `2c445a51c111dcf69284674a914a1a3bc6ac492a` after four exact-head green checks at `2763164d0caf579cc8a70147d8a99bdde4c32f89`. The Arcane workflow now uploads a **third, separate** `Arcane_Rev3_Resonance_Manual_Preview_TEST_ONLY_1.18.2.zip` inside artifact `tarot-arcane-rev3-22-origin-dev-not-production`: https://github.com/DoorBlox/origins-tarot/actions/runs/44937501585.
- Preview ZIP contains **no Origin/power JSON or load/tick tags**, only 11 OP-invoked pair test functions, 98 individual one-power grant functions, list and clear. Names documented in `docs/ARCANE_RESONANCE_MANUAL_PREVIEW.md`. Uses a **distinct source** `tarot_arcane:resonance_manual_preview`, never the standard `tarot_arcane:slot_grants`. Cleanup revokes only its own source.
- This deliberately does **not** change the normal Sequence2→Sequence1 fail-closed development gate; **the intended game design remains auto-activating all ten Resonance kits at Sequence1**. Preview is for owner to test partial effects under OP in a disposable backed-up world and can stack with currently slotted individuals. Run the manual clear function before removing preview pack.
- All 98 Resonance definitions are partly/fully compiled but **12 entries still blocked** and **264 compiled abilities are explicitly partial**. Tests are structural; Minecraft gameplay/permissions not verified. The 12 named remaining Resonance blockers and concrete owner decisions are tracked in `docs/ARCANE_REMAINING_BLOCKERS_AND_OWNER_DECISIONS.md`.
- **Owner communication contract:** Continue implementation independently; alert owner concisely whenever a mechanic needs a changed requirement, a confirmed new mod/dependency, actual configured team names, or test evidence. The owner has said "tell me if you need me" and dislikes repeated generic questions. The mod integration matrix includes links to SkinShifter and Pehkui command docs and the caveat that ReMorphed's modern permission documentation mentions **Fabric Permissions API** (potential missing mod, not confirmed for installed 4.0). Do not ask to install until verified.

## 3e. Latest implementation after PRs #37–#40 (2026-11-22)

- **[PR #37](https://github.com/DoorBlox/origins-tarot/pull/37)** merged `9f787485d62490791891b35e1ed0c942ee9ba11c`. Adds `arcane/teams.json` and `arcane_rev3/team_policy.py` with allowlisted vanilla team-safe offensive and ally effects; teamless/unlisted neutral; 4 exact-head CI passes.
- **[PR #38](https://github.com/DoorBlox/origins-tarot/pull/38)** merged `3d62684cdde55971f38e5756cd6d8bca2a1d451a`. Compiles last twelve Resonance with bounded PARTIAL substitutes, 21 individual entries, five persisted-cooldown death saves and same-team-only Lovers isolation. **110/110 Resonance source entries compiled**, many not source-faithful.
- **[PR #39](https://github.com/DoorBlox/origins-tarot/pull/39)** merged `1fd430952e89cfdd331660542ab912b840422e31` with 4 exact-head passes at `05b3e1ce70227b9d3770f7c1128e74579ce7037b`. **OP-enabled per-player test-only real Seq2→1 ritual**, granting ten compiled Resonance powers for 11 fixed pairs (both primary directions) and second permanent identity. Wheel Debt of Fate permanently pinned. Default normal Seq1 LOCKED pending runtime acceptance; manual OP test is NOT production unlock. See `docs/ARCANE_SEQ1_OPERATOR_TEST.md`.
- **[PR #40](https://github.com/DoorBlox/origins-tarot/pull/40)** merged `afba754b5ccd7996d64029e7e455d048df1aaddb` with 4 exact-head passes at `123433540d35ab76f140032d91051ae15c7bf596`. Adds **32 bounded, explicit PARTIAL individual abilities** in `arcane_rev3/batches/individual7.py`, including ten Seq0 individual capstone prototypes, a weighted single-reel Fate spin and guarded stealth/utility. **Current true source counts: 434 total, 402 compiled = 73 full + 329 partial, 32 blocked (all individual). 110 Resonance source entries compiled.**
- **Owner decisions:** Explicitly confirms installed **Fabric Permissions API and LuckPerms**; accepted assistant-proposed **vanilla scoreboard teams** as combat source; **authorizes visible bounded behavior substitutions** rather than failing indefinitely on missing client/event hooks. Do not lie by relabeling partial as full or silently install KubeJS/custom Java. User requests direct concise notice only if old-version mod command, new dependency or real gameplay design decision needs involvement; continue other safe work without repeated permission requests.
- **Important blockers and acceptance:** `docs/ARCANE_REMAINING_BLOCKERS_AND_OWNER_DECISIONS.md` contains all 32 remaining individual blocks and 329 partial fidelity debt. Old mod APIs are now grounded in startup **ReMorphed 4.2, SkinShifter 1.3, Pehkui 3.8.3, Extra Keybinds 0.5.0**; the mod permissions versions do NOT support modern permission instructions. Fix the real baseline **heap OOM and offline-auth exposure** before stressing a new test-world datapack. No Arcane gameplay runtime test or SMP release.

## 3f. Actual Fabric server evidence supplied by owner — 2026-11-22

- **Evidence received and independently parsed:** full no-datapacks fresh-world Fabric startup log, server mod filename screenshot, actual uploaded ReMorphed and SkinShifter JSON5 configs. Do not request them again. [Full sanitized findings](docs/ARCANE_VERIFIED_SERVER_BASELINE_2026-11-22.md).
- **Verified versions:** Fabric Loader 0.20.1, Java 17; Origins 1.4.1/Apoli 2.3.3; Fabric API 0.77.0; Fabric Permissions API 0.3.1, LuckPerms 5.3.86, ReMorphed 4.2, SkinShifter 1.3, Pehkui 3.8.3, Extra Keybinds 0.5.0, Command Aliases 1.0.1 build 66, CraftedCore/Walkers 5.8.1, C2ME 0.2.0 alpha. Full inventory in [mod matrix](docs/ARCANE_MOD_INTEGRATION_MATRIX.md).
- **Result:** Server reached `Done (68.464s)!`, baseline Origins registry 76 powers/11 origins, but encountered **Terralith spire OutOfMemoryError: Java heap space** during fresh-world generation and warns **OFFLINE/INSECURE MODE**. Treat heap/OOM as a preflight blocker; direct-public authentication is a security blocker, unless a properly secured proxy provides authentication and backend isolation. Neither was caused by Arcane; no Tarot datapack was installed.
- **Exact old-mod limitation:** uploaded ReMorphed 4.2 config has **NO usePermissions**, matching official upstream addition of granular permissions only in 7.1; do not use modern LuckPerms remorphed.* nodes. SkinShifter 1.3 config: **changeName=true, changeCape=true, baseCommandOPLevel=2, selfCommandOPLevel=0**; official permission-node support began SkinShifter 3.0. Version-specific command tree registration is seen, but no test of activation or safe reset. ReMorphed config retains killToUnlock=1, killToUnlockPlayers=2, creativeUnlockAll=true, autoTransform=false.
- **New reusable diagnostics:** [scripts/arcane_server_evidence_audit.py](scripts/arcane_server_evidence_audit.py) reads private raw or markdown-export logs/configs WITHOUT mutating server; six synthetic regressions plus real log audit. It reports a conservative ready_for_arcane_load_test=False until memory/auth blockers resolved; clean log still never marks gameplay verified.
- **Owner follow-up resolves priorities:** 2026-11-22 the owner confirms **offline mode is intentional**, and Terralith OOM happened while initially generating a new world and is **accepted for development**. Do not request RAM/JVM arguments or insist on online mode as prerequisites; both remain documented caveats, not proven cured/secure. **NEXT: one Arcane DEV ZIP on a copied/backed-up already-generated world; capture the Arcane-enabled restart log and execute non-OP/OP/team/Seq1 checks.** Keep implementing 32 blocked and 329 partial source definitions independently. **No production deployment.**

## 3g. Owner confirms environment behavior — development testing unblocked

- User explicitly says the **Terralith heap OOM occurred on initial world generation**, expects better behavior now that initial terrain exists, and **accepts the risk**. Do NOT tell the user the issue has been conclusively fixed; watch new chunk generation for recurrence.
- User explicitly says **offline mode is intentional**. Do NOT ask them to change it repeatedly. Offline usernames cannot be authenticated; avoid untrusted direct access/impersonation as an operational caution, not a development hold.
- The audit utility gained development-only acknowledgement flags `--acknowledge-worldgen-oom --intentional-offline-mode`, which downgrade those two *owner-accepted* findings from blockers to visible warnings **only if startup completed**. Other blockers still fail closed. No changes to the server, JVM flags or authentication were made.
- **Historical first Arcane-enabled test:** It detected the original ZIP/menu but failed 2 core functions, 44 decoder definitions and five identity references. PR #44 corrected these; the SECOND real server test has now been performed and confirms Moon Seq9 initialization. See section 3i for the current two remaining armor decoder failures.

## 3h. First Arcane-ENABLED runtime log and decoder fixes — 2026-11-22

- **FIRST RUNTIME TEST ACTUALLY EXECUTED:** user screenshot confirms ONLY_DEV ZIP enabled and /trigger a_help clickable UI. Server 1.18.2/Origins 1.4.1/Apoli 2.3.3 started (11.971s), selected tarot:moon. **FAIL**: both player/detect and player/verify functions rejected due to origin has origin command syntax, **44 power/subpower decoder errors**, and five orphaned permanent Origin drawback refs. The registry count 580 powers/44 origins is **not** a functional/fully-loaded ability count. Exact 51-error category breakdown and names: [real runtime report](docs/ARCANE_FIRST_LIVE_RUNTIME_2026-11-22.md).
- **[PR #44](https://github.com/DoorBlox/origins-tarot/pull/44)** merged source at eef3392080448021e0736c41f03e5a7de004984d with four green exact-head CI workflows (fc223cfcd0b7c76e24f18346760f4b025150a9d6). New [arcane_rev3/compat_141.py](arcane_rev3/compat_141.py) serializes only known supported old-version types and substitutes bounded /spreadplayers Overworld surface blinks for missing origins:random_teleport, uses vanilla random_chance predicates for unavailable origins:chance ENTITY conditions, preserves distinct chance meta actions, corrects required cooldown, render_armor, ingredients, submerged_in, inverted item conditions. New tests inspect both emitted ZIPs recursively. The 402 source authored/110 Resonance counts do NOT change.
- **Player init architecture changed:** each one of 22 selected native Origin JSONs carries an invisible action_over_time runtime_sync power which calls the fixed player/sync/<slug> function and initializes/repairs that Origin's scoreboard state. No broken origin has origin or forced origin set commands, no ordinary user OP. Source CI proves generated function shapes, NOT runtime execution.
- **Historical PR44 request COMPLETED:** Owner installed the PR44 ONLY_DEV build and submitted the second live client transcript plus server log. Its two remaining armor errors are now tracked in PR #46 and section 3i. Do not ask for the older log again or re-test the older ZIP.
- **Existing owner decisions stand:** offline mode intentional, first-worldgen OOM accepted caveat; neither caused these new Arcane power errors. Client already uses Fabric API 0.77.0 and installed Architectury. No new client mod dependency added in PR44.
- **Important:** old 1.4.1 runtime may expose other decoder errors once these ones are fixed. Capture actual post-fix stderr and test every newly exposed type; do not assert all abilities work from four green source CI checks.

## 3i. Second actual server test and PR #46 — Moon Seq9 works, two armor errors remain

- **Owner's client transcript:** [Tarot] Awakened moon at Sequence 9; /trigger a_help, /trigger a_status, /trigger a_slots all work. Primary: The Moon; partner unlocks at Sequence 4; Sequence 9; 1 slot; 0 marks; Slot 1 = The Moon - Sequence 9. This confirms initialization/slot UX in the observed instance, NOT all ability mechanics.
- **Owner's new server log:** no old player/detect or player/verify function parse errors. Power registry 644, Origins 44, Done 11.043s. **Exactly two Apoli POWER decode errors** remain (plus downstream orphan): Temperance Unstable Manifestation and Walking Sanctuary Wraith's Prayer chest, both chest.ingredient expecting item/tag rather than items list. CraftedCore optional Patreon fetch has its own unrelated ERROR; no Terralith OOM on this boot. Exact privacy-sanitized record: [second runtime report](docs/ARCANE_SECOND_LIVE_RUNTIME_2026-11-22.md).
- **Root cause:** adapter compat_141.py recognized item_condition key but did not recognize direct head/chest/legs/feet item-condition fields inside origins:restrict_armor / conditioned_restrict_armor. It consequently left old-invalid ingredient.items arrays unconverted. [PR #46](https://github.com/DoorBlox/origins-tarot/pull/46) scopes that conversion to armor-restriction parent types; both outputs now contain origins:or with individual valid minecraft:item ingredients, preserving the prohibited armor set.
- **TDD/CI:** new tests/test_arcane_141_armor_ingredient.py added BEFORE code; RED CI source bb2a94ad9d34ad02a351b7988e67e63a2e92b82e intentionally failed eight generated-output assertions. FIX source 58c793b98220c18d00eabdffafdbca50e584f59f had **four exact-head green workflows**; rerun on final doc-inclusive PR head before merge. Regression checks both ZIP variants, all generated ingredients, nested multiple power, four armor slots, and no unrelated key rewrite. Authored coverage unchanged.
- **NEXT ACTUAL GAME TEST:** replace previous ONLY_DEV ZIP with fresh PR46 artifact in the BACKED-UP world, restart, check no chest.ingredient decode or missing Temperance power, run non-OP /trigger a_help, /trigger a_status, /trigger a_slots, check persistence/relog, and test armor restrictions (one at a time) as a disposable operator test character. Gameplay fidelity still pending.
- **Safety:** Owner intentionally uses offline mode and accepts fresh-worldgen heap caveat. No mods added, no server/world changes made by source PR, no automatic production release, no change to standard Seq1 fail-closed gate. On final merge, update issue #20 with the exact merge SHA and keep post-fix Minecraft acceptance NOT RUN until owner supplies new log.

## 3j. Wave 8 — 25 additional individual abilities, owner opts to defer runtime smoke (2026-11-22)

- Owner explicitly wants **rapid substantive source development first**, not a server restart to verify the small PR46 armor parser fix. Do not re-ask them to test after every batch; preserve the pending Minecraft 1.18.2 acceptance gate for a consolidated dev ZIP.
- [PR #47](https://github.com/DoorBlox/origins-tarot/pull/47) adds **25 previously blocked individual abilities** in `arcane_rev3/batches/individual8.py`, using supported 1.18.2 native actions, fixed read-only NBT queries, explicit nearby team-safe ally/enemy effects and bounded cooldowns. Representative mechanics: Emperor's shield+villager Hero of the Village trade discount (not exactly 10%), Magician stone speed without protected-block edits, High Priestess book-conditioned Luck/XP, Hierophant torch vision for same-team allies, Justice small-radius selected item read, Hermit fixed stronghold /locate, Death non-lethal Wither instead of unsupported execute, Moon bone-right-click passive regeneration, Moon potion regeneration upgrade and Judgement +10% hostile damage.
- **Truthfulness:** All 25 are **PARTIAL**, each records `missing` exact hooks. No actual cross-lectern book vault, enchant lapis discount, chat edits, forced AI aggro, no consent-free player targeting, no zombie minions, no genuine resurrection or player-target kills. The source status is a playable subset, **not** completion of exact handbook semantics.
- Expected manifest: **434 specified, 427 compiled (73 full, 354 partial), seven individual blocked; 110/110 Resonance source entries compiled**. Exactly seven remain: Hierophant Dietary Expansion (requires safe override of pinned meat ban), and Hanged Man Sin-Bearing, Burden Bearer, Trinity, Sin Overflow, Depraved Dependent, Weight of Sin Made Manifest. See [updated seven-blocker register](docs/ARCANE_REMAINING_BLOCKERS_AND_OWNER_DECISIONS.md).
- New `tests/test_arcane_individual8.py` requires 25 handbook-accurate names/sequences, exact current manifest, both generated ZIPs, no fake powers/unsafe OP commands/unbounded world edits, and verifies actual native subset shapes. Earlier tests were updated to assert historical **minimum** coverage rather than stale 402/434 exact totals; future source batches must remain free to improve coverage without defeating older tests.
- **Next actual work:** after PR47's four exact-head green workflows and safe merge, implement a **shared bounded Hanged Man Sin scoreboard resource** in an isolated source PR (do not fake per-hit event equality when unavailable), then Hierophant fish-only exception. After source work, test the newest ONE dev ZIP on copied world; check old PR46 chest.ingredient, new Json power decoding, all 22 paths, ally/teamless protections, Sin state/respawn and opt-in Seq1 Resonance.
- **No new client/server mods**, no direct live server/world changes, no forced test prompt, normal Sequence1 still locked by default. Update issue #20 with final PR47 merge SHA and actual counts.

## 4. Exact gameplay contract — do not break

- Seq 9: one chosen primary pathway, one Seq9 kit auto-active; Seq 8/7/6/5: two/three/four/five automatic kits of the primary pathway.
- Seq **4**: fixed *partner pathway* unlocks and **six** player-editable slots; Seq **3**: seven; Seq **2**: eight. One slot = a `(pathway, sequence)` pair and grants **all source-defined abilities for that sequence**. All available sequence numbers must be at least the player's current Sequence; duplicates rejected. Formula through Seq2: `slots = 10 - sequence`.
- Seq **1**: slots abolished, one *complete* paired Resonance suite (all Seq9–0 powers) activates in the intended design. **NORMAL gameplay is CURRENTLY BLOCKED**, consumes no ritual materials; **OP-enabled isolated test-world transition from PR #39 exists**, grants all ten source-compiled but often PARTIAL powers after genuine ritual/marks and preserves parent penalties. Seq0 included. Never remove default guard before actual 1.18.2 runtime acceptance.
- 22 separate identity Origins; 11 fixed unordered pairs from `arcane_rev3/model.py` (do not substitute the older V3 curated pairs):
  1. Fool + Hanged Man = `paper_martyr`
  2. World + Justice = `marked_verdict`
  3. Hermit + Chariot = `burning_archive`
  4. Death + Tower = `crumbling_reaper`
  5. Magician + Strength = `impossible_fist`
  6. Emperor + Lovers = `benevolent_crown`
  7. Devil + Judgement = `binding_contract`
  8. Star + Empress = `starless_poison`
  9. Sun + Moon = `eclipse`
  10. Temperance + Hierophant = `walking_sanctuary`
  11. High Priestess + Wheel of Fortune = `loaded_dice`
- Primary identity drawbacks **must remain permanent** after slot reassignment; Sequence9 drawback power IDs are pinned to the primary Origin rather than removable kit grants. Fool's Spiritual Expenditure is **+25%** exhaustion, not the older +40%. Of 22 pathways, 21 have *some* innate drawback implementation; Wheel's **Debt of Fate** remains absent. Justice, Hanged Man and Lovers' drawbacks are partial; see manifest and issue #20.
- 18 built-in Elytra gliders via Origins, **not** creative flight. No wings for Emperor, Hierophant, Strength, Judgement. Retain player re-login/reconciliation, combat lock and pause handling.
- Combat lock on ascent: 200 ticks after damage dealt/received or bow/crossbow/trident use. 1.18.2 scoreboard stats and `entity_hurt_player` are used; do **not** reintroduce the nonexistent 1.18.2 `player_hurt_entity` advancement trigger.

## 5. Player interaction, aliases and administration

- Intended ordinary-user alias: `/tarot`, `/tarot status`, `/tarot slots`, `/tarot ascend`, `/tarot slot N tarot:card S`, `/tarot slot N clear`, `/tarot slot auto`, `/tarot slot swap N M`, `/tarot reset`. Generated `output/tarot.json` is for Command Aliases 1.0.1 under `config/commandaliases/`, *not* the datapack folder. Its parser with non-OP users **NOT yet game-verified**.
- **Guaranteed datapack-side fallback, pending in-game test:** any non-OP player calls `/trigger a_help` or `/trigger a_slots`, clicks **Edit slot N** (1–8), selects primary or unlocked partner, then Seq 9–2. Clickable Clear/Auto/Status exist. Only `/trigger` events are in `clickEvent`; server-side `slot/assign` revalidates unlocks and duplicates. Implemented in PR #26, tests `test_arcane_clickable.py`. Don't accidentally allow `/function`, `/op` or freeform commands in a chat click event.
- Admin OP/console-only: `/execute as <player> run function tarot_arcane:admin/rollback_player` and corresponding `resume_player`. Whole online population: `/function tarot_arcane:admin/rollback_all` and `resume_all`. These persistently pause/reconcile Arcane slot grants but **do not restore a world backup, change innate Origin drawbacks or migrate V3 state**. Verify on disposable test world.
- No LuckPerms dependency for vanilla `/trigger`. LuckPerms may be installed for other permissions but must not become an unreviewed shortcut to elevated aliases.
- Preserve player-local scoreboards, action cooldowns and relog state; fail closed on unknown/invalid or hostile commands.

## 6. Code map / where to modify

| Path | Role |
|---|---|
| `arcane/catalog.json` | Source-traced catalog, 434 entries |
| `docs/HandbookRev2.txt` / `docs/HandbookRev3.txt` | Mechanical specs |
| `arcane_rev3/model.py` | Pure immutable slot rules, fixed pair graph; reference for expected semantics |
| `arcane_rev3/powers.py` | Registers individual/Resonance concrete powers into manifest, performs no-placeholder checks and retaliation guards |
| `arcane/templates.json` | Historical native power templates; **inspect before adding duplicates**; some values were recently corrected |
| `arcane_rev3/batches/{shared,support,control,mobility,native2,individual3,resonance,resonance2}.py` | Parallelized source-traced batch definitions; preferred location for new powers |
| `arcane_rev3/full_build.py` | 22 Origin JSON packs; scoreboard runtime, slots/grants, progression, clickable UI, admin recovery, manifest + ZIP builds |
| `arcane_rev3/build.py` | Separate Fool Sequence9 sandbox; do not mistake for 22-Origin full build |
| `arcane/tags.json` | Hostile/undead/passive mobs, block/item tags; native vanilla names |
| `tests/test_arcane_141_schema.py` | Origins 1.4.1 type allowlist, nested types, grant command checks |
| `tests/test_arcane_full.py`, `test_arcane_clickable.py`, `test_arcane_bulk38.py`, `test_arcane_native2.py`, `test_arcane_resonance.py`, `test_arcane_wave37.py` | Rev3 and batch regressions |
| `progression/`, `generate.py`, `passive_v2.py` | Existing older V3/V2 system; maintain regression compatibility; do not accidentally rewrite |
| `.github/workflows/{arcane-full,arcane_rev3,ascension,datapack}.yml` | Four PR gates + artifact outputs |
| `docs/ARCANE_REV3_DEVELOPMENT.md` | Technical history and exact known limitations |
| [Issue #20](https://github.com/DoorBlox/origins-tarot/issues/20) | Single remaining-work tracker |

Do **not** manually edit generated `output/` artifacts or the unpacked `datapacks/` trees instead of the generator. CI may sync older V2-generated source files back to `main`. Avoid making edits to generated files that will be overwritten.

## 7. How to validate, build and read truthful coverage

From an up-to-date checkout with **Python 3.12**, no extra Python dependencies:

```bash
git fetch origin
git switch main
git pull --ff-only
python3 -m compileall -q arcane_rev3 progression tests
python3 -m arcane_rev3.full_build
python3 -m unittest discover -s tests -p 'test_arcane_full.py' -v
python3 -m unittest discover -s tests -v
python3 -m arcane_rev3.build
```

A separate `progression.build` and `generate.py` are also run in CI for legacy compatibility. Use the actual workflow commands in GitHub rather than guessing all build flags. If working through the GitHub connector only, edit a branch, open a PR, and read exact-head Actions **job logs** before claiming success.

The full-build workflow prints the manifest summary. Artifacts are inside GitHub Actions **tarot-arcane-rev3-22-origin-dev-not-production**:

- `Arcane_Rev3_22_Origins_ONLY_DEV_1.18.2.zip` (replace Origins layer)
- `Arcane_Rev3_22_Origins_ADDON_DEV_1.18.2.zip` (add to Origins layer)
- `arcane_ability_manifest.json` (source truth)
- `tarot.json` (separate Command Aliases config)

Choose **one inner ZIP only** in a new disposable world, never both or alongside the old V2/V3 Tarot ZIPs. ZIP `pack.mcmeta` must be at root; outer GitHub artifact ZIP must be unwrapped. Do not imply these are production-ready because they download successfully.

### PR quality bar (mandatory)

1. Query live `main`, issue #20, open PRs, CI, relevant source and both handbooks. Confirm this handoff isn't stale.
2. Take a focused batch (ideally ~15–40 independent abilities in parallel modules; faster only if source tracing and test quality remain high). Write contract tests, register *real* power JSON and each `missing` field. Prefer source `[D]`, then defensible `[D/S]`; avoid replacing scripted mechanics with misleading nominal buffs.
3. Run manifest/build/schema/full regression. Cross-check expected/actual status and count; don't hand-edit numbers or use false `full` statuses. Critically review current 1.4.1 support for every power/condition/entity action, not just power names.
4. Open a focused non-draft PR. **Four workflow checks must pass on the *exact head SHA***: Arcane full, isolated Fool alpha, V3 Ascension, base Origins. Inspect failing logs, fix the *cause* (including flawed tests), then re-run; **no merge while red or pending**.
5. Diff review + verify PR head/mergeability, squash merge if all checks pass, check resulting `main` checks, then update **issue #20 + this handoff**. Historical PRs #7 and #8 were intentionally closed as superseded/incompatible; do not revive.

## 8. Important recent implementation details / mistakes already found

- **PRs #10–#19**: foundation, pause, combat lock, UI, permanent drawbacks, source-traced abilities, true 10-block spherical Fool Spirit Vision, hostile-only retaliation guard.
- **#21**: +38 source-traced individual skills in three independent modules; Lovers' real 600t loneliness counter (partial: checks any nearby player, not same-team).
- **#22**: +15 additional native interaction skills; player-owned **Transmute** executes a fixed guarded inventory transaction, consumes two iron only if present and then grants one gold; right-click hooks cannot claim unimplemented cooldowns.
- **#23**: +23 initial Resonance JSON definitions across all 11 pair forms; still no player unlock.
- **#24**: +28 further Resonance and +9 individual skills; all 37 explicitly partial; total reaches 241.
- **#25**: 1.4.1 schema gate uncovered `origins:modify_healing` in Lovers' Fertile Hands, which is unavailable. Fixed to native crop break +20%; its +25% healing requirement stays partial/blocked as described.
- **#26**: clickable non-OP chat menu using vanilla `/trigger` independent of old Command Aliases parser; test counts rose to 96.
- **Other known correctness pitfalls:** Older incremental upgrade template deltas were incorrect (Shaman actually 3 HP, Sun's +50% undead and World's +30% projectile are standalone bonuses). With slots, old and upgraded powers may **stack accidentally**: replacement-aware suppression is still required. The old area_of_effect shape did **not** guarantee Fool's 10-block sphere in Origins 1.4.1; fixed server-trusted `@e[distance=..10]` command, still requires Minecraft runtime check.
- **Safety:** Incomplete enemy-vs-ally team targeting; hostile-mob-only fallback guards retaliation. Avoid globally applying poison/Wither to `@a`. The fixed command actions with permission level 2 are written *by the datapack generator* and cannot interpolate player chat/input.
- **Do not count script-like placeholders as completion.** Some partials use conservative approximations (e.g., an XP drop in place of actual extra mob loot). Review whether they satisfy useful behavior and remove them if misleading.

## 9. Remaining work and prioritized next steps (do work, don't only plan)

**High-priority correctness:** Implement or prove limits of **same-team comparisons** (including ally-only healing and enemy-player PvP), permanent Wheel **Debt of Fate**, Lovers ally-only loneliness, upgrade replacement/nonstacking, true right-click cooldowns, and world/relog/respawn/pause integrity. Add tests tied to actual commands. Maintain 1.18.2 compatibility.

**Current blocked/fidelity work (after merged #40):** **32 individual entries blocked** (listed by name/seq in `docs/ARCANE_REMAINING_BLOCKERS_AND_OWNER_DECISIONS.md`); **0 Resonance blocked (110/110 source-compiled)** but MANY are partial. **329 compiled partial entries** have real effects yet omit exact scripted hooks/events; prioritize source fidelity, same-team protection, persistent Sin state, reversible mod integrations, accurate triggers and gameplay acceptance instead of dummy completions.

**Resonance activation:** Intended Rev3 Sequence1 activates all ten paired powers automatically and retains both permanent parental drawbacks. [PR #39](https://github.com/DoorBlox/origins-tarot/pull/39) implemented the **OP-only test-world transition** with original five acting marks, altar and **one Nether Star + eight Ender Pearls**, mode2, ten paired source grants, second parent's immutable identity, relog/repair and pause/resume. Operator flag `a_rtest` MUST be set by OP before test ascension; without it the Seq1 path is locked and consumes nothing. Do not silently make this permanent gate part of intended final game. Read `docs/ARCANE_SEQ1_OPERATOR_TEST.md`; separate manual one-power test ZIP is also available.

**Actual Minecraft runtime: SECOND BUILD PARTIAL PASS / TWO LOADER FAILS, PR46 source fix CI PASS, NEW BUILD NOT RUN.** The user installed PR44's corrected ONLY_DEV ZIP; Tarot Moon awakened at Seq9, and non-OP help/status/slots correctly reported the Moon Seq9 one-slot mode with 0 marks and partner at Seq4. The server started in 11.043s with registry 644 powers/44 origins and no earlier detected function parse failures. The log STILL rejects two armor-restricting powers: temperance/9_unstable_manifestation and walking_sanctuary/9_wraith_s_prayer_chest at chest.ingredient; Temperance identity then references its unregistered definition. No new Terralith OOM; offline mode intentional. [PR46](https://github.com/DoorBlox/origins-tarot/pull/46) tests/fixes nested armor slots (four item-condition fields, invalid ingredient.items to OR item children), initially RED on eight generated-output assertions and then four source CI GREEN. **NEXT: replace OLD ONLY_DEV ZIP with fresh exact-PR46 build on a backed-up test world, restart, check zero Apoli chest.ingredient errors, repeat non-OP status/slots, then verify actual armor gameplay, PvP and OP-only Seq1.** See [second runtime guide](docs/ARCANE_SECOND_LIVE_RUNTIME_2026-11-22.md).

**Deployment:** All merged PRs remain **source-only**. The owner accepts offline mode and the fresh-world OOM as development environment risks, but that does **not** count as functional acceptance. Optional dev ZIPs/OP transition are for backed-up isolated testing, not an actual SMP production release. Production still needs actual gameplay verification, versioned build, migration, rollback and explicit authorization; no Arcane ZIP is production-approved.

### Immediate starter action for the next chat

1. Open [this repository](https://github.com/DoorBlox/origins-tarot), [issue #20](https://github.com/DoorBlox/origins-tarot/issues/20), live `main`/PRs, `docs/HandbookRev3.txt` + Rev2, and output manifest from latest Arcane Actions run.
2. Check whether the most urgent blockers/compatibility issues were changed since this checkpoint.
3. Implement or precisely audit the **32 remaining individual blocked abilities** and **329 partial source fidelity gaps**; prioritize actual Hanged Man Sin lifecycle, events, team safety and old installed mod APIs. Seq1 OP test transition is already merged in #39. Choose independently testable PRs, and never claim parallel agents unless actually running them.
4. Make substantive source changes **now**, not a speculative plan; run CI, merge only green exact-head PRs, update issue #20 and this handoff afterward.

### Copy/paste continuation prompt

> Continue as the Arcane V2 Rev3 development agent for `DoorBlox/origins-tarot`. Read `AGENTS.md` and `CHATGPT_HANDOFF.md` on live `main`, issue #20, both Rev handbooks and actual source. Re-query live GitHub state; previous SHA is a checkpoint only. Owner authorized broad source edits and safe merges, asks for fast sizable batches, but **NO KubeJS/custom Java and NO live server deployment**. Preserve old V2/V3 and the no-OP `/trigger` UI. Implement source-backed ability batches and resolve correctness blockers, write regressions, require four exact-head CI passes and verify manifest counts, merge safe PRs, then update the handoff and issue #20. Do not pretend partial abilities or compiled Resonance are playable/full. Start work immediately.

---

**Checkpoint maintenance rule:** After each substantial milestone, update *in-place* the live `main` hash, counts, latest checks, active PRs, decisions, what's still missing, and the next smallest verifiable action. Prefer linking primary sources over copying entire logs/transcripts. Do not put passwords, auth tokens, personal info or server credentials in this public repository.
