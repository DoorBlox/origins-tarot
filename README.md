# The Tarot Club — 22 Major Arcana Origins

> A lore-inspired, multiplayer-focused Minecraft Origins datapack featuring **all 22 Major Arcana**, **44 active abilities**, distinctive drawbacks and **18 native Elytra-gliding builds**.

**Compatibility:** Minecraft Java **1.18.2** · Fabric · Origins **1.4.1** · `pack_format: 9`  
**Status:** **Alpha / server playtest required**. Automated JSON/reference checks are not a substitute for in-game behavior testing.

This is a **fan-made** adaptation of concepts from *Lord of the Mysteries* and *Circle of Inevitability*, not an official product. The Tarot Club's card codenames are **not** identical to the novel's 22 Standard Pathways. Some cards are based on canon characters; others are original pathway-inspired interpretations. **Book Two spoilers** appear in the Empress and Chariot.

## Quick start

### Download a ready-made datapack
1. Open [GitHub Actions → Build & validate](../../actions/workflows/datapack.yml).
2. Choose a successful run and download its **tarot-club-datapacks** artifact (unzip this outer GitHub artifact download).
3. You will find **two** ready-to-install datapack ZIP files:
   - **The_Tarot_Club_22_Arcana_Only_1.18.2.zip** — the 22 Tarot choices **replace** the standard Origins list.
   - **The_Tarot_Club_22_Arcana_1.18.2.zip** — **adds** 22 Tarot choices alongside existing Origins.
4. Upload **one** of those inner ZIPs to `<world>/datapacks/`, not `mods/`; restart your Fabric server, then run `datapack list`.
5. Test with `origin set <player> origins:origin tarot:fool` (console: no leading slash; in game: `/origin set ...`).

You can also use the versioned unpacked source trees in `datapacks/only/` and `datapacks/addon/` after the initial build-sync commit on `main`. Those source directories aren't the same thing as the ZIPs—**download the appropriate ZIP** for an easy installation.

See [detailed server installation and troubleshooting](docs/INSTALLATION.md).

### Controls and gliding
- Primary power: `key.origins.primary_active` (**G** by default).
- Secondary power: `key.origins.secondary_active` (**V** by default).
- 18 cards use **`origins:elytra_flight`**—deploy by jumping in midair. These are built-in Elytra-style **gliders**, not creative-flight users.
- **No wings:** Emperor, Hierophant, Strength, Judgement.
- Area effects may affect **teammates, pets, and villagers**. Some healing skills can heal enemies, too.

## The 22 Arcana
The short summaries below are for choosing a playstyle. The [full card guide](ARCANA_GUIDE.md) documents **every character's inspiration, personality, two active abilities and cooldowns, traits, weaknesses, and mobility**.

| # | Card | Lore / archetype | Playstyle | Glide |
|---:|---|---|---|:---:|
| 0 | [The Fool](ARCANA_GUIDE.md#00--the-fool-tarotfool) | Klein Moretti | Cautious trickster and escape artist who manipulates the fight without dominating it. | Yes |
| 1 | [The Magician](ARCANA_GUIDE.md#01--the-magician-tarotmagician) | Fors Wall | Portal traveler with a reliable short-range escape and vertical mobility. | Yes |
| 2 | [The High Priestess](ARCANA_GUIDE.md#02--the-high-priestess-tarothighpriestess) | Original card archetype | Knowledge and enemy revelation, balanced by fragility. | Yes |
| 3 | [The Empress](ARCANA_GUIDE.md#03--the-empress-tarotempress) | Franca Roland | Mirror-themed witch of toxins, beauty, misdirection and vulnerability. | Yes |
| 4 | [The Emperor](ARCANA_GUIDE.md#04--the-emperor-tarotemperor) | Original card archetype | Grounded tank who controls crowds and resists retaliation. | No |
| 5 | [The Hierophant](ARCANA_GUIDE.md#05--the-hierophant-tarothierophant) | Original card archetype | Stationary support scholar who sees the enemy and grants blessings. | No |
| 6 | [The Lovers](ARCANA_GUIDE.md#06--the-lovers-tarotlovers) | Original card archetype | Support guardian whose healing also benefits enemies if carelessly used. | Yes |
| 7 | [The Chariot](ARCANA_GUIDE.md#07--the-chariot-tarotchariot) | Lumian Lee | High-mobility warlock whose powerful assault demands food and restraint. | Yes |
| 8 | [Strength](ARCANA_GUIDE.md#08--strength-tarotstrength) | Original card archetype | Unflying juggernaut with immense health but slower movement. | No |
| 9 | [The Hermit](ARCANA_GUIDE.md#09--the-hermit-tarothermit) | Cattleya | Fragile investigator who marks enemies and commands star-bolts. | Yes |
| 10 | [Wheel of Fortune](ARCANA_GUIDE.md#10--wheel-of-fortune-tarotwheeloffortune) | Original card archetype | True random fate-roll with both boons and punishing outcomes. | Yes |
| 11 | [Justice](ARCANA_GUIDE.md#11--justice-tarotjustice) | Audrey Hall | Mental restraint and group support, but weak direct melee damage. | Yes |
| 12 | [The Hanged Man](ARCANA_GUIDE.md#12--the-hanged-man-tarothangedman) | Alger Wilson | Storm-call that slows foes, keen in water, vulnerable in direct combat. | Yes |
| 13 | [Death](ARCANA_GUIDE.md#13--death-tarotdeath) | Original card archetype | Soul-harvesting survivor who recovers by defeating threats. | Yes |
| 14 | [Temperance](ARCANA_GUIDE.md#14--temperance-tarottemperance) | Sharron | Wraith tactician who fades from sight but suffers a frail body. | Yes |
| 15 | [The Devil](ARCANA_GUIDE.md#15--the-devil-tarotdevil) | Original card archetype | A risky infernal bargain: short power spikes, hunger and sunlight curses. | Yes |
| 16 | [The Tower](ARCANA_GUIDE.md#16--the-tower-tarottower) | Original card archetype | Disaster-themed crowd-control specialist who pays for recklessness. | Yes |
| 17 | [The Star](ARCANA_GUIDE.md#17--the-star-tarotstar) | Leonard Mitchell | Nightwatcher who obscures enemies and thrives beyond daylight. | Yes |
| 18 | [The Moon](ARCANA_GUIDE.md#18--the-moon-tarotmoon) | Emlyn White | Sanguine medicine and nocturnal mastery, weakened beneath the sun. | Yes |
| 19 | [The Sun](ARCANA_GUIDE.md#19--the-sun-tarotsun) | Derrick Berg | Purifying defender whose radiance falters away from sunlight. | Yes |
| 20 | [Judgement](ARCANA_GUIDE.md#20--judgement-tarotjudgement) | Xio Derecha | Grounded arbiter who marks targets and stands her ground. | No |
| 21 | [The World](ARCANA_GUIDE.md#21--the-world-tarotworld) | Klein Moretti as Gehrman Sparrow | Aggressive hunter persona of Klein: enemy marks, precision and evasion. | Yes |

## Project structure

```text
generate.py                 Original deterministic Python source generator
ARCANA_GUIDE.md             Full 22-card lore, personalities and ability descriptions
docs/INSTALLATION.md        Server installation, controls and troubleshooting
docs/BALANCE.md             Combat, gliding and multiplayer balance notes
docs/DEVELOPMENT.md         Format, modifications and extension guide
tests/test_pack.py          Automated pack integrity contracts
.github/workflows/datapack.yml   Build, test, attach downloadable ZIPs, sync source
datapacks/only/             Generated replace=true datapack, after build sync
datapacks/addon/            Generated replace=false datapack, after build sync
output/                     Local generated ZIPs (gitignored)
```

## Rebuild and validate locally

Requires **Python 3**; there are no external Python dependencies.

```bash
python3 generate.py
python3 -m unittest discover -s tests -v
python3 tools/unpack_generated.py
```

Build outputs are under `output/`. Source JSON copies under `datapacks/` are generated from `generate.py`; **edit the generator**, not the generated copies, to avoid changes being overwritten. GitHub Actions validates changes and publishes a downloadable artifact for each successful run.

## What this pack does and does not do

- Does: vanilla-compatible Origins/Apoli datapack powers, 22 distinct origins, active G/V abilities, strengths/weaknesses, gliding, area effects, projectiles and chance-based effects.
- Does not: add new Fabric mod jars, new mobs/models/textures, admin command execution, true puppet AI, creative flight, or cinematic client-only visual effects.
- Testing: structural tests passed locally, but **we have not yet run a full in-game Fabric/Origins 1.4.1 acceptance test**. Verify abilities on a **backup test world** before using on an established multiplayer save.

## References and acknowledgements

- [Origins 1.4.1 documentation](https://origins.readthedocs.io/en/1.4.1/)
- [Official Origins example datapacks](https://github.com/apace100/origins-example-packs)
- [Lord of the Mysteries wiki — Tarot Club members](https://lordofmysteries.wiki.gg/wiki/Tarot_Club/List_of_Members)
- [Pathways](https://lordofmysteries.wiki.gg/wiki/Pathways) and [Major Arcana](https://lordofmysteries.wiki.gg/wiki/Tarot_Cards)
- Existing repository license: [MIT](LICENSE).

Please report exact Minecraft/Fabric/Origins versions, the console error, and the card/power involved when filing a bug.
