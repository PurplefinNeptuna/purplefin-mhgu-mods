# Equipment box, weapon crafting and armor series

MHGU 1.4.0. Each fact names its source; "inference" marks what the bytes have not shown.

## Equipment box

Forge singleton `sEquipBox` (find by name), 2000 slots of 44 bytes. My Weapon Tree's working reader (0.55
NRO+0x8481c, copied in `mods/wishlist-mwt-bridge/core/src/lib.rs::read_box`) reads them from +0x20: type = bits
0..4 and level = bits 5..9 of the u16 at slot +0, number = u16 at +2. The DTI class `cFestaEquip` is 44 bytes, and
the game's decoder `FUN_00b0803c` (`main+0x13f03c`: `ldrh r2, [r1, #4]`, `and r3, r2, #31`, `sub r2, r3, #1`,
`cmp r2, #23`, `movhi r0, #0`, then `ldrh r2, [r1, #6]`, `b main+0x13c208`) reads the type from the u16 at **+4**
and the number from **+6**, so types **1..23** are valid, 0 is empty, and the data getter is
`main+0x13c208(type, number)`. The smithy writes the level into bits 5..9 of that u16 (`and r1, r1, r2` with
`0xfc1f`, `orr r1, r1, r2, lsl #5` at `main+0x6f9ef8`; `bfi r0, r1, #0, #5` at `main+0x7008e4`).
`cFestaEquip::reset` (`main+0xdac14`) keeps bit 15 of the +4 u16. The two readings agree if the `cFestaEquip`
array starts at +0x1c; that base is inference until the code that indexes the array is read.

Weapons are types 7..21 except 12: type = weapon table + 7, and there is no table 05. Box armor is types 1..5,
part + 1 in head, chest, arms, waist, legs order (`cArmor00Base`..`cArmor04Base` return 1..5 from vtable +0x18),
number = armor series. Types 6, 22 and 23 are unnamed. **Where the equipped weapon and armor live is not
verified**: no code read so far shows whether they are box slots, other slot types, or references held elsewhere,
so a reader must not claim that the box omits or includes them. Availability helpers that take a `cFestaEquip*`:
`main+0xdb5c4` (count) and `main+0x54ff2c` (pouch + box).

## Weapon crafting data

Both tables are loose in the RomFS and also inside `arc/facility/blacksmith.arc`, tables 00..14 without 05.
Layouts are verified by exact file size over all 14 of each.

- `nativeNX/table/weaponProcessW<table>.wpd`, `rWeaponProcessData`: `float version, u32 entryCount`, rows of 32
  bytes `{u16 mNo, u16 mLevel, 4 x u16 item, 4 x u8 count, u16 mCategory, u16 mRank, 3 x {u16 id, u16 count}
  pieces}`, size `8 + 32*entryCount`, counts 958, 877, 885, 857, 718, 703, 875, 769, 809, 735, 844, 801, 547, 533,
  levels 1..15. `mCategory`/`mRank` are 0/0 on the lv 1, 4 and 7 rows; the lv 1 and lv 2 rows of number 1 are empty
  in every table.
- `nativeNX/table/weaponCreateW<table>.wcd`, `rWeaponCreateData`: rows of 38 bytes `{u16 mLevel, u16 mNo,
  u16 mDispFlag, 4 x {u16 item, u8 count, u8 key}, u16 mCategory, u16 mRank, 3 pieces}`, size `8 + 38*entryCount`.
  Its `(mLevel, mNo)` is the weapon number and level the smithy shows: of the 632 level-1 material groups
  KatSmithy logged in `work/wishlist/runs/r10-recomp-2026-11-07.txt`, 588 equal a create row's four items, over 142
  `(class, number)` nodes. **44 differ and 20 have no create row, unexplained**; until they are, treat the key as
  verified for those 142 nodes only.

The smithy window's row array at `+0x28d4` (48-byte rows) is built by code, not loaded from a file:
`main+0x6f0134` clears 2368 bytes of it (`bl main+0x13efd7c`, a memset), `main+0x70091c` fills the selected row
(`+2` number from window `+0x2ebc`, `+9` level, `+0x10` a pointer to a source record whose type is not verified)
and `main+0x6f5570`..`main+0x6f56bc` the list rows. Each row's entry comes from a per-class container at window
`+0x1f04 + type*4`, `{u32 count +0x64, data +0x6c}` of 48-byte elements indexed directly by the weapon number
(`main+0x4c0090`).

Inference, not shown in bytes: a level above 1 upgrades from level - 1 of the same number (the row shapes and My
Weapon Tree's baked table), and the `.wpd` row of a level that also has a `.wcd` row is a create-from-base-weapon
path, not an upgrade step (the rule `mods/wishlist/scripts/generate_weapon_path.py` builds on). Armor recipes are
`armorCreateA00..A04` (see the Resources and tooling reference for the 42-byte records).

## Armor names

`armorSeriesData_eng` holds ten strings per series number: five piece names in part order, then five descriptions. Matching a piece name within its part gives one series for 5,405 names and two for 232 (Mosgharl Vizor: series 76 and 694); none match zero or more than two. Treat a piece as owned when either series is in the box for that part.
