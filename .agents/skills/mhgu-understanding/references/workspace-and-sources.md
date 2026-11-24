# Original workspace, inputs, and coverage

The source workspace is `/mnt/storage2/Programs/MHGU_Modding`. All other source pointers are relative to that root. Commands require the referenced scripts/tool runtimes; private game-derived indexes and binaries may be absent in a source-only checkout.

## Local inputs

Machine paths (RomFS, library, logs) are in the workspace's root `AGENTS.md`, "Runtime evidence and installation paths"; the other local inputs (sealed game files, copied executables, research tooling) are in `docs/LOCAL_STATE.md`. Outside this workspace, supply equivalent inputs explicitly; the skill's Markdown stays usable without them. Copied executables and research indexes are under `work/shared/game-exefs/` and `work/research-tooling/`; task copies under `work/<task>/`.

What each input holds and when to use it: the Game data section of this skill's SKILL.md.

A RomFS-only dump cannot supply executable bytes. Folder presence is not activation. Do not inspect unrelated saves or alter settings to answer a data lookup.

## Reproducible reference snapshots

- Main SHA-256: `b3935415499549adaf4c0e89822831daa175cfd456a7990791c79be3997645ef`; build `FB08F1D20FD1204FE7070672777F869B`.
- GZF SHA-256: `b4b94c526f2d0b1b91dbcbd4bd5f411479a5db7270de04a50605f61db649f99a`. Supplied file authorship was not established from metadata.
- DTI dump SHA-256: `ea4c31e1845ea8f2fa7bda3173de0f324e97148683c12364fabb550e99f1175c`, runtime extraction 2026-10-03.
- [MHGU-Modding](https://github.com/RTHKKona/MHGU-Modding) offline snapshot: `a5b6d072f0ed5c7d701c2cb783ccd5060c49c6e8`.
- [MHGU-Modding wiki](https://github.com/RTHKKona/MHGU-Modding/wiki) offline snapshot: `d3a07dc8b6d1a91da24f4319050773c3da90e9bb`. Snapshot provenance is in `references/provenance.json`.

These skills include findings and methods, not game executables, extracted assets, full indexes/dumps, or third-party manuals. Public source references do not establish current-upstream behavior. Retest revised binaries/resources and preserve original hashes when extending this knowledge.
