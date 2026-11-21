# Batch 8 implementation gaps / approximations

Rev2 Part A Devil/Judgement and Part B Binding Contract govern ability
mechanics. Rev3 governs paired unlock at Seq4, kit slots Seq4–2, and
automatic full Resonance suite at Seq1.

- Sacred Rejection's half-healing currently detects starting a vanilla
  drinkable healing potion. It halves healing during a 60t window, but
  does not identify a splash/lingering potion or third-party effect source.
  Other healing inside that window may also be reduced. Exact behavior
  needs an effect-source scoped instant-health hook.
- No Unlawful Escape blocks vanilla right-click ender pearls and chorus
  fruit; other mods/commands may teleport unless separately intercepted.
- Blather can redirect MobEntity targets but cannot force PvP clients
  to choose a new opponent. Applying brief Nausea is a player fallback.
- Judgement Posse reports target vector privately; no bespoke direction HUD
  or accurate dimension-crossing map exists.
- Verdict's Weight 'flee' uses stop-target + Slowness, not a dedicated flee
  AI goal. Same for no_spawn decree: current No Spawn pacifies hostile mobs
  rather than preventing world spawning; do NOT claim exact prevention.
- Chaos Hunter +10% vs hostile mobs attacking another player is native;
  detection of an enemy player's intended target is still approximate.
- 'Stun' for Discipline/Order uses very high Slowness (255) rather than
  client-input immobilization, so attacking/jumping may still be possible.
- Contract Enforcement acceptance buffs are unspecified in Rev2. The
  fallback grants both players temporary Regeneration I and Resistance I;
  refusal removes one held item and applies Weakness II ONLY on explicit
  '/tarot contract refuse'. Non-response has no penalty.
- Binding capstone 'frozen' opponents use very high Slowness and server
  sprint/jump restriction for enemy players. A client control mod would be
  needed for perfect stasis.
- Binding capstone Wither-kill attribution tracks recent targets, and
  can credit an unattributed death within the 40–100t window that was
  actually caused by another hazard. Exact source-death classification
  still requires a dedicated damage-source tracker.
- Minions are bounded owner-tagged Vexes lasting600t, not bespoke demon
  models or custom AI. They are cleaned on owner death/disconnect.
- Other capstone weapon effects and anti-spawn semantics must be tested on
  a real multiplayer world; status JSON alone is not proof.
- 159 additional named entries remain after Batch8 (eight individual
  Arcana and four Resonances). Native mechanics across all authored
  groups remain subject to source-fidelity and client QA audits.
