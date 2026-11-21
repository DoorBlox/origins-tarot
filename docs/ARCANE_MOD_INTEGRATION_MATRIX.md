# Arcane V2 Rev3 — confirmed installed-mod inventory

**Updated 2026-11-22** from the owner's uploaded tarotmc(1).pdf, pages 22–25, plus their explicit confirmations that **LuckPerms and Fabric Permissions API are both installed**. This inventory is **owner-reported**; the combined Fabric instance and exact jar versions are not independently verified. Do not silently add dependencies.

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
| LuckPerms | Version not specified; owner confirmed installed | Permission layer | Manage narrowly scoped permission nodes; **does not establish multiplayer ally/enemy teams** |
| **Fabric Permissions API** | **Version not specified; owner explicitly confirms installed** | Fabric server | Provides permission-node API compatibility where individual mods actually support it; inspect ReMorphed 4.0 config before enabling its nodes |

**Not installed / not selected:** Immersive Portals (owner declined), KubeJS (unavailable), any custom Java/Fabric companion mod (owner declined). Apugli, FabricTailor and Identity are not assumed installed; SkinShifter and ReMorphed are the chosen alternatives.

## Hard integration rules

1. Mainline remains an Origins 1.4.1 datapack plus **verified** existing-mod configuration. Version-specific commands must be sourced and tested, never guessed or inserted unverified.
2. **LuckPerms + Fabric Permissions API are installed**; that does not prove that ReMorphed 4.0 uses their nodes or that permissions can replace vanilla OP gates. Never grant arbitrary operator access or wildcard permissions or expose Arcane admin functions to normal players. Preserve player-scoped /trigger and clickable /trigger a_help fallback.
3. Pehkui, ReMorphed and SkinShifter can be considered for scale/transform/disguise abilities after inspecting their exact commands on the owner's build. Any integration must be opt-in, permission-checked, reversible, and run in a disposable test world first.
4. Extra Keybinds controls do not replace server authority, cooldowns, teammate filtering or anti-abuse checks. **Vanilla scoreboard teams** are the sole chosen PvP relationship, see [docs/ARCANE_TEAM_POLICY.md](ARCANE_TEAM_POLICY.md); default red/blue/green/gold teams, unassigned neutral. LuckPerms groups do NOT imply combat teams. LambDynamicLights cannot provide persistent in-world light levels.
5. Test real non-OP command permissions, source-scoped grants, relog/respawn, multiplayer ally/enemy targeting, graphics compatibility, and data persistence with the actual assembled modpack before marking gameplay accepted.

## Verified documentation interfaces, not yet integrated in gameplay

These interfaces are from public project documentation; the **owner's exact installed 1.18.2 jars and combined config are not yet verified**. Do not assume current documentation applies unchanged to the old game release.

- **SkinShifter:** project docs show `/skinshifter set @s <username-or-uuid>`. The `<username-or-uuid>` is a literal argument, **not** a dynamic expression containing a random online player's name. Fool's random-online-person Full Faceless Disguise and Borrowed Face cannot be represented by fabricating a dynamic /skinshifter parameter. Source: https://modrinth.com/mod/skinshifter
- **Pehkui:** project docs show `/scale set <scale_type> <value> [target]` and `/scale reset <scale_type> [target]`. A temporary Tarot scale change must also revert safely on expiry, death, dimension change, disconnect, pause, and source revoke; do not ship an activation-only /scale command that leaves players permanently resized. Source: https://modrinth.com/mod/pehkui
- **Origins Extra Keybinds:** current Fabric documentation publishes keys such as `key.originsextrakeybinds.tertiary_active`, but older version **0.2.0 must be checked** for this syntax before changing live ability bindings. Source: https://modrinth.com/project/origins-extra-keybinds
- **ReMorphed 4.0 / LuckPerms / Fabric Permissions API:** **the owner has now installed both LuckPerms and Fabric Permissions API**. Current official ReMorphed permission docs refer to enabling `usePermissions=true` and nodes such as `remorphed.morph` or `remorphed.command.addShape.self`. **Do NOT assume these exact names/settings exist in installed ReMorphed 4.0**; inspect the installed jar/config and verify 1.18.2 behavior before editing config/permissions or calling mod commands. Do not grant broad `remorphed.*`, `minecraft.selector.*` or OP-level access to normal players. Source: https://tocraft.dev/docs/remorphed/Permissions/
- **Command Aliases + /trigger:** aliases remain cosmetic convenience. The existing /trigger bridge is the security boundary for non-OP players; LuckPerms cannot be used as a substitute for validating actual server-side command execution.

**Owner input only if needed later:** upload or paste the Fabric startup/mod list and relevant ReMorphed/SkinShifter configs if exact integrations fail. A test character using the installed mods should record real command syntax, permission denials and reset behavior. No additional mods are being installed automatically.

## Current source checkpoint (2026-11-22)

- [PR #37](https://github.com/DoorBlox/origins-tarot/pull/37) implements explicit vanilla team safe PvP and allied effects, excluding unassigned players. See [team policy](ARCANE_TEAM_POLICY.md). This feature is source-CI verified, not game-runtime accepted.
- [PR #38](https://github.com/DoorBlox/origins-tarot/pull/38) completed the **110/110 source-mapped Resonance definitions** with multiple disclosed safe partial substitutions and added persistent-latch death saves.
- [PR #39](https://github.com/DoorBlox/origins-tarot/pull/39) adds **OP-opt-in test-only Seq2→1** with all ten paired Resonance source powers and second identity drawback, while normal non-OP progression remains gated. See [test instructions](ARCANE_SEQ1_OPERATOR_TEST.md).
- [PR #40](https://github.com/DoorBlox/origins-tarot/pull/40) adds 32 more individual abilities through bounded source-backed substitutions, including 10 individual capstone previews.
- **434 specified; 402 compiled = 73 full + 329 partial; 32 blocked, ALL individual.** Resonance **110/110** compiled but many partial. The 22 pathways, 11 pairs and three dev-only ZIPs do not constitute a production-ready pack.
- **No Minecraft startup/reload acceptance** and **no live SMP deployment**. Do not represent installed dependencies as proof that mod APIs, skins, size reset, command permission nodes or keybind IDs work under the exact old versions.

Next: verify exact installed mod filenames, Fabric 1.18.2 startup logs and ReMorphed 4.0/SkinShifter 1.0 config/commands in a **disposable world**; implement remaining 32 source blocks and prioritize fidelity of 329 partial mechanics. Ask owner for log/config only when actually necessary to validate interfaces, and continue other work without idle questions.
