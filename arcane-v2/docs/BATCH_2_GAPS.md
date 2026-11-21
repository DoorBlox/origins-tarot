# Batch 2 — known deltas versus Rev 2 / Rev 3

**Delivery status:** source implementation; Java compilation and JUnit tests
are separate from live in-game acceptance.

- Hanged Man Shadow of Degeneration has the light-gated Resistance and movement bonus. The specified silent footsteps still require client sound suppression.
- Shadow Whisper uses polling and limits hostile mob target range; a precisely 30% smaller detection radius across all AI implementations is not guaranteed.
- Weight of Sin uses a HungerManager natural-regeneration redirect, potion-consumption listener, and stationary darkness timer. Vanilla/mixin compatibility must be confirmed in Minecraft 1.18.2.
- Trinity tracks three distinct `DamageSource.getName()` values over 100 ticks. This is an approximate representation of 'three damage sources'.
- Sin accumulation is measured as actual health and absorption lost during each damage event; effects triggered by canceled damage do not generate Sin.
- Hanged Man Dark Blade and native capstone use mixin scaling for damage. The manifest's 15-block explosion is entity-only, never destructive to the world.
- Hanged Man's kill-triggered 'fallen enemies rise as minions' is only partially implemented; summoned allies are bounded Vex-like fighters rather than custom models.
- Paper Martyr decoys are invisible tagged armor stands, not client-side paper figurines. A model/texture mod is required for the exact appearance.
- Paper Martyr's Suffering Sight uses chat health/debuff information, without a custom client health-bar overlay.
- Borrowed Sacrifice uses invisibility instead of a rendered borrowed identity.
- Paper Martyr's Sin shadow detonation and summoned minion explosion use tagged entity damage interceptors. These are untested in a real Minecraft server.
- The exact protection against other mod-owned flight during disconnect/restart is not yet established; avoid production use.
- Handbooks do not define a standalone Acting economy. A new native bridge reuses earlier V3 item/kill/trade Acting, online cooldowns, altar and offerings for /tarot ascend, progressing one shared Sequence. This is an adaptation requiring live-world validation.
- The remaining 20 pathways and 10 Resonance pairs have not been ported. **Do not present this build as all 434 abilities completed.**

No KubeJS code or KubeJS dependency is included in this Arcane V2 runtime.
