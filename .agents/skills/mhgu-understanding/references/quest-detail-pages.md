# Quest detail pages

## Quest detail pages: counter, quest board, Quest Info

Bytes, and run in all four places. Each keeps its page
as a page cursor ([Page cursor](start-menu.md#page-cursor)) and draws only the game's pages.

**Detail panel** (`cUIOQuestCounterDetail`, vtable `0x1774a24`, 92 bytes, layout `counter_down.gui`). Page fills
`(detail, page, cQuestData, bool)`: 1 `0x613170`, 2 `0x613954`, 3 `0x613c48`, each first running `0x612fe8` (hides the
page groups 7, 0, 1, 36, 9) and the header `0x6135fc` (name, kind, map; stores the quest at detail `+0x50`). Instance
map in [Known screens and trees](gui-screens.md#known-screens-and-trees). Other users of the class, not examined: `0x68e920` (a list
screen) and the start menu's `0x67ae24`.

- **At the receptionist** (village and hub): the quest list controller (`0x54d030`'s object; the hub's at counter
  `+0x13dc`) holds the detail at `+0x50` and its cursor at `+0x28` (row byte `+0x35` = page), sized to 3 rows with
  `0x54edec(list+0x28, 3, 9 or 0, 0)` at `0x54b8d0`, `0x54d008`, `0x54d99c`, on events: a quest change keeps the row
  (run). Dispatcher `0x54d674(list, info, mode)` every frame from the hub list draw `0x782af8`
  (`0x782e58`) and the village (`0x6e3350`, `0x6e4478`): quest `0x39b848(word(info+0x38+4*s16(info+8)), 0)`
  (`rQuestData::getData`), bool `byte(info + s16(info+8) + 0x1154)`; rows 0..2 fill, others draw nothing; it ends with
  `0x613d8c(detail, mode == 1 && info+1 == 1)`, which sets instances 2, 0x40, 0x3e by detail `+0x58` and that test.
- **At the multiplayer quest board** (`uUIQuestBoard`, vtable `0x177e280`, 20,272 bytes, constructor `0x77e060`):
  cursor `+0x1370` (row `+0x137d`) sized `0x54edec(+0x1370, 3, 9, 0)` at `0x77f76c`; detail `+0x13b8`, joined players'
  panel `+0x13c4`. Draw `0x780bc4(board, show)`: selector `*0x188ae38`, slot `+0x1359`, quest ID `0x3bf718(selector,
  slot)`, `cQuestData` `0x3b9fd4(selector, id)`, bool `0x523da4(*0x1897f78 + 0x42c, id)`; it draws only when
  `0x3be79c(selector)` is non-null with a non-zero word at `+slot*0x2858` and bit `s8 +0x13cc` of `selector+0x1e6` clear.
  Row 0 the players' panel, rows 1 and 2 the detail's pages 1 and 2, each showing one object (vtable `+0x20`) and hiding
  the other (`+0x24`).

**Quest Info** (`cUIOQuestInfo`, vtable `0x1774b1c`, 280 bytes, layout `menu_questconfirm.gui`): start menu page
object 7 and its only owner (there is no Quest Info at the counter; the start menu's help line for it reads "Check the
status and conditions of the Quest at hand."). Runner `0x6728a8` (step `+0x58`: 1 open `0x672930`, 0 run `0x672ae8`)
from the lobby page runner `0x790480` and the quest one `0x677fa4`. Open: cursor at menu `+0x18c`, `0x54edec(c, 1, 3, 0)`
then `0x54ee34(c, G, 3)`; G 3 in town (`0x3f8678(*0x188ca48)` true: window `+0x4c` 1, quest `0x3bd96c(*0x188ae38)`, the
accepted quest) or 4 in a quest (`+0x4c` 0, status page first; filled from `sQuest`). Run: `0x54ee98(menu+0x18c, pad)`,
then the draw `0x614b14(window)`: page from the cursor's virtual `+0x24`; `0x614c7c` resets the groups (shows 0, hides
6, 8, 0xb, 0xc, 0xe, 0x18); mode 0 pages 0 status (0xc, or 0x18 when `+0x50` is 3), 1 objectives (6/7), 2 monsters
(8/9), 3 client and summary (0xb/10); mode 1 pages 0..2 are the last three.

**The running quest in a quest.** `sQuest` (`*0x188ad90`) `+0xa4` (`mpQuestData`) is the running quest's `cQuestData`
itself: `sQuest::initQuest` reads `mQuestTime` (+0x12) from it at `0x3abc44`; `+0xa0` (`mpQuestDataRes`) is the
resource. Passing `+0xa4` to `rQuestData::getData` reads quest ID 0 (run). `cQuestData +8` is
`mQuestNo` (DTI).
