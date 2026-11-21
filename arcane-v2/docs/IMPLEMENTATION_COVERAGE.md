# Arcane V2 capability coverage (native KubeJS-free build)

Rev2 contains 324 individual ability entries and 110 Resonance ability
entries = 434 total; Rev3 governs all Sequence transitions and slot grants.

| Group | Individual powers | Resonance powers | Status |
|---|---:|---:|---|
| Fool / Hanged Man / Paper Martyr | 28 | 10 | Native compiled, runtime approximations |
| World / Justice / Marked Verdict | 30 | 10 | Native compiled, runtime approximations |
| Hermit / Chariot / Burning Archive | 29 | 10 | Build/boot CI passed before next batch; live acceptance pending |
| Death / Tower / Crumbling Reaper | 30 | 10 | New native handlers; run exact-head CI and manual gameplay tests |
| **Total authored** | **117** | **40** | **157/434** |
| **Remaining** | **207** | **70** | **277/434** |

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

### Important qualification

The 157 entries count packaged named ability definitions, not 157 independently
verified gameplay effects. Some require client rendering, custom mob AI,
combat edge-case testing, and server-world acceptance. The source handbooks
remain authoritative, and unimplemented/approximate behavior is documented
per batch rather than substituted silently.
