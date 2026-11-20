> **V2 ALPHA:** the buffs and drawbacks in `passive_v2.py` are now built by `generate.py`. The document below describes general design intent; verify actual generated JSON and test food restrictions, visibility, villagers, night exposure, hunger and defensive effects. Do not claim that unimplemented soul links or lunar-cycle checks are shipped.

# Gameplay balance, limitations, and acceptance plan

## Philosophy
All 22 Major Arcana should create **different gameplay decisions**. Every card has G/V actions, passive benefits and explicit drawbacks. High mobility is compensated by reduced health, increased damage taken, dependence on a context or reduced direct damage. The 18 winged cards use vanilla-style Elytra gliding rather than creative flight.

## Important multiplayer rules
- **Friendly fire is a design cost.** Current AoE effects don't discriminate between allies and enemies unless a specific power says otherwise.
- Healing can support enemies, while poisons and debuffs may hit friendly entities, pets and villagers. Test in a controlled arena before using in a town or hub.
- PvP balance is **provisional**. Short ability durations, cooldowns and hunger costs aim to avoid permanent dominance, not to guarantee tournament fairness.
- Players with no built-in Elytra (Emperor, Hierophant, Strength, Judgement) receive generally stronger grounded defenses/control or XP specialization; make sure limited mobility suits your server culture.
- Effects persist only for their documented durations. No new client-only particle textures, models or visual spells are included.
- This pack modifies *origins abilities*; it does not regulate player equipment, enchantments, totems, potions, or extra mods. Those can strongly change balance.

## Acceptance checklist (manual, **NOT YET RUN**)
1. **Compatibility:** load the two variants separately under the exact Fabric/Origins versions; watch every startup log for JSON and power errors.
2. **Selection:** each variant offers exactly the intended 22 cards; confirm add-on vs replace layer.
3. **Controls:** pick all 22 cards, press G and V, verify action output, cooldowns, hunger and hotbar rendering.
4. **Gliding:** test with and without chest armor, after death/relog and in each dimension; ensure four grounded cards cannot glide automatically.
5. **Area effects:** test owner, ally player, enemy player, tame pet and villager for every AoE.
6. **Biome/daylight:** verify sunlight conditions at daytime, midnight, underwater, covered by blocks, Nether and End.
7. **Resource stress:** multiple players trigger abilities while pregeneration is running; check for server exceptions and TPS changes.
8. **World lifecycle:** save, restart, reconnect, die, respawn and change dimensions. Confirm no permanent effect bugs or origin loss.
9. **Edge cases:** target behind walls, different heights, edge-of-range targets, full-health targets, empty hunger, flight launch near water.
10. **Regression:** install alongside your current gameplay mods and verify KubeJS recipes, existing custom powers and other datapacks still work.

## Balance feedback format
Card | context (PvP/PvE/building/exploration) | estimated player skill | action used | expected result | observed result | exact mod versions | server logs | suggested change.

## Candidate directions for v0.2
These are **ideas**, not features implemented in v0.1:
- Mercy-aware party-targeting or friendly-fire configuration for Justice/Hierophant/Lovers.
- Better visual distinctions for the 18 winged cards using an *optional* client resource pack.
- Additional ritualistic, non-combat powers and synergy mechanics that don't reward raw PvP damage.
- Multi-stage "Beyonder" progression and corruption risks rather than fixed origin loadouts.
- Advanced features such as Fool's autonomous marionettes would require scripts or a compatible mod; don't mislabel basic debuffs as true puppet control.
