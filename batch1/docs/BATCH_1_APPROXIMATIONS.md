# Batch 1 approximations / VERSION CONCERNS

The executable files are **best-effort** server-side code, not runtime-verified substitutes for Rev2.

| Ability | Implemented server-side approximation / missing detail |
|---|---|
| Full Faceless Disguise | Invisibility + chosen online-player identity hint, not actual skin/name/model swap. Requires client mod. |
| Borrowed Face | Nearby-player identity hint and invisibility; not true model/name copying. |
| Trickster's Favor | Throttled 10-tick mob aggro polling, not literal LivingChangeTargetEvent on Fabric. |
| Stage Magician | Air-only block teleport + temporary marker decoy; validate collision/headspace. |
| Clown's Mischief | KubeJS script instead of pure [D] JSON to filter same-team attackers. |
| Puppet String | Weakness I approximates next mob attack at -50%; player no-sprint uses server tick. |
| Fools' Gathering | Two NoAI Vex projections follow owner and inflict 1 HP via script, without true minion AI. |
| History Substitution | Cancellation of lethal entity.hurt events requires real loader check; destination checks are not collision-complete. |
| Paper Figurine | Marker decoy, not player-shaped decoy; never cancels lethal damage. |
| Legend of the Fool | Resistance IV roughly 80% instead of exact -75%; Strength I is not an exact +50% final-damage modifier. |
| Legend's double loot | Exact entity-loot-table duplication not yet implemented. Generic death callbacks are insufficient to duplicate exact drops safely. |
| Legend rewind | Coordinates saved on server; dimension transitions and exact food/saturation need verification. |
| Elytra expenditure | Vanilla Elytra has zero exhaustion; test pack defines 0.02/tick baseline plus +25% = 0.025/tick. |
| Overlapping active keys | /tarot bind selects which script is used; Origins HUD itself may show only native 1-tick dispatch cooldown. |
| Java event/hooks | Verify 1802.5.5 event names, potionEffects, AABB.of, getEntitiesWithin, effect cancellation, scheduleInTicks, updateAbilities, player data methods. |

Team safety: When entity scanning fails, no target is chosen. This is safer than blindly affecting teammates.
