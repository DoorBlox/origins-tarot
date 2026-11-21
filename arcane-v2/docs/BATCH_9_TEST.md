# Batch 9 — Star / Empress / Starless Poison acceptance checklist

Native Fabric 1.18.2 + Origins 1.4.1. **Do not mark any check completed
without direct Minecraft testing.** This is a development candidate.

- [ ] Choose Star Seq9: permanent identity True Sleeplessness disables bed sleep, but still sets respawn point.
- [ ] Star Seq9 Sleepless gives permanent Night Vision and shorter Blindness/Darkness (the duration-shortening is not yet exact).
- [ ] Star Seq9 Nightwatch +15% movement at night, +15% vs tagged undead at night. Seq4 Nightwatch II extends to light<=7.
- [ ] Star Seq9 Evernight's Patience removes 20% exhaustion at night.
- [ ] Star Seq9 Sleepless Vigil phantom threshold requires 5 days (7 at Seq1), still marked incomplete.
- [ ] Star Seq8 crouch60t Lullaby: hostile mobs AND enemy players within5 get Slowness I60t, cooldown1200.
- [ ] Seq7 Nightmare 20% chance +1 XP for hostile kill at night.
- [ ] Seq6 Soul Shield 10% chance Resistance I40t on night damage.
- [ ] Seq5 V Haunt: nearest hostile OR enemy player within6 receives Blindness I60t/CD900.
- [ ] Seq3 Terror: at night 10% chance enemies nearby lose mob target / Slowness40t, no teammates affected.
- [ ] Seq2 Conceal: Invisibility100t/CD3600.
- [ ] Seq1 Misfortune: Weakness II+Slowness II160t, Blindness60t to enemies within10/CD1800.
- [ ] Seq0 The Starless Sky G: 800t/CD24000, Invisibility+Speed II, +20% damage, Blindness/Slowness I to enemies within30; light sources visually dimmed by particles, NOT destroyed.
- [ ] Choose Empress Seq9: identity Exposed Reflection increases incoming PROJECTILE damage by25% in direct sunlight, persists without Seq9 slot.
- [ ] Empress Witch's Venom melee Poison I60t/CD240 against hostile mob AND enemy player; Plague Touch Seq5 extends Poison80+Hunger40.
- [ ] Empress Mirror Veil sneak at light<=7 and not exposed to sun gives Invisibility; armor visibly rendered (client appearance caveat).
- [ ] Empress Witch's Grace +10% speed, immune to Poison; Reflected Beauty on damage in light>=12 puts Nausea I40t on enemy attacker/CD400.
- [ ] Seq8 Whisper crouch-rightclick passive to pursue nearest other player 200t, not true aggressive AI; no teammate forced attack.
- [ ] Seq7 Black Fire 10% chance melee ignition20t, NEVER lights the ground.
- [ ] Seq6 Thread rightclick enemy player within6 → Slowness I40t/CD400.
- [ ] Seq4 Aura of Despair every40t 10% chance nearby hostiles/enemy players lose targeting, slowdown.
- [ ] Seq3 Ageless reduces exhaustion for sprint/jump, never makes negative exhaustion.
- [ ] Seq2 Mirror Passage V: cross up to10 glass blocks to safe air/CD3600. Verify no suffocation or bypass of protected worlds.
- [ ] Seq1 Apocalypse's Herald G spawns 5 visual meteors over160t within10, 6 damage and 60t ignition to enemies only, CD3600.
- [ ] Seq1 Petrifying Gaze crouch60t gives enemies within6 Slowness II60t/CD1200.
- [ ] Seq0 The Mirror World G 500t/CD18000: invisibility, temporary unrestricted flight, incoming damage immunity; /tarot mirror exit exits within30 blocks of entry and poisons/withers enemies within8 for100t.
- [ ] Mirror World restores initial ability flight state on timeout, manual exit, death, disconnect, dimension change, Origin change AND restart.
- [ ] At Seq4 both Star and Empress identities remain permanent, even if parent Sequence kits are unselected.
- [ ] At Seq1 all individual kits revoked; all ten Starless Poison Resonance Seq9-0 powers become active, including Seq0.
- [ ] Starless Seq9 Night Vision/+10% speed/Poison immunity/+15% night speed, no sleep, sunlight arrow +25% taken.
- [ ] Seq8 Lullaby Whisper can crouch60t slow enemies and crouch-rightclick passive as a non-owner diversion.
- [ ] Seq7 Nightmare Fire XP20% on night kill and melee ignition10%; Seq6 Soul Thread 10% Resistance on night damage and Thread Slow40t/CD400.
- [ ] Seq5 Haunting Plague V Blindness60+Poison I60 to enemy within6/CD900. Venom attacks Poison I80+Hunger I40.
- [ ] Seq4 Night Venom applies poisoned aura and night damage bonus to poisoned enemies, excluding teammates.
- [ ] Seq3 Poison Conceal from Invisibility inflicts Poison II80t and Glowing40t, with involuntary reveal only on critical melee.
- [ ] Seq2 Shadow Whisper when attacked applies enemy 2 damage, Blindness20t, Poison40t and self Speed I40t.
- [ ] Seq1 Midnight Apocalypse G launches5 meteors/160t and adds Poison II60/Blindness60 to hit enemies.
- [ ] Seq0 The Starless Poison G 800t/CD24000: 30-block Blindness I+Slowness I, Poison II per60t and +25% damage to poisoned enemies.
- [ ] Poisoned deaths in capstone spread poison to enemies within3 without damaging same-team players; end deals6 damage + Wither I100t only to poisoned, still-valid enemies, self Invisibility100t.
- [ ] Repeat with unteamed PvP enemy, same-team ally, and different-team enemy. Allies never receive offensive debuffs.
- [ ] Test relog/restart while poisoned, flying, invisible and while meteors are pending. Flight permissions must not remain elevated.
- [ ] Verify 315 named sequence power resources and all Origin identity-only powers; single→slot at Seq4 and slot→Resonance at Seq1.
- [ ] Collect exact commit, full logs and reproduction before publicly enabling the capstones.

Headless server startup is a baseline gate, not gameplay acceptance.
