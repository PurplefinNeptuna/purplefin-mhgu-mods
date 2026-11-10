# Equipment box, weapon crafting and armor series

MHGU 1.4.0. Each fact names its source; "inference" marks what the bytes have not shown.

## Equipment box

Forge singleton `sEquipBox` (find by name), class size 261108: 2000 records of 44 bytes from +0x1c, then 1000 more
from +0x157dc, both walked by the save loader `main+0x14b0b0`. My Weapon Tree's working reader (0.55
NRO+0x8481c, copied in `mods/wishfinder-mwt-bridge/core/src/lib.rs::read_box`) reads them from +0x20: type = bits 0..4 and level bits = bits 5..9 of the u16 at slot +0, number = u16 at +2. The DTI class `cFestaEquip` is 44 bytes, and
the game's decoder `FUN_00b0803c` (`main+0x13f03c`: `ldrh r2, [r1, #4]`, `and r3, r2, #31`, `sub r2, r3, #1`,
`cmp r2, #23`, `movhi r0, #0`, then `ldrh r2, [r1, #6]`, `b main+0x13c208`) reads the type from the u16 at **+4**
and the number from **+6**, so types **1..23** are valid, 0 is empty, and the data getter is
`main+0x13c208(type, number)`. The smithy writes the level into bits 5..9 of that u16 (`and r1, r1, r2` with
`0xfc1f`, `orr r1, r1, r2, lsl #5` at `main+0x6f9ef8`; `bfi r0, r1, #0, #5` at `main+0x7008e4`). **The level bits count from 0: they hold the shown level minus one.** `main+0x6f9f00` loads the row byte at window `+0x28dd` (row `+9`) and `main+0x6f9f08` shifts it straight into the bits, and in the tester's save (`system`, read-only, 44-byte records at 0x192fd2..0x1931ee) the six weapons they listed at shown levels 5, 6, 5, 3, 4 and 2 hold 4, 5, 4, 2, 3 and 1. So a level-1 weapon holds 0 with a non-zero type, and the row byte counts from 0 too: saved upgrade keys hold 1 and 6 where the matching process rows are levels 2 and 7 (Sage Rod, General's Bayonet; a third saved key, Full Bolt Chamber, matches no row of its table). RomFS `mLevel`, `deriveLv` and the player's display count from 1.
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
(`+132028`) and `+254028` have no reader in those two functions. The instance slots are all read as
`ldr rX, [pc, #imm]` then `ldr rY, [pc, rX]`, whose pc is the second load's address + 8: the box save loader's object
is `main+0x1839394` (`main+0x3e77f0` → literal `main+0x3e7944` = `0x1451b94`), the equip code's box object is the same
`main+0x1839394` (`main+0x2633bc` → literal `main+0x2634c8` = `0x15d5fbc`), the getter's session object is
`main+0x1838d88` (`main+0x1438b4` → literal `main+0x143948` = `0x16f54c4`), the hunter status object is
`main+0x1838d80` (`main+0x3e782c` → literal `main+0x3e7950` = `0x1451544`), and the param loader's object is
`main+0x1838bbc` (`main+0x3e7840` → literal `main+0x3e7954` = `0x145136c`).

Weapons are types 7..21 except 12: type = weapon table + 7, and there is no table 05. Box armor is types 1..5,
part + 1 in head, chest, arms, waist, legs order (`cArmor00Base`..`cArmor04Base` return 1..5 from vtable +0x18),
number = armor series. Types 6, 22 and 23 are unnamed, and game code gates the weapon path on them: `main+0x26ee70`
`ldrh r0, [r1, #4]; and r0, #31; sub r0, #7; cmp r0, #14; bhi` rejects anything outside 7..21.

**The equipped gear is one box index plus one copied `cFestaEquip` per slot, and the weapon is slot 0.** The
type→slot table `main+0xdae68` (`ldr r0, [r1, r0, lsl #2]`, data at `main+0x159fd28`) maps a record's type bits to a
slot: `0 → 255`, `1..5 → 1..5`, `6 → 6`, `7..22 → 0`, `23 → 1`, `24 → 2` (the table's words). The param loader writes
types 22, 23 and 24 into entries 0, 1 and 2 when their index is `0xffff` (`main+0x263424`..`main+0x263434`), so
those three types are what an empty weapon, head and chest slot hold; what they draw as is not read. The live gear lives in
`nPlayer::cPlayerParam` (1376 bytes), which `uPlayerBase + 0x13c4` holds a **pointer** to (`mpPlParam`; the factory
`main+0x275d44` computes `base + 0x5bdc + player*1376` with `mov r0, #1376; mla r0, r6, r0, r9` plus
`movw r1, #0x5bdc`, stores it at `main+0x275d6c` (again at `main+0x275e1c`), and `main+0x275d78` loads it back before using it; the
constructor zeroes the slot at `main+0x27a3f8`): the 7 indices are the u16s at `param + 8 + slot*2`
(`0xffff` = empty) and the entries are at `param + 0x18 + slot*44`, both indexed by the accessors `main+0xe100c` /
`main+0xe1018` (index) and `main+0xdf814` / `main+0xe0d90` (`mov r2, #44; mla r0, r1, r2, r0; add r0, r0, #20`).
Writer: the equip action `main+0x26eaa8(param, boxIndex, flag)` resolves the box record with `main+0x143894` (kind 1
only when the byte at `param+0x4d4` is 15, otherwise kind 0) and `main+0x26f024(param, slot, record, index)` stores
it with `bl main+0xdadf0` plus the index with `bl main+0xe1018`, then recomputes derived state (`main+0x26fa30`,
`main+0x26fb00`, `main+0xdee34`, `main+0xe1bbc`, `main+0xe1e7c`, `main+0xe1eec`, `main+0xe79a0`, `main+0xe1fe4`).
Reader: `uPlayerBase::calculateSharpnessType` `main+0x29cdfc` takes entry 0 (`mov r1, #0; bl main+0xdf814`), calls
the weapon data getter `main+0x13f03c` and puts bits 5..9 of its `+4` u16 (`ldrh r1, [r6, #4]; ubfx r1, r1, #5, #5`)
into that record's vtable `+0xd8`. The saved hunter status holds the same 7 slots at `status + 0x84` (indices) and
`status + 0x94` (entries), resolved with kind 0 by the loader `main+0x2755f0` (`main+0x275670 mov r1, #0; bl
main+0x143894`).

**`param + 0x4d4` is the equipped weapon's category: the equipped record's type minus 7.** The store follows the
equip: `main+0x26ea70 mov r0, r9; bl main+0xdaea4; main+0x26ea78 cmp r0, #255; main+0x26ea7c strbne r0, [r4,
#0x4d4]`, with `r9` the record's type bits (`main+0x26e9fc ldrh r0, [r5, #4]; main+0x26ea00 and r0, r0, #31`) and
`main+0xdaea4` indexing the words at `main+0x159fdcc`: types 0..6 and 23, 24 → 255 (leave the byte), types 7..22 →
0..15. So 15 is type 22's category. The same byte picks the box kind (the equip action's `cmp r0, #15`) and the
player class: `main+0x275afc` (`ldrb r0, [r8, #0x4d4]; cmp r0, #15; bhi main+0x275db4`) jumps 16 ways over the table
at `main+0x275b18`, entry 5 exits — the missing weapon table 05 — and entry 15 goes to `main+0x276028 mov r0, #13312;
bl main+0x2b6894` where entry 0 goes to `main+0x275b58 mov r0, #13120`. The factory's second test, `main+0x275d90
ldrb r0, [r8, #0x4d4]; cmp r0, #15`, re-equips 3 entries for 15 (`main+0x276610`: slots 0, 1, 2) and all 7 otherwise
(`main+0x276478`). Type 22 is not a weapon to `main+0x26ee70` (7..21), it maps to gear slot 0 (`main+0x159fd28`), and
the equipment data getter `main+0x13c208` sends it to the container at `+0x1d4` (`main+0x13c320`) and types 23, 24 to
the one at `+0x1d0` (`main+0x13c2a0`), while type 12 has no case (its table entry jumps to `main+0x13c32c`). That
category 15 is the Prowler's (Otomo, equip type 22) is **inference**: the RomFS pairs `otWeaponData.owp` +
`otWeaponCreate.oec` and `otArmorData.oar` + `otArmorCreate.oec`, DTI `uOtomo` and `uOtomoLobby`, and the list in
`mods/modern-weapon-controls/DEVELOPMENT.md`, "0 GS … 14 CB, 15 Prowler (5 unused)". No byte names that container.
The 12 bytes `+0x4d4..+0x4df` match, by count and width, DTI `mCharParam[i]` of another class
(`nFestaNetwork::netPlData`, 12 `u8` properties at its `+0x4dc..+0x4e7`; `nPlayer::cPlayerParam` lists none), so
that name is inference; `mStyle` (Ghidra type, `+0x4d9`) is the sixth of them: `main+0x26e618`..`main+0x26e674` copy them between params
bytewise, and the hunter status save carries them at `status + 1360` = `(status + 0x7c) + 0x4d4` (`add r1, r10,
#1360; mov r2, #12` at `main+0x275730`) beside those kind-0 indices. The param loader `main+0x263368` always uses
kind 1, and its one caller `main+0x2639ac` loads 84 params (`main+0x263ba4`..`main+0x263bc4`, `add r6, r6, #1376;
cmp r4, #84`) at `object + 0x113938 + i*1376`; the default-init loop `main+0x2575f0` runs the same 84 × 1376 over
`object + 0x13938` and stores 15 in each at `main+0x25a224`. A hunter's param carries a byte of 0..14 and kind-0
indices — the saved status pairs them in one block, and the smithy equips that `+0x7c` block (`main+0x709954`'s slot
`main+0x1838d80` → `main+0x709960 bl main+0x277454` = `add r0, r0, #124` → `main+0x709974 bl main+0x26eaa8`) — while
a param with 15 indexes the 1000-record array. The entry is a copy of the box record at that index, so the equipped
weapon is also a record in the array the byte's kind selects. That the box keeps the record after equipping is inference: nothing read clears or moves it, and no code that removes a box record was read. Availability helpers
that take a `cFestaEquip*`: `main+0xdb5c4` (count) and `main+0x54ff2c` (pouch + box).

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
  `mNo` is the weapon number and `mLevel` the level at which that number can be **crafted directly**, which is not
  always 1: table 00 number 8 has its create row at level 6 with process rows at 1..9, number 12 at level 1 with
  process rows 1..7, and table 13 number 11 at level 6. Some numbers have no create row at all: table 11 number 6
  and number 25 have process rows for levels 1..8 and no create row, so their level-1 row is an upgrade from a
  *different* number, not a craft. Which file answers for a level is measured against the Smithy's own visits rather
  than inferred: a create row is what a direct craft charges, and at level 1 it is the step a chain starts from. All 127 create rows above level 1 also have a priced process row (table 00 number 8 at level 6: create 330x7, 1774x5, 333x1, 329x20, process 1774x1, 332x2, 324x5), and a chain walking up from level 1 pays the process row (that the upgrade screen charges it is inference from what the file is for, until a run compares them). 807 process rows carry no materials: a level-1 create row prices 771 of them, leaving 36 free steps, 22 at level 1 and 14 at level 2. A level neither file lists is absent. All 700 material groups KatSmithy logged in
  `work/wishfinder/runs/r10-recomp-2026-11-07.txt` (tables 03, 04, 06, 07, 08, 10, 12, 13) equal a create row's four
  items exactly, 163 distinct rows (`work/wishfinder-katsmithy-bridge/rise_vs_wcd.py`); in the 2026-11-09 log 22 of
  the 25 distinct groups equal the matching row of `work/wishfinder/inputs/weaponPath.bin` at the number and level
  named, 2 equal that number's create row at its own level, and one group is KatSmithy leaving one of four items
  out (`Clero Blade 1` omits 582x4, which the game's own row carries) —
  `work/wishfinder-katsmithy-bridge/rise_vs_path.py` reproduces that count. KatSmithy prints only the four items,
  never the row's pieces. Its `FULL layout type=N` is the weapon table N, not the equip type.
  The three piece slots hold a disjoint set of IDs: over all 14 classes the item slots hold 1,733 distinct
  IDs and the piece slots 337, none in common (empty slots are 0 and excluded), and the three Scrap IDs
  2158 Ore Scrap, 2164 Bone Scrap and 2187 Velociprey Scrap+ appear only in piece slots. Whether a piece ever
  adds to what the Smithy charges is open until a run compares a step with the game's upgrade screen.
- `nativeNX/table/weaponNNBaseData.wNNd` holds the derive links. A record is `(len-8)/entryCount` bytes, 32 to 34,
  and the last ten bytes of each are five `{u8 deriveLv, u8 deriveID}` pairs: this weapon at level `deriveLv` leads
  into number `deriveID` at its level 1. Inverted, that names the parent of a derived first level, and the shortest
  such link is what the Smithy's list offers. Kiranico agrees on three: Petrified Blade LV2 makes Defender LV1
  (table 00 number 8, whose process row at level 1 charges 318 Iron Ore x5, 321 Disc Stone x5, 320 Machalite Ore
  x2); Petrified Daggers LV3 makes Type 51 Macerators LV1 (table 11 number 6, process row level 1 = 861 x2, 855 x4,
  318 x4, 423 x4); Dual Piercers (table 11 number 22) at LV2 makes Khezu Daggers (number 25) LV1. A level-1 row the
  create file prices has no parent, that weapon being crafted where it stands.
- `nativeNX/table/weaponNNLevelData.wNNd` is **per-level stats**, not a tree: its rows start with the number, the
  level and the attack, defense and affinity fields (`cWeaponLevelData`), and say nothing about which weapon a level
  comes from. What My Weapon Tree 0.55 reads is built in memory, from that plugin's own code (copied in
  `mods/wishfinder-mwt-bridge/core/src/lib.rs::level`): a per-class `{ptr, len}` pair of 80-byte level entries with the
  name `{ptr,len}` at words 0/1, a craft list `{ptr,len}` at 6/7 and an upgrade list `{ptr,len}` at 10/11, whose
  8-byte elements `{u16 id, u8 kind, u8 0, u32 count}` carry the parent link in `kind`: 0 is an item, 1..15 names the
  weapon that level comes from, in table `kind - 1`, at `id = number << 8 | level`. That shape is MWT's reader's, not
  a fact about the RomFS files above.

The smithy window's row array at `+0x28d4` (48-byte rows) is built by code, not loaded from a file:
`main+0x6f0134` clears 2368 bytes of it (`bl main+0x13efd7c`, a memset), `main+0x70091c` fills the selected row (`+2` number from window `+0x2ebc`, `+9` level counted from 0, `+0x10` a pointer to a source record whose type is not verified)
and `main+0x6f5570`..`main+0x6f56bc` the list rows. Each row's entry comes from a per-class container at window
`+0x1f04 + type*4`, `{u32 count +0x64, data +0x6c}` of 48-byte elements indexed directly by the weapon number
(`main+0x4c0090`).

**The window names the selected weapon, not its level.** What is reliable across a co-installed weapon-tree mod is
category (`+0x5c` u16) and number (`+0x5c` high half, repeated at `+0x5e` u16), which the game and the mod agree on;
the row's `+9` level byte belongs to whatever row the game last built for that slot. Over 30 right-stick presses on
2026-11-09 the category and number matched KatSmithy's own `5C=`/`5E=` in every one and the row's level byte matched
its tree level in none, because that mod rewrites the displayed rows and the level field it leaves alone
(`DIRECT rows(+2) before: 0001 000B 001A … m2 after 6F53E4: 005B 0086 0085 0084 0008 0051 0000 0000 cur=4 page=4
5E=8`). Untried alternative: the entry array at window `+0x1f80 + index*0x30` (`+0xcc` class, `+0xd0` level).

Inference, not shown in bytes: the `.wpd` row of a level 1 that also has a `.wcd` row is a create-from-base-weapon path rather than the step a chain starts from (the rule `mods/wishfinder/scripts/generate_weapon_path.py` builds on). Armor recipes are
`armorCreateA00..A04` (see the Resources and tooling reference for the 42-byte records).

## Armor names

`armorSeriesData_eng` holds ten strings per series number: five piece names in part order, then five descriptions. Matching a piece name within its part gives one series for 5,405 names and two for 232 (Mosgharl Vizor: series 76 and 694); none match zero or more than two. Treat a piece as owned when either series is in the box for that part.
