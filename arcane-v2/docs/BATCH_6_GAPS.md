# Batch 6: implementation gaps / safeguards

Source: Rev2 Magician (§I), Strength (§VIII), Impossible Fist (§V); Rev3
controls slot/Resonance timing. This is a development implementation only.

- Full Moon Ravings' Nausea interval is server-world-time based, and does not
  depend on a real full moon; the source defines exposed sky.
- Star Chart currently draws a direction line but DOES NOT find a nearest
  structure. Never describe it as working structure detection.
- Recorded Step binds the last crouch-right-clicked block and only teleports
  to safe standing space, instead of arbitrary ungrounded coordinates.
- Shortcut picks the block opposite the player's facing as an approximation
  of 'opposite block', with native breaking permission and no bypass.
- Magician Seq1 Waypoint and Astral Lock have identity/Sequence JSONs but
  require proper portal marker interaction, consent, expiry, and
  cross-dimension control. These are **not yet functional**.
- All Paths Converge currently uses experimental server-side noClip. Client
  collision prediction, wall/anticheat interaction, exact prohibition on
  block interaction, and return-to-safe-air still require live tests.
- Strength No Bow restriction uses a server UseItem callback. Client bow draw
  prediction and bow projectile penalty at Seq7 are not fully implemented.
- Swim penalty applies a movement-speed modifier when submerged, rather than
  a native 45% swim-only movement factor.
- Grounded Slam now uses an exact per-fall landing event instead of
  tick polling, but the strike/slow effects still need timing acceptance.
- Dawnlight currently shows particles / Night Vision, not true temporary
  world light level8 blocks. A crash-safe light-block manager is necessary.
- Strength Silver Blade ignores no armor yet; true armor penetration requires
  controlled damage bypass rather than an undocumented damage multiplier.
- The Giant's Decay and Impossible Fist do not halve enemy armor exactly.
  They only apply Wither/Slowness and native damage multipliers.
- Divine Door currently implements the pull branch, not an alternate teleport
  or choose-one UI. Exact stun is approximated with Slowness255.
- Giant's Shortcut and unrestricted phasing remain experimental; special
  unphasable block enforcement is checked each server tick.
- Impossible Fist's through-wall melee reach is not yet implemented, and its
  momentum-based shockwave needs real game testing.
- 238 ability entries remain unimplemented across 12 individual pathways
  and 6 Resonance pairs, excluding unresolved exactness gaps in authored kits.
