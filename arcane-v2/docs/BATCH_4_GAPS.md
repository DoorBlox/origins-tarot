# Batch 4 - deliberate approximations and remaining engineering gaps

All 39 new power JSONs have native Java handler coverage or the explicit
approximation below. `origins:simple` is a valid marker for a server-native
event ability, not proof of exact mechanics.

- Hermit +35% XP is applied at PlayerEntity.addExperience() with fractional
  accounting. The 'cave bonus' clause is not quantified by the handbook;
  no additional undocumented cave multiplier was invented.
- The Hermit Forbidden Insight +5% enchanting power is currently replaced
  by an on-condition Luck I approximation. It does NOT modify real
  enchanting-table effective power.
- Hermit Sage's Counsel has an underspecified arbitrary yes/no structure
  question. The prototype returns a bounded Yes/No oracle and a brief Luck
  effect; it is not a proper structure index or LLM response.
- Emperor's Library copies no item enchantments yet; its +50% arrow attack
  window is native and active for 300t. Copying enchantments without
  permanently altering gear needs a safe overlay implementation.
- Hermit The Unseen and Burning Archive critical arrows double raw damage;
  they do not bypass vanilla armor fully. Structure reveal is approximate
  region intel in chat, not an indexed structure HUD.
- Chariot Trail of Embers emits Flame particles and ignites enemies only
  when valid targets are in the trail. Test client synchronization.
- Taunt can retarget hostile AI mobs, but cannot force a human enemy player
  to attack a chosen target. Enemy players are visually marked instead.
- Storm Call is LOCAL particles/Slowness, not a true local rain biome/weather
  volume. Vanilla weather is global; a dedicated client/weather protocol
  would be required to represent a 20-block local storm exactly.
- Meteor uses safe forward teleport through air, rather than a smoothly
  animated immune dash; temporary immunity is server-controlled for 5t.
- The Battlefield and Burning Archive can compel vanilla hostile mobs
  to retarget, but not manipulate human PvP aggro or remote modded AI
  exactly. Enemy players receive Glow without forced attacks.
- Burning Archive critical-arrow radius ignition and Burn-stacks have
  server-side native logic but still need a live combat acceptance test.
- There are 317 remaining ability entries across 14 individual pathways
  and 7 Resonance pairs; these are NOT implemented in this development jar.
