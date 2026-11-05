# Local state

Baseline: stock Switch Forge 1.5.1 and forge-rs 1.5.0, on branch `main`. On PC, MHGURecomp loads the Switch NROs. This file describes workspace sources and deliveries, not current emulator activation.

## Deliveries

Each mod's DISTRIBUTION.json is authoritative. "Packaged" means a local,
unpublished ZIP; approval is not a gameplay result. Design and manual checks are
in each mod's DEVELOPMENT.md; exact validation and runtime records are in its
EVIDENCE.json.

| Mod | Current | Acceptance scope |
| --- | --- | --- |
| Damage Numbers | r38 READY_TO_DISTRIBUTE (2026-11-05) | r36 plus stacking on another plugin's Forge hook; user reported damage numbers working on Eden (2026-11-05). Scope of r36: Hits outside the camera view stay hidden until the camera turns to them instead of showing at screen centre. Release `build/damage-numbers/releases/r36/damage-numbers-r36.zip`, promoted unchanged from the candidate. User reports an Eden run (log not retained); r37-projection-ab, a diagnostic with r36's display code, ran docked on Eden and looked right. Handheld unreported. |
| Key Quest Markers | r19 READY_TO_DISTRIBUTE (2026-11-05) | r18 plus stacking on another plugin's Forge hook; user reported quest badges working on Eden (2026-11-05). Scope of r18: Link rebuild of the Eden/Linux-accepted r17. HD is optional. Ryujinx and Switch hardware unconfirmed. |
| Modern Weapon Controls | r15 READY_TO_DISTRIBUTE (2026-11-05) | r14 without the fixed-list check that aborted on MHGURecomp; not run. r14 is r13 plus stacking on another plugin's Forge hook; user reported the ZR remap working on Eden (2026-11-05). Scope of r13: Rust/forge-rs rewrite of r12 using Forge hooks. User reported it working on Eden, unitemized; installed NRO matches.  Ryujinx and native Switch unconfirmed. |
| Online Roaming | r14 DEVELOPMENT candidate | r13 plus name tags outside a lobby, with L switching their mode. Gameplay NOT RUN. Candidate `build/online-roaming/candidates/r14/delivery/`, payload NRO `5655be422b6b1fc1a57af6432c4a6b42f1c2c160c3eaadbf711c13cfc5923fa4`. r13 was READY_TO_DISTRIBUTE, unplayed, and is preserved at `backups/accepted/online-roaming/r13-before-name-tags/`. r12 has logs from one Eden session (2026-11-05), no player report. Scope of r11: On top of roaming, players with the mod who share a village, bedroom, the ranch or a preparation area see each other's hunters and Palicos, and r11 updates a hunter whose look changes. Candidate `build/online-roaming/candidates/r11/delivery/`, payload NRO `d4098cefbbdb74f41556400c648e62202b5e1dac23a55f4f655ae463db0c93c0`. r11 is NOT RUN. r10 is the accepted build for seeing each other: on Eden, "its working well now", with a look change not updating as the open report. Exit 5, area 6, saving and quests during a village visit, Ryujinx and native Switch have no run. |
| Please do Better | r26 READY_TO_DISTRIBUTE (2026-11-05) | r25 plus stacking on another plugin's Forge hook; user reported luck highlights working on Eden (2026-11-05). Scope of r25: Rust/forge-rs rewrite of r24-forge151. User reported it working on Eden, unitemized; installed NRO matches.  Ryujinx and native Switch unconfirmed. |
| Shared Urgent Quests | r2 READY_TO_DISTRIBUTE (2026-11-05) | Rust/forge-rs rewrite of r1, no intended behaviour change. Records a rank-up urgent clear for an online client when the urgent is on that client's own board. Candidate `build/shared-urgent-quests/candidates/r2/delivery/`, payload NRO `ea71cb605c28a4cc9d8cb34cf152582dc1704e3a4e07b6dc632daae0800c689b`. User reported it working for a joiner on Eden, with the rank-up and next quests following, for the Diablos and Nakarkos urgents; the host's installed NRO matches, and no joiner log exists. A joiner without the urgent on their board, Ryujinx and native Switch are untested. |
| Village Quests in Hub | r5 READY_TO_DISTRIBUTE (2026-11-05) | r4 without the fixed-list check that aborted on MHGURecomp; not run. r4 is r3 plus stacking on another plugin's Forge hook; logs from one Eden session (2026-11-05), no player report. Scope of r3: L or R at the Hub or Pub quest counter switches to the Village quests, to post and join them. Rebuilds a Village list left empty by an area load, and lets a joiner take either record of a variant pair. Forge port of MHGURecomp's feature without its HP scaling. Candidate `build/village-quests-in-hub/candidates/r3/delivery/`, payload NRO `28245e9292f41e8caaad033ba3d215dbf6362f3d72831b32c1dd22e8b0ef42b5`. r3 gameplay NOT RUN. r2 is the accepted build for the rebuilt list, user report on Eden, see its `EVIDENCE.json`. |
| World Sharpness Gauge | r67 READY_TO_DISTRIBUTE (2026-11-05) | The per-tier bar works like Monster Hunter: World's. r67 loads beside plugins that hook the same functions, such as KatLib, and its cut and shade follow the bar's uploaded matrix, so they track UIScale live. Candidate `build/world-sharpness-gauge/candidates/r67/delivery/`, payload NRO `06990cd19a0549d7c92646007ff654c9ce312b03329bab87b8b12c5f236058ee`. r67 gameplay NOT RUN. r65 is the approved release, kept in `backups/accepted/world-sharpness-gauge/r65-before-katlib-compat/`. r64 is the accepted build: on Eden, "all works perfectly" over two quests with different weapons. Sharpness +1/+2, Heavy Polish, Ryujinx and native hardware have no runtime check. r61 is withdrawn, do not ship. |
| HD Project, wiki cheats, DTI dumper support | LOCAL_ONLY | Local integrations. |

Candidates are under `build/NAME/candidates/VERSION/`, packaged releases under
`build/NAME/releases/VERSION/`.

## Last gameplay-accepted builds

The rollback for a release with no gameplay run of its own. `backups/` is an optional local archive, and nothing here or in any tool depends on it.

| Mod | Build | Where | Scope |
| --- | --- | --- | --- |
| Damage Numbers | r38, before its log-line amendment | `build/damage-numbers/candidates/r38-accepted/` | User-reported Eden run for damage numbers, in a two-player session; not itemized further. Loading beside a foreign hook not exercised |
| Key Quest Markers | r19 | `build/key-quest-markers/candidates/r19/` | User-reported Eden run for quest badges, in a two-player session; not itemized further. Loading beside a foreign hook not exercised |
| Modern Weapon Controls | r14 | `build/modern-weapon-controls/candidates/r14/` | User-reported Eden run for the ZR remap, in a two-player session; not itemized further. Loading beside a foreign hook not exercised |
| Online Roaming | r10 | `build/online-roaming/candidates/r10/` | User-reported Eden run with two players, both logs read; all eight meetings enabled. A look change doesn't update |
| Please do Better | r26 | `build/please-do-better/candidates/r26/` | User-reported Eden run for luck highlights, in a two-player session; not itemized further. Loading beside a foreign hook not exercised |
| Shared Urgent Quests | r2 | `build/shared-urgent-quests/candidates/r2/` | User-reported Eden run for a joiner on the Diablos and Nakarkos urgents, no joiner log |
| Village Quests in Hub | r2 | `build/village-quests-in-hub/candidates/r2/` | User-reported Eden run for the blank difficulty menu fix, no log lines from the mod |
| World Sharpness Gauge | r67 | `build/world-sharpness-gauge/candidates/r67/` | User-reported quest on MHGURecomp beside KatLib and UIScale. r64 at `build/world-sharpness-gauge/candidates/r64/` is the Eden-accepted picture, under an earlier name: remove the other folder when switching |

Older accepted C++ builds stay at `build/modern-weapon-controls/candidates/r10/` and `build/please-do-better/candidates/r23/` and `r17-config1/`, each with a `SHA256SUMS`. Dated records in `EVIDENCE.json`, `COMPACTION.json` and `WORKSPACE_EVIDENCE.json` name `backups/` paths that may no longer exist. They keep the hashes, which remain each file's identity.

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
