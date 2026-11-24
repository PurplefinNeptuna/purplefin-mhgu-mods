# Local state

Baseline: stock Switch Forge 2.0.0 and forge-rs 2.0.0 (every mod still builds on 1.5.1 and 1.5.0), branch `main`. MHGURecomp
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
| Key Quest Markers | r23 | READY_TO_DISTRIBUTE, release | Eden and MHGU Recomp, unitemized |
| Lock-on Target | r5 | DEVELOPMENT, candidate | Not run (r4 did nothing on MHGU Recomp); r2 accepted on Eden and MHGU Recomp |
| Modern Weapon Controls | r15 | READY_TO_DISTRIBUTE, release | Loads on MHGU Recomp; controls accepted on r14 (Eden) |
| Multiplayer Roaming (`online-roaming`) | r16 | READY_TO_DISTRIBUTE, release | Multiplayer, user report; Eden and MHGU Recomp installed |
| Please do Better | r37 | READY_TO_DISTRIBUTE, release | MHGU Recomp with Purple-lib r17 (r36 registers on Eden too) |
| Purple-lib | r22 | READY_TO_DISTRIBUTE, release | Eden and MHGU Recomp 0.17 (input hold with game actions) |
| Purple-lib Tester | r14 | DEVELOPMENT, not for distribution | Not run (8 extra sets); r13 on MHGU Recomp with Purple-lib r20 |
| Shared Urgent Quests | r2 | READY_TO_DISTRIBUTE, release | Eden joiner, no joiner log |
| Skin Loader | r18 | READY_TO_DISTRIBUTE, release, with a `-fast` package | MHGU Recomp (full); r16 on Eden too; fast not run since r14 |
| Village Quests in Hub | r6 | READY_TO_DISTRIBUTE, release | Accepted on Eden beside MHGU Definitive Edition 2.0.0; inactive beside 3.0.0 |
| WishFinder (was Wishlist) | r143 | DEVELOPMENT, candidate | Not run; r135 the release; r134 accepted on Eden with MHGU Definitive Edition 3.0.0. Needs Key Quest Markers r20+ |
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
| Key Quest Markers | r23 (r20 before it) | `build/key-quest-markers/releases/r23/`, `candidates/r23/`, `r20/` |
| Lock-on Target | r2 | `build/lock-on-target/candidates/r2/` |
| Modern Weapon Controls | r14 | `build/modern-weapon-controls/candidates/r14/` |
| Multiplayer Roaming | r16 | `build/online-roaming/candidates/r16/` |
| Please do Better | r37 (r31 on Eden, r30 on Ryubing) | `build/please-do-better/candidates/r37/`, `r31/`, `r30/` |
| Purple-lib | r22 | `build/purple-lib/candidates/r22/`, `r21/`, `r20/`, `r19/`, `r18/`, `r17/`, `r16/` |
| Purple-lib Tester | r11 | `build/purple-lib-tester/candidates/r11/` |
| Shared Urgent Quests | r2 | `build/shared-urgent-quests/candidates/r2/` |
| Skin Loader | r18 (r16 before it) | `build/skin-loader/releases/r18/`, `candidates/r18/`, `r16/` |
| Village Quests in Hub | r6 | `build/village-quests-in-hub/candidates/r6/` |
| WishFinder | r134 | `build/wishfinder/candidates/r134/`, `r131/`, `r127/`, `r122/`, `r119/`, `r114/`, `r111/`, `r107/`, `r105/`, `r103/`, `r102/`, `r92/`, `r86/`, `r85/`, `r82/`, `r76/`, `r72/` |
| WishFinder bridge for My Weapon Tree | r11 | `build/wishfinder-mwt-bridge/candidates/r11/`, `r10/` |
| World Sharpness Gauge | r70 (r68 on Eden and Ryubing) | `build/world-sharpness-gauge/candidates/r70/`, `r68/` |

Older accepted C++ builds: `build/modern-weapon-controls/candidates/r10/`,
`build/please-do-better/candidates/r23/` and `r17-config1/`.

## Inputs and runtime paths

Emulator, RomFS and library paths are in the root AGENTS.md, "Runtime evidence
and installation paths". This table holds the rest.

| Purpose | Path |
| --- | --- |
| Sealed base game (v0) | `/mnt/storage2/ROM/Switch/Game/`, the XCI with title ID `0100770008DD8000` and `[v0]` |
| Sealed 1.4.0 update (v262144) | `/mnt/storage2/ROM/Switch/Update+DLC/`, the NSP with title ID `0100770008DD8800` and `[v262144]` |
| Keys for the XCI/NSP | `/mnt/storage2/ROM/Switch/keys+firmware/` |
| Copied native inputs (1.4.0 code; its `forge` is Forge 2.0.0's `subsdk9`) | `work/shared/game-exefs/` |
| Build inputs for mods on Forge 1.5.1 (`main`, `sdk`, `forge` as each `dependencies.lock.json` pins; each mod's `build.local.json` `inputs` points here or at its own `work/NAME/inputs/`) | `work/shared/forge-1.5.1/inputs/` |
| Official Forge packages | `work/shared/forge-2.0.0/`, `work/shared/forge-1.5.1/` (what the mods build on) |
| Ghidra and saved DTI | `work/research-tooling/` |

Library target: game 1.4.0, cheat build FB08F1D20FD1204F, NSO
FB08F1D20FD1204FE7070672777F869B. Check the launched version before executable
work. HD resource priorities: [mods/hd-project/README.md](../mods/hd-project/README.md).
DTI extraction is not enabled for gameplay.

## Recovery

- `docs/COMPACTION.json` (the 2026-10-15 cleanup's hashes and removed paths) and `docs/WORKSPACE_EVIDENCE.json` (workspace tool and research receipts): Git history at `29a61af8` and earlier. Live pins they held are in `scripts/baselines.json`.
- `/mnt/storage2/Programs/MHGU_Modding-pre-rewrite.git`: history before the 2026-11-11 rewrite, with its tags (`cleanup/before-stock-forge-20261015`, `archive/backups-records-20261102` holding pre-prune `work/` notes and `backups-inventory.txt`).
- Run logs removed from the docs: Git history at `84e8410` and earlier.
