---
name: mhgu-forge-modding
description: Develop, review, build, package, and diagnose native ARM32 Forge plugins for Monster Hunter Generations Ultimate on Switch. Covers C/C++ Forge and forge-rs, hooks, native GUI extensions, rendering, settings, and release evidence. Use for Switch plugins running on hardware or Switch emulators, not Forge PC or GURecomp ports.
---

# MHGU Forge Modding

Target MHGU Switch 1.4.0, title `0100770008DD8000`. The compiled knowledge snapshot is dated 2026-10-17, with NRO build/hardware and HUD planning guidance updated 2026-10-18. Source baseline: stock Forge 1.5.1 and forge-rs 1.5.0. Read only the topic references needed for the task.

## Start the task

1. Establish the game/build, loader revision, affected mod, and requested operation. In the original workspace, read its current instructions and the mod's development/distribution records. Preserve unrelated edits and accepted bytes.
2. Search existing code, saved Ghidra/DTI, and fixtures before adding native calls or replacing Forge facilities. The companion `mhgu-understanding` skill explains game structures and resource discovery.
3. Match every native boundary to actual target headers, instructions, exports, and calling conventions. Imported annotations and a successful build do not establish a valid runtime contract.
4. For every Switch Rust/GCC NRO build, retain PIC and the `-nostartfiles` / `-Wl,-z,text` linker settings. Apply them to new mod targets before the first build. Follow [NRO relocation requirements](references/api-and-builds.md#rust-nro-relocation-requirements), including final ELF/NRO checks.
5. Validate the changed behavior, package where required, and report exact evidence limits. Preparation does not authorize installation, activation, game launch, settings/save edits, publication, or push.

For GUI plans and reviews, read [Native GUI extensions](references/native-gui-extensions.md) before treating the quest-row recipe as a solution for another menu. Require the target's ownership/map/cache audit and a complete rendering path. Version and package diagnostic candidates before manual tests using [Validation and delivery](references/validation-and-delivery.md).

## Choose a reference

| Task | Read |
| --- | --- |
| Loader, Rust/C++ APIs, metadata, ABI, standalone builds | [API and builds](references/api-and-builds.md) |
| Detours, trampolines, flags, TLS, transactions, rollback | [Hooks and lifetimes](references/hooks-and-lifetimes.md) |
| Add game-owned GUI objects or extend a native menu | [Native GUI extensions](references/native-gui-extensions.md) |
| ImGui, fonts/textures, damage overlay, INIs, save mounts | [Rendering and settings](references/rendering-and-settings.md) |
| Tests, exports, packaging, legal/support files, commits | [Validation and delivery](references/validation-and-delivery.md) |
| Failed initialization, logs, historical failures, physical Switch feasibility | [Diagnostics](references/diagnostics.md) |
| Original workspace paths, evidence locations, source coverage | [Workspace and sources](references/workspace-and-sources.md) |

## Portable use

The Markdown references carry the findings. `agents/openai.yaml` is optional UI metadata. Commands beginning `./scripts/tool.sh`, `python3 scripts/…`, or `./build.sh` require the corresponding checkout and its prerequisites. Source pointers name workspace-root paths or files beneath a named mod/upstream checkout. They are optional verification inputs when these skills are copied elsewhere.

If private executables, resource fixtures, or saved analysis are unavailable, identify the missing input and continue only with supported source/host checks. Do not fabricate signatures, substitute MHXX/PC layouts, or claim native verification. Hardware compatibility remains unconfirmed.
