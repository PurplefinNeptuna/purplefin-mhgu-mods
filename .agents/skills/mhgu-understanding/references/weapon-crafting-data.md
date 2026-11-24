# Weapon crafting data

Both tables are loose in the RomFS and also inside `arc/facility/blacksmith.arc`, tables 00..14 without 05. Layouts are verified by exact file size over all 14 of each.

- `nativeNX/table/weaponProcessW<table>.wpd`, `rWeaponProcessData`: `float version, u32 entryCount`, then rows of 32 bytes. A row is `{u16 mNo, u16 mLevel, 4 x {u16 item, u8 count}, u16 mCategory, u16 mRank, 3 x {u16 id, u16 count} pieces}`. Size is `8 + 32*entryCount`, and levels run 1..15. Counts: 958, 877, 885, 857, 718, 703, 875, 769, 809, 735, 844, 801, 547, 533. `mCategory`/`mRank` are 0/0 on the lv 1, 4 and 7 rows; the lv 1 and lv 2 rows of number 1 are empty in every table.
- `nativeNX/table/weaponCreateW<table>.wcd`, `rWeaponCreateData`: rows of 38 bytes `{u16 mLevel, u16 mNo, u16 mDispFlag, 4 x {u16 item, u8 count, u8 key}, u16 mCategory, u16 mRank, 3 pieces}`, size `8 + 38*entryCount`.
  - `mNo` is the weapon number and `mLevel` the level at which that number can be **crafted directly**, which is not always 1. Table 00 number 8 has its create row at level 6 with process rows at 1..9. Number 12 has it at level 1 with process rows 1..7, and table 13 number 11 at level 6.
  - Some numbers have no create row at all: table 11 number 6 and number 25 have process rows for levels 1..8 and no create row, so their level-1 row is an upgrade from a *different* number, not a craft.
  - Which file answers for a level is measured against the Smithy's own visits rather than inferred: a create row is what a direct craft charges, and at level 1 it is the step a chain starts from.

All 127 create rows above level 1 also have a priced process row. For example, table 00 number 8 at level 6: create 330x7, 1774x5, 333x1, 329x20; process 1774x1, 332x2, 324x5. A chain walking up from level 1 pays the process row. That the upgrade screen charges it is inference from what the file is for, until a run compares them. 807 process rows carry no materials: a level-1 create row prices 771 of them, leaving 36 free steps, 22 at level 1 and 14 at level 2.

A level neither file lists is absent. The three piece slots hold a disjoint set of IDs. Over all 14 classes the item slots hold 1,733 distinct IDs and the piece slots 337, none in common (empty slots are 0 and excluded). The three Scrap IDs 2158 Ore Scrap, 2164 Bone Scrap and 2187 Velociprey Scrap+ appear only in piece slots. Whether a piece ever adds to what the Smithy charges is open until a run compares a step with the game's upgrade screen.
- `nativeNX/table/weaponNNBaseData.wNNd` holds the derive links. A record is `(len-8)/entryCount` bytes, 32 to 34, and the last ten bytes of each are five `{u8 deriveLv, u8 deriveID}` pairs: this weapon at level `deriveLv` leads into number `deriveID` at its level 1.
  - Inverted, that names the parent of a derived first level, and the shortest such link is what the Smithy's list offers.
  - Kiranico agrees on three:
    - Petrified Blade LV2 makes Defender LV1 (table 00 number 8). Its process row at level 1 charges 318 Iron Ore x5, 321 Disc Stone x5, 320 Machalite Ore x2.
    - Petrified Daggers LV3 makes Type 51 Macerators LV1 (table 11 number 6, process row level 1 = 861 x2, 855 x4, 318 x4, 423 x4).
    - Dual Piercers (table 11 number 22) at LV2 makes Khezu Daggers (number 25) LV1.
  - A level-1 row the create file prices has no parent, that weapon being crafted where it stands.
- `nativeNX/table/weaponNNLevelData.wNNd` is **per-level stats**, not a tree: its rows start with the number, the level and the attack, defense and affinity fields (`cWeaponLevelData`), and say nothing about which weapon a level comes from.

The smithy window's row array at `+0x28d4` (48-byte rows) is built by code, not loaded from a file.

- `main+0x6f0134` clears 2368 bytes of it (`bl main+0x13efd7c`, a memset).
- `main+0x70091c` fills the selected row: `+2` number from window `+0x2ebc`, `+9` level counted from 0, `+0x10` a pointer to a source record whose type is not verified.
- `main+0x6f5570`..`main+0x6f56bc` fill the list rows.

Each row's entry comes from a per-class container at window `+0x1f04 + type*4`, `{u32 count +0x64, data +0x6c}` of 48-byte elements indexed directly by the weapon number (`main+0x4c0090`).

Inference, not shown in bytes: the `.wpd` row of a level 1 that also has a `.wcd` row is a create-from-base-weapon path rather than the step a chain starts from. Armor recipes are `armorCreateA00..A04` (see the Resources and tooling reference for the 42-byte records).

Value-material rows (`mCategory` set, `mRank` the value required; RomFS `nativeNX/table/`, 1.4.0):

| Table | Rows with a value material |
| --- | --- |
| Weapon crafts (`.wcd` +22) | 0 of 1152 |
| Armor crafts (`.acrd` +26) | 340 of 2720; categories 13 and 14 most often (60 + 15 rows each), with value 8 or 5 |
| Weapon upgrades (`.wpd` +16) | 5685 of 10911 |
| Armor upgrades (`.apd` +22) | 1506 of 5162 |
| Kinsect level-ups (`insectProcess.wpd` +16) | 0 of 204 |

Decoration rows (`decoCreate.dcd`) are 16 bytes; whether one holds a category is unread.
