# Sharpness: player data, tier tables and the HUD row

Verified on MHGU Switch 1.4.0 through Modern Sharpness Gauge. "Run" means an Eden log; everything else is from original bytes, decompiles or the dump's files.

## Player fields

The local player is session cell `0x188ca48` +0x30 (hunter index 0..3), then the `sPlayer` cell `0x1885b58` +0x1c + 4*index.

| Field | Meaning |
| --- | --- |
| `uPlayerQuest` +10100 | `mSharpness`: signed points, not a percentage |
| `uPlayerQuest` +10104 | `mMaxSharpness`: signed points, follows `150 + 25 * amount` in the weapon's level row |
| `uPlayerBase` +5104 | `mSharpnessType`: tier index, 0 red, 1 orange, 2 yellow, 3 green, 4 blue, 5 white, 6 purple (mapping from the tester) |

`uPlayerQuest::adjustSharpness` (main+`0x2ad288`) is the only writer found of `mSharpness`. It applies the amount as a `short` and clamps to 0 and to the maximum, then recomputes the tier through `calculateSharpnessType` (main+`0x29cdfc`) and fires events on a change. Skills change the cost: HeavyPolish zeroes it; RazorSharp, StonefistSoul(X), SteadyHand and NightcloakSoul(X) halve it, with a coin flip on 1 point; BluntEdge doubles it. So the cost per hit is not fixed (runs read 2 to 42 points between samples).

A tier is a per-weapon band of points, not a percentage. In runs, 250 points crossed at 189 and 200 points crossed at 190. Take fill length from `current/max` and colour from the game; a ratio can never pick the tier.

A hunter changes weapon at the box, never mid-quest (tester). A weapon with no sharpness, such as a bowgun, has no gauge row at all, and the HUD is also absent in the hub and during loading screens.

## RomFS tables

`table/kireajiData.kad`: 8-byte header, 164 entries of seven u16 cumulative thresholds. The tier index is how many thresholds are strictly below the sharpness value; all 12 measured transitions fit that rule and no type fits the non-strict one.

`table/weapon07LevelData.w07d` (Long Sword, 876 entries, stride 15) and `table/weapon11LevelData.w11d` (Dual Blades, 845 entries, stride 17) have an 8-byte header. Each row starts: int32 level ID, u8 base ID, u8 level, u8 kireaji type, u8 sharpness amount, int16 raw. File sizes match `8 + entries * stride`. Other weapon tables were not read.

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

Sequences: `DEFAULT`; looping `sharp_0..6` (IDs 1000017..23, 50 frames), which key `VertexColor` on the bar and glow and hide the edge; static `sharp_0a..6a` (IDs 1000052..58, 0 frames), which fix the colour, hide the glow and show the edge. The looping set is the normal quest display. What selects between them is untraced. The HUD driver `0x61912c` (widget type 8) reads the tier through player vtable +0x1a0.

## Measured geometry

Not derived from the atlas. The accepted cut runs 128 to 200 px on the 110..238 rect, the tester's measurement, carried as offsets 18 and 90 of the rect's 128. The ink measured 124..200 px on screen, with a few px of noise from downscaled screenshots.

Sources: `mods/modern-sharpness-gauge/{DEVELOPMENT.md,core/src/lib.rs,src/insert.rs}`; `work/modern-sharpness-gauge/{PHASE0_RESEARCH.md,PHASE2_RESEARCH.md,PHASE5_RESEARCH.md,hud0-sharpness.json}`.
