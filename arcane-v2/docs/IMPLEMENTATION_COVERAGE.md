# Arcane V2 native capability coverage

Rev2 lists 324 individual and 110 Resonance ability entries = 434 total.
Rev3 governs shared Sequence, slots, and Sequence1 fusion.

| Pair | Individual entries authored | Fusion entries authored | Verification |
|---|---:|---:|---|
| Fool + Hanged Man / Paper Martyr | 28 | 10 | Java/boot tested, gameplay acceptance pending |
| World + Justice / Marked Verdict | 30 | 10 | Java/boot tested, gameplay acceptance pending |
| Hermit + Chariot / Burning Archive | 29 | 10 | Java/boot tested, gameplay acceptance pending |
| Death + Tower / Crumbling Reaper | 30 | 10 | Latest CI pending; gameplay acceptance pending |
| Magician + Strength / Impossible Fist | 29 | 10 | Java and startup CI passed; experimental phasing |
| Emperor + Lovers / Benevolent Crown | 29 | 10 | New candidate; exact-head CI pending |
| **Authored** | **175** | **60** | **235 / 434** |
| **Remaining** | **149** | **50** | **199 / 434** |

**Read "authored" as packaged named power IDs with native handlers or
documented approximations, never as in-game verified complete behavior.**
Known missing exact mechanics include player disguise visuals, some custom
weather and block lighting, structure finding, Waypoint/Astral Lock,
enchant transfer, accurate phasing/collision and armor penetration.

Non-OP native /tarot ascend (Acting + offerings) adapts the former V3
economy to the Rev3 synchronized progression, not from Rev2 mechanics.
A disposable Minecraft 1.18.2 Fabric/Origins boot test runs in PR CI,
but true multiplayer gameplay testing is still outstanding.

Batch 7 adds native domain authorization and movement policy, permanent
shield and solitude drawbacks, allied healing and server-driven attribute
modifiers. See the Batch 7 gaps list for approximate villager discounts,
land-claim interactions, leaf phasing and player-target control.
