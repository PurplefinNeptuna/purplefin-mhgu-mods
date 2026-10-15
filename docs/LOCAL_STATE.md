# Local state

Workspace baseline updated 2026-10-15: stock Switch Forge 1.5.1, forge-rs 1.5.0,
and stock Forge PC 0.2.1. This cleanup changes workspace sources and deliveries;
it does not inspect or change current emulator activation.

The workspace now uses `main`. Merged task branches, obsolete local source
forks and the old release worktree are removed. Historical commits remain
reachable through main or archive tags; the cleanup receipt records their tips.

## Deliveries and acceptance

DISTRIBUTION.json in each mod is authoritative. Damage Numbers r26 and Key Quest
Markers r15 replace the C++ Switch projects with fully renamed Rust implementations.
Modern Weapon Controls r12 and Please do Better r24-forge151 target stock Forge.
The user approved distribution of these maintenance builds after validation;
there is no new gameplay run. Earlier accepted payloads and their evidence remain
under backups/accepted/ and the per-mod EVIDENCE.json collections.

All four PC mods retain their accepted Linux/Windows payloads. Linux user
acceptance is scoped to the recorded binaries; Windows gameplay remains untested.
See README.md in each source folder for installation/use, DEVELOPMENT.md for
implementation/manual scenarios, and its distribution/runtime records for evidence.
The Damage Numbers r3 third-party placement report at 900p/1.25× was deferred by
the user, unreproduced locally; this maintenance task does not investigate it.

Key Quest Markers r17 is READY_TO_DISTRIBUTE following user-confirmed Eden/Linux
testing of the unchanged candidate. Other platforms remain unconfirmed. It uses
the game UI colours for the existing three saved colour controls. It preserves the original 32×32
emblem, Y3, X365/329 and title widths299/263. Defaults are Gathering green
#006305 for keys, objective red #A30000 for urgents and grey for completed/old
quests. Edits require Save & apply. The r15 release is
preserved under backups/accepted/key-quest-markers/r15-before-colours/. The game
owns native children and draw-cache/map allocations.
r17 also removes the old success/row ERROR diagnostics; startup is one INFO
line and genuine failures remain deduplicated. English HD resources remain an
external dependency.

## Inputs and runtime paths

| Purpose | Path |
| --- | --- |
| Game dump/RomFS | `~/.local/share/eden/dump/0100770008DD8000/` |
| Uninstalled library | `/mnt/storage2/ROM/Switch/cheats/mhgu/` |
| Eden packages | `~/.local/share/eden/load/0100770008DD8000/` |
| Eden log | `~/.local/share/eden/log/eden_log.txt` |
| Ryujinx-Nextendo packages | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/mods/contents/0100770008dd8000/` |
| Ryujinx-Nextendo logs | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/Logs/` |
| Copied native inputs | `work/shared/game-exefs/` |
| Official Forge package/input | `work/shared/forge-1.5.1/` |
| Ghidra and saved DTI | `work/research-tooling/` |

The supplied dump is RomFS-only. Library target is game 1.4.0, cheat build
FB08F1D20FD1204F, NSO FB08F1D20FD1204FE7070672777F869B. Verify actual launch
version/build before executable work. Folder presence proves no activation.
Trust the user's alternative-mod activation choices; investigate overlap only
when fresh evidence implicates it. After a reported run, inspect that emulator's
latest log before concluding.

GURecomp installation/export paths, SDL3 override and native-port limits are in
[GURECOMP.md](GURECOMP.md). HD resource priorities are in
[CLEANUP_HD_PROJECT.md](CLEANUP_HD_PROJECT.md). DTI extraction is not enabled
for gameplay. There is no automated in-game suite.

## Evidence and recovery

[COMPACTION.json](WORKSPACE_EVIDENCE.json) records source revisions, archive/payload
hashes, removed paths, validation and space measurements.
[WORKSPACE_EVIDENCE.json](WORKSPACE_EVIDENCE.json) preserves dated workspace
research and original migration receipts. Historical installed hashes and
settings are dated evidence, not a statement about current activation.
The recovery tag is `cleanup/before-stock-forge-20261015`; Git history is intact.
