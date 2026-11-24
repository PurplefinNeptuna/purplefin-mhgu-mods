# Quest counter pages and rows

## Counter pages and their rows

Bytes; row decorations built on these rules were seen working in a run.

**Counter.** `uUIQuestCounter` (vtable `0x177e2d4`): update slot 9 `0x781e34` runs the state dispatcher `0x781e60`, then the list draw `0x782af8` for states 1..2; draw slot 18 `0x781bb0`. State byte +0x3c: 0 rebuild (`0x783074` re-runs the rows, plays sound 121, moves to state 1), 1 rank page, 2 star page, 5 quest list (meanings upstream). Native writes are `strh`, so +0x3d clears with it. The village counter is the same class; `0x6e3f64` belongs to `uUIArenaCounter` (vtable `0x177d7e4`). `info` is counter +0x3c.

**Row builders** (`cUIOQuestList`, vtable `0x1774b98`, holder +0x24, reached as `0x65cb3c(counter, 2)`). The list draw switches on the list's kind byte +0x3c (1..11): 5, 7, 11 quest rows (`0x54d030` -> `0x616cb0`); 1 rank rows `0x616164`; 2..4 star rows `0x616574` (after reading eight row bytes +0x9d..+0xa4: 255 empty; 13, 14, 16 special); 8 `0x6176d4`, 9 `0x617a7c`, 10 `0x617dd8`. Rank and star pages draw with `counter.gui` animation 1 ([Known screens and trees](gui-screens.md#known-screens-and-trees)).

**Rank rows.** Five: label `info+0x1171+row` (0 Low, 1 High, 2 G Rank, 3 Special Permit, 4 Training, 5 Hunt of the Day, 6 hidden; a village shows `[4 0 1 5 6]`, the pub `[0 1 2 3 5]`), flag `info+0x116c+row` (0 locked: the confirm refuses it). The confirm `0x7838c0` maps a label to star code `info+0x59`: Low 0 in a village, 1 at hub and pub (`0x508924(_, 2)`); High 2 or 3; G 4; Special Permit goes to page 17, Training 14, Hunt of the Day 19 (list 23). The rebuild `0x783074` decides which rank rows light: at the hub it checks codes 3 (High) and 4 (G, when `0x5078e4` allows), elsewhere the village's code 2, each through the star-slot test `0x784964`, then the Special Permit groups and list 23. So a row the game lights has at least one available quest.

**Star codes.** `0x78484c(counter, code, u8 rows[8])` (pure apart from `rows`) writes the star page's normal rows from the s8 {min, max} pair at `0x162cdc5 + 4 * code`, max capped per code (0 -> 5, 1 -> 3, 2 -> 10, 3 -> 7, 4 -> 14), stopping at the first slot `0x784964` refuses, and returns the count. `0x784964` needs the slot's unlock bit and one quest of list `0x1650a2f[s]` (= s + 1) passing `0x54af8c(q, 0xff, 0)`.

| Code | Slots | Stars | Unlock bit in the save block +0x500 |
| --- | --- | --- | --- |
| 0 | 0..5 | Village 1..6 | Slot 0 always; `0x1650a70[s-1]` = 10, 15, 24, 28, 33 |
| 1 | 0..2 | Hub Low 1..3 | Slot 0 always; `104 + 4(s-1)` |
| 2 | 6..9 | Village 7..10 | `0x1650a70[s-1]` = 1008, 1025, 1035, 1052 |
| 3 | 3..6 | Hub High 4..7 | `104 + 4(s-1)` |
| 4 | 10..13 | G 1..4 | `0x159775c[s-10]` = 1400, 1405, 1409, 1413 |

**Star page** `0x783b48(counter, info, flag)`: rows `info+0x61..+0x68` (255 empty), count `info+0x60`; normal rows from `0x78484c(counter, info+0x59, rows)`, then two special rows from the byte table (GOT at `0x783bd8`) `[code * 4 + 2..3]`: 15 (Event, codes 1, 3, 4) and 14 written as is, 16 (urgent) only when the urgent pool `info+0x1104` (count `info+0x1144`, at most 16) holds an available, uncleared quest.

**Urgent pool** per code: index `[0, 2, 1, 3, 4][code]` (`0x1650aa0`), 16 IDs at `selector + 104 + 64 * i`, count u16 at `selector + 424 + 2 * i`; shown when available and not cleared (`0x523da4([0x1897f78] + 0x42c, quest)` is 0). **Special Permit**: 18 groups of up to 16 IDs at `0x3bc9e0(selector, i)` (`[selector + 0x1b4] + 64 * i`), counts u16 at `selector + 440 + 2 * i`, kept by `0x54af8c`.

**Which quests a page lists.** `0x54b994(ctrl, info, page, mode, first)` fills one page of eight quest rows (`page*8 .. page*8+7`) and returns how many quests passed; callers `0x54b834` (village `0x6e4554`, hub `0x782108`/`0x782268`) and the counter's step `0x54c130` (`0x54ca08`/`0x54ca30`). List number = row byte + 1, with remaps: 14 -> 20 + `info+0x1177`; 15 -> 15, 16 or 17 by rank code 1, 3 or 4 (the per-rank Event row); 16 -> the urgent pool (counts filled slots `info+0x1104..0x1140`); 19 -> 23. `mode == 1` picks from `0x121312 >> (8 * info+0x1176)` instead. The catalogue is the selector (its cell is loaded at `0x54bb78`): `0x3bc9f8(mgr, list)` is the count (u16 at `mgr + 0x38 + list*2`); `0x3bc96c(mgr, list)` (list < 24) gives a 396-byte record of 99 u32 quest IDs at `[mgr+0x34] + 396 * idx`, idx an s8 from a 24-byte row chosen by the area type (0..7); negative idx gives 0. A quest is kept only when available, the `0x54af8c(quest, category, info)` test: category 14 with `info+0x1177 == 1` needs `0x3bd150` to equal `info+0x11e6` (inference: Hunt of the Day group); `0x3b9870` passes event/DLC IDs (millions digit 1); otherwise `0x3b2174(quest)` -> `0x3d7e90(mgr, &out, quest)`, the progression query (cached per quest at +0x8e0, count +0x8dc, top bit the answer), must be 1; then a special encounter entry's enable bit decides. This is what hides a 4-star quest whose chain hasn't started.
