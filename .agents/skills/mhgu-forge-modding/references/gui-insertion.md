# Add objects to a native GUI tree

This recipe is established for the quest counter row in MHGU Switch 1.4.0 (Key Quest Markers, WishFinder) and the smithy's list rows (WishFinder). It is a retained game-owned tree, with resource animation bindings and cached draw commands. Other menus need their own count, ownership, and destructor audit. For resource decoding and object layouts, use the optional companion `mhgu-understanding` native GUI reference.

## Plan a different menu before adapting the recipe

Establish the selected resource hash/variant, live instance, animation ID versus table row, owned object range and sequence bindings. Node names and file presence do not establish a spare rendering mechanism. The corrected hud0 case has `Anm_sharp` selecting animation ID 4 at row 7. Its apparent `sgauge` candidates belong to stamina, and `Txt_mask05..55` belong to `h_hand`.

Use the companion's native GUI identity table when researching that fixture. At runtime (World Sharpness Gauge r9 Eden log, 2026-10-22), `Txt_sharp`, `Txt_sharpefx` and the third sharpness texture are siblings whose parent is the gauge controller itself. The file's child indices do not describe this tree: there is no group node, and the glow is not a child of the bar.

Like the counter row, it has a map alias: controller +0xa0 holds the same pointer as instance +0xd8 (r16 log; the insertion's gate has required it on every insert since r18). An earlier zero reading did not hold.

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
3. Run the 12 style setters, each with two integer arguments.
   - Names are from the saved DTI; values are the badge's: `BlendState` `0xa4dc24`=1, `ControlPoint` `0xa4a9f4`=0, `FixFrame` `0xa47a94`=0, `Mask` `0xa4dca0`=0, `Priority` `0xa47a04`=2, `ReferencePosition` `0xa4aa24`=1, `ReferenceRotation` `0xa4aa5c`=1, `ReferenceScaleX/Y/Z` `0xa4aa94`/`0xa4aac8`/`0xa4aafc`=3, `Reverse` `0xa4dc54`=0, `SamplerState` `0xa4fa5c`=0.
   - A zeroed block leaves every `Reference*` property at 0. These are the badge's values: a copy of another sprite takes that sprite's sampler, the low nibble of +`0x108` (the sharpness bar's is 2; a copy left on 0 filtered its edges differently).
4. Run `Texture` `0xa4faf0` last; it returns early while +`0x78` is 0. Then set `mTextureRect` through `0xa4fb58` with a pointer to four floats, and keep using that setter afterwards (see "A texture caches its quad").

The constructor's own defaults include +`0x54` = `0x020a0001` and +`0xb4`/+`0xb8` = 32.0 (main+`0xa4d0d8`). Reading those words back proves only that the constructor ran, not that the node draws. +`0x80`/+`0x84` and +`0xb4`/+`0xb8` are local values, not screen pixels.

A node's rect at +`0xe0` is not its sprite either: the sharpness bar is authored 88x24 with an x scale of 1.0, its rect is 128x128, and its ink was measured ending at 200 px inside the rect's 110..238. No mapping from atlas columns to rect pixels was ever derived, so measure geometry on screen and store it as a fraction of the rect (P7 step 2).

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

Key Quest Markers and WishFinder both add children to the quest counter row, and either may insert first. So the 13-pointer map and 168-byte cache above hold only for a row with no other additions: size both from the live tree each time.

WishFinder takes the map as the live count `0xa38ffc` plus two. It takes the cache as (the resource's drawables + nodes beyond the resource's own + 2) × 16 + 8. That counts every added node as drawable, so a foreign non-drawable node only over-allocates. A build that read the map and cache at fixed sizes crashed beside WishFinder when WishFinder inserted first.

Find your own nodes by their private ID (+`0x50`), never by index.

### Size any row from its own numbers

Root setup `0xa49b28` allocates `(objects << 4 | 8) + sequences * 12` through root vtable slot 0x58 and stores it at root +`0xa4`, with the walker's pointer root +`0x80` = allocation + `sequences * 12`. Both counts are the halfwords at **row+8**, not row+4: the sharpness row reads 3 and 16 there and 4 and 15 at row+4.

- Objects is the node count. The map is one longer, because its first entry is the controller.
- The walker's list is 8 bytes per record plus an 8-byte terminator. A visible drawable node emits an enter and an exit; a hidden one emits neither.
- The grown map comes from the `cGUIInstance` allocator, slot 0x1c with `(bytes, 16)`. Passing no alignment leaves it as register garbage. Publish instance +`0xd8` and root +`0xa0` together.
- A row with sequences has live animation tracks in the prefix: setup (`0xa484c4`) stores each object's slice at +`0x64`, and the row update `0xa4915c` evaluates and writes them every frame. Copy the prefix into the new block and move every map entry's +`0x64` that points into the old prefix to the same offset before freeing the old block; freeing it under them crashed Ryubing at `0xb349c0`.
- Return the old cache through root slot 0x5c, after that move.
- Link last, so a larger tree never exists against the old map, and then set root +`0x8c` bits 0 and 1 (bit 0 rebuilds the walker's list, bit 1 starts the transform walk).

The game allocates a row's map in `FUN_01401bc0` and frees it in `0xa38828` (`setAnimationId`) through the same class allocator. World Sharpness Gauge still leaks the old 16-byte block, a shortcut from before that was read.

## Art, colour and paired nodes

- The game multiplies the vertex colour (`0xa4e0b8`, `0xAABBGGRR`) with the texel, so tintable art must be white or grey. Coloured art (WishFinder tried the yellow flag on `HD_lobby00`) cannot take a source colour.
- Use an atlas the row's resource already loads, and check the cell in every language's atlas: item icon cell 9 (ore) is drawn differently in the German, Italian and Spanish `HD_cmn_icon_GSM_NOMIP` than in English. Modern Weapon Controls replaces that atlas with a double-size copy, so take the size from the texture header (`mhgu-understanding` resources reference).
- Nodes that only work together (WishFinder's shadow and pin) are created together or not at all, on one rect. Link the one painted first first, and give both a Priority above the row's own (the counter row uses 0..2, WishFinder 3 and 4) so the `0xa4915c` re-sort keeps that order.
- A row that does not need the decoration gets no children, so the native tree stays the game's own on every other row.

Worked example: WishFinder's [quest rows](../../../../mods/wishfinder/docs/worked/wishfinder-quests.md) and [smithy page](../../../../mods/wishfinder/docs/worked/wishfinder-smithy.md) (the smithy's `cUIOFacilityShopMenu` rows are `shop_menu.gui` animation 25, four drawables, no cache prefix).

## Material, geometry, and title fitting

Decode `INIT_PARAM` kinds 17/18 as immediate boolean/u32 values. Treating them as section offsets concealed the real material state. `Mask=0` is normal colour drawing; Mask 1 enters mask-writing even when Visible and vertex colours are correct.

For clipping, establish both the mask writer and consuming material/draw, their coordinate space and order, cache invalidation and mask reset/restoration before unrelated HUD draws. Parenting a Mask1 object alone proves none of those. Test empty, partial and full fill with unchanged texture proportions, aligned effect layers and preserved outlines as required. A resource fallback must meet the same continuous-fill contract and preserve unrelated entries.

Reuse texture descriptors the row already loaded and native logical atlas coordinates; logical coordinates need not match physical HD image pixels. Validate the live descriptor, dimensions and texture pointer, and ship no extracted texture or replacement ARC.

Place a decoration from the row's own objects and their live visibility (+`0x54` bit 0 after the native update), not from fixed offsets. Key Quest Markers' badge geometry, title widths and colours are its contract: [its page](../../../../mods/key-quest-markers/docs/worked/quest-badges.md).

Title binding 4/ID 6 is `cGUIObjMessage`, CRC `0x2fb82eae`, size 352. It is not `cGUIObjText` size 384. Derive fixture classes and getDTI from the real resource. Common setter addresses alone do not prove a subclass. Native Size/AutoScale setters need the glyph-cache dirty bit at +`0xf0` bit 16. Restore the original title size/AutoScale before a reusable row can exit early on missing metadata.

Do not apply the title Size `0xa53528` or AutoScale `0xa53348` contract to Texture objects. Saved Texture DTI's Size entry has a getter and no setter. Check callback direction, actual class fields, native body and ABI before choosing a property operation. Getter-only metadata does not rule out a different verified geometry path.

Copy any applied settings (colours and the like) out once per row; do no file I/O or settings locking in the hook.

## Verify the full route

Trace handshake, original trampoline, hook entry, resource identity, attachment, classification, material dispatch, geometry, and visible output. Existing ARM fixtures execute native construction, getDTI, setters, prepaint, Texture Draw, quad generation, traversal, and cleanup. They caught wrong subclasses and mask branches that simpler draw-callback doubles missed.

Mocked GPU commands/allocations establish no actual clipping or pixels. Manual acceptance checks opening, scrolling, selection, request overlap, confirmation, closing/reopening, and scene transitions. Preserve successful payload hashes. A visible bit or successful plugin load does not establish a working GUI.
