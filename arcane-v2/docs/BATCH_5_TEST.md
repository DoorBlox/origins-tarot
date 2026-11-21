# Batch 5: Death + Tower + Crumbling Reaper — manual acceptance

Target Minecraft 1.18.2 + Fabric API + Origins 1.4.1 + native Arcane V2.
**All boxes below are UNTESTED in a real world.** Gradle/JUnit and headless
server startup do not verify player PvP, nether portal geometry, or block behavior.

- [ ] Choose Death Seq 9; confirm Severed Vitality *permanently* disables natural hunger-based health regeneration while potions and direct heals still work.
- [ ] Soul Harvest: a hostile mob OR enemy player kill heals 2 HP, with 200t cooldown; teammates not treated as targets.
- [ ] Grave Affinity: −25% damage from `#tarot:undead`, night/low-light vision; Rev2 Grave Whisper extra 10% drop behavior verified against actual loot tables.
- [ ] Reaper's Touch: undead hit gives Weakness I for 60t with 200t cooldown.
- [ ] Death Seq 8: right-click skull/grave for 1 XP, 1200t cooldown.
- [ ] Death Seq 7: crouch 60t and reveal undead within 10 blocks with 100t Glowing, cooldown600.
- [ ] Death Seq 6: an undead death within 8 blocks from ANY source heals 1 HP, cooldown20.
- [ ] Death Seq 5: bind secondary `gate`, create framed 4x5 Nether portal into empty, grounded space; cannot overwrite existing blocks or create portals in the End; CD12000.
- [ ] Death Seq 4: 5% chance to survive lethal damage at 2 HP with 12000t CD.
- [ ] Death Seq 3: right-click water: Dolphin's Grace approximation 100t; actual water-walking is NOT implemented.
- [ ] Death Seq 2: bind `consul`: a bounded allied Vex substitute lasts 200t, CD6000; NOT a converted undead mob.
- [ ] Death Seq 1, normally skipped by automatic Resonance: `reap` kills hostile mobs/enemy players below 30% health within 8 blocks, CD2400; no friendly fire.
- [ ] Death Seq 0, normally skipped by automatic Resonance: `the_final_harvest` 600t/24000t, every 60t nearest weakest enemy in 10 blocks gets execution damage; bosses/enemy players lose ≤50% current HP per pulse.
- [ ] Each *confirmed* capstone kill grants +1 Absorption heart; track 10-heart cap and 1200t expiration precisely (remaining limitation below).
- [ ] Choose Tower Seq 9: explosives deal −60% damage; 30% faster stone mining with Cracked Foundations; +75% fall damage and assess +20% knockback drawback (not yet exact).
- [ ] Unstable Strike hits hostile mobs/enemy players with Slowness I 20t (40t at Seq4); 260t cooldown.
- [ ] Unstable Ground 5% chance triggers crack particles on stone mining.
- [ ] Tower Seq 8 crouch-right-click stone to prime an isolated charge; block breaks after 60t, CD600; no overwriting unrelated protected blocks.
- [ ] Tower Seq 7 Fault Line 5% chance of breaking stone immediately above newly broken stone.
- [ ] Tower Seq 6 holding a pickaxe reduces falling damage 20%.
- [ ] Tower Seq 5 bind secondary `collapse` for 3x3 stone breaking without touching protected blocks; CD1200.
- [ ] Tower Seq 3 Shockwave triggers on a 4+ block fall, deals 2 HP to nearby *enemies* in 3 blocks; no allies.
- [ ] Tower Seq 2 Cataclysm gives Mining Fatigue I 200t to hostiles/enemy players in 5 blocks, CD3600.
- [ ] Tower Seq 1 Falling Tower primary leap/slam approximation deals 10 damage and Slowness II 100t to hostiles/enemy players within 6 blocks; CD2400.
- [ ] Tower Seq 0 The Fall duration 600t, CD24000: ground within15 blocks deals **4 damage/second to ANY grounded entity (including owner AND allies)**, then hostile mobs/enemy players are tossed up.
- [ ] Advance Death or Tower from 5 → 4: both identity drawbacks remain active irrespective of slotted kits. Verify slot swap/clear/auto and relog.
- [ ] Advance from 2 → 1: all individual Sequence kits revoked and all ten Crumbling Reaper powers, Sequence9 through0, granted automatically.
- [ ] Crumbling Reaper Seq9 Grave Ruin combines 30% stone break, undead−25%, explosion−60%, and fall+75%.
- [ ] Seq8 Grave Dirt + Fault Line both work.
- [ ] Seq7 Spirit Shockwave detects undead and triggers shockwave on 4+ block fall.
- [ ] Seq6 Guide's Foundation includes undead death within8 and pickaxe falling damage−20%.
- [ ] Seq5 Gate Collapse creates safe Nether portal plus 3x3 stone break, cooldown12000.
- [ ] Seq4 Falling Harvest: after 3+ block fall, next hostile kill within200t heals 4 hearts and does 2 HP blast within3.
- [ ] Seq3 Collapse of the Living: nearby enemy death within8 triggers 1 damage to other enemies within3.
- [ ] Seq2 Unstable Souls: fall damage splashes equal damage to enemies; kills heal2 HP (approximate Soul Harvest).
- [ ] Seq1 Falling Tower's Reap: bind primary `falling_towers_reap`; 6-block
  impact zone launches and hurts enemies, executes those below20%, grants
  1 Absorption heart for confirmed kills, 600t duration and 2400t cooldown;
  the exact 8-block leap/ground-impact timing remains approximate.
- [ ] Seq0 Crumbling Reaper: 600t/24000t, 60t periodic harvesting, 15-block unstable ground, +1 Absorption heart per kill cap15 and 1200t duration; test bosses, enemy players, owner and ally interactions.
- [ ] Test every skill after death/reconnect/dimension change, under mixed Origin combinations and server restarts; confirm temporary effects and granted powers are revoked.
- [ ] Back up world before terrain-changing abilities and collect server logs for any mixin crash or unexpected deletion.

Do NOT invite friends on the assumption this checklist passed.
