# Arcane V2 Rev3 — developer build status

**TEST-WORLD ONLY. Do not merge to or install on the live SMP.**

Authoritative specifications: `docs/HandbookRev3.txt` governs progression and slots; `docs/HandbookRev2.txt` governs the 434 individual/Resonance abilities and PvP/team targeting.

## Implemented in code

- 22 pathway Origins and 18 inherited Elytra gliders; 11 paired Resonance IDs are reserved, not activated.
- Pure datapack/scoreboard runtime: Sequence 9 through 2, 22 distinct acting quest tracks, altar requirements, combat lock, fixed second pathway at Sequence 4, 6/7/8 editable slots, grant/revoke and re-login reconciliation. No KubeJS or custom Fabric mod.
- Non-OP `/tarot`, `/tarot status`, `/tarot slots`, `/tarot ascend`, `/tarot slot N tarot:card S`, `/tarot slot N clear`, `/tarot slot auto`, `/tarot slot swap N M`, and `/tarot reset` via player-scoped CLIENT `/trigger` operations. Command Aliases schema uses permission 0.
- The full 434-entry source manifest identifies every ability, its flag, exact description, compiled power (when present), and remaining work. **84 powers compiled (including partial implementations), 350 still blocked.** No fake `origins:simple` abilities are emitted.
- Fool's identity drawback (+25% exhaustion sprinting/Elytra) remains on its Origin independently of slots.

## Not implemented / not verified

**Sequence 1 Resonance intentionally remains locked** because all 110 Resonance abilities aren't implemented; no ritual ingredients are consumed for this blocked transition. Most advanced Rev2 [S] mechanics (skin/name/model swapping, minion AI, some teleport and player-inventory hooks) require a scripting/mod runtime excluded by the owner. Additional Rev2 [D/S] parts remain incomplete and are labeled `partial`.

Structural CI does **not** prove compatibility in a live Minecraft 1.18.2 / Fabric / Origins 1.4.1 / Command Aliases 1.0.1 server. Gameplay, non-OP command parsing, party-team targeting, and world-reload verification are **NOT RUN**. The developer pack also does **not** migrate existing V3 `tc_*` progression scores or player save state.

## Build outputs

From the successful **Build Arcane V2 Rev3 22-Origin Dev Pack** GitHub Actions workflow, download and extract the *outer* artifact ZIP. The enclosed files are:

- `Arcane_Rev3_22_Origins_ONLY_DEV_1.18.2.zip` — 22 Tarot Origins replace normal choices.
- `Arcane_Rev3_22_Origins_ADDON_DEV_1.18.2.zip` — Tarot Origin choices supplement normal choices.
- `tarot.json` — Command Aliases 1.0.1 configuration for `config/commandaliases/`.
- `arcane_ability_manifest.json` — exact `full`, `partial`, `blocked` statuses with source traces.

Use at most one inner ZIP, only in a **new disposable test world**. Never install this dev build alongside the current V2/V3 Tarot datapacks or copy it over a world containing existing progression. A separate test world and backup are mandatory for manual acceptance.

**The user does not need to install anything now.** Keep this PR in draft until full compatibility and gameplay are verified. The owner did not authorize removing the no-KubeJS/no-custom-Java constraint, so exact completion of all 434 mechanics cannot yet be claimed.
