# Menus and screens: start menu, Item Pouch, button guide, popups

Game facts read from the 1.4.0 bytes for WishFinder's Hunter's Notes page and Purple-lib's Mod Options,
guide buttons and arrival popups. The GUI tree side (rows, instances,
atlases, part setters) is in [Native GUI](native-gui.md#known-screens-and-trees);
sounds are in [Sounds](sounds.md); how a plugin adds a page or a guide entry is
in the Forge skill's native GUI extensions ("Reuse a game screen as a new
page", "Button guide and popups"). WishFinder's own use of each fact is in
`mods/wishfinder/DEVELOPMENT.md` (Hooks, Hunter's Notes, Button guide, Arrival
popups); its research notes are `work/wishfinder/PLAN.md` and `NOTICES.md`.

## Start menu

Three classes share the base `uUIStartMenu` (1,712 bytes, vtable `0x177adac`): village and hub `uUILobbyStartMenu` (`0x177e424`, 2,048 bytes) and in-quest `uUIQuestStartMenu` (`0x177aeb8`). Constructors store the vtables at `0x66dc88` (base), `0x78efbc` (lobby), `0x677b60` (quest).

| Field | Meaning |
| --- | --- |
| +0x48 | Menu level: 0 top, 1 submenu, 2 second submenu, 3 page open, 4 other |
| +0x4c | Top menu index; 5 is Hunter's Notes (4 Palicoes) |
| +0x50 | Submenu row chosen on A; +0x58 page step (0 open, 1 running), +0x5c page shown |
| +0xa8 / +0xb0 / +0xb8 | Row arrays {u8 enabled, 3 pad, u32 text pointer}, counts +0xac / +0xb4 / +0xbc. The base constructor `0x66de60` sizes the submenu array to 7 (`mov r0,#7; str r0,[r4,#0xb4]`) |
| +0xc0 / +0xc8 / +0xd0 | Help arrays, 12-byte entries {vtable, u8 flag +4, u16 file +6, u16 message +8, u16 0xffff +10}; the +0xc8 count is +0xcc, its allocation unread |
| +0xd8, +0xfc, +0x120 ... | Cursors, 0x24 bytes each; +0xfc is the submenu's (row count u16 at cursor +0x14). For it +0x109 row, +0x10a page, +0x10c rows per page |

| Slot | Lobby / quest | Role |
| --- | --- | --- |
| 0x9c | `0x7918d8` / `0x6793d0` | Fill the submenu rows: copies one default entry over all seven, then writes its own. Hunter's Notes: row 0 message 0x212 (Control Type), rows 1..4 messages 14..17, row 5 0x21d (Manual), file 9 `StartMenuMsg` (text getter `0x55bc4c`), help 544, 117..120, 0x21e; row 5 enabled is `!0x227a98(...)`. The in-quest tutorial mode gives 2 rows (`0x3ae744() == 1`) |
| 0xb0 | `0x792490` / `0x6786d0` | "Has a submenu" per top index; sizes the cursor with `0x670098(menu, count, 1)`; index 5 loads `mov r1,#6` at `0x7924f0` |
| 0x98 | `0x66fdf8` | "Row allowed": the row's enabled byte |
| 0x8c | `0x66fd7c` (the lobby's slot branches to it) | Submenu help line, run from `0x66f834` at level 1. It indexes the help array by cursor row with no bound, and a flag of 255 means "no help line" (`cmp r1,#255; bxeq lr`), leaving the previous line up |
| 0x78 | `0x79119c` / `0x6783bc` | Close the open page; run at level 3 by close-all `0x66ffb4` (+). Hunter's Notes' case is `0x678598`, the pouch page's `0x671a04` |
| 0x68 | `0x790414` / `0x677ee0` | Run the open page each frame: returns 0 to stay, 2 to go back to the submenu (B path: `0x54f260(0, 2)`, return 2), after which the base update calls slots 0xb0 and 0x9c again |

Opening: on A (`0x66fc30`) slot 0x98 runs, then +0x50 = row, +0x58 = 0, and slot 0x68 runs the page until it returns nonzero. Lobby slot 0x68 jumps by +0x4c; index 5 goes to the shared `0x676528`, whose open step `0x67655c` clamps the row (`if (+0x50 >= 6) +0x50 = 0`), so a seventh row opens Control Type unless the runner is replaced for it. Rows 0..4 then show page object slot `19 + row` (`0x65cbe8`); row 5 is the Manual. A forced close is +0x38 = 3 in update `0x66ed24`; the base update hides objects 0 and 1 through `0x56dfac` on entering level 3 (that this is "hide" is inference).

Submenu object: slot 2 is `cUIOSMenuSub` (vtable `0x1776488`), wired with +0x54 = menu+0xb0 in the lobby create `0x78f784`. Its slot 0x48 (`0x62c8f0`) binds 7 row panels (instances 0x12..0x18, animation 0x1b), and draw loop `0x62c4d4` shows as many rows as the cursor holds (cursor slot 0x30), reading each enabled byte. A seventh row draws (run in WishFinder).

Page runners by top index (lobby slot 0x68's table at `0x790474`): 0 `0x671954` (Item Pouch), 1 `0x671a0c`, 2 `0x67271c`, 3 `0x6728a8`, 4 `0x674e9c`, 5 `0x676528` (Hunter's Notes), 6 `0x7904b4`, 7 `0x790658`, 8 `0x7907b4`, 9 `0x672b98`, 10 `0x67443c` (Equipment), 11 `0x674b98`, 12 `0x790920`, 13 `0x67497c`, 14 `0x674da0`, 15 `0x7909e0`.

Page objects built by the base create (slot 0x48, `0x66e6dc`), by slot: 1 cUIOSMenuDownTop, 4 cUIOItemPouch, 5 cUIOMix, 6 cUIOMixList, 7 cUIOQuestInfo, 8 cUIOStatus, 9 cUIOOtodokeSetStatus, 0xa cUIOEquipList, 0xb cUIOEquipDetail, 0xc..0xf Palico objects, 0x10 cUIOPanelCustomize, 0x12 cUIOChatFixedPharase, 0x13 cUIOHunterNoteStandard, 0x14 cUIOHNActivityMemo, 0x15 cUIOHunterNoteTips, 0x16 cUIOHunterNoteMonsterList, 0x17 cUIOHunterNoteWeaponGuide, 0x18..0x1b their Low panels, 0x1e cUIOActionList, 0x1f cUIOOptionWindowForGame. Slot to DTI comes from each create call's GOT load (`work/wishfinder/mi.py` `dti_map`). Page runners show and hide them through `0x65cba0(menu, slot)` / `0x65cbc4`.

Input inside a page: the menu view of `sFestaPad` (pressed +0x6bfc, repeat +0x6c34), page left/right through `0x65f8c4`/`0x65f914` ([Input and actions](input-and-actions.md)).

## Options window

Start menu object 31 is `cUIOOptionWindowForGame` (vtable `0x1772c88`, 144 bytes; base `cUIOOptionWindowBase` `0x1772b0c`, siblings ForChat `0x1772bc8` and ForNetwork `0x1772d48`), built by the base create at `0x66ebf0`. Options is top index 14 in the village/hub menu and 10 in a quest; both runners call the Options runner `0x674da0` (callers `0x7904ac`, `0x677f64`), which opens the window with `0x56de60`, stays while window +0x80 is 1 and hides it with `0x56dfac`; the forced close is `0x674e7c` (callers `0x7912f8`, `0x678574`). Sizers (slot 0xb0) give submenus only to lobby indices 4..11 and quest 4..5.

- **Update**: base `0x5e5840` is slot 0x4c of the base, ForChat and ForNetwork; ForGame's slot 0x4c is its own `0x5e7000`, which tail-calls the base update while byte +0x85 is 0 (open and close write 0) and runs its own sequence at 10. State +0x74: 1 browsing (row +0x59 u8, page +0x5c u16, 8 rows a page, cursor +0x4c in row mode 1 Up/Down and page mode 3 Left/Right); A describes the row (slot 0x68) and edits (state 2) or, for kinds 5/6/7, opens a yes/no popup whose yes calls slot 0x78/0x7c/0x80. In editing, every frame describes the row (slot 0x68) and reads get (slot 0x6c), then Left/Right (menu-pressed +0x6bfc bits 0x80 `0x5e5a24` / 0x20 `0x5e5a2c`, no repeat word, so holding does not repeat) step the value between record min/max (wrapping when set; slot 0x70 gates the step) and call **slot 0x74 set at once**; A keeps, the cancel branch `0x5e60d8` calls slot 0x74 with the value get gave on A (+0x7c). B while browsing sets +0x80 = 2. The base update itself opens confirm popups by position for any subclass: page 2 rows 6/7 and page 3 row 0 in editing. Slot 0x90 redraws when +0x78 bit 0 is set; slot 0x94 runs every update, at the very end of the base update after its input and redraw (`0x5e62bc`; base: empty). Every store of a new state +0x74 goes through `0x5e6274`, which then calls slot 0x84 (this, page, row, record); ForGame's is empty (`0x5e69cc`). A in browsing (menu bit 0x2000, `0x5e5920`) plays tone 1, sets the cursor's mode with `0x54ecc0(+0x4c, 1)` and the dirty bit (`0x5e5cb0`), describes the row, stores get's value in +0x7c and stores state 2; leaving editing sets `0x54ecc0(+0x4c, 0)` (`0x5e5bcc`). Browsing moves the cursor on `pressed | repeat` (`0x5e58d8`..`0x5e58e8`), so Up and Down repeat when held; editing steps only on pressed. Page turning wraps: Right on the last page shows the first (seen in Purple-lib's Mod Options, 4 pages, on Eden and MHGURecomp).
- **ForGame slots**: 0x60 rows = 27, 0x64 title StartMenuMsg 23, 0x68 describe(record, page, row) `0x5e7558`, 0x6c get(page, row), 0x74 set(page, row, record, value), 0x90 `0x5e87d0` = base redraw `0x5e635c` then the help bar line; 0x88 empty, 0x98/0x9c return 0, 0xa0 returns 1. Open/close (0x18/0x1c) copy session `0x188ca48` +0x5d to +0x72.
- **Row record** (0x50 bytes, on the caller's stack): +0 name `char*`, +4 kind, +8 u8 wrap, +0xa u16 min, +0xc u16 max, +0xe u8 label count, +0x10 sixteen `char*`. The base redraw describes and reads get for every row (`0x5e65e0`, `0x5e660c`), draws kinds 0..4 from StartMenuMsg texts by value and kind 8 as `label[value]` when value <= 15 and value < count (`0x5e673c`), else a default text, through the plain-string text setter. On the edited row both arrows show when wrap is set, else the left one while value != min and the right one while value != max (`0x5e67d0`..`0x5e6840`). A copy of the vtable with these slots replaced shows any rows (Purple-lib, `mods/purple-lib/DEVELOPMENT.md`).
- **L/R**: `0x65f8c4`/`0x65f914` return the menu-pad bits 0x100/0x200, or 0x400/0x800 when the shoulder swap byte +0x446e is set; the cursor mover `0x54ee98` uses them only in modes 4, 5, 9 and 10.

## Help

`cUIOHelp` (vtable `0x176fe04`, 200 bytes) is UI-manager object 7, opened by `0x65ed60(category, topic)` -> `0x5ab188(help, category, topic, 1)`; topic `0xffff` opens the topic grid, any other value that topic's pages. Mode +0x4c: 0 grid (8 `cUIOHelpPanel`s, 2 columns x 4 rows, page +0x94), 1 pages, 2 pages for category 0 (with a picture: instance 24, sequence from table `0x1631974`, clamped at entry 24), 0xff closed; switch `0x5aa968`, close `0x5aaa7c`, grid fill `0x5ab7c0`, page draw `0x5ababc` / `0x5abc94` (title instance 0x11 part 2, body instance 0x14 through `0x56fac8`, both plain-string setters). Its page view stops at a topic's first and last page; it does not wrap (seen on Purple-lib's added topics, Eden and MHGURecomp).

- **Data**: table `0x176fd0c`, 19 relocated pointers in the data segment, to 12-byte category records {u16 table, u16 name id, u8 topic count, u8, u16 body table, topic*}; topics are 16 bytes in rodata {u16 title table, u16 title id, u16 head table, u16 head id, u16 first page id, u8 page count, u8, u32 lock kind (1..6 progress checks show "???")}. Text is `0x55bac0(obj, category > 1, table, id)`: table 4 `LbHelp`, 11 `CommonHelpMsg`. The grid's size comes from the count byte at open. All eight code readers of the table are inside cUIOHelp (`0x5ab20c..0x5abd78`).
- **Categories** with a constant opener: 0 `0x67079c` and 1 `0x6714b8` (start menu panel screens), 2 `0x796c48`, 3 `0x713e04`, 8 `0x7318bc`, 9 `0x6dd274`, 13 `0x1b8404`, 14 `0x1af14c`, 16 `0x778d24` (Courier), 18 `0x793250` (Village/Hub, 10 topics; "Settings & Search" is LbHelp 102, pages 363..367). 25 call sites in all.

## Item Pouch screen

`cUIOItemPouch`, start menu slot 4 (vtable `0x1770b50`, 208 bytes), with the pouch page's controller embedded at menu +0x220 (vtable `0x173ee50`): open `0x1869ec` (cursors, the screen's links into the controller, rows copied from the pouch, shown), step `0x187000`, close `0x188bec` (hidden). Nothing in the screen reads the pouch, so running open and close without the step leaves it showing whatever rows are written.

- Rows: drawn every frame (slot 0x4c `0x5bb5ac`, then `0x5bb5c4`) from +0x62 + row*6 = {u16 item, s16 count, u8 usable (+0x66 for row 0), u8}; item 0 hides the row's icon and count. Exactly eight row instances. The game's fill `0x5bb938` sets a name only when the row's item changed.
- Title: the `char*` at +0xb8 (the game's `StartMenuMsg` text when 0). Cursor +0x4c.
- Cursor: the controller's at +0x220+0xc, 8 rows a page (`0x54edec(c, 8, 1, 0)`, row mode 1: D-pad up/down), length `0x54ee34(c, n, 3)` (page mode 3: D-pad left/right), moves `0x54ee98`; the header's `n / N` is its page. A second cursor at +0x30 belongs to the side menu (state through `0x54ecc0`).
- Count colour `0x550388`: red at or above the item's carry limit (itemData +0xe) or with its +0x17 flag, else normal; palette index from `0x560e90` (3 red, 0 normal).
- Description window +0x9c (`cUIOItemExpWindow`, shared with other screens): shown through its slot 0x18, item set with `0x5ba1b4(window, item, 2)` (`0x5ba2e8(window, item, 1)` shows any item's icon, name, rarity and description), placed with `0x5ba2b8(window, node 0 + node 39)` from the screen's GUI positions `0x545a04(screen+0x24, node)`, hidden through slot 0x1c; byte +0x18 says shown. A shared window stays where its last user put it. `0x5bc4a0` sets its Yes/No text; `0x5bc490` clears it. The item draw is `0x5ba1e0` (instance 0).
- Side menu +0xa4, opened and closed by `0x5bc188(screen, show, 0)`; a one-entry menu is `0x5c5500(list, 1)` then `0x5c55b0(list, 0, text)`, enabled byte +5 of the first entry of the vector at menu +0x588.
- +0xb4 is the delivery-and-item window (a quest's open switches it to delivery, +0x4c 1); `0x5bc304(screen, 0)` closes it. Children +0xa0..+0xb4 (sub-menus, page counter) without the controller are unread.
- Help bar: `0x65e5bc(4, 0, file, message, 0, 1, args…)`; CommonMsg 14 is `%s`, so a plain string can be passed, as `0x65e67c` does. `0x65e7e4(3, 0)` takes down the Sort guide `0x188aec` puts up. The pouch's open pushes guide preset 0xb (with Sort); the start menu's own is preset 2.
- Equipment in rows: equipment are not items, so an equipment row needs its text and icon written after each draw: icon through the equipment list's setter `0x56ea38(screen, instance, 1, record, 0, 1)` with a 44-byte record holding only +4 (type, level from 0 in bits 5..9) and +6 (number); name part shown with `0x56e530(screen, instance, 2, 1)` as the equipment list's own setter `0x56e810` does; rarity `0x56e704`. Equipment names and descriptions read the text table at cell `0x1856b1c`, which is 0 in a quest (armor name virtual: `0xcf0b8`, then +0x3c `0xd02c4` = `getMessage(*0x1856b1c, series * 10 + part)`).

## Equipment page

`0x67443c` (open `0x67450c`, cursor change `0x6747c0`, detail refresh `0x674880`).

- List, slot 0xa `cUIOEquipList` (vtable `0x176e3d4`, 464 bytes): rows fixed at 7 (`0x589d48` is `mov r0,#7`). `0x589d50(list, param+4)` copies the seven equipped `cFestaEquip` records (`0xdf814` indexes them, `0xdadf0` copies into list+0x50+i*44). +0x4c is its cursor (menu+0x168). No paging.
- Detail, slot 0xb `cUIOEquipDetail` (256 bytes): `0x57e938(detail, cursor)`, `0x57e65c(detail, 0)`, then per row `0x57f468(detail, record, 0, status, ...)` with a 1,392-byte status block built by `0x26e354` / `0x26e600` / `0x26e580` and freed by `0x26e50c`. Its pages are menu cursor +0x18c. Labels and getters: `0x57f5ac` ([Equipment and crafting](equipment-and-crafting.md#equipment-stats-decorations-and-skills)).
- Record-driven, so a synthetic `cFestaEquip` could be shown; unread whether list or detail reads anything else. Decorations have no `cFestaEquip` form, and the Item Box decoration panel is not a start-menu object.

## Game list objects

The page that owns a list writes each row through `cUIObject` setters (text `0x56e808`, visibility `0x56e530`, colour `0x56e6fc`, number `0x56fde0`, item icon and name `0x56e62c`). The text setter reaches `0x547564`, which `strlen`s a plain `char*`, so a plugin's static string works. The generic `cUIOListWindow` (152 bytes) reads only per-row colour bytes from an 8-byte vector at +0x50 and a cursor at +0x54.

## UI objects outside their screen

A game window is a `cUIObject` class with its own layout file, and the game can make one from any screen. Read in bytes and run by WishFinder r82 on Eden and MHGU Recomp (village, hub and quest); notes in `work/wishfinder/REQ_MATERIALS.md`.

- **Finding the class.** `./scripts/tool.sh research find cUIO --kind dti` lists the UI classes with size, vtable and parent; a screen's objects are in its create (slot 0x48) as `0x65ca84(screen, slot, DTI, setup, flags)` calls. The class's vtable gives getDTI (slot 0x14), the resource picker (0x28), bind (0x48) and draw (0x4c). A DTI object's name is the `char*` at `+4`, which a plugin compares before using the address.
- **Factory.** `0x65c1e0(*0x18a1cd8, DTI, setup, flags)` is what `0x65ca84` calls: object from the DTI, resource (slot 0x28) when `setup` is 0, a GUI holder (`0x65c2e4`: the holder whose `+0xf0` is the same resource is reused, else a new 0x2b0-byte one is registered), shown `+0x18 = 1` unless flag 8, bind unless flag 4. It returns 0 when the object has no resource. Show `0x56de60`, hide `0x56dfac`; destroy through the deleting destructor, vtable slot 4, which detaches from the holder and releases the resource.
- **Resource.** Slot 0x28 picks a file ID by the session language (`[*0x188ca48]+0xa5`, English past Italian) and calls `0x56e1a8`, which only finds a loaded resource (`0x152960`). The game's file table `0x15a0ce0` holds {`~crc32` of the path without extension, the DTI's `mID`} per ID, so a path can be checked against an ID offline. A layout loaded only inside one facility (the smithy's) is absent elsewhere and the factory returns 0.
- **Loading it.** `sResource::create(*0x2126a64, DTI, path, 1)` `0xbcad18` loads by path, blocking, under the same key the lookup uses; `rGUI`'s DTI object is `0x212619c`. The layouts are loose files too (`nativeNX/<lang>/GUI/...gui`), and the load works with the facility's archive closed, in a quest as well. Release the extra reference with `0xbc8414(manager, resource)` once the object holds its own.
- **Draw gate.** The holder draws an object (`0x56e2d8`, message 1) when it is shown and the mode word `[*0x1899458]+0x1a4` is 0 or the object's mask `+0x20` has that bit. The word read 0 on the Hunter's Notes page and a new object's mask 0.
- **Texts.** `0x55bc7c(*0x1899220, file, id)` returns 0 when message file `file` is not loaded; file 14 (shop) is loaded in the village and hub and not in a quest. The text setters `0x56ea08` / `0x56e808` reach `0x547564`, which clears the text for a null `char*`, so a missing text is blank, not a fault.
- **Example, `cUIOShopCmnWindow`** (the smithy's four-row Req. Materials window: vtable `0x176e640`, DTI `0x189a7d8`, 84 bytes, layout `<lang>\GUI\04_lobby\shop\shop_cmn_win`, file IDs `0xf4cd` + 3 per language): draws while `+0x50 & 1` and clears it; reads four records behind the pointer at `+0x4c`, record i at `+4 + i*0x14` {u32 colour, u16 icon, u8 present, u16 needed at +8, u16 owned at +0xa, u32 0, `char*` name}; owned below needed turns the row red; titles are file 14 ids 0x1d and 0x99 into instance 1 parts 1 and 2. The smithy fills the block in `0x6fa3d8` (colour `0x560d3c(palette, itemData +0x19, 1)`, icon itemData `+0x18`). The three-row upgrade variant is `cUIOShopSmithMaterial` (`0x176ef7c`, layout `shop_prcsn`).

## Smithy top menu

`uUIBlackSmith` state 1 (`0x6f1ae8` case 1). Labels: block at window `+0x2d14` (byte style 7 for the top menu, 8..10 for
submenus; u16 `+0x2d16` 0 top, 1 submenu), then `{u32 flags, char* text}` rows at `+0x2d18 + row*8`, room for 7 before
`+0x2d50`; the open `0x6f0f84` fills four from table 14 (`LbShop_EqMakeMsg`) ids at `0x1630988`: 1, 16, 22, 23.
`cUIOShopTopPanel` update `0x592ffc` (`shop_top.gui`, `Anm_panel01..07`) shows panels while the index is below the
cursor's rows on the page, sets each text through `0x56e808` (plain `char*`) and greys a row with flag bit 1. The cursor
is `+0x1f64`; `0x54edec(cursor, rows, mode, keep)` keeps the row (clamped) only with `keep` 1. The only writers of
state 1 (every byte store to `+4` in `0x6f0000..0x70c000` checked) are the open, B from a submenu and the return from
Upgrade Equipment, and each sets four rows with `0x54edec(+0x1f64, 4, 1, 0)`. A stores `page * rows + row` in `+0x4c`:
0, 1, 3 open a submenu, 2 Upgrade Equipment, any other index does nothing. Cursor moves call the help bar with
`{u16 message, s16 kind}` from `0x16500cc` by row: 61, 73, 80, 112, then 62 "Select a weapon category." for a fifth
row. Source: `work/wishfinder/SMITHY_MENU_FINDINGS.md`. WishFinder r86 adds a fifth row this way; whether the fifth
panel lays out cleanly has not run.

## Button guide

UI object 5 of the manager in cell `0x1899458`, reached as every guide wrapper does: `0x65cb3c(0x55d2b4(*cell, 0), 5)` (the wrappers load the cell through GOT word `0x1838bd8`).

- **Presets.** `0x65e794(preset, flags)` -> `0x643814` -> `0x6439ec`; presets up to 217, current preset +0x4c, flags +0x50. A preset fills ten per-button slots at +0x248 (8 bytes each, -1 for default text) and clears the four extra entries at +0x228. The preset record (table `0x1639d5c`, 20 bytes: ten u16) holds a `buttonName` label id in the low byte and the icon in the flags: `0x400` X (id 1), `0x800` Y (id 0), `0x1000` L or ZL, `0x2000` R or ZR (by `sUserInfo+0x446c`), `0x4000` id 7, `0x8000` START (14), `0x100` lets slots 0 and 1 show. The word at +0x248 + 8 * slot is the UI instance the label draws into, not text (`0x643ebc`), so custom text cannot go in a per-button slot. The smithy's weapon forge preset 53 is {`0x11` Back, `0x51a` Toggle Display, `0x927` Skills, `0x815b` Resort}.
- **Extras.** Four {s32 icon, char* label} entries, icon -1 free. `0x65e8cc(icon, label)` puts one in the first free extra (`0x644c34`; nothing when all four are taken or the pair is already there) and lays the guide out again (`0x6439ec(guide, +0x4c, +0x50, 1)`). No game call drops one extra (`0x6437d8` drops all four).
- **Layout.** Extras draw lowest, extra 0 at the bottom (inference from `0x643ce8`: extras take positions 3 down, buttons 0..3 from `3 - extras`); per-button slots are laid out 3, 2, 0, 1 from the bottom up above them (`0x6442b0`).
- **Icons.** The icon is a message id in table 18, `buttonName`; IDs and the swap byte are in [Input and actions](input-and-actions.md#button-names-and-icons).

## Centre popup

UI object 1 of the same manager, `cUIOInfoWindow` (vtable `0x17707d8`, 5848 bytes).

- **Requests** are queued 56-byte entries {+0x18 type 1..9, +0x1c flags & 1, +0x20 message id, +0x28 argument}. Each call returns a request id, -1 when refused (also while the window is not created during loading: retry next update).
- **Messages** are DialogMsg (`resident_<lang>.arc` `table\DialogMsg_<lang>`, message table 2 in code), read with flags 0 through `0x55bac0(obj, 0, 6, id)`. Checked ids: 11 "Your Item Pouch is full.", 12 "%s at maximum.", 71 "Can't receive item: Item Box is full.", 29 "Received a new Award!", 115 "New Equipment can be forged at the Smithy!" (no caller found). 99 is `<COL FF0000FF>%s</COL>` in all seven languages; the game uses it through types 1 and 8 (`0x3aebb0`, `0x3f0f64`). Colour tags are inline `<COL RRGGBBAA>text</COL>`.
- **Wrappers** (each checks manager and object): `0x65dd68(flags, id, arg)` type 1, plain text, 126 callers; `0x65ddc4(flags, id, arg, x)` type 2, `snprintf(fmt(id), arg)` with `arg` at +0x28; `0x65de34(flags, id, item, ...)` type 3, an item name, 9 -> 10 (xN) for a count above 1; `0x65deac` type 4, an equipment name from category and number (via `0x13c208`, name virtual +0x3c).
- **Formatter** `0x5b41ac` loops over a window's entries (switch on type at `0x5b41b0`), joining lines with CommonMsg 14. The argument is read when the line is built, so a string passed in must stay valid until the popup shows.
- **Groups.** Outside a group each request takes a window of its own (`0x5b4d40` with byte +0x6c clear takes the head of the free list +0x16b4, count +0x16bc, and moves it to the shown list), so one popup per line. `0x65dce4` begins a group (`0x5b4ba0` sets +0x6c and empties the head window); requests add lines to that window and the seventh is refused (`count > 5`); `0x65dd24` ends it (`0x5b4c44` clears +0x6c and moves the window to the shown list; nothing for an empty one). The game's list popup `0x3f0f24` does the same: DialogMsg 101 as a header, up to five id-99 lines (`0x65e078`). Other begin/end callers: `0x27851c` / `0x278aa4`.
- **After a quest** `0x246b1c` queues the announcements (types 1..4: HR up 93, Wycademy Points 92, Monster List 28, Special Permit 89, "sent to Item Box" 7, shop music 112), called from `0x6ce4b8` and `0x6d19e8`. Lines queued on arrival in town follow the game's own.

## In town or in a quest

The main hunter (`sPlayer::getMainPlayer` `0x276278`) is in a village or the hub when its vtable slot 0x360, the add-item, is `0x28806c` (`uPlayerLobby`, vtable `0x1748534`); every `uPlayerQuestNN` has `0x3015e0` there. Its class switching from a quest class to `uPlayerLobby` marks an arrival; WishFinder waits 90 updates in a row there before using the popup.

## Items entering the pouch

`0x19b7fc(pouch, item, amount, flags)` is the shared add (51 callers), calling `0x19bbe8` (`FUN_00b64be8` in Ghidra). Player vtable slot 0x360 is the hunter's add: `0x28806c` in `uPlayerLobby` and the base, `0x3015e0` in every `uPlayerQuestNN` (checks the quest through `0x3a5ed0(…, 5, …)`, then `0x28806c`, then special cases for items 0x83e, 0x844, 0x859); 51 virtual call sites through `[vtable + 0x360]`, most in `0x2d3000..0x2e0000` (player actions; one at `0x2d38b0` is item use). Gathering in a quest reaches `0x19b7fc` with the main hunter's pouch but not `0x3015e0` (MHGU Recomp runs). Whether another hunter's pickup runs either on the local game is open.

## Leads from Faster Field Hunter (unverified in our main)

Read from that third-party mod's code (`work/wishfinder/POPUP_PLAN.md`); check each in the bytes before use.

- It queues item lines through `0x5b521c(window, 0, 9, item, ...)` (message 9, an item name) and keeps each request id, the window's counter +0x58 & 0x3ff, in a 32-slot ring; each frame it takes the shown window (+0x70, id at +8) and acts when that id is in the ring and within 64 of the counter.
- Window timing floats at +0x64/+0x68 (hold, early; meaning open); a pane's x/y +0x90/+0x94 and scale +0xa0/+0xa4, a root's x/y +0x40/+0x44.
- Popup icons are `cUIOPopIcon` (DTI `0x189e698`, vtable from `0x1774710 + 0x70`): a `cUIObjectSetupParam` block (`0x570688`) with +0x38 = 0x4000000, +0x3c = 0 and a word from `0x163e4a0`, created by `0x65c1e0(parent, dti, param, 0x202)` (parent through `0x183a954`), the block destroyed with `0x570688 + 0x88`. Slot +0x54 is normally `0x60eba0`.
