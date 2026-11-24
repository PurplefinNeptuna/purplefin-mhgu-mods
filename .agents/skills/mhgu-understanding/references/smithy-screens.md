# Smithy top menu and list screens

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
row. A fifth row fits the label block.

The list screen (state 3; `research dis`). The list object (slot 2, `cUIOFacilityShopMenu`, update `0x58b908`, reached
only from vtable `0x176e8ac` slot 0x4c through `0x58b8f0`) rewrites its header every frame: pane 5 text 1 through
`0x56fc58`, a message from the 12-byte table entry picked by header byte `+0x2d5d`. Pane 16 is the kind 2 card
(below); its texts 5 and 4 are the "Displaying" label and filter, which `0x58cb8c` sets only when header byte `+0x2d51`
has 0x20 (label table 2 id 67). Visibility is `0x56e528(object, pane, shown)`. The equipment panel (slot 5,
`cUIOEquipDetail`) pages with its own cursor at window `+0x1f88` (bound by `0x57e938`): the list handler steps it with
the repeat word only when the row cursor's step answers no 0xf0 bit (`0x6f48f0`), then redraws the preview
(`0x6f9b18(window, 0)`). The list fill sizes it (`0x6f57f4`): pages `0x57edac(record, 0, 0x8048)` for the sPlayer
(`0x1885b58`) gear entry `0xdf814(0x277454(sPlayer) + 4, 0xdae68(type))`, then `0x54edec(+0x1f88, pages, 5, 0)`;
cursor mode 5 reads 0x100/0x200 (L and R), modes 2 and 3 read 0x80/0x20 (stick left and right), table `0x162d0c0`. Mode 7 reads 0x80000/0x20000. The preview `0x6f9b18` re-sizes that cursor every time it runs, with mode 5, or 7 while the smithy's +0x3a is set. The call is `0x552988(status, 0, cursor, flags, mode, 1)`: page count `0x57edac` of the shown item, page kept. A screen of its own that keeps L and R writes mode 5 (+0x18) back after it.
`0x57e65c(panel, mode)` picks the panel's arrow icons: entering a list sets 1 (L and R, `0x6f2d60`), the decoration
screens 2 (the stick). Both stay as the last screen left them, so a screen of one's own sets them. Slot 7 (`cUIOShopSmithType`) is the "Currently: Blademaster/Gunner" box.

The card under the rows shows the selected entry's icon, name, rarity and owned count. `0x58c754` draws it from the list update, only while bit 3 of the header block's flags +0xc (window +0x2d5c) is clear (`0x58c04c`). It shows the pane of the block's kind +2 when the selected row's display flags (+6) are nonzero and bit 0 is clear. Kinds 0..4 use panes 15, 28, 16, 29, 31 (table `0x1630630`).

The lists set bit 3 in their other states (`0x6f2cb8`, `0x6f32e4`, `0x6f45bc`) and clear it on each selection (`0x6f4318`, before `0x6f8648`). `0x6f8648` writes kind 2 and +1 = 0x20 for types 2..6, kind 1 for type 1 and weapons; the decoration header `0x6f8a08` writes kind 2 and 0x20, so armor below the head and decorations share pane 16. Guide preset 0x34,
which the lists set, is {0x11, 0x10, 0x1a, 0x27} in table `0x1639d5c`; preset 2 is {0x11, 0x10}.
