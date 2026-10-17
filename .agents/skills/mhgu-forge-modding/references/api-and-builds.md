# Forge APIs, ABI, and builds

## Version and architecture

The Switch loader is native ARM32. C++ and Rust plugins produce `.nro` modules loaded into the game process. They can access native memory and affect game stability. A Rust wrapper does not establish pointer validity or game ownership.

| Component | Pinned source | Role |
| --- | --- | --- |
| Forge 1.5.1 | `b23e114a23f41c9a8e2fd34b2f4df2a2102d0ee1` | Loader, hooks, callbacks, graphics, native facilities |
| forge-rs 1.5.0 | `d1865b68e9b194eb3eacc8bd71bbf601a5fac63e` | Raw bindings, Rust wrappers/macros/runtime |
| cargo-forge converter 1.4.1 | Fingerprinted by the mod dependency lock/tool status | Separate ELF-to-NRO build tool |

Current Forge source is [Fexty's fork](https://github.com/Fexty12573/forge), based on Jeffi's original Forge. Update the existing official checkout in place when requested. Retired local loader, renderer, Better Input, mutex, and support patches are not the baseline. Historical revisions remain useful for interpreting evidence.

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

Version satisfaction compares major/minor ordering and ignores patch. Requesting 1.5.1 is not a strict runtime equality guard. Verify actual ABI/signatures separately. Current Damage Numbers `src/lib.rs` writes explicit 1.5.1/name metadata; older development paragraphs describing a no-op load callback are superseded by that source.

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
