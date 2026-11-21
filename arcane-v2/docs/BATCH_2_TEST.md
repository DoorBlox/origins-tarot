# Batch 2 — native Hanged Man + Paper Martyr, no KubeJS

**NOT gameplay-validated.** Required test: Minecraft Java 1.18.2, Fabric,
Fabric API, Origins 1.4.1, native Arcane V2 JAR from exact-head successful CI.
Never combine with old Tarot V2/V3 datapacks. Make backups of world, playerdata,
advancements and scoreboard.dat. Run on a private world.

- [ ] Boot Fabric with the Arcane JAR and Origins only; `datapack list` includes Arcane resources; verify NO mixin-apply or unknown power errors.
- [ ] Choose Hanged Man. Confirm only marker/identity/wings are inherited and Seq 9 powers are granted via `tarot_slot`.
- [ ] `/tarot slots` at Seq 9 shows one Hanged Man kit; check natural regeneration stops at eight hearts, but direct potions still heal.
- [ ] Test 25% Sin gained from real damage and cap at 16 HP, then 200-tick decay and any Burden Bearer Regeneration.
- [ ] At health below eight HP with Sin, burst damages nearby hostile mobs AND unteamed enemy players, applies Weakness and heals owner; teammates unaffected.
- [ ] Kill a hostile: Graze the Soul heals 2 HP and grants Resistance I, with 120-tick cooldown.
- [ ] Drink a healing potion: natural regeneration reaches 10 hearts for 1200 ticks. Kill: natural regeneration reaches nine hearts. Wait grounded in light ≤9 for 160 ticks to unlock ten hearts for 600 ticks.
- [ ] Sequence 8 Shadow Whisper lessens mob detection; Sequence 7 Shadow Cloak raises light threshold from 7 to 11.
- [ ] Sequence 6 Flesh Creek sometimes heals four HP on taking damage. Sequence 5 Burden Bearer reduces damage by 10% when Sin exists.
- [ ] Sequence 4 Dark Blade under 12 HP boosts speed 10% and melee damage 15% against hostile mobs/enemy players.
- [ ] Sequence 3 Trinity reacts to three distinct damage types within 100 ticks with Resistance II and four HP healing.
- [ ] Sequence 2 Profane Aura sometimes Weakness-debuffs attacker and Slowness-debuffs nearby hostile enemies on a kill.
- [ ] Reach Seq 4 via `/tarot debug sequence 4`, slot Fool kits and verify that unslotted Hanged buffs stop; attempt invalid or duplicate assignments.
- [ ] In Seq 2, eight slots offer Hanged Man and Fool Seq 9–2; Seq 3/2 slot growth persists over death and reconnect.
- [ ] At Seq 1, check individual Fool/Hanged powers are revoked, mode is RESONANCE, and exactly all ten Paper Martyr Seq 9–0 powers are granted.
- [ ] Check natural regeneration is still limited and Fool's sprint/glide +25% exhaustion persists in Paper Martyr.
- [ ] `/tarot bind secondary suffering_sight` then sneak+V; transfer 3 stored Sin for damage and Glowing on hostile mobs/enemy players only.
- [ ] `/tarot bind secondary burdened_beginning` then sneak+V; nearby living entities glow for 100 ticks.
- [ ] `/tarot bind secondary borrowed_sacrifice` then V; verify 3 Sin spent, invisibility, and attack-break retaliation.
- [ ] `/tarot bind secondary gathering_of_martyrs` then V; two bounded Vex-like minions appear, attack hostile mobs and enemy players but never damage teammates.
- [ ] Hit Paper Martyr until Shadow Step spawns a decoy. Attack the decoy; explosion must target hostile mobs and enemy players only.
- [ ] Test lethal Martyr's Substitute (7200-tick cooldown), 12-block retreat, Sin shadow, 20 HP restore, invisibility and speed.
- [ ] `/tarot bind primary the_paper_martyr` then G: capstone lasts 700 ticks, grants flight, exact damage multipliers from mixin, periodic nova and decoy, and rewind.
- [ ] During capstone, only same-team players get Absorption IV on expiry; enemy players are damage targets, not allies.
- [ ] Confirm death during capstone does not resurrect or detonate on next login/respawn.
- [ ] Repeat PvP tests with same-team players, enemy-team players and players without a team.
- [ ] Check world/server logs for errors after changing dimension, disconnecting mid-capstone, rejoining, and restarting.
- [ ] Run legacy V2/V3 test workflows to confirm unrelated release source remains unchanged.

Do NOT mark a checkbox passed based on Gradle compilation. Record server log, exact
commit SHA, mod list and reproduction for each failure.
