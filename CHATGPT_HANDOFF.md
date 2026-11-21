# HANDOFF — Tarot Club / Arcane V2 Rev3 (datapack-only)

> **READ THIS FIRST IN A NEW CHAT.** This file is a durable engineering checkpoint, **not** proof of current GitHub state. First query the live `main` branch, open PRs, CI, and issue [#20](https://github.com/DoorBlox/origins-tarot/issues/20), then read the authoritative handbooks. Do not ask the owner to re-explain the project.

**Last verified snapshot:** 2026-11-22 (Indonesia time), `main` at `326499b0f62105f5e0944d97e9f0f0ca2e4c00f4` after merged PR [#26](https://github.com/DoorBlox/origins-tarot/pull/26). This hash is *historical*; never assume it stays current. Last observed open PRs: **none**. The Arcane V2 Rev3 developer pack **has not been installed or tested on the live SMP**.

## 1. Mission and owner's standing instructions

Build **the entire Arcane V2 Rev3 Tarot Club experience** for Minecraft Java 1.18.2/Fabric/Origins: all 22 Major Arcana pathways, 434 handbook abilities (324 individual + 110 Resonance), 11 fixed paired Resonances, honest progression and slots, identity drawbacks, fair team-aware targeting and an accessible non-OP `/tarot` UX. The owner wants **fast, substantial, parallelized batches**, not one ability or PR at a time. Proactively implement, test, open PRs and merge sound source changes without stopping for repetitive permission requests. User has explicitly authorized repository edits and merges.

**Hard constraints that authorization does not erase:**

- **NO KubeJS, no custom Java/Fabric mod**, and do not silently change the chosen datapack-only architecture. Handbook KubeJS examples are *ideas*, not permission to install KubeJS. Vanilla data packs, scoreboard functions, Origins/Apoli 1.4.1 powers and existing approved mods are the constraints.
- **No live SMP install/deployment/world mutation** from a source-code merge. Do not touch hosted player saves, scoreboard.dat, datapacks, configs or admin permissions without a separately grounded deployment/test request and safety verification. Develop in GitHub; keep releases explicitly test-only until actual 1.18.2 runtime acceptance.
- Never invent completed abilities or dummy powers. If a source mechanic cannot be faithfully reproduced, implement a real *subset* only when meaningful and label it **partial** with `missing`; otherwise leave it **blocked**. Do not equate compiled JSON or green Python tests with in-game functionality.
- **Do not harm teammates** with offensive effects. Official Rev3 target rule: hostile mobs **and enemy players**, but *not* same-team players; healing/buffs target self and same-team allies. Current incomplete fallback fails closed to `#tarot:hostile` mobs for offensive effects; enemy-player PvP remains a known partial until safe team comparisons are proven. Some positive effects currently include other players indiscriminately; they are also partial.
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

**Version notes:** Minecraft Java **1.18.2**, Fabric, Origins **1.4.1**, pack format **9**. Owner has mentioned Fabric API, Pehkui, Extra Keybinds, Command Aliases **1.0.1**, ReMorphed, Woodwalkers, CraftedCore, SkinShifter and LambDynamicLights. **No Immersive Portals**. Verify exact mod jar/API versions in a disposable server; don't rely on newest Apoli examples. Official [Origins 1.4.1 power types](https://origins.readthedocs.io/en/1.4.1/types/power_types/) and [Command Aliases docs](https://wiki.commandaliases.flashyreese.me/command-modes/custom) are helpful but cannot substitute for the installed binary's behavior.

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

## 4. Exact gameplay contract — do not break

- Seq 9: one chosen primary pathway, one Seq9 kit auto-active; Seq 8/7/6/5: two/three/four/five automatic kits of the primary pathway.
- Seq **4**: fixed *partner pathway* unlocks and **six** player-editable slots; Seq **3**: seven; Seq **2**: eight. One slot = a `(pathway, sequence)` pair and grants **all source-defined abilities for that sequence**. All available sequence numbers must be at least the player's current Sequence; duplicates rejected. Formula through Seq2: `slots = 10 - sequence`.
- Seq **1**: slots abolished, one *complete* paired Resonance suite (all Seq9–0 powers) would become active. **CURRENTLY BLOCKED** and the failed ascension must consume **no ritual materials**. Seq0 is the paired capstone. Do not weaken this fail-closed gate until 110/110 source abilities and a real transition/migration are working and tested.
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

**Bulk ability completion:** 193 entries are still blocked in the snapshot: **134 individual**, **59 Resonance**. Expand `arcane_rev3/batches` in parallel source-traced batches; identify what is truly impossible under no-KubeJS/no-custom-Java and avoid deceptive "done" counts. Upgrade 168 partial definitions toward source fidelity. **51/110 Resonance definitions are compiled but NONE are in playable kits**.

**Resonance activation:** After all 110 are faithful, build validated 11 full 10-kit grants, one-way transition at Sequence1, permanent identity penalties and rollback/relog integration. Before that, keep all pair Origins unchoosable and the Sequence2→1 ritual blocked without spending resources.

**Real Minecraft acceptance:** Build a disposable dedicated Fabric 1.18.2 / Origins 1.4.1 server with exact mods, 2–6 non-OP and OP test accounts, clean logs. Verify pack load/unknown Origins schema first; then `/tarot` old alias vs `/trigger a_help` fallback, 22 Origins and 18 wings, progression from Seq9 to Seq2, exact slot rejections, ally/enemy PvP and undead-only restrictions, health/regen/cooldowns/consumptions, death/relog/restart, admin pause/resume, CPU/tick performance, and migration isolation. Record **PASS/FAIL/NOT RUN**, reproducible logs and screenshot/command evidence. **CI cannot substitute.**

**Deployment:** Only after explicit acceptance and a backed-up, versioned release branch/artifact/migration/rollback plan. The owner currently has **nothing to install**.

### Immediate starter action for the next chat

1. Open [this repository](https://github.com/DoorBlox/origins-tarot), [issue #20](https://github.com/DoorBlox/origins-tarot/issues/20), live `main`/PRs, `docs/HandbookRev3.txt` + Rev2, and output manifest from latest Arcane Actions run.
2. Check whether the most urgent blockers/compatibility issues were changed since this checkpoint.
3. Choose a **bulk** implementation track (e.g., 20–40 source `[D]` individual abilities) and a **correctness** track (team/progression/stacking) as separately testable PRs; if concurrent agents aren't actually available, perform the tracks sequentially without claiming parallel execution.
4. Make substantive source changes **now**, not a speculative plan; run CI, merge only green exact-head PRs, update issue #20 and this handoff afterward.

### Copy/paste continuation prompt

> Continue as the Arcane V2 Rev3 development agent for `DoorBlox/origins-tarot`. Read `AGENTS.md` and `CHATGPT_HANDOFF.md` on live `main`, issue #20, both Rev handbooks and actual source. Re-query live GitHub state; previous SHA is a checkpoint only. Owner authorized broad source edits and safe merges, asks for fast sizable batches, but **NO KubeJS/custom Java and NO live server deployment**. Preserve old V2/V3 and the no-OP `/trigger` UI. Implement source-backed ability batches and resolve correctness blockers, write regressions, require four exact-head CI passes and verify manifest counts, merge safe PRs, then update the handoff and issue #20. Do not pretend partial abilities or compiled Resonance are playable/full. Start work immediately.

---

**Checkpoint maintenance rule:** After each substantial milestone, update *in-place* the live `main` hash, counts, latest checks, active PRs, decisions, what's still missing, and the next smallest verifiable action. Prefer linking primary sources over copying entire logs/transcripts. Do not put passwords, auth tokens, personal info or server credentials in this public repository.
