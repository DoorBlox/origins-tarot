# Arcane V2 handbook: implementation and safety register

**Project:** The Tarot Club on Minecraft Java 1.18.2, Fabric, Origins 1.4.1, Apoli, optional KubeJS 1802.5.5.
**Status:** DRAFT PR, isolated test-world preview. NOT a released production update.

## What was supplied and preserved

The complete original specification is in [HisyamOrigins.txt](HisyamOrigins.txt). An auditable, structured catalog is in [arcane/catalog.json](../arcane/catalog.json).

| Category | Count |
|---|---:|
| Individual Major Arcana | 22 |
| Proposed fully fused Resonance forms | 11 |
| Sequence stages per form | 10 (9 through 0) |
| Individually named powers | 324 |
| Resonance stage powers | 110 |
| Total described entries | **434** |
| Tagged D in the handbook | 251 |
| Tagged D/S | 62 |
| Tagged S | 121 |

**Important:** The manuscript's D/S label is a design claim, not a proof of native Origins 1.4.1 feasibility. Several seemingly native features actually require older-version compatibility review or scripting.

## What's working at the source/test level

- One real native power preview is mapped to EACH of the 22 existing Arcana: 22 power JSON files, using the [vetted template manifest](../arcane/templates.json).
- **16 full matches and 6 partial matches** to the handbook. Every partial is explicitly labeled, including the missing behavior.
- The compiler [arcane/preview.py](../arcane/preview.py) generates TWO optional ZIP files by overlaying the existing V3 datapacks. It does not change normal V3 packaging.
- Each extra power is granted only when its Arcana is actively equipped and the player has reached the required sequence. All extra powers are revoked from a dedicated source on each V3 refresh.
- The 22 existing Origins, 18 built-in Elytra gliders, passive-first V2 traits, 2 active skills, saved primary/secondary progression and cooldown checks are carried over.
- Eight required entity/block/item tag sets are generated for later content work.
- The preview does not give players full double-Origin stacking, an extra Origin layer, or any active 11-form fusion.
- The exact PR-head GitHub Actions workflows verify build and JSON/reference integrity. In-game behavior has NOT been tested.

## What's NOT implemented yet

The remaining **412** entries are specifications, not playable powers. Some need client-side cosmetics, some require a version-specific KubeJS event bridge, and some require additional PvP/anti-grief design.

In particular, KubeJS-only abilities involving skin/model replacement, lethal-hit cancellation, mob/player AI redirection, persistent minions, teleportation through solid terrain, private inventories, inventory modification, custom spells and extensive area scans are not implemented here. DO NOT turn their descriptions into no-op power files.

**PvP and team safety.** The handbook explicitly requires negative effects to hit hostile mobs plus enemy players, while buffs affect self and same-team players. Origins 1.4.1 does NOT provide a general documented dynamic same-team bi-entity predicate. A simplistic OR of enemy player type and hostile tag would also affect teammates. The new 22 preview powers therefore deliberately avoid player-targeted area damage or debuffs. The requested shared team-filter helper must be implemented and tested separately before launching PvP abilities.

**Version correctness.** Do not copy power types from modern Origins/Apoli documentation blindly. For example, the base version uses the power type origins:modify_break_speed; the handbook sometimes writes origins:modify_block_break_speed. Newer Apoli added an entity-in-radius condition later; it is not safely assumed available in 1.4.1.

## Progression policy retained

The handbook contains a timing conflict: it proposes committing to full fused Resonance paths at Sequence 5, while the already-developed V3 only unlocks a second Arcana at Sequence 4. The PR preserves existing V3 progression:

- Sequence 9: start with one Arcana.
- Sequence 4: unlock second Arcana via Second Awakening trial.
- Sequence 3: portable switching.
- Sequence 2: limited Echo from inactive Arcana.
- Sequence 1: curated hybrid Resonance.
- Sequence 0: rare apotheosis / prestige.

The 11 entirely fused Origin designs are retained in the catalog for an explicit later decision; they are NOT silently substituted for the existing 12 V3 minor Resonance pair bonuses.

## How to test the preview (NOT main SMP)

1. Open the successful GitHub Actions workflow named **Arcane Handbook Preview** on this draft PR.
2. Download the artifact named **tarot-arcane-preview-alpha**, extract that outer artifact ZIP, and select ONE inner pack: ONLY or ADDON.
3. Back up the whole test world, especially playerdata, advancements and world/data/scoreboard.dat. Also preserve the old V3 ZIP.
4. Stop the test server. Remove the old V3 datapack from the selected test world and upload the single preview ZIP to that world's datapacks directory, WITHOUT extracting the inner ZIP.
5. Start the test server. Check datapack list and first-console startup messages for Apoli/Origins errors.
6. Test one representative Arcana at each sequence, including the exact condition/cooldown of the new preview power. Repeat with another player in the party to check isolation and switching.
7. Test Elytra (18 origins), all 22 basic classes, progression, Second Awakening, portable swapping and failed-swap protection.
8. Roll back by stopping the server and restoring both the old V3 ZIP and the backed-up world.

Do not install V3 and this overlay preview simultaneously: **the preview contains the full V3 datapack already**.

## Next implementation milestones

1. Verify every native D power type against Origins 1.4.1, including exact condition and action fields, and add them incrementally with gameplay tests.
2. Build a separate permissioned KubeJS 1802.5.5 entity-targeting helper respecting teams, owner, PvP rules, allies, pets, low TPS, radius and cap.
3. Implement the S and D/S scripts one power at a time, with load/unload, cooldown persistence and anti-grief guards.
4. Resolve the 11-full-fusion versus V3 dual-attunement design conflict before changing player saves.
5. Perform real in-game acceptance and compatibility checks before merging the expansion into main.

Official references: https://origins.readthedocs.io/en/1.4.1/ ; https://github.com/apace100/origins-example-packs .
