# Extend the game's native GUI

This recipe is established for the quest counter row in MHGU Switch 1.4.0 (Key Quest Markers, WishFinder) and the smithy's list rows (WishFinder). It is a retained game-owned tree, with resource animation bindings and cached draw commands. Other menus need their own count, ownership, and destructor audit. For resource decoding and object layouts, use the optional companion `mhgu-understanding` native GUI reference.

## Plan a different menu before adapting the recipe

Establish the selected resource hash/variant, live instance, animation ID versus table row, owned object range and sequence bindings. Node names and file presence do not establish a spare rendering mechanism. The corrected hud0 case has `Anm_sharp` selecting animation ID 4 at row 7. Its apparent `sgauge` candidates belong to stamina, and `Txt_mask05..55` belong to `h_hand`. Use the companion's native GUI identity table when researching that fixture. At runtime (World Sharpness Gauge r9 Eden log, 2026-10-22), `Txt_sharp`, `Txt_sharpefx` and the third sharpness texture are siblings whose parent is the gauge controller itself. The file's child indices do not describe this tree: there is no group node, and the glow is not a child of the bar. Like the counter row, it has a map alias: controller +0xa0 holds the same pointer as instance +0xd8 (r16 log; the insertion's gate has required it on every insert since r18). An earlier zero reading did not hold.

Before adding a child, identify the target menu's construction/update/draw/destruction paths, every affected count/map consumer, map aliases, cache prefix and capacity, allocation/free pairing and publication order. Derive its sizes from those paths. The 13-pointer map and 168-byte cache below are quest-row results, not reusable HUD constants. Resource counts alone do not establish runtime capacity. Prepare allocations before publishing, preserve original bindings, avoid duplicate insertion and verify failure cleanup.

Choose an update point after the final native write and before transform/draw-cache construction for the properties being changed. Keep pointers inside a verified owner lifetime. A HUD may disappear, hide or be recreated across weapon, scene and quest changes; measure how long the object you touch lives. Establish how the plugin restores its overrides while objects remain valid and reacquires new objects without retaining stale pointers. Include exit/re-entry and recreation in validation even if initial drawing works.

Keep the user's visual design distinct from mechanism feasibility. Mark unresolved masking, ownership or field contracts as research work. A plan is not ready for native mutation merely because the quest-row example worked.

## Attach at the correct lifecycle point

The normal row builder at main+`0x616cb0` has seven integer/pointer arguments. Call its original first, then decorate the completed row. Parent controller `0x54d030` has two pointer arguments and supplies synchronous offer context through guarded TLS. Keep native pointers local to that callback.

Validate native GUI identity, root/object class, IDs, owners, descriptor, map aliases, and bounded child traversal. The audited row is animation 20 with twelve lookup objects, fifteen sequences, nine drawables, and sixty-three resource instances. Reject conflicting IDs and cycles. A private marker ID `0x4b514d33` permits finding an existing owned child instead of allocating each frame.

## Allocate for the destructor that will run

`cGUIObjTexture` is 304 bytes. Use its DTI's MT allocator, verified alignment, and native constructor main+`0xa4f60c`. DTI allocator lookup is main+`0x7aa47c`; its allocator vtable uses alloc+`0x20` and free+`0x34`. The Texture DTI has only three virtual slots; vtable+`0x0c` is null, so the generic instantiate wrapper cannot supply a placement constructor here. Forge malloc is not the allocator expected by the native destructor.

Initialize geometry, material, texture, visibility, parent/owner/resource links before publication. Object +`0x74` is the owning `cGUI`, obtained from instance+`0x6c`; it is not the instance. Object +`0x78` borrows the `rGUI` resource. Scoped guards destroy/free unpublished objects if any allocation or validation fails. Native helper `0xa4844c` links siblings and parent.

The Key Quest Markers badge (`create()` in `mods/key-quest-markers/src/gui.rs`) is the only standalone Texture node that has drawn in-game. Build a new one with every step it takes, in this order, and name the native code that makes any skipped step unnecessary:

1. Allocate 304 bytes through alloc+`0x20` with `(bytes, 16, dti id)`, zero the block, then run constructor main+`0xa4f60c` with the storage in r0.
2. Write +`0x50` (a private ID), +`0x74` (owner) and +`0x78` (resource). World Sharpness Gauge also needed a live sibling's +`0x64`, because the `Texture` resolve scans `*(obj+0x64)+0xe8` (main+`0xb80fd0`). Without it, the copy is refused at the texture step.
3. Run the 12 style setters, each with two integer arguments. Names are from the saved DTI; values are the badge's: `BlendState` `0xa4dc24`=1, `ControlPoint` `0xa4a9f4`=0, `FixFrame` `0xa47a94`=0, `Mask` `0xa4dca0`=0, `Priority` `0xa47a04`=2, `ReferencePosition` `0xa4aa24`=1, `ReferenceRotation` `0xa4aa5c`=1, `ReferenceScaleX/Y/Z` `0xa4aa94`/`0xa4aac8`/`0xa4aafc`=3, `Reverse` `0xa4dc54`=0, `SamplerState` `0xa4fa5c`=0. A zeroed block leaves every `Reference*` property at 0. These are the badge's values: a copy of another sprite takes that sprite's sampler, the low nibble of +`0x108` (the sharpness bar's is 2; a copy left on 0 filtered its edges differently).
4. Run `Texture` `0xa4faf0` last; it returns early while +`0x78` is 0. Then set `mTextureRect` through `0xa4fb58` with a pointer to four floats, and keep using that setter afterwards (see "A texture caches its quad").

The constructor's own defaults include +`0x54` = `0x020a0001` and +`0xb4`/+`0xb8` = 32.0 (main+`0xa4d0d8`). Reading those words back proves only that the constructor ran, not that the node draws. +`0x80`/+`0x84` and +`0xb4`/+`0xb8` are local values, not screen pixels. A node's rect at +`0xe0` is not its sprite either: the sharpness bar is authored 88x24 with an x scale of 1.0, its rect is 128x128, and its ink was measured ending at 200 px inside the rect's 110..238. No mapping from atlas columns to rect pixels was ever derived, so measure geometry on screen and store it as a fraction of the rect (P7 step 2).

An untested alternative is to copy a live sibling of the same class byte for byte, then replace the ID, clear the +`0x68`/+`0x6c`/+`0x70` links and the animation binding, and link the copy with the native linker. No mod has run this, and the class has no clone function: its vtable slot 0x00 (main+`0xa4f6a4`) is not a constructor, and calling it on a fresh block froze the game.

When a new node becomes the parent of existing nodes, the draw walker main+`0xa494a0` decides the result. It descends +0x68, moves along +0x6c, and when a sibling is 0 it pops to that node's +0x70. It writes a node's exit entry only when a pop lands on that node. So a moved node's old sibling link and its parent link both decide whether the new parent's exit entry is ever written. Run a walker port over the tree after your writes before you trust it (playbook P2 step 5). An enter entry with no matching exit leaves masks and other state active for every draw that follows.

Appending a child requires both storage expansions:

| Storage | Original | Extended | Contract |
| --- | --- | --- | --- |
| Lookup map | 12 pointers | 13 pointers | Keep original indices, append static child; publish instance+0xd8 and root +0xa0 |
| Draw cache | 152 bytes | 168 bytes | No prefix on this row (`root+0x80 == root+0xa4`); `drawableCount*16+8`, 9 becomes 10 |

The map uses the instance's MT allocator. Cache allocation must match the native cache-free/destructor path. Fully prepare replacement allocations, publish aliases/cache/tree coherently, mark sorting/transform/draw state dirty, and free replaced storage at the verified point. The native root/instance recursively destroy the child, map, cache, and graphics allocations. No extra destructor hook is required for this audited static addition.

The count getter `0xa38ffc` counts the linked tree, while cleanup `0x5456e4` indexes the runtime map to that count. A 13-node tree with a twelve-entry map froze the game. Enlarging only the cache does not fix it. Original resource descriptors, first twelve animation bindings, and sequences remain unchanged. An animated addition may need another design.

### A row another plugin also extends

Key Quest Markers and WishFinder both add children to the quest counter row, and either may insert first. So the 13-pointer map and 168-byte cache above hold only for a row with no other additions: size both from the live tree each time. WishFinder takes the map as the live count `0xa38ffc` plus two and the cache as (the resource's drawables + nodes beyond the resource's own + 2) × 16 + 8, counting every added node as drawable, so a foreign non-drawable node only over-allocates. A build that read the map and cache at fixed sizes crashed beside WishFinder when WishFinder inserted first. Find your own nodes by their private ID (+`0x50`), never by index.

### Size any row from its own numbers

Root setup `0xa49b28` allocates `(objects << 4 | 8) + sequences * 12` through root vtable slot 0x58 and stores it at root +`0xa4`, with the walker's pointer root +`0x80` = allocation + `sequences * 12`. Both counts are the halfwords at **row+8**, not row+4: the sharpness row reads 3 and 16 there and 4 and 15 at row+4.

- Objects is the node count. The map is one longer, because its first entry is the controller.
- The walker's list is 8 bytes per record plus an 8-byte terminator. A visible drawable node emits an enter and an exit; a hidden one emits neither.
- The grown map comes from the `cGUIInstance` allocator, slot 0x1c with `(bytes, 16)`. Passing no alignment leaves it as register garbage. Publish instance +`0xd8` and root +`0xa0` together.
- A row with sequences has live animation tracks in the prefix: setup (`0xa484c4`) stores each object's slice at +`0x64`, and the row update `0xa4915c` evaluates and writes them every frame. Copy the prefix into the new block and move every map entry's +`0x64` that points into the old prefix to the same offset before freeing the old block; freeing it under them crashed Ryubing at `0xb349c0`.
- Return the old cache through root slot 0x5c, after that move.
- Link last, so a larger tree never exists against the old map, and then set root +`0x8c` bits 0 and 1 (bit 0 rebuilds the walker's list, bit 1 starts the transform walk).

The game allocates a row's map in `FUN_01401bc0` and frees it in `0xa38828` (`setAnimationId`) through the same class allocator. World Sharpness Gauge still leaks the old 16-byte block, a shortcut from before that was read.

## Move nodes under a new parent

The accepted shape (World Sharpness Gauge) is the controller over a mask over the bar, glow and edge, with a second mask over the shade as the first mask's sibling.

- **One inbound chain per node.** Native teardown (root `0xa486fc`, mask `0xa56758`) walks children and then siblings, calling slot 0x04 on each. After moving the first sibling under the new node, also write 0 to root +`0x6c`, or the moved nodes are reachable twice and are freed twice. That poisoned the allocator the next area's row builds from, so the row never came back, and it crashed at a quest end. The old chain also hides the bug: a visible bar can be drawing through it, outside the mask.
- **Native linkers.** `0xa48460(parent, child)` writes the child link and the child's parent. `0xa4844c(node, sibling)` writes the sibling link and copies `node`'s parent into the sibling, so link the parent first.
- **Paint order is walk order.** The walker has no sort and no z value. To draw under a node, a node has to be walked before it, but linking one ahead of the mask on the controller's chain lost the row (`root.child=0x0` 8 ms after insertion, never matched again; mechanism unread). A sibling after the mask is the only proven position.
- **Priority is a re-sort key, not a layer the walker reads.** Bit 19 of +`0x54` makes `0xa4915c` sort that node's children ascending by the halfword at +`0x60`, relink them and clear the bit. The constructor's default flags carry bit 19, so set a child's Priority deliberately.

## Clip with a scissor mask

A node's rect does not limit its drawing (a zero-width +`0xe0` and +`0xf0` landed and the copy painted anyway). The render state's scissor does. A mask's enter (main+`0xa4ba94`, slot 0x38) sets it and its exit (main+`0xa4bcdc`, slot 0x40) restores it, for everything walked between them. It clips at 1:1 and never scales what it covers.

A scissor stays in the game's pixels when something moves the HUD's quads after the game draws them, so a cut that must follow a sprite is not a scissor: see [HUD movers](#hud-movers-gu-native-and-uiscale). A mask with +`0xa4` bit 0 clear applies and restores no scissor (main+`0xa4bbe0`, main+`0xa4bce4`); World Sharpness Gauge keeps its masks at +`0xa4` = 2 only to place things.

Build a `cGUIObjScissorMask` (0xd0 bytes) with factory main+`0xa4b6cc`: no arguments, object in r0, allocated through its own DTI. Give it a marker at +`0x50` and a sibling's +`0x74`/+`0x78`. Then, in a hook on the enter handler filtered by that marker, write on every enter:

| Field | Value | Why |
| --- | --- | --- |
| +`0xa0` low nibble | 0 | Two anchor modes the factory leaves as recycled memory: `& 3` for +`0xa8`, `& 0xc` for +`0xac`. Mode 0 spans `0..size`, 1 centres, 2 spans `-size..0`, 3 collapses the axis. The class has no Anchor property. |
| +`0x10`, +`0x14` | 1.0, 0.0 | Builder `0xa4b390` multiplies the width by this row, and the factory's template leaves it zero. |
| +`0x40`, +`0x44` | floats, only to move the box | The box corner is the mask's own translation. The builder reads no parent field. The transform walk fills it from the parent, which is why a mask defaults to the row's corner. |
| +`0xa8`, +`0xac` | integers | Box size, forward from the corner. |
| +`0xa4` | 3 | Bit 1 rebuilds +`0xb0..+0xbc` and clears itself; bit 0 applies the scissor. |

Keep bit 17 on the mask's +`0x54`. Without it the node never takes its parent's transform and neither does anything under it.

These do nothing: +`0xb0..+0xbc` (derived, rebuilt from the row above), +`0x80`/+`0x84` on a mask with no animation entry, and +`0xe0` (past the end of the 0xd0-byte object). Take a width from the bar's rect, never from bar +`0xa8`, which is an animated field that reads zero at enter: feeding it produced a zero-width box, and "the layout zeroes the width" was that zero.

Turn a mask off with `Enable` `0xa4ba20(mask, 0)`, which writes bit 0 of +`0xa4` from its argument.

### Per-node scissor is not a substitute for a mask

Use a scissor mask. Static reading, never run: `ScissorSize` (`0xa4dcc4`) only takes effect under `Mask` 3 or 6, and `Mask` (`0xa4dca0`) is +`0xcc`'s low nibble.

- **There is no scissor-only mode.** After applying its box, the texture's enter (`0xa4e628`) always calls `0xb38004` for modes 3 and 6, and its exit (`0xa4eddc`) calls `0xb38bc8`. While `sGUI`+`0x1c` is set, `0xb38004` redirects the render target, draws a full-screen quad and swaps two GUI shaders.
- **It widens the live box.** The texture's enter takes min left/top and max right/bottom (`0xa4e71c`), a union. A mask's enter intersects (`0xa4bc78`). The node's own box is used alone only when the live box has no width or height.
- **The box is tied to the sprite.** Slot 0x74 (`0xa4f420`) builds +`0xe0` with `0xa4b390` from the node's own matrix, `ScissorSize` and `ControlPoint` (+`0xa0` & 0xf). Slot 0x44 (`0xa4e604`) sets the rebuild bit +`0xd0` bit 0.
- **The game never uses it.** In all 6,887 GUI files, `Mask` is 0 in 159,217 entries, 1 in 36 and never keyed, and `ScissorSize` never appears. The setters have no direct callers, only DTI words.

Unread: what writes `sGUI`+`0x1c`, so whether `0xb38004` does anything at runtime, and what the live box holds outside any mask. If both turned out harmless, this could in principle replace masks, but on a path no game GUI has ever run.

## A texture caches its quad

Draw slot 0x3c (main+`0xa4fc9c`) calls `0xa4feb4`, which copies the UVs from +`0x10c..+0x118` and the corner colours from +`0xa4..+0xb0` into the vertex record only while `global+0x98 & (+0xc0 >> 24) & 7` is nonzero, then clears those bits. Only slot 0x50 (main+`0xa4fc68`) sets them.

So use the setter. `mTextureRect` `0xa4fb58(node, *f32[4])` returns at once when the floats match, otherwise stores them, calls slot 0x28 when `+0x108 & 0x30`, and tail-calls slot 0x50. Calling it every frame is cheap. A raw write to +`0x10c` reads back perfectly and never repaints: the copy kept the band the first build left while a read-back showed the write landing on all 73 fill lines. Inference: raw colour writes after the first build are inert the same way, so use the `VertexColor*` setters. Position and authored-size writes after the build were also inert (`pos=90.0 0.0 size=0.7 24.0` with `rect=110 38 238 166`, mechanism unread), so move geometry with a mask.

## HUD movers (gu-native and UIScale)

Two things move HUD quads after the game has drawn them. Any placement a mod
computes from node fields, rects or the node's own matrix is then the
unmoved place.

| Mover | What it does | Source |
| --- | --- | --- |
| gu-native's renderer | Rewrites every GUI quad's uploaded matrix, anchored by that quad's own layer and position; moves the game's scissor only vertically | gu-native `runtime/nvn/vulkan/exec.c`, the `pos_z = m[14]` read and `scissor_rect` (local `9a1aef7`; first read at `c7fc45a`) |
| UIScale (KatLib) | Edits a sprite in the uploaded matrix block at `*(ctx+4)+0x18bc` after publishers main+`0xa4eb9c`/`0xa3e3b0`. The node's `+0x10` stays unscaled. Its own `+0xe0` rewrite refreshes only on a rebuild | World Sharpness Gauge *Following a rescaled bar* |

gu-native's rule, per quad: the anchor (left, right or centre; top, bottom or
centre) comes from layer `m[14]` and position `m[12]`/`m[13]` on the 1280x720
canvas, with special cases (layer 103 status HUD at y < 500 goes left/top, the
item bar right/bottom, layer 105 the minimap). The quad is scaled by
`s = (16/9)/aspect` and `sy = aspect/(16/9)`, so at exactly 16:9 nothing moves
except what the touch layout moves (item bar, Arts, target). The scissor moves
only vertically at 16:10 (`ui_scissor_v`) or is relaxed for the item bar, never
with the status pieces.

Rules:

1. **Cut a sprite in its own geometry, at its draw.** The texture draw
   main+`0xa4fc9c` uploads `node+0x10` (main+`0xa4fd10`/`0xa4fd38`) and rebuilds
   the UVs from the `[u1, v1, u2, v2]` window later in the same call
   (main+`0xa4fe44`). In a hook on it: scale m[0], move m[12], set the window
   through the setter, call the original, then put m[0] and m[12] back. The
   quad's local x span is the float authored width at +`0xb4` with anchor
   +`0xa0 & 3` (0: `0..w`, 1: centred, 2: `-w..0`; main+`0xa4ff1c..0xa4ffb4`),
   not the layout width at +`0xd8`. A mover then moves the cut with the sprite
   (World Sharpness Gauge `crop_span`; accepted on MHGURecomp, not run on
   gu-native).
2. **Read where a sprite really went after the original draw**, from the
   uploaded block. Words 0, 1, 4, 5, 12 and 13 equal to the node's mean a plain
   draw; an unchanged block address means nothing was uploaded. This sees
   UIScale; it cannot see gu-native, which moves the quad later, on the host.
3. **A node you add moves by its own position, not its parent's,** on
   gu-native (inference from the per-quad rule above). Keep added nodes on the
   same layer and inside the same position band as the part they belong to, or
   they split from it on a non-16:9 screen.
4. **An ImGui overlay never moves with the HUD.** Do not place ImGui drawing
   from HUD node positions if it must line up on gu-native. World-space
   overlays are a separate problem: [Runtimes](runtimes.md#imgui-on-each-host).
5. **Test what you can reach.** Nobody here runs gu-native. UIScale on
   MHGURecomp is the reachable mover: run the quest with a non-default scale, and
   ask the tester to drag the element in UIScale's editor (a live drag is still
   unconfirmed for World Sharpness Gauge). Report gu-native as source-only.

## Survive a row's end

The sharpness gauge's row lasts a quest (inference, see Lifecycle in `mods/world-sharpness-gauge/DEVELOPMENT.md`), other rows are unmeasured, and `cGUIObjRoot`'s destructor has fired in no saved log.

- Detect the death from a callback that keeps running. A freed mask's enter stops being called, so a check placed only there goes silent. Check from the draw walker: read-only, the marker, the mask's parent against the root and the root's child against the mask. On failure, drop every captured address and re-arm discovery, so the next row is read and inserted like the first.
- Write only where the game hands over a live object. In the mask's enter, when the links are gone, turn the mask off and drop the addresses. Left alone, it keeps applying its last box.
- Every HUD instance calls the walker, so capture the pair whose instance +`0xdc` is the controller you identified, not the last one seen. The walker has two entries: `0xa39300` calls it at `0xa39664`, and `0xa56a14` tail-branches with node +`0xcc`.

## Art, colour and paired nodes

- The game multiplies the vertex colour (`0xa4e0b8`, `0xAABBGGRR`) with the texel, so tintable art must be white or grey. Coloured art (WishFinder tried the yellow flag on `HD_lobby00`) cannot take a source colour.
- Use an atlas the row's resource already loads, and check the cell in every language's atlas: item icon cell 9 (ore) is drawn differently in the German, Italian and Spanish `HD_cmn_icon_GSM_NOMIP` than in English. Modern Weapon Controls replaces that atlas with a double-size copy, so take the size from the texture header (`mhgu-understanding` resources reference).
- Nodes that only work together (WishFinder's shadow and pin) are created together or not at all, on one rect. Link the one painted first first, and give both a Priority above the row's own (the counter row uses 0..2, WishFinder 3 and 4) so the `0xa4915c` re-sort keeps that order.
- A row that does not need the decoration gets no children, so the native tree stays the game's own on every other row.

Worked example: `mods/wishfinder/DEVELOPMENT.md` sections Quest row and Smithy (the smithy's `cUIOFacilityShopMenu` rows are `shop_menu.gui` animation 25, four drawables, no cache prefix).

## Reuse a game screen as a new page

WishFinder's Hunter's Notes row opens the game's Item Pouch screen with its own rows (`mods/wishfinder/DEVELOPMENT.md` section Hunter's Notes has every address). The method:

- **Add the menu row in the game's own structures.** Hook the fill (write your row after the original), the "has a submenu" sizer (grow the cursor through the game's own resize call), and the help reader. Read each reader's bounds first: the start menu's help reader indexes its array by cursor row with no bound, so write the extra row only when the array really has room.
- **Run the screen's open and close, never its step**, so nothing refills it from the game's data. The page runner hook replaces the original for your row only, because the game's open step would turn an unknown row into row 0. That makes it the one hook that does not stack under the chaining rule, and only for that row.
- **Use setters, not the game's fill.** The pouch fill sets a name only when the row's item changed, so names go through the text setter each refill.
- **A shared window keeps its last user's state.** The description window is shared with other screens, so place it on every refill or it stays where the last screen left it.
- **Give the screen back.** On close, and whenever the screen draws with your title while your page is not open, reset the title and blank the rows.
- **Some game data is empty in a quest.** The equipment message table cell `0x1856b1c` is 0 in a quest, so names and descriptions come back empty there; copy them outside quests and use the copies.
- **Follow the game's language** (session byte +`0xa5`; values in `mhgu-understanding` [Resources and tooling](../../mhgu-understanding/references/resources-and-tooling.md#formats-a-plugin-reads)). Keep every published string alive: the game's UI holds its address.

## Add pages to a game's paged panel

WishFinder adds pages after the game's to the quest detail panel (at the receptionist and the multiplayer quest board)
and to the start menu's Quest Info in town and in a quest; accepted in all four on Eden and MHGU Recomp (r131;
`mods/wishfinder/src/native/quest_page.rs`, `quest_info.rs`; natives in `mhgu-understanding`
[Quests and progression](../../mhgu-understanding/references/quests-and-progression.md#quest-detail-pages-counter-quest-board-quest-info)).

1. **List the owners from the code, not from screenshots.** Search the callers of the window's functions; every
   owner sizes the page cursor itself and may count pages differently (Quest Info: 3 in town, 4 in a quest). A
   screenshot's dialogue line is a help text, not a screen: the "counter Quest Info" one build assumed does not exist.
2. **Find the page cursor, every sizer and the draw.** The page is a cursor row or page
   ([Menus and screens](../../mhgu-understanding/references/menus-and-screens.md#page-cursor)); the game's draw handles
   its own pages only, so a later row draws nothing. Read whether the sizers run per frame or on events: a per-frame
   re-size would hold the row at 0.
3. **Hook after the draw** (an entry hook that stacks). Size the cursor to the game's pages plus yours only when the
   count differs, with the setter the owner uses: `0x54edec` with keep 1 clamps the row, `0x54ee34` resets the page.
4. **Draw your page through a game page.** Run the game's fill of a similar page (header, title and group come out
   right), then hide its rows and write your texts through the part setters, from static buffers.
5. **One text block.** Message objects do not clip, so all lines go into one text joined by `\r\n`; two text boxes
   gave the first line a different colour and spacing. Colour it with `<COL RRGGBBAA>` when the slot's own colour is
   wrong. Set the lines per page from a screenshot of your page, one owner at a time.
6. **Give back what no game page sets.** Rule lines, band objects and texts the game never touches stay hidden after
   your page; remember which window hid them and show them again on its next game page. A band set (`TexSet`) is one
   object: to keep one band, show another page's single-band object at the same place and hide the rest of that page.
7. **Read the quest the way the game does on each owner**, and confirm a field's type by a game reader before using
   it: `sQuest +0xa4` is a `cQuestData`, not the `rQuestData` its name suggested.

## Borrow a game window on another screen

WishFinder shows the smithy's Req. Materials window beside its Hunter's Notes list, in town and in a quest (`mods/wishfinder/src/native.rs` `materials_open`, `materials_show`, `materials_close`; natives in `mhgu-understanding` [Menus and screens](../../mhgu-understanding/references/menus-and-screens.md#ui-objects-outside-their-screen)). The method, in the order that worked:

1. **Take the window apart statically first.** Find its class by DTI, then read four things from its vtable: which layout file it asks for, which instance it binds, what its draw reads (the data block, the dirty flag) and which message texts it fetches. Find the screen code that fills that block and copy how each field is derived. A window that only reads a block behind a pointer is the easy case; one that reads its screen's fields is not.
2. **Let the game build it.** Call the game's object factory with the class's DTI instead of allocating and wiring an object by hand: it creates, binds, registers for drawing and gives the object the destructor that matches. Compare the DTI's name and the new object's vtable before touching either.
3. **Load what the factory expects.** The factory finds a layout only if it is already loaded, and a facility's layout is loaded only inside that facility. Load it yourself by path through the resource manager just before the factory call, then release your own reference once the object holds one. Check the path's hash against the game's file table offline, for every language folder, before a run.
4. **Feed it the way its screen does.** Point its data pointer at your own static block, fill the records with the same lookups, set its dirty flag, and show or hide it with the game's calls. Destroy it through its own deleting destructor when your page closes, every way the page can close.
5. **Make it survive a quest.** A quest loads less: message files and name tables that exist in town are missing. Find out which with a run, never by assuming. The game's text setter blanks a label for a missing text, so the window still works; copy the texts while they are loaded (at each town arrival, not only when your page opens, so a player who goes straight to a quest has them) and set the copies after the window's own draw, which would otherwise clear them. Run that draw yourself right after filling, so it does not happen later and undo your texts.
6. **Probe before polishing.** The first build logged one line with a flag per step (texts, class, factory, resource manager, layout, made). Three runs then named each missing piece in turn: the layout not loaded in the menu, then the texts not loaded in a quest. Keep the line until the feature is accepted.

What the runs refuted: the layout does not load with the town (it loads with the smithy), and a missing title text does not crash the draw.

## Button guide and popups

Game facts (presets, extras, layout, popup requests and groups): `mhgu-understanding` [Menus and screens](../../mhgu-understanding/references/menus-and-screens.md#button-guide).

- **Guide text goes in an extra** (`0x65e8cc`); per-button slots hold UI instances, not text. No game call drops one extra, so free your own entry by hand, matched by your label's address, and lay the guide out again with its current preset; the game's entries stay. Pick L/R or ZL/ZR icons by the shoulder-swap byte, as the start menu does.
- **Popup lines are static strings**: the game formats the argument when the popup builds, so keep it alive. Group up to six lines per popup, and retry a refused request (-1) on the next update.

## Material, geometry, and title fitting

Decode `INIT_PARAM` kinds 17/18 as immediate boolean/u32 values. Treating them as section offsets concealed the real material state. `Mask=0` is normal colour drawing; Mask 1 enters mask-writing even when Visible and vertex colours are correct.

For clipping, establish both the mask writer and consuming material/draw, their coordinate space and order, cache invalidation and mask reset/restoration before unrelated HUD draws. Parenting a Mask1 object alone proves none of those. Test empty, partial and full fill with unchanged texture proportions, aligned effect layers and preserved outlines as required. A resource fallback must meet the same continuous-fill contract and preserve unrelated entries.

Reuse texture descriptors the row already loaded and native logical atlas coordinates; logical coordinates need not match physical HD image pixels. Validate the live descriptor, dimensions and texture pointer, and ship no extracted texture or replacement ARC.

Place a decoration from the row's own objects and their live visibility (+`0x54` bit 0 after the native update), not from fixed offsets. Key Quest Markers' badge geometry, title widths and colours are its contract: `mods/key-quest-markers/DEVELOPMENT.md`.

Title binding 4/ID 6 is `cGUIObjMessage`, CRC `0x2fb82eae`, size 352. It is not `cGUIObjText` size 384. Derive fixture classes and getDTI from the real resource. Common setter addresses alone do not prove a subclass. Native Size/AutoScale setters need the glyph-cache dirty bit at +`0xf0` bit 16. Restore the original title size/AutoScale before a reusable row can exit early on missing metadata.

Do not apply the title Size `0xa53528` or AutoScale `0xa53348` contract to Texture objects. Saved Texture DTI's Size entry has a getter and no setter. Check callback direction, actual class fields, native body and ABI before choosing a property operation. Getter-only metadata does not rule out a different verified geometry path.

Copy any applied settings (colours and the like) out once per row; do no file I/O or settings locking in the hook.

## Verify the full route

Trace handshake, original trampoline, hook entry, resource identity, attachment, classification, material dispatch, geometry, and visible output. Existing ARM fixtures execute native construction, getDTI, setters, prepaint, Texture Draw, quad generation, traversal, and cleanup. They caught wrong subclasses and mask branches that simpler draw-callback doubles missed.

Mocked GPU commands/allocations establish no actual clipping or pixels. Manual acceptance checks opening, scrolling, selection, request overlap, confirmation, closing/reopening, and scene transitions. Preserve successful payload hashes. A visible bit or successful plugin load does not establish a working GUI.


## Common mistakes

| Mistake | Correct approach |
| --- | --- |
| Taking a pointer field's type from its DTI name | Find a game function that reads it: `sQuest` `mpQuestData` is the `cQuestData` itself, and `getData` on it read quest ID 0 (WishFinder r130). |
| Testing a lookup with an input whose wrong reading looks like a valid one | An in-quest case with a quest that lists nothing passed while the lookup read nothing. Choose inputs where a wrong reading gives a different output. |
| Using Forge `malloc` for game GUI objects | Use the class DTI's MT allocator so the native destructor frees it correctly. |
| Sizing a row's map or cache with fixed numbers | Another plugin may have added children first. Size both from the live tree ([Native GUI extensions](#a-row-another-plugin-also-extends)). |
| Appending a GUI child without growing the object map | The game indexes the map by the tree count and crashes. Grow map and draw cache together. |
| Freeing or zeroing a row's draw block prefix when growing it | Objects animate through `+0x64` pointers into it. Copy the prefix and move those pointers first (see above). |
| Reading tree shape from a `.gui` file's child index | The runtime links (+0x68 child, +0x6c sibling, +0x70 parent) are authoritative. In hud0 `sharp`, the three textures are siblings directly under the controller. |
| Copying another row's or mod's layout (cache size, flag bits, map aliases) and calling it "proven" | Only native code that reads the field for this class proves it. Label everything else as inference in code comments too. |
| Keeping a captured instance after a quest or scene ends | Clear it at the destruction path. An unchanged address does not prove the object is still alive. |
| Assuming how long a HUD object lives | Measure it. The sharpness gauge's row lasts a quest and other objects are unmeasured, so keep a liveness check, drop every captured address when it fails, and redo per-row setup on the next object. The cGUIObjRoot slot 0x04 destructor fired in no saved log, so do not rely on it (`mhgu-understanding` Rules). |
| Using a timer, frame counter or "no sample for N calls" as proof that an object is still alive (or already gone) | Write to or free a game object only while a native lookup made in the same callback finds it, or before a hooked teardown runs. Without that, leave the restore code out (the game's destructor owns what is linked into its tree) and report the missing teardown path. |
| Reparenting nodes with hand-written +0x68/+0x6c/+0x70 links | List every link the walker and the native teardown follow on each moved node and on its old neighbours, and say where each new value comes from. Prefer the native linkers `0xa48460` and `0xa4844c`, and end the old chain: a node reachable twice is freed twice (see above). Prove the tree with a walker port over the post-write state (playbook P2 step 5). |
| Checking a row's liveness only from a callback that row owns | A freed node's handler stops being called, so the check goes silent. Check read-only from a callback that keeps running (the draw walker), and write only where the game hands over a live object. |
| Re-reading the row after insertion with gates written for the tree before it | Each per-frame path after a write must accept the tree your write produced. Fixture it (playbook P2 step 5). |
| Deriving draw geometry from a node rect whose relation to the drawn sprite is unproven, or citing a setter probe as proof of clipping | Label such geometry inference. Shared render state read at an arbitrary moment proves only that the setter ran, not that it was active during the target draw. |
| Leaving out steps of an in-repo precedent (such as the KQM badge's construction) | Compare your code with the precedent field by field. Name every skipped step and the native code that makes it unnecessary (see above). |
| Logging the values you wrote and calling that placement evidence | Read back the game's own output (rect +`0xe0`, matrix +`0x10..+0x4c`, size) at the next callback, after the native layout has run. A constructor default read back proves only that the constructor ran, and a field you wrote reads back whether or not anything consumes it. |
| Writing screen pixels into a node's local position or size | Those fields are local, and later writes to them may be inert. Move geometry with a mask, and treat a node's rect as a layout box, not as its sprite. |
| Interpreting a screenshot | Name each HUD element in the photo and confirm it with the user or a baseline shot of the accepted build (the Dual Blades demon gauge was once misread as the mod's own node for three builds). A user's correction about one element does not extend to others. An artefact that appears or disappears between builds is evidence; never discard it. |

Sources: `mods/wishfinder/DEVELOPMENT.md` and `src/{gui.rs,native.rs,hooks.rs}`; `mods/key-quest-markers/src/{gui.rs,native.rs,offers.rs}`, `mods/key-quest-markers/scripts/gui_layout.py`, `tests/{resource.py,native_adapter.py,arm.py}`, `research/theme-colours.json`, `DEVELOPMENT.md`, `EVIDENCE.json`; `mods/world-sharpness-gauge/src/insert.rs` and its `DEVELOPMENT.md`.  Native addresses in the mask, cache and flag sections were rechecked against the original bytes on 2026-11-01.
