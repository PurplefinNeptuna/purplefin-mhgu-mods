# Forge APIs, ABI and builds

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
