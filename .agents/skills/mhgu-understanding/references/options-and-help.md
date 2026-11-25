# Options window and Help

## Options window

Start menu object 31 is `cUIOOptionWindowForGame` (vtable `0x1772c88`, 144 bytes; base `cUIOOptionWindowBase` `0x1772b0c`, siblings ForChat `0x1772bc8` and ForNetwork `0x1772d48`), built by the base create at `0x66ebf0`.

Options is top index 14 in the village/hub menu and 10 in a quest. Both runners call the Options runner `0x674da0` (callers `0x7904ac`, `0x677f64`). It opens the window with `0x56de60`, stays while window +0x80 is 1, and hides it with `0x56dfac`. The forced close is `0x674e7c` (callers `0x7912f8`, `0x678574`).

Sizers (slot 0xb0) give submenus only to lobby indices 4..11 and quest 4..5.

- **Update**: base `0x5e5840` is slot 0x4c of the base, ForChat and ForNetwork. ForGame's slot 0x4c is its own `0x5e7000`. It tail-calls the base update while byte +0x85 is 0 (open and close write 0), and runs its own sequence at 10.
  - State +0x74 is 1 while browsing: row +0x59 u8, page +0x5c u16, 8 rows a page, cursor +0x4c in row mode 1 Up/Down and page mode 3 Left/Right. A describes the row (slot 0x68) and edits it (state 2). For kinds 5/6/7, A instead opens a yes/no popup whose yes calls slot 0x78/0x7c/0x80.
  - In editing, every frame describes the row (slot 0x68) and reads get (slot 0x6c). Left/Right step the value between record min/max and call **slot 0x74 set at once**. The step wraps when the record says so, and slot 0x70 gates it. Left/Right are menu-pressed +0x6bfc bits 0x80 `0x5e5a24` / 0x20 `0x5e5a2c`; there is no repeat word, so holding does not repeat. A keeps the value. The cancel branch `0x5e60d8` calls slot 0x74 with the value get gave on A (+0x7c).
  - B while browsing sets +0x80 = 2. The base update itself opens confirm popups by position for any subclass: page 2 rows 6/7 and page 3 row 0 in editing. Slot 0x90 redraws when +0x78 bit 0 is set; slot 0x94 runs every update, at the very end of the base update after its input and redraw (`0x5e62bc`; base: empty).
  - Every store of a new state +0x74 goes through `0x5e6274`, which then calls slot 0x84 (this, page, row, record); ForGame's is empty (`0x5e69cc`).
  - A in browsing (menu bit 0x2000, `0x5e5920`) plays tone 1, sets the cursor's mode with `0x54ecc0(+0x4c, 1)` and the dirty bit (`0x5e5cb0`), describes the row, stores get's value in +0x7c and stores state 2; leaving editing sets `0x54ecc0(+0x4c, 0)` (`0x5e5bcc`).
  - Browsing moves the cursor on `pressed | repeat` (`0x5e58d8`..`0x5e58e8`), so Up and Down repeat when held; editing steps only on pressed. Page turning wraps: Right on the last page shows the first (run, 4 pages).
- **ForGame slots**:
  - 0x60: rows = 27
  - 0x64: title StartMenuMsg 23
  - 0x68: describe(record, page, row) `0x5e7558`
  - 0x6c: get(page, row)
  - 0x74: set(page, row, record, value)
  - 0x90: `0x5e87d0` = base redraw `0x5e635c`, then the help bar line
  - 0x88: empty
  - 0x98, 0x9c: return 0
  - 0xa0: returns 1
  - Open/close (0x18/0x1c) copy session `0x188ca48` +0x5d to +0x72.
- **Row record** (0x50 bytes, on the caller's stack): +0 name `char*`, +4 kind, +8 u8 wrap, +0xa u16 min, +0xc u16 max, +0xe u8 label count, +0x10 sixteen `char*`.
  - The base redraw describes and reads get for every row (`0x5e65e0`, `0x5e660c`). It draws through the plain-string text setter. Kinds 0..4 take StartMenuMsg texts by value. Kind 8 shows `label[value]` when value <= 15 and value < count (`0x5e673c`), else a default text.
  - On the edited row both arrows show when wrap is set, else the left one while value != min and the right one while value != max (`0x5e67d0`..`0x5e6840`). A copy of the vtable with these slots replaced shows any rows (run).
- **No disabled rows**: no slot or record field greys a row or refuses A. Slot 0x70 (page, row) only gates Left/Right in editing (`0x5e5df0`, `0x5e5ee4`; ForGame's `0x5e69b4` returns 1).
  - The redraw draws page row n into GUI instance `[3, 4, 5, 6, 9, 10, 11, 12][n]` (table `0x16256bc`, loaded at `0x5e6474`): the name as part 1 (`0x5e662c`), the value as part 2 (`0x5e67ac`). It sets no colour.
  - A text part's colour goes through `0x54700c(gui, instance, part, colour)`. For a `cGUIObjMessage` or `cGUIObjText` part it calls the DTI `Color` setter `0xa530bc(holder, &colour)`, which stores the u32 at holder +0xbc and asks for a redraw; the getter is `0xa530b0(out, holder)`.
- **L/R**: `0x65f8c4`/`0x65f914` return the menu-pad bits 0x100/0x200, or 0x400/0x800 when the shoulder swap byte +0x446e is set; the cursor mover `0x54ee98` uses them only in modes 4, 5, 9 and 10.

## Help

`cUIOHelp` (vtable `0x176fe04`, 200 bytes) is UI-manager object 7, opened by `0x65ed60(category, topic)` -> `0x5ab188(help, category, topic, 1)`; topic `0xffff` opens the topic grid, any other value that topic's pages.

Mode +0x4c:

- 0: grid of 8 `cUIOHelpPanel`s, 2 columns x 4 rows, page +0x94.
- 1: pages.
- 2: pages for category 0, with a picture (instance 24, sequence from table `0x1631974`, clamped at entry 24).
- 0xff: closed.

Switch `0x5aa968`, close `0x5aaa7c`, grid fill `0x5ab7c0`. Page draw is `0x5ababc` / `0x5abc94`: title instance 0x11 part 2, body instance 0x14 through `0x56fac8`, both plain-string setters.

Its page view stops at a topic's first and last page; it does not wrap (run).

- **Data**: table `0x176fd0c` holds 19 relocated pointers in the data segment. Each points to a 12-byte category record {u16 table, u16 name id, u8 topic count, u8, u16 body table, topic*}. Topics are 16 bytes in rodata: {u16 title table, u16 title id, u16 head table, u16 head id, u16 first page id, u8 page count, u8, u32 lock kind}.
  - Lock kinds 1..6 are progress checks that show "???". Text is `0x55bac0(obj, category > 1, table, id)`: table 4 `LbHelp`, 11 `CommonHelpMsg`. The grid's size comes from the count byte at open. All eight code readers of the table are inside cUIOHelp (`0x5ab20c..0x5abd78`).
- **Categories** with a constant opener:
  - 0, 1: `0x67079c`, `0x6714b8` (start menu panel screens)
  - 2: `0x796c48`
  - 3: `0x713e04`
  - 8: `0x7318bc`
  - 9: `0x6dd274`
  - 13: `0x1b8404`
  - 14: `0x1af14c`
  - 16: `0x778d24` (Courier)
  - 18: `0x793250` (Village/Hub, 10 topics; "Settings & Search" is LbHelp 102, pages 363..367)
  - 25 call sites in all.
