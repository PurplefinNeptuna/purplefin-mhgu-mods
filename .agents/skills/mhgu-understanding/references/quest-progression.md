# Quest groups, completion and progression

## Resource research versus runtime input

`common.arc` is a container used to study quest-group resources, names, and counter layouts. Several base/localized/HD archives can share that basename. Identify the exact path/hash and internal entry. Packed QSG resource records are seven bytes; the loaded runtime group record is twelve bytes. Never cast one layout into the other.

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
| `0x3d17f8` | Common-script VM; its stage queries expose Village 1..10, Hub/G 1..13 |
| `0x3b1a18` | Village prerequisite counter; bit 0 means requirements satisfied |
| `0x3b1d70` | Hub/G total/completed prerequisite counter |
| `0x3b2174` | Scene/quest-flag availability query |
| `0x54af8c` | Full native counter availability predicate |

Identical duplicate records can retain native completion positions; conflicting duplicates invalidate classification. Resolve a valid group before calling the completion reader, whose fallback can otherwise select index zero.

## Keys

Key categories are 1..17 and 19..22. Village categories 1..10 compare with Village tier. Hub/G categories 11..22 compare with Hub/G tier+10. Category 18 is a key-free transition; 23 is final/no-key. A star page currently displayed is not the player's current progression.

An unfinished key is needed only at its actual progression tier. Completed keys, old unfinished keys, and satisfied Village alternatives are Grey. For Village alternative bytes 1..11, another completed record with the same category/alternative satisfies the shared requirement. Other domains do not inherit that rule by analogy.

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

## Recording a clear online

Result routine `0x384af0` calls `0x388d40`, which writes completion with `0x523f30(sUserInfo+0x42c, sQuest+0xe0, 1)` (setter twin of `0x523da4`) unless the client gate at `0x388d8c..0x388ddc` returns first: `if (!A) { if (B) return; if (C) return; if (D) return; }`.

| Gate | Address | Meaning |
| --- | --- | --- |
| A | `0x3ae3b4` | Host or offline: net mode `0xbf0ba8() != 1`, else session bytes +0xd788 == +0xd789. The joiner side is supported by a user run; the host side is inference |
| B | `0x3ae75c` | Rank-up urgent: sQuest+0xb8 bit 12, set by `sQuest::initQuest` `0x3abc00` from cQuestData `mFlag` bit 0. One caller (`0x388da4`) |
| C | `0x3ae768` | sQuest+0xb8 bit 19: the 4MMNN family (MM 1..18, NN 1..16) from `0x3b5bb4(id)`, unnamed |
| D | `0x3a3424` | Request quest: `mRequestVillage` in {5, 6, 7, 8, 12} and `0x54af8c(id, 0xff, 0) != 1` |

The write is at `0x388e40`. Other completion writers: script opcodes 0x33/0x34 in `0x3d17f8`, one fixed quest 0x41d in `0x50d494`, a bulk block in `0x521d4c`. After the write the native follow-up is `0x5106f8` (stores +0x3d4 when newly cleared), `0x50cbd0(…, sUserInfo)`, `0xb91be0`; whether HR-up and unlocks follow from that alone is unknown (`work/urgent-share/FINDINGS.md`). `0x388d40` is called unconditionally from `0x384af0` (+0x49c), and the gate window is `0x388d70..0x388ddc`. The host-only branch in `0x3afd54` uses the same host test (+0xd56/+0xd57). So an online joiner never records a rank-up urgent's clear.

## Investigate a new quest discrepancy

Record quest ID, loaded group/category/alternative, real completion, progression domain/tier, urgent flag, offered-set membership, full availability, and prerequisite result. Compare native counter construction and resource records before changing a static list. Keep resource research counts tied to the particular archive, not a universal quest total. Saved screenshots/names alone cannot distinguish first-run/repeat state.
