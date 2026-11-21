# Batch 10 — native approximation and safety gaps

Source: Rev2 Sun (§XIX), Moon (§XVIII), Eclipse (§IX). Rev3 controls
slot transitions and Sequence-1 full Resonance activation.

- Sun's Inner Light, Radiance, White Angel and Eternal Day use particle
  illumination and Night Vision, not world block-light level8/15. A
  reversible, claim-aware dynamic light implementation is needed.
- Sun's 'no hostile spawns' tries to suppress newly spawned tagged hostile
  mobs in its domain through short-age detection. It is not an actual
  pre-spawn event cancellation. Existing mobs are not discarded.
- Rev2 explicitly says **all players** gain Regeneration I in some Sun
  abilities, while the handbook's global targeting convention restricts
  beneficial ally effects to same-team players. This version applies
  regeneration to self/same-team only (safety tiebreak).
- Moon Blood Diet is enforced using before/after vanilla eatFood hunger
  snapshots. It does not suppress effects like potion status or golden
  apple absorption; special modded foods need manual validation.
- Pharmacist and Scarlet recognize vanilla drinkable instant-health potions
  via a short consumption window. Splash and lingering healing source
  attribution, plus other healing during the same window, need an exact
  source-aware hook.
- Tame uses brief Slowness/navigation intervention rather than a genuine
  1200t no-flee AI goal. Summon uses a bounded owner-tagged Vex proxy, not
  a full cloned passive mob with combat AI.
- Brew manipulates vanilla BrewingStandBlockEntity BrewTime through its
  NBT round-trip and only while a reaction is underway; this must be
  tested on 1.18.2 to verify timer persistence and recipe safety.
- Life revives one new entity of the deceased passive type with an owner
  tag. NBT traits (color/genetics/tame owner) are not cloned, and the
  revived entity is not guaranteed to fight as an ally.
- Moonshadow 5-block night wall vision and Sun phasing-like lighting
  lack client-side rendering support; they are not functionally exact.
- Eclipse overlapping undead double-loot is not implemented. Loot table
  interception with source identity and safe per-kill duplication is needed.
- Eclipse healing is capped to **30HP total distributed** across self and
  team for one capstone activation. Rev2's cap30 wording does not specify
  per player versus total; this is a conservative cap.
- Rev2 'Sun all players Regen' versus global same-team ally rule is flagged
  above; all hostile/offensive effects still target tagged hostile mobs
  **AND enemy players** and never same-team players.
- The 355/434 named resource count is a SOURCE count: 79 named ability
  resources across four individual pathways and two resonances still
  missing; runtime acceptance is not completed for earlier sources either.
