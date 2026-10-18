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

Other kinds need their own native decoding. Treating 17/18 as offsets made icon parameters appear mostly 1, concealing `Mask=0`. Mask 1 writes masks. Normal coloured texture rendering requires the actual material path as well as visibility and vertex colours.

## Establish GUI identity before proposing reuse

For a target resource, record the copied file hash, source ARC/entry and known base/HD/language variant. Resolve the live instance, its `AnimationId`, the matching animation ID, that record's table row, object range and sequence bindings. Keep object IDs, lookup indices, animation IDs and table rows in separate columns. A string scan can match an unrelated value that happens to equal a string offset. Confirm the actual field semantics before interpreting a match.

Follow ownership from the selected animation's object range and verified hierarchy fields. Do not classify an object as unused or hidden because it exists elsewhere in the file, or interpret numeric name suffixes as percentages. Default Visible values do not establish final visibility after animation/native updates. Sequence length alone does not establish interpolation, triggers or visible effects. Describe unknown runtime behaviour as a research question.

### Corrected hud0 sharpness example

The inspected copy `work/sharp-gauge-research/hud0.gui` has SHA-256 `5966122d6a28b1ba57007d06adb9927f5328c37637e7c6b04c67d76c40298fb9`. Its original ARC/entry and base/HD provenance remain unrecorded. These are fixture findings, not proof of every installed HUD or game variant:

| Animation name | ID | Zero-based row | Object rows | Objects relevant to reuse |
| --- | --- | --- | --- | --- |
| `h_hand` | 10 | 1 | 3..15 | `Txt_mask55` through `Txt_mask05` |
| `stami_frame` | 3 | 5 | 24..26 | `Txt_sgauge1`, `Txt_sgauge0` |
| `stami_gauge` | 6 | 6 | 27..28 | `Pol_sgauge` |
| `sharp` | 4 | 7 | 29..32 | Root, `Txt_sharp`, `Txt_sharpefx`, `Txt_sharpEdge` |
| `pl_gauge0` | 7 | 8 | 33..38 | Other player HUD objects |

`Anm_sharp` selects ID 4, not ID 7. The sharp resource counts are four objects, fifteen sequences and three drawables. The stamina tiling texture is `Txt_sgauge1` at 960×16. `Txt_sgauge0` is 24×16, and `Pol_sgauge` is 960×4. The `Txt_mask` objects belong to `h_hand`, not the sharpness animation, and their names do not establish 5% steps. Do not expose or repurpose these objects as dormant sharpness machinery.

Reproduce identity checks using `mods/key-quest-markers/scripts/gui_layout.py:Gui`: animation records use table `(40,164,24)`, ID at +0, counts as three little-endian 16-bit fields at +4, first object at +12, name offset at +16 and first sequence at +20. Objects use table `(48,172,36)`, ID at +0, name offset at +16 and properties at +24/count byte +4. Instances use `(68,188,36)`, name at +20 and properties at +28/count +16. Decode the instance's `AnimationId` property and match the animation's ID explicitly. Keep serialized tree-link offsets distinct from runtime object links. The scratch `parse_hud0.py`, `parse2.py` and `decode.txt` are exploratory output, not an independent native audit.

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
| +0x54 | Visibility/draw/dirty flags |
| +0x68 / +0x6c / +0x70 | First child / next sibling / parent |
| +0x74 / +0x78 | Borrowed owning cGUI / rGUI resource context |
| Texture +0x80 / +0x84 | Local X/Y floats |
| Texture +0xb4 / +0xb8 | Width/height floats |
| Instance +0x6c | Owning cGUI source |
| Instance +0xd8 / +0xdc | Runtime object map / owned root |
| Root +0x9c / +0xa0 | Original descriptor / live map alias |
| Root +0xa4 / +0x80 | Owned draw-cache allocation / command-list start |
| Root +0x8c bits 1/2 | Draw-list/transform dirty state |

Object +0x74 does not point to the animation instance. Native factory `0xa38bc0` establishes owner/resource links. Holder lookup uses the primary table at +0xf8/count +0x298 and the alternate table +0x294 for higher indices. Counter row instances 16..23 have their own maps/root objects.

Native count getter `0xa38ffc` counts the tree. Cleanup `0x5456e4` indexes the map to that count. A child addition changes both, even if sequence descriptors stay unchanged. With secondary prefix count zero, root setup `0xa49b28` allocates `drawableCount*16+8`: nine drawables 152 bytes, ten 168. Another animation may have a nonzero prefix and need a different calculation.

The optional Forge skill's GUI-extension reference owns the allocation/publication procedure. Its verified lesson is to preserve original bindings while expanding tree/map/cache together, with allocation matched to the native destructor. Native texture DTI has three slots; there is no placement constructor at +0x0c.

## Coordinates, colours, and drawing

Loaded texture 22 identifies the audited white lobby emblem at logical rectangle `(136,344,198,406)`. Logical resource coordinates can differ from HD image pixels. The r17 reference draws 32×32 at Y 3 and X 365/329 according to request visibility; title widths 299/263 preserve the gap. These are counter-specific geometry values, not general GUI constants.

Size/AutoScale updates also need title +0xf0 bit 16 to rebuild glyph caches. Parent/root transform and sorting dirty state must be updated after structural changes. Some float setters use hard-VFP s-register arguments.

The resource theme audit traces Gathering Green `#006305` and objective Red `#A30000` to native properties. The objective instance overrides its shared Message template. Slaying category Red `#CC0000` is a separate colour. Current badge user labels are Green/Red/Grey, with completed Grey `#808080`. Historical yellow/purple badge palettes are superseded.

Reward world-quad helper `0xa4b390` combines anchors +0xa0, size +0xb4, matrix +0x10, direction bit 0x40 at +0x56, and hard-VFP scale s0. Scissor `0xa37c1c` applies draw offsets/scales and viewport intersections; sentinel fallback is at `0xbc12d8..0xbc1364`. A computed world quad does not establish framebuffer coordinates. The exact shader/constant-buffer route remained unresolved in that experiment.

Verify constructor, setters, material dispatch, quad output, traversal, and destruction using original ARM bodies. GPU doubles prove no actual pixels/clipping. Counter r17 visible acceptance is scoped to dated Eden/Linux user reports with optional HD, not every menu/language/platform.

For a fill/clipping proposal, trace mask production, the consuming draw/material, coordinate transforms, ordering, cached commands and mask reset before unrelated draws. A Mask1 child does not establish that its parent or siblings consume the mask. Changing Size/scale alone can distort a textured shape. Verify geometry and sampling together, including effect layers and an uncut outline where required. Use empty, partial and full ratios to expose incorrect clipping, then require real pixels for visual acceptance. Reusing discrete resource frames must still satisfy a requested continuous fill.

Player-field names are also research leads. For a current/max display, verify signedness, units, maximum semantics, recovery/buff paths, local-player selection and HUD absence/recreation. Specify positive-denominator and floating-point division rules before clamping. Unsupported data should preserve or restore native visuals within valid object lifetimes.

HUD correction sources: hash-identified `work/sharp-gauge-research/hud0.gui`, decoded with the counter parser; saved `work/research-tooling/dti/dti.jsonl` object-vtable Texture properties. Private fixture paths are optional verification inputs when this skill is copied elsewhere.

Sources: `docs/RESEARCH.md`; `mods/key-quest-markers/{DEVELOPMENT.md,EVIDENCE.json}`, `src/gui.rs`, `mods/key-quest-markers/scripts/gui_layout.py`, `tests/{resource.py,native_adapter.py}`, `research/theme-colours.json`; `mods/please-do-better/DEVELOPMENT.md` native geometry/shader findings.
