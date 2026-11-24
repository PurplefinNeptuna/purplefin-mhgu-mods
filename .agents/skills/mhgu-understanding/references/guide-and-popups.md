# Button guide and centre popup

## Button guide

UI object 5 of the manager in cell `0x1899458`, reached as every guide wrapper does: `0x65cb3c(0x55d2b4(*cell, 0), 5)` (the wrappers load the cell through GOT word `0x1838bd8`).

- **Presets.** `0x65e794(preset, flags)` -> `0x643814` -> `0x6439ec`; presets up to 217, current preset +0x4c, flags +0x50. A preset fills ten per-button slots at +0x248 (8 bytes each, -1 for default text) and clears the four extra entries at +0x228.
  - The preset record (table `0x1639d5c`, 20 bytes: ten u16) holds a `buttonName` label id in the low byte and the icon in the flags. Flags: `0x400` X (id 1), `0x800` Y (id 0), `0x1000` L or ZL, `0x2000` R or ZR (by `sUserInfo+0x446c`), `0x4000` id 7, `0x8000` START (14). `0x100` lets slots 0 and 1 show.
  - The word at +0x248 + 8 * slot is the UI instance the label draws into, not text (`0x643ebc`), so custom text cannot go in a per-button slot. The smithy's weapon forge preset 53 is {`0x11` Back, `0x51a` Toggle Display, `0x927` Skills, `0x815b` Resort}.
- **Extras.** Four {s32 icon, char* label} entries, icon -1 free. `0x65e8cc(icon, label)` puts one in the first free extra (`0x644c34`; nothing when all four are taken or the pair is already there) and lays the guide out again (`0x6439ec(guide, +0x4c, +0x50, 1)`). No game call drops one extra (`0x6437d8` drops all four).
- **Layout.** Extras draw lowest, extra 0 at the bottom (inference from `0x643ce8`: extras take positions 3 down, buttons 0..3 from `3 - extras`); per-button slots are laid out 3, 2, 0, 1 from the bottom up above them (`0x6442b0`).
- **Icons.** The icon is a message id in table 18, `buttonName`; IDs and the swap byte are in [Input and actions](input-and-actions.md#button-names-and-icons).

## Centre popup

UI object 1 of the same manager, `cUIOInfoWindow` (vtable `0x17707d8`, 5848 bytes).

- **Requests** are queued 56-byte entries {+0x18 type 1..9, +0x1c flags & 1, +0x20 message id, +0x28 argument}. Each call returns a request id, -1 when refused (also while the window is not created during loading: retry next update).
- **Messages** are DialogMsg (`resident_<lang>.arc` `table\DialogMsg_<lang>`, message table 2 in code), read with flags 0 through `0x55bac0(obj, 0, 6, id)`. Checked ids:
  - 11 "Your Item Pouch is full."
  - 12 "%s at maximum."
  - 71 "Can't receive item: Item Box is full."
  - 29 "Received a new Award!"
  - 115 "New Equipment can be forged at the Smithy!" (no caller found).
  - 99 is `<COL FF0000FF>%s</COL>` in all seven languages; the game uses it through types 1 and 8 (`0x3aebb0`, `0x3f0f64`). Colour tags are inline `<COL RRGGBBAA>text</COL>`.
- **Wrappers** (each checks manager and object):
  - `0x65dd68(flags, id, arg)`: type 1, plain text, 126 callers.
  - `0x65ddc4(flags, id, arg, x)`: type 2, `snprintf(fmt(id), arg)` with `arg` at +0x28.
  - `0x65de34(flags, id, item, ...)`: type 3, an item name; 9 -> 10 (xN) for a count above 1.
  - `0x65deac`: type 4, an equipment name from category and number (via `0x13c208`, name virtual +0x3c).
- **Formatter** `0x5b41ac` loops over a window's entries (switch on type at `0x5b41b0`), joining lines with CommonMsg 14. The argument is read when the line is built, so a string passed in must stay valid until the popup shows.
- **Groups.** Outside a group each request takes a window of its own (`0x5b4d40` with byte +0x6c clear takes the head of the free list +0x16b4, count +0x16bc, and moves it to the shown list), so one popup per line.
  - `0x65dce4` begins a group: `0x5b4ba0` sets +0x6c and empties the head window. Requests add lines to that window, and the seventh is refused (`count > 5`). `0x65dd24` ends it: `0x5b4c44` clears +0x6c and moves the window to the shown list, doing nothing for an empty one. The game's list popup `0x3f0f24` does the same: DialogMsg 101 as a header, up to five id-99 lines (`0x65e078`).
  - Other begin/end callers: `0x27851c` / `0x278aa4`.
- **After a quest** `0x246b1c` queues the announcements (types 1..4: HR up 93, Wycademy Points 92, Monster List 28, Special Permit 89, "sent to Item Box" 7, shop music 112), called from `0x6ce4b8` and `0x6d19e8`. Lines queued on arrival in town follow the game's own.
