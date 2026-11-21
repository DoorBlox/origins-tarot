# Arcane V2 Rev3 — remaining true source blockers and fidelity debt

**Source checkpoint: PR #47 / 2026-11-22 (pending merge/gameplay acceptance).** The authoritative Rev2 catalog has **434** abilities; wave8 adds **25 individual source-mapped partials**. Expected source manifest after this PR: **427 compiled (73 source-full + 354 partial), 7 blocked**, with all **110 Resonance source powers present**. This does **not** mean 427 fully working or game-tested powers. [PR #47](https://github.com/DoorBlox/origins-tarot/pull/47) includes 25 new concrete, bounded substitutes in `arcane_rev3/batches/individual8.py` and regressions in `tests/test_arcane_individual8.py`. Check the actual generated manifest after every merge.

## Seven still-uncompiled individual abilities

| Pathway | Seq | Ability | Original requirement and reason not claimed |
| --- | ---: | --- | --- |
| Hierophant | 1 | **Dietary Expansion** | Fish become edible, while existing Seq9 meat restriction remains for non-fish. Requires an upgrade-aware nonstacking exception to the **pinned** dietary vow; ordinary buff would falsely claim it works. |
| Hanged Man | 9 | **Sin-Bearing** | 25% damage into capped shared Sin (16 HP), 200-tick inactivity decay, low-health 8-block burst, hostile+enemy-player team-safe targets, weakness and proportional healing |
| Hanged Man | 5 | **Burden Bearer** | 10% damage reduction while Sin exists; 60-tick Regeneration when Sin dissipates |
| Hanged Man | 3 | **Trinity** | Three distinct damage sources in 100 ticks grant Resistance II for 60 ticks and heal 2 hearts |
| Hanged Man | 1 | **Sin Overflow** | Upgrade Sin burst to radius 10, Weakness II + Slowness II, and heal 75% stored Sin |
| Hanged Man | 1 | **Depraved Dependent** | 20% chance on kill to spawn a max-two AI minion for 300 ticks, 2400-tick cooldown |
| Hanged Man | 0 | **Weight of Sin Made Manifest** | Primary key, 1200-tick active window, 14400-tick cooldown, full Sin/capstone combination |

Do not register a seven-line fake placeholder or an empty `origins:simple` power to make the number 434. Any partial must have a tangible runtime behavior, fail-closed multiplayer targeting and an exact missing-API disclosure.

## 354 partials and remaining fidelity work

- The **25 new wave8 implementations are explicitly PARTIAL**. They preserve bounded gameplay intent (e.g., Hero of Village near shield-bearing Emperor and villagers; small-range self-only player Health/held item disclosure; source-safe right-click passive regeneration; tagged hostile debuffs; fixed stronghold locator; potion self-regeneration), **not** complete event semantics. No inventory duplication, teleport event cancellation, villager trade handler, cross-lectern storage, AI ownership, normal-player OP, real resurrection, terrain damage or global weather is claimed.
- **Sin engine is the highest-priority shared source gap:** sampled per-hit damage accounting and saturation, 200-tick idle decay, safe exact power-owned reset on revoked slots/relog, capped burst, no teammate damage, upgraded modifiers, cooldowns, and online/offline save semantics. Even a scored substitute must be clearly described as approximate if 1.18.2 lacks per-source event context.
- **Legacy mod APIs:** real server has ReMorphed 4.2, SkinShifter 1.3, Pehkui 3.8.3, Extra Keybinds 0.5.0, LuckPerms 5.3.86, Fabric Permissions API 0.3.1. ReMorphed granular permissions were added later (7.1); SkinShifter LuckPerms nodes later (3.0). Actual command + inverse reset is unverified; do not blindly apply modern config or require new mods.
- **Multiplayer source of truth:** explicit vanilla teams `tarot_red`, `tarot_blue`, `tarot_green`, `tarot_gold`. Other-team effects only when BOTH caster and target are in the allowlist; same team allies, unassigned/unlisted neutral. No public team management and no unintended negative `@a` selectors.
- **No live SMP deployment:** real test after PR44 proved Moon Seq9 initialization and help/status/slots, with two item-ingredient loader rejects. PR46 source fixed both, but user elected to **defer that minor server recheck while broader source development continues**. PR47 output is source CI only, not loader-accepted gameplay. Later test one isolated backed-up current-version DEV ZIP and capture parser/power/identity errors.
- **Normal Sequence1 fail-closed** despite 110/110 compiled Resonance definitions; operator-enabled real Seq2->1 transition remains development-test only, not a production release. The next source sprint should prioritize the Sin state machine, diet upgrade exception, team-target audits, and deepening 354 partial power semantics before inviting production deployment.

## Standing owner decisions

- Continue substantial batches of source development **now**; do **not** require another Minecraft server test between every minor source fix. Do not pretend deferred acceptance succeeded.
- Owner permits documented, bounded gameplay workarounds without KubeJS, custom Java/Fabric extension or Immersive Portals. Avoid shallow/no-op placeholders.
- Offline authentication is intentional; initial fresh-worldgen Terralith heap event is an accepted development caveat. Do not ask to change either merely to write source.
- Ordinary GitHub source edits/merges are authorized **after all four workflows are green at exact PR HEAD**. Keep `CHATGPT_HANDOFF.md` and issue #20 synchronized, with accurate compiled/full/partial/blocked counts.
