# Arcane V2 capability coverage (native KubeJS-free build)

Rev2 contains 324 individual ability entries and 110 Resonance ability
entries = 434 total; Rev3 governs all Sequence transitions and slot grants.

| Group | Individual powers | Resonance powers | Status |
|---|---:|---:|---|
| Fool / Hanged Man / Paper Martyr | 28 | 10 | Native compiled, runtime approximations |
| World / Justice / Marked Verdict | 30 | 10 | Native compiled, runtime approximations |
| Hermit / Chariot / Burning Archive | 29 | 10 | In current source candidate; CI pending |
| **Total authored** | **87** | **30** | **117/434** |
| **Remaining** | **237** | **80** | **317/434** |

An authored power is not equivalent to verified behavior: client disguises,
custom local weather, enchantment copying, true armor-ignoring arrows and
some AI/control edge cases remain approximated.

Native progression: /tarot status and /tarot ascend are available without
OP for the implemented origins. Their Acting and ritual offerings are
adapted from the repo's previous V3 progression model, whereas Rev3 controls
the shared Sequence, slot and Resonance transitions.

CI: Gradle and JUnit + headless Fabric 1.18.2 / Origins 1.4.1 server startup,
plus unchanged legacy V2/V3 workflows. Live-world acceptance remains
unverified until run by the SMP owner.
