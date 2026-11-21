# Arcane V2 Rev3 — developer build status

**TEST-WORLD ONLY. Do not merge to or install on the live SMP.**

Authoritative specifications: `docs/HandbookRev3.txt` governs progression and slots; `docs/HandbookRev2.txt` governs the 434 individual/Resonance abilities and PvP/team targeting.

## Implemented in code

- 22 pathway Origins and 18 inherited Elytra gliders; 11 paired Resonance IDs are reserved, not activated.
- Pure datapack/scoreboard runtime: Sequence 9 through 2, 22 distinct acting quest tracks, altar requirements, combat lock, fixed second pathway at Sequence 4, 6/7/8 editable slots, grant/revoke and re-login reconciliation. No KubeJS or custom Fabric mod.
- Non-OP `/tarot`, `/tarot status`, `/tarot slots`, `/tarot ascend`, `/tarot slot N tarot:card S`, `/tarot slot N clear`, `/tarot slot auto`, `/tarot slot swap N M`, and `/tarot reset` via player-scoped CLIENT `/trigger` operations. Command Aliases schema uses permission 0. Both `/tarot status` and `/tarot slots` display actual Arcana titles and Sequence numbers rather than internal numeric kit codes; the partner is revealed at Sequence 4.
- The full 434-entry source manifest identifies every ability, its flag, exact description, compiled power (when present), and remaining work. **132 powers compiled (73 fully translated, 59 explicitly partial), 302 still blocked.** No fake `origins:simple` abilities are emitted.
- Permanent primary-pathway drawbacks are innate Origin powers, **not removable Sequence-9 slot abilities**: Fool's +25% exhaustion plus 19 more compiled pathway drawbacks are attached directly to their Origins, outside the source-grant/revoke cycle.

## Rev3 identity-drawback integrity

The first version only pinned the Fool's Spiritual Expenditure permanently. This allowed players from 19 other pathways to remove the encoded Seq9 drawback when they switched slots at Sequence 4. The build now extracts the compiled penalty from each corresponding Seq9 kit and puts it into the **primary Origin's power list**. Every other Seq9 power remains in the removable slot kit. This also means administrators' `rollback_player` only revokes sequence-granted powers, not inherent identity penalties.

**Two primary pathways still lack a native identity drawback:** Lovers (Separation Anxiety) and Wheel of Fortune (Debt of Fate). These remain visible release blockers. Justice (Compassionate Restraint) now enforces −70% damage against passive mobs but cannot distinguish unprovoked enemy players (partial). Hanged Man (Weight of Sin) prevents natural regeneration above eight hearts but does not yet support the three temporary cap-unlock events (partial). Do not claim all 22 drawbacks are faithful. The 434-ability source-manifest count is unchanged, because the fix rehomes existing powers rather than inventing new abilities.

The Justice and Hanged Man penalties are now real native *partial* powers, attached to their Origins. The manifest distinguishes them from complete implementations. At present there are 20 Origins with some permanent drawback behavior (including Fool), and two without.

## Additional source-traced abilities

Batch 2 implements 13 more native or partial abilities across Empress, Emperor, Wheel of Fortune, Justice, Hanged Man, Sun, World, Tower, Star and Hermit. Examples include Mirror Veil invisibility, a six-way equally weighted Fate's Current, undead-only Solar Flare, active self-cleansing with Purify and upgraded retaliation effects.

**Only Solar Flare is classified a complete Rev2 translation** in this batch. The other twelve retain detailed per-ability `missing` descriptions in `arcane_ability_manifest.json` (for example, Rev2 does not define Fate's Current effect durations, and team-aware PvP targeting cannot yet be reproduced exactly without scripting). Structural JSON/power tests do not establish in-game compatibility.

## Higher-sequence upgrades

Ten further Rev2 abilities are compiled: Devil's Demon Form, Tower's Ruin-Proof II, Wheel of Fortune's Misfortune, Judgement's Law's Weight II, Moon's Shaman, World's Cold Precision II, Sun's Unshadowed II, Hanged Man's Dark Blade, Star's Nightwatch II, and Empress's Plague Touch.

**Dark Blade is a complete source translation in code.** The other nine are partial primarily because the source specifies a replacement or upgrade of an earlier kit, while selectable sequence slots can contain both and therefore stack the effects. Several still lack exact enemy-player targeting. Their machine-readable manifest entries state each limitation. These powers must not be described as having exact in-game fidelity without gameplay acceptance and a stacking policy.

## Not implemented / not verified

**Sequence 1 Resonance intentionally remains locked** because all 110 Resonance abilities aren't implemented; no ritual ingredients are consumed for this blocked transition. Most advanced Rev2 [S] mechanics (skin/name/model swapping, minion AI, some teleport and player-inventory hooks) require a scripting/mod runtime excluded by the owner. Additional Rev2 [D/S] parts remain incomplete and are labeled `partial`.

Structural CI does **not** prove compatibility in a live Minecraft 1.18.2 / Fabric / Origins 1.4.1 / Command Aliases 1.0.1 server. Gameplay, non-OP command parsing, party-team targeting, and world-reload verification are **NOT RUN**. The developer pack also does **not** migrate existing V3 `tc_*` progression scores or player save state.

## Minecraft 1.18.2-compatible combat lock

The developer runtime prevents ascension for 200 ticks (10 seconds) after damage received, direct melee damage dealt, or firing a bow, crossbow, or trident. It uses the 1.18.2 scoreboard criteria `minecraft.custom:minecraft.damage_taken`, `minecraft.custom:minecraft.damage_dealt` and `minecraft.used:minecraft.{bow,crossbow,trident}` with saved per-player baselines. Damage received also retains the supported `minecraft:entity_hurt_player` advancement as a backup.

The previous attacker-side `minecraft:player_hurt_entity` advancement is removed because that advancement trigger is unavailable in Minecraft 1.18.2. Projectile firing locks ascension proactively rather than waiting for an arrow to land; damage-dealt statistics alone count melee damage and are insufficient for ranged weapons. Other ranged attacks, modded combat systems and the precise scoreboard behavior must still be verified in the disposable test server.

## Admin-only persistent pause and recovery

The developer pack includes an emergency **slot-power pause** that persists across relogs, death, manual power refresh, and periodic reconciliation. It does not change the player's sequence or delete saved slot allocations. The persistent flag is a scoreboard objective named `a_paused`.

From the **server console or as an OP**, use `/execute as <player> run function tarot_arcane:admin/rollback_player` to pause one player and revoke their Arcane slot powers. Use `/execute as <player> run function tarot_arcane:admin/resume_player` to restore that player's owned powers and original Tarot Origin. `/function tarot_arcane:admin/rollback_all` and `/function tarot_arcane:admin/resume_all` perform the same operations for every online player.

None of these admin functions is exposed through player-level `/tarot` aliases. Rollback does **not** revoke innate identity drawbacks or wings inherited from the Origin, nor does it roll back the Minecraft world or existing V3. Test administrative behavior in a disposable world before depending on it.

## Build outputs

From the successful **Build Arcane V2 Rev3 22-Origin Dev Pack** GitHub Actions workflow, download and extract the *outer* artifact ZIP. The enclosed files are:

- `Arcane_Rev3_22_Origins_ONLY_DEV_1.18.2.zip` — 22 Tarot Origins replace normal choices.
- `Arcane_Rev3_22_Origins_ADDON_DEV_1.18.2.zip` — Tarot Origin choices supplement normal choices.
- `tarot.json` — Command Aliases 1.0.1 configuration for `config/commandaliases/`.
- `arcane_ability_manifest.json` — exact `full`, `partial`, `blocked` statuses with source traces.

Use at most one inner ZIP, only in a **new disposable test world**. Never install this dev build alongside the current V2/V3 Tarot datapacks or copy it over a world containing existing progression. A separate test world and backup are mandatory for manual acceptance.

**The user does not need to install anything now.** Source integration may be merged without installing this developer pack on a Minecraft server. Full compatibility and gameplay verification are still required before an actual Arcane V2 release. The owner's no-KubeJS/no-custom-Java requirement remains active.
