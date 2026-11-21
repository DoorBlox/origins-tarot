# Batch 5 gaps, source fidelity and SMP risks

Source: `spec/REV2.txt` Death (§XIII), Tower (§XVI), and Crumbling Reaper
(§IV); `spec/REV3.txt` governs Sequence slot/resonance transitions.

- `origin:simple` JSON powers register names/requirements, but actual logic is
  in server Java and Mixins. Named resources are not equivalent to proof of
  complete behavior.
- Death's Grave Whisper is implemented as a *single bonus bone on some
  qualifying kills*, not a strict 10% multiplier on that mob's entire loot table.
- Death's Gate now builds a **full framed Nether portal in empty space**
  instead of directly changing dimensions. Its blocks are persistent, and
  server-side block placement may bypass third-party claim/protection mods.
  Keep this terrain-changing skill **disabled for public SMP use** until
  region-protection integration is implemented and tested.
- Death's Ferry grants Dolphin's Grace 100t; it **does not** walk on water.
- Death's Consul summons a temporary bounded Vex-like ally; it does not
  temporarily convert a specific nearby undead enemy.
- Tower Falling Tower has approximate launch rather than an animated eight-block
  leap and ground slam. +20% incoming knockback is still missing.
- Tower Falling Ground self/ally damage is **intentional per Rev2**. Its ground
  sampling currently tests entities each second; exact '5-tick throttle,
  50-block cap' still needs further work.
- Crumbling Reaper's absorption uses direct vanilla absorption amount and a
  server-tracked 1200t clock. To avoid deleting buffs from other mods, it
  does not yet forcibly subtract the remaining Arcane-owned absorption when
  that clock expires. **Exact expiration needs a source-attributed effect.**
- Crumbling Reaper's Seq1 Falling Tower's Reap uses an immediate
  impact/damage zone rather than a physics-synchronized 8-block leap and
  slam. Absorption awards occur on confirmed kills; exact visual timing
  remains approximate.
- No exact custom animations, terrain cracking models, or guaranteed modded-AI
  compatibility are in this batch.
- The native engine remains a development-only private SMP candidate; 277
  ability entries across 14 individual pathways and 7 Resonance forms still
  require implementation and verification.
