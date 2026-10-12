# Local state

Switch delivery documentation refreshed 2026-10-10 from the tracked distribution
and evidence records; Eden/Ryujinx activation was not re-inspected for that
cleanup. GURecomp's exported Linux game, resource packages and Forge PC loader
were separately inspected on 2026-10-12.

## Local deliveries

| Mod | Version | Status | Runtime evidence |
| --- | --- | --- | --- |
| Damage Numbers (Rust) | r1 | DEVELOPMENT | Host/config/rollback, r25 oracle, real ImGui and ARM checks passed; no gameplay run or installation. |
| Damage Numbers | r25 | READY_TO_DISTRIBUTE | User-approved 1080p size preview; no r25 game run or behavior-suite rerun. Prior r22-config1 Eden confirmation remains scoped to those bytes. |
| Please do Better | r19-savehint | READY_TO_DISTRIBUTE | Host/ARM checks for save feedback; no new game run. Prior r17-config1 Eden confirmation remains scoped to those bytes. |
| Modern Weapon Controls | r11 | READY_TO_DISTRIBUTE | Static cleanup checks; prior r10 controls/help/bowgun acceptance, without exhaustive style/ammo coverage. |
| Key Quest Markers | r2 | READY_TO_DISTRIBUTE | Static cleanup checks; prior r1 Eden Village 1/2-star and Hub 1-star acceptance, plus Ryujinx full-rank coverage. |
| Forge, HD Project, wiki cheats, DTI dumper support | See each record | LOCAL_ONLY | Loader and resource evidence retain their recorded scope. |

The Rust r1 candidate is under `build/damage-numbers-rs/candidates/r1/delivery/`; it uses stock forge-rs configuration and eight ordinary native Forge hooks. [Source and workflow](../mods/damage-numbers-rs/README.md).

Each `mods/<name>/DISTRIBUTION.json` is authoritative. Verified delivery folders
are under `build/<name>/releases/<version>/`; the full distribution check verifies
runtime, ZIP, guides, notices and checksums. All four ready releases are unpublished.

Damage Numbers uses 24 px Wilds/Classic and 20 px Rise bases at 720p, with a
1.4× Rise weak-point boost. Exact r25 evidence is in
[R25_SIZE_CHANGE.json](../mods/damage-numbers/docs/R25_SIZE_CHANGE.json).
Earlier r24 bytes remain under `backups/damage-numbers/base-size-r25-20261008/`.

The 2026-10-08 tested Eden setup used Forge `1.4.1-render1`, Damage Numbers
r22-config1 and Please do Better r17-config1. The user confirmed that setup;
Forge remains LOCAL_ONLY at their direction. The matching
[runtime receipt](CONFIG_RELEASE_RUNTIME.json) identifies log/screenshot and
payload hashes. It establishes no fresh Ryujinx, exhaustive save-restart or
clean-shutdown result. Later plugin revisions have their own static evidence.

## Inputs and installation paths

| Purpose | Path |
| --- | --- |
| Game dump | `~/.local/share/eden/dump/0100770008DD8000/` |
| Uninstalled mod/cheat library | `/mnt/storage2/ROM/Switch/cheats/mhgu/` |
| Eden packages | `~/.local/share/eden/load/0100770008DD8000/` |
| Eden log | `~/.local/share/eden/log/eden_log.txt` |
| Ryujinx-Nextendo packages | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/mods/contents/0100770008dd8000/` |
| Ryujinx-Nextendo logs | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/Logs/` |

The inspected dump is RomFS-only. Library targets are MHGU 1.4.0, cheat build
`FB08F1D20FD1204F`, NSO `FB08F1D20FD1204FE7070672777F869B`; these identifiers
do not verify the running game. Folder presence establishes no activation.
Re-inspect packages/configuration and the tested emulator's latest log when
doing installation or diagnosing a user-run result. Initial counts and library
inventories remain in [local-state.json](local-state.json) as dated snapshots.

## GURecomp Linux runtime

The user confirmed the MHGU 1.4.0 export runs with the process-local SDL3
override, then confirmed Forge PC 0.2.1 runs. Fresh logs corroborate the F10
menu, loader attachment/overlay readiness and resource loading for FOV (Medium),
HD Project and Z_Balanced. Key Quest Markers PC now has a staged Linux/Windows
native candidate, with gameplay acceptance pending and no installation. Local
paths, export behavior, the exact launch command and evidence limits are in
[GURECOMP_LOCAL_SETUP.md](GURECOMP_LOCAL_SETUP.md); the
[runtime receipt](GURECOMP_LOCAL_RUNTIME.json) preserves hashes and log extracts.

## Maintained source and recovery

Preserve `tools/forge-local/` on `codex/forge-legacyctx14`. The integrated adapter
and separate renderer trial are described in [FORGE_LOCAL_BRANCH.md](FORGE_LOCAL_BRANCH.md).
Use Base -> HD Project -> Z_Balanced -> others; current ownership is in
[CLEANUP_HD_PROJECT.md](CLEANUP_HD_PROJECT.md).

Retired components remain in Git history. Required support moved to
`mods/forge-patched/compat/`, shared binary/asset helpers, Modern Controls' `help/`,
`work/shared/game-exefs/` and `work/shared/forge-sdk/`. Historical build-source
hashes and their current destinations are recorded in
[WORKSPACE_SOURCE_MIGRATION.json](WORKSPACE_SOURCE_MIGRATION.json).
Active rollback material stays under `backups/`.

The four standalone source folders own their recipes, tests, pinned dependencies
and export lists. [STANDALONE_MIGRATION.json](STANDALONE_MIGRATION.json) records
the migration; [STANDALONE_MODS.md](STANDALONE_MODS.md) describes the workflow.
There is no automated in-game suite. Keep the DTI dumper and flag removed during
play; its [runtime record](DTI_DUMPER_RUNTIME.md) documents failure and recovery.
