# Item Pouch and Equipment screens

## Item Pouch screen

`cUIOItemPouch`, start menu slot 4 (vtable `0x1770b50`, 208 bytes), with the pouch page's controller embedded at menu +0x220 (vtable `0x173ee50`): open `0x1869ec` (cursors, the screen's links into the controller, rows copied from the pouch, shown), step `0x187000`, close `0x188bec` (hidden). Nothing in the screen reads the pouch, so running open and close without the step leaves it showing whatever rows are written.

- Rows: drawn every frame (slot 0x4c `0x5bb5ac`, then `0x5bb5c4`) from +0x62 + row*6 = {u16 item, s16 count, u8 usable (+0x66 for row 0), u8}; item 0 hides the row's icon and count. Exactly eight row instances. The game's fill `0x5bb938` sets a name only when the row's item changed.
- Title: the `char*` at +0xb8 (the game's `StartMenuMsg` text when 0). Cursor +0x4c.
- Cursor: the controller's at +0x220+0xc, 8 rows a page (`0x54edec(c, 8, 1, 0)`, row mode 1: D-pad up/down), length `0x54ee34(c, n, 3)` (page mode 3: D-pad left/right), moves `0x54ee98`; the header's `n / N` is its page. A second cursor at +0x30 belongs to the side menu (state through `0x54ecc0`).
- Count colour `0x550388`: red at or above the item's carry limit (itemData +0xe) or with its +0x17 flag, else normal; palette index from `0x560e90` (3 red, 0 normal).
- Description window +0x9c (`cUIOItemExpWindow`, shared with other screens):
  - Shown through its slot 0x18 and hidden through slot 0x1c; byte +0x18 says shown.
  - Item set with `0x5ba1b4(window, item, 2)`. `0x5ba2e8(window, item, 1)` shows any item's icon, name, rarity and description.
  - Placed with `0x5ba2b8(window, node 0 + node 39)` from the screen's GUI positions `0x545a04(screen+0x24, node)`. A shared window stays where its last user put it. `0x5bc4a0` sets its Yes/No text; `0x5bc490` clears it. The item draw is `0x5ba1e0` (instance 0).
- Side menu +0xa4, opened and closed by `0x5bc188(screen, show, 0)`; a one-entry menu is `0x5c5500(list, 1)` then `0x5c55b0(list, 0, text)`, enabled byte +5 of the first entry of the vector at menu +0x588.
- +0xb4 is the delivery-and-item window (a quest's open switches it to delivery, +0x4c 1); `0x5bc304(screen, 0)` closes it. Children +0xa0..+0xb4 (sub-menus, page counter) without the controller are unread.
- Help bar: `0x65e5bc(4, 0, file, message, 0, 1, args…)`; CommonMsg 14 is `%s`, so a plain string can be passed, as `0x65e67c` does. The second argument is the message group, passed through `0x6429a4` to `0x55bac0(manager, group, file, message)`. Group 0 holds CommonMsg (file 1). Group 1 holds the smithy's tables, and its Yes/Nos pass `0x14, 1, 14, …`; there file 1 message 14 reads "HR 3+" (run). `0x65e7e4(3, 0)` takes down the Sort guide `0x188aec` puts up. The pouch's open pushes guide preset 0xb (with Sort); the start menu's own is preset 2.
- Equipment in rows: equipment are not items, so an equipment row needs its text and icon written after each draw.
  - Icon: the equipment list's setter `0x56ea38(screen, instance, 1, record, 0, 1)`, with a 44-byte record holding only +4 (type, level from 0 in bits 5..9) and +6 (number).
  - Name: shown with `0x56e530(screen, instance, 2, 1)`, as the equipment list's own setter `0x56e810` does.
  - Rarity: `0x56e704`.
  - Equipment names and descriptions read the text table at cell `0x1856b1c`, which is 0 in a quest (armor name virtual: `0xcf0b8`, then +0x3c `0xd02c4` = `getMessage(*0x1856b1c, series * 10 + part)`).

## Equipment page

`0x67443c` (open `0x67450c`, cursor change `0x6747c0`, detail refresh `0x674880`).

- List, slot 0xa `cUIOEquipList` (vtable `0x176e3d4`, 464 bytes): rows fixed at 7 (`0x589d48` is `mov r0,#7`). `0x589d50(list, param+4)` copies the seven equipped `cFestaEquip` records (`0xdf814` indexes them, `0xdadf0` copies into list+0x50+i*44). +0x4c is its cursor (menu+0x168). No paging.
- Detail, slot 0xb `cUIOEquipDetail` (256 bytes): `0x57e938(detail, cursor)`, `0x57e65c(detail, 0)`, then per row `0x57f468(detail, record, 0, status, ...)` with a 1,392-byte status block built by `0x26e354` / `0x26e600` / `0x26e580` and freed by `0x26e50c`. Its pages are menu cursor +0x18c. Labels and getters: `0x57f5ac` ([Equipment stats, decorations and skills](equipment-stats.md#equipment-stats-decorations-and-skills)).
- Record-driven, so a synthetic `cFestaEquip` could be shown; unread whether list or detail reads anything else. Decorations have no `cFestaEquip` form, and the Item Box decoration panel is not a start-menu object.

## Items entering the pouch

`0x19b7fc(pouch, item, amount, flags)` is the shared add (51 callers), calling `0x19bbe8` (`FUN_00b64be8` in Ghidra).

Player vtable slot 0x360 is the hunter's add. It is `0x28806c` in `uPlayerLobby` and the base, and `0x3015e0` in every `uPlayerQuestNN`. That one checks the quest through `0x3a5ed0(…, 5, …)`, then calls `0x28806c`, then handles items 0x83e, 0x844, 0x859 specially. There are 51 virtual call sites through `[vtable + 0x360]`, most in `0x2d3000..0x2e0000` (player actions; one at `0x2d38b0` is item use).

Gathering in a quest reaches `0x19b7fc` with the main hunter's pouch but not `0x3015e0` (run). Whether another hunter's pickup runs either on the local game is open.

The popup formatter (`0x5b41f0`) reads a line's message with `0x55bac0(manager, group, table, id)`. Request flags 0 is group 0 table 6, `DialogMsg_<lang>`. Flags 1 is group 2 table 2, `QuestDialog_<lang>` (`quest_<lang>.arc`; checked: 74 is the fish popup "You caught a %s!"). The lookup is `[[manager + 0x5c] + group * 4]`, then the table at index.

Pickups go through the hunter's get-item `0x2e04d4` ([Jingles](jingles.md)), which adds through slot 0x364 (`0x2880b4` in `uPlayerLobby`, `0x301784` in every `uPlayerQuestNN`), reaching `0x19c2a0`.

That function calls `0x19b7fc` at `0x19c320` and turns its result into the item popup (`0x65de34`, DialogMsg ids). It does so when its flags (r2) have bit 0; the get-item passes 7 for a fish, else 3.

| Result | Meaning | Popup id |
| --- | --- | --- |
| 0, 1 | added | 9 "obtained."; bit 2 instead gives 74 "You caught a %s!", bit 3 71 "You made a %s.", bit 4 72 "No! It became a %s.", all with request flags 1 |
| 2 | added to the maximum | 12 "at maximum." |
| 3 | stack at its maximum; in a village or the hub the add tries the box (`0x19945c`) | 12 "at maximum." in a quest |
| 5 | no free slot. A carried item (`0x1943bc`) gives popup 15; in a village or the hub the add tries the box. Otherwise (a quest) `0x19c494` calls `0x670500(item, amount)`, which a tester saw as the prompt to swap a pouch item (inference: `0x670500` unread). The item taken after the swap is added through `0x19b7fc` (run: a WishFinder hook there saw it) | 15 "You cannot carry any more items." for a carried item |
| 6 | | 17 "sent to Item Box." |
| 7 | not the main hunter, or the quest check `0x3a5ed0(…, 5, 1)` refuses | |
