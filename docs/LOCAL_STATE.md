# Local state

Baseline: stock Switch Forge 1.5.1 and forge-rs 1.5.0, branch `main`. MHGURecomp
loads the Switch NROs. This file lists workspace builds, not emulator activation.

Each mod's `DISTRIBUTION.json` is authoritative for status; `EVIDENCE.json` holds
run history and tester quotes; each build folder's `SHA256SUMS` holds its hashes.
Candidates are under `build/NAME/candidates/VERSION/`, packaged releases under
`build/NAME/releases/VERSION/`.

## Current builds

| Mod | Current | Status | Runtime |
| --- | --- | --- | --- |
| Damage Numbers | r48 | READY_TO_DISTRIBUTE, release | Runs on MHGU Recomp with Purple-lib r20 |
| ImGui Meter | r4 | DEVELOPMENT | NOT RUN; r3 cut Eden to 37 fps (r1 ran on MHGU Recomp, unitemized) |
| Key Quest Markers | r23 | DEVELOPMENT, candidate | Not run (r21 plus orange badges for reward quests and their chains); r21 Recomp, unitemized; r20 accepted on Eden |
| Lock-on Target | r2 | READY_TO_DISTRIBUTE, release | Eden and MHGU Recomp |
| Modern Weapon Controls | r15 | READY_TO_DISTRIBUTE, release | Loads on MHGU Recomp; controls accepted on r14 (Eden) |
| Multiplayer Roaming (`online-roaming`) | r16 | READY_TO_DISTRIBUTE, release | Multiplayer, user report; Eden and MHGU Recomp installed |
| Please do Better | r37 | READY_TO_DISTRIBUTE, release | MHGU Recomp with Purple-lib r17 (r36 registers on Eden too) |
| Purple-lib | r22 | READY_TO_DISTRIBUTE, release | Eden and MHGU Recomp 0.17 (input hold with game actions) |
| Purple-lib Tester | r14 | DEVELOPMENT, not for distribution | Not run (8 extra sets); r13 on MHGU Recomp with Purple-lib r20 |
| Shared Urgent Quests | r2 | READY_TO_DISTRIBUTE, release | Eden joiner, no joiner log |
| Skin Loader | r11 | DEVELOPMENT, candidate (Rust) | Not run (r10 made fast with a colour table; r10 slow on MHGU Recomp); r9 accepted on MHGU Recomp with a second player |
| Village Quests in Hub | r6 | READY_TO_DISTRIBUTE, release | Accepted on Eden beside MHGU Definitive Edition |
| WishFinder (was Wishlist) | r143 | DEVELOPMENT, candidate | Not run (r135 plus the rare pickup jingle, quest table stages 101 to 104, weapon levels forged or upgraded, API 8; no gather-sound log; r142 crashed KatSmithy in MHGU Recomp); r135 the release; r134 accepted on Eden with MHGU Definitive Edition 3.0.0. Needs Key Quest Markers r20+ |
| WishFinder bridge for My Weapon Tree | r11 | READY_TO_DISTRIBUTE, release | Eden with My Weapon Tree 0.67 and WishFinder r83 |
| World Sharpness Gauge | r70 | READY_TO_DISTRIBUTE, release | MHGU Recomp; r68 on Eden and Ryubing |
| HD Project, wiki cheats, DTI dumper support | — | LOCAL_ONLY | — |

Ryujinx and Switch hardware are unconfirmed for every mod unless its
`EVIDENCE.json` says otherwise.

## Last gameplay-accepted builds

The rollback for a current build that has no run of its own.

| Mod | Build | Where |
| --- | --- | --- |
| Damage Numbers | r48 (r38 on Eden) | `build/damage-numbers/releases/r48/`, `candidates/r47/`, `r42/`, `r38-accepted/` |
| Key Quest Markers | r20 | `build/key-quest-markers/candidates/r20/` |
| Lock-on Target | r2 | `build/lock-on-target/candidates/r2/` |
| Modern Weapon Controls | r14 | `build/modern-weapon-controls/candidates/r14/` |
| Multiplayer Roaming | r16 | `build/online-roaming/candidates/r16/` |
| Please do Better | r37 (r31 on Eden, r30 on Ryubing) | `build/please-do-better/candidates/r37/`, `r31/`, `r30/` |
| Purple-lib | r22 | `build/purple-lib/candidates/r22/`, `r21/`, `r20/`, `r19/`, `r18/`, `r17/`, `r16/` |
| Purple-lib Tester | r11 | `build/purple-lib-tester/candidates/r11/` |
| Shared Urgent Quests | r2 | `build/shared-urgent-quests/candidates/r2/` |
| Skin Loader | r9 (r8 before it) | `build/skin-loader/candidates/r9/`, `r8/` |
| Village Quests in Hub | r6 | `build/village-quests-in-hub/candidates/r6/` |
| WishFinder | r134 | `build/wishfinder/candidates/r134/`, `r131/`, `r127/`, `r122/`, `r119/`, `r114/`, `r111/`, `r107/`, `r105/`, `r103/`, `r102/`, `r92/`, `r86/`, `r85/`, `r82/`, `r76/`, `r72/` |
| WishFinder bridge for My Weapon Tree | r11 | `build/wishfinder-mwt-bridge/candidates/r11/`, `r10/` |
| World Sharpness Gauge | r70 (r68 on Eden and Ryubing) | `build/world-sharpness-gauge/candidates/r70/`, `r68/` |

Older accepted C++ builds: `build/modern-weapon-controls/candidates/r10/`,
`build/please-do-better/candidates/r23/` and `r17-config1/`.

## Inputs and runtime paths

| Purpose | Path |
| --- | --- |
| Game RomFS | `/mnt/storage2/Programs/MHGURecomp/data/romfs/` (1.4.0; the Eden dump keeps only `exefs` and `nso`) |
| Sealed base game (v0) | `/mnt/storage2/ROM/Switch/Game/Monster Hunter Generations Ultimate™ [0100770008DD8000][v0]).xci` |
| Sealed 1.4.0 update (v262144) | `/mnt/storage2/ROM/Switch/Update+DLC/MONSTER HUNTER GENERATIONS ULTIMATE [0100770008DD8800][v262144].nsp` |
| Keys for the XCI/NSP | `/mnt/storage2/ROM/Switch/keys+firmware/` |
| Uninstalled library | `/mnt/storage2/ROM/Switch/cheats/mhgu/` |
| Eden packages / log | `~/.local/share/eden/load/0100770008DD8000/`, `~/.local/share/eden/log/eden_log.txt` |
| Ryubing 1.3.3 (portable) | `/mnt/storage2/Programs/Ryubing-1.3.3/app/`, data in `app/portable/` |
| Ryujinx-Nextendo | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/` (`mods/contents/0100770008dd8000/`, `Logs/`) |
| Copied native inputs (1.4.0 code) | `work/shared/game-exefs/` |
| Official Forge package | `work/shared/forge-1.5.1/` |
| Ghidra and saved DTI | `work/research-tooling/` |

Library target: game 1.4.0, cheat build FB08F1D20FD1204F, NSO
FB08F1D20FD1204FE7070672777F869B. Check the launched version before executable
work. HD resource priorities: [CLEANUP_HD_PROJECT.md](CLEANUP_HD_PROJECT.md).
DTI extraction is not enabled for gameplay.

## Recovery

- [COMPACTION.json](COMPACTION.json): hashes and removed paths of the 2026-10-15 cleanup (its `starting_commit` is the pre-cleanup state).
- [WORKSPACE_EVIDENCE.json](WORKSPACE_EVIDENCE.json): workspace research records.
- `/mnt/storage2/Programs/MHGU_Modding-pre-rewrite.git`: history before the 2026-11-11 rewrite, with its tags (`cleanup/before-stock-forge-20261015`, `archive/backups-records-20261102` holding pre-prune `work/` notes and `backups-inventory.txt`).
- Run logs removed from the docs: Git history at `84e8410` and earlier.
