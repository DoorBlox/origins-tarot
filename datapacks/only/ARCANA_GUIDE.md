# The Tarot Club — 22 Major Arcana Origins

**Minecraft 1.18.2 • Fabric • Origins 1.4.1 • pack_format 9**

Fan-made reinterpretations of *Lord of the Mysteries* and *Circle of Inevitability* concepts for a Minecraft multiplayer server; not an official adaptation.

## Installation (Pterodactyl / play.hosting)

1. Back up your test world or final SMP before making changes.
2. Stop the Minecraft server. Do **not** put this ZIP in `/mods`.
3. Upload **only one of the two ZIP versions** into `<world-name>/datapacks/` (for your current test world: `tarot-world-test/datapacks/`).
4. Start server; run `datapack list` and confirm this pack is enabled. If server already running, `reload` is possible, but a stop/start is safer for the initial install.
5. Run `origin set <player> origins:origin tarot:fool` to test the Fool; replace `fool` with any ID below.
6. Once verified, transfer the ZIP to the **final** world's `datapacks` folder. Each world has its own datapacks.

These are server-side datapack JSON files: players only need the same Origins mod and Fabric API as the server. No KubeJS script or other custom Origins addon is required.

### Elytra and controls

**18 / 22 cards have a real Origins built-in Elytra-flight power**. Wings are rendered using the normal Elytra appearance. You do not need to equip an Elytra; this is **gliding**, not creative flight. Start falling, then press Jump again to enter glide mode. Firework rockets can still be used in normal Elytra flight.
Primary ability: `key.origins.primary_active` (normally **G**). Secondary ability: `key.origins.secondary_active` (normally **V**). Change keys under Minecraft Controls if needed.
The power screen lists each benefit and drawback with its cooldown.

### Design and PvP warnings

- The 22 tarot cards are not canonically the 22 Standard Pathways. Card names are member codenames; this pack combines canon members with original card concepts.
- The Fool and the World represent two personae of the **same** character, Klein Moretti, but are deliberately distinct playable builds.
- The Empress and Chariot references are Book Two / *Circle of Inevitability* spoilers.
- **Area-of-effect abilities affect all nearby living targets, including teammates, villagers, pets, and enemy players.** This deliberate cost matters in SMP battles; use cautiously.
- No admin command execution, item duplication, terrain destruction, or KubeJS privileges are used by this datapack.
- This pack appends all 22 cards to the existing Origins selection layer (`replace:false`). It will not replace existing vanilla or other custom Origins.
- The pack has been structurally checked; **live in-game behavior has not been tested in your server**. Begin with your temporary test world, inspect the server log, and test abilities one by one.

## The 22 cards — personalities, powers, weaknesses

### 00 — The Fool (`tarot:fool`)

- **Lore basis:** Klein Moretti; Fool pathway influence. **Canon**.
- **Personality:** Careful, compassionate, theatrical; triumphs by preparation rather than brute force.
- **Playstyle:** Cautious trickster and escape artist who manipulates the fight without dominating it.
- **Primary (G):** Gray Fog Masquerade — G: Hide yourself for 6s, gain Speed I for 6s; costs hunger. Cooldown: 21s.
- **Secondary (V):** Marionette Thread — V: Sightline curse on one target within 14 blocks: heavy slowness and glowing. Cooldown: 17s.
- **Special traits:** Seer Instinct — Every 14s, your next successful melee hit briefly weakens its target.
- **Weakness:** Drawback: Your cautious body has one fewer heart.
- **Movement:** **Built-in Elytra glide**.

### 01 — The Magician (`tarot:magician`)

- **Lore basis:** Fors Wall; Door pathway influence. **Canon**.
- **Personality:** Helpful, imaginative, comfort-loving writer, reluctant to take unnecessary risks.
- **Playstyle:** Portal traveler with a reliable short-range escape and vertical mobility.
- **Primary (G):** Doorstep — G: Throw a summoned ender pearl to travel through space. The normal ender-pearl damage still applies. Cooldown: 21s.
- **Secondary (V):** Traveler's Updraft — V: Leap upward into an Elytra glide; 24s cooldown. Cooldown: 24s.
- **Special traits:** Traveler's Stride — Travelers move 10% faster on land.
- **Weakness:** Drawback: You deal 12% less melee damage.
- **Movement:** **Built-in Elytra glide**.

### 02 — The High Priestess (`tarot:high_priestess`)

- **Lore basis:** Original card archetype; White Tower / Hermit pathway influence. **Original**.
- **Personality:** Observant, enigmatic, patient; carries forbidden insight with uncomfortable certainty.
- **Playstyle:** Knowledge and enemy revelation, balanced by fragility.
- **Primary (G):** Unsealed Sight — G: Illuminate nearby living creatures with Glowing for 9s; may reveal allies. Cooldown: 15s.
- **Secondary (V):** Foreknowledge — V: Gain Night Vision and Resistance I for 10s. Cooldown: 23s.
- **Special traits:** Arcane Literacy — Gain 25% more experience from orbs.
- **Weakness:** Drawback: 2 hearts fewer maximum health.
- **Movement:** **Built-in Elytra glide**.

### 03 — The Empress (`tarot:empress`)

- **Lore basis:** Franca Roland; Demoness pathway influence. **Canon (Book Two)**.
- **Personality:** Expressive, brave, resourceful; turns precarious circumstances into possibilities.
- **Playstyle:** Mirror-themed witch of toxins, beauty, misdirection and vulnerability.
- **Primary (G):** Mirror Plague — G: Afflict nearby living entities with Poison I and Slowness I. Allies are not protected. Cooldown: 22.5s.
- **Secondary (V):** Glass Reflection — V: Vanish for 6s and gain Speed II for 5s. Cooldown: 25s.
- **Special traits:** Witch's Grace — Movement is 8% faster.
- **Weakness:** Drawback: Take 16% more damage from attacks.
- **Movement:** **Built-in Elytra glide**.

### 04 — The Emperor (`tarot:emperor`)

- **Lore basis:** Original card archetype; Black Emperor pathway influence. **Original**.
- **Personality:** Proud, calculating, disciplined; seeks absolute order even at a personal cost.
- **Playstyle:** Grounded tank who controls crowds and resists retaliation.
- **Primary (G):** Imperial Decree — G: Slowness II and Weakness I to nearby creatures. Everyone nearby pays for disobedience. Cooldown: 21s.
- **Secondary (V):** Royal Bulwark — V: Resistance II for 8s; movement slows during the decree. Cooldown: 26s.
- **Special traits:** Armored Sovereign — Permanent +3 armor points.
- **Weakness:** Drawback: Your speed is reduced by 12%. No astral wings.
- **Movement:** **Grounded (no built-in glide)**.

### 05 — The Hierophant (`tarot:hierophant`)

- **Lore basis:** Original card archetype; White Tower / Sun pathway influence. **Original**.
- **Personality:** Reverent scholar and counselor; rewards planning, ritual and shared knowledge.
- **Playstyle:** Stationary support scholar who sees the enemy and grants blessings.
- **Primary (G):** Sacred Reading — G: Reveal nearby living beings and give yourself Haste II for 12s. Cooldown: 23s.
- **Secondary (V):** Shared Blessing — V: Grant Regeneration I for 6s to everyone within 6 blocks, including enemies; heal yourself by 1 heart. Cooldown: 30s.
- **Special traits:** Ritual Scholar — You learn 35% faster from experience orbs.
- **Weakness:** Drawback: 2 fewer hearts; no astral wings.
- **Movement:** **Grounded (no built-in glide)**.

### 06 — The Lovers (`tarot:lovers`)

- **Lore basis:** Original card archetype; Mother / Visionary pathway influence. **Original**.
- **Personality:** Empathic mediator; values connection, promises and sacrifice.
- **Playstyle:** Support guardian whose healing also benefits enemies if carelessly used.
- **Primary (G):** Promise of Hearts — G: Regeneration II to living entities within 7 blocks, friend or foe. A tactical choice. Cooldown: 25s.
- **Secondary (V):** Sacrificial Vow — V: Gain Absorption II for 10s but Weakness I for 6s; costs hunger. Cooldown: 23s.
- **Special traits:** Light of Togetherness — A modest +1 heart of resilience.
- **Weakness:** Drawback: You deal 17% less melee damage.
- **Movement:** **Built-in Elytra glide**.

### 07 — The Chariot (`tarot:chariot`)

- **Lore basis:** Lumian Lee; Red Priest pathway influence. **Canon (Book Two)**.
- **Personality:** Defiant, sly, courageous and protective; channels unrest into action.
- **Playstyle:** High-mobility warlock whose powerful assault demands food and restraint.
- **Primary (G):** War March — G: Strength II and Speed II for 9s, at a serious hunger cost. Cooldown: 25s.
- **Secondary (V):** Ironblood Volley — V: Fire three non-retrievable arrows in a rapid volley. Cooldown: 16s.
- **Special traits:** Flame Within — Fire cannot burn a veteran of the Red Priest.
- **Weakness:** Drawback: While submerged in water, you suffer Slowness II.
- **Movement:** **Built-in Elytra glide**.

### 08 — Strength (`tarot:strength`)

- **Lore basis:** Original card archetype; Twilight Giant pathway influence. **Original**.
- **Personality:** Steadfast, courageous, protective; meets danger directly.
- **Playstyle:** Unflying juggernaut with immense health but slower movement.
- **Primary (G):** Lionheart — G: Strength II and Resistance II for 8s; you also become slow for 7s. Cooldown: 28s.
- **Secondary (V):** Earthshaker — V: Stagger nearby creatures with Slowness III and Weakness I. Cooldown: 20s.
- **Special traits:** Giant Blood — Permanent +3 hearts.; Iron Hide — Additional +2 armor points.
- **Weakness:** Drawback: Move 16% slower. You cannot glide without an item.
- **Movement:** **Grounded (no built-in glide)**.

### 09 — The Hermit (`tarot:hermit`)

- **Lore basis:** Cattleya; Hermit pathway influence. **Canon**.
- **Personality:** Brilliant, experienced and guarded; still yearns for belonging.
- **Playstyle:** Fragile investigator who marks enemies and commands star-bolts.
- **Primary (G):** Eyes of Mystery Prying — G: Mark a creature at sightline range 18 with Glowing and Weakness II. Cooldown: 15s.
- **Secondary (V):** Astral Scriptorium — V: Manifest two spectral arrows of starlight. Cooldown: 19s.
- **Special traits:** Hidden Scholarship — Gain 30% more experience from orbs.
- **Weakness:** Drawback: 1 fewer heart.
- **Movement:** **Built-in Elytra glide**.

### 10 — Wheel of Fortune (`tarot:wheel_of_fortune`)

- **Lore basis:** Original card archetype; Wheel of Fortune pathway influence. **Original**.
- **Personality:** Impulsive, curious and dangerously optimistic; accepts risk as a principle.
- **Playstyle:** True random fate-roll with both boons and punishing outcomes.
- **Primary (G):** Fate's Sixfold Cast — G: Roll one of six equal outcomes: Speed II, Strength II, Regeneration II, Blindness, Hunger II, or Poison I. Cooldown: 14s.
- **Secondary (V):** Borrowed Luck — V: Risk a second, milder gamble (either Resistance I or Slowness II). Cooldown: 19s.
- **Special traits:** Fortune's Step — Permanent +7% walking speed.
- **Weakness:** Drawback: Receive 12% more damage.
- **Movement:** **Built-in Elytra glide**.

### 11 — Justice (`tarot:justice`)

- **Lore basis:** Audrey Hall; Visionary pathway influence. **Canon**.
- **Personality:** Compassionate, intelligent and composed; listens before judging.
- **Playstyle:** Mental restraint and group support, but weak direct melee damage.
- **Primary (G):** Psychological Stillness — G: Calm living entities within 8 blocks with Weakness II and Slowness I. Cooldown: 19s.
- **Secondary (V):** Therapist's Shelter — V: Regeneration II for nearby living beings including foes; grant yourself Absorption I. Cooldown: 30s.
- **Special traits:** Measured Heart — A calm mind grants +1 heart.
- **Weakness:** Drawback: Melee attacks inflict 20% less damage.
- **Movement:** **Built-in Elytra glide**.

### 12 — The Hanged Man (`tarot:hanged_man`)

- **Lore basis:** Alger Wilson; Tyrant, later Hanged Man pathway influence. **Canon**.
- **Personality:** Strategic, ambitious and suspicious; commands the storm with discipline.
- **Playstyle:** Storm-call that slows foes, keen in water, vulnerable in direct combat.
- **Primary (G):** Tempest Canticle — G: The air thickens; Slowness II on nearby living entities while you gain Resistance I. Cooldown: 24s.
- **Secondary (V):** Sea-Lord's Javelin — V: Fire two swift spectral bolts. Cooldown: 15s.
- **Special traits:** Experienced Sailor — You travel 9% faster across land.; Sea Pressure — Successful strikes briefly slow victims, 11s internal cooldown.
- **Weakness:** Drawback: One fewer heart.
- **Movement:** **Built-in Elytra glide**.

### 13 — Death (`tarot:death`)

- **Lore basis:** Original card archetype; Death pathway influence. **Original**.
- **Personality:** Solemn, reflective and merciful in finality; sees every ending as a beginning.
- **Playstyle:** Soul-harvesting survivor who recovers by defeating threats.
- **Primary (G):** Grave Quietus — G: Send out an aura of Wither I for 4s, affecting everyone nearby. Cooldown: 25s.
- **Secondary (V):** Return from the Brink — V: Regeneration II and Resistance I for 7s; costs a heavy portion of hunger. Cooldown: 31s.
- **Special traits:** Harvest the Departed — Recover one heart whenever you defeat a creature, at most once per 8s.
- **Weakness:** Drawback: In direct sunlight, you suffer Weakness I.
- **Movement:** **Built-in Elytra glide**.

### 14 — Temperance (`tarot:temperance`)

- **Lore basis:** Sharron; Chained pathway influence. **Canon (Book Two)**.
- **Personality:** Quiet, reserved, self-controlled; refuses to be ruled by desire.
- **Playstyle:** Wraith tactician who fades from sight but suffers a frail body.
- **Primary (G):** Wraith Form — G: Invisibility and Resistance I for 6s, but self-inflicted Weakness for 6s. Cooldown: 21.5s.
- **Secondary (V):** Quiet Possession — V: Fix the target you face with Slowness III and Weakness II. Cooldown: 22.5s.
- **Special traits:** Eyes Behind Glass — Permanent Night Vision.
- **Weakness:** Drawback: 2 fewer hearts.
- **Movement:** **Built-in Elytra glide**.

### 15 — The Devil (`tarot:devil`)

- **Lore basis:** Original card archetype; Abyss pathway influence. **Original**.
- **Personality:** Charismatic and manipulative; every gift has an ugly hidden price.
- **Playstyle:** A risky infernal bargain: short power spikes, hunger and sunlight curses.
- **Primary (G):** Forbidden Bargain — G: Strength III and Speed II for 7s, but suffer Poison I and exhausting hunger. Cooldown: 30s.
- **Secondary (V):** Tempting Whispers — V: Nearby beings suffer Weakness II and Hunger I; this affects allies. Cooldown: 19s.
- **Special traits:** Infernal Heritage — You do not burn in fire.
- **Weakness:** Drawback: Direct sunlight inflicts Weakness II.
- **Movement:** **Built-in Elytra glide**.

### 16 — The Tower (`tarot:tower`)

- **Lore basis:** Original card archetype; Tyrant / Red Priest pathway influence. **Original**.
- **Personality:** Catastrophic, uncompromising and unpredictable; breaks the safe path.
- **Playstyle:** Disaster-themed crowd-control specialist who pays for recklessness.
- **Primary (G):** Collapse of Certainty — G: Nearby targets become blind for 3s and slow for 5s. You are not protected from retaliation. Cooldown: 24s.
- **Secondary (V):** Rising Ruin — V: Violent skyward launch, usable before gliding. Cooldown: 21s.
- **Special traits:** Shatterer — Your melee blows are 9% stronger.
- **Weakness:** Drawback: You take 20% more damage.
- **Movement:** **Built-in Elytra glide**.

### 17 — The Star (`tarot:star`)

- **Lore basis:** Leonard Mitchell; Darkness pathway influence. **Canon**.
- **Personality:** Casual and poetic, yet perceptive and brave when it counts.
- **Playstyle:** Nightwatcher who obscures enemies and thrives beyond daylight.
- **Primary (G):** Midnight Poetry — G: Blindness and Slowness I to nearby targets, revealing the advantage of darkness. Cooldown: 21s.
- **Secondary (V):** Nightwatcher's Refuge — V: Invisibility and Night Vision for 8s. Cooldown: 24s.
- **Special traits:** Sleepless Gaze — You see clearly in darkness.
- **Weakness:** Drawback: Direct sunlight gives Slowness I.
- **Movement:** **Built-in Elytra glide**.

### 18 — The Moon (`tarot:moon`)

- **Lore basis:** Emlyn White; Moon pathway influence. **Canon**.
- **Personality:** Proud, eccentric and sheltered; gradually learns responsibility.
- **Playstyle:** Sanguine medicine and nocturnal mastery, weakened beneath the sun.
- **Primary (G):** Scarlet Medicine — G: Regeneration II for 9s, but must spend substantial energy. Cooldown: 24s.
- **Secondary (V):** Blood Moon Awakening — V: Strength II and Night Vision at night or indoors; in direct sun, only Resistance I. Cooldown: 24s.
- **Special traits:** Sanguine Eyes — Permanent Night Vision.
- **Weakness:** Drawback: In direct sun, you are weakened.
- **Movement:** **Built-in Elytra glide**.

### 19 — The Sun (`tarot:sun`)

- **Lore basis:** Derrick Berg; Sun pathway influence. **Canon**.
- **Personality:** Sincere, loyal and hopeful; carries light to dark places.
- **Playstyle:** Purifying defender whose radiance falters away from sunlight.
- **Primary (G):** Unshadowed Pulse — G: Glowing on nearby creatures and Strength I for yourself. Allies are visible too. Cooldown: 21s.
- **Secondary (V):** Radiant Shelter — V: Regeneration II, Resistance I, and brief illumination (Night Vision). Cooldown: 27s.
- **Special traits:** Vessel of Dawn — Fire has no power over you.
- **Weakness:** Drawback: Whenever you are away from sunlight, you suffer Slowness I.
- **Movement:** **Built-in Elytra glide**.

### 20 — Judgement (`tarot:judgement`)

- **Lore basis:** Xio Derecha; Justiciar pathway influence. **Canon**.
- **Personality:** Principled, determined and stern but kind; values a fair sentence.
- **Playstyle:** Grounded arbiter who marks targets and stands her ground.
- **Primary (G):** Sentence Pronounced — G: Target you are looking at becomes Slowness III and Glowing. Cooldown: 19s.
- **Secondary (V):** Writ of Protection — V: Resistance II and Strength I for 7s. You must stand your ground. Cooldown: 25s.
- **Special traits:** Marshal's Plate — Gain +3 armor points.
- **Weakness:** Drawback: Move 10% slower; no astral wings.
- **Movement:** **Grounded (no built-in glide)**.

### 21 — The World (`tarot:world`)

- **Lore basis:** Klein Moretti as Gehrman Sparrow; Fool pathway influence. **Canon (same person as Fool)**.
- **Personality:** Cold-seeming, daring and ruthlessly efficient; secretly protective.
- **Playstyle:** Aggressive hunter persona of Klein: enemy marks, precision and evasion.
- **Primary (G):** Hunting Notice — G: Mark a target within 16 blocks with Glowing and Weakness II. Cooldown: 13s.
- **Secondary (V):** Faceless Withdrawal — V: Vanish for 5s with Speed II and Absorption I, costing hunger. Cooldown: 24s.
- **Special traits:** Bounty Hunter — You strike 10% harder in melee.
- **Weakness:** Drawback: One fewer heart.
- **Movement:** **Built-in Elytra glide**.

## How to make and modify a custom Origin

Each origin is a JSON under `data/tarot/origins/<id>.json`. The `powers` array references power JSONs stored under `data/tarot/powers/<id>/*.json`.
The layer `data/origins/origin_layers/origin.json` appends our 22 origin IDs. You can tweak numbers (durations are in ticks; 20 ticks = 1 second) by editing the JSON and zipping the datapack again with `pack.mcmeta` at the archive root.

Example origin (trimmed):

```json
{
  "powers": [
    "tarot:fool/primary",
    "tarot:fool/secondary",
    "tarot:fool/passive",
    "tarot:fool/drawback",
    "tarot:fool/wings"
  ],
  "icon": "minecraft:totem_of_undying",
  "name": "The Fool",
  "description": "A careful trickster."
}
```

Example custom power (trimmed):

```json
{
  "type": "origins:active_self",
  "name": "Veil of Fog",
  "description": "Invisibility for 6 seconds, with a cooldown.",
  "entity_action": {
    "type": "origins:apply_effect",
    "effect": {
      "effect": "minecraft:invisibility",
      "duration": 120,
      "amplifier": 0,
      "show_particles": true
    }
  },
  "cooldown": 420,
  "key": {
    "key": "key.origins.primary_active"
  },
  "hud_render": {
    "should_render": true,
    "bar_index": 2
  }
}
```

## Inspiring examples to learn from

- The Origins developer example repository shows complete custom Origins (`aerum_origin`, `deepling_origin`, `salamander_origin`), changing powers (`elytrian_boost`) and even adding a whole second selection layer (`second_layer`): https://github.com/apace100/origins-example-packs
- Origins++ showcases a large roster of more than 100 playable Origins; examine its designs as balance inspiration, not as a technical dependency: https://modrinth.com/mod/origins-plus-plus
- Origins: Starborne is an example of a themed 1.18.2-era custom Origin: https://www.curseforge.com/minecraft/mc-mods/origins-starborne
- To go beyond JSON powers, custom textures need an optional resource pack; truly novel mechanics may require a Java mod or script integration. This pack deliberately stays within built-in powers for compatibility.

## Canon/source boundaries and references

Core Origins 1.4.1 documentation: https://origins.readthedocs.io/en/1.4.1/
Example packs from Origins developers: https://github.com/apace100/origins-example-packs
List of Tarot Club members and their actual pathways: https://lordofmysteries.wiki.gg/wiki/Tarot_Club/List_of_Members
22 Standard Pathways: https://lordofmysteries.wiki.gg/wiki/Pathways
Tarot Major Arcana: https://lordofmysteries.wiki.gg/wiki/Tarot_Cards
Character personality/reference articles: https://lordofmysteries.wiki.gg/wiki/Klein_Moretti ; https://lordofmysteries.wiki.gg/wiki/Audrey_Hall ; https://lordofmysteries.wiki.gg/wiki/Alger_Wilson ; https://lordofmysteries.wiki.gg/wiki/Derrick_Berg ; https://lordofmysteries.wiki.gg/wiki/Fors_Wall ; https://lordofmysteries.wiki.gg/wiki/Cattleya ; https://lordofmysteries.wiki.gg/wiki/Emlyn_White
This is fan-created gameplay translation, not a claim that these skills or original personas are canonical.

## Testing checklist

1. All 22 cards appear in origin selection.
2. Switch between two origins with the server command; confirm G and V actions and cooldowns.
3. For wings, drop from a ledge and press jump again; verify gliding works with and without chest armor.
4. Test exposed-to-sun weaknesses, submerged-in-water weakness, team AoE, and no-flight cards.
5. Check after death/respawn, server restart, Nether travel, and returning to the Overworld.
6. Watch console and RAM on 3GB play.hosting; no new dependencies are required.

