# Arcane V2 native capability coverage

Rev2 lists 324 individual and 110 Resonance ability entries = 434 total.
Rev3 governs shared Sequence, slots, and Sequence1 fusion.

| Pair | Individual entries authored | Fusion entries authored | Verification |
|---|---:|---:|---|
| Fool + Hanged Man / Paper Martyr | 28 | 10 | Java/boot tested, gameplay acceptance pending |
| World + Justice / Marked Verdict | 30 | 10 | Java/boot tested, gameplay acceptance pending |
| Hermit + Chariot / Burning Archive | 29 | 10 | Java/boot tested, gameplay acceptance pending |
| Death + Tower / Crumbling Reaper | 30 | 10 | Java/boot CI passed; gameplay acceptance pending |
| Magician + Strength / Impossible Fist | 29 | 10 | Java and startup CI passed; experimental phasing |
| Emperor + Lovers / Benevolent Crown | 29 | 10 | Java/boot CI passed; gameplay acceptance pending |
| Devil + Judgement / Binding Contract | 30 | 10 | Java unit tests/CI passed; smoke may still be pending |
| Star + Empress / Starless Poison | 30 | 10 | Candidate source, exact-head CI pending |
| **Authored** | **235** | **80** | **315 / 434** |
| **Remaining** | **89** | **30** | **119 / 434** |

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

Batch 8 adds explicit consent-based contracts, timed law domains, Devil
combat buffs, Judgement PvP debuffs and native summons. It retains known
gaps in no_spawn, precise potion-healing attribution, human stun/aggro and
client rendering. Tests and owner gameplay acceptance are separate gates.

Batch 9's Starless Poison line contains native damage targeting and
server-side flight restoration, but client rendering, phantom-day thresholds,
true extinguished lights and passive hostile mob AI are unresolved. Treat
resource coverage separately from mechanic fidelity and owner acceptance.
