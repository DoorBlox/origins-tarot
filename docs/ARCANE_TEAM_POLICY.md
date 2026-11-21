# Arcane Rev3 — safe PvP team policy (Minecraft Java 1.18.2)

**Decision:** use **vanilla scoreboard teams**, not LuckPerms groups, as the game's ally/enemy relationship. LuckPerms + the owner-installed **Fabric Permissions API** are for permission nodes, **not** combat allegiance. The pack never creates, joins, changes or deletes teams automatically; admin retains control.

## Policy

The file `arcane/teams.json` contains the explicit team allowlist:

```json
["tarot_red", "tarot_blue", "tarot_green", "tarot_gold"]
```

- Same **listed** team: ally. Harmful Arcane PvP commands **never** target teammates. New ally buffs only target that same team; players outside a listed team cannot get accidental support.
- Different **listed** teams: opponent. The caster must be assigned one of the listed teams, and the target must belong to **another** listed team. Harmful effects require spatial distance and run only when the player's ability is activated.
- **No team / other team name:** neutral. No extra PvP debuffs or ally buffs from these new handlers. This fails closed and avoids affecting staff/spectators or another minigame's teams.
- Tagged hostile mobs still receive the original hostile-only effects. Vanilla PvP damage and these scripted AoE status effects are separate systems.
- Names are validated (2–8 unique, 1–16 ASCII-safe characters); never interpolate client-supplied names into commands. Runtime functions contain only literal selectors.
- Changed abilities retain their `partial` manifest status. This adds safe team-targeted effects but does not replace missing AI, custom overlays, field persistence, exact damage, or player contract mechanics.

## One-time operator setup — only on the owner's test server

These commands must be executed **by an OP/admin** on a backed-up disposable 1.18.2 test world. Do not grant OP or team management to ordinary players.

```mcfunction
/team add tarot_red
/team add tarot_blue
/team add tarot_green
/team add tarot_gold
/team modify tarot_red friendlyFire false
/team modify tarot_blue friendlyFire false
/team modify tarot_green friendlyFire false
/team modify tarot_gold friendlyFire false
/team join tarot_red TestPlayerA
/team join tarot_blue TestPlayerB
/team list
```

**Do not execute these blindly in production**: skip commands for pre-existing teams, and replace test names with the actual consenting test players. `friendlyFire false` is useful but **does not stop status-effect commands**; the team-filtered selectors provide that protection.

For deployments with custom teams, edit `arcane/teams.json` and rebuild the datapack. Merely changing the JSON on a running server will **not** change already generated power definitions. Do not assume arbitrary other team names become enemies.

## Gameplay test cases that must be observed (currently NOT RUN)

1. Two members of `tarot_red`, one member of `tarot_blue`, one `tarot_green` and an unassigned player in range. Trigger e.g. Judgement Order. Confirm only other listed teams receive Slowness/Weakness; same team and unassigned do not.
2. Activate Sun The Eternal Day with a same-team friend and an opponent standing in range. Only the friend should gain shared Regeneration/Night Vision; opponent must not.
3. Move targets out of range, relog, respawn, leave a team mid-buff and test administrative pause. Existing duration-limited potion effects won't automatically be cleared by leaving a team—this is a known limitation, and operators can clear effects if needed.
4. Verify permissions as a true non-OP using `/trigger a_help` / `/tarot`. Staff functions and player team joining must remain OP-only.
5. Check original hostile mobs remain affected, and all four exact-head CI workflows pass. **Source CI is not real Minecraft compatibility acceptance**.

**References:** Minecraft Java target selectors' `team` argument and vanilla scoreboard team membership: https://minecraft.wiki/w/Target_selectors and https://minecraft.wiki/w/Scoreboard.
