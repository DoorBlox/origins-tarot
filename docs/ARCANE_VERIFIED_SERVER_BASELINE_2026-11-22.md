# Arcane Rev3 — verified Fabric 1.18.2 server baseline (22 November 2026)

**Evidence:** the owner's fresh-world startup log, screenshot of the server mod filenames, and the actual remorphed.json5 and skinshifter.json5. This is before installing ANY Tarot datapack. Never commit raw private logs, full server configurations, ports, usernames, world data or player identities to this repository.

**Verdict: server started, but the baseline is NOT clean.** Minecraft reported "Done (68.464s)!" after Terralith spire world generation emitted "java.lang.OutOfMemoryError: Java heap space". The server also warned it is in offline/unauthenticated mode. Neither warning is a Tarot datapack failure because no Tarot datapack was loaded.

## Actual loaded versions (log is more authoritative than earlier PDF estimates)

| Mod / runtime | Verified server version |
| --- | --- |
| Minecraft / Fabric Loader / Java | 1.18.2 / 0.20.1 / 17 |
| Origins / bundled Apoli | 1.4.1 / 2.3.3 |
| Fabric API | 0.77.0+1.18.2 |
| Fabric Permissions API (ID fabric-permissions-api-v0) | 0.3.1 |
| LuckPerms | 5.3.86; initialized successfully with H2 storage |
| ReMorphed | 4.2 |
| SkinShifter | 1.3 |
| Pehkui | 3.8.3+1.14.4-1.21 |
| Origins Extra Keybinds | 0.5.0+1.17-1.19.4 |
| Command Aliases | 1.0.1+mc1.18.2-build.66 |
| CraftedCore / Walkers | 5.8.1 / 5.8.1 |
| C2ME | 0.2.0+alpha.7.40 (experimental) |
| ServerCore | 1.2.9-1.18.2 |
| ViaVersion / ViaBackwards / ViaRewind | 5.12.3-SNAPSHOT / 5.12.3-SNAPSHOT / 4.2.0 |
| Tectonic / bundled Terralith | 2.3.5a / 2.2.6 |

The log reports 138 loaded mod IDs including bundled dependencies, NOT 138 independent JARs. Before Tarot was added the Origins data registry had 76 powers and 11 origins. Origins/Apoli initialized, Command Aliases registered commands and LuckPerms initialized. There is still NO proof a generated Arcane ZIP will load or run correctly.

## Config details and version-specific integration boundaries

**ReMorphed 4.2** (uploaded remorphed.json5):
- creativeUnlockAll=true, killToUnlock=1, killToUnlockPlayers=2; autoTransform=false, lockTransform=false, unlockFriendlyNormal=false, loadMenuAsynchronous=true.
- NO usePermissions property. Upstream ReMorphed CHANGELOG says granular permission-system integration was **added in 7.1.0**, long after this server's v4.2. Do not apply modern ReMorphed 7.1+ LuckPerms nodes or blindly insert usePermissions=true into a legacy configuration. https://github.com/ToCraft/Remorphed/blob/main/CHANGELOG.md
- Startup registered ReMorphed addSkin/removeSkin and Walkers switchShape command branches, but their Brigadier ambiguity WARNings are NOT successful invocation tests. No verified temporary morph cleanup/reset is yet available for Arcane.

**SkinShifter 1.3** (uploaded skinshifter.json5):
- changeCape=true, changeName=true, baseCommandOPLevel=2, selfCommandOPLevel=0.
- This appears to allow self-service visual skins/names for non-OP players, but does not grant unrelated server OP authority. On an unauthenticated or public SMP the name rendering can create confusion, so preserve deliberate control over self-disguise.
- Official SkinShifter README states permission-system/LuckPerms integration arrived only **as of v3.0**, substantially later than installed v1.3. No modern SkinShifter permission nodes should be assumed. https://github.com/ToCraft/SkinShifter/blob/main/README.md
- The server command tree registers SkinShifter set player name/UUID arguments. It does NOT verify a 1.3-safe inverse/reset, random-online-player selection, name protection, or reload/death cleanup. Never wire a temporary Tarot skin shift before both activation and inverse are verified.

**Pehkui:** the log registered scale command branches, including reset. These are registration observations only, not proof that scale effects restore on expiry, death, relog, pause and source revoke. Extra Keybinds is 0.5.0, not the previously assumed 0.2.0; verify key IDs and collision with ReMorphed before tertiary binding.

**Fabric Permissions API 0.3.1 and LuckPerms 5.3.86**: both installed/loaded, but this does NOT retroactively add newer permission-node APIs to ReMorphed 4.2 or SkinShifter 1.3. Multiplayer allegiance still uses explicit vanilla scoreboard teams as described in ARCANE_TEAM_POLICY.md.

## Prioritized operational triage

1. **Resolve heap OOM first**: inspect hosting RAM limit and actual JVM -Xmx/-Xms, leaving sufficient headroom for native memory. Retry fresh-world generation after correcting allocation. If OOM persists, isolate C2ME alpha and world-generation mods one at a time on a backed-up separate test seed. The error points to Terralith spire loading, not necessarily a Terralith code defect. Use Spark once the world starts cleanly.
2. **Secure authentication**: the log states Minecraft is in OFFLINE/INSECURE MODE. If directly reachable by untrusted players, set online-mode=true and restart. If behind an authenticated Velocity/Bungee proxy, ensure the backend port cannot be reached directly and forwarding is properly configured. A whitelist alone does not prevent spoofed names on an offline server.
3. **Keep SkinShifter self-command permission intentional**: selfCommandOPLevel=0 and changeName=true may be a desired game mechanic. For a secure SMP, consider stricter self-command access until the disguise test harness is verified, backing up the config first. No config changes were made automatically.
4. **Non-blocking warnings**: Debugify recommended Mod Menu but it is not a dedicated-server startup blocker. The 2.3.5a Tectonic semantic-version warning is metadata. CraftedCore Patreon fetch and Debugify update-check network failures did not stop startup. Lithium/Krypton redirect conflicts and C2ME/ModernFix overrides deserve monitoring, not blind mod removal. ViaVersion's development snapshot warns Java 17 may eventually be unsupported; do NOT upgrade to Java 21 without testing the whole 1.18.2 modpack.
5. **After clean baseline**: back up an isolated world, install EXACTLY ONE Arcane Rev3 DEV ZIP (not V2/V3 simultaneously), restart and inspect the NEW latest.log for unknown Origins powers/JSON parse failures. Run /datapack list and /trigger a_help as a true non-OP, inspect 22 Tarot selections and source grants, then the default vanilla team friend/enemy/neutral cases. Only after those pass, test the OP-gated real Sequence 2 -> 1 transition from ARCANE_SEQ1_OPERATOR_TEST.md. Record PASS / FAIL / NOT RUN with screenshots, reload, death, cooldown, rollback and performance; source CI alone does not verify gameplay.

## Read-only command-line evidence audit

Run locally against your PRIVATE server files, without uploading log/config contents into GitHub:

    python scripts/arcane_server_evidence_audit.py --log latest.log --remorphed config/remorphed.json5 --skinshifter config/skinshifter.json5
    python scripts/arcane_server_evidence_audit.py --log latest.log --remorphed config/remorphed.json5 --skinshifter config/skinshifter.json5 --json

The script reads, classifies and reports; it does not mutate world state, server configurations or permissions, or issue any Minecraft command. The conservative ready_for_arcane_load_test flag is NOT an approval of gameplay. Six synthetic tests cover ordinary and markdown logs, warnings, mod parsing and config parsing.

**Source inventory is unchanged by this evidence audit:** 434 specified; 402 compiled (73 full, 329 partial); 32 individual blocked; 110/110 Resonance source-compiled. Actual in-game acceptance remains NOT RUN, and no production SMP deployment was performed.
