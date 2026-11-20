# The Tarot Club — V3 Path of Ascension

**Version:** V3 alpha · **Minecraft Java:** 1.18.2 · **Loader:** Fabric · **Origins:** 1.4.1 · **Pack format:** 9.  
**Design:** 22 Major Arcana, two progression tracks at most, 18 native Elytra gliders. A card name is not necessarily the corresponding *Lord of the Mysteries* Beyonder pathway.

> This pack is designed for a **test world** first. The JSON and generated functions are checked automatically, but no local Minecraft client/server acceptance run has been performed. Do not claim production stability until players have verified quests, swaps, rituals, and server logs.

## Install / upgrade from working V2

1. **Back up your world**, including `level.dat`, `playerdata/`, `advancements/`, and the existing V2 ZIP. Also back up `world/data/scoreboard.dat` because V3 saves progression in the world's scoreboards.
2. Stop the Minecraft server. Choose **ONE**: `The_Tarot_Club_V3_Ascension_ONLY_1.18.2.zip` replaces vanilla Origins choices, while `The_Tarot_Club_V3_Ascension_ADDON_1.18.2.zip` adds the 22 cards alongside standard Origins.
3. Remove the old V2 ZIP from `<level-name>/datapacks/` (**do not run V2 and V3 together**) and upload the selected V3 ZIP without extracting its contents. Ensure `pack.mcmeta` is at the top of that ZIP.
4. Start the server. In the console use `datapack list`, then `/function tarot_progress:info/help` for an OP/admin smoke test. If replacing an existing pack, players should **retain their current Arcana**. V3 automatically enrolls each player who holds one of the 22 Tarot Origins.
5. Players can use `/trigger tc_help`, `/trigger tc_status`, and `/trigger tc_cards`; vanilla keybinds G/V still work for the selected V2 origin.
6. **Test one player first** with a fresh test world, a second with an existing V2 origin, and a third after a death and reconnect. Check the console for unknown commands or invalid advancement triggers. The first registration requires the Origins `/origin has origin` command to report the active card.

**Dependencies:** Fabric 1.18.2 + Origins 1.4.1 and its usual Fabric dependencies; **KubeJS not required** for this V3 datapack. The existing passive-first V2 powers, G/V skills, and Elytra mechanics are bundled in the ZIP.

### Ritual altar

Place a **lectern directly on top of crying obsidian**. Stand on the lectern while grounded. Unlike a lodestone, a lectern is accessible for early-Sequence ritual play. You cannot perform ascension, attunement or altar switches while in combat or while fall-flying. This is a check on the actual blocks underneath the player, not a decorative structure generated in the world.

## Player commands (no OP permissions needed)

| Command | Purpose |
|---|---|
| `/trigger tc_help` | In-game instruction summary |
| `/trigger tc_cards` | Numbered 1–22 Arcana list |
| `/trigger tc_status` | Primary/secondary card IDs, both Sequence levels, Acting marks, travel proofs and cooldowns |
| `/trigger tc_ascend` | At the altar, digest the next Sequence using Acting marks and offerings |
| `/trigger tc_trialcmd set <id>` | At primary Sequence 4 or better, commit to one second Arcana trial |
| `/trigger tc_unlock` | After the second trial, unlock the chosen Arcana at Sequence 9 |
| `/trigger tc_swap set 1` | Equip primary Arcana |
| `/trigger tc_swap set 2` | Equip secondary Arcana |
| `/trigger tc_meditate` | Restore stability at the altar for four amethyst shards (five-minute cooldown) |

Commands are server-authorized. Scoreboards track progress per player and persist across deaths and logout. If a command returns "You cannot trigger this objective yet", wait one second after the world loads or after the previous command. **Do not OP players just to use these.**

## The two-card rule

- You begin with **one fully equipped Arcana**, at **Sequence 9**. The original V2 core buffs and drawbacks stay active as before.
- Your Sequences descend from 9 toward 0. Sequence **8**, **7**, **6**, and **5** add cumulative, bounded automatic perks. Sequence **4** unlocks the *Second Awakening* questline.
- Your **primary** must reach Sequence 4 (or lower) and you must have visited the **Nether and End at least once after installing V3**. At the altar run `/trigger tc_trialcmd set <id>`, selecting any different card from `/trigger tc_cards`.
- For the chosen second Arcana, complete **four alternate Acting proofs** (A / B / A / B); then offer **16 amethyst shards, 4 ender pearls and 1 ghast tear** and run `/trigger tc_unlock` at the altar.
- Secondary Arcana starts at Sequence **9** and levels **independently**. Your old primary retains its Sequence and marks. You may have **at most two** Arcana; this version does not let players discard and reselect a third.
- At primary Sequence **4**, switches require the altar. At primary Sequence **3** or lower, switching can be done from anywhere **when grounded**. Every successful switch imposes a **10-minute online-time cooldown**, prevents switching in combat (10 seconds after dealing/taking damage), and prevents switching while fall-flying.
- At active Sequence **2** or lower, your currently active card gets **one reduced passive Echo** from the inactive card. It never gets both complete Origins simultaneously.
- At active Sequence **1** or lower, you also receive **one Resonance passive**. Twelve lore-themed combinations have curated Resonance powers; other pairings receive a small universal fallback. This is intentionally **not unrestricted fusion**.
- Sequence **0** is an endgame prestige and a modest Luck bonus, not god mode or permanent creative flight.

**Loss of Control / stability:** Everyone starts at 100 stability. Successful Acting restores 4 stability points; a trial proof restores 2. Ascension costs 12; switching costs 4. At 20 stability or lower you suffer temporary Weakness. You must have at least 25 stability to attempt an advancement. To recover, stand at the altar and use `/trigger tc_meditate`; spend four amethyst shards for up to +30 stability, once every five online minutes. The system never causes permanent deletion or forced death.

When switching, V3 calls Origins' `/origin set` for the same **one** origin layer, removes its own previously granted tier/Echo/Resonance powers using unique Apoli source IDs, then regrants only the new active card's appropriate bonuses. Core V2 origin powers are **never** globally cleared.

## How Acting works

Every Arcana has two distinct themed actions: **A** requires picking up/carrying the specified object (detected on inventory changes); **B** requires an actual combat, trade, breeding, consumable, or dimensional event. The two alternate. An Acting success gives one digestion mark, with a **two-minute online-time cooldown**. Neither AFK time alone nor running `/trigger` grants marks. You may bank at most 20 marks per character; each Sequence spends the required number. The second-Arcanum trial uses an **independent four-mark proof track**, subject to the same action cooldown.

| # | Arcana | Inspiration (not always canonical club member) | Acting A — acquire/handle | Acting B |
|---:|---|---|---|---|
| 1 | The Fool | Klein / Seer–Clown | compass | kill spider |
| 2 | The Magician | Fors / Door | ender pearl | dimension the nether |
| 3 | The High Priestess | Original / White Tower–Hermit | book | trade |
| 4 | The Empress | Franca / Demoness | spider eye | kill spider |
| 5 | The Emperor | Original / Black Emperor | shield | kill pillager |
| 6 | The Hierophant | Original / ritual scholar | lectern | trade |
| 7 | The Lovers | Original / Mother–Visionary | wheat | breed |
| 8 | The Chariot | Lumian / Red Priest | flint and steel | kill blaze |
| 9 | Strength | Original / Twilight Giant | iron pickaxe | kill zombie |
| 10 | The Hermit | Cattleya / Hermit | lapis lazuli | trade |
| 11 | Wheel of Fortune | Original / Monster | rabbit foot | kill skeleton |
| 12 | Justice | Audrey / Visionary | honey bottle | trade |
| 13 | The Hanged Man | Alger / Tyrant | kelp | kill drowned |
| 14 | Death | Original / Death | bone | kill skeleton |
| 15 | Temperance | Sharron / Chained–Wraith | glass bottle | kill spider |
| 16 | The Devil | Original / Abyss | blaze powder | kill ghast |
| 17 | The Tower | Original / catastrophe | tnt | kill creeper |
| 18 | The Star | Leonard / Darkness–Sleepless | clock | kill phantom |
| 19 | The Moon | Emlyn / Moon–Sanguine | redstone | consume cooked beef |
| 20 | The Sun | Derrick / Sun | torch | kill zombie |
| 21 | Judgement | Xio / Justiciar | iron bars | kill pillager |
| 22 | The World | Gehrman Sparrow / Fool | crossbow | kill pillager |

## Sequence costs and milestones

| Advancement | Acting marks | Required ritual items | Unlock |
|---|---:|---|---|
| S9 → S8 | 1 | 6× amethyst shard, 8× lapis lazuli | First Digestion passive |
| S8 → S7 | 2 | 12× copper ingot, 2× glow ink sac | Specialized passive |
| S7 → S6 | 2 | 8× gold ingot, 2× ender pearl | Mid-Sequence mastery |
| S6 → S5 | 3 | 6× blaze powder, 1× ghast tear | Ritual-tempered passive |
| S5 → S4 | 3 | 4× diamond, 16× amethyst shard | Second Awakening eligibility |
| S4 → S3 | 4 | 1× netherite scrap, 2× ender eye | Portable switching |
| S3 → S2 | 4 | 2× ancient debris, 4× phantom membrane | Echo access |
| S2 → S1 | 5 | 1× nether star, 8× ender pearl | Resonance access |
| S1 → S0 | 6 | 2× nether star, 1× enchanted golden apple | Apotheosis prestige |

**Costs are consumed only if all required items and marks are present.** Natural V2 drawbacks (diet, sleeping, villager trade restrictions, and so on) are preserved. In-game achievement descriptions reflect Minecraft activities rather than canonical Sequences.

## Curated high-sequence Resonances

| Arcana combination | Granted Resonance power |
|---|---|
| Fool + Magician | Hidden Door |
| Chariot + Empress | Calamity |
| Star + Death | Midnight Requiem |
| Emperor + Judgement | Absolute Decree |
| Sun + Moon | Eclipse |
| High Priestess + Hermit | Forbidden Library |
| Lovers + Justice | Gentle Heart |
| Magician + Hanged Man | Storm Gate |
| Fool + World | One Soul |
| Strength + Tower | Ruinborn |
| Temperance + Devil | Shadow Pact |
| Fool + Wheel Of Fortune | Fated Vision |

Other combinations get **Unbound Resonance** (+3% walking speed), rather than an unbalanced merger. Hybrid powers have ordinary cooldowns and are revoked when no longer eligible.

## Safety, troubleshooting, rollback

- **Existing player migration:** players with a Tarot V2 Origin are enrolled automatically with Sequence 9 on first V3 load. Already-earned Minecraft XP is **not** converted to Acting marks. Visits to other dimensions must be repeated after the upgrade, so the trial evidence is explicit.
- **Status doesn't appear:** `datapack list` and test `/function tarot_progress:info/help` in server console. Use a test account with a Tarot Origin; the pack will not enroll a non-Tarot Origin. Wait a second after joining before using `/trigger`.
- **Advancement doesn't progress:** alternate the listed A and B actions, allow two online minutes, and check which Arcana is currently equipped. A trial's tasks concern the **target** Arcana, even if you're still wearing your primary. A quest action alone may set combat lock temporarily.
- **Swapping fails:** check that the second card is unlocked, use `tc_status` for the cooldown, exit combat for 10 seconds and stand on solid ground. At S4 the altar is mandatory; S3 enables portable switching. No midair Elytra switching.
- **KubeJS compatibility:** the pack intentionally does not require KubeJS. You may install it alongside KubeJS, but test other scripts and packs for scoreboard/advancement conflicts.
- **Area-effect caveat:** existing V2 powers may heal or debuff allies and pets. V3 does not silently change their targeting semantics.
- **Version caveat:** commands here target **1.18.2** and deliberately avoid newer `/execute if dimension`, data components, macros and commands added in later versions.
- **Admin rollback without deleting progression:** run `/function tarot_progress:admin/rollback_all` **before** removing the V3 datapack, to revoke V3-granted tier/Echo/Resonance powers while keeping each player's selected V2 Origin and saved scoreboard scores. Then stop server, remove V3 ZIP, restore backed-up V2 ZIP and start. If you want to erase V3 data permanently, do so only after backing up `scoreboard.dat`; the pack never wipes player scores automatically.
- **Don't call this production verified:** static tests confirm JSON, structural references and basic state rules, but cannot substitute for a running Fabric 1.18.2 acceptance test.

### Maintainer/source notes

`progression/catalog.py` defines the 22 Arcana, acting requirements, per-sequence offerings and pair affinities. `progression/model.py` contains an independently testable reference state machine. `progression/build.py` builds both V3 ZIPs from the existing 22-origin V2 source trees in `datapacks/`. `.github/workflows/ascension.yml` will rebuild and attach both ZIPs to successful runs. Commands are generated as ordinary `.mcfunction` files; no paid or proprietary runtime dependency.

Core technical references: https://origins.readthedocs.io/en/1.4.1/misc/commands/origin/ and https://origins.readthedocs.io/en/1.4.1/misc/commands/power/ and https://origins.readthedocs.io/en/1.4.1/json/origin/.
