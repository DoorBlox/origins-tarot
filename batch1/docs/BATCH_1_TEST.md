# Batch 1 Minecraft acceptance checklist — all NOT RUN

- [ ] Server starts without unknown KubeJS event IDs or invalid Apoli power types.
- [ ] Only Fool appears in the isolated test pack selection screen.
- [ ] Fool's powers array includes only origin marker, permanent +25% exhaustion drawback, and identity glider.
- [ ] Seq9 gives 4 powers from **tarot_slot** source, and /tarot slots shows 1/1.
- [ ] Sneak+V Spirit Vision outlines ALL nearby entities for 40 ticks, cooldown 100 ticks.
- [ ] Test Clown's Mischief 20% chance, 100-tick cooldown; friendly players are not affected.
- [ ] 3 hostiles or one ENEMY player within 8 blocks triggers Nausea; teammates do not.
- [ ] G Faceless camouflage activates for 2400–2880 ticks and cancels on combat.
- [ ] Debug Seq8 Trickster retarget works, Seq7 escape + decoy works, Seq6 Borrowed Face timer works, Seq5 Puppet String works on mobs and enemy players, excluding allies.
- [ ] Seq5→4 retains Fool Seq9–5, gives slot6 EMPTY.
- [ ] /tarot slot 6 tarot:fool 4 grants Seq4; /tarot slot 6 clear revokes Seq4.
- [ ] /tarot slot swap 1 6, /tarot slot auto, /tarot reset work without duplicates.
- [ ] Locked sequence, duplicate, invalid index, unimplemented Hanged Man, another player's slots cannot be edited.
- [ ] Seq4→3 adds empty 7th slot; Seq3→2 adds empty 8th slot.
- [ ] Golden Apple grants Speed for 100 ticks at Seq3; Fools Gathering produces 2 safe short-lived projections at Seq2.
- [ ] Seq2→1 fails CLOSED until Batch2; does not destroy existing powers.
- [ ] Relog/respawn/dimension change restores sources, preserves Sequence and slot assignments.
- [ ] No periodic revoke/re-grant every 20 ticks (cooldowns remain usable).
- [ ] Removing the Fool origin clears slot-granted powers without touching unrelated mod powers.
- [ ] 25% sprint hunger surcharge and gliding surcharge are observable.
- [ ] Test damage cancellation and temporary capstone only via isolated OP power grants, not regular progression.
- [ ] Both same-team and enemy-team PVP targeting are correct, no ally debuffs.
- [ ] Verify world backup/rollback before live deployment.

**Not marked passed**: this assistant cannot launch the real Minecraft client/server.
