# Smithy window and its code

## Smithy window and its code

`uUIBlackSmith` update `0x6f1ae8` (vtable `0x177d988` slot 0x24) is the one per-frame entry.

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
| `0x70301c(window)` | Upgrade of one box record, then the pay step at `0x7035d0`; called from `0x702de8`. Record choice below the table |
| `0x6fd690` | Box-space check before confirm, so the pay functions run only for crafts that proceed |
| `0x709a08`, `0x709d54` under `0x709824` | Consume one item at a time; unread |
| `0x54f260(0, n)` | Smithy sounds: 1 accept, 2 cancel, 3 deny. 43 (taken for `lb_sys_chat_reception`) played nothing |
| `0x13c208(sEquip, category, number)` then virtual +0xbc(level) / +0xc0(level) | Equipment name / description; +0x1c rarity. Text table cell `0x1856b1c`, 0 in a quest |
| `sItem::getItemData` `0x194228`, `rGUIMessage::getMessage` `0xb84114` | Item name: data+8 times two, on the table at cell `0x18583ac` |
| `0x54ff2c` | Owned count = pouch `0x19c21c` (`*0x18584b8`) plus box `0x199048` (`*0x1858438`); both only read |

**Upgrade record.** `0x70301c` sets its box index once (`uxth r8` at `0x703068`): `u16 +0x20c0 * +0x20be * +0x20bf + (+0x20be * +0x20bd + +0x20bc) & 0xff`, low 16 bits. It reads the record with `0x143894(box, 0, index)` (box: GOT `0x1839394` names cell `0x1856fe8`), and every branch writes it back with `0x1431f8(box, 0, index, record)` at `0x7035c0`; an empty record skips the write and only pays.

The smithy row list is a native GUI tree ([Known screens and trees](gui-screens.md#known-screens-and-trees)). `uUIBlackSmith` is 12,824 bytes. Smithy buttons: A 0x2000, B 0x4000, X 0x1000, Y 0x8000; `0x65f808` returns Options (8, or 1 when `sUserInfo+0x446d` is nonzero) and `0x65f830` Help, the reverse; Options is Resort when +0x5c is 2..6 and Show Skills in `0x6f5064` (also read at `0x6f5b50`, `0x6f5bd8`, `0x707884`; 5 of 47 callers read). `0x70a30c` is only the upgrade preview. A row label set through `0x56e808` -> `0x547564` takes a plain `char*` (strlen). Pad menu bits in +0x6c are listed in [Input and actions](input-and-actions.md); no smithy handler, preview slot or cursor mode (table `0x162d0c0`) tests L3 0x2 or R3 0x4, and `0x65f808` starts with PC-relative loads.

**Item limit.** `[[[main+0x18583a8] + 0x1c] + 0x64] - 1` is the loaded `rItemData`'s last ID, the bound lookup `0x192530` uses: 2990 on 1.4.0 (2991 records).

**Loaded smithy tables.** `0x152960(0, file ID)` is the smithy's own lookup (`0x6f0870`): file table `0x15a0ce0`, then the resource manager's find `0xbcba9c` (`sResource` vtable `0x1795948` slot 0x38), which never loads and returns a loaded resource with +0x48 raised, or 0; release through `0x887660` (slot 0x3c, `0xbc8414`), as the window's destructor `0x6f02fc` does. File IDs are `~crc32` of the path: `weaponCreateW..` 0xf4a4.., `armorCreateA00..04` 0xf4b2.., `decoCreate` 0xf4b7, `weaponProcessW..` 0xf4b8.., `armorProcessA00` 0xf4c6 (`arc/facility/blacksmith.arc`, loaded with a town area), `weaponNNBaseData` 0xdde4.. (`loc/arc/resident.arc`). Count +0x64, records at `[+0x6c]`. DTI sizes: `cWeaponCreateData` 44 (`mLv` +4, `mNo` +6, `mItem` +10, `mNum` +18), `cWeaponProcessData` 36 (`mNo` +4, `mLv` +6, `mItem` +8, `mNum` +16), `cArmorCreateData` 48 (`mNo[4]` +4, `mItem` +14, `mNum` +22), `cWeaponNNBaseData` 40 (`mDeriveLv[5]` +28, `mDeriveID[5]` +33; +26/+31 for tables 04 and 06, `cLongWeaponBase`). The loose `nativeNX/table/` files equal the archive entries (47 of 47).

Do not: sum a smithy row's three piece slots into a cost (337 item IDs there, none shared with the 1,733 in the four item slots, and the runtime row has none); read a gear pack at `sPlayer::Instance + 0x7c` (unverified, read `kind=255`).

**Row price and owned count.** A list row's price is its block +0x10 (+0x28e4 + row*0x30); the header fill `0x6f8648` copies it to the display record +8, and the confirm steps (`0x6f44a8`, `0x6f4cb8`, `0x6f536c`) read it into +0x7c. With the table object `0x13c208(type, number)`: the craft list fill (`0x6f56c4`) charges, at row level 0 (+9, from 0), twice slot +0x20 for armor (types up to 5) and v + v/2 for a weapon; above level 0 it charges 1000 for armor and twice +0x158(level, flag, extra) for a weapon, flag and extra being 1 and 0x2134 for type 16 number 47 and type 21 number 26. The upgrade list fill (`0x700180`) charges +0x158(target level) for a weapon and +0x158(current level) for armor (types up to 6), not doubled. A decoration costs its item record's +0x20 (`0x6fdd54`, 200 without a record). Both lists charge 1000 without a table object. The card's owned count (header +6, `0x2d56`) is `0x142de4(box, 0, type, number)`, every level together.

**Kinsects** (bytes; a run confirmed the screen bytes). A kinsect lives in its Insect Glaive's box record, type 20 only: ID at +0x10 (`0xdcb8c`/`0xdcba8`), level at +0x11 counted from 0 (`0xdcbbc`/`0xdcbd8`), stats and attributes at +0x12..+0x25, filled from `cInsectData` by `0xdd7d0`. `cInsectData` (DTI `0x17368c4`, 56 bytes) is `0x13f518(*0x1856b18, id)`: +4 mType, +0x10 mTrgLv, +0x34 mIndex, the name's index in the message table at cell `0x1856b64` (`0xb84114(table, index)`; `insectData_eng.gmd` has 32 names, 20 Bullshroud). The smithy's kinsect screens are state 7 with +0x5c 0x14 and +0x4a 1; the level-up list `0x70181c` writes rows like the upgrade list's (+0x28d6 the ID, +0x28dd target level from 0, price 0, four materials). The level-up itself is `0x70301c` with +0x4a 1: +0x11 raised by one on a copy, bonus fields cleared, written back by `0x1431f8`, then `0x6fbcfc`; the record's +4 and +6 do not change.
