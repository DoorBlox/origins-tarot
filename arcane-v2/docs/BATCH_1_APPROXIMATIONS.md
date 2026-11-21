# Arcane V2 — current approximations, not exact Rev 2 mechanics

An approximation is **not** a faithful implementation. Do not infer full behavior from a
power JSON containing `origins:simple`; these are identity descriptors whose gameplay
must be provided by native Java handlers.

| Ability | Current behavior / missing detail |
|---|---|
| Spiritual Expenditure | Native mixin multiplies exhaustion while sprinting or gliding by 1.25; some unrelated exhaustion in those movement states also receives the multiplier. Precise action attribution needs a narrower injection. |
| Full Faceless Disguise | Server-only invisibility approximation; real random-online-player name, skin and model require client-side identity rendering and packet synchronization. |
| Borrowed Face | Server-only invisibility approximation; true name swap, exact end-of-disguise Speed II, and client-visible profile replacement not yet implemented. |
| Puppet String | Slowness II applies to hostile mobs and enemy players; coordinates are shown immediately, but 100-tick coordinate visibility, exact player sprint denial and mob next-hit half-damage are not yet exact. |
| Stage Magician | Backward teleport and decoy are implemented in native damage callback; safe-location checks and decoy expiry are not yet verified. |
| Trickster's Escape | Low-health Speed II and decoy implemented; decoy expiry and anti-loop controls require game acceptance. |
| Spiritual Overload | Uses nearby vanilla hostile class, not all custom `#tarot:hostile` tag entries. |
| Clown's Mischief | Damage callback approximation, rather than specific attack-only trigger conditions. |
| Paper Figurine Substitute | 25% damage callback approximation; attacker hostility qualification is not yet enforced. |
| Fool's Bounty | +20% food via player mixin, with fractional accumulation; potion/food specifics require live verification. |
| History Substitution | Lethal-damage event and teleport; safe destination, timing, and cancellation need live tests. |
| Spirit Vision | All nearby living entities glow; exact all-entities including nonliving needs adjustment. |

Unimplemented abilities are recorded in BATCH_1_BLOCKED.md, not counted as complete.
