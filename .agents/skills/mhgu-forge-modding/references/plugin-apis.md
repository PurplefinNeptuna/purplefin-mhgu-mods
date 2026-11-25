# Plugin-to-plugin APIs

A plugin can export plain C functions for another plugin (WishFinder: `wishfinder_api_version`, `wishfinder_sync`, `wishfinder_search`, `wishfinder_add`, `wishfinder_remove` and ten more).

The callers should not have to find them: WishFinder r70 and Purple-lib both hand a table of their functions to each plugin that exports a known name (`wishfinder_on_register`, `purplelib_on_register`), the way [below](#a-library-that-calls-its-clients-purple-lib).

`nn::ro::LookupSymbol` resolves only the game's own modules and finds nothing in a plugin, which is why the library reads each NRO's symbol table itself (`mods/wishfinder/core/src/nro.rs`, `mods/purple-lib/core/src/nro.rs`). WishFinder keeps its exports for callers built before the table. Rules from WishFinder and its two bridges:

- The contract is a fixed-layout record (WishFinder's 64-byte `WishFinderEntry`) and a version function the caller checks first. Check range readability and alignment on entry, copy, and hand the data to `forge_onUpdate` through a bounded mailbox; nothing locks.
- A plugin that exports only Forge's callbacks (My Weapon Tree) cannot be looked up by symbol. Walk `svcQueryMemory` for an R-X mapping starting with an NRO header (`NRO0` at +0x10) whose build ID at +0x40 matches, pin that exact build, and check the whole range is mapped readable before every read of its memory. Then read its data by fixed offsets ([the bridge's page](../../../../mods/wishfinder-mwt-bridge/docs/worked/mwt-bridge.md) has a layout table); a host test that loads the real NRO at base 0 checks the offsets and relocated tables.
- Keep the logic in a `core` crate that both the plugin and the host test build (`mods/wishfinder-mwt-bridge/core/src/lib.rs`).
- Find a partner by its exported name or build ID, never by folder prefix or position.

### A library that calls its clients (Purple-lib)

Purple-lib puts a mod's settings in the game's Options window and its topics in the game's help.

To use it from a mod, read `mods/purple-lib/API.md` and copy from the two working clients:

- **Purple-lib Tester** (`mods/purple-lib-tester`) uses every feature: each row kind, action rows with the mod's own window, the input hold, a preview beside the page, page help, help topics with `open`.
- **Please do Better** (`mods/please-do-better/src/purple_lib.rs` and `core/src/purple_lib.rs`) is a shipping mod's page: two labels rows in seven languages, a help topic per row, lock-free `get`/`set`, saving on `closed`.

`mods/purple-lib/examples/` holds the same as twin C++ and Rust plugins, with Rust bindings in `purplelib.rs`. Its book is the standard for [API books](api-books.md).

How it works, and what to keep when another library needs the same:

- The client exports one function, `purplelib_on_register(const PurpleLibApi *)`, and imports nothing, so it loads and works without the library.
  - At its first `forge_onUpdate` the library walks the process's R-X mappings (`svcQueryMemory`), reads that name from each NRO's dynamic symbol table and calls it with a table of its functions (`mods/purple-lib/src/registry.rs::call_mods`, `core/src/nro.rs`).
  - Forge runs every `forge_onLoad` and `forge_onInit` before any `forge_onUpdate` (`tools/forge-local/source/forge/plugin.cpp`), so every client is loaded and initialised by then, in any load order. Runs on Eden and MHGURecomp (Purple-lib r17 with Tester r10 and Please do Better r36).
- A Rust mod exports every `#[unsafe(no_mangle)] pub extern "C"` function. Its `build.rs` passes only `link/switch32.ld` to the linker, so `link/exported.txt` stays as it is; that file is a copy of cargo-forge's template pinned in `dependencies.lock.json`. The WishFinder bridges r9 and r18 export `wishfinder_on_register` without it, and their `verify.py` reads it in the NRO's dynamic symbols. A C++ mod lists the name in `src/exports.txt`. Either way add it to the mod's export audit (`scripts/verify.py`, or `CALLBACKS` in `scripts/please_do_better.py`).
- The library calls only an address that is a multiple of 4 inside executable memory, and every read of a foreign mapping is checked readable first.
- The table starts with a version word and only grows at its end; a record is read by its `size`. The client registers when the version is at least the one it was built for.
- A client learns the library is absent by not being called: the two first updates come in load order, so the client's second `forge_onUpdate` is the earliest it can tell.
- Why not a plain import or a Forge lookup: Forge keeps each plugin's `nn::ro::Module` private (`plugin.cpp` `getSymbol`). MHGURecomp binds a plugin's import only against modules loaded before it, and a weak one to 0 (`references/MHGURecomp/runtime/loader.c` `resolve`). So an import works only in one load order. How the Switch's `nn::ro` binds imports between plugins is unread.
- `python3 scripts/mod_distribution.py check` compares every mod's copy of Purple-lib's records, table and names with `mods/purple-lib/core/src/api.rs` (`purple_lib_clients` in `scripts/purple_lib_clients.py`), because no mod may build from a sibling. A client's `Api` table may be the start of Purple-lib's (an older API version's: the table only grows at its end); the other records match exactly.
- Purple-lib's API exports stay in its NRO for a mod that finds them itself (API version 2); no mod in this workspace does any more. Version 4 (Purple-lib r19) adds `purplelib_help_shown` at the table's end: true while a page's own help screen is open. Version 5 (Purple-lib r23) adds the row flag `ROW_LIST`.
- An older library refuses a flag bit it does not know, and Purple-lib then drops the whole page. So a client sets a new flag only when the table's version has it (source: `mods/purple-lib/core/src/api.rs` `row_acceptable`).
