# Batch 3 - World / Justice / Marked Verdict native acceptance

This file describes manual acceptance tests. **No checkbox is considered passed by
compilation or by the disposable server reaching Ready.** Use Minecraft 1.18.2,
Fabric API, Origins 1.4.1, native Arcane V2 jar; NO KubeJS or legacy Tarot V2/V3 datapacks.

- [ ] Boot world with Fool, Hanged Man, World and Justice selectable and no unknown Origins powers.
- [ ] Choose World at Sequence 9: Marked Prey Glowing 120t, Hunter's Tempo Speed I 160t on hostile kill (360t cooldown), +25% projectile damage against tagged hostiles and enemy players.
- [ ] With bow held and still, Predator's Patience charges +5% per 60t up to +30%; inspect projectile damage at maximum and after moving.
- [ ] World identity drawback: villagers refuse trading even if World Seq 9 kit is unslotted later.
- [ ] World Seq 8: use `/tarot bind secondary paper_dagger` then V: paper consumed, nearest hostile or enemy player takes 3 HP and Slowness I for 40t. 200t cooldown.
- [ ] World Seq 7: use `/tarot bind primary air_cannon` then G: target within 14 blocks takes 4 HP with large KB if hostile mob, or 3 HP with smaller KB if enemy player.
- [ ] World Seq 6: borrowed_face approximation provides out-of-combat invisibility 600t.
- [ ] World Seq 5: Puppet String applies slowing only to hostile mobs and enemy players, never teammates.
- [ ] World Seq 4: Historical Recall extends mark Glow to 160t.
- [ ] World Seq 3 and Seq 2: Small Miracle and Mystery Step bounded fallback effects function with 9600t / 4800t cooldown; **spec details unspecified and approximated**.
- [ ] World Seq 1 (test via developer injection because Seq 1 normally Resonance): Hunter's Substitution cancels lethal, relocates safely 8 blocks and restores 2 hearts.
- [ ] World Seq 0: Perfect Prey marks enemy player within 50 blocks for 900t; homing arrow tries to track target without penetrating blocks, +100% hit damage and Slowness II 100t, 24000t cooldown.
- [ ] Choose Justice: -12% mob damage while not sprinting, Weakness I on attacker for 80t CD360, Therapist's Presence Regeneration I 80t to allies every 900t.
- [ ] Justice Compassionate Restraint permanently reduces passive mob/villager/pet damage by 70%; unprovoked enemy players by 30%; teammates never receive offensive spells.
- [ ] Justice crouch-right-click player: Mind Read reports exact health privately, CD200.
- [ ] Justice right-click enemy mob or enemy player: Calm applies Slowness I 60t, CD400.
- [ ] Justice Seq 6 Suggestion: stops mob target pursuit 100t, approximates player targeting with Slowness.
- [ ] Justice Seq 5 sleep then wake: Dream Step Regeneration I 200t.
- [ ] Justice Seq 3 crouch for 60t: Shared Dream Night Vision to self and same-team nearby players only, CD1200.
- [ ] Justice Seq 2 Discern: prints target player's inventory to caster only, CD3600.
- [ ] Justice Seq 1 Author's Edit: check documented approximation for chat editing, Weakness and health reveal.
- [ ] Justice Seq 0 Mindscape: 600t 20-block freeze hostile mobs/enemy players, disable sprint/jump in radius, symmetric damage cancellation, cooldown24000.
- [ ] As OP `/tarot debug sequence 4`: unlock paired path (World/Justice), six slots, and manually mix eligible Sequence 9-4 kits.
- [ ] `/tarot slot 6 tarot:justice 9`, `/tarot slot swap 1 6` and `/tarot slot 6 clear` correctly grant/revoke whole kits; independent identity drawback never revoked.
- [ ] As OP `/tarot debug sequence 1`: revoke all individual sequences and grant **all ten Marked Verdict powers, Sequence 9 to 0**.
- [ ] Marked Verdict has both Terrifying Reputation and Compassionate Restraint active.
- [ ] Resonance Seq 9 Cold Judgment: +25% projectile, -12% incoming mob while not sprinting, -70% passive outgoing.
- [ ] Resonance Seq 8 Paper Sentence: 3 HP, Slowness I 40t and Weakness I 40t.
- [ ] Resonance Seq 7 Hunter's Calm: stationary bow charges 2x faster, applies Slowness I to hostile mobs and enemy players within 6 blocks.
- [ ] Resonance Seq 6 Silent Witness: disguise approximation for 600t and target health reveal.
- [ ] Resonance Seq 5 Puppet's Sentence: Slow II 40t + coordinates player, Slow II 80t + Glow mobs.
- [ ] Resonance Seq 4 Marked Judgment: marked target Weakness I 120t + direction/position information.
- [ ] Resonance Seq 3 Hunter's Stillness: stationary bow applies Slowness to nearby hostiles/enemy players.
- [ ] Resonance Seq 2 The Verdict: marked kill pacifies opponents within 8 blocks and grants Absorption I 600t.
- [ ] Resonance Seq 1 Swift Judgment cancels lethal, moves 8 blocks, Slowness 255 40t on attacker CD9600.
- [ ] Resonance Seq 0 Marked Verdict: 900t 50-block player mark, disables target sprint/jump; next arrow homes and slows/freezes, pacifies surrounding opponents, rewards killer and same-team allies only.
- [ ] Repeat with same-team player, enemy-team player and unteamed player; verify no teammate can receive hostile damage, debuffs or forced targeting from Arcane powers.
- [ ] Reconnect, respawn, change dimension, change Origin through Orb, restart mid-capstone; verify no residual stale flags, unlimited flight, or leaked grant sources.
- [ ] Record exact build SHA, startup log, any stack traces, and reproduction details.

Development-world installation has not been tested manually by the author.
