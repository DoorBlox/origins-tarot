# Batch 3 - implementation gaps and approximations

This is **native code** with one discrete Origins JSON power entry per ability,
not KubeJS. Static datapack files whose type is `origins:simple` are markers:
their observable effects come from `WorldJusticeAbilities`, `MarkedVerdict`,
and combat/player/projectile Mixins. Do not interpret JSON-only inspection
as proof of live ability implementation.

- World Predator's Patience computes time holding a bow while motionless at impact
  instead of attaching charge to the actual projectile on firing. This can drift
  if the shooter moves between launch and impact.
- World Paper Dagger uses nearest enemy within 8 blocks and an explicit V binding;
  Rev2 did not specify a key or range. Air Cannon is approximated using
  immediate damage/knockback instead of a rendered flying projectile, but
  preserves player/mob split and 14-block cap.
- World Small Miracle and Mystery Step only specify cooldowns in Rev2.
  Their bounded self-heal and safe 12-block blink are **approximations**,
  not invented claims of source fidelity.
- World Borrowed Face and Marked Verdict Silent Witness lack client player
  skin/name disguise. Server invisibility and private health report are available.
- World Perfect Prey and Marked Verdict auto-hit depend on native homing of a
  single projectile, which cannot guarantee a hit through solid blocks.
  In exact source, targeting/trails should be improved before public SMP.
- Justice Calming Presence stops animal navigation while calm but cannot
  disable every passive mob flee/panic AI goal without dedicated goal mixins.
- Justice Patient Observation periodic reveal is scanned every 100t;
  Rev2 does not specify a period.
- Justice Compassionate Restraint detects 'unprovoked' using whether an enemy
  player attacked the holder within 200t, not a global social consent state.
- Justice Dream Step is detected by polling sleeping state once each second.
- Justice Author's Edit is an **approximation** using 300t Weakness and private
  target-health report, not literal chat word mutation.
- Justice Mindscape uses server-level slow/weakness and damage cancellation.
  Potion effects approximate freezing player locomotion. Exact anti-jump and
  sprint logic also requires Mixins and in-game verification.
- Resonance Marked Judgment emits target coordinates as chat instead of a
  custom directional HUD. Target position reports remain private to caster.
- Mob 'pacification' is approximated by Slowness 255, Weakness 255, stopped
  navigation and cleared mob target. Some other-mod AI may ignore it.
- The Marked Verdict is not fully source-faithful in visual particle effects,
  cinematic animations, specific mob goal behavior, and friendly marker indicators.
- Sequence-up now has a non-OP survival /tarot ascend path adapted from the repository's prior V3 Acting+ritual economy; live testing of item/kill/trade hooks and altar requirements is still necessary. The Rev3 natural progression
  economy has not been connected. Testing these modes as ordinary players requires
  implementing a validated ascension trigger.
- Remaining: 18 individual pathways and 9 other Resonance forms (356 entries),
  with the extended mechanics not ported. All 434 must be implemented before
  this can be called Arcane V2 complete.

All trade, reveal and targeting logic is server-authoritative. The SMP owner
should test these on a disposable world before granting access to friends.
