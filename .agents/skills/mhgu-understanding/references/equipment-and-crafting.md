# Equipment box, weapon crafting and armor series

MHGU 1.4.0. Each fact names its source; "inference" marks what the bytes have not shown.

## Equipment box

Forge singleton `sEquipBox` (find by name), class size 261108: 2000 records of 44 bytes from +0x1c, then 1000 more
from +0x157dc, both walked by the save loader `main+0x14b0b0`. My Weapon Tree's working reader (0.55
NRO+0x8481c, copied in `mods/wishlist-mwt-bridge/core/src/lib.rs::read_box`) reads them from +0x20: type = bits
0..4 and level = bits 5..9 of the u16 at slot +0, number = u16 at +2. The DTI class `cFestaEquip` is 44 bytes, and
the game's decoder `FUN_00b0803c` (`main+0x13f03c`: `ldrh r2, [r1, #4]`, `and r3, r2, #31`, `sub r2, r3, #1`,
`cmp r2, #23`, `movhi r0, #0`, then `ldrh r2, [r1, #6]`, `b main+0x13c208`) reads the type from the u16 at **+4**
and the number from **+6**, so types **1..23** are valid, 0 is empty, and the data getter is
`main+0x13c208(type, number)`. The smithy writes the level into bits 5..9 of that u16 (`and r1, r1, r2` with
`0xfc1f`, `orr r1, r1, r2, lsl #5` at `main+0x6f9ef8`; `bfi r0, r1, #0, #5` at `main+0x7008e4`).
`cFestaEquip::reset` (`main+0xdac14`) and `::assign` (`main+0xdadf0`: `bfi r3, r2, #0, #5` type bits 0..4, `lsr r2,
r2, #5` + `bfi r3, r2, #5, #5` level bits 5..9, `movw r2, #0x83ff` keeps bit 15 of the destination, then copies `+6`,
`+8`, `+10`, `+12`, `+14` and 24 bytes from `+16`) keep bit 15. The array base is **+0x1c**, from the slot getter
`main+0x143894(box, kind, index)`: 0 when the index is `0xffff` (`movw r0, #0xffff; cmp r5, r0`), a capacity check
from the session flags (`ldr r2, [r0, #0x958]` bits 0x15 and 0x16): kind 0 allows `1000 + 200 × flags + 200 ×
main+0x525878()`, kind 1 `300 + 200 × flags + 100 × main+0x525878()`, then `mov r0, #44; mla r0, r5, r0, r8; add r4, r0, #28` (kind 0, `main+0x14391c`) or `add r0, #988;
add r4, r0, #87040` (kind 1, `main+0x143930`) → `box + 0x1c + index*44` and `box + 0x157dc + index*44`. The save
loader `main+0x14b0b0` (read, via `main+0x3df2a8` → the memcpy `main+0x13efe30`) and the writer `main+0x14b1c4` (via
`main+0x3df378`) touch 2000 records at the first base (u16 `+0x20`, u16 `+0x22`, u16 `+0x24`, 6 bytes `+0x26`, 24
bytes `+0x2c`, plus `bl main+0xddd48(box + 0x1c + i*44)`) and 1000 at the second, so the bridge's `+0x20` base and
the decoder's `+4`/`+6` are one record (bridge base = base + 4). It also reads a 5440-byte blob at `+254028` and a
1632-byte blob at `+259468` (8 bytes before the class end); the 122,000 bytes between the second array's end
(`+132028`) and `+254028` have no reader in those two functions. The instance cell is `main+0x1839398` (save
dispatcher) and `main+0x1839390` (equip code); `main+0x1838d80` is the getter's session cell.

Weapons are types 7..21 except 12: type = weapon table + 7, and there is no table 05. Box armor is types 1..5,
part + 1 in head, chest, arms, waist, legs order (`cArmor00Base`..`cArmor04Base` return 1..5 from vtable +0x18),
number = armor series. Types 6, 22 and 23 are unnamed, and game code gates the weapon path on them: `main+0x26ee70`
`ldrh r0, [r1, #4]; and r0, #31; sub r0, #7; cmp r0, #14; bhi` rejects anything outside 7..21.

**The equipped gear is one box index plus one copied `cFestaEquip` per slot, and the weapon is slot 0.** The
type→slot table `main+0xdae68` (`ldr r0, [r1, r0, lsl #2]`, data at `main+0x159fd28`) maps a record's type bits to a
slot: `0 → 255`, `1..5 → 1..5`, `6 → 6`, `7..22 → 0`, `23 → 1`, `24 → 2` (the table's words). The param loader writes
types 22, 23 and 24 into entries 0, 1 and 2 when their index is `0xffff` (`main+0x263424`..`main+0x263434`), so
those three types are what an empty weapon, head and chest slot hold; what they draw as is not read. The live gear lives in
`nPlayer::cPlayerParam` (1376 bytes), reached as `uPlayerBase + 0x13c4` (`mpPlParam`, set at `main+0x275d6c` and
`main+0x275e1c` and zeroed by the constructor at `main+0x27a3f8`): the 7 indices are the u16s at `param + 8 + slot*2`
(`0xffff` = empty) and the entries are at `param + 0x18 + slot*44`, both indexed by the accessors `main+0xe100c` /
`main+0xe1018` (index) and `main+0xdf814` / `main+0xe0d90` (`mov r2, #44; mla r0, r1, r2, r0; add r0, r0, #20`).
Writer: the equip action `main+0x26eaa8(param, boxIndex, flag)` resolves the box record with `main+0x143894` (kind 1
only when the byte at `param+0x4d4` is 15, otherwise kind 0) and `main+0x26f024(param, slot, record, index)` stores
it with `bl main+0xdadf0` plus the index with `bl main+0xe1018`, then recomputes derived state (`main+0x26fa30`,
`main+0x26fb00`, `main+0xdee34`, `main+0xe1bbc`, `main+0xe1e7c`, `main+0xe1eec`, `main+0xe79a0`, `main+0xe1fe4`).
Reader: `uPlayerBase::calculateSharpnessType` `main+0x29cdfc` takes entry 0 (`mov r1, #0; bl main+0xdf814`), calls
the weapon data getter `main+0x13f03c` and puts bits 5..9 of its `+4` u16 (`ldrh r1, [r6, #4]; ubfx r1, r1, #5, #5`)
into that record's vtable `+0xd8`. The saved hunter status holds the same 7 slots at `status + 0x84` (indices) and
`status + 0x94` (entries), resolved with kind 0 by the loader `main+0x2755f0`; the param loader `main+0x263368` uses
kind 1 (its one direct caller, `main+0x263bb4` in `main+0x2639ac`, passes `r3 = 1`; which hunter that caller loads is
not read), and which array the main hunter's param points at is **not settled** (it depends on `param+0x4d4 == 15`).
The entry is a copy of the box record at that index, so the equipped weapon is also a record in whichever array
the index means. That the box keeps the record after equipping is inference: nothing read clears or moves it, and
no code that removes a box record was read. If the index means kind 1, a scan of the 2000 kind-0 records misses
the equipped weapon. Availability helpers that take a `cFestaEquip*`:
`main+0xdb5c4` (count) and `main+0x54ff2c` (pouch + box).

## Weapon crafting data

Both tables are loose in the RomFS and also inside `arc/facility/blacksmith.arc`, tables 00..14 without 05.
Layouts are verified by exact file size over all 14 of each.

- `nativeNX/table/weaponProcessW<table>.wpd`, `rWeaponProcessData`: `float version, u32 entryCount`, rows of 32
  bytes `{u16 mNo, u16 mLevel, 4 x {u16 item, u8 count}, u16 mCategory, u16 mRank, 3 x {u16 id, u16 count}
  pieces}`, size `8 + 32*entryCount`, counts 958, 877, 885, 857, 718, 703, 875, 769, 809, 735, 844, 801, 547, 533,
  levels 1..15. `mCategory`/`mRank` are 0/0 on the lv 1, 4 and 7 rows; the lv 1 and lv 2 rows of number 1 are empty
  in every table.
- `nativeNX/table/weaponCreateW<table>.wcd`, `rWeaponCreateData`: rows of 38 bytes `{u16 mLevel, u16 mNo,
  u16 mDispFlag, 4 x {u16 item, u8 count, u8 key}, u16 mCategory, u16 mRank, 3 pieces}`, size `8 + 38*entryCount`.
  Its `(mLevel, mNo)` is the weapon number and level the smithy shows: all 700 material groups KatSmithy logged
  in `work/wishlist/runs/r10-recomp-2026-11-07.txt` (tables 03, 04, 06, 07, 08, 10, 12, 13) equal a create row's
  four items exactly, 163 distinct rows (`work/wishlist-katsmithy-bridge/rise_vs_wcd.py`). KatSmithy prints only
  the four items, never the row's pieces. Its `FULL layout type=N` is the weapon table N, not the equip type.

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
