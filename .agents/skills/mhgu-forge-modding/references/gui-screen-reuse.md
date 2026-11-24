# Reuse game screens, panels and windows

## Reuse a game screen as a new page

WishFinder's Hunter's Notes row opens the game's Item Pouch screen with its own rows ([its page](../../../../mods/wishfinder/docs/worked/wishfinder-notes.md) has every address). The method:

- **Add the menu row in the game's own structures.** Hook the fill (write your row after the original), the "has a submenu" sizer (grow the cursor through the game's own resize call), and the help reader. Read each reader's bounds first: the start menu's help reader indexes its array by cursor row with no bound, so write the extra row only when the array really has room.
- **Run the screen's open and close, never its step**, so nothing refills it from the game's data. The page runner hook replaces the original for your row only, because the game's open step would turn an unknown row into row 0. That makes it the one hook that does not stack under the chaining rule, and only for that row.
- **Use setters, not the game's fill.** The pouch fill sets a name only when the row's item changed, so names go through the text setter each refill.
- **A shared window keeps its last user's state.** The description window is shared with other screens, so place it on every refill or it stays where the last screen left it.
- **Give the screen back.** On close, and whenever the screen draws with your title while your page is not open, reset the title and blank the rows.
- **Some game data is empty in a quest.** The equipment message table cell `0x1856b1c` is 0 in a quest, so names and descriptions come back empty there; copy them outside quests and use the copies.
- **Follow the game's language** (session byte +`0xa5`; values in `mhgu-understanding` [File layouts](../../mhgu-understanding/references/file-formats.md#file-layouts)). Keep every published string alive: the game's UI holds its address.

## Add pages to a game's paged panel

WishFinder adds pages after the game's to the quest detail panel (at the receptionist and the multiplayer quest board), and to the start menu's Quest Info in town and in a quest. All four were accepted on Eden and MHGU Recomp (r131; `mods/wishfinder/src/native/quest_page.rs`, `quest_info.rs`). Natives: `mhgu-understanding` [Quest detail pages: counter, quest board, Quest Info](../../mhgu-understanding/references/quest-detail-pages.md#quest-detail-pages-counter-quest-board-quest-info).

1. **List the owners from the code, not from screenshots.** Search the callers of the window's functions; every owner sizes the page cursor itself and may count pages differently (Quest Info: 3 in town, 4 in a quest). A screenshot's dialogue line is a help text, not a screen: the "counter Quest Info" one build assumed does not exist.
2. **Find the page cursor, every sizer and the draw.** The page is a cursor row or page ([Page cursor](../../mhgu-understanding/references/start-menu.md#page-cursor)); the game's draw handles its own pages only, so a later row draws nothing. Read whether the sizers run per frame or on events: a per-frame re-size would hold the row at 0.
3. **Hook after the draw** (an entry hook that stacks). Size the cursor to the game's pages plus yours only when the count differs, with the setter the owner uses: `0x54edec` with keep 1 clamps the row, `0x54ee34` resets the page.
4. **Draw your page through a game page.** Run the game's fill of a similar page (header, title and group come out right), then hide its rows and write your texts through the part setters, from static buffers.
5. **One text block.** Message objects do not clip, so all lines go into one text joined by `\r\n`; two text boxes gave the first line a different colour and spacing. Colour it with `<COL RRGGBBAA>` when the slot's own colour is wrong. Set the lines per page from a screenshot of your page, one owner at a time.
6. **Give back what no game page sets.** Rule lines, band objects and texts the game never touches stay hidden after your page; remember which window hid them and show them again on its next game page. A band set (`TexSet`) is one object: to keep one band, show another page's single-band object at the same place and hide the rest of that page.
7. **Read the quest the way the game does on each owner**, and confirm a field's type by a game reader before using it: `sQuest +0xa4` is a `cQuestData`, not the `rQuestData` its name suggested.

## Borrow a game window on another screen

WishFinder shows the smithy's Req. Materials window beside its Hunter's Notes list, in town and in a quest (`mods/wishfinder/src/native.rs` `materials_open`, `materials_show`, `materials_close`; natives in `mhgu-understanding` [UI objects outside their screen](../../mhgu-understanding/references/gui-objects.md#ui-objects-outside-their-screen)). The method, in the order that worked:

1. **Take the window apart statically first.** Find its class by DTI, then read four things from its vtable. Which layout file does it ask for, and which instance does it bind? What does its draw read (the data block, the dirty flag), and which message texts does it fetch? Find the screen code that fills that block and copy how each field is derived. A window that only reads a block behind a pointer is the easy case; one that reads its screen's fields is not.
2. **Let the game build it.** Call the game's object factory with the class's DTI instead of allocating and wiring an object by hand: it creates, binds, registers for drawing and gives the object the destructor that matches. Compare the DTI's name and the new object's vtable before touching either.
3. **Load what the factory expects.** The factory finds a layout only if it is already loaded, and a facility's layout is loaded only inside that facility. Load it yourself by path through the resource manager just before the factory call, then release your own reference once the object holds one. Check the path's hash against the game's file table offline, for every language folder, before a run.
4. **Feed it the way its screen does.** Point its data pointer at your own static block, fill the records with the same lookups, set its dirty flag, and show or hide it with the game's calls. Destroy it through its own deleting destructor when your page closes, every way the page can close.
5. **Make it survive a quest.** A quest loads less: message files and name tables that exist in town are missing. Find out which with a run, never by assuming. The game's text setter blanks a label for a missing text, so the window still works. Copy the texts while they are loaded: at each town arrival, not only when your page opens, so a player who goes straight to a quest has them. Set the copies after the window's own draw, which would otherwise clear them. Run that draw yourself right after filling, so it does not happen later and undo your texts.
6. **Probe before polishing.** The first build logged one line with a flag per step (texts, class, factory, resource manager, layout, made). Three runs then named each missing piece in turn: the layout not loaded in the menu, then the texts not loaded in a quest. Keep the line until the feature is accepted.

What the runs refuted: the layout does not load with the town (it loads with the smithy), and a missing title text does not crash the draw.

## Button guide and popups

Game facts (presets, extras, layout, popup requests and groups): `mhgu-understanding` [Button guide](../../mhgu-understanding/references/guide-and-popups.md#button-guide).

- **Guide text goes in an extra** (`0x65e8cc`); per-button slots hold UI instances, not text. No game call drops one extra, so free your own entry by hand, matched by your label's address, and lay the guide out again with its current preset; the game's entries stay. Pick L/R or ZL/ZR icons by the shoulder-swap byte, as the start menu does.
- **Popup lines are static strings**: the game formats the argument when the popup builds, so keep it alive. Group up to six lines per popup, and retry a refused request (-1) on the next update.
