# Local state

Workspace baseline updated 2026-10-15: stock Switch Forge 1.5.1 and forge-rs
1.5.0, on branch `main`. GURecomp, Forge PC and the `-pc` ports were retired on
2026-10-30 because MHGURecomp loads the Switch NROs. Merged task branches, obsolete
source forks and the old release worktree are removed; their tips are recorded
in [COMPACTION.json](COMPACTION.json) and remain reachable through main or archive
tags. This file describes workspace sources and deliveries, not current
emulator activation.

## Deliveries

Each mod's DISTRIBUTION.json is authoritative. "Packaged" means a local,
unpublished ZIP; approval is not a gameplay result. Release history, design and
manual checks are in each mod's DEVELOPMENT.md; exact validation and runtime
records are in its EVIDENCE.json.

| Mod | Current | Acceptance scope |
| --- | --- | --- |
| Damage Numbers | r36 READY_TO_DISTRIBUTE (2026-10-30) | Hits outside the camera view stay hidden until the camera turns to them instead of showing at screen centre. Release `build/damage-numbers/releases/r36/damage-numbers-r36.zip`, promoted unchanged from the candidate (approval and archive in `backups/accepted/damage-numbers/r36-distribution-approved/`). User reports an Eden run (log not retained); r37-projection-ab, a diagnostic with r36's display code, ran docked on Eden and looked right. Handheld unreported. Release r35 is archived at `backups/accepted/damage-numbers/r35-before-hidden-offscreen/`. r27 was the last user-tested build before this. |
| Key Quest Markers | r18 READY_TO_DISTRIBUTE (2026-10-18) | Link rebuild of the Eden/Linux-accepted r17. HD is optional. Ryujinx and Switch hardware unconfirmed. |
| Modern Sharpness Gauge | r63 READY_TO_DISTRIBUTE (2026-11-01) | r62 with its run instruments removed, promoted on static validation by the user's choice: r63 itself has never been run. Runtime evidence is r62, accepted on Eden 2026-11-01 at the red tier and frozen in `backups/accepted/modern-sharpness-gauge/r62-screen-accepted/`. Release `build/modern-sharpness-gauge/releases/r63/modern-sharpness-gauge-r63.zip`, payload NRO `202c0719c7edfb28f4b3b359630b60f84ec69ac00c632a573284f7b2d3cc965f`, approved snapshot in `backups/accepted/modern-sharpness-gauge/r63-distribution-approved/`. Open: an orange-tier crop, Ryujinx and native hardware. r61 is withdrawn, do not ship. Run history and corrections are in the mod's DEVELOPMENT.md. |
| Modern Weapon Controls | r12 READY_TO_DISTRIBUTE | Stock-Forge maintenance build approved after static validation; no new gameplay run. |
| Please do Better | r24-forge151 READY_TO_DISTRIBUTE | Stock-Forge maintenance build approved after static validation; no new gameplay run. |
| Shared Urgent Quests | r1 DEVELOPMENT candidate (2026-10-21), gameplay NOT RUN | Records a rank-up urgent clear for an online client when the urgent is on that client's own board. Needs a two-instance session test. |
| HD Project, wiki cheats, DTI dumper support | LOCAL_ONLY | Local integrations. |

Candidates are under `build/NAME/candidates/VERSION/`, packaged releases under
`build/NAME/releases/VERSION/`. Superseded and accepted deliveries are preserved
unchanged under `backups/accepted/NAME/`, named after the change that replaced
them (for example `r30-before-status-damage/`).

Open device reports: Damage Numbers placement on real Switch and Android in
handheld mode (reported against r28; testers' exact loader/plugin hashes were
not supplied). Neither r29-diagnostics nor r30 was run on an affected device.
The r28 and r18 rebuilds do not bundle or verify the updated loader.

## Inputs and runtime paths

| Purpose | Path |
| --- | --- |
| Game dump/RomFS | `~/.local/share/eden/dump/0100770008DD8000/` |
| Sealed base game (v0) | `/mnt/storage2/ROM/Switch/Game/Monster Hunter Generations Ultimate™ [0100770008DD8000][v0]).xci` |
| Sealed 1.4.0 update (v262144) | `/mnt/storage2/ROM/Switch/Update+DLC/MONSTER HUNTER GENERATIONS ULTIMATE [0100770008DD8800][v262144].nsp` |
| Keys for the XCI/NSP | `/mnt/storage2/ROM/Switch/keys+firmware/` |
| Uninstalled library | `/mnt/storage2/ROM/Switch/cheats/mhgu/` |
| Eden packages | `~/.local/share/eden/load/0100770008DD8000/` |
| Eden log | `~/.local/share/eden/log/eden_log.txt` |
| Ryujinx-Nextendo packages | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/mods/contents/0100770008dd8000/` |
| Ryujinx-Nextendo logs | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/Logs/` |
| Copied native inputs | `work/shared/game-exefs/` |
| Official Forge package/input | `work/shared/forge-1.5.1/` |
| Ghidra and saved DTI | `work/research-tooling/` |

The supplied dump is RomFS-only. Eden made it on 2026-10-01 while loading the
update from its external content folder (`Update+DLC/`), so it should hold base
and 1.4.0 merged; no file has been compared against the base yet. The update's
code is the copy in `work/shared/game-exefs/`. Library target is game 1.4.0, cheat build
FB08F1D20FD1204F, NSO FB08F1D20FD1204FE7070672777F869B. Verify actual launch
version/build before executable work. Folder presence proves no activation.
Trust the user's alternative-mod activation choices; investigate overlap only
when fresh evidence implicates it. After a reported run, inspect that emulator's
latest log before concluding.

HD resource priorities are in
[CLEANUP_HD_PROJECT.md](CLEANUP_HD_PROJECT.md). DTI extraction is not enabled
for gameplay. There is no automated in-game suite.

## Evidence and recovery

[COMPACTION.json](COMPACTION.json) records source revisions, archive/payload
hashes, removed paths, validation and space measurements for the 2026-10-15
cleanup. [WORKSPACE_EVIDENCE.json](WORKSPACE_EVIDENCE.json) preserves dated
workspace research and original migration receipts. Historical installed hashes
and settings are dated evidence, not a statement about current activation.
The recovery tag is `cleanup/before-stock-forge-20261015`; Git history is intact.
