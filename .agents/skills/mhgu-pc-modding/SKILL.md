---
name: mhgu-pc-modding
description: Port or write Forge PC 0.2.1 plugins (.so/.dll) for Monster Hunter Generations Ultimate 1.4.0 running as a native GURecomp export on Linux or Windows. Covers how PC hooks differ from Switch Forge, guest-address rules, the PC scaffold and build, paired Linux/Windows packaging, hot reload and lifetimes, settings, and reading GURecomp/Forge PC logs. Use with mhgu-understanding for game research; not for Switch .nro plugins (use mhgu-forge-modding).
---

# MHGU PC Modding (GURecomp + Forge PC)

GURecomp recompiles the Switch game's ARM32 code into a native x64 program.
Forge PC 0.2.1 loads native plugins into it. Game data and offsets are the
same as Switch 1.4.0 (main build `FB08F1D20FD1204FE7070672777F869B`), so
offsets from `mhgu-understanding` apply. The **hooking model is completely
different**, so Switch hook code cannot be reused. Knowledge dated 2026-10-20.

Read first: `docs/GURECOMP.md` (setup, paths, port research), then the PC mod's
`AGENTS.md` and `DEVELOPMENT.md`. Working examples: `mods/key-quest-markers-pc`
(smallest; one post hook, returns a guest string), `mods/modern-weapon-controls-pc`
(five hooks), `mods/damage-numbers-pc` (overlay), `mods/please-do-better-pc`.

## How PC differs from Switch

| Topic | Switch Forge 1.5.1 | Forge PC 0.2.1 |
| --- | --- | --- |
| Plugin binary | ARM32 `.nro` | x64 `.so` (Linux) **and** `.dll` (Windows), both shipped |
| Hook | Overwrites 8 ARM bytes, trampoline calls original | `hook_create(target, pre, post, user)` registers callbacks on a recompiled block; no bytes are written |
| Where hooks work | Any safe instruction pair | Only at the **start of a recompiled block** (function entries, branch targets). `hook_create` returns NULL otherwise |
| Interior taps | Possible with a gateway | Only if that address is already a block start. A post hook is not an instruction tap: the epilogue may already have restored registers |
| Skip original | Detour does not call the trampoline | Pre callback returns `FORGE_HOOK_RETURN` (returns to guest LR) |
| Patching code bytes | Changes behaviour | `mem_write` to code does nothing to the compiled game. Use hooks |
| Pointers | Native pointers into game memory | Game addresses are `uint32_t` guest addresses. Never return or store a host pointer for the game |
| Calling game functions | Direct call through a function pointer | `forge_api->call(addr, args, n, fargs, fn, &out)`; only for functions that never wait or make system calls. A failed call restores registers but not memory |
| Plugin-owned game data | Game allocators | `mem_alloc(size, align)` returns guest memory the game can read |
| Singletons/DTI | Forge singleton/DTI lookup | `singleton_getByName("sMhGUI")`, `dti_of`, `dti_name` |
| Module base | Forge main base | `mem_getModuleBase("main")` + main-relative offset |
| Unload | None | Hot reload can unload a plugin while the game holds its data |

## Rules

- Guest addresses are always `uint32_t`. Read and write game memory with
  `mem_read`/`mem_write` (or `mem_ptr` for a checked contiguous view).
- Check every `hook_create` result on the actual export. A NULL means that
  address is not a block start in this export; redesign or pick another block.
  Earlier offline block probes do not prove anything about the user's export.
- Register all hooks for a feature, and if one fails, disable the earlier ones
  with `hook_enable(h, false)`.
- Data handed to the game (strings, structs) must live in `mem_alloc` memory and
  stay alive for as long as the game may hold it. Key Quest Markers PC keeps its
  titles until process exit and requires `hot_reload = false`.
- Default build, verify and package need **both** Linux `.so` and Windows `.dll`.
  A single-target build is development-only and cannot be packaged.
- Native plugin builds disable C++ exceptions and RTTI; never throw across the
  loader boundary.
- Same workspace rules as Switch: new version per runtime change, no install or
  launch without being asked, full `python3 scripts/mod_distribution.py check`
  before committing, and honest validation scope (Windows gameplay is untested
  for every current PC mod).

## Playbook: new PC plugin or port

1. `python3 scripts/mod_distribution.py init NAME-pc --kind plugin --platform forge-pc`.
   PC mods live in their own `<name>-pc` folder; only `--kind plugin` is supported.
2. From the mod folder: `./build.sh doctor`, then `./build.sh build` to prove
   the empty plugin compiles for Linux (GCC) and Windows (MinGW-w64). Needs GCC,
   MinGW-w64, CMake, Ninja, Python 3 and binutils; `prepare` downloads nothing.
3. In `src/plugin.cpp`, keep `forge_onLoad` filling `ForgePluginInfo` with
   `required_ver = {0, 2, 1}`. Install hooks in `forge_onInit`. In
   `forge_onUnload`, disable hooks and free only `mem_alloc` blocks the game
   can no longer hold; keep anything the game may still point to. Check
   `forge_api->size` before using a 0.2 field such as `mem_alloc`.
4. For each Switch hook you are porting, decide the PC form:
   entry around hook → pre (copy args) + post (read `cpu->r[0]`, saved
   `args[0..3]`, `args[4]` entry LR, `args[5]` entry SP); entry before-only tap
   → pre; interior tap → only if the address is a block start, otherwise find an
   earlier block start whose state is equivalent (see the Please do Better notes
   in docs/GURECOMP.md "Per-mod implementation route").
5. Port the pure logic (classification, policies, presentation math) unchanged
   and replace the native layer with guest-memory adapters. Add host tests with
   a fake guest memory, as the existing PC mods do.
6. `./build.sh test --host`, `./build.sh verify`, then package as the mod's
   DEVELOPMENT.md describes and run the workspace `check`.
7. Report hashes for both libraries and the steps the user should run.

## Installing and running (only when the user asks)

| Item | Path |
| --- | --- |
| Game folder | `/mnt/storage/Games/GURecomp/Game/MONSTER HUNTER GENERATIONS ULTIMATE/` |
| Plugins | `mods/0100770008DD8000/<mod-folder>/plugins/<name>.so` and `.dll` |
| Forge PC | `mods/0100770008DD8000/Forge/` (`forge.so`, `forge.ini`), enabled by `[Mods] loader = Forge/forge.so` in `game_settings.ini` |
| Hot reload | `forge.ini` `[plugins]` `hot_reload = false` for plugins that publish guest data |
| Game log / report | `user/log/suyu_log.txt`, `user/recomp_report.txt` |
| Forge PC log | `mods/0100770008DD8000/Forge/forge.log` |

Launch with the SDL workaround (fish):

```fish
cd "/mnt/storage/Games/GURecomp/Game/MONSTER HUNTER GENERATIONS ULTIMATE"
env SDL3_DYNAMIC_API=/usr/lib/libSDL3.so.0 "./MONSTER HUNTER GENERATIONS ULTIMATE"
```

Without it, F10 fails with `no renderer: SDL not built with rendering support`.
Try this before proposing a rebuild. **Insert** opens Forge's overlay; **F10**
opens GURecomp's menu. Guest addresses in logs change between launches; use
main-relative offsets.

After a reported run, read all three logs, confirm Forge PC 0.2.1 attached
(ABI 2), find your plugin's registration lines and compare the installed
library hashes with the package before concluding.
