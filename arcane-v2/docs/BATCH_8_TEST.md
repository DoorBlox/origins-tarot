# Batch 8 — Devil / Judgement / Binding Contract (native-only)

**Manual multiplayer acceptance checklist. Every box starts UNTESTED.**
Target Java 1.18.2 / Fabric / Origins 1.4.1; no KubeJS. Use a backed-up
development world, one same-team player and one enemy/un-teamed player.

- [ ] Choose Devil. Origin has only identity/marker and Elytra wings; Sacred Rejection blocks both golden apples without revoking other origins' powers.
- [ ] Seq9 Hellborn gives full fire/lava immunity; melee Corrupting Claws Wither I 40t CD320 against hostile mobs AND enemy players, never teammates.
- [ ] Desperate Malice: +18% melee damage below40% health. Infernal Vitality: +1 HP every80t while burning.
- [ ] Drinking healing potions receives approximately half healing; splash potions and other heals during the same window need independent verification.
- [ ] Seq8 damage received has ~10% Strength I40t; Seq7 kills grant Speed I60t.
- [ ] Seq6 Devil's Mark right-click hostile mob or enemy player → Wither I40t/CD400; teammate right-click must not debuff.
- [ ] Seq5 crouch-right-click player privately reports their held item, CD200.
- [ ] Seq4 Demon Form extends Malice below50% HP.
- [ ] Seq3 Blather 10% chance on nearby enemies to redirect mob aggression or approximate player confusion; human targeting cannot be forced.
- [ ] Seq2 bind secondary blood_price: lose exactly4 HP and gain Strength II200t, CD3600; cannot be cast at ≤4 HP.
- [ ] Seq1 bind primary chaos_unleashed: enemies within10 Slowness II+Weakness I160t; next melee +50%/Wither II100t, CD1800.
- [ ] Seq1 Infernal Vitality II improves burning healing to1 HP/60t.
- [ ] Seq0 Descent G lasts800t/CD18000, Strength II/Fire Resistance/Speed I, melee Wither I, 1 HP lifesteal at most once20t, 75% kill chance minions lifespan600t at most4, 15% extra incoming damage. End Hunger II200 and remove Absorption.
- [ ] Choose Judgement. No Elytra. No Unlawful Escape disallows vanilla ender pearl/chorus fruit even when Seq9 kit not slotted.
- [ ] Law's Weight gives +2 armor/+45% knockback resistance. Retaliatory Sentence slows enemy attackers60t/CD280.
- [ ] Hold the Line reduces incoming melee damage12% when not sprinting; Imperative Seq4 increases to18%.
- [ ] Verdict's Weight kills: 10% chance nearby hostiles lose their targets, flee-like approximation40t.
- [ ] Seq8 right-click another player to track direction/distance privately1200t; reconnect and dimension checks do not leak coordinates after expiry.
- [ ] Seq7 Question crouch-right-click hostile/enemy player gives Weakness I60t/CD400.
- [ ] Seq6 Verdict kill applies Slowness I40t to nearby hostiles AND enemy players within4, CD400.
- [ ] Seq5 bind secondary discipline → next melee Slow25520t, CD600.
- [ ] Seq3 Chaos Hunter +10% against a hostile mob targeting another player; enemy-player target inference is incomplete.
- [ ] Seq2 bind secondary balance: equalize current HP with nearest hostile mob/enemy player within6, CD3600; no teammate health exchange.
- [ ] Seq1 Order G: Slowness II+Weakness II160t within8, next melee stuns40t, CD1800; law KB resist becomes60%.
- [ ] Seq0 The Absolute Law G 600t/CD24000; select /tarot decree no_sprint/no_jump/no_attack/no_spawn. Test each choice and enforcement radius30. No_spawn only pacifies currently; does not block spawn registration.
- [ ] Verify Seq5→4 second identity drawback applies permanently even with zero partner kits slotted.
- [ ] Verify Seq2→1 individual kits revoked; all ten Binding Contract Sequence9–0 kits active simultaneously.
- [ ] Seq9 Hellborn Verdict gives fire immunity, +2 armor/+45% KB resist, attacker Slowness60, forbids golden apples/ender pearls.
- [ ] Seq8 Fallen Question: 10% Strength I on damage and sneak-rightclick hostile/enemy Weakness I60t.
- [ ] Seq7 Predator's Calm kill Speed I60t and enemy right-click Slow I60t.
- [ ] Seq6 Devil's Verdict applies Wither I40t on right-click and nearby Slowness I40t on kills.
- [ ] Seq5 Desire's Discipline: crouch-right-click player reports held item; hostile player also gets Slowness II60t. Secondary Discipline stuns next melee20t.
- [ ] Seq4 Infernal Verdict melee applies Wither I40t, Slow I40t, Glowing80t (not custom red shader).
- [ ] Seq3 Law of Hell when hurt: attacker takes2 damage+Slow II40; if below50% HP also Wither I60t.
- [ ] Seq2 Contract Enforcement on player right-click sends a 10-second offer: /tarot contract accept grants both temporary buffs; /tarot contract refuse explicitly applies Weakness II600t and drops only ONE held item. No reply, expiry or disconnect must have **no refusal penalty**.
- [ ] Seq1 Chaos Law G casts Slow II+Weakness I160t to nearby enemies, primes +50% melee, while active attackers receive1 damage+Slow II60t.
- [ ] Seq0 The Binding Contract G 800t/CD18000: Strength II, Fire Resistance, +20% speed, enemy area15 Slowness255+Wither II, on-hit Wither II+Slow I, lifesteal1 HP/second, bounded4 minions 600t, +15% incoming damage; end Hunger II200.
- [ ] Seq0 offers contracts to all nearby players; each must explicitly accept or refuse; silently ignored offers expire harmlessly.
- [ ] Wither-attributed kills grant Absorption II600t where safe; test no duplicate rewards on a single death.
- [ ] Team and friendly-minion tests: allies never receive damaging offensive effects from caster; summons never attack owner/teammates; all summoned Vexes despawn on death/relog.
- [ ] Test Origin reassignment, slot removal, dimension change, concurrent domains, server crash recovery and death while active; never leave movement bans or permanent strength/speed.
- [ ] Record exact commit SHA, Java/Origins versions, log and reproduction for any error.

CI compilation and headless startup are prerequisites, NOT substitutes for these checks.
