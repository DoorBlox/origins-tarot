# Arcane V2 native capability coverage

Rev2 lists 324 individual and 110 Resonance ability entries = 434 total.
Rev3 governs shared Sequence, slots, and Sequence1 fusion.

| Pair | Individual entries authored | Fusion entries authored | Verification |
|---|---:|---:|---|
| Fool + Hanged Man / Paper Martyr | 28 | 10 | Java/boot tested, gameplay acceptance pending |
| World + Justice / Marked Verdict | 30 | 10 | Java/boot tested, gameplay acceptance pending |
| Hermit + Chariot / Burning Archive | 29 | 10 | Java/boot tested, gameplay acceptance pending |
| Death + Tower / Crumbling Reaper | 30 | 10 | Latest CI pending; gameplay acceptance pending |
| Magician + Strength / Impossible Fist | 29 | 10 | Candidate source/CI pending; experimental phasing |
| **Authored** | **146** | **50** | **196 / 434** |
| **Remaining** | **178** | **60** | **238 / 434** |

**Read "authored" as packaged named power IDs with native handlers or
documented approximations, never as in-game verified complete behavior.**
Known missing exact mechanics include player disguise visuals, some custom
weather and block lighting, structure finding, Waypoint/Astral Lock,
enchant transfer, accurate phasing/collision and armor penetration.

Non-OP native /tarot ascend (Acting + offerings) adapts the former V3
economy to the Rev3 synchronized progression, not from Rev2 mechanics.
A disposable Minecraft 1.18.2 Fabric/Origins boot test runs in PR CI,
but true multiplayer gameplay testing is still outstanding.
