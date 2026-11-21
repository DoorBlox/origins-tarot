# Arcane V2 — native Fabric port (no KubeJS)

This is **not** the existing V3 Path of Ascension datapack. It is a separate
implementation line for the user-supplied Rev 2 (abilities) / Rev 3 (slots and progression).
Do not install both simultaneously; they share tarot: origin IDs.

Target: Minecraft **1.18.2**, Fabric Loader **0.14.25**, Fabric API
**0.76.0+1.18.2**, Origins **1.4.1**, Java **17** runtime, no KubeJS.

Sources: `spec/REV2.txt` and `spec/REV3.txt` stop at their explicit end markers.
Rev 3 wins on progression and Resonance timing. Identity-only origin powers
follow the owner's revised architecture.

The Fabric module is under `native/`. Build with:
```
cd arcane-v2/native
gradle build
```

Server admin must replace the legacy Tarot datapack, back up the world,
then load the new built JAR (including its bundled data resources).
The native mod now includes the Fool's initial event handlers, bounded Vex-like minions, and a timed capstone approximation. **These abilities have not been accepted in a live world.**

This branch is **not production-ready** until the full 434-ability coverage
and live Minecraft acceptance gates pass. Never treat static tests as in-game proof.

## Arcane V2 native development slice — Fool + Hanged Man / Paper Martyr

The compiled mod bundles 14 Fool, 14 Hanged Man, and 10 Paper Martyr
Sequence power IDs, their origin resources, and shared entity/blocks/item tags.
The 10 Paper Martyr abilities activate together at Sequence 1. The rest of the
handbook is **not implemented**. Never install the old V3 datapack alongside
this mod: it also owns `tarot:*` origin identifiers and implements a conflicting
progression model.

The branch is a **development test build**, not a completed 434-power release.
See `docs/BATCH_2_TEST.md` and `docs/BATCH_2_GAPS.md`. You may test on a
private SMP before inviting friends, but back up the world and player files first.
A new optional native survival progression bridge now supports `/tarot status`
and `/tarot ascend` without OP: it reuses the existing repository's V3
alternating Acting marks, 120-second online cooldown, and ritual offerings.
All upgrades advance the Rev3 **single shared Sequence**. This is a port of
the earlier V3 economy, not a claim that Rev2/Rev3 explicitly specify an
Acting economy. Manual in-game confirmation remains necessary.
