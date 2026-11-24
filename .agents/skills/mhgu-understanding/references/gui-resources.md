# GUI resources: file layout and identity

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

Record layout: animation records use table `(40,164,24)`, ID at +0, counts as three little-endian 16-bit fields at +4, first object at +12, name offset at +16 and first sequence at +20. Objects use table `(48,172,36)`, ID at +0, name offset at +16 and properties at +24/count byte +4. Instances use `(68,188,36)`, name at +20 and properties at +28/count +16. Decode the instance's `AnimationId` property and match the animation's ID explicitly. Keep serialized tree-link offsets distinct from runtime object links.

Keyframes (hud0, 2026-10-19). The object×sequence table at header +176 has 16-byte records, object-major, one record per object per sequence: flag byte +0, init-param count +2, keyed-param count +3, frame length u16 +6, init-param index +8, keyed-param index +12.

Keyed params at header +184 are 24 bytes: value type +4, key count +5, owning object ID +8, name +12, key index +16, value offset +20. The key table is at header **+264** (+244 is `messageOffset`; both read 48,000 in hud0 only because it has no messages). Each key is 8 bytes with its frame in the first u16.

A check over all 1972 dumped `.gui` files found the keyed-param word at +8 always equal to the owning object's ID, so it is not an interpolation mode.
