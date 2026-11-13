# Menus and screens: start menu, Item Pouch, button guide, popups

Game facts WishFinder read from the 1.4.0 bytes to add a start-menu page, guide
buttons and popups. The GUI tree side (rows, instances, atlases) is in
[Native GUI](native-gui.md#known-screens-and-trees); how a plugin adds a page
or a guide entry is in the Forge skill's native GUI extensions ("Reuse a game
screen as a new page", "Button guide and popups"). Copied from
`mods/wishfinder/DEVELOPMENT.md`, whose sections Hooks, Hunter's Notes,
Button guide and Arrival popups stay the mod's own record.

## Entry points

| Site | Function | Arguments | WishFinder's use |
| --- | --- | --- | --- |
| `0x7918d8` / `0x6793d0` | Start menu slot 0x9c, fills the submenu rows: village and hub `uUILobbyStartMenu` (vtable `0x177e424`) / in-quest `uUIQuestStartMenu` (`0x177aeb8`) | this | After: Hunter's Notes row 6 |
| `0x792490` / `0x6786d0` | Slot 0xb0, "has a submenu" for a top index; sizes the submenu cursor | this, top index | After: cursor 6 rows to 7 |
| `0x66fd7c` | Slot 0x8c, the submenu help line, both menus | this | After: row 6's line |
| `0x79119c` / `0x6783bc` | Slot 0x78, the open page's close, run at level 3 by the close-all `0x66ffb4` ((+)); Hunter's Notes' case is `0x678598`, the pouch page's `0x671a04` | this | Before: closes WishFinder's page (`0x188bec`, `release`) |
| `0x790414` / `0x677ee0` | Slot 0x68, runs the open page each frame; 0 stays, 2 goes back | this | Instead, for row 6 only: the WishFinder page |
| `0xbaade4` | `sPad::move`, called each frame only from `sFestaPad::move` `0x3ddf1c` (vtable `0x1754954` slot 0x1c, `bl` at `0x3ddf24`) | pad | After: empties the pad records while the welcome window blocks input |
| `0x782af8` | `uUIQuestCounter` list draw, tail-called by its update `0x781e34` (vtable `0x177e2d4` slot 9); runs the rank, star or quest row builder for the page | counter | After: rank and star row pins |

## Start menu and the Item Pouch screen

The start menu (base `uUIStartMenu`) keeps the top index at `+0x4c` (5 is Hunter's Notes), the chosen submenu row at `+0x50`, the page step at `+0x58`, the submenu rows at `+0xb0` (8-byte {u8 enabled, u32 text} entries, count `+0xb4`, 7 from the base constructor `0x66de60`) and their help lines at `+0xc8` (12-byte entries, flag byte `+4`, count `+0xcc`; its allocation is unread). Slot 0x9c copies one default entry over all seven rows and then writes its own: six for Hunter's Notes, two in the in-quest tutorial mode. WishFinder's fill hook then writes row 6 {1, "WishFinder"} and help flag 0xff, which the submenu help reader `0x66fd7c` (slot 0x8c, run from `0x66f834` at menu level `+0x48` = 1; the lobby's slot is a branch to it) treats as "no help line" (`cmp r1,#255; bxeq lr`) and leaves the previous line up, so WishFinder's hook on it writes the row's own line (`Words::row_help`) when the reader's index, cursor row `+0x109` + page `+0x10a` × rows per page `+0x10c`, is 6; the fill writes row 6 only when rows 5 and 6 differ (six-row mode) and both counts hold 7, because that reader indexes the help array by the cursor row with no bound. The count hook re-sizes the submenu cursor (`+0xfc`, row count u16 at cursor `+0x14`) from 6 to 7 through the game's own `0x670098(menu, rows, 1)`. The page runner opens with +0x58 = 1, stays with 0, and returns 2 on B with the cancel tone; the game's open step `0x67655c` would turn row 6 into row 0 (`if (+0x50 >= 6) +0x50 = 0`), so the original never runs for that row.

The page is the game's Item Pouch screen, start menu slot 4 `cUIOItemPouch` (vtable `0x1770b50`), with the pouch page's controller embedded at menu `+0x220` (vtable `0x173ee50`): WishFinder runs its open `0x1869ec` (cursors, the screen's links into the controller, rows from the pouch, shown) and its close `0x188bec` (hidden), never its step, so nothing reads the pouch after the open. The screen draws its eight rows every frame (slot 0x4c `0x5bb5ac`, then `0x5bb5c4`) from `+0x62 + row*6` = {u16 item, s16 count, u8, u8}: item 0 hides the row's icon and count. Names go through the text setter `0x56e808(screen, row instance, 2, char*)` (instances at `0x1770bb0`), because the game's own fill `0x5bb938` sets a name only when the row's item changed. The title is the `char*` at `+0xb8` (the game's text when 0). The controller's cursor (`+0x220+0xc`) runs as the game's: 8 rows a page (`0x54edec(c, 8, 1, 0)`, row mode 1: D-pad up/down), the list's length (`0x54ee34(c, n, 3)`, page mode 3: D-pad left/right) and its moves `0x54ee98`; the header's `n / N` is that cursor's page. L and R (`0x65f8c4` / `0x65f914`, ZL and ZR when the game's L/R setting swaps them) open the entries with L ("WishFinder": equipment by name with no icon, decorations as items) and the materials with R ("WishFinder Materials": what is owned, pouch plus box); a press on the list already open does nothing. The description window is `+0x9c` (the game's fill shows it through its slot 0x18, sets the item with `0x5ba1b4(window, item, 2)`, places it with `0x5ba2b8(window, node 0 + node 39)` from the screen's GUI positions `0x545a04(screen +0x24, node)`, and hides it through slot 0x1c; byte `+0x18` says shown). The window is shared with other screens, so WishFinder places it on every refill (`place_description`), or it stays where its last user left it: it follows the row, hidden on an equipment row. `0x5bc4a0` / `0x5ba2e8` set that window's Yes/No text, not an item; `0x5bc490` clears it. `+0xb4` is the delivery-and-item window, which a quest's open switches to delivery (`+0x4c` 1); `0x5bc304(screen, 0)` closes it. The help bar is `0x65e5bc(4, 0, file, message, 0, 1, args…)`: CommonMsg 14 is `%s`, so WishFinder passes its own line, as `0x65e67c` does; `0x65e7e4(3, 0)` takes down the Sort guide `0x188aec` puts up. Each row's byte `+0x66` is "usable": normal colours when set, grey when clear. A material row is always usable; an entry is usable when it can be crafted now (the tester's rule: white when craftable, grey when not, independent of the material totals): pouch plus box covers its four materials (`native::KEY_ITEMS`) together with those of every listed step its chain has to make first (`native::KEY_BEFORE`, a 64-bit mask per entry of the listed entries `chains.reaches(entry, step)`, built in `publish_list`). Entry rows read `[C] name` (a craft or a decoration) or `[U] name` (an upgrade, from the key's kind) with ` lvN` for a weapon and for any upgrade, as the panel's level label. An item-0 row has its icon part hidden by the draw; after it, WishFinder shows that part and sets the equipment's own icon through the equipment list's setter `0x56ea38(screen, instance, 1, record, 0, 1)` with a 44-byte record holding only +4 (type, level counted from 0 in bits 5..9) and +6 (number). Entry rows are named with the name stored with the entry (`Entry::name`, published as `native::KEY_NAMES` beside `KEYS`), and the game's lookup only when that is empty: in a quest the equipment names' message table, cell `0x1856b1c`, is 0, and the name virtual (`+0xbc`, armor `0xcf0b8` then `+0x3c` `0xd02c4`: `getMessage(*0x1856b1c, series * 10 + part)`) gives nothing; the r24 run logged 4 of 4 equipment names empty in a quest and 0 of 4 in the village. The name part is also shown after each draw (`0x56e530(screen, instance, 2, 1)`), as the equipment list's own name setter `0x56e810` does. The page's words (menu row, titles, help lines, Remove) follow the game's language, the session's byte `+0xa5` as `cQuestData::getMessage` `0x37a2e4` reads it (2 French, 3 Spanish, 4 German, 5 Italian, 7 Traditional and 8 Simplified Chinese, else English); the translations are WishFinder's own (`native::WORDS`). On the entries list a decoration's count part is hidden after each draw (the draw shows it for any item). A weapon or armor row fills the description window as its own item draw (`0x5ba1e0`, instance 0) would: part 2 the equipment icon (`0x56ea38`), part 6 the stored rarity (`0x56e704`, from the equipment object's virtual `+0x1c`: weapon `+0xf`, armor `mRare +0x73`), part 5 the description (virtual `+0xc0(level)`, beside `+0xbc(level)` the name), parts 3 and 4 hidden, its pending redraw `+0x52` cleared. The description reads the equipment text table at cell `0x1856b1c`, empty in a quest, so `native::cache_descriptions` (from `forge_onUpdate`, once per list change while that cell is set) copies each listed weapon and armor description, 384 bytes, keyed by entry; a quest uses the copies made before it. A on an entry opens the pouch's side menu (screen `+0xa4`, opened and closed by `0x5bc188(screen, show, 0)`, its cursor the controller's second one at `+0x30`, state through `0x54ecc0`) as a one-entry menu: `0x5c5500(list, 1)`, `0x5c55b0(list, 0, "Remove")`, enabled byte `+5` of the first entry of the vector at menu `+0x588`. A there pushes `Request::Remove(key)` (the deny tone for a protected chain step, as the store refuses it), B closes it; the page refills when `GENERATION` changes, keeping the cursor's place. The pouch's open pushes button guide preset 0xb (with Sort); WishFinder sets preset 2 (`0x65e794(2, 1)`), the one the start menu sets for itself, and adds its L and R entries (section Button guide) on every runner step that keeps the page, none while the side menu is open; `release` takes them off. The game colours a count red at the carry limit (`0x550388`, itemData +0xe); an after-hook on `0x5bb5ac` recolours each material count with palette index 3 (red) below what the list needs and 0 (normal) at or above, the pair `0x550388` uses for a usable row, through `0x560e90` and `0x56e6fc(screen, instance, 3, colour)`. B and that hook give the screen back (title 0, blank rows and names), the hook doing it when the screen draws with WishFinder's title but not under WishFinder's page, as after a menu closed under it. The research behind this, and the planned pages, are in `work/wishfinder/PLAN.md`.

## Start menu internals

Static reading from `work/wishfinder/PLAN.md` (Hunter's Notes research); the row, help and page facts were later run in WishFinder.

### Menu objects and rows

Helpers: `work/wishlist/mi.py` (main image words, GOT loads, DTI object to class map), decompiled functions in
`work/wishlist/decomp3a/`, targets in `ghidra-targets-3a.txt`.

Three menu classes share the base `uUIStartMenu` (1,712 bytes, vtable 0x177adac): village and hub `uUILobbyStartMenu`
(0x177e424, 2,048 bytes; the tester's screenshot), in-quest `uUIQuestStartMenu` (0x177aeb8). Constructors store the
vtables at 0x66dc88 (base), 0x78efbc (lobby), 0x677b60 (quest).

| Field | Meaning |
| --- | --- |
| +0x48 | Menu level: 0 top, 1 submenu, 2 second submenu, 3 page open, 4 other |
| +0x4c | Top menu index; 5 is Hunter's Notes (4 Palicoes) |
| +0x50 | Submenu index chosen on A; +0x58 page state, +0x5c page shown |
| +0xa8 / +0xb0 / +0xb8 | Row arrays {u8 enabled, 3 pad, u32 text pointer}, counts at +0xac / +0xb4 / +0xbc. The base constructor allocates the submenu one with 7 entries (`mov r0,#7; str r0,[r4,#0xb4]` at 0x66de60) |
| +0xc0 / +0xc8 / +0xd0 | Help arrays, 12-byte entries {vtable, u8 flag +4, u16 file +6, u16 message +8, u16 0xffff +10} |
| +0xd8, +0xfc, +0x120 ... | Cursors (0x24 bytes each); +0xfc is the submenu's. +0x109 row, +0x10a rows per page, +0x10c page |

Submenu rows. Vtable slot 0x9c fills them (lobby 0x7918d8, quest 0x6793d0): for +0x4c 5, row 0 message 0x212
(Control Type), rows 1..4 messages 14..17, row 5 0x21d (Manual), all file 9 = `StartMenuMsg` (text getter 0x55bc4c),
help messages 544, 117..120, 0x21e. Row 5's enabled byte is `!0x227a98(...)`. Slot 0xb0 (lobby 0x792490) answers
"has a submenu" per top index and sizes the cursor with `0x670098(menu, count, 1)`: index 5 loads `mov r1,#6` at
0x7924f0. Slot 0x98 (0x66fdf8) is "row allowed": the row's enabled byte.

Submenu object: slot 2 is `cUIOSMenuSub` (vtable 0x1776488), wired with +0x54 = menu+0xb0 in the lobby create
0x78f784. Its slot 0x48 (0x62c8f0) binds 7 row panels (instances 0x12..0x18, animation 0x1b), so a 7th row has a
panel. Draw loop 0x62c4d4 shows as many rows as the cursor holds (cursor slot 0x30) and reads each enabled byte.
Inference: count 7 and a filled entry 6 draw a 7th row; no game menu uses 7 submenu rows, so only a run proves it.

Opening. On A (0x66fc30): slot 0x98, then +0x50 = row, +0x58 = 0, slot 0x68 runs the page each frame until it
returns nonzero. Lobby slot 0x68 (0x790414) jumps by +0x4c; index 5 goes to 0x676528 (shared). Its open step
0x67655c clamps the row: `if (+0x50 >= 6) +0x50 = 0`, so a 7th row would open Control Type unless intercepted. Then
rows 0..4 show page object slot `19 + row` (0x65cbe8), row 5 is the Manual.

Page objects the base create (slot 0x48, 0x66e6dc) builds, by slot: 4 cUIOItemPouch, 5 cUIOMix, 6 cUIOMixList,
7 cUIOQuestInfo, 8 cUIOStatus, 9 cUIOOtodokeSetStatus, 0xa cUIOEquipList, 0xb cUIOEquipDetail, 0xc..0xf Palico
objects, 0x13 cUIOHunterNoteStandard, 0x14 cUIOHNActivityMemo, 0x15 cUIOHunterNoteTips, 0x16 cUIOHunterNoteMonsterList,
0x17 cUIOHunterNoteWeaponGuide, 0x18..0x1b their Low panels, 0x1e cUIOActionList, 0x1f cUIOOptionWindowForGame,
1 cUIOSMenuDownTop, 0x10 cUIOPanelCustomize, 0x12 cUIOChatFixedPharase. Slot index to DTI comes from each create
call's GOT load, matched to the class whose getDTI loads the same DTI object (`mi.dti_map`).

Hook plan for the menu row (static): an entry-and-exit hook on lobby slot 0x9c adds entry 6 (label and help) when
+0x4c is 5; one on slot 0xb0 re-sizes the cursor to 7 for index 5; one on slot 0x68 runs the Wishlist page when +0x4c
is 5 and +0x50 is 6, before 0x67655c can clamp it. Label text is a plugin string (row draw takes a `char*`, as the
smithy row label does). Quest menu: same slots (0x6793d0, 0x6786d0, 0x677ee0); the tester wants the row there too.
The full hook table is in the design inputs section below.

### Pages

Page runners, by top index, from lobby slot 0x68's table at 0x790474: 0 0x671954 (Item Pouch), 1 0x671a0c, 2 0x67271c,
3 0x6728a8, 4 0x674e9c, 5 0x676528 (Hunter's Notes), 6 0x7904b4, 7 0x790658, 8 0x7907b4, 9 0x672b98, 10 0x67443c
(Equipment, the tester's image 2), 11 0x674b98, 12 0x790920, 13 0x67497c, 14 0x674da0, 15 0x7909e0. Each returns 0
while the page stays open; +0x58 is its step (0 open, 1 running).

Equipment page (0x67443c, open 0x67450c, cursor change 0x6747c0, detail refresh 0x674880):
- List, slot 0xa `cUIOEquipList` (vtable 0x176e3d4, 464 bytes): rows fixed at 7 (`0x589d48` is `mov r0,#7`).
  `0x589d50(list, param+4)` copies the seven equipped `cFestaEquip` records (44 bytes, `0xdf814` indexes them,
  `0xdadf0` copies into list+0x50+i*44). +0x4c is its cursor (menu+0x168). No paging.
- Detail, slot 0xb `cUIOEquipDetail` (256 bytes): `0x57e938(detail, cursor)`, `0x57e65c(detail, 0)`, then per row
  `0x57f468(detail, record, 0, status, ...)` with a 1,392-byte status block built by 0x26e354 / 0x26e600 / 0x26e580
  and freed by 0x26e50c. Its pages (`1 / 5` in image 2) are menu cursor +0x18c.
- Record-driven, so a wishlist weapon or armor entry could be shown from a synthetic `cFestaEquip` (type, level
  bits, number; vtable copied from a live record). Unread: whether the list or detail reads anything else (box index,
  decorations, owned flags), and how `cFestaEquip`'s constructor sets its vtable.
- Decorations have no `cFestaEquip` form: they are items. The tester's image 3 panel is the Item Box decoration
  screen's, not a start menu object.

Item Pouch page (0x671954): a controller embedded at menu+0x220 runs it (open 0x1869ec, step 0x187000, close
0x188bec) and reads the live pouch. Its header shows `< n / 4 >` and its counts turn red (image 5: the red ones are
items at their carry limit; the rule is unread). Unread: whether it can be pointed at other storage.

Fit against the tester's design:
- Page 1 needs more than 7 rows (up to 64 entries), mixed equipment and decorations, and a decoration panel. No single
  start menu object does that; the list would need paging the game never wrote for it.
- Page 2 needs an item list with "owned / needed" colouring; the pouch controller is the closest, but it is wired to
  the pouch.
- Header with L/R between the two pages: the Equipment Box header (image 4) lives in uUIItemBox, not the start menu.

Decision (the user, 2026-11-09): option 2, the native menu row with the page drawn by Wishlist in ImGui. The user's
words: "way: 2. also for equipent page one, add scrolls so it can put 64 there. paging is for switching between wish
item list, and material list. also the coloring again, follow my coloring, red for not enough, white for enough.
in quest: yes". So: page 1 scrolls through up to 64 entries, L/R switches between page 1 (entries) and page 2
(materials), a material count is red when pouch plus box is below the total needed and white otherwise, and the row
is added to the in-quest menu too. The native-object route (synthetic `cFestaEquip` records into
`cUIOEquipList`/`cUIOEquipDetail`) stays recorded above but is not the plan.

### Page control and input

Page control, static. A page runner returns 0 to stay open and 2 to go back to the submenu (the quest runner's B
path: sound `0x54f260(0, 2)`, return 2); the base update then calls slot 0xb0 and 0x9c again, so the row is re-added.

Input, read in the runner from the pad cell `0x188c670`: pressed +0x6bfc, repeat +0x6c34 (the game ORs `repeat &
0xf0` for the D-pad). B 0x4000 closes; up/down scroll; page left/right are `0x65f8c4()` and `0x65f914()`, which
return L 0x100 / R 0x200, or ZL 0x400 / ZR 0x800 when "L/R Button Controls" swaps them (`sUserInfo+0x446e`). Sounds
through `0x54f260(0, n)`: 2 is cancel (seen); the cursor-move and page-turn numbers are unread.

Sounds: `0x54f260(kind, id)` picks one of five game functions by kind (0 0x4eeb78 with an id: 1 accept, 2 cancel,
3 deny as Wishlist uses; 1 0x4eec94, 4 0x4ef2c4, 6 0x4eed04, which the native cursor 0x54ee98 calls directly).
Which kind is "move" and which "page turn" is inference until a run. The native cursor itself (0x54edec set up,
0x54ee98 move, +0xd row, +0x10 page, +0x12 page count) pages with ZL or the D-pad depending on its mode, so the
Wishlist page keeps its own row and scroll state and uses L/R only to switch pages.

### Game list objects

- Game list objects are passive: the page that owns one writes each row through `cUIObject` setters (text
  `0x56e808`, visibility `0x56e530`, colour `0x56e6fc` with a palette index from `0x560e90`, number `0x56fde0`,
  item icon and name from item data `0x56e62c`). The generic `cUIOListWindow` (152 bytes) reads only per-row colour
  bytes from an 8-byte vector at +0x50 and a cursor at +0x54.
- `cUIOItemPouch` (start menu slot 4, 208 bytes, the tester's image 5) draws its 8 rows every frame from its own array:
  vtable slot 0x4c `0x5bb5ac` runs the base and then `0x5bb5c4`, which for row i reads object +0x62 + i*6 = {u16 item,
  s16 count, u8, u8} and sets icon and name from the item data, the count and the count colour; the title is the
  `char*` at +0xb8 when set (else StartMenuMsg); the cursor is +0x4c. Nothing in it reads the pouch: the controller
  embedded at menu+0x220 (0x1869ec / 0x187000 / 0x188bec) copies pouch slots in. So the native Item Pouch list can
  show any 8 items with counts, under any title.
- Its count colour `0x550388` is red when the count is at or above the item's carry limit (itemData +0xe) or the
  item's +0x17 flag is set, else normal. The tester's rule (red below need) needs a recolour after every refresh: an
  after-hook on `0x5bb5ac`.
- Its child at +0x9c is the description box `cUIOItemExpWindow`; `0x5ba2e8(window, item, 1)` shows any item's icon,
  name, rarity and description. That covers materials and decorations as items, not the decoration panel of image 3
  (slots and skill points), which is an Item Box object.
- Page 1 has no native list that fits: `cUIOEquipList` is 7 fixed rows of equipped gear; the pouch list's rows take
  item data for icon and name, and equipment are not items. Equipment rows in the pouch list need their text and
  icon written after the refresh, and the equipment icon setter is unread (`cUIOEquipList` code, 0x589xxx).
- Equipment detail: `cUIOEquipDetail` (slot 0xb) with a synthetic `cFestaEquip` through `0x57f468(detail, record, 0,
  status, ...)`; the 1,392-byte status block (0x26e354 / 0x26e600 / 0x26e580, freed by 0x26e50c) and the panel's own
  show and page calls are unread.
- Showing objects: page runners show and hide them through `0x65cba0(menu, slot)` / `0x65cbc4`; which of the pouch's
  children (+0xa0..+0xb4: sub-menus, page counter, etc.) must stay hidden without the controller is unread.

### Smithy top menu

`cUIOShopTopPanel` update 0x592ffc loops over exactly 7 panels and shows a row while its index is below the cursor's count;
`shop_top.gui` has `Anm_panel01..07`. The submenu already uses 7. Smithy menu entry calls `0x54edec(+0x1f64, 4, 1, 0)`,
and row 4's confirm currently does nothing (`uVar9 != 3` falls through). The help-text table is indexed by cursor, so
row 4 reads the next table's entry: wrong text, needs a guard.

## Button guide

The guide at the bottom right is UI object 5 of the manager in cell `0x1899458`, reached as every guide wrapper reaches it: `0x65cb3c(0x55d2b4(*cell, 0), 5)` (the wrappers load the cell through GOT word `0x1838bd8`). A preset (`0x65e794(preset, flags)` -> `0x643814` -> `0x6439ec`, presets up to 217, current preset `+0x4c`, flags `+0x50`) fills ten per-button labels at `+0x248` (8 bytes each, -1 for the default text) and clears the four extra entries at `+0x228`: {s32 icon, char* label}, icon -1 for free. `0x65e8cc(icon, label)` puts one in the first free extra (`0x644c34`, nothing when all four are taken or the pair is already there) and lays the guide out again (`0x6439ec(guide, +0x4c, +0x50, 1)`); the layout draws extra 0 lowest and each next one above it, then the per-button labels above those (inference from `0x643ce8`: extras go to positions 3 down, buttons 0..3 from `3 - extras`). The icon is a message id in table 18, `buttonName` (`resident_<lang>.arc`), whose text is the glyph, joined to the label through CommonMsg 13: 4 `PAD_L`, 5 `PAD_R`, 14 `PAD_START`, 15 `PAD_SELECT` (the smithy's Help), 128 `PAD_ZL`, 129 `PAD_ZR`, 130 `ANALOG_LB`, 131 `ANALOG_RB`, 132 `ANALOG_RS`; WishFinder takes 131 for the right stick's click (the glyph is unverified in game). The start menu's own R label (`0x678214`) picks 5 or 129 by `0x65f858`, the L/R swap byte `+0x446e`, and so does WishFinder. No game call drops one extra (`0x6437d8` drops all four), so `native::guide_sync` frees a WishFinder entry by hand (icon -1, label 0) and lays the guide out again with its current preset; it touches only entries whose label is one of WishFinder's own strings (`wishfinder_label`), so the game's Help stays. The smithy hook calls `smithy_guide` after the original each frame: the label shows on the list screens `r3_list` accepts, the same test R3 uses, so under KatSmithy only the upgrade and decoration lists. The page shows the other list's button with `Words::guide`, short labels the guide's width fits.

Per-button labels cannot carry WishFinder's text. The preset record (table `0x1639d5c`, 20 bytes per preset: ten u16) holds a `buttonName` label id in the low byte and the icon in the flags: `0x400` X (id 1), `0x800` Y (id 0), `0x1000` L or ZL, `0x2000` R or ZR (by byte `+0x446c`), `0x4000` id 7, `0x8000` START (14), `0x100` lets slots 0 and 1 show; the word at `+0x248 + 8 * slot` is the UI instance the label draws into, not text (`0x643ebc`). The smithy's weapon forge preset 53 is {`0x11` Back, `0x51a` Toggle Display, `0x927` Skills, `0x815b` Resort}. Slots are laid out 3, 2, 0, 1 from the bottom up, above the extras (`0x6442b0`), so an extra entry always sits below the game's own buttons.

## Centre popup and "in town"

Arrival: the main hunter (`main_player`, as `sPlayer::getMainPlayer` finds it) is in the village or hub when its vtable slot 0x360, the add-item, is `0x28806c` (`uPlayerLobby`, vtable `0x1748534`); every `uPlayerQuestNN` has `0x3015e0` there (both checked by `verify.py`). After 90 updates in a row there (`ARRIVAL_UPDATES`), and only when armed (`NOTICE_ARMED`: set at start-up and whenever the main hunter is a quest hunter, used up by the arrival), `notices_update` (from `forge_onUpdate`) builds one line for each own entry that `craftable` passes and that is not `PROTECTED` (a step a chain target needs; the target itself counts), and hands each to the centre popup, `cUIOInfoWindow` (UI object 1 of the manager in cell `0x1899458`), through the game's type-2 request `0x65ddc4(0, 99, text, 0)`. DialogMsg 99 is `<COL FF0000FF>%s</COL>` in all seven languages, and `text` is formatted into it when the popup builds the line, so the lines are static (`NOTICE_TEXT`) and close the colour after the name: `Defender lv1</COL> is ready to craft.<COL FF0000FF>` (`notice_text`, wording in `Words::notice`, one wording for crafts and upgrades because an upgrade is named by the level it reaches, the name and level as `label` gives them without the tag). A request the game refuses returns -1 and is tried again on the next update; lines not taken when the hunter leaves are dropped. Lines share one popup only inside a group: `0x65dce4` begins one (`0x5b4ba0` sets byte `+0x6c` and empties the head window), each request then adds a line to that window and the seventh is refused (`0x5b4d40`: `count > 5` gives no window), and `0x65dd24` ends it (`0x5b4c44` moves the window to the shown list, nothing for an empty one). The game's own list popup `0x3f0f24` does the same, a header and five lines. Outside a group each request takes a window of its own, one popup per line. WishFinder sends up to six lines (`POPUP_LINES`) per group, one group per update. The popup runs only when `Settings::popup` is on (`native::POPUP`, default on).

## Popups, pouch adds and sounds

Research from `work/wishfinder/NOTICES.md` (bytes, plus the runs named; the popups later shipped in WishFinder).

### The centre popup is cUIOInfoWindow

- UI object 1 of the manager in cell `0x1899458` (`0x65cb3c(0x55d2b4(*cell, 0), 1)`), class
  `cUIOInfoWindow` (vtable `0x17707d8`, size 5848). Its requests are queued: each one is a
  56-byte entry {+0x18 type 1..9, +0x1c flags & 1, +0x20 message id, +0x24.., +0x28 argument};
  one popup holds up to 6 lines (`0x5b4d40`: `count > 5` takes the next window), and further
  requests open the next popup in a linked list. Each call returns a request id, -1 when refused.
- Message ids are DialogMsg (`resident_<lang>.arc`, `table\DialogMsg_<lang>`; in code message
  table 2): with flags 0 the formatter reads it through `0x55bac0(obj, 0, 6, id)`. Verified by
  matching ids: 11 "Your Item Pouch is full.", 12 "%s at maximum.", 71 "Can't receive item: Item
  Box is full.", 29 "Received a new Award!".
- Wrappers (each checks the manager and object, then calls the method):
  `0x65dd68(flags, id, arg)` type 1, plain text, 126 callers; `0x65ddc4(flags, id, arg, x)` type 2,
  `snprintf(fmt(id), arg)` with `arg` stored at +0x28 (the game passes strings: "%s redeemed a
  %s.", "%s increased!"); `0x65de34(flags, id, item, ...)` type 3, item name, swaps 9 -> 10 (×N)
  when the count is above 1; `0x65deac` type 4, equipment name from category and number (via
  `0x13c208`, name virtual +0x3c).
- Formatter: `0x5b41ac` loop over the window's entries, switch on type at `0x5b41b0`, each line
  joined with CommonMsg 14. The argument is read when the line is built, so a string passed in
  must stay valid until the popup shows (a static buffer).
- DialogMsg 99 is `<COL FF0000FF>%s</COL>` in all seven languages. A type-2 request with id 99 and
  the string `NAME</COL> is ready to craft.<COL FF0000FF>` gives a red name and a white rest; the
  game already uses id 99 through types 1 and 8 (`0x3aebb0`, `0x3f0f64`).
- Colour tags are inline: `<COL RRGGBBAA>text</COL>`.
- DialogMsg 115 "New Equipment can be forged at the Smithy!" exists; its id is not a constant
  anywhere (no caller found yet).

### When the game announces things after a quest

- `0x246b1c` queues the post-quest announcements (types 1/2/3/4: HR up 93, Wycademy Points 92,
  Monster List 28, Special Permit 89, "sent to Item Box" 7, shop music 112). Its callers are
  `0x6ce4b8` and `0x6d19e8` (quest result flow).
- Wishlist does not need that call: the popup is a queue, so lines queued on arrival in the
  village or hub follow the game's own. Arrival needs a signal (open: the main player's class
  switching from a `uPlayerQuestNN` to `uPlayerLobby`, vtable `0x1748534`, is the candidate) and
  a retry when the request returns -1 (window not created during loading).

### Items entering the pouch

- `0x19b7fc(pouch, item, amount, flags)` is the shared add (51 callers), calling
  `0x19bbe8(pouch, item, amount, flags)` (`FUN_00b64be8` in the Ghidra DB).
- Player vtable slot 0x360 is the hunter's add: `0x28806c` in `uPlayerLobby` and the base,
  `0x3015e0` in every `uPlayerQuestNN` (checks the quest through `0x3a5ed0(…, 5, …)`, then
  `0x28806c`, then special cases for items 0x83e, 0x844, 0x859). 51 virtual call sites through
  `[vtable + 0x360]`, most of them in `0x2d3000..0x2e0000` (player actions); which of those are
  gathering, carving and fishing is unverified (one at `0x2d38b0` is item use).
- Open: whether another hunter's pickup runs this on the local game (filter by main player).

### Sounds

- `0x54f260(bank, id)`: bank 0..6, each a sound-manager call (bank 0 `0x4eeb78`). Bank 0 ids the
  game uses most: 2 (356 sites), 1, 6, 3, 13, 4, 14, 7, 10, 16, 31, 9, 15, 21, 27, 30; bank 1 ids
  101..194. Which id sounds like what is in the sound data, not the code.

### Sound data

- The menu sounds are `sound\se\system` in `loc/arc/resident.arc`: 36 waves (type `0x79c47b59`),
  bank `snd_sys_com` (SBKR, `0x15d782fb`, 50 entries naming the waves in order, some waves twice)
  and request table `snd_sys_com` (SRQR, `0x1bcc4966`, 57 records of 0x84 bytes from 0x34: u16
  request id at +0, u16 bank entry at +0x12). Request 1 `sys_kettei`, 6 `sys_cancel`, 7
  `sys_bubu`, 3 `sys_box_get`, 14 `sys_mix_success`, 9 `sys_info`, 5
  `sys_saywindow_important`; the full list is reproducible from the two files.
- How `0x54f260(0, n)`'s n becomes a request id is open: `0x4eeb78` only queues n (slot +0x10)
  for `0x887648`. Wishlist's accept 1, cancel 2, deny 3 are the smithy's numbers, not request ids
  (request 2 is `sys_moji`).
- Quest common sounds are `sound\se\com\wav` in `loc/arc/quest.arc` (148 waves).
- Waves: mono DSP-ADPCM; +0x10 a build date, +0x18 16 LE s16 coefficients, +0x60 nibble count,
  +0x64 sample rate (48000), data from +0x78 in 8-byte frames. `sound-samples/dsp2wav.py ARC
  PREFIX OUTDIR` decodes them; `sound-samples/system/` and `sound-samples/quest_common/` hold the
  decoded WAVs.

### Pickup jingles (the sound to replace)

- `sSoundControl` (DTI vft `0x17696a0`): `mpResSeSys` +0xc0 (menu bank `snd_sys_com`),
  `mpResSeJingle` +0xc8. `0x4eeb78(sound, n)` queues n on +0xc0 with no table, so menu sound n is
  likely `snd_sys_com` request id n (1 `sys_kettei`, 2 `sys_moji`, 3 `sys_box_get`): inference,
  unheard.
- The pickup jingles are the realtime jingles, one per `arc/sound/rt_jNN.arc` (`sound\rt_j%02d`,
  built by `0x15339c`): 01 `item_non`, 02 `item_gets`, 03 `item_gets02`, 04 `katamari`, 05
  `egg_get`, 06 `egg_lost`, 07 `mix`, 08 `fish_get`, 09 `trophy`, 10 `retire`.
- `0x4eef00(sound, kind)` queues a jingle by pickup kind: 0 -> 2 `item_gets`, 1 -> 3
  `item_gets02`, 2/3/130/131 -> 4 `katamari`, 4 -> 5 `egg_get`, anything else nothing.
  `0x4eede8(sound, id, arg)` queues any jingle id (the shop music passes id + 11).
- Its four callers (`0x2d55e0`, `0x2d5688`, `0x2d5734`, `0x2d5778`) are the hunter's item-get
  pose, a switch on the kind at player +0x32d8 (0..4); `| 0x80` when player byte +7 is clear.
  The item itself is added earlier, through player slot 0x360, so a replacement needs the
  last-added item from that add (a hook on `0x3015e0`) consumed at the jingle (a hook on `0x4eef00`).
- Waves are mono or stereo (byte 4 = channels; stereo data interleaved in 0x100-byte blocks); the
  jingles are stereo at 44.1 or 48 kHz. `sound-samples/jingles/` holds them decoded; `retire`
  still decodes silent.

### The gather jingle is not code-driven (MHGU Recomp runs)

- r37 (MHGU Recomp): a needed Shiny Beetle gathered in a quest logged no `0x4eef00` call. r39: the same
  gather logged no call of the quest hunter's add-item `0x3015e0` either; the only add in that quest was
  `item=16 amount=-1` (an item used). So gathering adds through another path (likely the shared pouch
  add `0x19b7fc`, unverified) and plays its jingle without `0x4eef00`.
- Only three functions queue a jingle in `sSoundControl`'s request slots (kind byte 2): `0x4eede8`
  (one caller, shop music id + 11), `0x4eee68` (one caller, fixed id 1), `0x4eef00` (the item-get pose).
  The gather jingle is therefore requested elsewhere, most likely by the motion's sound events (data,
  `sound\call\pl`) straight to the sound system.
- r39 saw no new entry in the request slots at +0xec during the quest (they may be taken within the
  frame); the realtime slots at +0x9ec change constantly, and their +0xc is a running handle, not a
  sound number.

### The pouch add sees gathering; menu sound 43 is silent

- Gathering in a quest reaches `0x19b7fc` with the main hunter's pouch (17 adds logged, `item=392 amount=1
  needed=true` among them), so the needed-pickup test works there.
- `0x54f260(0, 43)` played nothing the tester heard. Either n is not the `snd_sys_com` request id, or request
  43 (`lb_sys_chat_reception`, an `lb_` lobby sound) does not play in a quest. The inference that
  `0x54f260(0, n)` plays request n is unsupported.

### Popup groups: several lines in one popup

- Outside a group every request takes a window of its own, so each line is its own popup: `0x5b4d40` with byte
  `+0x6c` clear takes the head of the free list (`+0x16b4`, count `+0x16bc`) and moves it to the shown list.
- `0x65dce4` (no arguments) begins a group: `0x5b4ba0` sets `+0x6c` and empties the head window. Requests then add
  lines to that window; the seventh is refused (`count > 5` returns no window, the wrapper -1). `0x65dd24` ends it:
  `0x5b4c44` clears `+0x6c` and moves the window to the shown list, nothing for a window with no lines.
- The game's own list popup `0x3f0f24` uses the pair: begin, DialogMsg 101 as a header, up to five id-99 lines
  (`0x65e078`), end. Other begin/end callers: `0x27851c` / `0x278aa4`.

### Leads from Faster Field Hunter (unverified in our main)

Read from that third-party mod's code (`work/wishfinder/POPUP_PLAN.md`); check each in the bytes before use.

- It queues item lines through `0x5b521c(window, 0, 9, item, ...)` (message 9, an item name) and keeps each request id, the window's counter +0x58 & 0x3ff, in a 32-slot ring; each frame it takes the shown window (+0x70, id at +8) and acts when that id is in the ring and within 64 of the counter.
- Window timing floats at +0x64/+0x68 (hold, early; meaning open); a pane's x/y +0x90/+0x94 and scale +0xa0/+0xa4, a root's x/y +0x40/+0x44.
- Popup icons are `cUIOPopIcon` (DTI `0x189e698`, vtable from `0x1774710 + 0x70`): a `cUIObjectSetupParam` block (`0x570688`) with +0x38 = 0x4000000, +0x3c = 0 and a word from `0x163e4a0`, created by `0x65c1e0(parent, dti, param, 0x202)` (parent through `0x183a954`), the block destroyed with `0x570688 + 0x88`. Slot +0x54 is normally `0x60eba0`.
