# Arcane V2 — native no-KubeJS Fool acceptance checklist

**Status: not playtested; do not install on production.** This checklist is for an isolated,
backed-up Minecraft 1.18.2 Fabric world with Origins 1.4.1, Fabric API,
and the native mod. Never use the existing V3 Path of Ascension datapack simultaneously.

- [ ] Check server starts with no JSON parsing or mixin errors; `/datapack list` includes native mod data.
- [ ] Choose Fool in Origins; get `[Tarot] Enrolled as fool at Sequence 9`.
- [ ] Run `/tarot slots`: SINGLE, Sequence 9, one filled Fool 9 slot.
- [ ] Sprint / Elytra glide and compare exhaustion with an ordinary player; Fool multiplier should be 1.25 when the relevant action produces exhaustion.
- [ ] Sneak and press the secondary key or `/tarot cast spirit_vision`: all nearby living entities within ten blocks glow for 40 ticks; 100-tick cooldown.
- [ ] Get hit repeatedly and confirm Clown's Mischief occasionally blinds the attacker (20% chance, 100-tick cooldown).
- [ ] Stand within eight blocks of three hostile mobs or one enemy player; Spiritual Overload Nausea triggers at 40-tick intervals.
- [ ] Try enemy teammate and unteamed players. Teammates must never be affected by Puppet String; unteamed players may be enemies.
- [ ] Verify `/tarot slot 1 tarot:fool 8` fails in single mode.
- [ ] As OP run `/tarot debug sequence 8`; check automatic Seq 9 and Seq 8 activation and the increased slot count.
- [ ] As OP run `/tarot debug sequence 5`; check five auto-filled slots.
- [ ] As OP run `/tarot debug sequence 4`; check six slots, Fool 9–5 retained and slot 6 empty.
- [ ] Assign `/tarot slot 6 tarot:hanged_man 9`; check assignment persists in `/tarot slots`. Hanged Man mechanics are not yet available in Batch 1.
- [ ] Check duplicates, nonpaired Arcana and locked Sequence assignments fail; check `/tarot slot 6 clear`, `/tarot slot swap 1 2`, `/tarot slot auto`, `/tarot reset`.
- [ ] Die, respawn and reconnect; verify slots and native power grant source have been reconciled. Check changing dimension likewise.
- [ ] As OP run `/tarot debug sequence 3`, then `2`, verify slot counts 7 then 8; extra slots remain empty.
- [ ] As OP run `/tarot debug sequence 1`; check all individual sequence kits revoked and mode RESONANCE. The full Paper Martyr kit is **not implemented yet**, so its acceptance is NOT PASS.
- [ ] As OP run `/tarot debug sequence 0`; confirm Resonance mode stays active, with no second slot transition.
- [ ] Check no KubeJS mod, KubeJS server scripts or KubeJS config is required.

If any test fails, retain server log, mod list, error stack, world backup and exact command.
The current draft cannot pass the full SMP acceptance bar: see BATCH_1_BLOCKED.md.
