# Forge APIs, ABI, and builds

## Version and architecture

The Switch loader is native ARM32. C++ and Rust plugins produce `.nro` modules loaded into the game process. They can access native memory and affect game stability. A Rust wrapper does not establish pointer validity or game ownership.

| Component | Pinned source | Role |
| --- | --- | --- |
| Forge 2.0.0 | `fd03ecb4c4ad16a02edb508c5a9b7731b84008d3` | Loader, hooks, callbacks, graphics, native facilities |
| forge-rs 2.0.0 | `112e0e032ad72db992870989384aba65331978c2` | Raw bindings, Rust wrappers/macros/runtime |
| cargo-forge converter 1.4.1 | Fingerprinted by the mod dependency lock/tool status | Separate ELF-to-NRO build tool |

Current Forge source is [Fexty's fork](https://github.com/Fexty12573/forge), based on Jeffi's original Forge. Update the existing official checkout in place when requested. Retired local loader, renderer, Better Input, mutex, and support patches are not the baseline.

## Loader contract

Forge scans `app:/nativeNX/plugins` for `.nro`, registers module hashes, loads modules, resolves callbacks, calls `forge_onLoad`, checks the requested version, and calls `forge_onInit` for accepted plugins. A plugin built with forge-rs 2.0 asks for Forge 2.0: Forge 1.5.1 removes it and logs `requires Forge version 2.0.*` (`plugin.cpp`). MHGURecomp hosts Forge 2.0.0 from 0.18.0. Keep startup independent of ImGui availability.

| Export | Native signature / purpose |
| --- | --- |
| `forge_onLoad` | `void(PluginInitParam*)`, fill metadata |
| `forge_onInit` | `void()`, initialize plugin |
| `forge_onUpdate` | `void(float dt)`, after `sFestaMain::move` (`0x3da8fc`) returns. `dt` is `sMain::mDeltaTime` (main+0x68), a frame count: 2.0 per frame at 30 fps, not seconds. Runs in plugin load order |
| `forge_onImGuiInit` | `void(void* ctx, void* alloc, void* free)` |
| `forge_onImGuiRender` | `void()`, only while Forge's own window is open with its "Plugin UI" header expanded (`source/forge/graphics.cpp`); a settings panel, never an overlay |
| `forge_onImGuiFreeRender` | `void()`, every frame, plugins in load order; overlays and anything drawn over the game or another plugin |

Use C linkage and exported unmangled names. Forge's native metadata is **70 bytes**, alignment 2: three `u16` version fields at 0/2/4 and a 64-byte name at 6. The pinned Rust `PluginInitParams` declares only the six-byte version prefix. A name needs a checked native-compatible output view and a bounded NUL-terminated label. Native `forge_onInit` takes no argument. The pinned `#[forge::entry]` macro generates an init function with an unused pointer parameter; maintained explicit callbacks use the actual zero-argument ABI. Inspect generated exports before copying a macro recipe.

Version satisfaction compares major/minor ordering and ignores patch. Requesting 1.5.1 is not a strict runtime equality guard. Verify actual ABI/signatures separately. Maintained mods write explicit 1.5.1/name metadata in `forge_onLoad` (Damage Numbers `src/lib.rs`, Please do Better `src/lib.rs`).

`PluginInitParam` is defined only in Forge's private `source/forge/plugin.cpp`, not in a public header. C++ mods therefore declare `struct ForgeVersion { uint16_t major, minor, patch; }; struct PluginInitParam { ForgeVersion required_ver; char name[64]; };` locally with `static_assert(sizeof(PluginInitParam) == 70 && offsetof(PluginInitParam, name) == 6)`. This is the only accepted local re-declaration; include `<forge/log.h>`, `<forge/hook.h>`, `<forge/mem.h>`, `<forge/singleton.h>`, `<forge/fs.h>` and others for everything else. `<forge/mem.h>` lacks a C++ linkage guard, so include it inside `extern "C" { }`.

## Compiler-derived layouts

Use the ARM32 target compiler, not host `sizeof`. All pointer fields below are four bytes.

| Type | Size / alignment | Fields |
| --- | --- | --- |
| Native `Hook` | 24 / 4 | target 0, detour 4, original 8, context 12, ctx_cell 16, has_ctx 20 |
| Pinned libnx `Jit` | 28 / 4 | type 0, size 4, src 8, rx 12, rw 16, executable 20, handle/reservation union 24 |

Compare native and Rust layout records in the final artifact, including offsets and alignment. Equal integer widths do not guarantee C++ mangled-symbol compatibility: the historical mutex correction involved `s32` versus a different same-width declaration. Keep current upstream declarations instead of reviving that patch.

## Use existing facilities

Forge supplies lifecycle, logging, hooks/context hooks, main-section bases, input, singleton lookup, filesystem mounts, patching, and graphics. Its C++ MT bindings already support `MtDti::find(name)`. DTI finds class metadata; singleton lookup finds an existing instance. An allocator/constructor is still needed to create an object.

forge-rs layers `mhgu-forge-sys` FFI, `mhgu-forge` wrappers, procedural macros, startup glue in `mhgu-forge-rt`, and Cargo tooling. Cargo dependencies may alias the public crate as `forge`. Wrappers include MT types, patches, patterns, TLS/locks, INI serialization, and ImGui draw helpers. Attribute macros generate exports or typed detours. Distinguish those conveniences from the underlying loader APIs.

Headers can declare functions unavailable to an NRO. `forge_mem_queryMemory` has a header/source definition but lacks the needed export in the inspected release. Check strong imports against the actual Forge, main, and SDK binaries. Existing mods use narrow checked SVC/native adapters for verified missing memory-query, program-ID, cache, SDK file, or GUI operations. Reuse that pattern only when the same gap and ABI are verified.

## Rust NRO relocation requirements

For every future Switch Rust/GCC NRO build, retain these settings in the mod-owned custom target JSON. Merge the arguments with any existing `gcc` pre-link arguments:

```json
{
    "relocation-model": "pic",
    "pre-link-args": {
        "gcc": ["-nostartfiles", "-Wl,-z,text"]
    }
}
```

Forge's Rust runtime supplies its own startup metadata and `init`/`fini`. `-nostartfiles` excludes GCC startup objects, which introduced six relocations into executable text in each accepted Key Quest Markers r17 and Damage Numbers r27 NRO. PIC in Rust code alone did not prevent this. `-Wl,-z,text` makes remaining read-only dynamic relocations a link error; it does not repair them. Preserve the linker output and resolve the contributing object/section before delivering a build.

After `cargo forge new NAME`, add these settings to the generated mod target before the first build. The pinned upstream and vendored cargo-forge templates predate this rule; they remain provenance snapshots. Maintained builds use their mod-local `./build.sh build`, which invokes `cargo forge build --release` with pinned tools and separate output paths.

Validate the final ELF and converted NRO: reject `DT_TEXTREL` and `DF_TEXTREL`, and check that every dynamic relocation write targets writable data/BSS. A relocation table stored in read-only memory is normal; the destination of each write determines safety. Keep the NRO checks in the mod's verifier and record exact hashes. C/C++ NRO builds need the same writable-destination invariant; `-nostdlib` already excludes default startup objects when that is their existing recipe.

Excluding GCC's startup objects removes all six executable-text relocations from an NRO with no other change; that is a build result, not physical Switch acceptance. Evidence: `mods/key-quest-markers/research/hardware-link.json` and `mods/damage-numbers/research/hardware-link.json`.

## Lawrence's hardware-test loader

[Lawrence-al/forge](https://github.com/Lawrence-al/forge) at [`bbc540f4b831881f4980a4939a049cc14c31b9e4`](https://github.com/Lawrence-al/forge/commit/bbc540f4b831881f4980a4939a049cc14c31b9e4) is one commit ahead of the pinned Forge 1.5.1 base. The reviewed diff retains the public Hook header and adds hardware startup/loading fixes. Its [hardware document](https://github.com/Lawrence-al/forge/blob/bbc540f4b831881f4980a4939a049cc14c31b9e4/docs/hardware-compatibility.md) specifies the same Rust flags and says loader fixes do not rewrite plugin relocations.

Plugins built against the pinned 1.5.1 SDK are expected to work with that reviewed fork when their imports and ABI match. Confirm the tester's exact loader revision/binary, strong imports and runtime results before claiming compatibility. The fork is an optional hardware-test loader; it does not replace the workspace's stock SDK/source baseline or become a required dependency merely because a test uses it. The reviewed source and the r18/r28 candidates were not tested together on physical hardware here.

## Plugin-to-plugin APIs

A plugin can export plain C functions for another plugin (WishFinder: `wishfinder_api_version`, `wishfinder_sync`, `wishfinder_search`, `wishfinder_add`, `wishfinder_remove` and ten more). The callers should not have to find them: WishFinder r70 and Purple-lib both hand a table of their functions to each plugin that exports a known name (`wishfinder_on_register`, `purplelib_on_register`), the way [below](#a-library-that-calls-its-clients-purple-lib). `nn::ro::LookupSymbol` resolves only the game's own modules and finds nothing in a plugin, which is why the library reads each NRO's symbol table itself (`mods/wishfinder/core/src/nro.rs`, `mods/purple-lib/core/src/nro.rs`). WishFinder keeps its exports for callers built before the table. Rules from WishFinder and its two bridges:

- The contract is a fixed-layout record (WishFinder's 64-byte `WishFinderEntry`) and a version function the caller checks first. Check range readability and alignment on entry, copy, and hand the data to `forge_onUpdate` through a bounded mailbox; nothing locks.
- A plugin that exports only Forge's callbacks (My Weapon Tree) cannot be looked up by symbol. Walk `svcQueryMemory` for an R-X mapping starting with an NRO header (`NRO0` at +0x10) whose build ID at +0x40 matches, pin that exact build, and check the whole range is mapped readable before every read of its memory. Then read its data by fixed offsets (the bridge's DEVELOPMENT.md has a layout table); a host test that loads the real NRO at base 0 checks the offsets and relocated tables.
- Keep the logic in a `core` crate that both the plugin and the host test build (`mods/wishfinder-mwt-bridge/core/src/lib.rs`).
- Find a partner by its exported name or build ID, never by folder prefix or position.

### A library that calls its clients (Purple-lib)

Purple-lib puts a mod's settings in the game's Options window and its topics in the game's help. To use it from a mod, read `mods/purple-lib/API.md` and copy from the two working clients: **Purple-lib Tester** (`mods/purple-lib-tester`, every feature: each row kind, action rows with the mod's own window, the input hold, a preview beside the page, page help, help topics with `open`) and **Please do Better** (`mods/please-do-better/src/purple_lib.rs` and `core/src/purple_lib.rs`, a shipping mod's page: two labels rows in seven languages, a help topic per row, lock-free `get`/`set`, saving on `closed`). `mods/purple-lib/examples/` holds the same in a single file for C++ and Rust.

How it works, and what to keep when another library needs the same:

- The client exports one function, `purplelib_on_register(const PurpleLibApi *)`, and imports nothing, so it loads and works without the library. At its first `forge_onUpdate` the library walks the process's R-X mappings (`svcQueryMemory`), reads that name from each NRO's dynamic symbol table and calls it with a table of its functions (`mods/purple-lib/src/registry.rs::call_mods`, `core/src/nro.rs`). Forge runs every `forge_onLoad` and `forge_onInit` before any `forge_onUpdate` (`tools/forge-local/source/forge/plugin.cpp`), so every client is loaded and initialised by then, in any load order. Runs on Eden and MHGURecomp (Purple-lib r17 with Tester r10 and Please do Better r36).
- A Rust mod exports every `#[unsafe(no_mangle)] pub extern "C"` function: its `build.rs` passes only `link/switch32.ld` to the linker, so `link/exported.txt`, a copy of cargo-forge's template pinned in `dependencies.lock.json`, stays as it is (the WishFinder bridges r9 and r18 export `wishfinder_on_register` without it; their `verify.py` reads it in the NRO's dynamic symbols). A C++ mod lists the name in `src/exports.txt`. Either way add it to the mod's export audit (`scripts/verify.py`, or `CALLBACKS` in `scripts/please_do_better.py`).
- The library calls only an address that is a multiple of 4 inside executable memory, and every read of a foreign mapping is checked readable first.
- The table starts with a version word and only grows at its end; a record is read by its `size`. The client registers when the version is at least the one it was built for.
- A client learns the library is absent by not being called: the two first updates come in load order, so the client's second `forge_onUpdate` is the earliest it can tell.
- Why not a plain import or a Forge lookup: Forge keeps each plugin's `nn::ro::Module` private (`plugin.cpp` `getSymbol`), and MHGURecomp binds a plugin's import only against modules loaded before it, a weak one to 0 (`references/MHGURecomp/runtime/loader.c` `resolve`), so an import works only in one load order. How the Switch's `nn::ro` binds imports between plugins is unread.
- `python3 scripts/mod_distribution.py check` compares every mod's copy of Purple-lib's records, table and names with `mods/purple-lib/core/src/api.rs` (`purple_lib_clients`), because no mod may build from a sibling. A client's `Api` table may be the start of Purple-lib's (an older API version's: the table only grows at its end); the other records match exactly.
- Purple-lib's API exports stay in its NRO for a mod that finds them itself (API version 2); no mod in this workspace does any more. Version 4 (Purple-lib r19) adds `purplelib_help_shown` at the table's end: true while a page's own help screen is open.

## Standalone workflow

From a maintained mod's directory:

```sh
./build.sh fetch      # Rust mods, once: the only network step
./build.sh doctor
./build.sh prepare
./build.sh build
./build.sh test
./build.sh verify
./build.sh package
./build.sh export --output DEST
```

Consult its usage for arguments. `test --host` intentionally omits native checks. `fetch` (Rust mods) and `prepare --fetch` (C template) are the only download operations. Supply copied/hash-verified inputs through ignored `build.local.json`. The mod owns its source, locks, dependency snapshots, recipes, tests, export allowlist, licenses, and notices. Sibling mods, installed emulators, personal paths, and parent Git history cannot be build dependencies.

## Rust dependencies

Git does not track fetched third-party trees; each mod's `.gitignore` lists them. `scripts/fetch_vendor.py` (identical in every mod and in the C template) downloads each `archives` entry in `dependencies.lock.json`, a GitHub tree at a pinned commit (`repo`, `rev`, `dest`, optional `source` prefix), and writes only the files pinned under its `dest`, the longest matching `dest` owning a file. It then applies the entry's tracked `patches` with GNU `patch -p1` inside `dest` and checks every pinned file against its SHA-256. Rust mods get forge-rs from `forge_rs_revision` (or an explicit `vendor/forge-rs/` entry), then `cargo vendor --quiet --locked --versioned-dirs` with `--sync` for the toolchain's `library/Cargo.toml` (build-std) and every `tests/*/Cargo.lock`. It refuses to overwrite existing vendor folders. Rust mods run it as `./build.sh fetch`, and `doctor` stops with "run ./build.sh fetch" when `vendor/crates` is missing; the C template runs it from `prepare --fetch` (Forge, jeffi6375/libnx, cimgui, imgui into `vendor/forge` and `vendor/sdk`; pins in `templates/standalone/vendor.lock.json`, copied into each new mod's lock by `init`). Crates are checked by cargo against `Cargo.lock`, so locks pin no `vendor/crates` files. `export_source.py` skips fetched folders (`FETCHED`). Damage Numbers also fetches cimgui/imgui and Roboto Medium, and patches forge-rs with `patches/forge-rs-c-char.patch`. Source: `mods/damage-numbers/dependencies.lock.json`, `mods/lock-on-target/scripts/fetch_vendor.py`.

To change a dependency, edit `Cargo.lock` (or `forge_rs_revision` and the forge-rs pins), delete both vendor folders, run `fetch`, then `doctor`. Every release `notices` path must be a tracked file: copy a crate's license into `licenses/` (for example `licenses/LOG-MIT.txt`, `licenses/FORGE-RS-MIT.txt`) instead of pointing at `vendor/`, or `check --staged` fails with "Missing file".

Rust NROs embed absolute source paths (std and crate panic locations, for example `.../vendor/crates/log-0.4.34/src/__private_api.rs`), so the same source built in two folders can give different bytes. Lock-on Target, Multiplayer Roaming, Shared Urgent Quests, Village Quests in Hub and the My Weapon Tree bridge happened not to, so their exported builds matched their releases; Damage Numbers, ImGui Meter, Key Quest Markers, WishFinder, the KatSmithy bridge and World Sharpness Gauge did not. To prove two builds equal, build both at one path. Removing the vendor trees was checked that way: all 13 NROs matched HEAD. An equal NRO does not cover code compiled only for host tests: forge-rs without the Damage Numbers patch builds the same NRO, because C `char` is `u8` on the ARM target, but fails the x86_64 render harness, where it is `i8`. Run `test --host` as well.

Workspace scaffolding: `python3 scripts/mod_distribution.py init NAME --kind plugin`. Upstream Rust scaffolding is `cargo forge new NAME`, followed by `cargo forge build --release`; the standalone recipe remains authoritative for maintained mods. Forge's own source build needs its submodules, devkitARM/devkitPro, and LZ4. Do not install system packages merely to explain a build.

Sources: `tools/forge-local/source/forge/plugin.cpp`, `tools/forge-local/include/forge/hook.h`, `tools/forge-local/libs/libnx/nx/include/switch/kernel/jit.h`; `tools/forge-rs/forge-sys/src/init.rs`, `tools/forge-rs/forge-macros/src/lib.rs`; maintained `src/lib.rs`, `src/abi.rs`, mod-local `scripts/verify.py`, dependency locks; `docs/DEVELOPMENT.md`.
