# Install the native Arcane V2 development build on your private SMP

**Target:** Minecraft Java 1.18.2 / Fabric Loader / Fabric API / Origins 1.4.1.
**KubeJS is NOT installed and is NOT required.** Java 17 is the minimum
runtime for the game server. The developer build is NOT a completed 434-ability release.

## 1. Choose the correct build

Open the PR's **Arcane V2 Native Fabric (no KubeJS)** check, select an
exact-head successful run, and download the Actions artifact
`tarot-arcane-v2-native-unverified`. Extract the outer GitHub artifact ZIP.
Inside is the remapped `tarot-arcane-v2-0.1.0.jar` mod file.

Do NOT copy `-sources.jar` or the entire artifact ZIP into `mods/`.
The native JAR includes `data/tarot/**` and the origin-layer JSON; it does
not need a second Arcane datapack ZIP.

## 2. Back up and install

1. Stop the SMP server. Back up `world/`, including `playerdata/`,
   `advancements/`, `data/scoreboard.dat`, and your previous Tarot packs.
2. Remove **all previous Tarot V2/V3 datapack ZIPs** from
   `world/datapacks/`. The old Tarot datapacks define the same Origin IDs
   and will fight with this implementation.
3. Move `tarot-arcane-v2-0.1.0.jar` into server `mods/` alongside
   Fabric API and Origins. The Fabric mod is marked `environment: "*"`;
   install the same mod on your Fabric game client if your client refuses
   the server pack or Origin setup. No KubeJS mod or scripts.
4. Start the server and inspect startup log for `mixin`, `tarot_arcane_v2`,
   `power`, `Failed to load`, and unknown Origin ID errors.
5. Join with a test character. Initially the supported selectable Origin
   IDs are `tarot:fool`, `tarot:hanged_man`, `tarot:world`,
   `tarot:justice`, `tarot:hermit`, `tarot:chariot`, `tarot:death`,
   `tarot:tower`, `tarot:magician`, `tarot:strength`,
   `tarot:emperor`, `tarot:lovers`, `tarot:devil`, `tarot:judgement`,
   `tarot:star`, `tarot:empress`, `tarot:sun`, and `tarot:moon`. The Paper Martyr, Marked Verdict, Burning Archive,
   Crumbling Reaper, Impossible Fist, Benevolent Crown and Binding Contract
   Starless Poison and Eclipse Resonances activate at Sequence 1; their Origin JSONs are not
   added as independent character-creation choices.
6. Check `/tarot slots` and `/tarot status`. Players can alternate
   **Acting A** (acquire/handle the card's designated item) and **Acting B**
   (an actual themed kill/trade) to earn digestion marks. Successful actions
   have a 120-second **online-time** cooldown. Once the required marks
   and ritual offerings are collected, stand on a **lectern directly above
   crying obsidian** and use `/tarot ascend`; no OP required.
7. For rapid owner-only testing, `/tarot debug sequence <0-9>` remains
   available to OP, but normal players should use `/tarot ascend`.

## 3. Survival progression

Current supported Acting A / Acting B tracks:
- **Fool:** acquire or handle a compass; then kill a spider
- **Hanged Man:** acquire or handle kelp; then kill a drowned
- **World:** acquire or handle a crossbow; then kill a pillager
- **Justice:** acquire or handle a honey bottle; then trade with a villager
- **Hermit:** acquire or handle lapis lazuli; then trade with a villager
- **Chariot:** acquire or handle flint and steel; then kill a blaze
- **Death:** acquire or handle a bone; then kill a skeleton
- **Tower:** acquire or handle TNT; then kill a creeper
- **Magician:** acquire or handle an ender pearl; then kill an Enderman
- **Strength:** acquire or handle an iron ingot; then kill a zombie
- **Emperor:** acquire or handle a shield; then kill a pillager
- **Lovers:** acquire or handle a poppy; then trade with a villager
- **Devil:** acquire or handle a blaze rod; then kill a blaze
- **Judgement:** acquire or handle iron bars; then trade with a villager
- **Star:** acquire or handle a clock; then kill a phantom
- **Empress:** acquire or handle a spider eye; then kill a spider
- **Sun:** acquire or handle glowstone dust; then kill a skeleton
- **Moon:** acquire or handle redstone dust; then kill a spider

Alternate A/B. Each accepted action grants one mark, to a maximum of 20.
Use `/tarot status` to see mark count, next required action and the
per-Sequence offering inventory requirements. The source of these
offerings is the previous repository's V3 Path of Ascension, adapted
to Rev3's **shared** Sequence. This is a new progression bridge, not
an assertion that the Rev2/3 handbooks define an Acting economy.

## 4. Quick debug command tests

Start at Sequence 9 after choosing Fool:
```
/tarot slots
/tarot debug sequence 4
/tarot slots
/tarot slot 6 tarot:hanged_man 9
/tarot slot swap 1 6
/tarot slots
/tarot slot 6 clear
/tarot slot auto
/tarot reset
/tarot debug sequence 1
/tarot slots
/tarot bind primary the_paper_martyr
```

For World paired with Justice:
```
/tarot debug sequence 4
/tarot slot 6 tarot:justice 9
/tarot slots
/tarot debug sequence 1
/tarot bind primary the_marked_verdict
/tarot slots
```

The debug Sequence command **only descends**; a test player cannot use it
to reset back to Sequence 9. Test early sequences with a fresh player UUID
or a fresh disposable world. Never manually delete `tarot_arcane_v2.dat`
from a meaningful save without a backup and migration.

## 5. Keys, targeting, and safety

- Origins' G/V active keys are routed through two native bound-skill
  dispatchers, each selecting **one active ability**.
- Use `/tarot bind primary <ability_name>` or
  `/tarot bind secondary <ability_name>` after slotting its Sequence.
- Offensive effects apply to tagged hostile mobs **and enemy players**,
  not teammates. Healing/buff auras target self + same-team players.
- Identity drawbacks stay active when a Sequence kit is unslotted.
- For tests of lethal rescue, PvP, flight, minions or environmental
  damage, use a backed-up disposable world.
- No server deployment is performed by this repository change. Download
  and install the JAR explicitly.

## 6. Acceptance and rollback

Follow `BATCH_1_TEST.md`, `BATCH_2_TEST.md`, `BATCH_3_TEST.md`, `BATCH_4_TEST.md`, `BATCH_5_TEST.md`, `BATCH_6_TEST.md`, `BATCH_7_TEST.md`, `BATCH_8_TEST.md`, `BATCH_9_TEST.md`, `BATCH_10_TEST.md`
and the associated gaps documents. Do not confuse successful CI with
real in-game gameplay acceptance.

To roll back, stop the server, remove the Arcane V2 JAR, restore the
old V3 datapack and matching world backup. Do **not** mix Arcane V2
persistent save data with V3 progression data without a migration.

**Status:** Eighteen individual pathways and nine Resonances have named power
resources in development source (355/434), with 79 remaining. Some of
these entries have incomplete or approximate mechanics; no live SMP acceptance
is recorded. The Fall can injure **self and allies** by Rev2 design.
**Do not enable experimental phasing in a protected or public world** until
its noClip safety, cleanup and client prediction are verified.

Batch 7 adds `/tarot allow <player>` for active Emperor/Benevolent Crown
domains and `/tarot consort <player>` for the fused capstone. These commands
are scoped to the player's active domain and cannot assign an offline consort.
Do not interpret startup CI as verified ally/PvP/land-claim behavior.

Batch 8: use `/tarot decree <no_sprint|no_jump|no_attack|no_spawn>`
inside an active Judgement Absolute Law, and `/tarot contract accept` or
`/tarot contract refuse` if you receive a pending Binding Contract offer.
Non-response causes **no penalty**. These commands require only a server
player account, not OP. Never deploy before exact-head CI and safe PvP tests.

Batch 9 includes `/tarot mirror exit` for a temporary Mirror World
capstone; the control is available only while the corresponding power is
active. Its safe-flight restoration must be live-tested before enabling
in survival multiplayer.

Batch 10: `/tarot bind primary the_eclipse` at Sequence1 casts the
Sun+Moon fused fixed/moving domain. Because Blood Diet is a permanent
identity drawback, food outside `#tarot:meat` will not restore hunger.
Do not co-install a previous V3 or legacy Tarot datapack.
