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
| cQuestData +0x10c bit 0 | Rank-up urgent flag (`mFlag` bit 0, loader `0x37539c` reads it as u16); matches group categories 24..46 (28 urgents among 1,302 records). Special encounters 47..54 have it clear (flags 0x300/0x308) |
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

Key Quest Markers also requires valid parent offer context and native metadata.

## Where the quest list comes from

Bytes unless marked upstream (MHGURecomp's source; its addresses are these plus `0x200000`). Source: `mods/village-quests-in-hub/DEVELOPMENT.md` Findings.

| Step | Where | Facts |
| --- | --- | --- |
| Area type | Session cell `0x188ca48` (through GOT word `0x1838bb4`), byte +0x4c | 0 Hub, 1..6 villages, 7 Pub (upstream). A quest writes 255 there (`0x6be048`, old value kept at +0x50); `0x6be09c` restores it |
| List job | Start `0x3b7fd8`, thread `0x3b7cf8`, loop `0x3b7de8`, finished `0x3b8070` | Frees and reallocates the 3456-byte list at +0x24, reads the area byte once. +0x28 count, +0x2c cursor, +0x30 state (0 load, 1 wait, 2 finished); at most 32 unready, 864 total. Starting a job destroys a running one's thread object |
| Filter | `0x3b8090(list, quest, type)`, one caller `0x3b7ea8` | Decides whether a quest is listed for the area type (`cmp r2,#7`) |
| Quest file | `loc\quest\questData\questData_%07d` (`0x1563ab7`), DTI `rQuestData` cell `0x188ab98` (GOT `0x183c984`), resource manager cell `0x2126a64` (GOT `0x1839450`), read in the job at `0x3b7e64`/`0x3b7e58` | Loaded through `sResource::create(this, dti, path, mode)` (vtable +0x30, `0xbcad18`): mode bit 0 `loadBlocking` `0xbcb0d0`, bit 1 `loadAsync` `0xbcb6bc`. A cached hit raises the count at +0x48. An async load is not ready when `create` returns |
| Lookup | `0x3ba50c(selector, quest)`, 19 callers | The scan at `0x3ba56c` skips an entry until its +0x50 bit 0 is set (loaded), then compares record +8 |
| Selector | Cell `0x188ae38` (GOT `0x1838d74`, caller `0xfdb8`) | Holds the lists, urgent pools and Special Permit groups below |
| Categories | Build `0x3b85d8`, fill `0x3bb318`, get `0x3bc96c` (reads area byte +0x4c, range 0..7), rebuild `0x3ba8fc` (caller `0x6bcafc`) | Quest lists per category; pool index for an urgent depends only on quest-ID ranges (`0x3bc5f0`), so host and client agree |

Availability `0x54af8c(id, 0xff, 0)` returns 1 for DLC IDs (`0x3b9870`). For other quests it asks the progression script `0x3b2174`, whose module is at +0x8d0 of the cell behind it: with the module null, `0x3d7ee4` writes answer 0 at `0x3d7ffc` unless its +0x8dc cache holds the flag. The special-encounter bit at owner +0x35d4 is saved by `0x51d94c`, and which record of a pair a save enables differs by save. So the result depends on when it is asked. `aResult` slot 7 `0x6a1fd4` loads the module and slot 9 `0x8e48` unloads it. `aVillage` loads it at `0x10618` (`0x506fec`) and unloads it at `0x106a0`. An area load's list job can run while the module is still unloaded: the job `0xfc1c` is the stage's loading method (slot 0x74, also called from `0xd8f0`) and `0x10548` a later slot (inference from that order; no run has logged it). It also needs the special encounter bits (above). It reads the local save, never the host's.

## Counter pages and their rows

Read from main (`work/wishfinder/COUNTER_PAGES.md`); marks built on these rules were accepted on Eden.

**Counter.** `uUIQuestCounter` (vtable `0x177e2d4`): update slot 9 `0x781e34` runs the state dispatcher `0x781e60`, then the list draw `0x782af8` for states 1..2; draw slot 18 `0x781bb0`. State byte +0x3c: 0 rebuild (`0x783074` re-runs the rows, plays sound 121, moves to state 1), 1 rank page, 2 star page, 5 quest list (meanings upstream). Native writes are `strh`, so +0x3d clears with it. The village counter is the same class; `0x6e3f64` belongs to `uUIArenaCounter` (vtable `0x177d7e4`). `info` is counter +0x3c.

**Row builders** (`cUIOQuestList`, vtable `0x1774b98`, holder +0x24, reached as `0x65cb3c(counter, 2)`). The list draw switches on the list's kind byte +0x3c (1..11): 5, 7, 11 quest rows (`0x54d030` -> `0x616cb0`); 1 rank rows `0x616164`; 2..4 star rows `0x616574` (after reading eight row bytes +0x9d..+0xa4: 255 empty; 13, 14, 16 special); 8 `0x6176d4`, 9 `0x617a7c`, 10 `0x617dd8`. Rank and star pages draw with `counter.gui` animation 1 ([Native GUI](native-gui.md#known-screens-and-trees)).

**Rank rows.** Five: label `info+0x1171+row` (0 Low, 1 High, 2 G Rank, 3 Special Permit, 4 Training, 5 Hunt of the Day, 6 hidden; a village shows `[4 0 1 5 6]`, the pub `[0 1 2 3 5]`), flag `info+0x116c+row` (0 locked: the confirm refuses it). The confirm `0x7838c0` maps a label to star code `info+0x59`: Low 0 in a village, 1 at hub and pub (`0x508924(_, 2)`); High 2 or 3; G 4; Special Permit goes to page 17, Training 14, Hunt of the Day 19 (list 23). The rebuild `0x783074` decides which rank rows light: at the hub it checks codes 3 (High) and 4 (G, when `0x5078e4` allows), elsewhere the village's code 2, each through the star-slot test `0x784964`, then the Special Permit groups and list 23. So a row the game lights has at least one available quest.

**Star codes.** `0x78484c(counter, code, u8 rows[8])` (pure apart from `rows`) writes the star page's normal rows from the s8 {min, max} pair at `0x162cdc5 + 4 * code`, max capped per code (0 -> 5, 1 -> 3, 2 -> 10, 3 -> 7, 4 -> 14), stopping at the first slot `0x784964` refuses, and returns the count. `0x784964` needs the slot's unlock bit and one quest of list `0x1650a2f[s]` (= s + 1) passing `0x54af8c(q, 0xff, 0)`.

| Code | Slots | Stars | Unlock bit in the save block +0x500 |
| --- | --- | --- | --- |
| 0 | 0..5 | Village 1..6 | Slot 0 always; `0x1650a70[s-1]` = 10, 15, 24, 28, 33 |
| 1 | 0..2 | Hub Low 1..3 | Slot 0 always; `104 + 4(s-1)` |
| 2 | 6..9 | Village 7..10 | `0x1650a70[s-1]` = 1008, 1025, 1035, 1052 |
| 3 | 3..6 | Hub High 4..7 | `104 + 4(s-1)` |
| 4 | 10..13 | G 1..4 | `0x159775c[s-10]` = 1400, 1405, 1409, 1413 |

**Star page** `0x783b48(counter, info, flag)`: rows `info+0x61..+0x68` (255 empty), count `info+0x60`; normal rows from `0x78484c(counter, info+0x59, rows)`, then two special rows from the byte table (GOT at `0x783bd8`) `[code * 4 + 2..3]`: 15 (Event, codes 1, 3, 4) and 14 written as is, 16 (urgent) only when the urgent pool `info+0x1104` (count `info+0x1144`, at most 16) holds an available, uncleared quest.

**Urgent pool** per code: index `[0, 2, 1, 3, 4][code]` (`0x1650aa0`), 16 IDs at `selector + 104 + 64 * i`, count u16 at `selector + 424 + 2 * i`; shown when available and not cleared (`0x523da4([0x1897f78] + 0x42c, quest)` is 0). **Special Permit**: 18 groups of up to 16 IDs at `0x3bc9e0(selector, i)` (`[selector + 0x1b4] + 64 * i`), counts u16 at `selector + 440 + 2 * i`, kept by `0x54af8c`.

**Which quests a page lists.** `0x54b994(ctrl, info, page, mode, first)` fills one page of eight quest rows (`page*8 .. page*8+7`) and returns how many quests passed; callers `0x54b834` (village `0x6e4554`, hub `0x782108`/`0x782268`) and the counter's step `0x54c130` (`0x54ca08`/`0x54ca30`). List number = row byte + 1, with remaps: 14 -> 20 + `info+0x1177`; 15 -> 15, 16 or 17 by rank code 1, 3 or 4 (the per-rank Event row); 16 -> the urgent pool (counts filled slots `info+0x1104..0x1140`); 19 -> 23. `mode == 1` picks from `0x121312 >> (8 * info+0x1176)` instead. The catalogue is the selector (its cell is loaded at `0x54bb78`): `0x3bc9f8(mgr, list)` is the count (u16 at `mgr + 0x38 + list*2`); `0x3bc96c(mgr, list)` (list < 24) gives a 396-byte record of 99 u32 quest IDs at `[mgr+0x34] + 396 * idx`, idx an s8 from a 24-byte row chosen by the area type (0..7); negative idx gives 0. A quest is kept only when available, the `0x54af8c(quest, category, info)` test: category 14 with `info+0x1177 == 1` needs `0x3bd150` to equal `info+0x11e6` (inference: Hunt of the Day group); `0x3b9870` passes event/DLC IDs (millions digit 1); otherwise `0x3b2174(quest)` -> `0x3d7e90(mgr, &out, quest)`, the progression query (cached per quest at +0x8e0, count +0x8dc, top bit the answer), must be 1; then a special encounter entry's enable bit decides. This is what hides a 4-star quest whose chain hasn't started.

## Downloaded event quests

The game lists event quests (lists 15..17) only while their row is open: `0x54dcac` starts a save job (`0x3dfa2c`), then `0x3bc234(selector, code)` lists the job's set at `[[0x188ad90] + 0xb4]`. That set is empty at any other time, so a plugin cannot read it from memory to see every event quest.

They live in the game's save file `system`. Header word 0x30 gives a shared section (`0xb281`), whose +0x4618 starts 200 slots of 0x1c00 bytes, each `{u32 quest, u32 size, ARC}`. A tester's save had 165 used, 46 of them G rank, and the game lists those 46. The rest of `system`: three hunter sections of 0x11f8c4 bytes at 0x18cc78, 0x2ac53c, 0x3cbe00; end word 0x1c = 0x4eb898. No code constant was found for 0x4618 or 0xf899 (movw search). Offset and slot count were read from saves, not from code, so count a slot only when it holds the ARC magic and an event ID. Listing rule (`0x3bc234`): millions digit 1, ten-thousands digit not 2, and `(id / 100) % 100` is 0, 1 or 10 for star codes 1, 3, 4. Reading the save read-only from a plugin: [Game files at runtime](../../mhgu-forge-modding/references/game-files-at-runtime.md). Source: `mods/wishfinder/core/src/quests.rs` (`event_slot`, `event_on`), `src/config.rs` `read_event_quests`.

## Recording a clear online

Result routine `0x384af0` calls `0x388d40`, which writes completion with `0x523f30(sUserInfo+0x42c, sQuest+0xe0, 1)` (setter twin of `0x523da4`) unless the client gate at `0x388d8c..0x388ddc` returns first: `if (!A) { if (B) return; if (C) return; if (D) return; }`.

| Gate | Address | Meaning |
| --- | --- | --- |
| A | `0x3ae3b4` | Host or offline: net mode `0xbf0ba8() != 1`, else session bytes +0xd788 == +0xd789. The joiner side is supported by a user run; the host side is inference |
| B | `0x3ae75c` | Rank-up urgent: sQuest+0xb8 bit 12, set by `sQuest::initQuest` `0x3abc00` from cQuestData `mFlag` bit 0. One caller (`0x388da4`) |
| C | `0x3ae768` | sQuest+0xb8 bit 19: the 4MMNN family (MM 1..18, NN 1..16) from `0x3b5bb4(id)`, unnamed |
| D | `0x3a3424` | Request quest: `mRequestVillage` in {5, 6, 7, 8, 12} and `0x54af8c(id, 0xff, 0) != 1` |

The write is at `0x388e40`. Other completion writers: script opcodes 0x33/0x34 in `0x3d17f8`, one fixed quest 0x41d in `0x50d494`, a bulk block in `0x521d4c`. After the write the native follow-up is `0x5106f8` (stores +0x3d4 when newly cleared), `0x50cbd0(…, sUserInfo)`, `0xb91be0`; whether HR-up and unlocks follow from that alone is unknown (`work/urgent-share/FINDINGS.md`). `0x388d40` is called unconditionally from `0x384af0` (+0x49c), and the gate window is `0x388d70..0x388ddc`. The host-only branch in `0x3afd54` uses the same host test (+0xd56/+0xd57). So an online joiner never records a rank-up urgent's clear. Source: `mods/shared-urgent-quests/DEVELOPMENT.md`.

## Investigate a new quest discrepancy

Record quest ID, loaded group/category/alternative, real completion, progression domain/tier, urgent flag, offered-set membership, full availability, and prerequisite result. Compare native counter construction and resource records before changing a static list. Keep resource research counts tied to the particular archive, not a universal quest total. Saved screenshots/names alone cannot distinguish first-run/repeat state.

Sources: `mods/key-quest-markers/core/src/lib.rs`, `src/{native.rs,offers.rs,gui.rs}`, `DEVELOPMENT.md` native classification/special urgents, ARM adapter tests, `EVIDENCE.json`; saved Ghidra/DTI and copied resources. Runtime base-game and optional-HD acceptance is dated 2026-10-15 on Eden/Linux; individual quest-state coverage is not exhaustive.
