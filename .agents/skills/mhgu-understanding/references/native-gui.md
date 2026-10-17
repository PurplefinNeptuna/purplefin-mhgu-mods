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

Sources: `docs/RESEARCH.md`; `mods/key-quest-markers/{DEVELOPMENT.md,EVIDENCE.json}`, `src/gui.rs`, `mods/key-quest-markers/scripts/gui_layout.py`, `tests/{resource.py,native_adapter.py}`, `research/theme-colours.json`; `mods/please-do-better/DEVELOPMENT.md` native geometry/shader findings.
