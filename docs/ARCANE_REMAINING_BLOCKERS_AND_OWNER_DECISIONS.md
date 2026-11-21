# Arcane V2 Rev3 — complete source coverage; remaining gameplay fidelity and release gates

**Current source checkpoint (2026-11-22; PRs #54 and #55 merged).** All **434/434** Rev2 catalog abilities have concrete source definitions (**73 source-full, 361 explicitly PARTIAL, 0 blocked**), including all **110/110** fixed-pair Resonance entries. **23 partial abilities improved across two CI-verified source PRs, but zero promoted to source-full without evidence.** These are authoring statistics, NOT in-game acceptance. Normal Seq1 stays locked outside the OP-only disposable-world test.

## Last source blocker: Hierophant Dietary Expansion

- **Pinned permanent Seq9 identity remains.** The Sacred Dietary Vow native Origin power is not a removable slot. Existing tarot:meat tag is split into exactly six fish items and eleven nonfish meat items via new tarot:fish and tarot:nonfish_meat tags.
- **Nonfish meat stays prohibited unconditionally.** The original immutable vow is now a native multiple power with one unconditional nonfish prevent_item_use subpower and one independent fish prevent_item_use subpower.
- **Fish is allowed only when the trusted Arcane slot source grants Seq1 Dietary Expansion.** The fish restriction has an inverted origins:power condition tied to tarot:hierophant/1_dietary_expansion from tarot_arcane:slot_grants. Revoking that source power restores the fish restriction. The upgrade itself still bans nonfish meat, so no disappearance of permanent nonfish identity is possible.
- **PARTIAL by design:** normal Rev3 Sequence1 is the fixed paired Resonance rather than an equipable individual Seq1 kit. This source-defined exception is useful for an opt-in developer grant and future unlock policy, but normal players do not automatically acquire it. Real 1.18.2 runtime acceptance is pending. See https://github.com/DoorBlox/origins-tarot/pull/49 and tests/test_arcane_dietary_expansion.py.
- No dummy origins:simple, OP access, vanilla inventory mutation or client mod added; four exact-head CI workflows required before merge.

## Remaining 361 partial fidelity gaps

- **Sin resource:** six Hanged Man powers use capped damage-taken scoreboard storage, 200-tick idle dissipation, team-safe low-health weakening, Trinity 100t window, and bounded 1200t capstone with 14400t cooldown. Still unable to identify exact *distinct* damage sources, dynamically inflict stored HP as direct AoE, heal exact percent of Sin, or summon source-faithful attacking minions. PARTIAL labels are permanent until those semantics exist and are tested.
- **Resonance:** all 11 paired suites have ten source powers each, but many are partial native substitutes; normal Sequence1 remains fail-closed, OP-gated real Seq2-to-1 ritual is test-world only.
- **World/API:** source cannot truly implement protected adjacent blockbreak, cross-lectern storage, enchanting lapis discounts, arbitrary mob AI aggro, real revival of historical mobs, other-player chat editing, precise potion resource events, client model/skin manipulation, world-state light/weather zones and exact score-driven damage under current datapack-only 1.18.2 runtime. Do not overclaim.
- **Team safety:** only explicit allowlisted vanilla teams tarot_red, tarot_blue, tarot_green, tarot_gold; same team allies, different known teams enemies, unlisted and teamless players neutral. LuckPerms group membership is not combat allegiance.
- **Mods:** real server has ReMorphed 4.2, SkinShifter 1.3, Pehkui 3.8.3, Extra Keybinds 0.5.0, Fabric Permissions API 0.3.1 and LuckPerms 5.3.86. The older ReMorphed and SkinShifter do not inherit later permission APIs; do not invent mod command or automatic reset behavior.
- **Runtime evidence:** after PR44 owner verified Moon Seq9 awakening and successful help/status/slots, with two residual chest.ingredient decoder errors. PR46 corrected these in source. The owner explicitly deferred that minor Minecraft server retest while source work continued. PR47, PR48 and PR49 are source-checked, not real in-game accepted. Offline mode intentional, initial Terralith worldgen heap OOM accepted caveat.
- **No hosted SMP deployment** authorized by source CI. User authorizes source edits and merges after all four exact-head green workflows; not world/player data mutation.

## Non-OP active key focus — source merged in PR #50

- [PR #50](https://github.com/DoorBlox/origins-tarot/pull/50) merged `5614087df2c444ffd9db163da9a8580d8219314f` after four exact-head green CI workflows. Many active powers share the same native Origins hotkeys; the new **opt-in** focus menu lets a player select ONE currently held active ability to receive the keypress. `/tarot focus` and clickable `/trigger a_focus_menu` are non-OP; `/tarot focus legacy` restores normal all-active default. Never infer this is a new source handbook ability.
- Key correctness: use client-synchronized hidden internal `origins:power` marker tokens rather than server-only `origins:scoreboard` entity conditions. Server validates parent-power ownership before selection; rollback revokes the internal focus source, and kit refresh/periodic reconciliation removes stale selections. No new mods or player OP authority.
- **Source CI passed; real Fabric 1.18.2 client/runtime test NOT RUN** by owner's explicit preference. When testing later, check focus/legacy switching, concurrent keypresses, revoked powers, respawn/relog, multiplayer isolation, UI accessibility and client conflicts with Extra Keybinds/ReMorphed. Legacy behavior remains default until opting in.

## Next development priorities

1. Raise *actual fidelity* of the highest-impact partial definitions, starting Sin, gameplay cooldowns, source identity, temporary-effect cleanup, AI/skin/mechanic fallback and full team/neutral safety.
2. Audit all 11 Resonance suites against the Rev2/Rev3 handbooks, source grants and target rules before declaring them playable.
3. At owner's preferred consolidated acceptance point, install one latest ONLY_DEV ZIP in a backed-up test world and check full data reload, no missing powers, 22 paths, 11 pairs, Moon Seq9 status, team safety, Sin state, death/relog/pause, mod commands and opt-in Seq1. Record PASS/FAIL/NOT RUN. No production promotion until verified.
4. Avoid asking for already-supplied mod lists/logs, changing intentional offline mode, or demanding a restart after each small source change.

## Latest verified source fidelity waves and next inventory

- [PR #54](https://github.com/DoorBlox/origins-tarot/pull/54): 13 selected abilities receive strictly team-filtered ally regeneration/speed, enemy-player Slowness/Glowing, and nighttime Star Read. Merged `ebe1423b0bd994505c8c01bf64a9882601194122` after 4/4 exact-head green CI at `53c1cc752e1def5c69d1a77e7a7d27fc0b3f3ed2`.
- [PR #55](https://github.com/DoorBlox/origins-tarot/pull/55): 10 further partial powers gain guarded enemy-player and ally components; Star Read Reaper correctly night-gated. Merged `3dd7f570896ef6309c03aed75b8009f608ed7c4e` after 4/4 exact-head CI at `3ac7c2ccd25427312881bbed74e6313e7c2eebf8`.
- **Inventory generator:** run `python -m tools.arcane_fidelity_report --format markdown` or `--format json`; inventory covers all 361 PARTIAL records and their original `missing` claims. Keyword groups overlap and are for triage only. A global negative-player-selector regression gate covers all compiled power definitions, but actual Minecraft mechanics remain UNTESTED until the owner's consolidated world acceptance.
- **Still missing:** unsupported scripting events, exact numerical effects/individual damage-source tracking, NPC/AI control, client skin/model hooks, permanent dynamic world regions, known-safe old mod API commands and inverse cleanup. Do not change architectures silently, remove the test-world Seq1 lock, or conflate a 434/434 source compile with ready-to-ship gameplay.
