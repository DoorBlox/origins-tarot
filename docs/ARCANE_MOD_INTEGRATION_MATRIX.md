# Arcane V2 Rev3 — confirmed installed-mod inventory

**Recorded 2026-11-22** from the owner's uploaded tarotmc(1).pdf, pages 22–25, and their follow-up confirming LuckPerms. This inventory is **owner-reported**; the combined Fabric instance and exact jar versions are not independently verified. Do not silently add dependencies.

| Existing mod | Version recorded in PDF | Placement | Supported potential (requires verifying actual 1.18.2 API/commands) |
| --- | --- | --- | --- |
| Origins | 1.4.1 | Client + server | Primary Origins powers, source-scoped grants, actions and conditions |
| Fabric API | 0.76.0+1.18.2 | Client + server | Existing mod dependencies, not standalone script handling |
| Pehkui | 3.7.11 | Client + server | Scaling and hitbox changes where documented commands exist |
| Origins Extra Keybinds | 0.2.0 | Client | More ability controls; verify actual key IDs and default bindings |
| Command Aliases | 1.0.1 | Server | Existing player-facing /tarot aliases; vanilla /trigger remains safe fallback |
| ReMorphed | 4.0 | Client + server | Potential mob transformations; never invent a callable command |
| Woodwalkers | 5.4 | Client + server | ReMorphed dependency |
| CraftedCore | 5.1 | Client + server | ReMorphed dependency |
| SkinShifter | 1.0 | Client + server | Potential player disguise/skins, require verified command semantics |
| LambDynamicLights | Version not specified | Client | Cosmetic visual lighting only, not server-authoritative light mechanics |
| LuckPerms | Version not specified; now confirmed installed | Permission layer | Grant narrowly scoped permission nodes for existing mod commands, not automatic custom command registration |

**Not installed / not selected:** Immersive Portals (owner declined), KubeJS (unavailable), any custom Java/Fabric companion mod (owner declined). Apugli, FabricTailor and Identity are not assumed installed; SkinShifter and ReMorphed are the chosen alternatives.

## Hard integration rules

1. Mainline remains an Origins 1.4.1 datapack plus **verified** existing-mod configuration. Version-specific commands must be sourced and tested, never guessed or inserted unverified.
2. LuckPerms may narrow permissions, but never grant arbitrary operator access, wildcard permissions, or expose internal administrative Arcane functions to normal players. Preserve player-scoped /trigger controls and clickable /trigger a_help fallback.
3. Pehkui, ReMorphed and SkinShifter can be considered for scale/transform/disguise abilities after inspecting their exact commands on the owner's build. Any integration must be opt-in, permission-checked, reversible, and run in a disposable test world first.
4. Extra Keybinds controls do not replace server authority, cooldowns, teammate filtering or anti-abuse checks. LambDynamicLights cannot provide persistent in-world light levels.
5. Test real non-OP command permissions, source-scoped grants, relog/respawn, multiplayer ally/enemy targeting, graphics compatibility, and data persistence with the actual assembled modpack before marking gameplay accepted.

## Current source checkpoint

PR #30 (https://github.com/DoorBlox/origins-tarot/pull/30) merged at commit a45377cc2a1d33f2f514221c63db3624ef977317 after four exact-head green PR workflows at a41f1ac6301fe3876a21db12803a310d13377d80.

- 19 new individual and 12 Resonance partial ability definitions, with regression tests and real source-traced effects.
- **434 specified; 272 compiled (73 full, 199 partial); 162 blocked.**
- **63/110 Resonance definitions compiled, zero equipped.** Sequence 1 remains fail-closed without consuming offerings.
- No live server acceptance, no SMP deployment. The 199 partial definitions must not be represented as handbook-complete.

Next: verify documented commands/configs for installed mods, resolve team-aware ability conditions and permanent drawbacks, expand and improve actual kits without fake placeholders, and perform Minecraft 1.18.2 gameplay acceptance.
