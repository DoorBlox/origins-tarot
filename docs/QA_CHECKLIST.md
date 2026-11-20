# V3 test-world acceptance checklist (not yet run)

Run on **Minecraft Java 1.18.2, Fabric, Origins 1.4.1**. A passing Python test or green GitHub Action does not prove any Minecraft command was accepted by a running server.

## First-load acceptance

- [ ] Replace V2 ZIP, confirm one V3 pack enabled (`datapack list`). No duplicated V2/V3 packs.
- [ ] Vanilla/Origins G and V abilities and all 18 gliders still function.
- [ ] A player already using a Tarot Origin is automatically registered with `tc_pseq=9` and their correct primary ID; `/trigger tc_status` works.
- [ ] `/trigger tc_help` and `/trigger tc_cards` work for non-OP players.
- [ ] No syntax errors from generated `load`, `tick`, or advancement functions appear in console.
- [ ] Confirm `origin has origin @s origins:origin tarot:fool` returns a nonzero result for a Fool player; registration depends on this 1.4.1 behavior.

## Progression

- [ ] Acquire the listed A item; receive exactly one Acting mark, only with the matching active Arcana.
- [ ] Repeating A immediately gives no marks; after the 120-second cooldown, perform B, then A again.
- [ ] Acting marks persist after death and relog.
- [ ] Build a lodestone over crying obsidian; Sequence 9 -> 8 consumes exactly 6 amethyst and 8 lapis, one mark, and 12 stability.
- [ ] Without enough items, marks, stability, or altar, no items are consumed and no level change occurs.
- [ ] One command invocation **never** advances multiple levels, even if a player has materials for more than one tier.
- [ ] Upgrade powers appear after ascent, and on logout/relog; no duplicate attribute stacking.
- [ ] At 20 or less stability, Weakness applies; `/trigger tc_meditate` at altar with 4 amethyst restores up to 30, only once per 5 minutes.

## Dual Attunement / controls

- [ ] Visit Nether and End *after V3 is installed* and confirm recorded travel flags.
- [ ] At primary S4, choose a different card via `/trigger tc_trialcmd set N`; same card is rejected.
- [ ] Complete alternating A/B **of the candidate** four times; unlock fails if candidate not proven.
- [ ] Pay 16 amethyst + 4 ender pearls + 1 ghast tear; secondary is saved at S9.
- [ ] At primary S4, switching is blocked away from altar; at primary S3, it works away from altar.
- [ ] Switching blocked while FallFlying, airborne, during combat and while cooldown >0; verify 10-minute online cooldown survives reconnect.
- [ ] Switching changes to **exactly one full Origin**. Passives of previously active Origin disappear. Primary and secondary Sequence/marks persist separately.
- [ ] At active S2, exactly one reduced Echo from the inactive card; none at S3.
- [ ] At active S1, curated pair gets its special Resonance, non-curated pair gets mild generic resonance; no two full Origins stack.
- [ ] Test Fool+Magician, Star+Death, Emperor+Judgement, World+Fool and one unbound pair.
- [ ] `function tarot_progress:admin/rollback_all` revokes only V3-tier/echo/resonance powers, then V2 backup restores normal existing origin functionality.

## Performance

- [ ] 2-6 players online with moving, killing, trading and dimension travel; no repeated advancement flood, server stall or tick spikes.
- [ ] Verify packet/client disconnect handling and restart persistence.
- [ ] If any test fails, **do not use on the main SMP**. Record first log error and exact command, rollback to V2.
