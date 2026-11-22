# Safe test-server installation and rollback

[← Player handbook](README.md) · [Full operator runbook](../ARCANE_SMP_UPGRADE_PREFLIGHT.md)

> **Development build only; not production-certified.** A passing source CI workflow does not prove Minecraft 1.18.2 server startup, player save compatibility, book click rendering or full multiplayer safety.

## Table of contents
- [Choose the right artifact](#choose-the-right-artifact)
- [Before an upgrade](#before-an-upgrade)
- [Verify the result](#verify-the-result)
- [Rollback](#rollback)

## Choose the right artifact

Use [Build Arcane V2 Rev3 22-Origin Dev Pack](https://github.com/DoorBlox/origins-tarot/actions/workflows/arcane-full.yml), **not** the legacy Tarot V2 or V3 build workflows. Download the outer artifact named **tarot-arcane-rev3-22-origin-dev-not-production**, then unzip it. Select exactly one inner pack:

- **Arcane_Rev3_22_Origins_ONLY_DEV_1.18.2.zip** — replaces ordinary Origins selection with Tarot choices.
- **Arcane_Rev3_22_Origins_ADDON_DEV_1.18.2.zip** — adds Tarot choices alongside ordinary Origins.

The optional **tarot.json** is Command Aliases config in **config/commandaliases/**, not a datapack. It is not required for normal /trigger player commands. Do not install the separate OP-only Resonance preview on SMP.

## Before an upgrade

1. **Stop the server**. Create and verify a full restorable world backup with **playerdata, scoreboard.dat, level.dat**, previous working pack and configuration files.
2. Read the build SHA and preserve the original ZIP for rollback.
3. Do not combine the Arcane ZIP with old Tarot V2/V3 datapacks. Install exactly one **inner ZIP** without extracting the inner ZIP.
4. Check the full startup log and **/datapack list** before allowing normal play.

## Verify the result

As a non-OP player, run **/trigger a_book**, **/trigger a_tome** and **/trigger a_focus_menu**. Test the clickable contents, pathway weaknesses, slot-specific Focus books, actual selected key, individual HUD, partner restrictions, death/relog persistence, ability targeting and neutral/teammate protection. Fool's Spirit Vision is a useful first test: sneak + Secondary Origins key.

## Rollback

On failure, stop the server and **restore the entire matching backup**, not just the old ZIP. Do not delete or reset playerdata or scoreboard.dat to suppress loading errors.

The detailed diagnostic and upgrade procedure is maintained in the [operator preflight](../ARCANE_SMP_UPGRADE_PREFLIGHT.md).

[↑ Table of contents](#table-of-contents) · [← Player handbook](README.md)
