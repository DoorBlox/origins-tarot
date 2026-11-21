# Arcane V2 Rev3 — current source blockers and fidelity debt

**2026-11-22 source checkpoint for [PR #48](https://github.com/DoorBlox/origins-tarot/pull/48)** (do not call merged until four exact-head CI checks pass). The authoritative Rev2 catalog remains **434 abilities** (324 individual and 110 Resonance). Expected manifest after PR48: **433 source-compiled = 73 source-full + 360 source-PARTIAL, one blocked**, all **110/110 Resonance** source-defined. These are generated source definitions, **NOT gameplay-verified abilities**.

## One still-uncompiled individual requirement

| Pathway | Seq | Ability | What must be engineered |
| --- | ---: | --- | --- |
| Hierophant | 1 | **Dietary Expansion** | Exact **fish-only** exception to the Hierophant’s permanently pinned Seq9 **Sacred Dietary Vow**. The original ban uses item tag `tarot:meat` (including fish), and this needs a reversible, source-owned exception only while the Seq1 improvement is active, still banning nonfish meat without creating a removable identity loophole |

Do not add a dummy `origins:simple` merely to force 434. If the exact source-owned carveout cannot be achieved, implement only a genuine meaningful subset with explicit PARTIAL disclosure or keep this entry blocked.

## Hanged Man Sin — implemented as a partial source-backed subsystem

[PR #48](https://github.com/DoorBlox/origins-tarot/pull/48) adds six catalog-matched Hanged Man powers and `arcane_rev3/sin_engine.py`, all marked **PARTIAL**:
- Seq9 **Sin-Bearing:** persistent scoreboard samples changes in the actual 1.18.2 damage-taken statistic, stores a rounded quarter into a **16HP-equivalent** capped resource, dissipates after **200 online ticks** without damage, triggers low-health bounded hostile/elected-opponent status pulse when below **8HP**, and has an owner-specific HUD. No fabricated exact damage-source callback or arbitrary dynamic damage.
- Seq5 **Burden Bearer:** native **−10% incoming damage** while Sin resource positive, and **60-tick Regeneration** when it dissipates.
- Seq3 **Trinity:** three received hit events within **100 ticks** give Resistance II for **60 ticks** and Instant Health I (2 hearts); cannot guarantee three *distinct sources*.
- Seq1 **Sin Overflow:** 10-block hostile and explicit enemy-team debuffs, stronger Weakness/Slowness than base; can't inflict exact stored-Sin dynamic HP damage or heal precisely 75%.
- Seq1 **Depraved Dependent:** 20% on kill (2400t cooldown) harmless smoke cloud lasting **300 ticks**, not fake attacking AI, max one concurrent rather than two; no persistent ownership.
- Seq0 **Weight of Sin Made Manifest:** primary-key **1200t** active form, **14400t** cooldown, native −75% incoming damage and −15% movement, 80t bounded weakening nova and safe expiry; **not** exact 40-heart dynamic explosion, 100% conversion, kill minions or 50% stored-Sin proportional healing.

The engine resets on source revocation, pause, death, native Origin reselection, and tracks only online ticks. All negative player effects use explicit vanilla scoreboard teams, never unassigned/unlisted or friendly targets; world terrain is not edited. Some scoreboard sampling and player health readout mechanics still need **real in-game acceptance** and should not be called exact until tested. Regression tests enforce both generated ZIP variants, attack/decay thresholds, team-safe selectors, cleanup and exact source manifests.

## 360 partial mechanics still need fidelity improvements

- **Missing event APIs:** block-break adjacent blocks respecting protections, actual enchanting lapis discounts, cross-lectern storage, temporary light zones, exact AI aggro, genuine controlled minions and resurrection, potion consumption/healing scalars, exact chat editing, true invulnerability/teleport-cancellation, and event-perfect damage-source signatures cannot be promised under the 1.18.2 datapack-only constraint.
- **UI and mods:** SkinShifter **1.3**, ReMorphed **4.2**, Pehkui **3.8.3**, Origins Extra Keybinds **0.5.0**, LuckPerms **5.3.86** and Fabric Permissions API **0.3.1** are installed. Old ReMorphed 4.2 does **not** have modern v7.1 granular permission nodes; SkinShifter 1.3 predates modern v3.0 LuckPerms support. Exact command activation + inverse/reset remains unverified. Do not grant wildcard admin permissions.
- **Multiplayer:** fixed vanilla `tarot_red`, `tarot_blue`, `tarot_green`, `tarot_gold` combat teams; opposing teams only if both allowlisted; same-team allies; neutral/no-team players must not be hit by a custom negative player command. Never infer enemies from LuckPerms groups.
- **Resonance:** 110/110 source definitions represented, many partial. Default Seq1 progression remains fail-closed; OP-enabled genuine Seq2→1 ritual remains **test-world only** pending actual game and PvP acceptance. All normal slot/progression rules through Seq2 preserved.
- **Environment:** Moon Seq9 help/status/slots worked in actual server test after PR44, though two armor JSON decoder problems were observed; PR46 corrected those in source but user expressly **defers that minor Minecraft retest** while source development continues. No direct hosted player/world modifications. Existing intentional offline mode and early one-time Terralith worldgen OOM are accepted for development, not risk-free.

## Standing owner decisions and next engineering work

Owner authorizes safe GitHub changes and merges **only with four green exact-head CI workflows** and focused diff review. They want **substantial source development first** before consolidated game tests, and documented bounded substitutions without introducing KubeJS/new Java mods. Update `CHATGPT_HANDOFF.md`, this register and GitHub issue #20 at every major merge.

**Next:** complete Hierophant’s safe reversible Dietary Expansion, then prioritize source-faithful upgrades of high-value PARTIAL powers, refine and test Sin/Resonance interactions and reserved team PvP safeguards, and finally run ONE consolidated backed-up 1.18.2 server DEV pack acceptance. **No production release or unvalidated gameplay-complete claim.**
