# MHGU Definitive Edition

Current version: **3.0.0** (tag `v3.0.0`, commit `cf91bd5`, source in `references/MHGU-Definitive-Edition/`, installed files in `/mnt/storage2/Programs/MHGU-DE/mod/`). Other versions write other words, so never carry a site or count across versions.

## What it patches

An IPS for main (`FB08F1D20FD1204FE7070672777F869B.ips`, 286 four-byte records, file offset - 0x100 = main offset) plus its own `subsdk1`, loaded at main+`0x2715000`. Most records are `add pc, pc, #imm` jumps onto a `b` veneer in subsdk1. Offsets below are read from the 3.0.0 IPS, except the handlers, which come from WishFinder's reading of its subsdk1.

| Site | Word | What it does | Effect on our mods |
| --- | --- | --- | --- |
| `0x3b7de8` quest list job loop | `e28ff790` | Renames its placeholder quest-group entries | Village Quests in Hub r6 accepts it |
| `0x3b2194` in quest script query `0x3b2174` | `e28ff790` | Answers 1 for its own quests | Village Quests in Hub r6 accepts it |
| `0x3bb318` star board fill | `e28ff790` | Puts its Harvest Tours first (`tour_board`) | **Entry of a Village Quests in Hub r6 hook. r6 refuses it and stays off** |
| `0xb80fd0` atlas lookup | `e28ff771` | To +0xabfd8, stub +0x3614, handler +0xd47c; claims only ids with top 24 bits `0x4d4800` | WishFinder accepts it and still gets the game's record for ids 9 and 21 |
| `0x19443c` item obtained bit | `e28ff798` | To +0x7f444, stub +0x4344, handler +0x8ad0; replaces the function | WishFinder accepts it |
| `0x6fcebc` smithy picker | `e3005bf5` | Raises the last item id from 2989 to 3061 | WishFinder accepts it |
| `0x3a3874` capture and break record | `e28ff790` | Handler +0x9458 serves its monsters from `mhgu_de/*.bin` | Read by WishFinder's table builders |
| `0x152960` file lookup by ID | `e28ff79a` | Handler +0x71d8 through the stub at +0x148; returns 0 below ID `0x10700` and serves only its packages' `FILE` chunks | |
| `0xac0ec` dropped-material carve pick | `e28ff79c` | | |
| `0x15339c` resource path formatter | `e28ff799` | First word replaced, so that entry cannot take a Forge hook | Skin Loader hooks the `sprintf` site `0x153b60` instead |

It leaves the start code `0x3ad988`, the pop file choice `0x31a404` and `0x3a8ccc` alone. A new signature window needs this check: parse the IPS and look for a record inside it.

## What it adds

- 48 quests (45 for its 13 monsters, 3 Harvest Tours), listed in its `allocations.toml`. Its quests name a game boss that it swaps for its own monster at spawn (Kushala 0x18 for Gogmazios 0x59, Zinogre 0x39 for Stygian Zinogre 0x139, Gendrome 0xf for Dalamadur's tail ...). Use the list: no rule over the quest files alone gets them all right.
- Three maps: Fortress (26) loads `m28`, Sanctuary (18) `m29`, Ruined Pinnacle (24) `m30`, whose files keep the game stage's internal names.
- rItemData grows from 2991 to 3063 records (`allocations.toml` appends).
- WishFinder's table from the loaded smithy tables holds 17083 rows beside it, against 16698 in 1.4.0 (Eden log).
- Captures and breaks are in `mhgu_de/*.bin` (`MH4P`). It ships no `result.arc`.

Read tables from the loaded game or the layered RomFS, never from base-game counts. How WishFinder reads all this: [its tables](../../../../mods/wishfinder/docs/worked/wishfinder-tables.md), [its checked windows](../../../../mods/wishfinder/docs/worked/wishfinder-other-mods.md).
