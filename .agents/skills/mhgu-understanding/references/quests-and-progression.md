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

## Investigate a new quest discrepancy

Record quest ID, loaded group/category/alternative, real completion, progression domain/tier, urgent flag, offered-set membership, full availability, and prerequisite result. Compare native counter construction and resource records before changing a static list. Keep resource research counts tied to the particular archive, not a universal quest total. Saved screenshots/names alone cannot distinguish first-run/repeat state.

Sources: `mods/key-quest-markers/core/src/lib.rs`, `src/{native.rs,offers.rs,gui.rs}`, `DEVELOPMENT.md` native classification/special urgents, ARM adapter tests, `EVIDENCE.json`; saved Ghidra/DTI and copied resources. Runtime base-game and optional-HD acceptance is dated 2026-10-15 on Eden/Linux; individual quest-state coverage is not exhaustive.
