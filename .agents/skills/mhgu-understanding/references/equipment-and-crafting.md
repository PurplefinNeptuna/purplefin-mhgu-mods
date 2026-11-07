# Equipment box, weapon crafting and armor series

Verified on MHGU 1.4.0 through the Wishlist bridge for My Weapon Tree (`mods/wishlist-mwt-bridge/`, `scripts/generate_armor.py`).

## Equipment box

Forge singleton `sEquipBox` (find by name): 2000 slots of 44 bytes from +0x20. The slot record is
`cFestaEquip` (DTI, 44 bytes): type = bits 0..4 of the u16 at **+4**, level = bits 5..9 of that u16, number = u16 at
**+6**, bit 15 of the +4 u16 is a flag `cFestaEquip::reset` (`main+0xdac14`) preserves, and a 40-byte payload plus a
pointer at +0x28 follow. A box slot carries the same two u16s four bytes earlier, at slot +0 and +2, and that is
the pair My Weapon Tree's working reader uses; the two views differ only by that 4-byte head.
`FUN_00b0803c` (`main+0x13f03c`) is the decoder: `and r3, r2, #31`, `sub r2, r3, #1`, `cmp r2, #23`, `movhi r0, #0`
⇒ types **1..23 are valid and 0 is empty**, and the data getter is `main+0x13c208(type, number)`. The availability
helpers that take a `cFestaEquip*` are `main+0xdb5c4` (count) and `main+0x54ff2c` (pouch + box). Weapons are types
7..21 except 12 (type = weapon table + 7). Armor types 1..5 are part + 1 in head, chest, arms, waist, legs order
(inferred from My Weapon Tree's reader and from `armorCreateA00` holding Leather Headgear), number = armor series.
Types 6, 22 and 23 are unnamed, and which one holds the weapon in hand is not settled by the bytes. Equipped gear sits in the same array, which is why the armor parts have their own types; the type of the **equipped weapon** slot is not verified, and is one of the types the ranges above leave out (0, 6, 12). My Weapon Tree's reader, and any reader that copies it, counts box weapons at 7..21 and equipped armor at 1..5, so it treats an equipped weapon as not owned.

## Weapon crafting data

`nativeNX/table/weaponProcessW<table>.wpd`, tables 00..14 without 05 (the same files sit inside
`arc/facility/blacksmith.arc`), is `rWeaponProcessData`: `float version, u32 entryCount`, then rows of 32 bytes
`{u16 mNo, u16 mLevel, 4 x {u16 item, u8 count}, u16 mCategory, u16 mRank, 3 x {u16 id, u16 count} pieces}`,
verified as exactly `8 + 32*entryCount` for all 14 sizes, counts 958, 877, 885, 857, 718, 703, 875, 769, 809, 735,
844, 801, 547, 533, and levels 1..15. `mCategory` and `mRank` are 0/0 on the lv 1, 4 and 7 rows and non-zero on the
others; the lv 1 and lv 2 rows of number 1 are empty in every table. `nativeNX/table/weaponCreateW<table>.wcd` is
`rWeaponCreateData`: rows of 38 bytes `{u16 mLevel, u16 mNo, u16 mDispFlag, 4 x {u16 item, u8 count, u8 key},
u16 mCategory, u16 mRank, 3 pieces}`, verified as exactly `8 + 38*entryCount`; its `mNo` is a create-entry index,
not the weapon number a smithy list names. The smithy window (its sub-screen `shop_prcsn`) loads 74 `.wpd` records
into `+0x28d4` (`main+0x6f0134` calls `main+0x13efd7c(window+0x28d4, 2368)`) and indexes them as 48-byte rows, so
the row list the game shows is `.wpd` data; which file feeds a given create-list row is not verified. No row stores
its own chain link: taking the upgrade-from of a level above 1 as level - 1 of the same line is inference from the
shape of the rows and My Weapon Tree's baked table, not from the bytes. Armor recipes are `armorCreateA00..A04`
(see the Resources and tooling reference for the 42-byte records).

## Armor names

`armorSeriesData_eng` holds ten strings per series number: five piece names in part order, then five descriptions. Matching a piece name within its part gives one series for 5,405 names and two for 232 (Mosgharl Vizor: series 76 and 694); none match zero or more than two. Treat a piece as owned when either series is in the box for that part.
