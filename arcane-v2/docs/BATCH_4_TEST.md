# Batch 4 - Hermit, Chariot and Burning Archive acceptance (no KubeJS)

This is a **manual test checklist**; none of these are marked PASS merely
because Java compilation or Fabric headless startup succeeded.

- [ ] Select Hermit at Seq 9: default 9 kit, plus permanent Forbidden Knowledge and Elytra wings.
- [ ] Earn exactly 35% more vanilla XP through orb pickup, including fractional progression; compare identical XP sources without double-counting administrative XP.
- [ ] Hold book/clock in offhand: break speed +20%; remove: returns to baseline.
- [ ] At XP level 30+, without book in offhand, Mining Fatigue I is applied; with book, it clears after short effect expiry.
- [ ] In low light, Astral Calculation grants Night Vision and projectile damage +20% against hostile mobs AND enemy players, not teammates.
- [ ] Take damage until Combat Insight gives Resistance I 40t about 20% of events.
- [ ] Crouch-right-click hostile mob/enemy player with Hex: Weakness I 60t and 600t cooldown.
- [ ] Crouch-right-click a block holding paper at Hermit Seq 6: paper NBT contains TarotRecallX/Y/Z.
- [ ] At night, bind V to star_read; names/health of hostiles and enemy players within 15 are revealed privately, glowing 100t and 1200t cooldown.
- [ ] At level 30+ with offhand book, Forbidden Insight *approximation* Luck I appears; true +5% enchantment table power is not yet implemented.
- [ ] Under mob pursuit, Omen occasionally grants Speed I 60t (polling approximation).
- [ ] Bind Sage's Counsel: source specifies a yes/no structure question; current limited oracle approximation reports yes/no with 6000t cooldown; do not mistake it for structure location.
- [ ] Hermit Seq 1 Emperor's Library: G enables 300t +50% arrow modifier and 3600t cooldown. True enchantment-copy effect is marked approximate.
- [ ] Hermit Seq 0 The Unseen: G activates 900t/24000t, Night Vision, glowing players within 100, private coordinates, and a one-shot 2x arrow.
- [ ] Select Chariot Seq 9: sprinting melee +15%; hostile kill Speed I 160t cooldown360.
- [ ] Fire/lava damage immune and Strength I when burning; while raining/underwater permanent Extinguished Fury causes Weakness I + Mining Fatigue I.
- [ ] Sprint trail ignites only hostile mobs and enemy players, not teammates, for 40t, cooldown300.
- [ ] At Seq 8 crouch-right-click enemy Taunt: mob switches target to you, enemy player receives Glowing I (approximation).
- [ ] At Seq 7 Flame Burst also ignites targets when trail Seq 9 is unslotted.
- [ ] At Seq 6 Plot 20% chance on kill grants +1 XP level.
- [ ] At Seq 5 bind V to Reap: next melee within 100t gets +30%, CD600.
- [ ] Seq 4 Iron Skin grants +1 armor below 12 HP, removed when health restored.
- [ ] Seq 3 Rally grants Speed I 100t to self and same-team players within 8 on kill, CD600.
- [ ] Seq 2 Storm Call approximates local rain via particles and Slowness within 20, 600t duration, CD6000; world rain weather does NOT change.
- [ ] Seq 1 Meteor G dashes up to 15 safe blocks, ignites enemies in 3-block path for 100t, grants short damage immunity, CD2400.
- [ ] Seq 1 Burning Wrath +20% melee when on fire.
- [ ] Seq 0 The Battlefield G lasts 900t, CD18000: +30% damage, +20% speed, on-hit ignite100, enemy mobs may retarget other hostiles and enemy players are visually marked.
- [ ] Reach Seq4 using /tarot ascend or OP /tarot debug sequence 4: Hermit and Chariot identity drawbacks both remain permanent even with no sequence kit from a parent slotted.
- [ ] At Seq1 all individual kits revoked and all 10 Burning Archive Resonance kits automatically granted.
- [ ] Seq9 Scholar's Fire: +35% XP, fire immunity, +15% sprinting melee.
- [ ] Seq8 Combat Insight: on damage 20% Resistance I + Speed I, 40t.
- [ ] Seq7 Astrologer's Trail: star coordinates and ignition for hostile mobs and enemy players.
- [ ] Seq6 Recorded Plot: scroll coordinates and 20% kill → +1 XP.
- [ ] Seq5 Star Read Reaper: V reveals enemy health for 5s and primes +30% melee and 60t ignition with 600t cooldown.
- [ ] Seq4 Scholar's Momentum: reading book triggers +25% sprinting melee for 1200t; not active before reading.
- [ ] Seq3 Insightful Flame: trail applies +1 damage, Slowness I 40t and enemy health reveal.
- [ ] Seq2 Reaper's Library: kill grants XP + Burn stack (+5% melee, max3), consumed on crit.
- [ ] Seq1 Burning Lecture: G enables 300t arrow +50%, melee ignition100t, arrows ignition60t, CD3600.
- [ ] Seq0 Burning Archive G: 900t 24000t CD, player outline within100, region intel, one 2x arrow, mob-versus-mob retargeting within20, +30% damage and +20% speed, melee ignition, up to5 Burn stacks, crit-arrow AoE ignition10, end burst when5 stacks.
- [ ] Repeat offensive tests with unteamed enemy players, enemy-team players and teammates; only tagged hostiles and enemy players may be harmed.
- [ ] Test death, disconnect, crash recovery, dimension transfer and relog while Storm Call, Reap, and capstone are active.
- [ ] Verify /tarot status and /tarot ascend with non-OP players still work and never give two parallel sequence tracks.
- [ ] Record Minecraft/Fabric/Origins versions, exact commit, full log and reproduction for failures.

Do not invite friends before real-world gameplay acceptance.
