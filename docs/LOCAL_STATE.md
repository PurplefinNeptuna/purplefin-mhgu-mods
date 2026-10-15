# Local state

Switch delivery documentation refreshed 2026-10-10 from the tracked distribution
and evidence records; Eden/Ryujinx activation was not re-inspected for that
cleanup. GURecomp's exported Linux game, resource packages and Forge PC loader
were separately inspected on 2026-10-12.

## Local deliveries

| Mod | Version | Status | Runtime evidence |
| --- | --- | --- | --- |
| Damage Numbers PC | r3 | READY_TO_DISTRIBUTE | User accepted Linux r3; logs/hashes confirm eight hooks and two settings saves. Windows gameplay remains untested. |
| Damage Numbers (Rust) | r3 | DEVELOPMENT | External OpenSans/RGBA assets, 24 exact r2 visual scenes, file/lifecycle failures, host and ARM checks passed; no gameplay acceptance. |
| Damage Numbers | r25 | READY_TO_DISTRIBUTE | User-approved 1080p size preview; no r25 game run or behavior-suite rerun. Prior r22-config1 Eden confirmation remains scoped to those bytes. |
| Please do Better PC | r1 | READY_TO_DISTRIBUTE | Unchanged paired binaries; Linux user acceptance and exact runtime evidence recorded. Windows gameplay remains untested. |
| Please do Better | r23-reward-pages | READY_TO_DISTRIBUTE | User approved the unchanged candidate. Fresh Eden log/installed hash confirm r23 loading; individual reward-page, Palico, appraisal/collection, persistence and consecutive-quest checks were not enumerated. Ryujinx/native Switch remain untested. |
| Modern Weapon Controls | r11 | READY_TO_DISTRIBUTE | Static cleanup checks; prior r10 controls/help/bowgun acceptance, without exhaustive style/ammo coverage. |
| Key Quest Markers | r2 | READY_TO_DISTRIBUTE | Static cleanup checks; prior r1 Eden Village 1/2-star and Hub 1-star acceptance, plus Ryujinx full-rank coverage. |
| Key Quest Markers PC | r1 | READY_TO_DISTRIBUTE | User-confirmed successful Linux use; matching installed/loaded-copy hashes and fresh activation logs. Windows build/static checks only; gameplay untested. |
| Native Quest Badges (Rust) | r10 | DEVELOPMENT | Request-slot placement and native title auto-fit; r10 manual acceptance pending. Preceding r9 is user-confirmed working on Eden/Linux on 2026-10-15 and remains preserved. |
| Forge, HD Project, wiki cheats, DTI dumper support | See each record | LOCAL_ONLY | Loader and resource evidence retain their recorded scope. |

The Rust r3 candidate is under `build/damage-numbers-rs/candidates/r3/delivery/`; it uses stock forge-rs configuration and eight ordinary native Forge 1.5.0 hooks. Loader-version gating is disabled. The previous r1 and r2 deliveries remain preserved. [Source and workflow](../mods/damage-numbers-rs/README.md).

Native Quest Badges r9 uses MHGU's in-game GUI, with native texture children
reusing the loaded HD emblem. Forge provides the supporting APIs; drawing uses
neither ImGui nor its free-render callback. ARC files remain untouched. The
working fix decodes GUI immediate kinds17/18 directly and uses Mask0 for normal
colour drawing. Preserve the accepted r9 payload; see the
[native audit](../mods/key-quest-markers-rs/docs/NATIVE_AUDIT.md) and
[runtime evidence](../mods/key-quest-markers-rs/docs/RUNTIME_RESULTS.json).
The r10 candidate moves badges into the request slot, or four pixels left of a
visible bubble, and fits long titles with native AutoScale. It has separate manual
acceptance pending; r9 confirmation does not apply to the new placement.
Future native menu work should start with the reusable
[native GUI modding guide](NATIVE_GUI_MODDING.md).

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
HD Project and Z_Balanced. Key Quest Markers PC r1 has a verified Linux/Windows
local release and matching installed Linux payload. The user confirmed it worked
well; individual ranks/languages/screens were not enumerated, and Windows gameplay
is untested. Local
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

Modern Weapon Controls PC r1 is READY_TO_DISTRIBUTE with matching Linux/Windows
payloads and English help. The user confirmed Linux use; fresh logs and hashes
confirm registration, activation and both help ARC reads. Individual cases were
not enumerated, and Windows gameplay remains untested. See
[its runtime receipt](../mods/modern-weapon-controls-pc/RUNTIME_RESULTS.json).

Damage Numbers PC r3 is the third native release, approved on 2026-10-13.
Stock Forge PC 0.2.1 guest calls supply SDK thread identity without a loader patch.
The current export supplies the alternate `0x16dd4c` HZV block, avoiding re-export.
The user accepted Linux use; installed and loaded hashes match the released SO.
Specific cases were not enumerated, and Windows gameplay remains untested.
The release is unpublished. See
[its development guide](../mods/damage-numbers-pc/DEVELOPMENT.md) and
[stock-loader integration](../mods/damage-numbers-pc/STOCK_FORGE.md).
