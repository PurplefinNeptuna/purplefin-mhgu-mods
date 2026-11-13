# Quest groups, completion, and progression

## Resource research versus runtime input

`common.arc` is a container used to study quest-group resources, names, and counter layouts. Several base/localized/HD archives can share that basename. Identify the exact path/hash and internal entry. Packed QSG resource records are seven bytes; the loaded runtime group record is twelve bytes. Never cast one layout into the other.

Current Key Quest Markers reads loaded `sQuest`/group and quest objects. It ships no replacement common archive or copied classification table. Its copied English HD resource is a build-time fixture, not a runtime requirement. Earlier fixed-key/prefix implementations and their counts are historical baselines, not the current progression policy.

## Native structures and queries

All addresses below are main-relative on verified Switch 1.4.0.

| Address / field | Meaning |
| --- | --- |
| sQuest +0xb4 | Loaded group-resource pointer |
| Resource +0x64 / +0x6c | Count / record-array pointer |
| Record stride 12 | Quest ID+4, category byte+8, alternative byte+9 |
| cQuestData +0x10c bit 0 | Historical rank-up urgent identity |
| `0x523da4`, sUserInfo +0x42c | Actual group-index completion reader/bitfield |
| `0x523d00`, sUserInfo +0x100 | New/acknowledgement state, separate from completion |
| Cell `0x18979f0` | Separate progression-record pointer |
| Progression +0x3e0 / +0x3e2 | u16 Village / Hub-G tiers |
| `0x3d17f8` | Script stage queries: Village 1..10, Hub/G 1..13 |
| `0x3b1a18` | Village prerequisite counter; bit 0 means requirements satisfied |
| `0x3b1d70` | Hub/G total/completed prerequisite counter |
| `0x3b2174` | Scene/quest-flag availability query |
| `0x54af8c` | Full native counter availability predicate |

The adapter bounds the group count to 1..4096, verifies aligned readable storage, and rechecks pointer/count identity during the synchronous callback. Identical duplicate records can retain native completion positions; conflicting duplicates invalidate classification. Resolve a valid group before calling the completion reader, whose fallback can otherwise select index zero.

## Keys

Key categories are 1..17 and 19..22. Village categories 1..10 compare with Village tier. Hub/G categories 11..22 compare with Hub/G tier+10. Category 18 is a key-free transition; 23 is final/no-key. A star page currently displayed is not the player's current progression.

An unfinished key is needed only at its actual progression tier. Completed keys, old unfinished keys, and satisfied Village alternatives are Grey. For Village alternative bytes 1..11, another completed record with the same category/alternative satisfies the shared requirement. Other domains do not inherit that rule by analogy.

The core classification policy needs only the quest's own progression tier. The current native adapter additionally requires both tier fields readable and rejects the update when Village>10 or Hub/G>13. Zero can pass that global check, but is unknown to the core's relevant-domain test and hides an unfinished key. Viewing/marking a row does not complete a quest, write progression, change unlocks, or modify saves.

## Rank-up urgents

Categories 24..46 require the native urgent flag. Current active urgent status also requires actual availability, native prerequisites, and membership in the counter's offered set. Completion makes the badge Grey. An unavailable/old unfinished urgent also displays Grey; unresolved evidence hides it.

Parent controller `0x54d030` passes QuestInfoList with at most sixteen offered IDs at +0x1104, count +0x1144, and UI identity from controller+0x54. Native construction `0x781e60` fills/clears those IDs and count together after availability/completion filtering. It corresponds to parent-state +0x1140/count +0x1180 because the info base is parent+0x3c.

Copy only IDs/UI into a stack/TLS scope used by nested row builder `0x616cb0`. A selector's unfinished pool, a static rank range, the separate+0x200 UI bitfield, or one scene flag cannot substitute for that offered set. Evaluate simultaneous offered IDs independently, including phases involving quest 601 and 1005.

## Special Village encounters

Categories 47..54 represent four first-run/repeat encounter families even when cQuestData's rank-up urgent bit is clear:

| Family | Quest IDs / categories |
| --- | --- |
| 1 | 308/47 and 309/48 |
| 2 | 319/49 and 320/50 |
| 3 | 324/51 and 325/52 |
| 4 | 329/53 and 330/54 |

Family getter `0x3b21f0` uses table `0x162a8a0`; initial words 1, 1, 2, 2, 3, 3, 4, 4 establish pairing. Predicate `0x3b2214` distinguishes repeat categories. These eight IDs occupy entries 0..7 in the 51-entry enabled-bit table at `0x162cde4`, stride 8, whose flags live at owner +0x35d4.

Use the full three-argument availability predicate with `(id,0xff,0)` as audited. Scene availability alone misses the first-run/repeat enabled bits. Completion of either record satisfies the family. Available unfinished unsatisfied pairs can be active urgent without rank-up offered/prerequisite conditions. Limit this policy to 47..54; do not extend a similar-looking family table to other categories.

The adapter still requires valid parent offer context and native metadata. r17 retains the special encounter semantics from r13, accepted geometry, and current Green/Red/Grey palette. Earlier yellow/purple narratives describe superseded colours.

## Where the quest list comes from

Bytes unless marked upstream (MHGURecomp's source; its addresses are these plus `0x200000`). Source: `mods/village-quests-in-hub/DEVELOPMENT.md` Findings.

| Step | Where | Facts |
| --- | --- | --- |
| Area type | Session cell `0x188ca48` (through GOT word `0x1838bb4`), byte +0x4c | 0 Hub, 1..6 villages, 7 Pub (upstream). A quest writes 255 there (`0x6be048`, old value kept at +0x50); `0x6be09c` restores it |
| List job | Start `0x3b7fd8`, thread `0x3b7cf8`, loop `0x3b7de8`, finished `0x3b8070` | Frees and reallocates the 3456-byte list at +0x24, reads the area byte once. +0x28 count, +0x2c cursor, +0x30 state (0 load, 1 wait, 2 finished); at most 32 unready, 864 total. Starting a job destroys a running one's thread object |
| Filter | `0x3b8090(list, quest, type)`, one caller `0x3b7ea8` | Decides whether a quest is listed for the area type (`cmp r2,#7`) |
| Quest file | `loc\quest\questData\questData_%07d` (`0x1563ab7`), DTI `rQuestData` cell `0x188ab98` | Loaded through `sResource::create(this, dti, path, mode)` (vtable +0x30, `0xbcad18`): mode bit 0 blocking, bit 1 async. A cached hit raises the count at +0x48 |
| Lookup | `0x3ba50c(selector, quest)`, 19 callers | Skips an entry until its +0x50 bit 0 is set (loaded), then compares record +8 |
| Selector | Cell `0x188ae38` | Holds the lists, urgent pools and Special Permit groups below |
| Categories | Build `0x3b85d8`, fill `0x3bb318`, get `0x3bc96c` (reads area byte +0x4c, range 0..7), rebuild `0x3ba8fc` | Quest lists per category; pool index for an urgent depends only on quest-ID ranges (`0x3bc5f0`), so host and client agree |

Availability `0x54af8c(id, 0xff, 0)` returns 1 for DLC IDs (`0x3b9870`). For other quests it asks the progression script `0x3b2174`, whose module is at +0x8d0 of the cell behind it: with the module unloaded it answers 0 unless its +0x8dc cache holds the flag. So the result depends on when it is asked. `aResult` slot 7 `0x6a1fd4` loads the module and slot 9 `0x8e48` unloads it. `aVillage` loads it at `0x10618` and unloads it at `0x106a0`. An area load's list job can run while the module is still unloaded (inference from the stage's slot order; no run has logged it). It also needs the special encounter bits (above). It reads the local save, never the host's.

## Counter pages and their rows

`uUIQuestCounter` (vtable `0x177e2d4`: update slot 9 `0x781e34`, draw slot 18 `0x781bb0`; list draw `0x782af8`). State byte +0x3c, dispatcher `0x781e60`; state 0 re-runs rows (`0x783074`), plays sound 121 and moves to state 1. Page: 1 rank, 2..4 star (5 list, upstream). Native writes are `strh`, so +0x3d clears with it. `info` is counter +0x3c. Source: `mods/wishfinder/DEVELOPMENT.md` section Rank and star rows, and `work/wishfinder/COUNTER_PAGES.md`.

| Row kind | Data |
| --- | --- |
| Rank rows (five) | Label `info+0x1171+i` (0 Low, 1 High, 2 G Rank, 3 Special Permit, 4 Training, 5 Hunt of the Day, 6 hidden), flag `info+0x116c+i` (0 locked). Confirm `0x7838c0` sets star code `info+0x59`: Low 0 in a village, 1 at hub and pub (`0x508924(_, 2)`); High 2 or 3; G 4. Special Permit goes to page 17, Training 14, Hunt of the Day 19 (list 23) |
| Star codes | `{s8 first, s8 last, special, special}` at `0x162cdc5 + 4 * code`: 0 village 1..6, 1 hub low 1..3, 2 village 7..10, 3 hub high 4..7, 4 G 1..4; special 16 (urgent) everywhere, 15 (Event) at the hub. `0x78484c(counter, code, u8 rows[8])` writes the slots shown, stopping at a locked star or one with no available quest |
| Star rows | Bytes `info+0x61..0x68` (255 empty). Slot 0..13 is quest list `0x1650a2f[slot]`, listed by `0x3bc96c(selector, list)`, count `0x3bc9f8`, kept when `0x54af8c` is 1 |
| Urgent row (16) | Pool `[0, 2, 1, 3, 4][code]` (`0x1650aa0`): 16 IDs at `selector + 104 + 64 * pool`, count u16 at `selector + 424 + 2 * pool`; shown when available and not cleared (`0x523da4([0x1897f78] + 0x42c, quest)` is 0) |
| Event row (15) | See *Downloaded event quests* |
| Special Permit | 18 groups of up to 16 IDs at `0x3bc9e0(selector, i)` (`[selector + 0x1b4] + 64 * i`), counts u16 at `selector + 440 + 2 * i`, kept by `0x54af8c` |

Rank and star pages draw their rows with `counter.gui` animation 1 (see [Native GUI](native-gui.md#known-screens-and-trees)).

## Downloaded event quests

The game lists event quests (lists 15..17) only while their row is open: `0x54dcac` starts a save job (`0x3dfa2c`), then `0x3bc234(selector, code)` lists the job's set at `[[0x188ad90] + 0xb4]`. That set is empty at any other time, so a plugin cannot read it from memory to see every event quest.

They live in the game's save file `system`. Header word 0x30 gives a shared section (`0xb281`), whose +0x4618 starts 200 slots of 0x1c00 bytes, each `{u32 quest, u32 size, ARC}`. A tester's save had 165 used, 46 of them G rank, and the game lists those 46. Offset and slot count were read from saves, not from code, so count a slot only when it holds the ARC magic and an event ID. Listing rule (`0x3bc234`): millions digit 1, ten-thousands digit not 2, and `(id / 100) % 100` is 0, 1 or 10 for star codes 1, 3, 4. Reading the save read-only from a plugin: [Game files at runtime](../../mhgu-forge-modding/references/game-files-at-runtime.md). Source: `mods/wishfinder/core/src/quests.rs` (`event_slot`, `event_on`), `src/config.rs` `read_event_quests`.

## Recording a clear online

Result routine `0x384af0` calls `0x388d40`, which writes completion with `0x523f30(sUserInfo+0x42c, sQuest+0xe0, 1)` (setter twin of `0x523da4`) unless the client gate at `0x388d8c..0x388ddc` returns first: `if (!A) { if (B) return; if (C) return; if (D) return; }`.

| Gate | Address | Meaning |
| --- | --- | --- |
| A | `0x3ae3b4` | Host or offline: net mode `0xbf0ba8() != 1`, else session bytes +0xd788 == +0xd789 |
| B | `0x3ae75c` | Rank-up urgent: sQuest+0xb8 bit 12, set by `sQuest::initQuest` `0x3abc00` from cQuestData `mFlag` bit 0. One caller (`0x388da4`) |
| C | `0x3ae768` | sQuest+0xb8 bit 19: the 4MMNN family (MM 1..18, NN 1..16) from `0x3b5bb4(id)`, unnamed |
| D | `0x3a3424` | Request quest: `mRequestVillage` in {5, 6, 7, 8, 12} and `0x54af8c(id, 0xff, 0) != 1` |

So an online joiner never records a rank-up urgent's clear. Source: `mods/shared-urgent-quests/DEVELOPMENT.md`.

## Investigate a new quest discrepancy

Record quest ID, loaded group/category/alternative, real completion, progression domain/tier, urgent flag, offered-set membership, full availability, and prerequisite result. Compare native counter construction and resource records before changing a static list. Keep resource research counts tied to the particular archive, not a universal quest total. Saved screenshots/names alone cannot distinguish first-run/repeat state.

Sources: `mods/key-quest-markers/core/src/lib.rs`, `src/{native.rs,offers.rs,gui.rs}`, `DEVELOPMENT.md` native classification/special urgents, ARM adapter tests, `EVIDENCE.json`; saved Ghidra/DTI and copied resources. Runtime base-game and optional-HD acceptance is dated 2026-10-15 on Eden/Linux; individual quest-state coverage is not exhaustive.
