# MHGU Definitive Edition

Current version: **3.1.0** (tag `v3.1.0`, commit `bd3785d`, source in `references/MHGU-Definitive-Edition/`, installed files in `/mnt/storage2/Programs/MHGU-DE/mod/`). Eden's `MHGUDE` load folder may still hold 3.0.0; its `mhgu-de-install.json` names the release. Other versions write other words, so never carry a site or count across versions.

## What it patches

An IPS32 file for main (`FB08F1D20FD1204FE7070672777F869B.ips`, file offset - 0x100 = main offset) plus its own `subsdk1`, loaded at main+`0x2715000`. 3.0.0's IPS has 286 four-byte records and 3.1.0's has 321. Most records are `add pc, pc, #imm` jumps onto a `b` veneer in subsdk1. 3.1.0's subsdk1 is larger, so many jump immediates differ by one step at the same site. Words below are read from both IPS files, and handler offsets from both subsdk1 files.

| Site | Word (3.0.0 / 3.1.0) | What it does | Effect on our mods |
| --- | --- | --- | --- |
| `0x3b7de8` quest list job loop | `e28ff790` both | Renames its placeholder quest-group entries | Village Quests in Hub accepts it |
| `0x3b2194` in quest script query `0x3b2174` | `e28ff790` both | Answers 1 for its own quests | Village Quests in Hub accepts it |
| `0x3bb318` star board fill (`board_put`) | `e28ff790` both | `tour_board` puts its Harvest Tours and ported quests first and returns 0; the fill's own code follows | Village Quests in Hub r7 accepts it and flips around the fill's three callers; r6 refuses it |
| `0xb80fd0` atlas lookup | `e28ff771` both | To +0xabfd8; stub +0x3614 / +0x3a64, handler +0xd47c / +0xdbbc, the same code; claims only ids with top 24 bits `0x4d4800` | WishFinder accepts it and still gets the game's record for ids 9 and 21 |
| `0x19443c` item obtained bit | `e28ff798` / `e28ff799` | To +0x7f444 / +0xbf444; stub +0x4344 / +0x47dc, handler +0x8ad0 / +0x9148, the same code; replaces the function | WishFinder r147 accepts both |
| `0x6fcebc` smithy picker | `e3005bf5` both | Raises the last item id from 2989 to 3061 | WishFinder accepts it |
| `0x3a3874` capture and break record | `e28ff790` both | 3.0.0 handler +0x9458 serves its monsters from `mhgu_de/*.bin` | Read by WishFinder's table builders |
| `0x152960` file lookup by ID | `e28ff79a` both | 3.0.0 handler +0x71d8 through the stub at +0x148; returns 0 below ID `0x10700` and serves only its packages' `FILE` chunks | |
| `0xac0ec` dropped-material carve pick | `e28ff79c` both | | |
| `0x15339c` resource path formatter | `e28ff799` / `e28ff79a` | First word replaced, so that entry cannot take a Forge hook | Skin Loader hooks the `sprintf` site `0x153b60` instead |
| `0x12e7e0` | none / `e28ff79a` | `gear_rapidshot` (`module/gear_hooks.txt`) | |

It leaves the start code `0x3ad988`, the pop file choice `0x31a404` and `0x3a8ccc` alone. A new signature window needs this check: parse the IPS and look for a record inside it.

3.1.0 raises GU's quest limits with plain immediates (`module/build.py`, `QUEST_LIMIT_SITES`):

| Limit | Sites | GU | 3.1.0 |
| --- | --- | --- | --- |
| Loaded quests (array size, loader cap, release loops) | `0x3b7d58`, `0x3b7d64`, `0x3b7e70`, `0x3b7f84`, `0x3b6300`, `0x3b65f0`, `0x3b659c` | 864 | 1024 |
| Quests per star board (block size, getter stride, `board_put` strides and caps) | `0x3ba988`, `0x3ba994`, `0x3bc9c8`, `0x3bb3cc`..`0x3bb860` | 99 | 255 |

A plugin that sizes a quest list or a board reads the immediate at its site, as Village Quests in Hub's `list_capacity` and WishFinder's `board_capacity` do. None of these sites lies in a window of ours. Its `build.py` also keeps `PLUGIN_CHECKED`, the windows of Key Quest Markers r18 and Damage Numbers r36, and refuses a hook or patched byte inside them.

## What it adds

- 51 quests in 3.1.0 (48 for its 14 monsters, 3 Harvest Tours), listed in its `allocations.toml`; 3.0.0 has 48. Its quests name a game boss that it swaps for its own monster at spawn. Examples: Kushala 0x18 for Gogmazios 0x59, Zinogre 0x39 for Stygian Zinogre 0x139, Gendrome 0xf for Dalamadur's tail. In 3.1.0's 11497 to 11499, Crimson Fatalis 0x10d becomes G-rank Crimson Fatalis 0x60d. Use the list: no rule over the quest files alone gets them all right.
- Three maps: Fortress (26) loads `m28`, Sanctuary (18) `m29`, Ruined Pinnacle (24) `m30`, whose files keep the game stage's internal names.
- rItemData grows from 2991 to 3063 records (`allocations.toml` appends). G-rank Crimson Fatalis adds no item: it uses GU's Crimson Fatalis materials.
- WishFinder's table from the loaded smithy tables held 17083 rows beside 3.0.0, against 16698 in 1.4.0 (Eden log).
- Captures and breaks are in `mhgu_de/*.bin` (`MH4P`, u32 monster at 0x1c; 3.1.0's `g_crimson_fatalis.bin` is 0x60d). It ships no `result.arc`.

Read tables from the loaded game or the layered RomFS, never from base-game counts. How WishFinder reads all this: [its tables](../../../../mods/wishfinder/docs/worked/wishfinder-tables.md), [its checked windows](../../../../mods/wishfinder/docs/worked/wishfinder-other-mods.md).
