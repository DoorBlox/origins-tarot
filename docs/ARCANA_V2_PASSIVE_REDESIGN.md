# The Tarot Club — Passive-First Arcana V2 (Design RFC)

> **Status: DESIGN PROPOSAL, NOT IMPLEMENTED OR MERGED.** This document defines the future balance contract; the current 22-origin datapack remains functional and unchanged on main.

Minecraft Java 1.18.2 · Fabric · Origins 1.4.1 · 22 cards · 18 native Elytra gliders.

## Why the present pack needs changing

The existing V1 pack concentrates most of its distinctive effects into G/V cooldown abilities. Everyday mining, exploration, combat, hunger, farming, caving, and travel often still feel vanilla. Weaknesses too often consist of maximum-health reductions or blanket damage/speed debuffs. A better Origin should change behavior **without pressing any key**.

### Design contract

- Each origin receives **2–4 automatic mechanics**: a foundation that always matters, a conditional or event-driven trait, and sometimes a social/economic specialty.
- Drawbacks should impose a **behavioral decision** or ecosystem constraint, not merely subtraction of hearts. Most are unique to that card.
- Signature G/V abilities survive in a weaker supporting role; an Origin must have an identity even if those keys are never pressed.
- Retain **18 innate Elytra-style gliders**. Emperor, Hierophant, Strength, and Judgement remain grounded. Gliding is not creative flight.
- Positive effects are bounded to avoid AFK farms, PvP permanent Strength/Regeneration, and always-on infinite flight. Proposed values are initial targets; game testing is required.
- This is **lore-inspired**, not literal late-sequence godhood. The card title and the Pathway are different concepts. Some cards have canonical Tarot Club members; the others are original reinterpretations.
- **Book Two spoilers:** Chariot, Empress, and Temperance member status. The Fool and the World refer to separate personas of Klein, not separate people.
- **Implementation tags:** **[D]** = feasible with Origins 1.4.1 datapack powers (after exact-schema verification); **[S]** = requires a lightweight KubeJS/scoreboard helper or another compatible extension. Where [S] is shown, a datapack-only fallback is specified.

## 00 — The Fool (Klein Moretti, Fool / Seer–Clown)

**Role:** Precognitive survivor; tactical scout instead of burst-damage rogue. **Elytra:** yes.

- **[D] Spirit Vision — passive:** while crouching, periodically outline nearby threats (within 10 blocks, 2s pulses). This approximates spiritual observation rather than a wallhack; the glow will be visible to others unless an advanced viewer-specific effect is added.
- **[D] Clown's Balance — passive:** 35% less fall damage and +15% jump height; regular journeys and rooftop escapes feel supernatural.
- **[D] Premonition — reactive passive:** when hit, gain Speed I for 3s (45s internal cooldown); helps escape an ambush without pre-emptive button use.
- **[D] Drawback: Spiritual Expenditure:** sprinting and Elytra travel consume **40% more exhaustion**, so a Seer must provision food and avoid reckless chases. No health-heart penalty.
- **Optional active:** Paper Figurine Substitute, one short invisibility/escape trigger on a long cooldown—not continuous immunity.

**Why it fits:** Klein survives by information, premonition, balance, preparation and escape, not raw physical superiority.

## I — The Magician (Fors Wall, Door)

**Role:** Reliable explorer, courier and escape artist. **Elytra:** yes.

- **[D] Traveler's Body — passive:** 12% faster walking and 70% less fall damage. Gliding makes this a premier exploration origin.
- **[D] Wayfarer's Instinct — passive:** +20% jump height when not submerged; less dependence on repeated launch key use.
- **[S] Door's Mercy — reactive passive:** once every 120s, a near-fatal hit instead gives a short displacement to nearby safe ground. Datapack-only fallback: brief Resistance II + Speed I on first low-health hit; no literal teleport claim.
- **[S] Drawback: Full Moon Ravings:** every eighth Minecraft night, under the open sky, periodic Nausea and reduced mining efficiency. This is a true lunar-cycle restriction. Datapack-only fallback: a milder exposed-night debuff, not incorrectly described as a real full-moon detector.
- **Optional active:** one manually aimed short-range Doorstep teleport/ender pearl.

**Why it fits:** Fors's Door progression emphasizes traversal, while moon-related ravings are a meaningful canon-inspired danger.

## II — The High Priestess (original White Tower / Hermit archetype)

**Role:** Knowledge-specialist and ritual explorer. **Elytra:** yes.

- **[D] Reader's Aptitude — passive:** +35% XP gained from orbs. Enchanting and repair progression become her economy.
- **[D] Ritual Focus — conditional passive:** while carrying a book or enchanted book in the offhand, mine 25% faster and gain low-light visibility.
- **[D] Scripted Insight — passive:** +20% ranged projectile damage while not sprinting, rewarding preparation and composed positioning.
- **[D] Drawback: Dependent on Rituals:** without a book in the offhand, break blocks **20% slower**. This changes inventory, offhand and shield decisions without reducing maximum health.
- **Optional active:** brief reveal of nearby creatures.

**Why it fits:** White Tower and Hermit pathways value reading, ritual, knowledge and careful spellcraft.

## III — The Empress (Franca Roland, Demoness)

**Role:** Covert poisoner and nimble ambusher. **Elytra:** yes.

- **[D] Witch's Venom — reactive passive:** melee hits inflict Poison I for 3s, max once every 12s.
- **[D] Mirror Veil — conditional passive:** crouching in low light gives Invisibility; armor and held items may still be visible, and this is not full invisibility to all server systems.
- **[D] Witch's Grace — passive:** +10% movement speed and immunity to Poison.
- **[D] Drawback: Exposed Reflection:** in direct sunlight, Mirror Veil fails and incoming arrows deal **25% more damage**. A defensive counter based on exposure, not missing hearts.
- **Optional active:** a short decoy/escape, not perpetual burst Strength.

**Why it fits:** The Demoness pathway inspires toxins, invisibility, mirrors and dangerous beauty. The sunlight counter is a gameplay adaptation, not a canonical general weakness.

## IV — The Emperor (original Black Emperor archetype)

**Role:** Frontline ruler who protects territory and refuses to flee. **Elytra:** no.

- **[D] Sovereign's Plate — passive:** +3 armor and +40% knockback resistance.
- **[D] Distorted Authority — reactive passive:** incoming melee hits inflict Slowness I on the aggressor for 2s (14s internal cooldown).
- **[D] Imperial Presence — conditional passive:** while holding a shield, gain another 10% damage resistance, favoring defensive formation.
- **[D] Drawback: Weight of the Crown:** shield-bearing movement is **25% slower** and sprinting while armored increases exhaustion by 50%. Cannot kite like a Traveler.
- **Optional active:** Imperial Decree as a short-range emergency crowd-control command.

**Why it fits:** The Black Emperor distorts rules and dominates social hierarchy. The cost is physical inertia and positional commitment.

## V — The Hierophant (original White Tower / Sun ritualist)

**Role:** Stationary scholar, village guardian and group support. **Elytra:** no.

- **[D] Scripture and Study — passive:** +40% XP gained; meaningful for enchanting, breeding and mob farms.
- **[D] Consecrated Workspace — conditional passive:** within 8 blocks of a lectern or enchanting table, Haste I and 15% reduced exhaustion.
- **[D] Quiet Benediction — automatic pulse:** every 40s, nearby players receive Regeneration I for 4s. **[S]** for ally/team-only targeting; a pure [D] area-effect fallback also heals enemies, which must be disclosed.
- **[D] Drawback: Sacred Dietary Vow:** cannot consume meat, fish or rotten flesh. Crop farming and food preparation are part of this class.
- **Optional active:** mark dangerous entities with a brief reveal.

**Why it fits:** This is a deliberately original clergy/scholar construction; no nonexistent canonical Hierophant member is asserted.

## VI — The Lovers (original Mother / Visionary archetype)

**Role:** Cooperative support focused on sustained proximity to allies. **Elytra:** yes.

- **[S] Linked Hearts — passive:** when another same-team player stays within 8 blocks, both get +10% movement speed and receive 1 health point of healing every 25s, subject to an internal cooldown. No health stacking across multiple Lovers.
- **[D] Fertile Hands — passive:** +25% self-healing from ordinary sources (where supported) and 20% more crop-harvest speed; fallback: brief self-Regeneration after harvesting crops, with cooldown.
- **[D/S] Shared Refuge — passive:** when near another player, small Resistance I pulse every 30s; team awareness requires a helper. No free permanent Resistance.
- **[S] Drawback: Separation Anxiety:** after 30s without another teammate within 16 blocks, exhaustion rises **35%** and mining speed drops **15%** until reunited.
- **Optional active:** sacrificial heal, reducing your own saturation rather than adding damage.

**Why it fits:** Attachment, cooperation and sacrifice should be tangible social mechanics; the lone-wolf cost is intentional. Full ally-proximity detection needs an extension.

## VII — The Chariot (Lumian Lee, Red Priest)

**Role:** Momentum fighter and battlefield instigator. **Elytra:** yes.

- **[D] Hunter's Momentum — passive:** sprinting melee attacks inflict **15% more damage**; standing-still attacks do not.
- **[D] War Rush — reactive passive:** kills award Speed I for 8s (18s internal cooldown). Rewards closing fights, not repeatedly clicking buffs.
- **[D] Pyromaniac — passive:** immune to fire and lava burn damage; gains brief Strength I when burning, capped with a cooldown.
- **[D] Drawback: Extinguished Fury:** rain or submersion applies Weakness I and Mining Fatigue I; rivers and storms change his route and combat plans.
- **Optional active:** Provoker's War Cry, pulling aggro or weakening enemies briefly.

**Why it fits:** Hunter, Provoker, Pyromaniac and Red Priest progression values motion, fire, planning and war.

## VIII — Strength (original Twilight Giant archetype)

**Role:** Heavy miner, bruiser and defensive anchor. **Elytra:** no.

- **[D] Giant's Grip — passive:** +18% melee damage and 55% knockback resistance.
- **[D] Quarry Hands — passive:** 35% faster breaking natural stone and stone-like blocks, with ordinary drops unchanged.
- **[D] Steel Frame — passive:** +2 armor; no huge always-on Resistance effect.
- **[D] Drawback: The Giant Sinks:** swim speed **45% lower**, and the class cannot use bows/crossbows. Boats and water crossings become serious logistical choices.
- **Optional active:** one delayed ground-shock attack.

**Why it fits:** The Twilight Giant is a formidable physically grounded combatant, not a magical ranged caster.

## IX — The Hermit (Cattleya, Hermit)

**Role:** Enchanting economy, occult archer and researcher. **Elytra:** yes.

- **[D] Mystery Prying — passive:** +35% XP gained, stronger while investigating caves.
- **[D] Astral Calculation — passive:** 20% more projectile damage; Night Vision when brightness is low.
- **[D] Prepared Investigator — passive:** +20% break speed while holding an enchanted book or clock in the offhand.
- **[D] Drawback: Forbidden Knowledge:** at **level 30 XP or above**, gain Mining Fatigue I unless holding a book in the offhand. Hoarding experience has a real cost; enchanting restores focus.
- **Optional active:** short range spectral mark.

**Why it fits:** Hermit power comes from dangerous knowledge, divination and calculated mystical techniques.

## X — Wheel of Fortune (original Monster / Wheel of Fortune pathway)

**Role:** Automatic high-variance survivor. **Elytra:** yes.

- **[D] Fate Intervenes — reactive passive:** whenever struck, an approximately **15% chance** to reduce that blow by 50%; no G key required. Use Origins chance conditions and independent cooldowns.
- **[D] Gentle Fortune — passive:** +10% XP and Luck +1 where the vanilla attribute applies.
- **[D] Fate's Current — automatic:** every 90s of active play, randomly gain a 10s boon such as Speed I, Haste I or Absorption I.
- **[D] Drawback: Debt of Fate:** the automatic roll also has equally plausible bad results (Hunger, Slowness, Mining Fatigue). Avoid instant death, forced inventory deletion, explosions or forced teleportation.
- **Optional active:** once in a long while, reroll one fate pulse at the cost of hunger.

**Why it fits:** The Wheel is not a button-dependent gambler—luck is always happening, including when inconvenient.

## XI — Justice (Audrey Hall, Visionary)

**Role:** Spectator, psychological defender, pacifist strategist. **Elytra:** yes.

- **[D] Patient Observation — conditional passive:** while not sprinting, take 12% less damage from mobs; remain stationary/crouched to periodically reveal nearby entities for 2s.
- **[D] Emotional Recoil — reactive passive:** attackers are afflicted with Weakness I for 4s (18s internal cooldown).
- **[D] Therapist's Presence — automatic pulse:** nearby living creatures receive brief Regeneration I every 45s. This may also heal enemies unless an ally-aware helper is enabled.
- **[D/S] Drawback: Compassionate Restraint:** damage to passive animals, villagers and the player's own pets is reduced 70%; attacking an unprovoked player is reduced 30% (requires [S] tracking for provocation).
- **Optional active:** 5s hypnotic calm/Slowness on a chosen target.

**Why it fits:** Audrey's strengths are observation, emotion and psychological manipulation; her compassion should genuinely complicate brutality.

## XII — The Hanged Man (Alger Wilson, Tyrant)

**Role:** Naval exploration, storms and trident combat. **Elytra:** yes.

- **[D] Sea-Lord's Lungs — passive:** breathe underwater indefinitely; +35% swim speed.
- **[D] Storm Companion — conditional passive:** while in rain, move 20% faster and suffer 15% less projectile damage.
- **[D] Ocean Songster — passive:** trident/projectile damage +20% and immunity to ordinary lightning strikes.
- **[D] Drawback: Drought of the Sailor:** in the Nether and hot/dry biome categories, exhaustion doubles and mining slows 15%. Carry supplies or fight near water.
- **Optional active:** small, short-lived thunderous knockback burst.

**Why it fits:** His actual pathway begins as Tyrant, so ocean and weather affinities should dominate over interpreting the Hanged Man card literally.

## XIII — Death (original Death pathway)

**Role:** Sustain through defeating enemies rather than eating to regenerate. **Elytra:** yes.

- **[D] Soul Harvest — reactive passive:** killing a hostile creature restores 2 health points, max once every 10s.
- **[D] Grave Affinity — passive:** undead inflict 25% less damage; limited low-light vision.
- **[D] Reaper's Touch — reactive passive:** attacks on undead weaken them for 3s (10s internal cooldown).
- **[D] Drawback: Severed Vitality:** **natural food-based health regeneration is disabled**. Recover by winning fights, drinking potions, or receiving healing from allies.
- **Optional active:** a brief soul-draining radius effect, with a substantial cooldown.

**Why it fits:** Death is a different survival economy, not a character who merely has fewer hearts.

## XIV — Temperance (Sharron, Chained / Wraith)

**Role:** Patient stealth, intangibility and evasive infiltration. **Elytra:** yes.

- **[D] Wraith's Veil — conditional passive:** in dim light, crouching causes invisibility; being visibly armored or holding items may betray you.
- **[D] Ethereal Landing — passive:** 60% reduced fall damage; immune to most Slowness effects, reflecting a detached spiritual body.
- **[D/S] Mirror Passage — conditional passive:** phase through at most one block-thick barriers while crouching and lightly armored, subject to an anti-grief safeguard, a short duration and cooldown. Simplified [D] fallback: Climbing on walls in darkness instead of unrestricted phasing.
- **[D] Drawback: Unstable Manifestation:** cannot equip high-armor chestplates (iron, diamond, netherite), so even with innate gliding she cannot become a conventional armored tank.
- **Optional active:** one brief possession-style Slow effect, **not** true mob mind control.

**Why it fits:** Sharron's Wraith features include intangibility, mirrors, concealment and self-restraint. No ordinary datapack can safely promise genuine freeform possession.

## XV — The Devil (original Abyss pathway)

**Role:** Infernal close combat and self-sustaining pressure. **Elytra:** yes.

- **[D] Hellborn — passive:** immunity to fire, including lava burn.
- **[D] Corrupting Claws — reactive passive:** melee attacks inflict Wither I for 2s (16s internal cooldown).
- **[D] Desperate Malice — conditional passive:** below 40% health, melee damage +18%, but no permanent Strength potion.
- **[D] Drawback: Sacred Rejection:** cannot use golden apples, and ordinary healing potions are less effective (implement potion multiplier if supported; otherwise restrict just golden apples). Strong in the Nether, poor at emergency holy-style recovery.
- **Optional active:** costly Infernal Bargain with temporary Strength and exhaustion.

**Why it fits:** The Abyss pathway trades power for corruption and vulnerability. The golden-apple restriction is a Minecraft balance metaphor, not a literal canon rule.

## XVI — The Tower (original catastrophe archetype inspired by Tyrant)

**Role:** Risky miner, demolition expert and explosion survivor. **Elytra:** yes.

- **[D] Ruin-Proof — passive:** explosions deal 60% less damage; useful around TNT, ghasts and creepers.
- **[D] Cracked Foundations — passive:** break stone, deepslate and Nether stone 30% faster; no free duplicated drops.
- **[D] Unstable Strike — reactive passive:** hits briefly stagger targets with Slowness I (13s internal cooldown).
- **[D] Drawback: Falling Tower:** suffer **75% more fall damage** and 20% more knockback. Being able to glide makes landing skill a core part of play.
- **Optional active:** directional launch as a calculated gamble.

**Why it fits:** The card represents catastrophic collapse, here treated as a high-risk relation with architecture and impact rather than simply more sword damage.

## XVII — The Star (Leonard Mitchell, Darkness / Sleepless)

**Role:** All-night tracker and nocturnal scout. **Elytra:** yes.

- **[D] Sleepless — passive:** permanent Night Vision; Darkness and Blindness effects are shortened or resisted.
- **[D] Nightwatch — conditional passive:** at night, gain 15% speed and +15% damage to undead.
- **[D] Evernight's Patience — passive:** 20% reduced exhaustion while walking or guarding at night.
- **[D] Drawback: True Sleeplessness:** cannot sleep in a bed; right-clicking one still sets spawn. Phantoms and night cycles become management concerns.
- **Optional active:** a brief Nightmare whisper that distracts enemies.

**Why it fits:** Leonard's pathway explicitly includes the Sleepless sequence and other darkness-related characteristics, not mere sunlight allergy.

## XVIII — The Moon (Emlyn White, Moon / Sanguine)

**Role:** Night healer and potion specialist. **Elytra:** yes.

- **[D] Sanguine Sight — passive:** permanent Night Vision and 15% faster movement at night.
- **[D] Blood's Renewal — conditional passive:** at night, restore 1 health point every 30s (does not stack faster with other Moon players).
- **[D/S] Pharmacist — passive:** 25% stronger healing from potions; if the exact 1.4.1 type doesn't support filtering, use modest extra regeneration when drinking one.
- **[D] Drawback: Blood Diet:** only meat, fish and rotten flesh restore hunger; ordinary plant foods cannot be eaten. The character must organize animal farming or trade.
- **Optional active:** Scarlet Medicine, a modest on-demand personal heal.

**Why it fits:** Emlyn is a Sanguine from the Moon pathway, associated with medicine and blood. This dietary translation is thematic, not a verbatim novel mechanic.

## XIX — The Sun (Derrick Berg, Sun)

**Role:** Anti-undead purifier and underground light-bearing guardian. **Elytra:** yes.

- **[D] Unshadowed — passive:** +40% damage against undead, whether in sunshine or deep underground.
- **[D] Inner Radiance — passive:** Night Vision even in caves and immunity to fire burn; his radiance is intrinsic, not dependent on direct daylight.
- **[D] Purification — automatic passive:** every 45s, cleanse Poison and/or Weakness when afflicted. This is stronger in caves and dungeons.
- **[D] Drawback: Beacon of Faith:** always visibly Glowing to other players; cannot rely on invisibility or secret approaches in PvP. The glow is **not** a dynamic light source.
- **Optional active:** short purification pulse around nearby allies.

**Why it fits:** Derrick is from the City of Silver, where sunlight is absent. Penalizing him merely for being underground (as V1 did) contradicts his role as the light in darkness.

## XX — Judgement (Xio Derecha, Justiciar)

**Role:** Grounded enforcer, shield guard and anti-escape controller. **Elytra:** no.

- **[D] Law's Weight — passive:** +2 armor, +45% knockback resistance.
- **[D] Retaliatory Sentence — reactive passive:** each attacker is slowed for 3s after landing a hit (14s shared cooldown).
- **[D] Hold the Line — conditional passive:** when not sprinting, incoming melee damage is 12% lower.
- **[D] Drawback: No Unlawful Escape:** cannot use ender pearls or chorus fruit. Mobility restrictions are enforced by the player as well as by her decrees.
- **Optional active:** single-target Prohibition: a short, noticeable Slowness/Weakness sentence.

**Why it fits:** Justiciar users issue rules and verdicts; a self-imposed ban on evasion is deliberately ironic and supports her grounded power budget.

## XXI — The World (Gehrman Sparrow / Klein, Fool persona)

**Role:** Infamous professional hunter, distinct from the Fool's survival style. **Elytra:** yes.

- **[D] Cold Precision — passive:** projectiles deal 25% more damage; melee remains ordinary.
- **[D] Marked Prey — reactive passive:** any successfully hit hostile target Glows for 6s (10s internal cooldown), making pursuit an ordinary part of combat.
- **[D] Hunter's Tempo — reactive passive:** killing a hostile mob grants Speed I for 8s (18s internal cooldown).
- **[D] Drawback: Terrifying Reputation:** villagers refuse to trade with you. The World must procure equipment through exploration, combat or friends, which is a genuine SMP social cost.
- **Optional active:** one Faceless Withdrawal for a high-risk escape, with a long cooldown.

**Why it fits:** The World reflects Gehrman Sparrow's dangerous public persona and the professional hunter role; the Fool remains the more cautious, divination-focused version of Klein.

## Cross-origin checks and balancing

| Playstyle | Most distinctive options |
|---|---|
| Exploration and aerial mobility | Magician, Fool, Hanged Man |
| Caving and knowledge economy | High Priestess, Hermit, Hierophant |
| Aggressive PvE / combat | Chariot, Strength, Devil, World |
| Defensive authority | Emperor, Judgement, Justice |
| Stealth and infiltration | Empress, Temperance |
| Group roles | Lovers, Hierophant, Justice |
| Night specialization | Star, Moon, Death |
| Unpredictability / risky traversal | Wheel of Fortune, Tower |
| Undead and darkness control | Sun, Star, Death |

### Initial acceptance criteria

1. Choosing an origin must change ordinary gameplay within **five minutes** without pressing G/V.
2. At least **two beneficial passive behaviors** must trigger per origin in common test cases, and the drawback must be demonstrable.
3. No negative maximum-health modifier is used as the *primary* weakness. Avoid adding global permanent Strength II, Resistance II or Regeneration II.
4. Each origin's core weakness must be distinct, ideally requiring an altered inventory, environment, food strategy, economy or social relationship.
5. Passives that apply to players or nearby entities must explicitly define team targeting, ownership, friendly fire, PvP and AFK-farm safeguards.
6. Original 18 innate gliders remain. Test flyers with armor, death, respawn, dimension changes and firework rockets.
7. Build both datapack variants and test all power types against the **1.4.1** schema; an otherwise-valid JSON file can still contain unsupported fields or wrong behavior.
8. Test rollback: v1 must remain installable as a stable fallback. Don't merge a behavioral replacement directly to main before server acceptance.
9. Performance: use event callbacks and **20+ tick intervals** when possible; avoid per-tick area scans and repeated unbounded effect application. Test with several players online.
10. Version status: a design RFC is not a released or gameplay-tested datapack. Feature implementation and test evidence need their own PR.

### Proposed next engineering milestone

1. Implement all **[D]** perks and unique drawbacks using Origins/Apoli JSON in an isolated v2 generator; migrate away from universal -hearts penalties.
2. Keep existing G/V actions temporarily but reduce burst strength where passive upgrades would exceed the v1 power budget.
3. Add content tests that verify each origin has at least 2 true passive advantages + 1 non-generic drawback and no data-loss commands.
4. Optionally use **KubeJS 1802.5.5** for [S] mechanics on your server only if the current installed environment supports the exact event/scoreboard hooks. Otherwise use the specified datapack fallbacks.
5. Publish two alpha ZIPs from a separate GitHub Actions artifact and run a private test-world acceptance pass before merging v2.

### References

- https://github.com/DoorBlox/origins-tarot
- https://origins.readthedocs.io/en/1.4.1/types/power_types/
- https://origins.readthedocs.io/en/1.4.1/types/entity_condition_types/
- https://lordofmysteries.wiki.gg/wiki/Tarot_Club/List_of_Members
- https://lordofmysteries.wiki.gg/wiki/Fool_Pathway/Abilities
- https://lordofmysteries.wiki.gg/wiki/Red_Priest_Pathway/Abilities
- https://lordofmysteries.wiki.gg/wiki/Justiciar_Pathway/Abilities
- https://lordofmysteries.wiki.gg/wiki/Chained_Pathway/Abilities
- https://lordofmysteries.wiki.gg/wiki/Moon_Pathway/Abilities

Fan-made gameplay designs and interpretive balance constraints; the original works are credited for inspiration, and novel text is not reproduced.
