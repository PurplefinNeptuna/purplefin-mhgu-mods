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

## Smithy window and its code

From WishFinder (`mods/wishfinder/DEVELOPMENT.md` sections Hooks and Smithy). `uUIBlackSmith` update `0x6f1ae8` (vtable `0x177d988` slot 0x24) is the one per-frame entry; KatSmithy guards it, so read [Other mods](../../mhgu-forge-modding/references/other-mods.md) before hooking it.

| Field | Meaning |
| --- | --- |
| +4 byte 0 | State: 1 menu, 2 submenu, 3 weapon or armor list `0x6f31d8`, 5 decorations `0x6f5064`, 6 `0x6f5940`, 7 upgrade `0x6f7220` |
| +5, +6 | Sub-states. The list has focus at state 3 or 5 with +5 = 0, and state 7 with +5 = 0x19 and +6 = 0 (`0x7045dc`) |
| +0x44 | Row confirmed |
| +0x4c / +0x4d | Menu index / submenu index |
| +0x68 | Saved list position, written as `page << 3`, read on rebuild sub-state 9 |
| +0x6c / +0x70 / +0x74 | Pad pressed / repeat / held, copied from `sFestaPad` +0x6bfc / +0x6c34 / +0x6bf4 each update |
| +0x1f64 | Row cursor (`0x54edec(+0x1f64, 4, 1, 0)` sets up the menu); page at +0x1f74 |
| +0x2d14, +0x2d18 + i*8 | Top menu text table {flag word, text pointer} |
| +0x5c | Category: 1..5 armor head..legs, 6 talisman/decorations, 7 + table for weapons. Set at `0x6f2c90` (weapons from byte table `0x1650022` by +0x4d, else +0x4d + 1); Upgrade copies the box item's type at `0x6f7e2c`. 2..6 gates armor's Resort; 1 picks the head preview |
| +0x6c | Copy of the menu-pressed pad word `sFestaPad+0x6bfc` |
| +0x1f71 | Cursor's row on the page |
| +0x28d4 + row * 0x30 | Row: +2 number, +9 level from 0, +0x14 four {u16 item, u8 count at +2} every 4 bytes. A decoration row (builder `0x6fdb84`) has +2 the item, +4 the recipe index into the table at window +0x1f18 (`0x4c0e60`: count +0x64, 20-byte objects at +0x6c, item from virtual +0x18), +9 zero |

| Code | Role |
| --- | --- |
| `0x6fbcfc` | Pays and consumes for a confirmed row; called by craft `0x6fb224` and upgrade `0x70301c` |
| `0x6fdf14` | Decoration: consumes, pays, adds the item; called from `0x6f513c` |
| `0x70301c(window)` | Upgrade of one box record, then the pay step at `0x7035d0`; called from `0x702de8` and by KatSmithy's direct upgrade with the window still in state 3 (its log, `ARM-WIN W+4=00000003`). Record choice below the table |
| `0x6fd690` | Box-space check before confirm, so a hook on the pay functions sees only crafts that proceed |
| `0x709a08`, `0x709d54` under `0x709824` | Consume one item at a time; unread |
| `0x54f260(0, n)` | Smithy sounds: 1 accept, 2 cancel, 3 deny. 43 (taken for `lb_sys_chat_reception`) played nothing |
| `0x13c208(sEquip, category, number)` then virtual +0xbc(level) / +0xc0(level) | Equipment name / description; +0x1c rarity. Text table cell `0x1856b1c`, 0 in a quest |
| `sItem::getItemData` `0x194228`, `rGUIMessage::getMessage` `0xb84114` | Item name: data+8 times two, on the table at cell `0x18583ac` |
| `0x54ff2c` | Owned count = pouch `0x19c21c` (`*0x18584b8`) plus box `0x199048` (`*0x1858438`); both only read |

**Upgrade record.** `0x70301c` sets its box index once (`uxth r8` at `0x703068`): `u16 +0x20c0 * +0x20be * +0x20bf + (+0x20be * +0x20bd + +0x20bc) & 0xff`, low 16 bits. It reads the record with `0x143894(box, 0, index)` (box: GOT `0x1839394` names cell `0x1856fe8`), and every branch writes it back with `0x1431f8(box, 0, index, record)` at `0x7035c0`; an empty record skips the write and only pays.

The smithy row list is a native GUI tree ([Native GUI](native-gui.md#known-screens-and-trees)). `uUIBlackSmith` is 12,824 bytes. Smithy buttons: A 0x2000, B 0x4000, X 0x1000, Y 0x8000; `0x65f808` returns Options (8, or 1 when `sUserInfo+0x446d` is nonzero) and `0x65f830` Help, the reverse; Options is Resort when +0x5c is 2..6 and Show Skills in `0x6f5064` (also read at `0x6f5b50`, `0x6f5bd8`, `0x707884`; 5 of 47 callers read). `0x70a30c` is only the upgrade preview. A row label set through `0x56e808` -> `0x547564` takes a plain `char*` (strlen), so a plugin's static string works. Pad menu bits in +0x6c are listed in [Input and actions](input-and-actions.md); no smithy handler, preview slot or cursor mode (table `0x162d0c0`) tests L3 0x2 or R3 0x4, and `0x65f808` starts with PC-relative loads, so do not hook it. Finish keys a craft reports: kind, the row's 0-based level, category and number in one word (`00140012` craft, `01140012` upgrade, `42140012` the game's own upgrade screen).

**Item limit.** `[[[main+0x18583a8] + 0x1c] + 0x64] - 1` is the loaded `rItemData`'s last ID, the bound lookup `0x192530` uses: 2990 on 1.4.0 (2991 records), 3055 records with Definitive Edition.

**Loaded smithy tables.** `0x152960(0, file ID)` is the smithy's own lookup (`0x6f0870`): file table `0x15a0ce0`, then the resource manager's find `0xbcba9c` (`sResource` vtable `0x1795948` slot 0x38), which never loads and returns a loaded resource with +0x48 raised, or 0; release through `0x887660` (slot 0x3c, `0xbc8414`), as the window's destructor `0x6f02fc` does. File IDs are `~crc32` of the path: `weaponCreateW..` 0xf4a4.., `armorCreateA00..04` 0xf4b2.., `decoCreate` 0xf4b7, `weaponProcessW..` 0xf4b8.., `armorProcessA00` 0xf4c6 (`arc/facility/blacksmith.arc`, loaded with a town area), `weaponNNBaseData` 0xdde4.. (`loc/arc/resident.arc`). Count +0x64, records at `[+0x6c]`. DTI sizes: `cWeaponCreateData` 44 (`mLv` +4, `mNo` +6, `mItem` +10, `mNum` +18), `cWeaponProcessData` 36 (`mNo` +4, `mLv` +6, `mItem` +8, `mNum` +16), `cArmorCreateData` 48 (`mNo[4]` +4, `mItem` +14, `mNum` +22), `cWeaponNNBaseData` 40 (`mDeriveLv[5]` +28, `mDeriveID[5]` +33; +26/+31 for tables 04 and 06, `cLongWeaponBase`). The loose `nativeNX/table/` files equal the archive entries (47 of 47).

Do not: sum a smithy row's three piece slots into a cost (337 item IDs there, none shared with the 1,733 in the four item slots, and the runtime row has none); read a gear pack at `sPlayer::Instance + 0x7c` (unverified, read `kind=255`).

**Row price and owned count.** A list row's price is its block +0x10 (+0x28e4 + row*0x30); the header fill `0x6f8648` copies it to the display record +8, and the confirm steps (`0x6f44a8`, `0x6f4cb8`, `0x6f536c`) read it into +0x7c. With the table object `0x13c208(type, number)`: the craft list fill (`0x6f56c4`) charges, at row level 0 (+9, from 0), twice slot +0x20 for armor (types up to 5) and v + v/2 for a weapon; above level 0 it charges 1000 for armor and twice +0x158(level, flag, extra) for a weapon, flag and extra being 1 and 0x2134 for type 16 number 47 and type 21 number 26. The upgrade list fill (`0x700180`) charges +0x158(target level) for a weapon and +0x158(current level) for armor (types up to 6), not doubled. A decoration costs its item record's +0x20 (`0x6fdd54`, 200 without a record). Both lists charge 1000 without a table object. The card's owned count (header +6, `0x2d56`) is `0x142de4(box, 0, type, number)`, every level together.

**Kinsects** (static reads of main 1.4.0; the r97 capture confirmed the screen bytes). A kinsect lives in its Insect Glaive's box record, type 20 only: ID at +0x10 (`0xdcb8c`/`0xdcba8`), level at +0x11 counted from 0 (`0xdcbbc`/`0xdcbd8`), stats and attributes at +0x12..+0x25, filled from `cInsectData` by `0xdd7d0`. `cInsectData` (DTI `0x17368c4`, 56 bytes) is `0x13f518(*0x1856b18, id)`: +4 mType, +0x10 mTrgLv, +0x34 mIndex, the name's index in the message table at cell `0x1856b64` (`0xb84114(table, index)`; `insectData_eng.gmd` has 32 names, 20 Bullshroud). The smithy's kinsect screens are state 7 with +0x5c 0x14 and +0x4a 1; the level-up list `0x70181c` writes rows like the upgrade list's (+0x28d6 the ID, +0x28dd target level from 0, price 0, four materials). The level-up itself is `0x70301c` with +0x4a 1: +0x11 raised by one on a copy, bonus fields cleared, written back by `0x1431f8`, then `0x6fbcfc`; the record's +4 and +6 do not change.

## Equipment stats, decorations and skills

Static reading from `work/wishfinder/PLAN.md`: the game's detail-panel getters and table objects, with RomFS cross-checks.

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
- Rarity is stored one below what the game shows (itemData +5: Antidote Jwl 2 stores 4, shows 5; armor Bulldrome 0,
  shows 1); whether a getter already adds the 1 is unread.

Cross-check fixtures from the RomFS (for tests, not shipped): `decoData.deco` record item-2638 = {slots, skill A,
points A, skill B, points B}, Antidote Jwl 2 `02 01 03 04 ff` = slots 2, Poison +3, Stun -1 as in the screenshot;
`skillTypeData_eng.gmd` text 2*i (1 Poison, 4 Stun); `armorSeriesData.asd` (127-byte file records) Rathalos S (446)
res 4/0/-2/0/-4, head slots 0; Bulldrome (44) res 0/2/-2/1/0, arm slots 1; `armorBuildData.abd` per-level increases
give 58+8+8+8 = 82 (Rathalos Helm S level 4) and 12+4+4+4+8 = 32 (Bulldrome Braces level 5), the screenshots' values;
`itemData_eng.gmd` name 2*id, description 2*id+1. Weapon level files: families 00..03, 07, 13 are 15 bytes in the wiki
`w00d_lvl` order; the others differ, which the runtime interface hides.

## Armor names

`armorSeriesData_eng` holds ten strings per series number: five piece names in part order, then five descriptions. Matching a piece name within its part gives one series for 5,405 names and two for 232 (Mosgharl Vizor: series 76 and 694); none match zero or more than two. Treat a piece as owned when either series is in the box for that part.
