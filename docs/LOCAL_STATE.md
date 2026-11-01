# Local state

Baseline: stock Switch Forge 1.5.1 and forge-rs 1.5.0, on branch `main`. On PC, MHGURecomp loads the Switch NROs. This file describes workspace sources and deliveries, not current emulator activation.

## Deliveries

Each mod's DISTRIBUTION.json is authoritative. "Packaged" means a local,
unpublished ZIP; approval is not a gameplay result. Design and manual checks are
in each mod's DEVELOPMENT.md; exact validation and runtime records are in its
EVIDENCE.json.

| Mod | Current | Acceptance scope |
| --- | --- | --- |
| Damage Numbers | r36 READY_TO_DISTRIBUTE (2026-10-30) | Hits outside the camera view stay hidden until the camera turns to them instead of showing at screen centre. Release `build/damage-numbers/releases/r36/damage-numbers-r36.zip`, promoted unchanged from the candidate. User reports an Eden run (log not retained); r37-projection-ab, a diagnostic with r36's display code, ran docked on Eden and looked right. Handheld unreported. |
| Key Quest Markers | r18 READY_TO_DISTRIBUTE (2026-10-18) | Link rebuild of the Eden/Linux-accepted r17. HD is optional. Ryujinx and Switch hardware unconfirmed. |
| Modern Sharpness Gauge | r63 READY_TO_DISTRIBUTE (2026-11-01) | r62 with its run instruments removed, promoted on static validation by the user's choice: r63 itself has never been run. Runtime evidence is r62, accepted on Eden 2026-11-01 at the red tier and at `build/modern-sharpness-gauge/candidates/r62/`. Release `build/modern-sharpness-gauge/releases/r63/modern-sharpness-gauge-r63.zip`, payload NRO `202c0719c7edfb28f4b3b359630b60f84ec69ac00c632a573284f7b2d3cc965f`. Open: an orange-tier crop, Ryujinx and native hardware. r61 is withdrawn, do not ship. |
| Modern Weapon Controls | r13 DEVELOPMENT candidate (2026-11-02), gameplay NOT RUN | Rust/forge-rs rewrite of r12 using Forge hooks, no intended behaviour change. Candidate `build/modern-weapon-controls/candidates/r13/delivery/`, payload NRO `24677d6636b1527e8196af79a58efcae7e1b4a3b969e0ab5a7ce3d01c281333c`. The approved r12 release is preserved at `backups/accepted/modern-weapon-controls/r12-before-rust-port/`. |
| Please do Better | r25 DEVELOPMENT candidate (2026-11-02), gameplay NOT RUN | Rust/forge-rs rewrite of r24-forge151, no intended behaviour change. Candidate `build/please-do-better/candidates/r25/delivery/`, payload NRO `84902446e37c6abbd41516a751e66d0adb76262c9531bcf642664095979a8c32`. The approved r24-forge151 release is preserved at `backups/accepted/please-do-better/r24-forge151-before-rust-port/`. |
| Shared Urgent Quests | r2 DEVELOPMENT candidate (2026-11-02), gameplay NOT RUN | Rust/forge-rs rewrite of r1, no intended behaviour change. Records a rank-up urgent clear for an online client when the urgent is on that client's own board. Candidate `build/shared-urgent-quests/candidates/r2/delivery/`, payload NRO `ea71cb605c28a4cc9d8cb34cf152582dc1704e3a4e07b6dc632daae0800c689b`. Needs a two-instance session test. |
| HD Project, wiki cheats, DTI dumper support | LOCAL_ONLY | Local integrations. |

Candidates are under `build/NAME/candidates/VERSION/`, packaged releases under
`build/NAME/releases/VERSION/`.

## Last gameplay-accepted builds

The rollback for a release with no gameplay run of its own. `backups/` is an optional local archive, and nothing here or in any tool depends on it.

| Mod | Build | Where | Scope |
| --- | --- | --- | --- |
| Damage Numbers | r36 | `build/damage-numbers/releases/r36/` | User-reported Eden run, log not retained |
| Key Quest Markers | r17 | `build/key-quest-markers/candidates/r17/` | Accepted on Eden/Linux |
| Modern Sharpness Gauge | r62 | `build/modern-sharpness-gauge/candidates/r62/` | Accepted on Eden at the red tier |
| Modern Weapon Controls | r10 | `build/modern-weapon-controls/candidates/r10/` | Accepted on the retired loader; not checked on stock Forge 1.5.1 |
| Please do Better | r23, r17-config1 | `build/please-do-better/candidates/r23/`, `build/please-do-better/candidates/r17-config1/` | r23 confirmed loading with an approval; r17-config1 confirmed by the user on the retired loader |

The three ZIP-only folders have a `SHA256SUMS`. Dated records in `EVIDENCE.json`, `COMPACTION.json` and `WORKSPACE_EVIDENCE.json` name `backups/` paths that may no longer exist. They keep the hashes, which remain each file's identity.

Open device reports: Damage Numbers placement on real Switch and Android in
handheld mode (reported against r28; testers' exact loader/plugin hashes were
not supplied). No later build has run on an affected device.

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

[COMPACTION.json](COMPACTION.json) records source revisions, archive and payload hashes, removed paths and validation for the 2026-10-15 cleanup. [WORKSPACE_EVIDENCE.json](WORKSPACE_EVIDENCE.json) keeps dated workspace research. Run logs removed from the docs are in Git history at commit `31ed4ef` and earlier. The recovery tag is `cleanup/before-stock-forge-20261015`. Tag `archive/backups-records-20261102` holds the pre-prune `work/` research notes, the text records from `backups/accepted/`, and an inventory of `backups/` taken on 2026-11-02, with no working-tree cost: `git show archive/backups-records-20261102:backups-inventory.txt`.
