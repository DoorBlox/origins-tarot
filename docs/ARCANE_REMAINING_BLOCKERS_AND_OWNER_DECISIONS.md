# Arcane V2 Rev3 — outstanding gameplay fidelity, mod dependencies and owner decisions

**Checkpoint:** after source PRs #32, #33 and manual preview #35 on 2026-11-22. This is a priority/action register, not an assertion that unsupported content is impossible to implement. The 434-entry source catalog is authoritative, and the generated manifest is the source of exact statuses.

## Required end state (not negotiable without asking owner)

- Rev3 **Sequence 1** must activate the corresponding fixed paired Resonance's **all ten kits, Seq9 through Seq0** together, in place of individual slot abilities, while keeping both relevant permanent identity drawbacks. The current Sequence1 lock is a **temporary incomplete-development safety gate**, not the final design.
- Offensive effects affect tagged hostiles **and enemy players**, excluding teammates. Positive ally effects must not heal enemies. No blanket OP rights for players. No destruction of player world or inventories to fake an ability.
- Minecraft Java 1.18.2 / Fabric / Origins 1.4.1; owner-installed Pehkui, Extra Keybinds, Command Aliases, ReMorphed, Woodwalkers, CraftedCore, SkinShifter, LambDynamicLights and LuckPerms. No Immersive Portals, no KubeJS and no custom Java/Fabric companion mod unless the owner explicitly changes their mind.
- Source CI passing is not equivalent to testing interaction, targeting, performance, persistence or permissions on the **real Minecraft server**.

## Twelve uncompiled Resonance entries (remaining after #33)

| Pair | Seq / ability | Main missing technical contract |
| --- | --- | --- |
| Paper Martyr | 5 / Gathering of Martyrs | Two 200t ally figurines, actual Sin ownership, hostile-and-enemy-player AI, scoped detonation |
| Paper Martyr | 4 / Burdened Trickster | Genuine Sin cap increase and real decoy Sin storage/detonation |
| Paper Martyr | 2 / Sacrificial Gathering | Upgraded minion/detonation chain and synced Sin budget |
| Paper Martyr | 1 / Martyr's Substitute | Once-per-7200t lethal cancel, bounded safe relocation and persisted Sin shadow |
| Marked Verdict | 1 / Swift Judgment | Once-per-9600t lethal save with attacker-targeted frozen effect, no collateral |
| Crumbling Reaper | 5 / Gate Collapse | Safe, permission-aware temporary Nether portal with bounded 3x3 terrain edits |
| Crumbling Reaper | 4 / Falling Harvest | Fall-height and 200t kill-window resource, healing and guarded enemy-only explosion |
| Impossible Fist | 4 / Doorstep Punch | Timed post-teleport +15% melee event association |
| Impossible Fist | 2 / Giant's Shortcut | Exact post-phase-exit enemy health-scaled AoE, PvP team safety |
| Benevolent Crown | 3 / Shared Domain | Genuine Emperor's Corrupt Ground region state plus team-specific regeneration |
| Binding Contract | 2 / Contract Enforcement | Explicit player accept/refuse contract state, permission-safe inventory effects |
| Loaded Dice | 1 / Loaded Answer | Typed yes/no fate event predicates, cooldown, deterministic consequence tracking |

These entries are **not automatically solved by installing LuckPerms, Pehkui or a morphing mod**. Many are possible only with more extensive vanilla scoreboard/advancement logic plus in-game verification, explicit acceptance of weaker approximations, or a scripting/event-hook capability that the current architecture forbids. Do **not** register empty dummy powers to make the metric 110/110.

## Other must-fix areas before release

- **85 individual catalog entries still blocked** after #33, including Full Faceless Disguise, Borrowed Face, Recorded Step, Waypoint, Sin-Bearing, Debt of Fate, and various world, AI and client-rendering mechanics.
- **264 explicitly partial** definitions have real JSON but omitted details; their damage, cooldown, ally/enemy targeting, trigger specificity and resource dependencies must be tested and refined. A count of compiled entries is not a count of handbook-complete abilities.
- **Fair PvP:** no general arbitrary-team comparison available in plain current power JSON; fixed team selectors or a verified team-source contract may work, but need to know whether the SMP uses vanilla `/team` names or another team system. Until then, hostile-mob-only offensive fallback must not hit allies.
- **Mod integration:** documented SkinShifter `/skinshifter set @s <username-or-uuid>` does not accept a datapack runtime expression for random online username. Pehkui scale setters need expiry/relog/death/pause reset. Exact installed ReMorphed 4.0 permission semantics with LuckPerms must be checked. Current ReMorphed permission docs mention a separate Fabric Permissions API and `usePermissions=true`; **not yet verified for 4.0**.
- **Version discipline:** some modern Origins power types listed in latest docs (e.g. modify_insomnia_ticks, modify_healing) are not listed for Origins 1.4.1. Do not silently use them as if supported. See https://origins.readthedocs.io/en/1.4.1/types/power_types/.
- **Preview**: The separate operator-only `Arcane_Rev3_Resonance_Manual_Preview_TEST_ONLY_1.18.2.zip` is for isolated testing. It overlays current slots and is not the Seq1 transition. Always manually revoke preview source before uninstalling; see `docs/ARCANE_RESONANCE_MANUAL_PREVIEW.md`.

## Owner involvement: only when materially necessary

The engineer can keep implementing source batches **without asking again for general authorization**. Before implementing exact PvP filtering or certain advanced mods, the owner can help by supplying:

1. The actual **mod jar list and Fabric startup log**, especially ReMorphed 4.0, SkinShifter, LuckPerms and whether Fabric Permissions API is present. This can wait until command integration or runtime acceptance.
2. **How players are assigned allies/enemies**: vanilla Minecraft scoreboard team names/configuration versus another plugin/mod concept. Do not invent or silently change teams.
3. If a required mechanic cannot be reproduced under the current installed mods, choose explicitly between **a documented weaker datapack workaround** or **authorizing an additional existing 1.18.2 event-capable mod**. No scripting dependency or custom Java may be added without this decision.

**Immediate source tasks:** tackle Sin-Bearing/Death-save resource state and bounded timers, implement real slot-to-Resonance transition with rollback tests in an isolated feature flag, close individual register gaps with concrete mechanics, verify team-scope operations against vanilla commands, and get in-game acceptance logs from the owner before calling any build ready.
