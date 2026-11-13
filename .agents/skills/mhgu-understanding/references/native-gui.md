# Native GUI resources and objects

MHGU's inspected menus use retained native objects. Resource instances and sequences establish object lookup/bindings; native updates modify state, transform traversal builds draw commands, and native ownership destroys the tree. Sizes and fields here are verified for the Switch 1.4.0 counter reference.

## Resource interpretation

The counter fixture is `eng\GUI\05_meeting_p\count\counter`, GUI magic `GUI\0`, version 141077. Animation 20 has twelve lookup objects, fifteen sequences, nine drawables, and sixty-three resource instances. File-relative table offsets differ from runtime pointers after native fixups.

The parser checks header length/size, count×stride bounds, string termination, and property-section bounds. Property meaning comes from native loader main+`0xb7f988` and dispatcher `0xb344f4`.

| INIT_PARAM kind | Storage in the audited resource |
| --- | --- |
| 1 integer, 2 float, 7 texture ID | Offset into the 32-bit section |
| 3 boolean | Offset into the byte section |
| 4 float4/size/colour/rectangle | Offset into the 128-bit section |
| 17 immediate boolean | Low byte of value, zero/nonzero |
| 18 immediate integer/enum | Value itself |

Other kinds need their own native decoding. Treating 17/18 as offsets made icon parameters appear mostly 1, concealing `Mask=0`. Mask 1 writes masks. The game authors only 0 and 1; modes 1, 2, 4, 5 and modes 3, 6 enter through `0xb375c4` and `0xb38004`. Normal coloured texture rendering requires the actual material path as well as visibility and vertex colours.

## Establish GUI identity before proposing reuse

For a target resource, record the copied file hash, source ARC/entry and known base/HD/language variant. Resolve the live instance, its `AnimationId`, the matching animation ID, that record's table row, object range and sequence bindings. Keep object IDs, lookup indices, animation IDs and table rows in separate columns. A string scan can match an unrelated value that happens to equal a string offset. Confirm the actual field semantics before interpreting a match.

Follow ownership from the selected animation's object range and verified hierarchy fields. Do not classify an object as unused or hidden because it exists elsewhere in the file, or interpret numeric name suffixes as percentages. Default Visible values do not establish final visibility after animation/native updates. Sequence length alone does not establish interpolation, triggers or visible effects. Describe unknown runtime behaviour as a research question.

### Corrected hud0 sharpness example

The inspected file is the English base `hud0.gui`, SHA-256 `5966122d6a28b1ba57007d06adb9927f5328c37637e7c6b04c67d76c40298fb9`: the loose dump file `nativeNX/eng/GUI/01_quest/hud/hud0.gui` and the `quest_eng.arc` entry `eng\GUI\01_quest\hud\hud0`. HD Project variants are unrecorded. These are fixture findings, not proof of every installed HUD or game variant:

| Animation name | ID | Zero-based row | Object rows | Objects relevant to reuse |
| --- | --- | --- | --- | --- |
| `h_hand` | 10 | 1 | 3..15 | `Txt_mask55` through `Txt_mask05` |
| `stami_frame` | 3 | 5 | 24..26 | `Txt_sgauge1`, `Txt_sgauge0` |
| `stami_gauge` | 6 | 6 | 27..28 | `Pol_sgauge` |
| `sharp` | 4 | 7 | 29..32 | Root, `Txt_sharp`, `Txt_sharpefx`, `Txt_sharpEdge` |
| `pl_gauge0` | 7 | 8 | 33..38 | Other player HUD objects |

The sharpness row's tier bands, sequences and live identity are in [Sharpness](sharpness.md).

`Anm_sharp` selects ID 4, not ID 7. The sharp resource counts are four objects, fifteen sequences and three drawables. The stamina tiling texture is `Txt_sgauge1` at 960×16. `Txt_sgauge0` is 24×16, and `Pol_sgauge` is 960×4. The `Txt_mask` objects belong to `h_hand`, not the sharpness animation, and their names do not establish 5% steps. Do not expose or repurpose these objects as dormant sharpness machinery.

Reproduce identity checks using `mods/key-quest-markers/scripts/gui_layout.py:Gui`: animation records use table `(40,164,24)`, ID at +0, counts as three little-endian 16-bit fields at +4, first object at +12, name offset at +16 and first sequence at +20. Objects use table `(48,172,36)`, ID at +0, name offset at +16 and properties at +24/count byte +4. Instances use `(68,188,36)`, name at +20 and properties at +28/count +16. Decode the instance's `AnimationId` property and match the animation's ID explicitly. Keep serialized tree-link offsets distinct from runtime object links.

Keyframes (hud0, 2026-10-19). The object×sequence table at header +176 has 16-byte records, object-major, one record per object per sequence: flag byte +0, init-param count +2, keyed-param count +3, frame length u16 +6, init-param index +8, keyed-param index +12. Keyed params at header +184 are 24 bytes: value type +4, key count +5, owning object ID +8, name +12, key index +16, value offset +20. The key table is at header **+264** (+244 is `messageOffset`; both read 48,000 in hud0 only because it has no messages). Each key is 8 bytes with its frame in the first u16. A check over all 1972 dumped `.gui` files found the keyed-param word at +8 always equal to the owning object's ID, so it is not an interpolation mode.

## Classes and identities

| Object | Verified identity / role |
| --- | --- |
| `cGUIObjRoot` | 176 bytes, row root ID 1 |
| Main Null | Lookup index 1, ID 14 |
| `cGUIObjTexture` | 304 bytes, existing icon index 2/ID 12 |
| Request texture | Index 3/ID 20, existing request-bubble visibility |
| `cGUIObjMessage` | 352 bytes, title index 4/ID 6, CRC `0x2fb82eae` |
| `cGUIObjText` | 384 bytes, a different class from the title |

Derive fixture class CRC/getDTI from the selected resource. Shared setter addresses do not identify an exact subclass. A test using the same wrong class assumption can pass while the real title guard rejects every row.

Check the callback direction too. Saved object-vtable DTI for `cGUIObjTexture` exposes a Size getter with setter 0, plus Mask and `mTextureRect` setters. A getter-only DTI property does not prove a native setter exists or that geometry is immutable. The Message Size setter main+`0xa53528` writes title fields +0xc8/+0xcc, while Texture dimensions are +0xb4/+0xb8. Resolve the actual class/body/ABI and dirty flags instead of borrowing a title setter for a texture.

## Runtime fields

| Object-relative offset | Meaning |
| --- | --- |
| +0x50 | Object ID |
| +0x54 | Flag word, bits below |
| +0x60 | Priority, halfword: the sort key when bit 19 is set |
| +0x64 | In a row with sequences, the object's slice of the draw block prefix: row setup `0xa484c4` stores it and writes the object at `+8` of each 12-byte track, and the row update `0xa4915c` evaluates the tracks through it every frame (`0xb349c0`). The `Texture` setter reads `*(obj+0x64)+0xe8` as a `cGUI` texture list. The constructor zeroes it. A replaced draw block must carry these pointers ([native GUI extensions](../../mhgu-forge-modding/references/native-gui-extensions.md)). |
| +0x68 / +0x6c / +0x70 | First child / next sibling / parent |
| +0x74 / +0x78 | Borrowed owning cGUI / rGUI resource context |
| Texture +0x80 / +0x84 | Local X/Y floats |
| Texture +0xa4..+0xb0 | Four corner colours, `0xAABBGGRR` |
| Texture +0xb4 / +0xb8 | Width/height floats |
| Texture +0xc0 bits 24..26 | Vertex cache dirty mark |
| Node +0xe0..+0xec / +0xf0..+0xfc | Rect (a 128x128 box on the sharpness row, not the sprite) / effective rect, four ints |
| Texture +0x100 / +0x104 | Texture ID / resolved texture object |
| Texture +0x108 | Style byte: sampler in the low nibble, bits 4/5 tested by the rect setter |
| Texture +0x10c..+0x118 | Atlas window, four floats `[u1, v1, u2, v2]` |
| Mask +0xa0 low nibble / +0xa4 / +0xa8, +0xac / +0xb0..+0xbc | Anchor modes / bit 0 apply, bit 1 rebuild / size ints / built box |
| Instance +0x6c | Owning cGUI source |
| Instance +0xd8 / +0xdc | Runtime object map / owned root |
| Root +0x9c / +0xa0 | Animation row / live map alias |
| Root +0xa4 / +0x80 | Owned draw-cache allocation / command-list start |
| Root +0x8c bit 0 / bit 1 | Walker rebuilds its record list / transform walk starts (`0xa39c40`) |

Flag word +0x54, read from the bytes on 2026-11-01. The constructor default `0x020a0001` is bits 0, 17, 19 and 25.

| Bit | Evidence and meaning |
| --- | --- |
| 0 | Visible. The walker skips the subtree when clear. |
| 17 | Transform dirty. Transform walk `0xa4964c` calls slot 0x44 (setMatrix) only with this bit (`0xa4969c`). It pushes bits 17 and 24 to children only from a node that has one of them (`0xa496e0`), so a clean parent leaves its subtree on its constructor's matrix. |
| 18 | Cleared by the walker after a node's exit call. Meaning unread. |
| 19 | One-shot child re-sort in `0xa4915c` (tested at `0xa49368`, cleared at `0xa49464`). Not a layout bit. |
| 21 | Set by the transform walk after setMatrix (`0xa496c8`). Meaning unread. |
| 22 | Byte +0x56 bit 6. The texture's enter skips its scissor branch when set (`0xa4e670`). |
| 25 | Drawable. The walker emits enter and exit records on it; byte +0x57 bit 1 is the same bit. |

Draw walker `0xa494a0`: with root +0x8c bit 0 set, it rebuilds an 8-byte record list, `(0,node)` on entry when drawable, `(1,node)` on exit, `(2,…)` to end. It descends +0x68, follows +0x6c, pops to +0x70 on a zero sibling, and stops when the next node is the root. It then consumes the list in order: kind 0 calls slots 0x38 and 0x3c, kind 1 calls slot 0x40. Slot 0x38 on a texture is `0xa4e628`, on a scissor mask `0xa4ba94`.

Object +0x74 does not point to the animation instance. Native factory `0xa38bc0` establishes owner/resource links. Holder lookup uses the primary table at +0xf8/count +0x298 and the alternate table +0x294 for higher indices. Counter row instances 16..23 have their own maps/root objects.

Native count getter `0xa38ffc` counts the tree. Cleanup `0x5456e4` indexes the map to that count. A child addition changes both, even if sequence descriptors stay unchanged. Root setup `0xa49b28` allocates `(objects << 4 | 8) + sequences * 12` from the halfwords at row+8: with no sequences that is `drawableCount*16+8`, nine drawables 152 bytes, ten 168; the sharpness row's 3 and 16 give 248.

The optional Forge skill's GUI-extension reference owns the allocation/publication procedure. Its verified lesson is to preserve original bindings while expanding tree/map/cache together, with allocation matched to the native destructor. Native texture DTI has three slots; there is no placement constructor at +0x0c.

## Coordinates, colours, and drawing

Loaded texture 22 identifies the audited white lobby emblem at logical rectangle `(136,344,198,406)`. Logical resource coordinates can differ from HD image pixels. The r17 reference draws 32×32 at Y 3 and X 365/329 according to request visibility; title widths 299/263 preserve the gap. These are counter-specific geometry values, not general GUI constants.

Size/AutoScale updates also need title +0xf0 bit 16 to rebuild glyph caches. Parent/root transform and sorting dirty state must be updated after structural changes. Some float setters use hard-VFP s-register arguments.

The resource theme audit traces Gathering Green `#006305` and objective Red `#A30000` to native properties. The objective instance overrides its shared Message template. Slaying category Red `#CC0000` is a separate colour. Current badge user labels are Green/Red/Grey, with completed Grey `#808080`. Historical yellow/purple badge palettes are superseded.

Reward world-quad helper `0xa4b390` combines anchors +0xa0, size +0xb4, matrix +0x10, direction bit 0x40 at +0x56, and hard-VFP scale s0. A scissor mask's enter calls the same builder with its own node and its +0xa8/+0xac size, so its box starts at its own +0x40/+0x44 translation. Scissor `0xa37c1c` applies draw offsets/scales and viewport intersections, writes the render target's scissor at target +0xe4..+0xf0 and stores the request at context +0xd0..+0xdc (one Eden run read the box at x1.5 there); sentinel fallback is at `0xbc12d8..0xbc1364`. A computed world quad does not establish framebuffer coordinates. The exact shader/constant-buffer route remained unresolved in that experiment.

For screen-space work: texture draw `0xa4fc9c` reaches `0xa4fe50` after it builds a quad's vertices. GUI publishers `0xa4eb9c` and `0xa3e3b0` supply model matrices and `0xa397d4` the globals (CBGUIMatrix 0x2d7, CBGUIGlobal 0x2d6 at renderer +0x18bc/+0x18b4). The sentinel rectangle is read through relocated GOT main+`0x183f2b0` (offline main+`0x191eaa0`). The game's NVN present wrapper ends at `0x86a330` (`mov r0,r12; bx r3`); `0x86a28c` records the acquired resource at owner +0x48cc, whose NVN texture is resource +0x3c. Downsample gateways `0xbbfb08`/`0xbbfb44` (GOT main+`0x18418f8`) never ran for reward geometry. A Forge hook inside `0xa4fc9c` leaves that per-draw function interpreted for the session on MHGURecomp, so recolour a reward frame natively instead: its per-vertex setter `0xa4e0b8` stores +0xa4 + 4 * vertex and marks the quad dirty, and nothing rewrites a frame's colour until the next reward screen (Please do Better). Host renderers read that uploaded model matrix too: gu-native rewrites each GUI quad's matrix by its own layer `m[14]` and canvas position `m[12]`/`m[13]`, and UIScale edits the block in place; what that means for a plugin is in the Forge skill's native GUI extensions, section HUD movers.

Verify constructor, setters, material dispatch, quad output, traversal, and destruction using original ARM bodies. GPU doubles prove no actual pixels/clipping. Counter r17 visible acceptance is scoped to dated Eden/Linux user reports with optional HD, not every menu/language/platform.

For a fill/clipping proposal, trace mask production, the consuming draw/material, coordinate transforms, ordering, cached commands and mask reset before unrelated draws. A Mask1 child does not establish that its parent or siblings consume the mask. Changing Size/scale alone can distort a textured shape. Verify geometry and sampling together, including effect layers and an uncut outline where required. Use empty, partial and full ratios to expose incorrect clipping, then require real pixels for visual acceptance. Reusing discrete resource frames must still satisfy a requested continuous fill.

Player-field names are also research leads. For a current/max display, verify signedness, units, maximum semantics, recovery/buff paths, local-player selection and HUD absence/recreation. Specify positive-denominator and floating-point division rules before clamping. Unsupported data should preserve or restore native visuals within valid object lifetimes.

HUD correction sources: hash-identified dump `nativeNX/eng/GUI/01_quest/hud/hud0.gui`, decoded with the counter parser; saved `work/research-tooling/dti/dti.jsonl` object-vtable Texture properties. Private fixture paths are optional verification inputs when this skill is copied elsewhere.

Sources: `docs/RESEARCH.md`; `mods/key-quest-markers/{DEVELOPMENT.md,EVIDENCE.json}`, `src/gui.rs`, `mods/key-quest-markers/scripts/gui_layout.py`, `tests/{resource.py,native_adapter.py}`, `research/theme-colours.json`; `mods/please-do-better/DEVELOPMENT.md` native geometry/shader findings.
