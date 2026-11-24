# File formats and the resource manager

## File layouts

Verified on the 1.4.0 RomFS with real files.

| Format | Layout |
| --- | --- |
| ARC version 17 | 12-byte header: `ARC\0`, u16 version 17, u16 count. Then `count` 80-byte entries: 64-byte name, u32 type hash, u32 packed size, u32 flags, u32 offset. Each entry is one zlib stream; unpacked size is `flags & 0x1fffffff` (all 14,154 entries checked) |
| GMD text | `GMD\0`; string count at +0x18, strings' byte size at +0x20; the strings are NUL-separated at the end of the file, UTF-8 |
| `rTexture` (TEX) | `TEX\0`, 24-byte header. Byte 13 is the format: `0x07` RGBA8, `0x13` BC1, `0x17` BC3. The word at +8 holds mip count (bits 0..5), width (6..18) and height (19..31). Level 0 follows |
| Texture layout | Tegra block-linear: GOBs of 64 bytes by 8 rows, 16 GOBs to a block, over texels (RGBA8) or 4x4 blocks (BC) |

Language folders and the game's language byte: `+0xa5` of the session (sGameControl), the object in cell `0x188ca48`. `cQuestData::getMessage` `0x37a2e4` reaches it through GOT word `0x1838bb4`, three loads; its jump table at `0x37a310` picks the text slot (`+236` English, `+240` French, `+252` Spanish, `+244` German, `+248` Italian, `+256` and `+260` the two Chinese). The game's own language setting decides it, not the console's.

| Byte | Folder code |
| --- | --- |
| 2 | `fre` |
| 3 | `spa` |
| 4 | `ger` |
| 5 | `ita` |
| 7 | `chT` |
| 8 | `chS` |
| anything else | `eng` |

The MHGU-Korean patch replaces the English files, so the byte still says English. Tell it apart by the strings of `eng\table\CommonMsg_eng` in `eng/arc/resident_eng.arc`: MHGU-Korean 1.0.5 has 142 strings of 198 with a Hangul syllable (U+AC00..U+D7A3), the base game none. Scan only the strings (the last `+0x20` bytes): the table's binary part reads as U+AFBE at byte 3796 in the base 1.4.0 table, so a whole-table byte scan calls every English game Korean.

Atlas facts are in [Text, fonts, and textures](resource-editing.md#text-fonts-and-textures). The game's own font is `font_festa.gfd`.

## How the resource manager loads and shares files

- Both loaders, `loadBlocking` `0xbcb0d0` and `loaderHandler` `0xbc74e0`, build `root\mPath.ext` in a 512- or 768-byte stack buffer. The root is the MtString at `sResource +0x4024` (`\nativeNX` for skin archives), or `+0x4028`. They then call `sResource +0x13040` as `filter(path, *(sResource +0x13044))` before `MtFile` opens it. The game only ever clears that field (`0xbc6e08`), so setting it redirects a load; `MtFile::canonicalizePath` `0x8292ec` keeps a `savedata:` prefix, so a file can load from the save. Run.
- `sResource` (cell `0x2126a64`) shares a loaded file by `{crc(path), type}`: the first load of a path wins and later requests get it. Two files with the same internal path cannot both be loaded, so a copy that must sit beside the original (a skin beside the armor it came from) needs its own internal names.
