# Sharpness: player data, tier tables and the HUD row

Verified on MHGU Switch 1.4.0 through Modern Sharpness Gauge. "Run" means an Eden log; everything else is from original bytes, decompiles or the dump's files.

## Player fields

The local player is session cell `0x188ca48` +0x30 (hunter index 0..3), then the `sPlayer` cell `0x1885b58` +0x1c + 4*index.

| Field | Meaning |
| --- | --- |
| `uPlayerQuest` +10100 | `mSharpness`: signed points, not a percentage |
| `uPlayerQuest` +10104 | `mMaxSharpness`: signed points, `min(150 + 25 * level, 450)`, set once by init main+`0x29b7d4` and never changed in a quest |
| `uPlayerBase` +5104 | `mSharpnessType`: tier index, 0 red, 1 orange, 2 yellow, 3 green, 4 blue, 5 white, 6 purple (mapping from the tester) |

`uPlayerQuest::adjustSharpness` (main+`0x2ad288`) is the only writer of `mSharpness` during a quest; the constructor zeroes it and init main+`0x29b7d4` sets it to the maximum. It applies the amount as a `short` and clamps to 0 and to the maximum, then recomputes the tier through `calculateSharpnessType` (main+`0x29cdfc`) and fires events on a change. Skills change the cost: HeavyPolish zeroes it while its timer at `+0x277c` runs; RazorSharp, StonefistSoul(X), SteadyHand and NightcloakSoul(X) halve it, with a coin flip on 1 point; BluntEdge doubles it. So the cost per hit is not fixed (runs read 2 to 42 points between samples). Sharpening has no partial steps: the points update at once when the sharpen animation ends (tester).

The level in the maximum is status stat 14, an s16 at `mpPlParam + 4 + 0x338`, written by main+`0xe1eec`: the weapon's base level, plus 2 for `Sharpness_Plus2` or `HellbladeSoul(X)`, otherwise plus 1 for `Sharpness_Plus1`, `HonedBlade` or `BoltreaverSoul(X)`, capped at 12. Init reads it through player vtable `+0x15c` with argument 14. A bonus can end the maximum partway through a tier's band, so the top band is clipped at `mMaxSharpness`.

A tier is a per-weapon band of points, not a percentage. In runs, 250 points crossed at 189 and 200 points crossed at 190. The bar's length is the fill inside the band its points sit in: `(current - floor) * 10_000 / (ceiling - floor)`, `floor` the top of the tier below (0 in tier 0) and `ceiling` the top of this tier clipped to `mMaxSharpness`, so the bar refills at every colour and a raised maximum reads full partway through its tier. Publish that fill directly: "the need is approximation, so jumpy is okay, no need for fancy smooth animations or lerp" (tester). Colour comes from the game, and a ratio can never pick the tier.

`uPlayerBase::calculateSharpnessType` (main+`0x29cdfc`, `(player, s32 points) -> tier`, 196 bytes) is the game's own points-to-tier rule, and a caller needs no weapon id, level row or table to use it: gate main+`0x27c7ec` with argument 1 answers nonzero for the sharpness states, the fixed-tier state main+`0x27b918` (bit 3 of the byte at `player + 0x13cc`, meaning unread) picks vtable `+0x144`, and otherwise the equip record's `+0x4` field `(& 0x3ff) >> 5` goes through vtable `+0x84`, which counts the thresholds as the RomFS section below describes. All 11 melee level classes share slots 0x7c/0x80/0x84 (23 vtable words equal the rule main+`0xf4794`), and all melee base classes share slot 0xd8 `0x127070`, the equip record, whose `(cell, index) -> cell + index * 44 + 20` address helper is main+`0xdf814`. The function's two dereferences, `player + 0x13c4` (main+`0x29ce34`) and that pointer's `+ 0x4d4` (main+`0x27c848`, main+`0x27c84c`), are unchecked, and every gate and lookup failure returns 0, the red tier; the body stores nothing. Validate the player and both pointers before calling it. Points equal to a threshold answer with the tier below, which makes the top of a band a point of that band, and the tier rule is monotonic, so a band search is sound. Log samples at kireaji row 10 and maximum 150: 150 tier 2, 131 tier 2, 130 tier 1, 100 tier 1, 90 tier 0, 8 tier 0. In the fixed-tier state the rule answers 0 for any points, so a band search then spans the whole maximum.

A hunter changes weapon at the box, never mid-quest (tester). A weapon with no sharpness, such as a bowgun, has no gauge row at all, and the HUD is also absent in the hub and during loading screens.

## RomFS tables

All in the dump's `nativeNX/loc/arc/resident.arc`.

`table/kireajiData.kad`: 8-byte header, 164 entries of seven u16 cumulative thresholds. The tier index is how many thresholds are strictly below the sharpness value (main+`0xf4794`); all 12 measured transitions fit that rule and no type fits the non-strict one. Every entry is monotonic, starts at 10 or more and ends at 450, so tier 7 is unreachable. 70 bands are zero-width, 58 of them tier 6 (`..., 450, 450`), and the rule never lands in one.

`table/weaponNNLevelData` for the 11 melee weapons has an 8-byte header and these strides: 15 for 00, 01, 02, 03, 07 (Long Sword) and 13; 16 for 09 and 12; 17 for 08, 11 (Dual Blades) and 14. Each row starts: int32 level ID, u8 base ID, u8 level, u8 kireaji type, u8 sharpness amount, int16 raw. All 8766 rows have an even amount from 0 to 12 and a valid kireaji type, and file sizes match `8 + entries * stride`. Bow and bowgun tables were not read.

## The HUD row

hud0 animation ID 4 (`sharp`). The sharpness digest is identical in every language's file and in HD Project's quest archive, and HD replaces atlases without changing logical rects, so identify the row by structure and never by language or file hash.

Live identity, as held across runs with other weapons, a non-English game and HD on: controller +0x9c gives the row; row+0 = 4, row+4 packs 4 objects (low) and 15 sequences (high), row+12 = 29. row+0x14 is a pointer, not a row index. Identify the bar by its authored 88x24 at +0xb4/+0xb8.

The runtime tree is the controller with `Txt_sharp`, `Txt_sharpefx` and `Txt_sharpEdge` as siblings under it. The file's child indices describe a nesting chain that does not exist at runtime. The rect is `110 38 238 166` in the usual layout, and other layouts moved it to `220 70 348 198` and `660 198 788 326`.

| Object | Size, position | Atlas window |
| --- | --- | --- |
| `Txt_sharp` | 88x24, `HD_hud00_BM_NOMIP`, SamplerState 2 | Yellow and above `0,280,88,304`; orange `0,304,88,328`; red `0,328,88,352` |
| `Txt_sharpefx` | 88x32 at (6,-6), alpha 120 | `0,160,88,192`, a solid white block, which is why it reads as a glow |
| `Txt_sharpEdge` | 88x24, `HD_hud01_BM_NOMIP` | `160,272,248,296` by default |

The blade's length runs along `u`; `v` selects the tier band. The atlas is greyscale, and the tier colour is `VertexColor`. The bands differ in their bottom outline: 280 is straight, 304 has chips at columns 46, 58 and 70, and 328 has more chips and a raised bottom over columns 62 to 73.

Sequences: `DEFAULT`; looping `sharp_0..6` (IDs 1000017..23, 50 frames), which key `VertexColor` on the bar and glow and hide the edge; static `sharp_0a..6a` (IDs 1000052..58, 0 frames), which fix the colour, hide the glow and show the edge. The looping set is the normal quest display, and the static set shows while the Heavy Polish timer runs. The driver is main+`0x62bb0c` (vtable word `0x177633c`): each frame it takes the main player's tier through vtable `+0x1fc`, clamps it to 6, and indexes table `0x1638ecc` (looping) or, when `player+0x2844 & 0x200` is set, table `0x1638ee8` (static). That flag is `+0x277c > 0`, built at `0x29f644` and stored at `0x29f834`. The HUD widget driver `0x61912c` is not this: its case 8 reads `+0x2784` through vtable `+0x1a0`, a different field whose meaning is unread.

## Measured geometry

Not derived from the atlas. The accepted cut runs 128 to 200 px on the 110..238 rect, the tester's measurement, carried as offsets 18 and 90 of the rect's 128. The ink measured 124..200 px on screen, with a few px of noise from downscaled screenshots.

Sources: `mods/modern-sharpness-gauge/{DEVELOPMENT.md,core/src/lib.rs,src/insert.rs}`; `work/modern-sharpness-gauge/{PHASE0_RESEARCH.md,PHASE2_RESEARCH.md,PHASE5_RESEARCH.md,hud0-sharpness.json}`.
