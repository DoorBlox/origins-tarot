# Arcane V2 Rev3 — confirmed installed-mod inventory

**Updated 2026-11-22 from actual uploaded 1.18.2 Fabric startup log and both installed .json5 configs** (rather than older PDF estimates). Runtime logs confirm the exact loaded versions below, not gameplay/API acceptance. The log is a no-Tarot-datapack baseline with an OOM and offline-auth warning; see [verified baseline](ARCANE_VERIFIED_SERVER_BASELINE_2026-11-22.md). No new dependencies are assumed.

| Existing mod | Version in real Fabric startup log | Placement | Supported potential / boundary |
| --- | --- | --- | --- |
| Origins | 1.4.1 | Client + server | Primary Origins powers, source-scoped grants, actions and conditions |
| Fabric API | 0.77.0+1.18.2 | Client + server | Existing mod dependencies, not standalone script handling |
| Pehkui | 3.8.3+1.14.4-1.21 | Client + server | Scaling and hitbox changes where documented commands exist |
| Origins Extra Keybinds | 0.5.0+1.17-1.19.4 | Client | More ability controls; verify actual key IDs and default bindings |
| Command Aliases | 1.0.1+mc1.18.2-build.66 | Server | Existing player-facing /tarot aliases; vanilla /trigger remains safe fallback |
| ReMorphed | **4.2** | Client + server | Older kill-to-unlock; modern granular permission nodes were only added in v7.1; command registration alone is not a tested morph/reset API |
| Walkers | 5.8.1 | Client + server | ReMorphed dependency |
| CraftedCore | 5.8.1 | Client + server | ReMorphed dependency |
| SkinShifter | **1.3** | Client + server | Self commands configured OP level 0, base level 2, visual name/cape enabled; LuckPerms nodes added only in v3.0, NOT v1.3 |
| LambDynamicLights | **Not listed by the dedicated server**; client-only is expected | Client | Cosmetic visual lighting; not a persistent in-world server light source |
| LuckPerms | 5.3.86; initialized H2 successfully | Permission layer | Manage narrowly scoped permission nodes; **does not establish multiplayer ally/enemy teams** |
| **Fabric Permissions API** | **0.3.1 (fabric-permissions-api-v0)** | Fabric server | Provides permission-node API compatibility where individual mods actually support it; inspect ReMorphed 4.0 config before enabling its nodes |

**Not installed / not selected:** Immersive Portals (owner declined), KubeJS (unavailable), any custom Java/Fabric companion mod (owner declined). Apugli, FabricTailor and Identity are not assumed installed; SkinShifter and ReMorphed are the chosen alternatives.

## Hard integration rules

1. Mainline remains an Origins 1.4.1 datapack plus **verified** existing-mod configuration. Version-specific commands must be sourced and tested, never guessed or inserted unverified.
2. **LuckPerms 5.3.86 + Fabric Permissions API 0.3.1 are loaded**. Granular ReMorphed permission support starts with v7.1, and SkinShifter permission-system support starts with v3.0; the server has 4.2 and 1.3 respectively. Permissions cannot replace vanilla OP gates. Never grant arbitrary operator access or wildcard permissions or expose Arcane admin functions to normal players. Preserve player-scoped /trigger and clickable /trigger a_help fallback.
3. Pehkui, ReMorphed and SkinShifter can be considered for scale/transform/disguise abilities after inspecting their exact commands on the owner's build. Any integration must be opt-in, permission-checked, reversible, and run in a disposable test world first.
4. Extra Keybinds controls do not replace server authority, cooldowns, teammate filtering or anti-abuse checks. **Vanilla scoreboard teams** are the sole chosen PvP relationship, see [docs/ARCANE_TEAM_POLICY.md](ARCANE_TEAM_POLICY.md); default red/blue/green/gold teams, unassigned neutral. LuckPerms groups do NOT imply combat teams. LambDynamicLights cannot provide persistent in-world light levels.
5. Test real non-OP command permissions, source-scoped grants, relog/respawn, multiplayer ally/enemy targeting, graphics compatibility, and data persistence with the actual assembled modpack before marking gameplay accepted.

## Verified documentation interfaces, not yet integrated in gameplay

These interfaces are from public project documentation; the **owner's exact installed 1.18.2 jars and combined config are not yet verified**. Do not assume current documentation applies unchanged to the old game release.

- **SkinShifter:** project docs show `/skinshifter set @s <username-or-uuid>`. The `<username-or-uuid>` is a literal argument, **not** a dynamic expression containing a random online player's name. Fool's random-online-person Full Faceless Disguise and Borrowed Face cannot be represented by fabricating a dynamic /skinshifter parameter. Source: https://modrinth.com/mod/skinshifter
- **Pehkui:** project docs show `/scale set <scale_type> <value> [target]` and `/scale reset <scale_type> [target]`. A temporary Tarot scale change must also revert safely on expiry, death, dimension change, disconnect, pause, and source revoke; do not ship an activation-only /scale command that leaves players permanently resized. Source: https://modrinth.com/mod/pehkui
- **Origins Extra Keybinds 0.5.0:** real server log identifies module `extrakeybinds` v0.5.0, not 0.2.0. Verify exact 0.5 key IDs and client-side ReMorphed key collision in game. Source: https://modrinth.com/project/origins-extra-keybinds
- **ReMorphed 4.2:** uploaded config explicitly lacks `usePermissions`; the upstream changelog records **permission-system support introduced in 7.1.0**. Modern `/lp ... remorphed.morph` and `usePermissions=true` instructions do not apply to this old installation. Existing `killToUnlock=1`, `killToUnlockPlayers=2`, `creativeUnlockAll=true`, `autoTransform=false`; command tree includes `/remorphed addSkin`, but no successful integration test or reset lifecycle yet. Source: https://github.com/ToCraft/Remorphed/blob/main/CHANGELOG.md
- **SkinShifter 1.3:** real config has `changeName=true`, `changeCape=true`, `selfCommandOPLevel=0`, `baseCommandOPLevel=2`. Modern SkinShifter docs state LuckPerms support was added only as of **3.0**, so don't invent 1.3 nodes. Server registered `/skinshifter set` with player-name/UUID argument branches; exact activation/reset and persistent cleanup still NOT RUN. Source: https://github.com/ToCraft/SkinShifter/blob/main/README.md
- **Command Aliases + /trigger:** aliases remain cosmetic convenience. The existing /trigger bridge is the security boundary for non-OP players; LuckPerms cannot be used as a substitute for validating actual server-side command execution.

**Owner evidence RECEIVED:** exact mod list, Fabric startup log, ReMorphed 4.2 and SkinShifter 1.3 configs have been inspected. No need to request them again. Remaining *operator-only* evidence: configured JVM -Xmx/RAM allocation; whether offline-mode is intentional with an authenticated proxy; exact mod command success and safe reset observed in a backed-up test world. No new mod installations or live server changes were made.

## Runtime baseline and release gates (2026-11-22)

- Fresh-world **no-datapack startup reached Done (68.464s)**, with 76 Origins powers and 11 default origins; this does not prove Tarot load or abilities.
- **BLOCKER: java.lang.OutOfMemoryError during terralith:spire world generation**. Diagnose actual Java heap and hosting RAM before Arcane load testing. Experimental C2ME v0.2.0+alpha.7.40 may complicate memory triage; no causal claim yet.
- **BLOCKER for directly accessible public server: OFFLINE/INSECURE MODE**. Require online-mode authentication or a correctly isolated authenticated proxy backend before production multiplayer.
- Version-specific ReMorphed 4.2 / SkinShifter 1.3 integration rules above take precedence over modern docs. See [real startup evidence](ARCANE_VERIFIED_SERVER_BASELINE_2026-11-22.md) and run the read-only [audit utility](../scripts/arcane_server_evidence_audit.py) against private future logs.
- Do not confuse command parser ambiguity warnings with fatal errors, mod API proof, or successful gameplay tests. No damage/friendly/skin/cooldown/relog acceptance performed.

## Current source checkpoint (2026-11-22)

- [PR #37](https://github.com/DoorBlox/origins-tarot/pull/37) implements explicit vanilla team safe PvP and allied effects, excluding unassigned players. See [team policy](ARCANE_TEAM_POLICY.md). This feature is source-CI verified, not game-runtime accepted.
- [PR #38](https://github.com/DoorBlox/origins-tarot/pull/38) completed the **110/110 source-mapped Resonance definitions** with multiple disclosed safe partial substitutions and added persistent-latch death saves.
- [PR #39](https://github.com/DoorBlox/origins-tarot/pull/39) adds **OP-opt-in test-only Seq2→1** with all ten paired Resonance source powers and second identity drawback, while normal non-OP progression remains gated. See [test instructions](ARCANE_SEQ1_OPERATOR_TEST.md).
- [PR #40](https://github.com/DoorBlox/origins-tarot/pull/40) adds 32 more individual abilities through bounded source-backed substitutions, including 10 individual capstone previews.
- **434 specified; 402 compiled = 73 full + 329 partial; 32 blocked, ALL individual.** Resonance **110/110** compiled but many partial. The 22 pathways, 11 pairs and three dev-only ZIPs do not constitute a production-ready pack.
- **No Minecraft startup/reload acceptance** and **no live SMP deployment**. Do not represent installed dependencies as proof that mod APIs, skins, size reset, command permission nodes or keybind IDs work under the exact old versions.

Next: fix/diagnose **server heap OOM and offline authentication**, then load one dev-only Arcane ZIP on a separate backed-up test world and capture new game logs. Continue the 32 remaining individual source blocks and 329 partial fidelity gaps while the server issues are addressed. Do NOT ask for previously supplied mod list or both configs again.
