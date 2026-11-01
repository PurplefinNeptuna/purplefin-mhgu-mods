# Original workspace, inputs, and coverage

The source workspace is `/mnt/storage2/Programs/MHGU_Modding`, Linux, user shell fish. This snapshot is dated 2026-10-17. All other source pointers are relative to that root. Commands require the referenced scripts/tool runtimes; private game-derived indexes and binaries may be absent in a source-only checkout.

## Local inputs

| Purpose | Path |
| --- | --- |
| RomFS-only dump | `~/.local/share/eden/dump/0100770008DD8000/` |
| Uninstalled library | `/mnt/storage2/ROM/Switch/cheats/mhgu/` |
| Copied executable inputs | `work/shared/game-exefs/` |
| GZF/main-memory/project/indexes | `work/research-tooling/` |
| Mod-specific copied resources/research | `work/<mod>/` and mod-local configured inputs |
| Current Eden log | `~/.local/share/eden/log/eden_log.txt` |
| Ryujinx logs | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/Logs/` |

What each input holds and when to use it: the Game data section of this skill's SKILL.md.

Library material is not an installed mod. A RomFS-only dump cannot supply executable bytes. Folder presence is not activation. For runtime diagnosis, correlate a fresh launch log with the exact relevant installed payload hashes and game/emulator versions. Do not inspect unrelated saves or alter settings to answer a data lookup.

## Source coverage

| Topic / reference | First sources to inspect |
| --- | --- |
| Discovery / executable identity | `docs/RESEARCH.md`, `scripts/{research_tools.py,mhgu_binary.py}`, `work/research-tooling/ghidra-export/summary.json`, DTI provenance |
| DTI trial / limitations | `mods/dti-dumper-support/README.md`, `docs/RESEARCH.md`, `scripts/dti_dumper.py`, `docs/WORKSPACE_EVIDENCE.json` |
| Native GUI | Key Quest Markers `src/{gui.rs,native.rs}`, `mods/key-quest-markers/scripts/gui_layout.py`, `tests/native_adapter.py`, `research/theme-colours.json`; Please do Better native geometry research |
| Sharpness | Modern Sharpness Gauge `DEVELOPMENT.md`, `core/src/lib.rs`, `src/insert.rs`; `work/modern-sharpness-gauge/PHASE*_RESEARCH.md` |
| Quests / progression | Key Quest Markers `core/src/lib.rs`, `src/{native.rs,offers.rs}`, native tests and `DEVELOPMENT.md` |
| Input / actions | Modern Weapon Controls `src/`, native fixtures, `src/game_signatures.h`, `DEVELOPMENT.md`, `RUNTIME_RESULTS.json` |
| Damage / cameras | Damage Numbers `src/signatures.rs`, `core/src/{capture.rs,lib.rs,presentation.rs,mailbox.rs}`, tests, `work/damage-numbers/projection-r27/` |
| Rewards / Luck | Please do Better `src/{runtime.cpp,quantity.h,attribution.h}`, native fixtures, `DEVELOPMENT.md`, research/layout receipts |
| Resource/tool workflows | `docs/TOOLS.md`, `docs/CLEANUP_HD_PROJECT.md`, tool wrappers/tests, offline wiki/templates/indexes, `mods/hd-project/README.md` |
| Exact current release/evidence scope | Each mod's `DISTRIBUTION.json` / `EVIDENCE.json`; dated workspace receipts in `docs/WORKSPACE_EVIDENCE.json` |

Current instructions and source establish present implementation. Dated evidence retains original hashes/claims. Mod development documents include older investigations, so check the current release/source before copying a colour, loader assumption, fixed key count, hook recipe, or unresolved-state workaround. Superseded materials live in Git or accepted backups.

## Reproducible reference snapshots

- Main SHA-256: `b3935415499549adaf4c0e89822831daa175cfd456a7990791c79be3997645ef`; build `FB08F1D20FD1204FE7070672777F869B`.
- GZF SHA-256: `b4b94c526f2d0b1b91dbcbd4bd5f411479a5db7270de04a50605f61db649f99a`. Supplied file authorship was not established from metadata.
- DTI dump SHA-256: `ea4c31e1845ea8f2fa7bda3173de0f324e97148683c12364fabb550e99f1175c`, runtime extraction 2026-10-03.
- [MHGU-Modding](https://github.com/RTHKKona/MHGU-Modding) offline snapshot: `a5b6d072f0ed5c7d701c2cb783ccd5060c49c6e8`.
- [MHGU-Modding wiki](https://github.com/RTHKKona/MHGU-Modding/wiki) offline snapshot: `d3a07dc8b6d1a91da24f4319050773c3da90e9bb`. Snapshot provenance is in `references/provenance.json`.

These skills include findings and methods, not game executables, extracted assets, full indexes/dumps, or third-party manuals. Public source references do not establish current-upstream behavior. Retest revised binaries/resources and preserve original hashes when extending this knowledge.
