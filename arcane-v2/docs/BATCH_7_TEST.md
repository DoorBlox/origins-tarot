# Batch 7 — Emperor / Lovers / Benevolent Crown (native Fabric, no KubeJS)

**Minecraft Java 1.18.2, Fabric API, Origins 1.4.1.**
All checks start **UNTESTED IN LIVE MINECRAFT**. Compile and headless startup do
not establish all gameplay or PvP behavior. Use a disposable backed-up world.

- [ ] Choose Emperor at Seq9. Origin has *only* marker + permanent Weight of the Crown; no Seq9 powers inherited from Origin.
- [ ] Emperor's Sovereign Plate gives +3 armor and +40% knockback resistance while Seq9 kit slotted.
- [ ] Distorted Authority: when harmed by hostile mob or enemy player, attacker Slowness I 40t (CD280). Teammates never debuffed.
- [ ] Shield held: incoming damage −10% (Iron Decree −15%), speed −25%, sprinting in any armor exhaustion +50%. Drawback remains active after un-slotting its Seq9 kit.
- [ ] Decree of the Sovereign applies Hero of the Village approximation while shield near villager (actual exact 10% discount is NOT yet verified).
- [ ] Seq8 Unbound removes Weakness below 12 HP.
- [ ] Seq7 bind secondary `coin`, hold at least 1 gold ingot: consume it and pacify nearest hostile mob or enemy player for100t, CD600. PvP pacified enemy cannot damage owner; cannot affect teammates.
- [ ] Seq6 crouch-right-click solid ground: 5×5 Corrupt Ground active600t, Slowness I to hostile mobs AND enemy players, CD1200.
- [ ] Seq5 bind secondary `decree`: mobs within6 retarget holder; enemy players visually marked rather than forced AI, duration100t, CD900.
- [ ] Seq4 Fallen Aura increases Distorted Authority slow to60t and Weakness I 20t.
- [ ] Seq3 Frenzy below8 HP Speed I + Haste I 100t, CD600.
- [ ] Seq2 Entropy Field auto-triggers on qualifying projectile hit within5: projectile damage ×0.5 for100t, CD3600.
- [ ] Seq1 Abolish primary strips positives from enemies within8, applies Slowness II/Weakness I 100t, CD1800.
- [ ] Seq0 Emperor's Domain primary1200t/CD18000: enemies held outside3, owner damage+15% and damage taken−15%; all players inside15 cannot sprint/jump except owner and those whitelisted by `/tarot allow <player>`.
- [ ] Choose Lovers Seq9: Elytra-style glide and permanent Separation Anxiety identity; after being alone for **more than600t**, exhaustion +35% and mining−15%. Reunite with another player to clear.
- [ ] Linked Hearts with same-team player within8: owner+teammate speed+10%; each receives 1 HP heal per500t. Enemy players must NOT receive ally benefits.
- [ ] Fertile Hands +25% healing on owner and +20% crop-breaking speed, but only while equipped.
- [ ] Shared Refuge near another player: Resistance I pulse every600t.
- [ ] Seq8 right-click ally Triage heals2 HP/CD400; right-click enemy must not heal.
- [ ] Seq7 crouch-right-click mature/immature crop grows it fully; **per-crop** CD1200, inspect growth and land-claim interactions.
- [ ] Seq6 passive mob within4 gives +1 maximum HP, reverts when none nearby.
- [ ] Seq5 secondary Nature's Grasp: hostiles AND enemy players within4 Slowness II 60t/CD900.
- [ ] Seq4 secondary Transmute takes 2 iron ingots and grants 1 gold ingot/CD12000; exploit-test stacked and full inventory cases.
- [ ] Seq3 Requiem: passive mob dying within8 grants owner Regeneration I 60t.
- [ ] Seq2 Withering triggers on enemies within5 Wither I 60t/CD3600 (no allies).
- [ ] Seq1 Nature's Step heals owner+allies within8 by4 HP, Regeneration I 200t, active300t/CD2400. Native leaf phasing remains approximate, NOT complete.
- [ ] Seq0 The Garden primary1800t/CD24000. Allies within15 Regen II and +10% speed; hostile mobs/player pacified unless attacked; all passive mobs inside cannot die, even to explosions.
- [ ] Reach Seq4 from primary Emperor or Lovers. Both drawbacks remain active regardless of slotted kits; slots 6 at Seq4, 7 at Seq3 and 8 at Seq2.
- [ ] Reach Seq1; verify individual kits revoked, all ten Benevolent Crown kits 9–0 active, no extra slots.
- [ ] Seq9 Sovereign's Care combines +3 armor/+40 KB/ +25% self-heal/teammate speed+5%; shield and solitude drawbacks.
- [ ] Seq8 Unbound Symbiosis removes Weakness at low HP and grants nearby passive-mob +1 max HP.
- [ ] Seq7 Coin's Blessing: both gold pacify and crop growing on proper inputs.
- [ ] Seq6 Corrupt Symbiosis: Corrupt Ground slows only enemies and grants symbiosis to nearby same-team allies.
- [ ] Seq5 Decree of Nature includes Slowness II to enemies within6 and allied Regeneration.
- [ ] Seq4 Linked Crown: while holding shield, teammates within8 get -5% incoming damage and 1 HP every200t.
- [ ] Seq3 Shared Domain: allies standing inside Corrupt Ground Regen I.
- [ ] Seq2 Emperor's Hymn invokes decree (CD900), allied Regeneration I/+10% speed and owner +10% resistance.
- [ ] Seq1 Triage Decree on right-click same-team ally heals2 HP, slows and damages nearest enemy by2 HP, CD400.
- [ ] Seq0 Benevolent Crown primary1200t/CD18000: enemies kept outside3; all players sprint/jump denied unless /tarot allow; allies Regen II/+10% speed; passive mobs invulnerable; enemies initially pacified100t.
- [ ] During fused capstone /tarot consort <player> must accept exactly one online same-team ally within15; consort +15% damage/+15% reduction, disallow enemies.
- [ ] During fused capstone, teammate deaths inside domain heal surviving same-team allies by4 HP.
- [ ] Test enemy and unteamed players, teammate players, right-click priority, overlapping domains, concurrent guilds, respawn, disconnect, World change, cooldown persistence and kit-swapping cleanup.
- [ ] Test full inventories and protection/claim mods. Do not infer third-party claim support from vanilla block permission tests.
- [ ] Record exact commit, Minecraft/Fabric/Origins versions, logs, any Mixin conflicts, and reproduction.

No line above can be marked passed without direct in-world verification.
