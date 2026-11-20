> **V2 ALPHA:** the 22 passive-first builds require their own in-game testing. Back up the world and the previously working V1 ZIP. Replacing a datapack on GitHub is not a hosted server deployment.

# Installation and first-run acceptance

## Compatibility
- Minecraft Java Edition **1.18.2** and **Java 17**
- Fabric Loader (server currently uses **0.20.1**)
- Origins **1.4.1**, Fabric API **0.76.0+1.18.2**, and compatible Apoli dependencies already loaded by Origins
- Terrain mods such as Terralith and Tectonic **do not need** to be installed by datapack clients purely for this origins pack.
- The Tarot datapack is server-side; all players must have a compatible **Origins client mod** installed.

## Choosing the ZIP
- `The_Tarot_Club_22_Arcana_Only_1.18.2.zip`: **replace:true** Origin layer, so the choice screen is Tarot-only.
- `The_Tarot_Club_22_Arcana_1.18.2.zip`: **replace:false**, so these are added alongside the normal choices.
- Choose **only one** variant. Installing both at once creates conflicting origin-layer definitions.

## play.hosting / Pterodactyl
1. Back up the current world and `server.properties`.
2. Stop the server.
3. Browse to the current world folder shown by `level-name` (example: `tarot-world-test`).
4. Create or open `datapacks/`.
5. Upload the selected **inner ZIP**, leaving `pack.mcmeta` at the root of that ZIP.
6. Start the server. In the console, type `datapack list` and confirm it is enabled.
7. Use `origin set YOUR_NAME origins:origin tarot:fool` to test, or in Minecraft chat: `/origin set YOUR_NAME origins:origin tarot:fool`.
8. Verify opening the selection screen, G and V, post-death persistence, and gliding. Only then copy the ZIP to your final world.

If updating an installed ZIP, stop server, replace that same ZIP path, then start again. Keep a backup of both world and previous pack.

## Client
Install **Fabric 1.18.2**, **Origins 1.4.1**, and compatible Fabric API on the client. This pack's powers are JSON on the server; copying its ZIP to every client is unnecessary. The `G` and `V` keys are configurable in Minecraft Controls (Origins primary and secondary active). Gliding uses a midair jump like an Elytra; it is **not** unlimited flight.

## Diagnosing common issues
- **Not shown at selection:** wrong world folder; the ZIP's first entry should include `pack.mcmeta` at archive root; verify `datapack list`; check whether another Origins layer/datapack overrides this one.
- **Unknown origin:** inspect `data/tarot/origins/*.json` inside the ZIP; try `/origin set ... origins:origin tarot:justice`.
- **Invalid power type / parse errors:** capture the first complete server error after startup and test with the exact versions above.
- **G/V does nothing:** verify Origins keybinds and that another mod hasn't bound the same keys; check cooldown bar and food level.
- **Glide won't engage:** use one of 18 winged cards and jump while falling; Emperor, Hierophant, Strength, and Judgement intentionally cannot glide.
- **World errors / high memory:** because the server has 3 GB allocated but may use a smaller Java heap, trial on the temporary world and check memory. The datapack does not require C2ME.

Do not assume structural JSON validation guarantees correct gameplay: run the acceptance checklist in [BALANCE.md](BALANCE.md).
