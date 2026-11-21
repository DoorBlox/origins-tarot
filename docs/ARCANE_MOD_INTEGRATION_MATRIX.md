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

## Verified documentation interfaces, not yet integrated in gameplay

These interfaces are from public project documentation; the **owner's exact installed 1.18.2 jars and combined config are not yet verified**. Do not assume current documentation applies unchanged to the old game release.

- **SkinShifter:** project docs show `/skinshifter set @s <username-or-uuid>`. The `<username-or-uuid>` is a literal argument, **not** a dynamic expression containing a random online player's name. Fool's random-online-person Full Faceless Disguise and Borrowed Face cannot be represented by fabricating a dynamic /skinshifter parameter. Source: https://modrinth.com/mod/skinshifter
- **Pehkui:** project docs show `/scale set <scale_type> <value> [target]` and `/scale reset <scale_type> [target]`. A temporary Tarot scale change must also revert safely on expiry, death, dimension change, disconnect, pause, and source revoke; do not ship an activation-only /scale command that leaves players permanently resized. Source: https://modrinth.com/mod/pehkui
- **Origins Extra Keybinds:** current Fabric documentation publishes keys such as `key.originsextrakeybinds.tertiary_active`, but older version **0.2.0 must be checked** for this syntax before changing live ability bindings. Source: https://modrinth.com/project/origins-extra-keybinds
- **ReMorphed / LuckPerms:** current official ReMorphed permissions documentation says Fabric servers need **Fabric Permissions API** (separate mod), then `usePermissions=true` in ReMorphed config to make LuckPerms permission nodes such as `remorphed.morph` or `remorphed.command.addShape.self` enforceable. This guidance may not match ReMorphed **4.0**; inspect the installed jar/config and verify the exact version-specific permission support before recommending an installation or changing permissions. Do not grant broad `remorphed.*`, `minecraft.selector.*` or OP-level access to normal players. Source: https://tocraft.dev/docs/remorphed/Permissions/
- **Command Aliases + /trigger:** aliases remain cosmetic convenience. The existing /trigger bridge is the security boundary for non-OP players; LuckPerms cannot be used as a substitute for validating actual server-side command execution.

**Owner input only if needed later:** upload or paste the Fabric startup/mod list and relevant ReMorphed/SkinShifter configs if exact integrations fail. A test character using the installed mods should record real command syntax, permission denials and reset behavior. No additional mods are being installed automatically.

## Current source checkpoint

- **PR #32** merged at `3e35a0974f6160e337a76b7f9f85a07fa991ba23`: 29 source-mapped partial Resonance abilities, including all 11 Seq0 prototype capstones; four exact-head green workflows.
- **PR #33** merged at `fa2f7ad91a6f4e3cf16840cbd5c67c448390d272`: 30 individual plus six Resonance concrete partial powers; four exact-head green workflows at `c2238fbfa33b09e4db7b7462542bb6cbe8d9e404`.
- **434 specified; 337 compiled (73 full, 264 partial); 97 blocked.** Individual **239/324 compiled**, Resonance **98/110 compiled**.
- All eleven Resonance pairs are present in source, but none of their incomplete kits are player-granted. Seq1 development gate remains fail-closed **only until the required gameplay contract is ready**. The handbook's intended design always activates Resonance at Seq1.
- **No in-game acceptance** and no source-triggered SMP deployment; compiled partially accurate JSON is not a finished/verified player ability.

Next: complete/verify 12 remaining Resonance + 85 individual blocks and 264 partial-fidelity gaps, implement team-safe PvP and permanent drawbacks, and test documented mod interfaces on the actual 1.18.2 installation.
