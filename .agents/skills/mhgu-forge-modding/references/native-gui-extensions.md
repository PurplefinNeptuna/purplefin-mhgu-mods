# Extend the game's native GUI

This recipe is established for the quest counter row in MHGU Switch 1.4.0. It is a retained game-owned tree, with resource animation bindings and cached draw commands. Other menus need their own count, ownership, and destructor audit. For resource decoding and object layouts, use the optional companion `mhgu-understanding` native GUI reference.

## Plan a different menu before adapting the recipe

Establish the selected resource hash/variant, live instance, animation ID versus table row, owned object range and sequence bindings. Node names and file presence do not establish a spare rendering mechanism. The corrected hud0 case has `Anm_sharp` selecting animation ID 4 at row 7. Its apparent `sgauge` candidates belong to stamina, and `Txt_mask05..55` belong to `h_hand`. Use the companion's native GUI identity table when researching that fixture. At runtime (Modern Sharpness Gauge r9 Eden log, 2026-10-22), `Txt_sharp`, `Txt_sharpefx` and the third sharpness texture are siblings whose parent is the gauge controller itself. The file's child indices do not describe this tree: there is no group node, and the glow is not a child of the bar. Unlike the counter row, the controller carries no map aliases at +0xa0/+0xa4.

Before adding a child, identify the target menu's construction/update/draw/destruction paths, every affected count/map consumer, map aliases, cache prefix and capacity, allocation/free pairing and publication order. Derive its sizes from those paths. The 13-pointer map and 168-byte cache below are quest-row results, not reusable HUD constants. Resource counts alone do not establish runtime capacity. Prepare allocations before publishing, preserve original bindings, avoid duplicate insertion and verify failure cleanup.

Choose an update point after the final native write and before transform/draw-cache construction for the properties being changed. Keep pointers inside a verified owner lifetime. A HUD may disappear, hide or be recreated across weapon/scene changes, and on every area transition inside a quest (each one has a loading screen). Establish how the plugin restores its overrides while objects remain valid and reacquires new objects without retaining stale pointers. Include exit/re-entry and recreation in validation even if initial drawing works.

Keep the user's visual design distinct from mechanism feasibility. Mark unresolved masking, ownership or field contracts as research work. A plan is not ready for native mutation merely because the quest-row example worked.

## Attach at the correct lifecycle point

The normal row builder at main+`0x616cb0` has seven integer/pointer arguments. Call its original first, then decorate the completed row. Parent controller `0x54d030` has two pointer arguments and supplies synchronous offer context through guarded TLS. Keep native pointers local to that callback.

Validate native GUI identity, root/object class, IDs, owners, descriptor, map aliases, and bounded child traversal. The audited row is animation 20 with twelve lookup objects, fifteen sequences, nine drawables, and sixty-three resource instances. Reject conflicting IDs and cycles. A private marker ID `0x4b514d33` permits finding an existing owned child instead of allocating each frame.

## Allocate for the destructor that will run

`cGUIObjTexture` is 304 bytes. Use its DTI's MT allocator, verified alignment, and native constructor main+`0xa4f60c`. DTI allocator lookup is main+`0x7aa47c`; its allocator vtable uses alloc+`0x20` and free+`0x34`. The Texture DTI has only three virtual slots; vtable+`0x0c` is null, so the generic instantiate wrapper cannot supply a placement constructor here. Forge malloc is not the allocator expected by the native destructor.

Initialize geometry, material, texture, visibility, parent/owner/resource links before publication. Object +`0x74` is the owning `cGUI`, obtained from instance+`0x6c`; it is not the instance. Object +`0x78` borrows the `rGUI` resource. Scoped guards destroy/free unpublished objects if any allocation or validation fails. Native helper `0xa4844c` links siblings and parent.

The Key Quest Markers badge (`create()` in `mods/key-quest-markers/src/gui.rs`) is the only standalone Texture node that has drawn in-game. Build a new one with every step it takes, in this order, and name the native code that makes any skipped step unnecessary:

1. Allocate 304 bytes through alloc+`0x20` with `(bytes, 16, dti id)`, zero the block, then run constructor main+`0xa4f60c` with the storage in r0.
2. Write +`0x50` (a private ID), +`0x74` (owner) and +`0x78` (resource). Modern Sharpness Gauge also needed a live sibling's +`0x64`, because the `Texture` resolve scans `*(obj+0x64)+0xe8` (main+`0xb80fd0`). Without it, its r46 copy was refused at the texture step.
3. Run the 12 style setters, each with two integer arguments. Names are from the saved DTI; values are the badge's: `BlendState` `0xa4dc24`=1, `ControlPoint` `0xa4a9f4`=0, `FixFrame` `0xa47a94`=0, `Mask` `0xa4dca0`=0, `Priority` `0xa47a04`=2, `ReferencePosition` `0xa4aa24`=1, `ReferenceRotation` `0xa4aa5c`=1, `ReferenceScaleX/Y/Z` `0xa4aa94`/`0xa4aac8`/`0xa4aafc`=3, `Reverse` `0xa4dc54`=0, `SamplerState` `0xa4fa5c`=0. A zeroed block leaves every `Reference*` property at 0.
4. Run `Texture` `0xa4faf0` last; it returns early while +`0x78` is 0. Then set `mTextureRect` through `0xa4fb58` with a pointer to four floats.

The constructor's own defaults include +`0x54` = `0x020a0001` and +`0xb4`/+`0xb8` = 32.0 (main+`0xa4d0d8`). Reading those words back proves only that the constructor ran, not that the node draws. +`0x80`/+`0x84` and +`0xb4`/+`0xb8` are local values, not screen pixels. Before converting a screen measurement into them, find which node in the parent chain carries the scale (the sharpness bar is authored 88 wide and drawn 128 px wide).

The alternative is to copy a live sibling of the same class byte for byte. That carries every style field. Then replace the ID, clear the +`0x68`/+`0x6c`/+`0x70` links and the animation binding, and link the copy with the native linker.

When a new node becomes the parent of existing nodes, the draw walker main+`0xa494a0` decides the result. It descends +0x68, moves along +0x6c, and when a sibling is 0 it pops to that node's +0x70. It writes a node's exit entry only when a pop lands on that node. So a moved node's old sibling link and its parent link both decide whether the new parent's exit entry is ever written. Run a walker port over the tree after your writes before you trust it (playbook P2 step 5). An enter entry with no matching exit leaves masks and other state active for every draw that follows.

Appending a child requires both storage expansions:

| Storage | Original | Extended | Contract |
| --- | --- | --- | --- |
| Lookup map | 12 pointers | 13 pointers | Keep original indices, append static child; publish instance+0xd8 and root +0xa0 |
| Draw cache | 152 bytes | 168 bytes | Zero secondary prefix, `drawableCount*16+8`, 9 becomes 10 |

The map uses the instance's MT allocator. Cache allocation must match the native cache-free/destructor path. Fully prepare replacement allocations, publish aliases/cache/tree coherently, mark sorting/transform/draw state dirty, and free replaced storage at the verified point. The native root/instance recursively destroy the child, map, cache, and graphics allocations. No extra destructor hook is required for this audited static addition.

The count getter `0xa38ffc` counts the linked tree, while cleanup `0x5456e4` indexes the runtime map to that count. A 13-node tree with a twelve-entry map froze the game. Enlarging only the cache does not fix it. Original resource descriptors, first twelve animation bindings, and sequences remain unchanged. An animated addition may need another design.

## Material, geometry, and title fitting

Decode `INIT_PARAM` kinds 17/18 as immediate boolean/u32 values. Treating them as section offsets concealed the real material state. `Mask=0` is normal colour drawing; Mask 1 enters mask-writing even when Visible and vertex colours are correct.

For clipping, establish both the mask writer and consuming material/draw, their coordinate space and order, cache invalidation and mask reset/restoration before unrelated HUD draws. Parenting a Mask1 object alone proves none of those. Test empty, partial and full fill with unchanged texture proportions, aligned effect layers and preserved outlines as required. A resource fallback must meet the same continuous-fill contract and preserve unrelated entries.

Reuse loaded texture descriptors and native logical atlas coordinates. The audited fixture uses texture 22, white lobby emblem rectangle `(136,344,198,406)`. Logical coordinates need not match physical HD image pixels. Validate the live descriptor, dimensions, and texture pointer. This ships no extracted texture or replacement ARC. The English HD archive is a build fixture; user confirmation on 2026-10-15 establishes r17 working with base game and optional HD.

Accepted original-emblem geometry: 32×32, Y 3, X 365 for a free request slot or X 329 before an occupied bubble. The original request object ID 20/index 3 occupies X 365..397. Its actual visibility comes from +`0x54` bit 0 after the native update. Preserve the four-pixel gap and title widths 299/263. Earlier 24px, outside-row, small-emblem, yellow, and purple variants are historical.

Title binding 4/ID 6 is `cGUIObjMessage`, CRC `0x2fb82eae`, size 352. It is not `cGUIObjText` size 384. Derive fixture classes and getDTI from the real resource. Common setter addresses alone do not prove a subclass. Native Size/AutoScale setters need the glyph-cache dirty bit at +`0xf0` bit 16. Restore the original title size/AutoScale before a reusable row can exit early on missing metadata.

Do not apply the title Size `0xa53528` or AutoScale `0xa53348` contract to Texture objects. Saved Texture DTI's Size entry has a getter and no setter. Check callback direction, actual class fields, native body and ABI before choosing a property operation. Getter-only metadata does not rule out a different verified geometry path.

Current r17 colours are Green `#006305`, Red `#A30000`, Grey `#808080`, with custom saved RGB preserved. Copy the three applied atomics once per row; do no file I/O or settings locking in the hook.

## Verify the full route

Trace handshake, original trampoline, hook entry, resource identity, attachment, classification, material dispatch, geometry, and visible output. Existing ARM fixtures execute native construction, getDTI, setters, prepaint, Texture Draw, quad generation, traversal, and cleanup. They caught wrong subclasses and mask branches that simpler draw-callback doubles missed.

Mocked GPU commands/allocations establish no actual clipping or pixels. Manual acceptance checks opening, scrolling, selection, request overlap, confirmation, closing/reopening, and scene transitions. Preserve successful payload hashes. A visible bit or successful plugin load does not establish a working GUI.

Sources: `mods/key-quest-markers/src/{gui.rs,native.rs,offers.rs}`, `mods/key-quest-markers/scripts/gui_layout.py`, `tests/{resource.py,native_adapter.py,arm.py}`, `research/theme-colours.json`, `DEVELOPMENT.md`, `EVIDENCE.json`; `docs/RESEARCH.md`. Read current source/r17 records before historical r3 through r16 narratives.
