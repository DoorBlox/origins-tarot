# Development guide

## Edit the source of truth
`generate.py` owns the **22 card records**, `BUILD` action definitions, JSON assembly and ZIP packaging. `ARCANA_GUIDE.md` and `datapacks/*` are generated outputs. Make changes in `generate.py` before rebuilding; direct edits to the generated JSON will be overwritten by the next sync.

### Commands
```bash
python3 generate.py
python3 -m unittest discover -s tests -v
python3 tools/unpack_generated.py
```

## Data layout
```text
pack.mcmeta
data/origins/origin_layers/origin.json
data/tarot/origins/<card>.json
data/tarot/powers/<card>/primary.json
data/tarot/powers/<card>/secondary.json
data/tarot/powers/<card>/passive.json
data/tarot/powers/<card>/drawback.json
data/tarot/powers/<card>/wings.json  (18 cards)
ARCANA_GUIDE.md
```
Some powers have extras or different types; inspect the generated files for exact data. Minecraft 1.18.2 datapack `pack_format` is 9, and durations/cooldowns are expressed in **ticks (20/s)**.

## How to add/change a power
1. Pick its arcana slug in `CARDS` and corresponding `BUILD[slug]`.
2. Use the existing helpers for active actions, projectile launches, attributes, conditional passives and effects; verify every power type exists in the target Origins 1.4.1 / Apoli implementation.
3. Preserve the primary and secondary key binding definitions and avoid duplicate power IDs.
4. For a wingless card, keep it out of `GLIDERS`; adding a card to `GLIDERS` generates a genuine `origins:elytra_flight` power.
5. Update the tests and regenerate both ZIP variants.
6. Verify behavior **in game** as automated structural tests cannot catch every version-specific power parsing or gameplay interaction.

## Quality gates
- Python generator exits cleanly and output ZIP passes CRC integrity.
- Both ZIPs have 22 origin JSONs, valid resource references, and 18 `origins:elytra_flight` powers.
- Exactly one G and one V bound active ability per card; all cooldowns positive.
- One origin layer has `replace: true`, the other `replace: false`.
- No new admin command execution or terrain mutation in datapack powers.
- Final in-game confirmation and manual acceptance signoff before a production SMP deployment.

## Fan content and contributions
This is a non-commercial fan design concept; no official endorsement or proprietary novel text is embedded. Please avoid copying wiki passages verbatim or submitting copyrighted artwork without permission. Character names and card themes are used as fan references only; the game mechanics and descriptions are newly authored.

References: [official Origins examples](https://github.com/apace100/origins-example-packs), [Origins 1.4.1 docs](https://origins.readthedocs.io/en/1.4.1/).
