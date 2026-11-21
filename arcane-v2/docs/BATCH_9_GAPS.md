# Batch 9 — approximations and missing dependencies

The Rev2 Star/Empress/Starless Poison mechanics are preserved as reference;
Rev3 overrides only sequence progression, slots and activation timing.

- True Sleeplessness bed interception is native and should set spawn via
  ServerPlayerEntity.setSpawnPoint. Vanilla phantom spawn delay remains 3 days
  unless a dedicated phantom-spawner hook implements 5 days / 7 days.
- Sleepless shortened Blindness/Darkness duration is currently not exact.
  Night Vision is active, but custom-duration interception is missing.
- Witch's Grace Poison immunity is implemented by removing poison each server
  ability tick (20t), not cancelling every poison application at inception.
- Mirror Veil uses server Invisibility but cannot hide/render armor according
  to the Rev2 render_armor client presentation without client-side rendering.
- Whisper moves passive mobs toward a different player with navigation and
  Speed, not a hostile attack goal (passive mobs lack target combat AI).
- Terror and Aura of Despair use clear MobEntity target/Slowness; human PvP
  opponents cannot be forced to flee.
- Starless Sky / Midnight Apocalypse / Starless Poison **do not permanently
  break or remove nearby light sources**. Darkness is suggested using smoke,
  blindness and particles to avoid griefing in the development SMP. A reversible,
  claim-aware temporary block light manager would be required for exactness.
- Apocalypse meteors use bounded damage/particles on nearby enemies, no
  terrain destruction or physical flying meteor model. The 5 impacts occur
  at scheduler ticks ~0,40,80,120,160.
- Empress Exposed Reflection applies +25% incoming projectile damage in direct
  sunlight as a permanent identity penalty, independent of slotted kit state.
- Mirror Passage permits safe teleport past glass without destroying blocks,
  but is not client-side animated phasing. Protection/land-claim enforcement
  requires separate integration.
- Mirror World temporary free flight is server-authoritative; persistent
  restore markers support crash recovery, but no live flight/desync acceptance
  exists. Its exact 'exit anywhere within30' is approximated by a manual
  /tarot mirror exit command and safe-return condition.
- Poison Conceal's attack-tracking/reveal timing is approximate without
  a client-side invisibility-cancellation event.
- Poisoned cloud on capstone kills is visual + Poison effects (no custom
  persistent area-effect cloud entity).
- The 315/434 resource count is NOT 315 proven-complete abilities: 119
  named resources remain, plus exactness gaps from all prior batches.
