# Arcane V2 native capability coverage

All mechanics use a Fabric companion mod, Apoli/Origins data powers, and
Mixins. **No KubeJS dependency** is necessary or allowed in this target.

| Category | Resources | Native behavior |
|---|---:|---|
| Fool | 14 | Early handlers and approximations; see Batch 1 gaps |
| Hanged Man | 14 | Sin/regen/death handlers; see Batch 2 |
| Paper Martyr resonance | 10 | Native 10-kit fusion at Sequence 1 |
| World | 15 | Projectile, targeting, trade, Mark and Perfect Prey effects |
| Justice | 15 | Healing, damage restraint, sleep, interactions and Mindscape |
| Marked Verdict resonance | 10 | Native 10-kit fusion at Sequence 1 |
| **Total represented** | **78 / 434** | **Not all exact; not playtested** |

Remaining 356 abilities across 18 individual Arcana and 9 Resonances.
These are **not** placeholders generated to pretend full coverage. They
have not been authored in this build.

CI gates: Gradle Java compilation + JUnit; V2/V3 regressions; headless
Fabric 1.18.2 + Origins 1.4.1 server startup. Passing does not replace
live multiplayer/ability acceptance.

Sources: `spec/REV2.txt` and `spec/REV3.txt`. Rev 3 controls the sequence
and slot transitions; Rev2 controls ability mechanics and cooldowns.

## Optional survival ascension bridge

The native mod also includes /tarot status and /tarot ascend for the
four implemented origins, using the previous V3 alternating Acting
A/B and ritual costs. Sequence-up calls the same transition logic as
the administrator's debug command. It is NOT included in the 78
ability count, and does not claim to be a Rev3-specified Acting economy.
