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

## Known screens and trees

Every GUI tree a mod here has mapped. Sizes are each row's own; never copy one row's to another (the Forge skill's native GUI extensions reference sizes any row from its live numbers).

| Screen / row | Resource and animation | Tree | Reached through | Detail |
| --- | --- | --- | --- | --- |
| Quest counter, quest row | `counter.gui` (`eng\GUI\05_meeting_p\count\counter`) animation 20 | 12 objects, 15 sequences, 9 drawables, no cache prefix. Null index 1/ID 14, icon texture 2/ID 12, request texture 3/ID 20, title `cGUIObjMessage` 4/ID 6. Atlas 21 is `HD_cmn_icon_GSM_NOMIP` | Row builder `0x616cb0` (7 args), from parent `0x54d030`, which rebuilds every row each frame the list shows (reached from the counter's update, vtable `0x177d808` slot 0x24 `0x6e243c`). Row instances 16..23 | `mods/key-quest-markers/DEVELOPMENT.md` |
| Quest counter, rank and star rows | `counter.gui` animation 1 (`Anm_list_v00..07`) | 18 objects, 9 sequences, 14 drawables; Null ID 14 at the quest row's place, texture ID 7 (index 5) under it | Counter list draw `0x782af8` runs the rank, star or quest row builder for the page; instances 8..14 and 24 | [Quests and progression](quests-and-progression.md#counter-pages-and-their-rows), `work/wishfinder/COUNTER_PAGES.md` |
| Smithy list rows | `shop_menu.gui` animation 25 | Root plus `Tex_icon` (index 1, ID 2, 34x34 at -7,-2), `Mes_name`, `Mes_num`, `Mes_runk`, all directly under the root; 4 sequences, 4 drawables, no prefix. Atlas `HD_lobby00` is ID 9 | Smithy UI object slot 2 (`*(this+0x34)+8`), `cUIOFacilityShopMenu`, update `0x58b908` draws row i on instance `0x16254dc[i]` (7+i) | `mods/wishfinder/DEVELOPMENT.md` Smithy |
| Quest detail panel (counter and quest board) | `counter_down.gui` (`eng\GUI\05_meeting_p\count\counter_down`, `common_eng.arc`) | Instances: page groups 0 `Null_page01`, 1 `Null_page02`, 36 `Null_page03`; page 2 rows `Null_Lv` 21 (`Mes_Lv` 22 label, `Mes_star` 23), `Null_monsName` 24 (`Anm_line_l01` 26, `Mes_name01` 25 label, `Mes_name02` 27 value), `Null_condition` 28 (`Anm_line_l02` 29, 30, 31), `Null_fail` 32 (`Anm_line_l03` 33, 34, 35); rule lines are their own instances (animation 56) over the plain `Anm_bg` 56, the level row's `Anm_line_l00` 6. Labels colour (27, 42, 52), values (78, 50, 11), 22-point | `cUIOQuestCounterDetail` setters by instance: text `0x56fc28(obj, inst, char*)`, visibility `0x56e528(obj, inst, on)` | [Quests and progression](quests-and-progression.md#quest-detail-pages-counter-quest-board-quest-info); `mods/wishfinder/DEVELOPMENT.md` Quest pages |
| Quest Info | `menu_questconfirm.gui` (`eng\GUI\02_common\menu\`, `resident_eng.arc`) | Page groups 6, 8, 11 (`Null_page01..03`, instances 7, 9, 10 `Anm_page01..03`, animations 29, 31, 32), 12/13 status (`Anm_page04`, 34), 24/25 (`Anm_page06`, 37). A page's "part" is the object index in its animation: `Anm_page03` 1 `TexSet_bg`, 3 "Client", 4 "Summary" (labels, colour 0, 128, 255), 6 client name, 7 summary (230, 230, 230); `Anm_page02` 1 `TexSet_bg` (three bands), 2 `TexSet_bg2` (one band at the top, where page 3's Client band is) | `cUIOQuestInfo` setters by instance and part: text `0x56e808(obj, inst, part, char*)`, visibility `0x56e530(obj, inst, part, on)`; groups `0x56e528` | As above |
| Quest HUD sharpness row | `hud0.gui` animation ID 4 (`sharp`), table row 7 | Resource: 4 objects, 15 sequences, 3 drawables. Runtime halfwords at row+8 read 3 and 16, and the draw block has an animation prefix. Bar, glow and edge are siblings under the controller | Draw walker `0xa494a0`; capture the instance whose +0xdc is the controller | [Sharpness](sharpness.md) |
| Start menu | `uUIStartMenu` (lobby `uUILobbyStartMenu` vtable `0x177e424`, quest `uUIQuestStartMenu` `0x177aeb8`) | Top index +0x4c (5 Hunter's Notes), submenu row +0x50, page step +0x58, rows +0xb0 (8-byte {u8 enabled, u32 text}, count +0xb4 = 7), help lines +0xc8 (12 bytes, count +0xcc) | Slots 0x9c fill, 0xb0 "has a submenu", 0x8c help, 0x78 close, 0x68 run page | `mods/wishfinder/DEVELOPMENT.md` Hunter's Notes |
| Item Pouch screen | `cUIOItemPouch`, start menu slot 4 (vtable `0x1770b50`), controller at menu +0x220; rows are `menu_itemPouch.gui` `Anm_mesM00..07`, ids 17..24, instance table `0x1770bb0` (exactly eight; more needs new instances) | Eight rows at +0x62 + row*6 {u16 item, s16 count, u8 usable, u8}; title `char*` +0xb8; description window +0x9c (shared with other screens); side menu +0xa4 | Open `0x1869ec`, close `0x188bec`; draw slot 0x4c `0x5bb5ac` | As above |
| Reward (result) screen | Result lists, group records stride 0x28 | Root ID at `list+group*0x28+0x160`, node-ID arrays at +0x16c; frame colours are sequence data (`0xf4242` plus a variant) | Holder lookup `0x546f84`; refresh `0x623c68` only assigns icons and visibility | `mods/please-do-better/DEVELOPMENT.md` Native slot and frame bindings |
| Centre popup | `cUIOInfoWindow`, UI object 1 | Lines grouped up to six | `0x65ddc4(0, 99, text, 0)`; group `0x65dce4`/`0x65dd24` | `mods/wishfinder/DEVELOPMENT.md` Arrival popups |
| Button guide | UI object 5 | Ten per-button slots +0x248 (UI instances, not text), four extras +0x228 {s32 icon, char* label} | Presets `0x65e794(preset, flags)`, extra `0x65e8cc(icon, label)` | WishFinder Button guide; icons in [Input and actions](input-and-actions.md#button-names-and-icons) |

Counter list rows (`counter.gui`, checked on the English HD fixture with `mods/key-quest-markers/scripts/gui_layout.py`). Rank and star pages switch the list (`cUIOQuestList`, holder +0x24) to GUI identity 4 (`0x546f28`/`0x56e61c`). Rank rows use instances 8..12 (`0x616164`'s table); star rows 8..14 and 24 (`0x1635118`, `Anm_list_v00..v07`), stamps 36..43 (`0x1635138`); quest rows are `Anm_list_S00..S07`, instances 16..23, animation 20. Rank and star rows play animation 1: index 0 root ID 1; index 1 Null ID 14 at X -548 (as the quest row's), whose direct children are messages ID 11 (64,10), 6 (36,11), 13 (40,9), textures ID 7 (index 5, at 0,0) and 16 (index 7), and Nulls 19 (316,22) and 21 (375,22). Star row instances are not consecutive.

UI objects 1 and 5 belong to the UI manager in cell `0x1899458`, reached as `0x65cb3c(0x55d2b4(*cell, 0), n)` (wrappers load the cell through GOT word `0x1838bd8`). `0x65cb3c(ui, n)` also gets a screen's own UI object n (the counter's quest list is `0x65cb3c(counter, 2)`, holder +0x24).

Part helpers used on list screens: text `0x56e808(screen, instance, part, char*)`, visibility `0x56e530(screen, instance, part, on)`, item icon `0x56e62c`, equipment icon `0x56ea38(screen, instance, 1, record, 0, 1)`, rarity `0x56e704`, colour `0x56e6fc(screen, instance, part, palette index)`, node position `0x545a04(screen+0x24, node)`. A list screen's fill often sets a name only when the row's item changed, so a mod's text goes through the setter on every refill.

## Classes and identities

| Object | Verified identity / role |
| --- | --- |
| `cGUIObjRoot` | 176 bytes, row root ID 1 |
| Main Null | Lookup index 1, ID 14 |
| `cGUIObjTexture` | 304 bytes, existing icon index 2/ID 12 |
| Request texture | Index 3/ID 20, existing request-bubble visibility |
| `cGUIObjMessage` | 352 bytes, title index 4/ID 6, CRC `0x2fb82eae` |
| `cGUIObjText` | 384 bytes, a different class from the title |

`cGUIObjMessage` operations (title of the counter row; source: `mods/key-quest-markers/DEVELOPMENT.md`):

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

Code map for HUD rows (World Sharpness Gauge `DEVELOPMENT.md`): walker `0xa494a0` is called by `bl` from `0xa39664` (instance draw `0xa39300`) and tail-branched from `0xa56a20`; controller setup `0xa49b28`; mask enter `0xa4ba94` (vtable word `0x178fb3c`) and exit `0xa4bcdc` (`0x178fb44`, restores the clip saved at +0xc0..+0xcc); mask Enable `0xa4ba20` and Size `0xa4ba40`; linkers `0xa48460`/`0xa4844c` (called from `0xa38dd8`/`0xa38dfc`); destructors: root `0xa486fc` (frees the cache, then its child chain), mask `0xa56758`; mask factory `0xa4b6cc` via the class table at `0x178ff04`; texture vtable slots 0x00 `0xa4f6a4` (not a constructor), 0x04 `0xa4f77c`, 0x38 `0xa4e628`, 0x74 `0xa4f420`. A row's map is allocated in `FUN_01401bc0` (allocation `0xa38c14`) and freed in `setAnimationId` (`0xa38880`, `0xa382c8`) through GOT slot `0x18422b4` (DTI registered as `cGUIInstance` at `0xa3c03c`).

Draw block prefix: a row with sequences starts its draw block (root +0xa4) with `sequences * 12` bytes of animation tracks. Row setup loads the block at `0xa38cfc`, and `0xa484c4` stores each object's slice at +0x64 and the object's address at +8 of each track. Row update `0xa4915c` walks the first `row+4` map entries and, for an object with bit 23, evaluates its tracks through +0x64 at `0xb349c0` (freed under it: crash at `0xb349c0` from `0xa49238`/`0xa4923c`).

Pitfalls read from the bytes and runs: vtable words are already main-relative (`0x85628`, `0x86420`, `0x866a4`, `0x8677c` are the Ghidra base subtracted by mistake); flag `0x00400000` is byte +0x56 bit 6, the walker's exit clears bit 18 (`0xfffbffff`), byte +0x57 bit 1 is drawable bit 25, and word index +0x33 is +0xcc (`Mask`), not a kind word; magenta is symmetric, so prove colour order with an asymmetric colour (the sharpness bar's yellow `0xff5efaff` shows `0xAABBGGRR`); a build that wrote a texture quad every frame also faulted in the game's own update (`strb r1,[r4,#0xcb00]` at `0x1014604`, r4 = 0, from `0xf28238`), mechanism unread.

Threads (static reading of 1.4.0 main, `work/world-sharpness-gauge/THREAD_RESEARCH.md`; no run has logged a thread). Chain from Forge's update to the draw walker, each link read from bytes or a decompile:

1. `tools/forge-local/source/forge/plugin.cpp` `forge_plugin_onUpdateHook` wraps main+0x3da8fc: it calls the
   original, then each plugin's `forge_onUpdate`, on the same call stack.
2. `sFestaMain::move` (main+0x3da8fc) calls field +0x38250's slot 0x1c inline. That field is allocated at
   0x44bb18 bytes in `sFestaMain::DTI::newInstance`, the size of `sFestaRender`. Its slot 0x1c main+0x3deb8c
   branches to main+0xbc2904.
3. main+0xbc2904 calls slot 0x34 of the global at 0x2126f48 inline at main+0xbc2a94 and main+0xbc2c2c,
   passing its draw context. The same global is read at main+0x3ea0e0 by sFestaUnit's slot 0x34, main+0x3ea0b0.
4. main+0x3ea0b0 loops the unit groups and calls each unit's slot 0x30 directly, no job.
5. uGUI's slot 0x30 main+0x919760 calls its slot 0x58 or 0x5c at main+0x919854. Those end in branches to
   main+0xa34070 (main+0x919ce0, main+0x91a050).
6. main+0xa34070 calls instance slot 0x3c at main+0xa341c8. cGUIInstAnimation's slot 0x3c is main+0xa39300,
   whose `bl` at main+0xa39664 is the walker main+0xa494a0.
7. The walker's only other direct branch, main+0xa56a20, is a vtable slot (word at main+0x178fc18) that forwards a
   node's +0xcc controller to the walker: a nested walk, reached from inside a walk.

So the walker, `check_liveness` and the mask's enter run inside `sFestaMain::move`, and `insert::run` runs after it
returns, on the same thread.

Other threads:

- sRender's own thread: created in main+0xbbca50, entry main+0xbbd7fc, frame body main+0xbbe9c8, handoff events at
  +0x1c4 and +0x1e0. Its body issues graphics calls. None of the sUnit slot 0x34 sites is in it.
- Worker queue: main+0xba67b4 enqueues, workers are made in main+0xba45c0. `sFestaMain::move` queues one job per
  frame at main+0x3dadd4, entry main+0x3daf88: fields +0x382ec, +0x38364, +0x38314, +0x38318. By allocation size
  those are sPop 232, sOtodokeService 88, sShell 30108 and sUIObject 56 (inference from size). Nothing was seen
  that waits for this job, so it can overlap `forge_onUpdate`.
- sUIObject's slot 0x1c main+0x65c108 prunes its list and calls entries' slot 0x04, so it destroys objects on that
  job. The class list is `cUIO*`; uGUI's parents are uFestaGUI, uGUI, uCoord.
- main+0xba62a8 runs batches and waits for them: synchronous, so it does not extend past its caller.

Not closed:

- 13 more functions call sUnit's slot 0x34 (main+0x8aa280 .. main+0x9ad854), and 10 other slot 0x3c call sites sit
  in main+0xa3d6d0 .. main+0xa54650. Their callers were not traced to a thread entry.
- Whether a gauge row's owner is a `cUIO*` object on the sUIObject job. The area-change teardown path is still
  unproven (see the understanding skill's Rules), so a destructor overlapping `insert::run` is not excluded.
- Confirmation needs a test build that records the current thread in the walker and compares it in `forge_onUpdate`.

Draw walker `0xa494a0`: with root +0x8c bit 0 set, it rebuilds an 8-byte record list, `(0,node)` on entry when drawable, `(1,node)` on exit, `(2,…)` to end. It descends +0x68, follows +0x6c, pops to +0x70 on a zero sibling, and stops when the next node is the root. It then consumes the list in order: kind 0 calls slots 0x38 and 0x3c, kind 1 calls slot 0x40. Slot 0x38 on a texture is `0xa4e628`, on a scissor mask `0xa4ba94`.

Object +0x74 does not point to the animation instance. Native factory `0xa38bc0` establishes owner/resource links. Holder lookup uses the primary table at +0xf8/count +0x298 and the alternate table +0x294 for higher indices. Counter row instances 16..23 have their own maps/root objects.

Native count getter `0xa38ffc` counts the tree. Cleanup `0x5456e4` indexes the map to that count. A child addition changes both, even if sequence descriptors stay unchanged. Root setup `0xa49b28` allocates `(objects << 4 | 8) + sequences * 12` from the halfwords at row+8: with no sequences that is `drawableCount*16+8`, nine drawables 152 bytes, ten 168; the sharpness row's 3 and 16 give 248.

The optional Forge skill's GUI-extension reference owns the allocation/publication procedure. Its verified lesson is to preserve original bindings while expanding tree/map/cache together, with allocation matched to the native destructor. Native texture DTI has three slots; there is no placement constructor at +0x0c.

## Coordinates, colours, and drawing

Loaded texture 22 is the white lobby emblem at logical rectangle `(136,344,198,406)` in the counter row's atlas; logical resource coordinates can differ from HD image pixels. The badge geometry Key Quest Markers draws there is in its DEVELOPMENT.md.

Size/AutoScale updates also need title +0xf0 bit 16 to rebuild glyph caches. Parent/root transform and sorting dirty state must be updated after structural changes. Some float setters use hard-VFP s-register arguments.

The resource theme audit traces Gathering Green `#006305` and objective Red `#A30000` to native properties. The objective instance overrides its shared Message template. Slaying category Red `#CC0000` is a separate colour.

Message text (`cGUIObjMessage`, set through `0x547564`, as `0x56fc28`, `0x56e808` and `0x56ea08` do): a `\r\n` breaks the line, as quest GMD text does (`questData_*`); a text runs past its layout `Size` instead of clipping (`counter_down` `Mes_name01`, sized for one line, drew eleven lines; WishFinder r126 to r131 on Eden and MHGU Recomp); `<COL RRGGBBAA>...</COL>` in a plain string colours it (`<COL 4E320BFF>` gave the panel's value brown in a label, r126; DialogMsg 99 uses the same tag). A `TexSet` object (type `0x4f7228fc`) draws several boxes from one texture as one object, so one of its bands cannot be hidden alone: its record's word at +32 is an offset into the float section named by header word 280, where the boxes are (x0, y0, x1, y1) after an 8-byte lead (`menu_questconfirm`: page 3's two bands (0, 0, 426, 34) and (0, 80, 426, 114), page 2's `TexSet_bg2` (0, 0, 426, 34) alone; the format is read off these records, inference for others).

Reward screen frames: layout setup `0x623a6c` starts sequence `0xf4242` plus a variant on the group's background root (`0x56e538` -> `0x546c74` -> root `0xa3896c`, which restarts only on a different ID); that colours Base rows red and Wound/Cap rows blue. A Base frame's corners hold `0xa02337dc` (R 0xdc, G 0x37, B 0x23, alpha 0xa0) over a light texture, so a white vertex colour shows the texture itself. The cursor's yellow cell comes from a path not yet read. Shaders: `root.arc` holds one shader resource of 58,841,740 bytes unpacked (ARC sizes are the low 29 bits of the flags, `flags & 0x1fffffff`); loader `0xce1fbc` checks SPK magic, version 0x26 and shader version `0xb2d34c60`. The exact GUI vertex program and constant-buffer bindings are unresolved.

Reward world-quad helper `0xa4b390` combines anchors +0xa0, size +0xb4, matrix +0x10, direction bit 0x40 at +0x56, and hard-VFP scale s0. A scissor mask's enter calls the same builder with its own node and its +0xa8/+0xac size, so its box starts at its own +0x40/+0x44 translation. Scissor `0xa37c1c` applies draw offsets/scales and viewport intersections, writes the render target's scissor at target +0xe4..+0xf0 and stores the request at context +0xd0..+0xdc (one Eden run read the box at x1.5 there); sentinel fallback is at `0xbc12d8..0xbc1364`. A computed world quad does not establish framebuffer coordinates. The exact shader/constant-buffer route remained unresolved in that experiment.

For screen-space work: texture draw `0xa4fc9c` reaches `0xa4fe50` after it builds a quad's vertices. GUI publishers `0xa4eb9c` and `0xa3e3b0` supply model matrices and `0xa397d4` the globals (CBGUIMatrix 0x2d7, CBGUIGlobal 0x2d6 at renderer +0x18bc/+0x18b4). The sentinel rectangle is read through relocated GOT main+`0x183f2b0` (offline main+`0x191eaa0`). The game's NVN present wrapper ends at `0x86a330` (`mov r0,r12; bx r3`); `0x86a28c` records the acquired resource at owner +0x48cc, whose NVN texture is resource +0x3c. Downsample gateways `0xbbfb08`/`0xbbfb44` (GOT main+`0x18418f8`) never ran for reward geometry. A Forge hook inside `0xa4fc9c` leaves that per-draw function interpreted for the session on MHGURecomp, so recolour a reward frame natively instead: its per-vertex setter `0xa4e0b8` stores +0xa4 + 4 * vertex and marks the quad dirty, and nothing rewrites a frame's colour until the next reward screen (Please do Better). Host renderers read that uploaded model matrix too: gu-native rewrites each GUI quad's matrix by its own layer `m[14]` and canvas position `m[12]`/`m[13]`, and UIScale edits the block in place; what that means for a plugin is in the Forge skill's native GUI extensions, section HUD movers.

Verify constructor, setters, material dispatch, quad output, traversal, and destruction using original ARM bodies. GPU doubles prove no actual pixels/clipping. Visible acceptance of the counter row is scoped to dated Eden/Linux user reports with optional HD, not every menu/language/platform.

For a fill/clipping proposal, trace mask production, the consuming draw/material, coordinate transforms, ordering, cached commands and mask reset before unrelated draws. A Mask1 child does not establish that its parent or siblings consume the mask. Changing Size/scale alone can distort a textured shape. Verify geometry and sampling together, including effect layers and an uncut outline where required. Use empty, partial and full ratios to expose incorrect clipping, then require real pixels for visual acceptance. Reusing discrete resource frames must still satisfy a requested continuous fill.

Player-field names are also research leads. For a current/max display, verify signedness, units, maximum semantics, recovery/buff paths, local-player selection and HUD absence/recreation. Specify positive-denominator and floating-point division rules before clamping. Unsupported data should preserve or restore native visuals within valid object lifetimes.

HUD correction sources: hash-identified dump `nativeNX/eng/GUI/01_quest/hud/hud0.gui`, decoded with the counter parser; saved `work/research-tooling/dti/dti.jsonl` object-vtable Texture properties. Private fixture paths are optional verification inputs when this skill is copied elsewhere.

Sources: `mods/key-quest-markers/{DEVELOPMENT.md,EVIDENCE.json}`, `src/gui.rs`, `mods/key-quest-markers/scripts/gui_layout.py`, `tests/{resource.py,native_adapter.py}`, `research/theme-colours.json`; `mods/please-do-better/DEVELOPMENT.md` native geometry/shader findings.
