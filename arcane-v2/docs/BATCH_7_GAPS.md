# Batch 7 — remaining fidelity gaps and safety

- Decree of the Sovereign currently grants short Hero of the Village near
  villagers, a **trade-discount approximation** and not exact 10%.
- Crouch-right-click crop uses CropBlock native growth and per-location
  cooldown. External claim/protection plugins must independently authorize
  block modification; no generic anti-grief claim API exists in Fabric.
- Linked Hearts uses a source-specific movement-speed attribute modifier
  applied to non-Tarot allies by a server-wide tick; stacking with other
  speed mods, owner logout and mixed Teams require multiplayer testing.
- Emperor Coin pacification cancels target's damage to this owner only;
  player attacks against other parties are not blocked. Human targeting
  cannot be forced by Decree; it is approximated with Glow/Slowness.
- Entropy Field is auto-triggered on projectile damage in5 rather than an
  explicit unspecified input key. It protects entities within the field.
- Separation Anxiety detects *any* other player within8 as companionship,
  instead of interpreting 'alone' as away from only same-team players.
- Symbiosis grants temporary +1 maximum HP via attribute; fused 6 applies
  it to same-team nearby players. Exact food/heal effects under extreme
  stat modifiers remain to be tested.
- Nature's Step heals and regenerates allies, but **does not implement
  walking through leaves yet**. Exact client collision/phase needs a
  client-side extension or safely sourced Origins phasing power.
- Domain movement restrictions use native player sprint flag and jump
  intercept; other mods' custom movement, flying, mounts and knockback
  are not necessarily disabled.
- The Garden pacification of hostile mobs uses vanilla target reset and
  navigation stop; some modded AI may immediately reacquire a target.
  Enemy players receive temporary damage-interception until challenged.
- Fused capstone consort damage/resistance bonuses are server-side; a
  dedicated consort HUD/particles are not implemented.
- The Garden and Benevolent Crown protect passive mobs via universal
  damage intercept. This may affect modded passive entities in the tag,
  but only within the active radius.
- Timed domain state is transient in RAM and removed on disconnect, death,
  origin switch or restart. Domain cooldowns and progression are persisted.
- 199 additional ability entries remain in 10 individual Arcana and five
  Resonances. Even the 235 named resources include source approximations.
