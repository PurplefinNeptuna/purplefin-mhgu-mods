# Masks, cached quads, HUD movers and row lifetime

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

So use the setter. `mTextureRect` `0xa4fb58(node, *f32[4])` returns at once when the floats match, otherwise stores them, calls slot 0x28 when `+0x108 & 0x30`, and tail-calls slot 0x50. Calling it every frame is cheap.

A raw write to +`0x10c` reads back perfectly and never repaints: the copy kept the band the first build left while a read-back showed the write landing on all 73 fill lines. Inference: raw colour writes after the first build are inert the same way, so use the `VertexColor*` setters.

Position and authored-size writes after the build were also inert (`pos=90.0 0.0 size=0.7 24.0` with `rect=110 38 238 166`, mechanism unread), so move geometry with a mask.

## HUD movers (gu-native and UIScale)

Two things move HUD quads after the game has drawn them. Any placement a mod computes from node fields, rects or the node's own matrix is then the unmoved place.

| Mover | What it does | Source |
| --- | --- | --- |
| gu-native's renderer | Rewrites every GUI quad's uploaded matrix, anchored by that quad's own layer and position; moves the game's scissor only vertically | gu-native `runtime/nvn/vulkan/exec.c`, the `pos_z = m[14]` read and `scissor_rect` (local `9a1aef7`; first read at `c7fc45a`) |
| UIScale (KatLib) | Edits a sprite in the uploaded matrix block at `*(ctx+4)+0x18bc` after publishers main+`0xa4eb9c`/`0xa3e3b0`. The node's `+0x10` stays unscaled. Its own `+0xe0` rewrite refreshes only on a rebuild | World Sharpness Gauge *Following a rescaled bar* |

gu-native's rule, per quad: the anchor (left, right or centre; top, bottom or centre) comes from layer `m[14]` and position `m[12]`/`m[13]` on the 1280x720 canvas. Special cases: the layer 103 status HUD at y < 500 goes left/top and the item bar right/bottom, and layer 105 is the minimap. The quad is scaled by `s = (16/9)/aspect` and `sy = aspect/(16/9)`, so at exactly 16:9 nothing moves except what the touch layout moves (item bar, Arts, target). The scissor moves only vertically at 16:10 (`ui_scissor_v`) or is relaxed for the item bar, never with the status pieces.

Rules:

1. **Cut a sprite in its own geometry, at its draw.** The texture draw main+`0xa4fc9c` uploads `node+0x10` (main+`0xa4fd10`/`0xa4fd38`) and rebuilds the UVs from the `[u1, v1, u2, v2]` window later in the same call (main+`0xa4fe44`). In a hook on it: scale m[0], move m[12], set the window through the setter, call the original, then put m[0] and m[12] back.
   - The quad's local x span is the float authored width at +`0xb4` with anchor +`0xa0 & 3` (0: `0..w`, 1: centred, 2: `-w..0`; main+`0xa4ff1c..0xa4ffb4`), not the layout width at +`0xd8`. A mover then moves the cut with the sprite (World Sharpness Gauge `crop_span`; accepted on MHGURecomp, not run on gu-native).
2. **Read where a sprite really went after the original draw**, from the uploaded block. Words 0, 1, 4, 5, 12 and 13 equal to the node's mean a plain draw; an unchanged block address means nothing was uploaded. This sees UIScale; it cannot see gu-native, which moves the quad later, on the host.
3. **A node you add moves by its own position, not its parent's,** on gu-native (inference from the per-quad rule above). Keep added nodes on the same layer and inside the same position band as the part they belong to, or they split from it on a non-16:9 screen.
4. **An ImGui overlay never moves with the HUD.** Do not place ImGui drawing from HUD node positions if it must line up on gu-native. World-space overlays are a separate problem: [Runtimes](runtimes.md#imgui-on-each-host).
5. **Test what you can reach.** Nobody here runs gu-native. UIScale on MHGURecomp is the reachable mover: run the quest with a non-default scale, and ask the tester to drag the element in UIScale's editor (a live drag is still unconfirmed for World Sharpness Gauge). Report gu-native as source-only.

## Survive a row's end

The sharpness gauge's row lasts a quest (inference, see Lifecycle in [the gauge's page](../../../../mods/world-sharpness-gauge/docs/worked/sharpness-gauge.md#accepted-shape)), other rows are unmeasured, and `cGUIObjRoot`'s destructor has fired in no saved log.

- Detect the death from a callback that keeps running. A freed mask's enter stops being called, so a check placed only there goes silent. Check from the draw walker: read-only, the marker, the mask's parent against the root and the root's child against the mask. On failure, drop every captured address and re-arm discovery, so the next row is read and inserted like the first.
- Write only where the game hands over a live object. In the mask's enter, when the links are gone, turn the mask off and drop the addresses. Left alone, it keeps applying its last box.
- Every HUD instance calls the walker, so capture the pair whose instance +`0xdc` is the controller you identified, not the last one seen. The walker has two entries: `0xa39300` calls it at `0xa39664`, and `0xa56a14` tail-branches with node +`0xcc`.

## The sharpness gauge's measured cut and fill

The bar's length is the fill inside the band its points sit in: `(current - floor) * 10_000 / (ceiling - floor)`. Here `floor` is the top of the tier below (0 in tier 0), and `ceiling` is the top of this tier clipped to `mMaxSharpness`. So the bar refills at every colour, and a raised maximum reads full partway through its tier. Publish that fill directly: "the need is approximation, so jumpy is okay, no need for fancy smooth animations or lerp" (tester). Colour comes from the game, and a ratio can never pick the tier.

Not derived from the atlas. The accepted cut runs 128 to 200 px on the 110..238 rect, the tester's measurement, carried as offsets 18 and 90 of the rect's 128. The ink measured 124..200 px on screen, with a few px of noise from downscaled screenshots.
