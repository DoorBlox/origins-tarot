# Arcane V2 Rev 3 — isolated development alpha

**DO NOT install this pack in the live SMP.** This is a deliberately restricted **Fool Sequence 9 proof of concept** based on the supplied handbooks, not a release of all 434 abilities. Work is isolated from main V3 and does not replace its sequence/quest system.

## Scope actually implemented

- **Rev3 pure state model** in arcane_rev3/model.py: 22 pathways, 11 exact pairs, one auto-filled slot at Seq9, auto-fill through Seq5, second partner at Seq4, six/seven/eight editable slots at Seq4/3/2, ten resonance kits at Seq1, and unchanged kit at Seq0. Validation prevents duplicate, unavailable, and locked assignments. **This is a Python reference model, not yet hooked into the Minecraft runtime.**
- **Playable test datapack for Fool Seq9 ONLY**: innate Elytra gliding; +25% exhaustion while sprinting/fall-flying; Spirit Vision (sneak + secondary key, 10-block glowing for 40 ticks, 100-tick cooldown). Spirit Vision is granted by source tarot_slot, not directly by the Origin.
- **Non-OP player controls**: /tarot, /tarot help, /tarot status, /tarot slots (or /trigger ta_help, /trigger ta_status, /trigger ta_slots if aliases are unavailable). Command Aliases uses **CLIENT** trigger dispatch and permission level 0, with no elevated SERVER action.
- Automatic init on Fool origin selection; periodic missing-power reconciliation; cleanup when the Fool origin is removed.

**Not yet implemented:** remaining three Fool Seq9 abilities, Seq8-0, all other 21 pathway abilities, all Resonance abilities, actual Minecraft runtime slot edits, progression/acting integration, permanent save migration, mod-controlled disguises, and live server acceptance. **No fake placeholder powers are generated.**

## Install to a disposable Minecraft 1.18.2 Fabric test world

1. Back up the world and its playerdata, scoreboard.dat and current V3 pack first. This alpha is self-contained: **remove the old V2/V3 Tarot datapacks from this disposable test world** before adding the new ZIP; never install overlapping versions.
2. Download the artifact **arcane-v2-rev3-fool-seq9-test-only** from the passing Validate Arcane V2 Rev3 workflow. Extract the **outer** GitHub artifact ZIP.
3. Copy Arcane_V2_Rev3_Fool_Seq9_ONLY_1.18.2.zip to the test world's datapacks directory without extracting its inner ZIP.
4. On the server, place tarot.json into config/commandaliases/tarot.json (Command Aliases Fabric 1.18.2 1.0.1); then restart or use /commandaliases reload. Do not copy alias config into the datapacks directory.
5. Install Origins 1.4.1 and Fabric API normally. LuckPerms is optional for this safe /trigger bridge; if it restricts the alias, grant only its player-facing alias permission, never wildcard/OP. Exact LuckPerms node for this legacy mod must be confirmed in game.
6. Choose **The Fool** on the origins screen. Check /tarot slots, /tarot status, and sneak + V with nearby entities. Test the direct /trigger ta_slots fallback with a **non-OP** account.
7. Test relog, death/respawn, and switching away from The Fool. Record logs and whether commands autocomplete. Structural tests cannot validate legacy mod runtime compatibility.

The user requested datapacks and existing mod configurations only: **no KubeJS, custom Java/Fabric mod, server deployment, or bypass of game permissions**.

## Known architecture gap

In Rev3 single mode, the primary Origin's Seq9 drawback and wings are innate; at slot mode an Origin switch or a neutral-Origin strategy will be needed to make **all** unslotted sequence powers truly revocable. This alpha does not enter slot mode, so it does not claim to solve that transition.

Rev2 marks some powers [S] (requires scripting) and some [D/S]; moving to datapacks only will require ability-by-ability verification of exact mechanics, with documented limitations rather than pretending that client skin/model or AI controls are supported by vanilla Origins. The separate old KubeJS and native-mod PRs remain closed.
