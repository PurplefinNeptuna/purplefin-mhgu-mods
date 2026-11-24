# Start menu, list objects and the page cursor

Bytes unless marked. GUI rows and instances are in [GUI screens](gui-screens.md#known-screens-and-trees), sounds in [Sounds](sounds.md).

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

Opening: on A (`0x66fc30`) slot 0x98 runs, then +0x50 = row, +0x58 = 0, and slot 0x68 runs the page until it returns nonzero. Lobby slot 0x68 jumps by +0x4c. Index 5 goes to the shared `0x676528`, whose open step `0x67655c` clamps the row (`if (+0x50 >= 6) +0x50 = 0`). So a seventh row opens Control Type unless the runner is replaced for it. Rows 0..4 then show page object slot `19 + row` (`0x65cbe8`); row 5 is the Manual. A forced close is +0x38 = 3 in update `0x66ed24`; the base update hides objects 0 and 1 through `0x56dfac` on entering level 3 (that this is "hide" is inference).

Submenu object: slot 2 is `cUIOSMenuSub` (vtable `0x1776488`), wired with +0x54 = menu+0xb0 in the lobby create `0x78f784`. Its slot 0x48 (`0x62c8f0`) binds 7 row panels (instances 0x12..0x18, animation 0x1b), and draw loop `0x62c4d4` shows as many rows as the cursor holds (cursor slot 0x30), reading each enabled byte. A seventh row draws (run).

Page runners by top index (lobby slot 0x68's table at `0x790474`):

| Index | Runner | Index | Runner |
| --- | --- | --- | --- |
| 0 | `0x671954` (Item Pouch) | 8 | `0x7907b4` |
| 1 | `0x671a0c` | 9 | `0x672b98` |
| 2 | `0x67271c` | 10 | `0x67443c` (Equipment) |
| 3 | `0x6728a8` | 11 | `0x674b98` |
| 4 | `0x674e9c` | 12 | `0x790920` |
| 5 | `0x676528` (Hunter's Notes) | 13 | `0x67497c` |
| 6 | `0x7904b4` | 14 | `0x674da0` |
| 7 | `0x790658` | 15 | `0x7909e0` |

Page objects built by the base create (slot 0x48, `0x66e6dc`), by slot:

| Slot | Object | Slot | Object |
| --- | --- | --- | --- |
| 1 | cUIOSMenuDownTop | 0x10 | cUIOPanelCustomize |
| 4 | cUIOItemPouch | 0x12 | cUIOChatFixedPharase |
| 5 | cUIOMix | 0x13 | cUIOHunterNoteStandard |
| 6 | cUIOMixList | 0x14 | cUIOHNActivityMemo |
| 7 | cUIOQuestInfo | 0x15 | cUIOHunterNoteTips |
| 8 | cUIOStatus | 0x16 | cUIOHunterNoteMonsterList |
| 9 | cUIOOtodokeSetStatus | 0x17 | cUIOHunterNoteWeaponGuide |
| 0xa | cUIOEquipList | 0x18..0x1b | their Low panels |
| 0xb | cUIOEquipDetail | 0x1e | cUIOActionList |
| 0xc..0xf | Palico objects | 0x1f | cUIOOptionWindowForGame |

Slot to DTI comes from each create call's GOT load. Page runners show and hide them through `0x65cba0(menu, slot)` / `0x65cbc4`.

Input inside a page: the menu view of `sFestaPad` (pressed +0x6bfc, repeat +0x6c34), page left/right through `0x65f8c4`/`0x65f914` ([Input and actions](input-and-actions.md)).

## Game list objects

The page that owns a list writes each row through `cUIObject` setters (text `0x56e808`, visibility `0x56e530`, colour `0x56e6fc`, number `0x56fde0`, item icon and name `0x56e62c`). The text setter reaches `0x547564`, which `strlen`s a plain `char*`, so any static string works. The generic `cUIOListWindow` (152 bytes) reads only per-row colour bytes from an 8-byte vector at +0x50 and a cursor at +0x54.

## Page cursor

The game's list and page cursor (36 bytes, set up by `0x54ed74`; read in `0x54edec`, `0x54ee34`, `0x54ee98`): `+0xd`
row (u8), `+0xe` rows per page, `+0x10` page (u16), `+0x12` pages (u16), `+0x14` rows (u16), `+0x18` row mode, `+0x1c`
page mode, `+0x20` set to 1 by each setter (inference: a changed flag). `0x54edec(c, rows, row mode, keep)` sets rows and rows per page and, with `keep` 1, clamps the
row to the new count (else row 0). `0x54ee34(c, n, page mode)` sets the row count and the page count and sets the page
to 0. `0x54ee98(c, pad)` moves it and wraps through the cursor's own getter (vtable `+0x2c`), so a count written by
these setters is the one L/R and the D-pad walk. `0x54ecc0(c, page)` sets the page. Screens that page with L/R keep the
page as the row of a one-row-per-page cursor (quest detail panels) or as its page (Quest Info, read through the
cursor's virtual `+0x24`). Owners in [Quest detail pages: counter, quest board, Quest Info](quest-detail-pages.md#quest-detail-pages-counter-quest-board-quest-info).

## In town or in a quest

The main hunter (`sPlayer::getMainPlayer` `0x276278`) is in a village or the hub when its vtable slot 0x360, the add-item, is `0x28806c` (`uPlayerLobby`, vtable `0x1748534`); every `uPlayerQuestNN` has `0x3015e0` there. Its class switching from a quest class to `uPlayerLobby` marks an arrival.
