# GUI object classes, fields and flags

## Classes and identities

| Object | Verified identity / role |
| --- | --- |
| `cGUIObjRoot` | 176 bytes, row root ID 1 |
| Main Null | Lookup index 1, ID 14 |
| `cGUIObjTexture` | 304 bytes, existing icon index 2/ID 12 |
| Request texture | Index 3/ID 20, existing request-bubble visibility |
| `cGUIObjMessage` | 352 bytes, title index 4/ID 6, CRC `0x2fb82eae` |
| `cGUIObjText` | 384 bytes, a different class from the title |

`cGUIObjMessage` operations (title of the counter row):

| Operation | Address / contract |
| --- | --- |
| AutoScale setter | `0xa53348`, two integers, preserves all but +0xf0 bit 0. Dispatch `0xa42374..0xa423cc`, clamp `0xa449c0` |
| AutoWrap setter | `0xa53324`, two integers, +0xf8 bits 18..19; enum 0 disables wrapping |
| Size setter | `0xa53528`, object and float2 pointer, writes +0xc8/+0xcc |
| FontSize invalidation tail | `0xa5350c`, ORs +0xf0 bit 16 |
| Cached-layout refresh | `0xa53aa8` checks bit 16, calls virtual +0x70, then clears it |
| Message type getter | `0xa56ab8`, GOT input main+`0x183f0b0` |

Size and AutoScale do not invalidate cached glyphs: set +0xf0 bit 16 after a real layout change. The counter title's own values are width 355, height 38, AutoScale 0, AutoWrap 0. The `cGUIObjText` subclass (CRC `0x313f6cc4`, 384 bytes) is a different class.

Allocation and ownership, read from the bytes for the counter row:

- The object map uses `cGUIInstance`'s MT allocator (alloc1 at vft+0x1c, GOT slot `0x18422b4`): built by `0xa38bc0`, destroyed by `0xa38b58`/`0xa38828`. `0xa38828` passes instance+0x6c to `0xa38bc0`, which writes that cGUI owner into every child +0x74.
- Map readers besides cleanup `0x5456e4`: `0x546360`, `0x547a14`, `0x548438`. Count getter `0xa38ffc` calls tree traversal `0xa47d2c` and adds the root.
- The row's draw cache allocator/free (virtual +0x58/+0x5c, `0x540c08`/`0x540c38`) and root destructor `0xa48668` read the same allocator DTI GOT slot `0x183ef98`, so a replacement cache from that allocator is freed correctly.
- `cGUIObjTexture` DTI vtable main+`0x178ff90`: destructors `0x32c` and `0xa568a8`, factory `0xa4f550`, null +0x0c; placement constructor `0xa4f60c`, Polygon base `0xa4d0d8`.
- GUI part helpers: identity `0x546f28`, visibility `0x56e530`, colour `0x56e6fc` (four integer arguments; colour writes all four vertices). The row builder sets the request's visibility through `0x56e530`/`0x545630` -> `0xa47950`, so +0x54 bit 0 is the displayed state right after the builder returns.

Derive fixture class CRC/getDTI from the selected resource. Shared setter addresses do not identify an exact subclass. A test using the same wrong class assumption can pass while the real title guard rejects every row.

Check the callback direction too. Saved object-vtable DTI for `cGUIObjTexture` exposes a Size getter with setter 0, plus Mask and `mTextureRect` setters. A getter-only DTI property does not prove a native setter exists or that geometry is immutable. The Message Size setter main+`0xa53528` writes title fields +0xc8/+0xcc, while Texture dimensions are +0xb4/+0xb8. Resolve the actual class/body/ABI and dirty flags instead of borrowing a title setter for a texture.

## Runtime fields

| Object-relative offset | Meaning |
| --- | --- |
| +0x50 | Object ID |
| +0x54 | Flag word, bits below |
| +0x60 | Priority, halfword: the sort key when bit 19 is set |
| +0x64 | In a row with sequences, the object's slice of the draw block prefix: row setup `0xa484c4` stores it and writes the object at `+8` of each 12-byte track, and the row update `0xa4915c` evaluates the tracks through it every frame (`0xb349c0`). The `Texture` setter reads `*(obj+0x64)+0xe8` as a `cGUI` texture list. The constructor zeroes it. A replaced draw block must carry these pointers. |
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

Code map for HUD rows:

| Part | Address |
| --- | --- |
| Walker | `0xa494a0`, called by `bl` from `0xa39664` (instance draw `0xa39300`) and tail-branched from `0xa56a20` |
| Controller setup | `0xa49b28` |
| Mask enter | `0xa4ba94` (vtable word `0x178fb3c`) |
| Mask exit | `0xa4bcdc` (`0x178fb44`); restores the clip saved at +0xc0..+0xcc |
| Mask Enable, Size | `0xa4ba20`, `0xa4ba40` |
| Linkers | `0xa48460`/`0xa4844c`, called from `0xa38dd8`/`0xa38dfc` |
| Root destructor | `0xa486fc`; frees the cache, then its child chain |
| Mask destructor | `0xa56758` |
| Mask factory | `0xa4b6cc`, via the class table at `0x178ff04` |
| Texture vtable slots | 0x00 `0xa4f6a4` (not a constructor), 0x04 `0xa4f77c`, 0x38 `0xa4e628`, 0x74 `0xa4f420` |

A row's map is allocated in `FUN_01401bc0` (allocation `0xa38c14`) and freed in `setAnimationId` (`0xa38880`, `0xa382c8`) through GOT slot `0x18422b4` (DTI registered as `cGUIInstance` at `0xa3c03c`).

Draw block prefix: a row with sequences starts its draw block (root +0xa4) with `sequences * 12` bytes of animation tracks. Row setup loads the block at `0xa38cfc`, and `0xa484c4` stores each object's slice at +0x64 and the object's address at +8 of each track. Row update `0xa4915c` walks the first `row+4` map entries and, for an object with bit 23, evaluates its tracks through +0x64 at `0xb349c0` (freed under it: crash at `0xb349c0` from `0xa49238`/`0xa4923c`).

Pitfalls read from the bytes and runs:

- Vtable words are already main-relative. `0x85628`, `0x86420`, `0x866a4`, `0x8677c` are the Ghidra base subtracted by mistake.
- Flag `0x00400000` is byte +0x56 bit 6, and the walker's exit clears bit 18 (`0xfffbffff`). Byte +0x57 bit 1 is drawable bit 25. Word index +0x33 is +0xcc (`Mask`), not a kind word.
- Magenta is symmetric, so prove colour order with an asymmetric colour. The sharpness bar's yellow `0xff5efaff` shows `0xAABBGGRR`.
- A build that wrote a texture quad every frame also faulted in the game's own update: `strb r1,[r4,#0xcb00]` at `0x1014604`, r4 = 0, from `0xf28238`. The mechanism is unread.
