# Batch 1 — delivery gaps and genuine client blockers

This draft branch **is not ready for release**. The native KubeJS replacement is a work-in-progress.

## Unimplemented / incomplete gameplay (engineering work, not platform blockers)

- Fool Seq 0: Legend of the Fool now has a native 700-tick activation, flight, decoys, rewind, fire/fall immunity, hit debuffs and end effects. The exact 75% DR, +50% final damage, double mob loot and restart-safe persistence remain unfinished.
- All other 21 individual pathways and all 11 Resonance kits are not implemented or granted in the native registry.
- A built-in native event listener for player Origin choice, death/respawn/dimension refresh and compatibility with externally managed sequence-up needs acceptance against actual runtime.
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
