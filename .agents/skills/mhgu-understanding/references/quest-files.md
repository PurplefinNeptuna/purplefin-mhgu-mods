# What a quest gives: rewards, carves, gathering, fishing

Use this to answer "where can the player get item X" from the game's own files.
Everything here was read by WishFinder's quest table builder over the 1.4.0
RomFS (1,854 quest files) and over Definitive Edition 2.0.0 (1,893), and the
builder reproduces the checked-in `quests.bin` byte for byte. Paths are
relative to `nativeNX/`. ARC and other container layouts are in
[Resources and tooling](resources-and-tooling.md#formats-a-plugin-reads).
Deeper notes: `mods/wishfinder/DEVELOPMENT.md` section Quest table, and
`work/wishfinder/{BREAKS_CAPTURES,MATERIAL_ORIGINS,SECRET_AREAS,DEFINITIVE_EDITION}.md`.

## Files and records

| Data | Location | Layout |
| --- | --- | --- |
| Quest | `loc/arc/quest/qNNNNNNN.arc`, type `1bbfd18e` | Packed mib. Its monster stride is 13 bytes; DTI's 14 is the runtime object |
| Reward names | Same ARC, type `00e0bb1c` | 15 slots of {u32 hash, char[16]} after 8 bytes: b1..b5 boss sets (`quest\boss\setEmMain\`, not rewards), z1..z3, rem1, rem2, add1, add2, sub, supp, plus |
| Rewards | Type `5b3c302d` | 8 {flag, count}, then 40 {u16 item, u8 amount, u8 weight}; each frame ends with weight 255 past its count |
| Large monster carves | `arc/enemy/emNNN_VV.arc`, type `33a84e14` (`rHagi`) | 26-byte head, 80 {rate, count, u16 item}. Quest monster ID = `VV << 8 | NNN` |
| Small monsters | Quest ARC type `32ca92f8` (`esl\0`) | 14 u32 offsets at 8; each `ESD\0` with u16 count at +8 and 36-byte records from +10, u16 ID first: high byte 0x10, low byte NNN of `arc/enemy/emsNNN_00.arc` |
| Gathering | `loc/arc/stage/map_com/mNN.arc`, type `25fd693f` | `IPL\0`; {count1, size1} at 0x10, {count2, size2} at 0x1c; (offset, count) tables at 0x24 and 0x24+size1, offsets relative to their table; entries {rate, count, u16 item} |
| Gathering areas | Same map ARC, `stage\mNNd\mNNd` (`_easy`, `_tuto`), type `52776ab1` | `IPS\0`, see *Gathering areas* |
| Fishing | `loc/arc/quest.arc` `quest/fishData`, type `3e0e02fc` | 625 records of 24 bytes: map, area, kind, level, 20 u8 rates |
| Captures and breaks | `loc/arc/result.arc` `quest\bui\bui_s0..4`, type `0x0ab54515` (`rBui`) | f32 2.0, u32 count, then 462-byte records (below) |

Which file a quest uses by rank:

- `bui_sN` by `cQuestData::mHagiLv` is the game's own lookup (`0x3a3874`).
- `hagi_sN` by `mHagiLv` (1 low, 2 high, 4 G, 3 arena) is inference from a census fit and the names; its reader is unread.
- The gathering file by `mPickLv` is the game's: 0 easy, 1 low, 2 high, 3 tuto, 4..6 clct1..3, 9 g.
- The fish level matching `mFishingLv` is inference by the same census. Fish rate index i is item `main+0x162a7b0`[i], 20 u16s: 362..366, 375 (Wanchovy), 367..374, 2064..2068 (Goldenfish, Silverfish, Brocadefish, King Brocadefish, Premium Sashimi), 382 (Guardfish). Its reader is unread; the table matches Kiranico's per-area rates for Whetfish, Popfish, Gastronome Tuna, Ancient Fish, Small Goldenfish and Guardfish, which 362+i does not.

## Carves, drops and shed items

`rHagi` data at +0x68 is `cHagi_PopListData`: vft, u8 `mIndexTable[22]` at +4, 80 {rate, num, u16 item} at +0x1a. A slot's list starts at `mIndexTable[slot]` (255: none) and runs to rate 255. Walking the slots gives each file's items exactly as the 80 entries do (650 of 650 files).

| Reader | Slot | Meaning |
| --- | --- | --- |
| `0xaba9c` | 1, 4 or 7 for carve point type 0, 1, 2, plus the Hyper shift (`0xa25970`) | Body, tail, another severed part (only Bloodbath Diablos, Barroth, Crystalbeard Uragaan). Point record `[monster+0x75f0]+0x6c + n*12`, type at byte 0 |
| `0xac0ec` | 10 + v | Dropped (shift applied twice for 0x44f Nightcloak Malfestio, none for 0x43c Redhelm Arzuros) |
| `0xabe08` | 16 + v | Shed in the fight (shift only for 0x439 Thunderlord Zinogre) |

Slot 0 has no reader.

## Captures and part breaks

- `0x3a3874(quest, emType)` takes the file by the s8 `mHagiLv` at `[quest+0xa4]+0x2c` through file-ID table `0x162a66c` (IDs `0xf05f..0xf063`), then the first record whose `mEmType` matches (`rBui::get` `0x399b5c`: `[+0x6c] + i * 468`, count +0x64).
- Record (reader `0x3559c0`): u16 `mEmType` (monster low byte, variant high byte), 18 interleaved {u8 `mHeadType`, u8 `mHeadItemNum`}, 106 {u8 rate, u8 num, u16 item}. 462 bytes in the file, 468 loaded; 94 records a file. A code's items start after every earlier pair's count + 1 (`0x354484`); the roll `0x3828e8` reads until rate 255.
- Codes (writer `0x3a6f54`; events at quest state `0x188ad90` +0x566, 60 of 6 bytes): capture is 10; a break of part 1..5 is 20..60 (table `0x162a736`). On a Hyper monster (variant 4) in a quest of `mHagiLv` 2 or 4 the code gains 0..2. Which body part a part number is differs per monster; no game data names it.
- Breaks are reported through the event wrapper `0x49964` (callers `0x99f98`, `0x9d458`, `0x9d4f4`); the trigger is compared with the body part the hit reports, a or b chosen by `0x3a8d68` (> 4 takes b); a part breaks once (bit mask `[monster+0x1428]+0x5cbe`). `dtbparts` (type `0x1bbc291e`, `DTP\0`) also holds the carve points (12-byte records) and drop-pop entries; its full layout is open (`work/wishfinder/MATERIAL_ORIGINS.md`). Carve picks by weight: `0x319358` / `0xce2358`.
- Part n comes from the monster's `dtbparts` (`rEnemyDtBaseParts`, object `monster+0x75f0`): 4-byte records {trigger, a, b, part | 0x80} at +0x64, count +0x8c.
- A record with sections but no code 10 is a monster that cannot be captured (elder dragons, Kirin, Lao-Shan, Yama Tsukami, Akantor, Ukanlos, Alatreon, Amatsu, Shagaru, Nakarkos, Valstrax, Ahtal-Ka).
- An intruder's captures count: neither capture appender (`0x3a6bc4`; `0x3a828c` in `0x3a7f40`) reads target or intruder, and the roll reads only the event. The break appender `0x49990` is unread, and no run has shown an intruder's break or capture.

## Intruders

After the five 13-byte monsters, the packed mib holds Zako 3, two EmSet records 10, BossRush 1 and five Appear records 25, then `mStrayRand`, `mStrayStartTime`, `mStrayStartRand`, `mStrayLimit_3..5` and `mStrayRand_3..5`. `0x3ab588` weights slots 3..5 by `mStrayRand_3..5`, and `0x3aca9c` lets one come when `rand % 100 < mStrayRand`. A slot counts as an intruder when `mStrayRand` and its own chance are nonzero and not both 100; slots 1 and 2 and other slots count as large monsters. The branch at `0x3aca50` through `0x3ab2b4(2, 1)` and the limits are unread.

## Gathering areas and the secret area

- **Start area.** `0x3ad988(sQuest, cQuestData)` picks it by map index `(mMapNo % 100) % 28` and `mStartType` (+17, mib byte 21): 1 a weighted pick from the map's list in table `0x1753b60`, 2 another list, else area 0 (camp). It sets `sQuest+0x5b mFlgStartSecret` when the map is in mask `0x14079fa` and the area is that map's column-1 entry, the secret area. Maps above 27 start at camp. Start lists in `0x1753b60` are 12 bytes per map, three pointers to {s8 weight, u8 area} lists ending at 255: type 1 takes column 0, or column 1 when `0x2864d4(*cell, 26)` is true for the main player (unread: a player state); type 2 takes column 2. On maps 11..14 and 22..24 a quest passing `0x14cbe8` and `0x3b9a18(quest number)` starts at camp (unread checks). Rank is not read; every real low-rank quest is type 0. No walking entrance to a secret area was found.
- **Rule.** An item whose every gathering point lies only in the secret area is gathered only on quests of start type 1. On 1.4.0, 900 quests lose such items and 434 keep them.
- **Files.** `0x31a404` takes the map number and `0x3a8ccc` (`mPickLv` 0..9, else 1). Pop list file ID `0xd5b7 + map * 10 + level`; pop set `0xd707 + map` (`mNNd_easy`) for level 0, `0xd6eb + map` (`mNNd_tuto`) for 3, `0xd6cf + map` (`mNNd`) otherwise.
- **`rItemPopSet`** (loader `0x319900`): head 0x34 bytes, area count at 8, sections at 0x34, 0x34 + word 7, 0x34 + word 10. Section 1 (`0x319a5c`, read at `0x31a5a0`): per area {offset, count} of 36-byte records, byte 0 a point of the first list. Section 2 (`0x319adc`): per area groups of 28-byte candidate positions. Section 3 (`0x319b28`, read at `0x31ad2c`): per area groups of 6-byte {weight, point of the second list, ...}, rolled by weight, so weight 0 never comes out. At most 13 areas, so a u16 mask covers them.
- **Fishing spots** are points of kind 10 or 11 in `rStageAreaInfo` (type `0x065375d5`; points from +0x1c, 28 bytes, kind at +16). 24 of the fish table's 25 map-area pairs hold one; map 12 area 2 is the exception.

## MHGU Definitive Edition 2.0.0

Its quests name a game boss that it swaps for its own monster at spawn (Kushala 0x18 for Gogmazios 0x59, Zinogre 0x39 for Stygian Zinogre 0x139, Gendrome 0xf for Dalamadur's tail ...). Three run on a map of its own: Fortress (26) loads `m28`, Sanctuary (18) `m29`, Ruined Pinnacle (24) `m30`, whose files keep the game stage's internal names. Its 39 quests are listed in its `allocations.toml`; a file-only test (a clear target no boss record spawns) gets 37 and picks wrong stand-ins in two, so use the list. Its captures and breaks are `mhgu_de/*.bin` (`MH4P`), served by its hook on `0x3a3874`. It ships no `result.arc`, and its rItemData has 3055 records (1.4.0: 2991). Details: `mods/wishfinder/DEVELOPMENT.md` *Definitive Edition's stand-in quests*.

Sources: `mods/wishfinder/{DEVELOPMENT.md,core/src/quest_build.rs,core/src/quests.rs,core/src/definitive_edition.rs}`, `mods/wishfinder/scripts/generate_quests.py`, `work/wishfinder/` notes above.
