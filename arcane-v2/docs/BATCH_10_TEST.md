# Batch 10 - Sun, Moon, Eclipse manual test plan

Use Minecraft Java 1.18.2, Fabric API, Origins 1.4.1 native mod.
All checkboxes begin **UNTESTED IN LIVE MINECRAFT**; startup CI alone is insufficient.

- [ ] Sun chosen with identity-only powers (marker, Beacon of Faith, Wings); permanent Glowing persists when Seq9 kit unslotted at Seq4.
- [ ] Sun Seq9 +40% outgoing damage specifically against tagged undead; ensure ordinary tagged hostile and enemy players do NOT receive this undead bonus.
- [ ] Sun Seq9 Inner Radiance Night Vision and fire immunity active only while Seq9 kit slotted.
- [ ] Sun Seq9 Inner Light 100t stationary in light≤4 triggers particle/vision approximation radius3, Seq3 radius5; no physical light blocks are created yet.
- [ ] Sun Seq9 Purification cleanses Poison+Weakness every900t.
- [ ] Sun Seq8 Holy Light crouch60t heals2HP, cooldown600t.
- [ ] Sun Seq7 Solar Flare 20% chance 40t Blindness on undead attacker (undead only), any time of day.
- [ ] Sun Seq6 Witness right-click player reveals private health and tracking for1200t; no unintended public chat leaks.
- [ ] Sun Seq5 Purify V removes Poison/Wither/Blindness from caster and eligible teammates within4, CD900; enemies never buffed.
- [ ] Sun Seq4 Unshadowed II boosts undead damage to +50%, replacing +40 not stacking.
- [ ] Sun Seq2 Sanctify CD3600 600t 5-block field hits undead 2HP/sec, no attacks on teammates.
- [ ] Sun Seq1 White Angel G 300t light-like zone15, undead 4HP/sec, same-team Regen I; CD3600. Exact all-player Regen wording versus team-only global rule documented.
- [ ] Sun Seq1 Beacon of Faith II reveals hostile mobs/enemy players within20 via Glowing.
- [ ] Sun Seq0 Eternal Day G 2400t/CD24000 fixed 30-block zone; undead6HP/sec, enemy players1HP/sec, allies Regeneration I/Night Vision and +2HP per200t; newly spawned hostile mobs suppressed, without accidentally deleting existing ones.
- [ ] Choose Moon Seq9: always Night Vision, +15% nighttime movement and Blood's Renewal heals1HP every600t at night (Seq4 Shaman 3HP).
- [ ] Moon permanent Blood Diet: eating only items in #tarot:meat raises hunger/saturation. Other edible items can apply their effects but restore NO hunger or saturation, and this restriction survives unslotted Seq9 and fused Seq1.
- [ ] Moon Seq9 10% night chance to clear Wither on incoming damage.
- [ ] Moon Seq9 Pharmacist drinkable instant-healing potions +25% heal; Seq1 Pharmacist II +35%; Seq5 Scarlet V temporarily +50% for200t, CD1200.
- [ ] Moon Seq8 right-click passive with bone, CD1200, applies 1200t no-flee approximation; does not replace Minecraft animal AI exactly.
- [ ] Moon Seq7 Blood Drain heals1HP on qualifying melee hit against hostile mob AND enemy player, CD100, never teammates.
- [ ] Moon Seq6 crouch-right-click active brewing stand with potion reaction: brewing timer accelerated to 1 tick, cooldown6000, no duplicate inventory or potion exploit.
- [ ] Moon Seq3 Summon right-click passive yields bounded owner-tagged temporary Vex combat proxy200t/CD1200 (not an exact animal-copy AI).
- [ ] Moon Seq2 Life on passive death within8 resurrects a new allied copy for400t once per3600; revived mob cannot recursively revive itself, disappears after expiry/death/logout.
- [ ] Moon Seq1 Beauty G pacifies hostile mobs and enemy players within10 for160t, self/same-team Regen I200t, CD2400.
- [ ] Moon Seq0 Scarlet Feast G600t/CD24000 moving15 aura: hostiles lose2HP/second; enemy players 2HP/60t; healing from drained HP shared among caster+allies up to30HP cumulative.
- [ ] Advance Sun/Moon from Seq5→4: paired permanent drawback stays active independent of equipped slot. Verify Seq4 six slots and Seq2 eight slots.
- [ ] Advance Seq2→1: only Eclipse sequence kits 9–0 active, individual Sun/Moon kits revoked.
- [ ] Eclipse Seq9 Unshadowed Sanguine has undead +40%, Night Vision, 10% Wither resistance at night, permanent Glow and Blood Diet.
- [ ] Eclipse Seq8 Holy Tamer offers Holy Light600t and bone-based Tame1200t.
- [ ] Eclipse Seq7 Solar Drain combines 20% Blindness on undead attacker with melee1HP lifesteal/100t.
- [ ] Eclipse Seq6 Witness Brew preserves private player health reveal1200 and instant Brew6000.
- [ ] Eclipse Seq5 Purify Scarlet cleanses poison/wither/blindness, Regeneration I100t, potion heal+50%200t, CD1200.
- [ ] Eclipse Seq4 Sunrise heals2HP on hits to undead, ignites40t; extra0.5-heart damage in same hit not yet exact.
- [ ] Eclipse Seq3 Moonshadow enables night wall vision5 blocks (currently approximate).
- [ ] Eclipse Seq2 Lunar Sanctuary CD3600 has undead2HP/sec, night drain2HP/40t nearby enemies and self healing.
- [ ] Eclipse Seq1 Solar Drain White Angel self heals1HP/sec, undead6HP/sec (4+2), CD3600.
- [ ] Eclipse Seq0 Eclipse G1200t/CD24000 has fixed30 Sun + moving15 Moon simultaneously. Sun affects enemy players1HP/sec, Moon enemy players2HP/60t, both exclude teammates from offensive damage.
- [ ] Eclipse Seq0 undead inside overlap burn + drain; official double-loot drop still flagged missing.
- [ ] Eclipse Seq0 final pulse at 1180t undead10HP, allies heal10HP, enemy players Blindness300t, with no extra direct damage to teammates.
- [ ] Try daylight/night, world change, respawn, relog, origin swap, scoreboard teams, no-team PvP and overlapping capstones, plus large mobs near spawn controls.
- [ ] Ensure no KubeJS scripts/mods installed or required; test exact commit and capture failure logs.

No source completeness guarantee is implied by compilation or headless startup.
