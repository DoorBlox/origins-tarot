# Repository Agent Entry Point — Tarot Club / Arcane V2 Rev3

Before changing this repository, **read [CHATGPT_HANDOFF.md](CHATGPT_HANDOFF.md)** and query live `main`, open PRs, CI and [issue #20](https://github.com/DoorBlox/origins-tarot/issues/20). The handoff is a checkpoint, not authoritative live status.

- Owner requests rapid, substantial, source-traced batches, and authorizes repository edits and safe PR merges. No need for repetitive approval for ordinary source changes.
- `docs/HandbookRev3.txt` governs progression and slot rules; `docs/HandbookRev2.txt` governs the 434 ability specifications. Do not substitute remembered mechanics or older V3 behavior.
- Hard constraints: Minecraft Java **1.18.2**, Fabric, Origins **1.4.1**; **no KubeJS and no custom Java/Fabric mod**. Preserve existing V2/V3 pack workflows.
- Preserve non-OP player-only `/trigger` Tarot UI, ally/team safeguards, permanent identity drawbacks and **Sequence 1 fail-closed** until all Resonance requirements work. Never issue arbitrary player OP privileges.
- Source merges are **not deployments**; never modify an actual SMP world/server/player state on the basis of a green CI run. Only a disposable test server for runtime acceptance, then separately approved versioned release.
- New power definitions must have concrete effects, source trace, correct `full`/`partial`/`blocked` status, explicit `missing` disclosures, proper 1.4.1 API, and tests. No dummy `origins:simple` completions.
- Validate all relevant tests and **four green exact-head PR workflows** before merging. Update `CHATGPT_HANDOFF.md` and issue #20 after milestones, not just chat memory.

Main development code: `arcane_rev3/full_build.py`, `arcane_rev3/powers.py`, `arcane_rev3/batches/`, `arcane_rev3/model.py`. Generated `output/` and `datapacks/` trees are not authoritative.
