# GUI walker, coordinates, colours and drawing

## Draw walker and row storage

Draw walker `0xa494a0`: with root +0x8c bit 0 set, it rebuilds an 8-byte record list, `(0,node)` on entry when drawable, `(1,node)` on exit, `(2,…)` to end. It descends +0x68, follows +0x6c, pops to +0x70 on a zero sibling, and stops when the next node is the root. It then consumes the list in order: kind 0 calls slots 0x38 and 0x3c, kind 1 calls slot 0x40. Slot 0x38 on a texture is `0xa4e628`, on a scissor mask `0xa4ba94`.

Object +0x74 does not point to the animation instance. Native factory `0xa38bc0` establishes owner/resource links. Holder lookup uses the primary table at +0xf8/count +0x298 and the alternate table +0x294 for higher indices. Counter row instances 16..23 have their own maps/root objects.

Native count getter `0xa38ffc` counts the tree. Cleanup `0x5456e4` indexes the map to that count. A child addition changes both, even if sequence descriptors stay unchanged. Root setup `0xa49b28` allocates `(objects << 4 | 8) + sequences * 12` from the halfwords at row+8: with no sequences that is `drawableCount*16+8`, nine drawables 152 bytes, ten 168; the sharpness row's 3 and 16 give 248.

Growing a row means preserving original bindings while expanding tree/map/cache together, with allocation matched to the native destructor. Native texture DTI has three slots; there is no placement constructor at +0x0c.

## Coordinates, colours, and drawing

Loaded texture 22 is the white lobby emblem at logical rectangle `(136,344,198,406)` in the counter row's atlas; logical resource coordinates can differ from HD image pixels.

Size/AutoScale updates also need title +0xf0 bit 16 to rebuild glyph caches. Parent/root transform and sorting dirty state must be updated after structural changes. Some float setters use hard-VFP s-register arguments.

The resource theme audit traces Gathering Green `#006305` and objective Red `#A30000` to native properties. The objective instance overrides its shared Message template. Slaying category Red `#CC0000` is a separate colour.

Message text is `cGUIObjMessage`, set through `0x547564`, as `0x56fc28`, `0x56e808` and `0x56ea08` do.

- A `\r\n` breaks the line, as quest GMD text does (`questData_*`).
- A text runs past its layout `Size` instead of clipping. `counter_down` `Mes_name01`, sized for one line, drew eleven lines (run).
- `<COL RRGGBBAA>...</COL>` in a plain string colours it. `<COL 4E320BFF>` gave the panel's value brown in a label (run), and DialogMsg 99 uses the same tag.

A `TexSet` object (type `0x4f7228fc`) draws several boxes from one texture as one object, so one of its bands cannot be hidden alone. Its record's word at +32 is an offset into the float section named by header word 280. There the boxes are (x0, y0, x1, y1) after an 8-byte lead. In `menu_questconfirm`, page 3 has two bands (0, 0, 426, 34) and (0, 80, 426, 114), and page 2's `TexSet_bg2` has (0, 0, 426, 34) alone. The format is read off these records and is inference for others.

Reward screen frames: layout setup `0x623a6c` starts sequence `0xf4242` plus a variant on the group's background root (`0x56e538` -> `0x546c74` -> root `0xa3896c`, which restarts only on a different ID); that colours Base rows red and Wound/Cap rows blue.

A Base frame's corners hold `0xa02337dc` (R 0xdc, G 0x37, B 0x23, alpha 0xa0) over a light texture, so a white vertex colour shows the texture itself. The cursor's yellow cell comes from a path not yet read.

Shaders: `root.arc` holds one shader resource of 58,841,740 bytes unpacked (ARC sizes are the low 29 bits of the flags, `flags & 0x1fffffff`); loader `0xce1fbc` checks SPK magic, version 0x26 and shader version `0xb2d34c60`. The exact GUI vertex program and constant-buffer bindings are unresolved.

Reward world-quad helper `0xa4b390` combines anchors +0xa0, size +0xb4, matrix +0x10, direction bit 0x40 at +0x56, and hard-VFP scale s0. A scissor mask's enter calls the same builder with its own node and its +0xa8/+0xac size, so its box starts at its own +0x40/+0x44 translation.

Scissor `0xa37c1c` applies draw offsets/scales and viewport intersections, writes the render target's scissor at target +0xe4..+0xf0 and stores the request at context +0xd0..+0xdc (one Eden run read the box at x1.5 there); sentinel fallback is at `0xbc12d8..0xbc1364`. A computed world quad does not establish framebuffer coordinates.

The exact shader/constant-buffer route remained unresolved in that experiment.

For screen-space work: texture draw `0xa4fc9c` reaches `0xa4fe50` after it builds a quad's vertices. GUI publishers `0xa4eb9c` and `0xa3e3b0` supply model matrices and `0xa397d4` the globals (CBGUIMatrix 0x2d7, CBGUIGlobal 0x2d6 at renderer +0x18bc/+0x18b4). The sentinel rectangle is read through relocated GOT main+`0x183f2b0` (offline main+`0x191eaa0`).

The game's NVN present wrapper ends at `0x86a330` (`mov r0,r12; bx r3`); `0x86a28c` records the acquired resource at owner +0x48cc, whose NVN texture is resource +0x3c. Downsample gateways `0xbbfb08`/`0xbbfb44` (GOT main+`0x18418f8`) never ran for reward geometry.

A reward frame's per-vertex setter `0xa4e0b8` stores +0xa4 + 4 * vertex and marks the quad dirty, and nothing rewrites a frame's colour until the next reward screen.

Verify constructor, setters, material dispatch, quad output, traversal, and destruction using original ARM bodies. GPU doubles prove no actual pixels/clipping.

For a fill/clipping proposal, trace mask production, the consuming draw/material, coordinate transforms, ordering, cached commands and mask reset before unrelated draws. A Mask1 child does not establish that its parent or siblings consume the mask. Changing Size/scale alone can distort a textured shape. Verify geometry and sampling together, including effect layers and an uncut outline where required. Use empty, partial and full ratios to expose incorrect clipping, then require real pixels for visual acceptance. Reusing discrete resource frames must still satisfy a requested continuous fill.

Player-field names are also research leads. For a current/max display, verify signedness, units, maximum semantics, recovery/buff paths, local-player selection and HUD absence/recreation. Specify positive-denominator and floating-point division rules before clamping. Unsupported data should preserve or restore native visuals within valid object lifetimes.

HUD correction sources: hash-identified dump `nativeNX/eng/GUI/01_quest/hud/hud0.gui`, decoded with the counter parser; saved `work/research-tooling/dti/dti.jsonl` object-vtable Texture properties. Private fixture paths are optional verification inputs when this skill is copied elsewhere.
