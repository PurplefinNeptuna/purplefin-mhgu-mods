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
| Damage Numbers | r42 | READY_TO_DISTRIBUTE, release | MHGU Recomp (FSR on) |
| ImGui Meter | r1 | DEVELOPMENT | Ran on MHGU Recomp, unitemized |
| Key Quest Markers | r20 | READY_TO_DISTRIBUTE, release | Eden, unitemized |
| Lock-on Target | r2 | READY_TO_DISTRIBUTE, release | Eden and MHGU Recomp |
| Modern Weapon Controls | r15 | READY_TO_DISTRIBUTE, release | Loads on MHGU Recomp; controls accepted on r14 (Eden) |
| Multiplayer Roaming (`online-roaming`) | r15 | READY_TO_DISTRIBUTE, release | Eden and MHGU Recomp |
| Please do Better | r37 | READY_TO_DISTRIBUTE, release | MHGU Recomp with Purple-lib r17 (r36 registers on Eden too) |
| Purple-lib | r18 | DEVELOPMENT | Not run (topic limits 255; r17 release works on Eden and MHGU Recomp) |
| Purple-lib Tester | r10 | DEVELOPMENT, not for distribution | Works on Eden and MHGU Recomp with Purple-lib r17 |
| Shared Urgent Quests | r2 | READY_TO_DISTRIBUTE, release | Eden joiner, no joiner log |
| Village Quests in Hub | r6 | READY_TO_DISTRIBUTE, release | Accepted on Eden beside MHGU Definitive Edition |
| WishFinder (was Wishlist) | r68 | READY_TO_DISTRIBUTE, release | Accepted on MHGU Recomp in French and English. Needs Key Quest Markers r20+ |
| WishFinder bridge for KatSmithy | r17 | READY_TO_DISTRIBUTE, release | Accepted on MHGU Recomp with KatSmithy of 2026-11-11 |
| WishFinder bridge for My Weapon Tree | r8 | READY_TO_DISTRIBUTE, release | Accepted on Eden with My Weapon Tree 0.60 |
| World Sharpness Gauge | r70 | READY_TO_DISTRIBUTE, release | MHGU Recomp; r68 on Eden and Ryubing |
| HD Project, wiki cheats, DTI dumper support | — | LOCAL_ONLY | — |

Ryujinx and Switch hardware are unconfirmed for every mod unless its
`EVIDENCE.json` says otherwise. An open device report remains: Damage Numbers
placement on real Switch and Android handheld (reported against r28, no hashes
supplied).

## Last gameplay-accepted builds

The rollback for a current build that has no run of its own.

| Mod | Build | Where |
| --- | --- | --- |
| Damage Numbers | r42 (r38 on Eden) | `build/damage-numbers/candidates/r42/`, `r38-accepted/` |
| Key Quest Markers | r20 | `build/key-quest-markers/candidates/r20/` |
| Lock-on Target | r2 | `build/lock-on-target/candidates/r2/` |
| Modern Weapon Controls | r14 | `build/modern-weapon-controls/candidates/r14/` |
| Multiplayer Roaming | r15 | `build/online-roaming/candidates/r15/` |
| Please do Better | r37 (r31 on Eden, r30 on Ryubing) | `build/please-do-better/candidates/r37/`, `r31/`, `r30/` |
| Purple-lib | r17 (release ZIP) | `build/purple-lib/candidates/r17/`, `r16/` |
| Purple-lib Tester | r10 | `build/purple-lib-tester/candidates/r10/` |
| Shared Urgent Quests | r2 | `build/shared-urgent-quests/candidates/r2/` |
| Village Quests in Hub | r6 | `build/village-quests-in-hub/candidates/r6/` |
| WishFinder | r68 (accepted) | `build/wishfinder/candidates/r68/` |
| WishFinder bridge for KatSmithy | r17 | `build/wishfinder-katsmithy-bridge/candidates/r17/` |
| WishFinder bridge for My Weapon Tree | r8 | `build/wishfinder-mwt-bridge/candidates/r8/` |
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
