# Operator-enabled Seq2 to Seq1 Resonance development transition

**Status: isolated Minecraft 1.18.2 test worlds only. Not for a live SMP.** All 110 handbook-named Resonance entries compile, but many powers are explicit PARTIAL substitutes. Neither structural CI nor manual preview proves Minecraft compatibility, event timings, PvP targeting, source restoration, cooldowns or performance.

This feature implements the **Rev3 handbook Sequence 1 transition contract** on an opt-in, per-player test flag. Without the flag, normal Seq2-to-Seq1 fails closed and spends NO marks or materials. The flag can ONLY be set using an OP command via vanilla function execution; never via public Tarot aliases, triggers or selected Origins.

## How to test

First back up a disposable Fabric 1.18.2 world with the owner's exact installed modpack. Do not mix both Arcane pack variants or old V2/V3, and do not use real player progress.

1. Progress normally to Sequence 2 with both fixed pathways, at least five acting marks and valid slots.
2. In chat as an OP test character, run **/function tarot_arcane:admin/enable_seq1_dev**. This sets per-player a_rtest=1 ONLY if initialized, unpaused and Seq2 slot mode.
3. At a proper lectern above crying obsidian, grounded and out of combat, bring **1 Nether Star plus 8 Ender Pearls**. Use **/tarot ascend** or the vanilla trigger fallback.
4. If all preconditions and offerings pass, deduct the precise marks/items, set sequence=1, mode=resonance (2), max slots=0, clear all eight slots, revoke individual slot powers and grant **all ten Seq9–0 Resonance powers** of the fixed pair and the **partner's immutable identity drawback**. Primary Origin and its innate drawback/wings remain.
5. Test /tarot status and /tarot slots; only Resonance should be available. Check all ten powers, multiplayer team safety, keybind conflicts, relog, respawn and restart.
6. OP-only **/function tarot_arcane:admin/rollback_player** pauses and revokes temporary sources; **/function tarot_arcane:admin/resume_player** resumes and restores. These do NOT reverse a completed Sequence 1 transition! Restore the backed-up world to undo that progression. Before transition, an OP can run **/function tarot_arcane:admin/disable_seq1_dev** to revoke permission.

## Separate source ownership

- tarot_arcane:slot_grants — individual kit slots in modes 0/1. Not regranted in mode 2.
- tarot_arcane:resonance_seq1_test — ten Resonance powers after OP opt-in and actual Seq2 ascension.
- tarot_arcane:resonance_partner_identity_test — one secondary permanent drawback, based on the fixed pair. Primary drawback remains on the native Origin. Fool Spiritual Expenditure is a special native identity; Wheel Debt of Fate is now also pinned.

These source names and admin commands never appear in player-clickable UI, and only operator command privilege accesses the admin functions.

## Remaining acceptance and caveats

- Current truthful source: **370/434 compiled = 73 full + 297 partial; 64 individual blocked; 110/110 Resonance source-compiled.** The full ten-power grant is a development **prototype**, not all original mechanics faithfully implemented.
- Default vanilla team allowlist: tarot_red, tarot_blue, tarot_green, tarot_gold; OP assigns members. Unlisted/teamless people remain neutral for the new PvP functions.
- Cross-world and relog source reconciliation, exact damage/cooldowns, safe lethal saves, Sin substitutes, performance and packet compatibility need real game tests. Temporary status effects from former individual powers may remain after grant revocation; don't force-clear unrelated potion effects.
- User confirms **Fabric Permissions API installed**, as well as LuckPerms, Pehkui, ReMorphed 4.0, SkinShifter, Extra Keybinds and the existing modpack. ReMorphed version-specific permission-node support requires actual jar/config/runtime testing. No unverified mod commands are invoked by the build.
- Record PASS / FAIL / NOT RUN plus logs for test-world reload, both dev variants, teammate/enemy damage, nonOP security, respawn/death/rollback and original V2/V3 regression. A failure prevents any production release.
- The final Rev3 design requires this mode to work normally at Seq1, WITHOUT an admin test flag. The gate is strictly an incomplete-development safeguard, to be removed only after gameplay acceptance.

Authoritative sources: docs/HandbookRev3.txt Part C.2/C.6 (mode transition) and docs/HandbookRev2.txt (per-power behavior). Owner-authorized substitutions are disclosed individually in the manifest.
