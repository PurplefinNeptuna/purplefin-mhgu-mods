# Sharpness: player data, tier tables and the HUD row

MHGU Switch 1.4.0. "Run" means a game log; everything else is from original bytes, decompiles or the dump's files.

## Player fields

The local player is session cell `0x188ca48` +0x30 (hunter index 0..3), then the `sPlayer` cell `0x1885b58` +0x1c + 4*index.

| Field | Meaning |
| --- | --- |
| `uPlayerQuest` +10100 | `mSharpness`: signed points, not a percentage |
| `uPlayerQuest` +10104 | `mMaxSharpness`: signed points, `min(150 + 25 * level, 450)`, set once by init main+`0x29b7d4` and never changed in a quest |
| `uPlayerBase` +5104 | `mSharpnessType`: tier index, 0 red, 1 orange, 2 yellow, 3 green, 4 blue, 5 white, 6 purple (mapping from the tester) |

`uPlayerQuest::adjustSharpness` (main+`0x2ad288`) is the only writer of `mSharpness` during a quest; the constructor zeroes it and init main+`0x29b7d4` sets it to the maximum. It applies the amount as a `short` and clamps to 0 and to the maximum, then recomputes the tier through `calculateSharpnessType` (main+`0x29cdfc`) and fires events on a change. Skills change the cost: HeavyPolish zeroes it while its timer at `+0x277c` runs; RazorSharp, StonefistSoul(X), SteadyHand and NightcloakSoul(X) halve it, with a coin flip on 1 point; BluntEdge doubles it. So the cost per hit is not fixed (runs read 2 to 42 points between samples). Sharpening has no partial steps: the points update at once when the sharpen animation ends (tester).

The level in the maximum is status stat 14, an s16 at `mpPlParam + 4 + 0x338`, written by main+`0xe1eec`: the weapon's base level, plus 2 for `Sharpness_Plus2` or `HellbladeSoul(X)`, otherwise plus 1 for `Sharpness_Plus1`, `HonedBlade` or `BoltreaverSoul(X)`, capped at 12. Init reads it through player vtable `+0x15c` with argument 14. A bonus can end the maximum partway through a tier's band, so the top band is clipped at `mMaxSharpness`.

A tier is a per-weapon band of points, not a percentage. In runs, 250 points crossed at 189 and 200 points crossed at 190. `uPlayerBase::calculateSharpnessType` (main+`0x29cdfc`, `(player, s32 points) -> tier`, 196 bytes) is the game's own points-to-tier rule, and a caller needs no weapon id, level row or table to use it: gate main+`0x27c7ec` with argument 1 answers nonzero for the sharpness states, the fixed-tier flag main+`0x27b918` (bit 3 of the byte at `player + 0x13cc`, set only on the lobby classes `uOtomoLobby` and `uPlayerPreview`, so a quest player does not carry it) picks vtable `+0x144`, and otherwise the equip record's `+0x4` field `(& 0x3ff) >> 5` goes through vtable `+0x84`, which counts the thresholds as the RomFS section below describes. All 11 melee level classes share slots 0x7c/0x80/0x84 (23 vtable words equal the rule main+`0xf4794`), and all melee base classes share slot 0xd8 `0x127070`, the equip record, whose `(cell, index) -> cell + index * 44 + 20` address helper is main+`0xdf814`. The function's two dereferences, `player + 0x13c4` (main+`0x29ce34`) and that pointer's `+ 0x4d4` (main+`0x27c848`, main+`0x27c84c`), are unchecked, and every gate and lookup failure returns 0, the red tier; the body stores nothing. Validate the player and both pointers before calling it. Points equal to a threshold answer with the tier below, which makes the top of a band a point of that band, and the tier rule is monotonic, so a band search is sound. Log samples at kireaji row 10 and maximum 150: 150 tier 2, 131 tier 2, 130 tier 1, 100 tier 1, 90 tier 0, 8 tier 0. A rule answering 0 for any points makes a band search span the whole maximum.

A hunter changes weapon at the box, never mid-quest (tester). A weapon with no sharpness, such as a bowgun, has no gauge row at all, and the HUD is also absent in the hub and during loading screens.

More code, read from the bytes:

| Address | Meaning |
| --- | --- |
| `0x26893c` | `uPlayerBase::getSharpnessType`, returns `mSharpnessType` |
| `0xf4724` | Level object slot 0x80, threshold lookup: the u16 at `row + 4 + 2*i` of the row slot 0x20 picks, through the data singleton (`0x13f290`, then `0x12db78`) |
| `0x62bb0c` | Gauge colour driver (slot 0x3c of widget vtable `0x1776300`, vtable word `0x177633c`): tier through vtable +0x1fc, clamped to 6, indexes sequence table `0x1638ecc`, or `0x1638ee8` while `player+0x2844 & 0x200` (Heavy Polish); stores the sequence at +0x50 and applies it through `0x546c74` -> `0xa3896c` |
| `0x61912c` | HUD widget driver; its case 8 reads +0x2784 through vtable +0x1a0, not the tier |
| `0x2ac990` | `ChallengeSheath`: a random gain on a condition, current points only |
| `0x27bcd0` | Another gate in the chain, unexercised |
| `0x27c7ec` detail | Case 1 loads `*(player+0x13c4)` and reads byte +0x4d4, answering 1 for the values `(v-4) & 7` that bit mask 0x47 selects (`0x27c844..0x27c86c`) |
| `0x27b918` setters | Only `0x259aec` (`uOtomoLobby`) and `0x275bd4` (`uPlayerPreview`, when param byte +0x4d4 is 15) set it; both are 10064-byte lobby classes (`movw #0x13cc` and `add #0x1300` scans of `.text`; constructor vtable words at `0x2651c0` and `0x298b7c` against the DTI). Writes through a computed pointer are not excluded |
| `0x29b7d4` detail | Player init writes `mMaxSharpness` (+0x2778 = 10104) and `mSharpness` (+0x2774 = 10100), then `calculateSharpnessType` into +0x13f0 (5104); bytes at `0x29b870..0x29b8bc` |
| `0xe1eec` | Also reached from the player update path `0x27b9c8`; rerunning it does not move `mMaxSharpness`, so take the maximum from `mMaxSharpness` only |

`adjustSharpness` fires event 0x1c (tier down), 0x1d (tier up) or 0x1e (reached the maximum) through vft+0x3ac; 14 call sites apply positive amounts (whetstones and the like). The base data is reached by `FUN_00aa8814(&mpPlParam->mStatusParam, 0)` then `FUN_00b0803c` over the singleton pair at `DAT_00c65ec0 + 0xc65e54` (Ghidra names). `/DTI_Types/WpDatEntry` (68 bytes): `Sharpness` +21, `SharpnessQuality` +22, `WeaponId` +58, `WeaponNameId` +60. `mCmdTblId` at player +9388 identifies the weapon's command table: 1000 Long Sword, 2000..2033 Dual Blades, 9999 none (bowgun).

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
