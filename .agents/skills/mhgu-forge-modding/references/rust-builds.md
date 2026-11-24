# Rust NRO builds and dependencies

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

## Rust dependencies

Git does not track fetched third-party trees; each mod's `.gitignore` lists them. `scripts/fetch_vendor.py` (identical in every mod and in the C template) downloads each `archives` entry in `dependencies.lock.json`, a GitHub tree at a pinned commit (`repo`, `rev`, `dest`, optional `source` prefix), and writes only the files pinned under its `dest`, the longest matching `dest` owning a file. It then applies the entry's tracked `patches` with GNU `patch -p1` inside `dest` and checks every pinned file against its SHA-256. Rust mods get forge-rs from `forge_rs_revision` (or an explicit `vendor/forge-rs/` entry), then `cargo vendor --quiet --locked --versioned-dirs` with `--sync` for the toolchain's `library/Cargo.toml` (build-std) and every `tests/*/Cargo.lock`. It refuses to overwrite existing vendor folders. Rust mods run it as `./build.sh fetch`, and `doctor` stops with "run ./build.sh fetch" when `vendor/crates` is missing; the C template runs it from `prepare --fetch` (Forge, jeffi6375/libnx, cimgui, imgui into `vendor/forge` and `vendor/sdk`; pins in `templates/standalone/vendor.lock.json`, copied into each new mod's lock by `init`). Crates are checked by cargo against `Cargo.lock`, so locks pin no `vendor/crates` files. `export_source.py` skips fetched folders (`FETCHED`). Damage Numbers also fetches cimgui/imgui and Roboto Medium, and patches forge-rs with `patches/forge-rs-c-char.patch`. Source: `mods/damage-numbers/dependencies.lock.json`, `mods/lock-on-target/scripts/fetch_vendor.py`.

To change a dependency, edit `Cargo.lock` (or `forge_rs_revision` and the forge-rs pins), delete both vendor folders, run `fetch`, then `doctor`. Every release `notices` path must be a tracked file: copy a crate's license into `licenses/` (for example `licenses/LOG-MIT.txt`, `licenses/FORGE-RS-MIT.txt`) instead of pointing at `vendor/`, or `check --staged` fails with "Missing file".

Rust NROs embed absolute source paths (std and crate panic locations, for example `.../vendor/crates/log-0.4.34/src/__private_api.rs`), so the same source built in two folders can give different bytes. Lock-on Target, Multiplayer Roaming, Shared Urgent Quests, Village Quests in Hub and the My Weapon Tree bridge happened not to, so their exported builds matched their releases; Damage Numbers, ImGui Meter, Key Quest Markers, WishFinder, the KatSmithy bridge and World Sharpness Gauge did not. To prove two builds equal, build both at one path. Removing the vendor trees was checked that way: all 13 NROs matched HEAD. An equal NRO does not cover code compiled only for host tests: forge-rs without the Damage Numbers patch builds the same NRO, because C `char` is `u8` on the ARM target, but fails the x86_64 render harness, where it is `i8`. Run `test --host` as well.

Workspace scaffolding: `python3 scripts/mod_distribution.py init NAME --kind plugin`. Upstream Rust scaffolding is `cargo forge new NAME`, followed by `cargo forge build --release`; the standalone recipe remains authoritative for maintained mods. Forge's own source build needs its submodules, devkitARM/devkitPro, and LZ4. Do not install system packages merely to explain a build.

Sources: `tools/forge-local/source/forge/plugin.cpp`, `tools/forge-local/include/forge/hook.h`, `tools/forge-local/libs/libnx/nx/include/switch/kernel/jit.h`; `tools/forge-rs/forge-sys/src/init.rs`, `tools/forge-rs/forge-macros/src/lib.rs`; maintained `src/lib.rs`, `src/abi.rs`, mod-local `scripts/verify.py`, dependency locks; `docs/DEVELOPMENT.md`.

## Lawrence's hardware-test loader

[Lawrence-al/forge](https://github.com/Lawrence-al/forge) at [`bbc540f4b831881f4980a4939a049cc14c31b9e4`](https://github.com/Lawrence-al/forge/commit/bbc540f4b831881f4980a4939a049cc14c31b9e4) is one commit ahead of the pinned Forge 1.5.1 base. The reviewed diff retains the public Hook header and adds hardware startup/loading fixes. Its [hardware document](https://github.com/Lawrence-al/forge/blob/bbc540f4b831881f4980a4939a049cc14c31b9e4/docs/hardware-compatibility.md) specifies the same Rust flags and says loader fixes do not rewrite plugin relocations.

Plugins built against the pinned 1.5.1 SDK are expected to work with that reviewed fork when their imports and ABI match. Confirm the tester's exact loader revision/binary, strong imports and runtime results before claiming compatibility. The fork is an optional hardware-test loader; it does not replace the workspace's stock SDK/source baseline or become a required dependency merely because a test uses it. The reviewed source and the r18/r28 candidates were not tested together on physical hardware here.
