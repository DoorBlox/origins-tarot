# Arcane V2 — Batch 1 / Fool + Slots

**TEST-WORLD ALPHA. NOT LIVE-GAME-VERIFIED. DO NOT REPLACE YOUR WORKING SMP PACK.**

This isolated Minecraft 1.18.2 pack contains only Fool for selection. It is built around Origins 1.4.1, KubeJS 1802.5.5 and the Rev 3 slot rules. Rev 2 preserves the exact ability specifications. Both original handbooks are preserved in docs/ through their explicit end markers.

## Install
1. Download the successful GitHub Actions artifact **tarot-arcane-batch1-fool-test-world** from this feature branch's Arcane Batch 1 workflow.
2. Extract the outer Actions artifact. Take **Tarot_Arcane_Batch1_Fool_Datapack_1.18.2.zip** and copy it (not its extracted contents) into the test world's datapacks/ directory.
3. Extract **Tarot_Arcane_Batch1_Server_Bundle.zip** to a temporary folder. Copy the contained kubejs/server_scripts/tarot folder into the server's kubejs/server_scripts/ folder.
4. Back up the test world, scoreboard.dat, advancements, playerdata, current V3 datapack and old Tarot KubeJS scripts. Remove the previous V3 datapack and scripts from this **test world** before restarting. The Batch 1 pack intentionally offers Fool only.
5. Restart Fabric 1.18.2. Confirm Origins 1.4.1, Fabric API, KubeJS 1802.5.5, zero invalid JSON power types and zero unknown event errors.
6. Pick Fool. Use /tarot slots. At Seq9 there is one Fool Seq9 slot and four abilities.
7. Sneak + V uses Spirit Vision; G activates the server approximation of Faceless. /tarot bind secondary puppet_string selects Puppet String once Seq5 is slotted; /tarot cast secondary is a fallback for key issues.
8. OPs may simulate advancement one step at a time: /tarot debug sequence 8, then 7, 6, 5, 4, 3, 2. Use /tarot slot 6 tarot:fool 4, /tarot slot 6 clear, /tarot slot swap 1 6, /tarot slot auto and /tarot reset at Seq4.
9. Seq1 Resonance is intentionally **locked until Batch2** supplies Hanged Man + Paper Martyr. It must not erase players' current powers.
10. Check docs/BATCH_1_TEST.md and inspect KubeJS server logs. Restore backup to roll back.

## Important
The Fool's Spiritual Expenditure is +25% exhaustion for sprinting and an explicit extra gliding surcharge. Actual skin, model and name copying requires a client extension. More mechanics require in-game compatibility tests; see docs/BATCH_1_APPROXIMATIONS.md. The two Origins key binds select one of several skills using /tarot bind; they do not fire every unlocked active skill simultaneously.

Do not install this isolated package alongside the original V3 datapack on production.
