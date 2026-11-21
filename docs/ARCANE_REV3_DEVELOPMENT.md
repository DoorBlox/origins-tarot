# Arcane V2 Rev3 — developer build status

**TEST-WORLD ONLY. Do not merge to or install on the live SMP.**

Authoritative specifications: `docs/HandbookRev3.txt` governs progression and slots; `docs/HandbookRev2.txt` governs the 434 individual/Resonance abilities and PvP/team targeting.

## Implemented in code

- 22 pathway Origins and 18 inherited Elytra gliders; 11 paired Resonance IDs are reserved, not activated.
- Pure datapack/scoreboard runtime: Sequence 9 through 2, 22 distinct acting quest tracks, altar requirements, combat lock, fixed second pathway at Sequence 4, 6/7/8 editable slots, grant/revoke and re-login reconciliation. No KubeJS or custom Fabric mod.
- Non-OP `/tarot`, `/tarot status`, `/tarot slots`, `/tarot ascend`, `/tarot slot N tarot:card S`, `/tarot slot N clear`, `/tarot slot auto`, `/tarot slot swap N M`, and `/tarot reset` via player-scoped CLIENT `/trigger` operations. Command Aliases schema uses permission 0. Both `/tarot status` and `/tarot slots` display actual Arcana titles and Sequence numbers rather than internal numeric kit codes; the partner is revealed at Sequence 4.
- The full 434-entry source manifest identifies every ability, its flag, exact description, compiled power (when present), and remaining work. **241 powers compiled (73 source-complete, 168 explicitly partial), 193 still blocked.** No fake `origins:simple` abilities are emitted.
- Permanent primary-pathway drawbacks are innate Origin powers, **not removable Sequence-9 slot abilities**: Fool's +25% exhaustion plus 20 more compiled pathway drawbacks are attached directly to their Origins, outside the source-grant/revoke cycle.

## Rev3 identity-drawback integrity

The first version only pinned the Fool's Spiritual Expenditure permanently. This allowed players from 20 other pathways to remove the encoded Seq9 drawback when they switched slots at Sequence 4. The build now extracts the compiled penalty from each corresponding Seq9 kit and puts it into the **primary Origin's power list**. Every other Seq9 power remains in the removable slot kit. This also means administrators' `rollback_player` only revokes sequence-granted powers, not inherent identity penalties.

**Only Wheel of Fortune's Debt of Fate still lacks a separate native identity power.** Lovers' Separation Anxiety now uses a persistent 600-tick proximity counter, +35% exhaustion and −15% mining when alone; it is partial because the fallback measures all players nearby rather than only same-team allies. These remain visible release blockers. Justice (Compassionate Restraint) now enforces −70% damage against passive mobs but cannot distinguish unprovoked enemy players (partial). Hanged Man (Weight of Sin) prevents natural regeneration above eight hearts but does not yet support the three temporary cap-unlock events (partial). Do not claim all 22 drawbacks are faithful. The 434-ability source-manifest count is unchanged, because the fix rehomes existing powers rather than inventing new abilities.

The Justice and Hanged Man penalties are now real native *partial* powers, attached to their Origins. The manifest distinguishes them from complete implementations. At present there are 21 Origins with some permanent drawback behavior (including Fool), and one without.

## Additional source-traced abilities

Batch 2 implements 13 more native or partial abilities across Empress, Emperor, Wheel of Fortune, Justice, Hanged Man, Sun, World, Tower, Star and Hermit. Examples include Mirror Veil invisibility, a six-way equally weighted Fate's Current, undead-only Solar Flare, active self-cleansing with Purify and upgraded retaliation effects.

**Only Solar Flare is classified a complete Rev2 translation** in this batch. The other twelve retain detailed per-ability `missing` descriptions in `arcane_ability_manifest.json` (for example, Rev2 does not define Fate's Current effect durations, and team-aware PvP targeting cannot yet be reproduced exactly without scripting). Structural JSON/power tests do not establish in-game compatibility.

## Parallel large-batch delivery (38 new powers)

Three independent source modules, `arcane_rev3/batches/support.py`, `control.py` and `mobility.py`, add **38 unique, non-placeholder abilities** to the pre-existing 128. Their machine-readable manifest exposes all full/partial classifications and detailed limitations.

- **14 support and identity skills:** regeneration circles and Benedictions, Hymn, Therapist's Presence, Rally, Shared Dream, Spirit Sense, Nightmare, Beauty, White Angel, Shared Refuge II, Grave Affinity II, Requiem, and Lovers' Separation Anxiety.
- **17 hostile-mob control and retaliation skills:** Nature's Grasp, Withering, Bane, Cataclysm, Haunt, Misfortune, Petrifying Gaze, Abolish, Lullaby, Puppet String, Trickster's Escape, Paper Figurine Substitute, Flesh Creek, Profane Aura, Devil's Mark, Hex and Question.
- **7 movement/stealth/defense skills:** Threshold Step, Doorstep, Sealed Room, Wraith's Veil II, Incorporeal, Shadow Whisper and Iron Fist.

The 1.18.2-safe targeting helper emits **fixed server-side commands** with `@e[type=#tarot:hostile]`, `@e[type=#tarot:undead]` or players-only positive buffs; it does not interpolate player input. Enemy-player targeting, script-driven decoys, spell charging, missing cooldown resources, structural phasing, teleport raycasts and advanced mob AI remain **partial** where specified in Rev2. `action_on_entity_use` in 1.4.1 does not supply a built-in cooldown field, so right-click attacks are not misrepresented as fully rate-limited.

Lovers' Separation Anxiety has a real per-player `a_alone_time` tick counter, capped at 601 and reset when any player enters eight blocks. After more than 600 ticks alone, the native scoreboard condition applies +35% exhaustion and −15% break speed. Its same-team qualifier is not yet implemented and is recorded as partial.

All compiled abilities remain test-world-only until actual 1.18.2 Origins 1.4.1 testing.

## Non-OP clickable Tarot menu — mod-independent fallback

The development build includes a **native clickable chat menu**, accessible to any ordinary player through `/trigger a_help`. It does not rely on the Command Aliases mod to parse `/tarot slot` commands, and it does not grant operator permissions.

After opening `/trigger a_slots`, players at Sequence 4–2 can click **Edit slot N**, select the primary or unlocked partner pathway, then select an available Sequence. Each click sends a normal, player-owned `/trigger` command; the server revalidates current Sequence, unlocks, duplicates and remaining slots through the existing `slot/assign` contract. Players can also click **Clear slot N** or **Auto-fill primary slots**. All 22 pathways and eight possible slots are supported.

The associated `a_menu`, `a_card` and `a_seqpick` trigger objectives and `a_pick_slot`, `a_pick_path` scratch scores are scoped to each player. The GUI is disabled by the persistent admin pause and never grants early partner kits.

This is a fallback rather than proof that Command Aliases **1.0.1 for Minecraft 1.18.2** handles long child-command argument chains. Its `schemaVersion:1`, `COMMAND_CUSTOM`, literal `children` and permission-0 shape match the published documentation, but **actual non-OP parser acceptance must be tested** with that exact installed mod. <https://modrinth.com/mod/commandaliases/version/rQr6FUYI> and <https://wiki.commandaliases.flashyreese.me/command-modes/custom>.

## Official 1.4.1 type compatibility gate

The 1.4.1 audit caught a real earlier incompatibility: Lovers' Fertile Hands used `origins:modify_healing`, a newer-only power type. Its power now uses **native +20% crop-breaking speed** for seven vanilla crops, and its +25% self-healing enhancement is explicitly listed as unimplemented. No unverified healing API is emitted.

The build regression suite now includes `tests/test_arcane_141_schema.py`: the official [Origins/Apoli 1.4.1 power registry](https://origins.readthedocs.io/en/1.4.1/types/power_types/) is baked into a checked allowlist for top-level and nested `origins:multiple` power types. It rejects newer-only power type identifiers and checks common required fields, cooldowns, player-owned grant references and hard-coded privileged action commands. Compatible JSON still needs an actual Minecraft 1.18.2 acceptance test, since type registration does not confirm effect semantics or config mod compatibility.

## Resonance wave 2 and individual combat wave: 37 additional powers

A second independently auditable module `arcane_rev3/batches/resonance2.py` adds **28 named middle-sequence Resonance skills** across marked_verdict, burning_archive, crumbling_reaper, impossible_fist, benevolent_crown, binding_contract, starless_poison, eclipse, walking_sanctuary and loaded_dice. These include real tagged-hostile status effects, XP gains, undead-linked healing, sneak/bow conditions and fixed ability key cooldowns. The separate `individual3.py` adds **nine individual pathway combat/utility abilities**: Reap, Bulwark, Guide, Verdict, Grave Whisper, Twilight Blade, Sanguine Resilience, Nature's Step and Sanctify.

**All 37 are explicitly PARTIAL.** The manifest records exactly which Rev2 effects cannot be reproduced faithfully, including enemy-player team safety, dynamic mob AI and targeting, next-hit damage modifiers, portal/terrain alteration, charge requirements and death-triggered location scans. Some are conservative non-equivalent analogues: e.g. Grave Whisper yields a rotten-flesh item rather than calculating actual entity loot. They are not presented as full, balanced abilities. Nonstandard 1.18.2 APIs, KubeJS and custom Java remain excluded.

These 28 new Resonance definitions are compiled into JSON, but **all eleven Resonance Origins remain unchoosable and no pair grants or Sequence1 unlock have been added**. Full-kits and runtime validation remain release gates.

## Resonance progression: 23 genuine pair powers, still fail-closed

The next module, `arcane_rev3/batches/resonance.py`, compiles **23 source-mapped Resonance powers across all 11 pair identities**. All 11 Sequence-9 forms are represented with a genuine subset of their prescribed combined passives; eight Sequence-8 combinations and four Sequence-7 combinations are also implemented. The compiler now accepts both `individual` and `resonance` catalog families.

**This is not a Resonance unlock.** The generated 11 Resonance Origins remain unchoosable with empty intrinsic power lists, no Resonance power is granted by a slot function, and the Seq2→Seq1 ritual remains fail-closed without consuming ingredients. The source manifest counts the compiled Resonance JSON as implemented/partial translations, **not usable kits**. The remaining scripted minion AI, Sin storage, creative flight windows, damage-source tracking, team-safe targeting and fully precise 10-kit states are still unavailable.

The 23 compilation records include **four source-complete and 19 explicitly partial** power translations; all still require actual Minecraft runtime acceptance.

## Second batch: native interactions and exact inventory trade

Another **15 non-placeholder abilities** are generated from `arcane_rev3/batches/native2.py`: Lovers Triage and Blessing, Hierophant Purify, Consecrated Workspace and Sanctified Ground II, Justice Calm and Compassionate Restraint II, Lovers Symbiosis and Transmute, Tower Unstable Ground, Emperor Coin, Fool Stage Magician and Spiritual Overload, Death Grave Dirt, Chariot Flame Burst.

These are intentionally labeled partial because Minecraft 1.18.2/Origins 1.4.1 cannot enforce the listed skill cooldowns in some native right-click hooks, and some require AI targeting, client cosmetics, exact team comparison or safer raycast hooks. The **Lovers Transmute** transaction is built as a server-owned function: count iron ingots non-destructively, require two, remove two, then grant one gold ingot; insufficient iron consumes nothing. The underlying `/tarot` alias still has no operator access. A 12000-tick activation cooldown is set, though it also starts on an insufficient-inventory attempt.

The supported vanilla sanctified-ground tag now includes all Minecraft 1.18.2 stone-brick base and stair/slab/wall variants. These effects scan their radius and need real performance acceptance before server deployment.

## Retaliation team-safety gate

Rev3 prohibits offensive effects against allied players. `origins:attacker_action_when_hit` has no inherent same-team comparison in Origins 1.4.1. Earlier abilities could inflict debuffs when an allied player hit the wielder. The compiler now adds a **native damage-source attacker condition** to every negative retaliation effect except Sun's already-undead-only Solar Flare: only attackers in the `tarot:hostile` entity tag can receive the effect.

This is intentionally **fail-closed**. Enemy players are not yet affected, because identifying hostile players without affecting same-team allies remains unverified under the datapack-only restriction. The ability audit automatically downgrades affected source-full powers to `partial`, with an explicit target deficit. The ability count stays 128, but the breakdown becomes 64 source-full, 64 partial, and 306 blocked. The Fool-only alpha receives the same Clown's Mischief guard. Structural tests verify the guard exists; they cannot substitute for real PvP/friendly-fire acceptance.

## Fool Spirit Vision sphere compatibility

Origins/Apoli 1.4.1's `origins:area_of_effect` entity action has a radius but no `shape` field; it cannot natively guarantee Rev2's spherical 10-block reveal. Both the full developer pack and earlier Fool-only sandbox pack therefore use one **fixed, server-side** `origins:execute_command` action with permission level 2 and the vanilla target selector `@e[distance=..10]`. The ability still requires sneak + secondary key, applies Glowing for 2 seconds, includes the caster, and keeps the 100-tick cooldown. The static power action is **not exposed as an arbitrary operator command through /tarot**, which remains a non-OP /trigger bridge.

This matches the handbook's radius geometry at the command level but must be verified against real Minecraft 1.18.2 behavior. The code explicitly tests the exact command and permission level; no unsupported action `shape` parameter is emitted.

## Higher-sequence upgrades

This batch adds **six new native powers** (Demon Form, Ruin-Proof II, Wheel's Misfortune, Law's Weight II, Nightwatch II and Plague Touch) and **repairs four existing legacy templates** that were incorrectly suited to the old cumulative progression: Moon's Shaman, World's Cold Precision II, Sun's Unshadowed II and Hanged Man's Dark Blade.

The handbook explicitly says Shaman heals 1.5 hearts = 3 HP every 600 ticks, not 2 HP. Cold Precision II now specifies a standalone +30% projectile modifier and Unshadowed II a standalone +50% undead modifier, rather than weak incremental deltas. Dark Blade uses two conditioned attributes below 12 HP, limiting its offensive effect to melee rather than every damage source.

**Dark Blade remains a full source translation in code.** The nine other upgrades are labeled partial primarily because Rev2 specifies replacing an earlier kit, while Rev3 slots can hold both and stack the effects. Exact player-team targeting and source replacement behavior remain unverified. All corrections retain traceable source information in the machine-readable manifest.

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
