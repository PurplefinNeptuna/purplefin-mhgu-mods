# Forge APIs, ABI, and builds

## Version and architecture

The Switch loader is native ARM32. C++ and Rust plugins produce `.nro` modules loaded into the game process. They can access native memory and affect game stability. A Rust wrapper does not establish pointer validity or game ownership.

| Component | Pinned source | Role |
| --- | --- | --- |
| Forge 1.5.1 | `b23e114a23f41c9a8e2fd34b2f4df2a2102d0ee1` | Loader, hooks, callbacks, graphics, native facilities |
| forge-rs 1.5.0 | `d1865b68e9b194eb3eacc8bd71bbf601a5fac63e` | Raw bindings, Rust wrappers/macros/runtime |
| cargo-forge converter 1.4.1 | Fingerprinted by the mod dependency lock/tool status | Separate ELF-to-NRO build tool |

Current Forge source is [Fexty's fork](https://github.com/Fexty12573/forge), based on Jeffi's original Forge. Update the existing official checkout in place when requested. Retired local loader, renderer, Better Input, mutex, and support patches are not the baseline.

## Loader contract

Forge scans `app:/nativeNX/plugins` for `.nro`, registers module hashes, loads modules, resolves callbacks, calls `forge_onLoad`, checks the requested version, and calls `forge_onInit` for accepted plugins. Keep startup independent of ImGui availability.

| Export | Native signature / purpose |
| --- | --- |
| `forge_onLoad` | `void(PluginInitParam*)`, fill metadata |
| `forge_onInit` | `void()`, initialize plugin |
| `forge_onUpdate` | `void(float dt)`, after original game update |
| `forge_onImGuiInit` | `void(void* ctx, void* alloc, void* free)` |
| `forge_onImGuiRender` | `void()`, inside Forge's plugin UI |
| `forge_onImGuiFreeRender` | `void()`, drawing outside the main window |

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

The 2026-10-18 r18/r28 rebuilds removed all six executable-text relocations from each NRO, passed their existing host/ARM fixtures and full distribution checks, and retained gameplay/assets apart from build identification. These are static/build results, not physical Switch acceptance. Evidence: `mods/key-quest-markers/research/hardware-link.json` and `mods/damage-numbers/research/hardware-link.json`.

## Lawrence's hardware-test loader

[Lawrence-al/forge](https://github.com/Lawrence-al/forge) at [`bbc540f4b831881f4980a4939a049cc14c31b9e4`](https://github.com/Lawrence-al/forge/commit/bbc540f4b831881f4980a4939a049cc14c31b9e4) is one commit ahead of the pinned Forge 1.5.1 base. The reviewed diff retains the public Hook header and adds hardware startup/loading fixes. Its [hardware document](https://github.com/Lawrence-al/forge/blob/bbc540f4b831881f4980a4939a049cc14c31b9e4/docs/hardware-compatibility.md) specifies the same Rust flags and says loader fixes do not rewrite plugin relocations.

Plugins built against the pinned 1.5.1 SDK are expected to work with that reviewed fork when their imports and ABI match. Confirm the tester's exact loader revision/binary, strong imports and runtime results before claiming compatibility. The fork is an optional hardware-test loader; it does not replace the workspace's stock SDK/source baseline or become a required dependency merely because a test uses it. The reviewed source and the r18/r28 candidates were not tested together on physical hardware here.

## Plugin-to-plugin APIs

A plugin can export plain C functions for another plugin (Wishlist: `wishlist_api_version`, `wishlist_sync`, `wishlist_search`, `wishlist_add`, `wishlist_remove`). A caller reads them from that plugin's NRO symbol table in its loaded mapping, in its own `forge_onInit` or later (`mods/wishlist-mwt-bridge/core/src/lib.rs::nro_symbol`); every NRO is loaded before any `forge_onInit`, so load order does not matter. `nn::ro::LookupSymbol` resolves only the game's own modules and finds nothing in a plugin. Rules from Wishlist and its My Weapon Tree bridge:

- The contract is a fixed-layout record (Wishlist's 64-byte `WishlistEntry`) and a version function the caller checks first. Check range readability and alignment on entry, copy, and hand the data to `forge_onUpdate` through a bounded mailbox; nothing locks.
- A plugin that exports only Forge's callbacks (My Weapon Tree) cannot be looked up by symbol. Walk `svcQueryMemory` for an R-X mapping starting with an NRO header (`NRO0` at +0x10) whose build ID at +0x40 matches, pin that exact build, and check the whole range is mapped readable before every read of its memory. Then read its data by fixed offsets (the bridge's DEVELOPMENT.md has a layout table); a host test that loads the real NRO at base 0 checks the offsets and relocated tables.
- Keep the logic in a `core` crate that both the plugin and the host test build (`mods/wishlist-mwt-bridge/core/src/lib.rs`).
- Look a partner up by name, never by folder prefix or position.

## Standalone workflow

From a maintained mod's directory:

```sh
./build.sh doctor
./build.sh prepare
./build.sh build
./build.sh test
./build.sh verify
./build.sh package
./build.sh export --output DEST
```

Consult its usage for arguments. `test --host` intentionally omits native checks. `prepare --fetch`, where supported, is an explicit download operation. Supply copied/hash-verified inputs through ignored `build.local.json`. The mod owns its source, locks, dependency snapshots, recipes, tests, export allowlist, licenses, and notices. Sibling mods, installed emulators, personal paths, and parent Git history cannot be build dependencies.

Workspace scaffolding: `python3 scripts/mod_distribution.py init NAME --kind plugin`. Upstream Rust scaffolding is `cargo forge new NAME`, followed by `cargo forge build --release`; the standalone recipe remains authoritative for maintained mods. Forge's own source build needs its submodules, devkitARM/devkitPro, and LZ4. Do not install system packages merely to explain a build.

Sources: `tools/forge-local/source/forge/plugin.cpp`, `tools/forge-local/include/forge/hook.h`, `tools/forge-local/libs/libnx/nx/include/switch/kernel/jit.h`; `tools/forge-rs/forge-sys/src/init.rs`, `tools/forge-rs/forge-macros/src/lib.rs`; maintained `src/lib.rs`, `src/abi.rs`, mod-local `scripts/verify.py`, dependency locks; `docs/DEVELOPMENT.md`.
