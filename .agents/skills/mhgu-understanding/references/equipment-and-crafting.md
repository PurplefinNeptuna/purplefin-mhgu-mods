# Equipment box, weapon crafting and armor series

Verified on MHGU 1.4.0 through the Wishlist bridge for My Weapon Tree (`mods/wishlist-mwt-bridge/`, `scripts/generate_armor.py`).

## Equipment box

Forge singleton `sEquipBox` (find by name): 2000 slots of 44 bytes from +0x20. Type = byte 0 bits 0..4; level = bits 5..9 of the first u16; number = u16 at +2. Weapons are types 7..21 except 12 (type = weapon table + 7). Armor types 1..5 are part + 1 in head, chest, arms, waist, legs order (inferred from My Weapon Tree's reader and from `armorCreateA00` holding Leather Headgear), number = armor series.

## Weapon crafting data

`arc/facility/blacksmith.arc` holds `weaponProcessW<table>` per weapon class, tables W00..W14 without W05. Row `(weapon number, level)` lists the craft items and the upgrade-from weapon (at most four items). Upgrade-from of level > 1 is always level - 1 of the same weapon. Armor recipes are `armorCreateA00..A04` (see the Resources and tooling reference for the 42-byte records).

## Armor names

`armorSeriesData_eng` holds ten strings per series number: five piece names in part order, then five descriptions. Matching a piece name within its part gives one series for 5,405 names and two for 232 (Mosgharl Vizor: series 76 and 694); none match zero or more than two. Treat a piece as owned when either series is in the box for that part.
