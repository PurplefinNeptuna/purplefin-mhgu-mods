# MHGU Definitive Edition

## What its mod files do

Facts here were read at 2.0.0 unless marked. **3.0.0** is the version WishFinder supports: its IPS has 286 records, it adds 48 quests, and 2.0.0 is refused there ([WishFinder and other mods](worked/wishfinder-other-mods.md)). Village Quests in Hub accepts 2.0.0's words only; its windows have not been checked against 3.0.0.

Its quests name a game boss that it swaps for its own monster at spawn (Kushala 0x18 for Gogmazios 0x59, Zinogre 0x39 for Stygian Zinogre 0x139, Gendrome 0xf for Dalamadur's tail ...). Three run on a map of its own: Fortress (26) loads `m28`, Sanctuary (18) `m29`, Ruined Pinnacle (24) `m30`, whose files keep the game stage's internal names. Its 39 quests are listed in its `allocations.toml`; a file-only test (a clear target no boss record spawns) gets 37 and picks wrong stand-ins in two, so use the list. Its captures and breaks are `mhgu_de/*.bin` (`MH4P`), served by its hook on `0x3a3874`. It ships no `result.arc`, and its rItemData has 3055 records (1.4.0: 2991). Details: [WishFinder tables](worked/wishfinder-tables.md).

Its IPS replaces the first word of `0x15339c` (the resource path formatter) with `add pc, pc, #imm`, so that entry cannot take a Forge hook; hook the `sprintf` site `0x153b60` instead.
