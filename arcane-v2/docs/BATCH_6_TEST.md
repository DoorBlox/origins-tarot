# Batch 6: Magician + Strength + Impossible Fist manual acceptance

Target Minecraft Java 1.18.2, Fabric API 0.76.0, Origins 1.4.1, and
**the exact-head native Arcane V2 JAR**. All boxes remain UNVERIFIED in
live gameplay even if Gradle and the server-start smoke test pass.

- [ ] Select Magician: Elytra-style gliding is available; Full Moon Ravings applies Nausea I for 100t under exposed sky every 1200t (identity persists at Seq4 for Strength-primary players).
- [ ] Sequence9 Traveler's Body +12% movement; fall damage −70%; Wayfarer's Instinct makes jumps 20% higher outside water.
- [ ] Threshold Step: 20% of falls cancel damage, attempt a safe 2-block horizontal relocation, and share 100t cooldown with Seq8 Sleight of Hand (30%).
- [ ] Seq7 Star Chart (V+sneak at night) draws particles 100t cooldown1200; **visual only, does not locate a true structure yet**.
- [ ] Seq6 Recorded Step: crouch-right-click block stores a location, second click within1200t teleports back within30 blocks; cannot teleport into solid blocks. Test cross-dimensional attempts.
- [ ] Seq5 Doorstep V: teleport toward gaze 8 blocks, selecting safe non-solid destination; cooldown300.
- [ ] Seq4 Sealed Room: successful fall-save additionally Blinds enemies within3 blocks for20t.
- [ ] Seq3 Shortcut: 10% chance on block break attempts an opposite-block break, subject to vanilla build permissions; test claims and protected blocks separately.
- [ ] Seq2 Planar Step: V exits behind up to4 solid blocks if it finds safe space, cooldown3600.
- [ ] Seq1 Waypoint and Astral Lock are packaged markers **without complete mechanics**; do not mark functional.
- [ ] Seq0 All Paths Converge: G activates900t, CD18000. Experimental server-side noClip phasing blocks `#tarot:unphasable`, blocks break/place need stricter restrictions, and the player must return to safe air on expiry/disconnect.
- [ ] Select Strength: **no Elytra**, permanent Giant Sinks swim speed penalty and bow/crossbow restriction. Verify Seq7 Master's Grip lifts restriction with −25% bow damage.
- [ ] Seq9 Giant's Grip +18% armed melee and +55% KB resistance, Quarry Hands +35% stone mining, Steel Frame +2 armor.
- [ ] Seq9 Grounded Slam from ≥3 blocks arms next melee within100t for +10% and Slowness I 20t.
- [ ] Seq8 Iron Fist gives +2 flat damage when unarmed; does not double-count Giant's Grip.
- [ ] Seq6 Dawnlight crouch60t emits short-lived light-like particles + Night Vision200t; exact block-light level8 is pending.
- [ ] Seq5 Bulwark V: 100t incoming −30% and Slowness255 to prevent walking, cooldown2400; confirm attack/knockback handling.
- [ ] Seq4 Hunter's Bane +15% against undead; demon-tag targeting still needs verification.
- [ ] Seq3 Silver Blade armor bypass is a **known missing exact mechanic**.
- [ ] Seq2 Twilight Blade: once each3600t next melee inflicts Slowness II + Weakness I 100t.
- [ ] Seq1 Divine Hand: G pulls a hostile mob/enemy player within15, applies a 60t severe Slow, next melee +50%; cooldown1800.
- [ ] Seq1 Unyielding below8 HP: knockback resistance reaches 100%.
- [ ] Seq0 Giant's Decay G: 600t/24000t, 15-block enemy Wither II + Slowness II, +30% damage against affected; exact armor halving pending.
- [ ] Advance primary Magician or Strength from5→4: second identity drawback applies permanently even with no slotted kit from partner.
- [ ] At Seq1 the individual kits are fully revoked and all ten Impossible Fist 9→0 kits activate, even the Seq0 capstone.
- [ ] Impossible Fist Seq9 Traveler's Might: +12% speed, −70% fall damage, +3 armor, +20% jump.
- [ ] Seq8 Sleight of Fist: fall-saving 30% chance and +2 unarmed.
- [ ] Seq7 Star Chart Grip: star particles, bows permitted but bow damage−25% still to validate.
- [ ] Seq6 Recorded Dawnlight: Recorded Step and Dawnlight approximations.
- [ ] Seq5 Doorstep Slam: safe8-block blink then next melee +10% and Slowness I 20t, 60t window, CD300.
- [ ] Seq4 Doorstep Punch raises that unarmed bonus to15%.
- [ ] Seq3 Sealed Slam: V teleports adjacent to hostile or enemy player, deals4 HP and KB3; no ally damage.
- [ ] Seq2 Giant's Shortcut: phasing through block makes enemies within2 take20% current health (experimental server NoClip).
- [ ] Seq1 Divine Door: G pull/stun, next melee+50%; teleport choice not yet complete.
- [ ] Seq0 The Impossible Fist: G 900t/18000t. Experimentally phases, applies enemy Wither II/Slowness II in15, +30% damage; +5% melee per solid block crossed (max50%); end shockwave2 HP per Momentum within5. Exact through-wall reach and armor-halving pending.
- [ ] Test with same-team friends, enemy players and unteamed players; offensive targeting must not affect teammate players.
- [ ] Verify noClip is restored on timeout, death, disconnect, world change and Origin reassignment; avoid protected regions and real SMP worlds until accepted.
- [ ] Test every ordinary skill with non-OP accounts, RPG Sequence4 slot swapping, Sequence1 fusion, acting/ascend, and survival restart.
- [ ] Record exact commit, Minecraft/Fabric/Origins versions, full log and reproducible PvP/block behavior.

DO NOT consider startup smoke a substitute for the above tests.
