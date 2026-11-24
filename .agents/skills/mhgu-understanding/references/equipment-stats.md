# Equipment stats, decorations, skills and armor names

## Equipment stats, decorations and skills

Bytes: the game's detail-panel getters and table objects, with RomFS cross-checks.

- Equipment, through the game's own detail-panel getters on a `cFestaEquip`. They read only the record's +4 (type in
  bits 0..4, level counted from 0 in bits 5..9) and +6 (number), plus +8 by `0xdb09c` (a variant number, 0 = use +6),
  and none calls a virtual on the record, so a zeroed 44-byte buffer with +4 and +6 set is enough (constructor
  `0xdaba4` and `reset` `0xdac14` exist if a full object is ever needed). Each looks the item up through `sEquip`
  (`0x13f03c` -> `0x13c208`, cell `0x1856b18`) and, for per-level values, the table object's
  virtual +0xd8(level). Paired with their labels in the game's detail panel `0x57f5ac` (message file 1 is
  `CommonMsg`, 9 is `StartMenuMsg`):

  | Getter | Value | Label |
  | --- | --- | --- |
  | `0xdb7e0` | Attack, weapons (type 7..21) | CommonMsg 0x36 "Attack" |
  | `0xdb88c` | Affinity, weapons | StartMenuMsg 0x105 "Affinity" |
  | `0xdbe74` | Defense: armor through the table's +0x120(level), weapons through the level object's +0x2c | CommonMsg 0x38 "Defense" |
  | `0xdb984(record, i)`, `0xdba5c(record, i)` | Element type and value, i = 0, 1 | CommonMsg 0x37 "Elem." |
  | `0xdbf78(record, i)` | Armor and talisman value i through the table's +0x150 (resistance, inference) | |

- Raw table objects, when a getter is missing. Every weapon family's level object has the same virtual interface,
  each reading its own offsets: +0x28 attack, +0x2c defense, +0x30 affinity, +0x34 element value, +0x38 slots (checked
  on families 00, 08, 10 and 04, the 15, 17, 31 and 100-byte layouts). Armor table objects (`cArmorNNBase`, record
  pointer at +4, runtime layout `cArmorSeriesBase` 140 bytes, DTI field names): +0x1c rarity (`mRare` +0x73), +0x28
  base defense (`mDef` +0x76), +0x2c this part's slots (`mHeadSlotNum` +0x78 on the head class), +0xf8..+0x108 the five
  resistances (signed bytes +30..+34), +0x148(i) / +0x14c(i) this part's skill i type and points.
- Decorations: `0x194230(sItem, item)` (25 direct callers; sItem cell `0x18583a8`) returns the 12-byte `cDecoBase`
  for items 2638 on, or null outside the table: +4 slots, +5 / +6 skill types, +7 / +8 points (signed), DTI names.
- Skill names: `0x4cf018(*(*0x1896c20 + 0x13c), type)` returns a 24-byte record whose +4 is a message index;
  `getMessage` `0xb84114` on the table at cell `0x1896c28` with index * 2 (the item panel at 0x62aefc does this).
- Item names and descriptions: `getMessage` on cell `0x18583ac` with `data+8` * 2 for the
  name and * 2 + 1 for the description (the game's own `0x72ccc0` ORs in the 1).
- Rarity is stored one below what the game shows (itemData file byte 5, memory +0xd: Antidote Jwl 2 stores 4, shows 5;
  armor Bulldrome 0, shows 1); whether a getter already adds the 1 is unread.
- itemData file and memory records differ. `table\itemData` (`loc/arc/resident.arc`, `rItemData` vft `0x173f44c`):
  an 8-byte header (magic `0x41aa6666`, u32 count, 2991 in 1.4.0), then 44-byte records from byte 8, each starting
  with its own id. The load (slot 0x2c `0x192340`) reads them field by field (`0x185694`) into 56-byte memory
  records at `[+0x6c] + id * 56`, which `0x194228` returns. File byte to memory: 0 u32 id → +8; 4 → +0xc; 5 → +0xd;
  6 → +0xe; 7 u16 → +0x10; 9..13 → +0x12..+0x16; 14 → +4; 15 → +0x17; 16..18 → +0x18..+0x1a; 19 u32 → +0x1c;
  23 u32 → +0x20; 27 → +0x24; 28..43 eight u16 → +0x26..+0x34. Bytes 9..15 are stored as 0 or 1. Memory fields
  named elsewhere: +0xe carry limit, +0x17 a count-colour flag ([Item Pouch screen](pouch-and-equipment-screens.md#item-pouch-screen)), +0x18 icon, +0x19 colour,
  +0x1a 2 for Rustshard and Ancient Shard only (their pickup jingle, [Jingles](jingles.md)).
- Skill effects: `0x2864c4(player, id)` is true when bit `id` of the bitset at
  `[[player + 0x13c4] + 0x188] + 0x3dc` is set (`0xe0da0`). The effect's name is text `2 * id` and its description
  `2 * id + 1` in `eng\table\skillData_eng` (a different table from `skillTypeData_eng`, the skill trees above).
  Checked on 206 Outdoorsman (the BBQ window), 244 Honey Hunter, 245 Charm Chaser, 246 Charm Collector,
  263 Soul of Yukumo, 271 Crystalbeard Soul, 289 C.beard Soul X and 320 Pack Rat against what the code does with
  each (pickup bonuses: [Jingles](jingles.md)).

Cross-check fixtures from the RomFS (for tests, not shipped): `decoData.deco` record item-2638 = {slots, skill A,
points A, skill B, points B}, Antidote Jwl 2 `02 01 03 04 ff` = slots 2, Poison +3, Stun -1 as in the screenshot;
`skillTypeData_eng.gmd` text 2*i (1 Poison, 4 Stun); `armorSeriesData.asd` (127-byte file records) Rathalos S (446)
res 4/0/-2/0/-4, head slots 0; Bulldrome (44) res 0/2/-2/1/0, arm slots 1; `armorBuildData.abd` per-level increases
give 58+8+8+8 = 82 (Rathalos Helm S level 4) and 12+4+4+4+8 = 32 (Bulldrome Braces level 5), the screenshots' values;
`itemData_eng.gmd` name 2*id, description 2*id+1. Weapon level files: families 00..03, 07, 13 are 15 bytes in the wiki
`w00d_lvl` order; the others differ, which the runtime interface hides.

## Armor names

`armorSeriesData_eng` holds ten strings per series number: five piece names in part order, then five descriptions. Matching a piece name within its part gives one series for 5,405 names and two for 232 (Mosgharl Vizor: series 76 and 694); none match zero or more than two. Treat a piece as owned when either series is in the box for that part.
