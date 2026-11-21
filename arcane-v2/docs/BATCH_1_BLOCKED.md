# Batch 1 — delivery gaps and genuine client blockers

This draft branch **is not ready for release**. The native KubeJS replacement is a work-in-progress.

## Unimplemented / incomplete gameplay (engineering work, not platform blockers)

- Fool Seq 0: Legend of the Fool now has a native 700-tick activation, flight, decoys, rewind, fire/fall immunity, hit debuffs and end effects. The exact 75% DR, +50% final damage, double mob loot and restart-safe persistence remain unfinished.
- The remaining 20 individual pathways and 10 Resonance pairs are not implemented or granted in the native registry. The Hanged Man and Paper Martyr mechanics are being validated in Batch 2.
- Native Origin callback, death/respawn/dimension refresh and sequence-up listeners are implemented but need live-world acceptance.
- Original V3 ascension progression has **not** been migrated into the Rev3 paired-path synchronized Sequence model. Until then only an OP debug Sequence command changes levels.
- Activation of individual Fool Seq1/Seq0 in normal progression is intentionally excluded by Rev3 Seq1 Resonance timing.
- CD/guard reset, cooldown effect cleanup, mob-specific targeting and per-path permanent identity drawbacks are incomplete outside initial Fool scope.

## Genuine missing client capability

- Full Faceless Disguise / Borrowed Face **exact** skin/model/name replacement requires
  client rendering or synchronized player profile replacement. The native server
  currently provides only invisibility approximation.
- Client-side custom HUD / cinematic overlays require a client implementation.
  Rev3 permits chat UI as a fallback.

No placeholder is to be represented as a finished or playtested ability.
