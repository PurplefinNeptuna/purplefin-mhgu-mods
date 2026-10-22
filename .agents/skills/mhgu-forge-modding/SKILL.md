---
name: mhgu-forge-modding
description: Develop, change, debug, build, package and release native ARM32 Forge plugins (.nro) for Monster Hunter Generations Ultimate 1.4.0 on Switch, Eden and Ryujinx. Step-by-step playbooks for new plugins, behaviour changes, user bug reports, adding hooks, promotion and doc refreshes, plus reference material on Forge/forge-rs APIs, hooks, native GUI insertion, ImGui rendering, settings and release evidence. Not for Forge PC or GURecomp ports (use mhgu-pc-modding).
---

# MHGU Forge Modding

Target: MHGU Switch 1.4.0, title `0100770008DD8000`, main build ID
`FB08F1D20FD1204FE7070672777F869B`. Loader: stock Forge 1.5.1 (Fexty's fork),
forge-rs 1.5.0. Knowledge dated 2026-10-20.

## Start here

1. Read the workspace `AGENTS.md`, then `mods/NAME/AGENTS.md`,
   `mods/NAME/DEVELOPMENT.md` (current state is at the top) and
   `mods/NAME/DISTRIBUTION.json` (authoritative status and hashes).
2. Pick the matching procedure in [Playbooks](references/playbooks.md) and
   follow it step by step. Each step names the exact command or file.
3. Open a topic reference below only when a step needs it.
4. Finish with the playbook's commit steps and report template.

## Game data

These are read-only originals. Copy a file into the scratchpad or `work/NAME/`
before extracting, unpacking or editing it.

| Location | What it holds | Use it for |
| --- | --- | --- |
| `~/.local/share/eden/dump/0100770008DD8000/romfs/` | Every game resource (ARC archives in `nativeNX/arc/`, GUI, tables, per-language text), 12 GB, no code. Eden dumped it on 2026-10-01 with the 1.4.0 update loaded, so it should be base and update merged; no file has been compared against the base yet. | Finding and reading resources: `rg --files DUMP/romfs \| rg NAME` |
| `work/shared/game-exefs/` | The 1.4.0 code only: `main` (the game), `sdk`, `subsdk0`, `rtld`, `main.npdm`. `forge` is Forge 1.5.1's `subsdk9`, not game code. | Instruction bytes and signatures. Read `main` with `scripts/mhgu_binary.py` `main_image()`, which refuses any other version. |
| `work/research-tooling/` | Saved Ghidra project/export and DTI index built from that `main` | Search first: `./scripts/tool.sh research find QUERY --kind functions` |
| `/mnt/storage2/ROM/Switch/Game/Monster Hunter Generations Ultimate™ [0100770008DD8000][v0]).xci` | Sealed base game (v0) | Rarely needed: an original the dump lacks |
| `/mnt/storage2/ROM/Switch/Update+DLC/MONSTER HUNTER GENERATIONS ULTIMATE [0100770008DD8800][v262144].nsp` | Sealed 1.4.0 update, about 193 MiB (v262144; Eden logs it as "v0.4.0"). Mostly a RomFS patch: a binary delta that only works applied onto the base RomFS, not a folder of files. | Rarely needed. Its resource changes are in the dump and its code is in `game-exefs/`; nothing else is missing. |
| `/mnt/storage2/ROM/Switch/keys+firmware/` | Keys needed to open the XCI/NSP | Only with the two files above |
| `/mnt/storage2/ROM/Switch/cheats/mhgu/` | Uninstalled mod/cheat library | Not the game, and not installed mods |

Opening the XCI/NSP needs hactool. Only its source is in `tools/hactool-source/`;
build it and extract into the scratchpad.

## Words used in this skill

| Term | Meaning |
| --- | --- |
| NSO / `main` | The game's compressed executable. Read it with `scripts/mhgu_binary.py` `main_image()`, never by seeking into the file. |
| NRO | A Forge plugin binary, loaded from `romfs/nativeNX/plugins/`. |
| main+0xNNNN / main-relative | Offset from the start of the game's main module. All offsets in these skills use this form. |
| Ghidra address | Address in the saved Ghidra database. Subtract `0x009c9000` to get main-relative. |
| Object offset (+0xNN) | Field position inside a game object. Never subtract the image base from it. |
| DTI | The game's runtime class metadata (name, size, properties, vtable). It describes a class; it is not an instance. |
| Hook / detour | Forge replaces the first 8 bytes of a function with a jump to your code. |
| Trampoline | Forge's copy of those 8 bytes plus a jump back, used to call the original. |
| Interior tap | A hook in the middle of a function, not at its entry. Needs full register preservation. |
| GE / NZCVQ | ARM status flag groups. Restore NZCVQ; never write GE (`APSR_g`). |
| Candidate | A packaged DEVELOPMENT build under `build/NAME/candidates/rN/`. |
| Release | A READY_TO_DISTRIBUTE build under `build/NAME/releases/rN/`. |
| Accepted | The user reported it working on a named emulator for exact hashes. |

## Hard rules

**Always**
- Give every runtime change a new version `rN`. Old candidates and releases stay byte-for-byte.
- Verify every offset against the original NSO bytes before using it.
- Use Forge headers and APIs first. When you must go lower, write the verified gap next to the code.
- Keep PIC and `-nostartfiles` / `-Wl,-z,text` in every Rust/GCC NRO target.
- Install hooks all-or-nothing, with signature checks before any write and rollback on failure.
- Copy values out of game memory inside the hook; render and log from copies later.
- Run `python3 scripts/mod_distribution.py check` before every commit.
- Say exactly what was validated and what was not.

**Never**
- Install, enable, launch an emulator, change emulator settings, edit saves, publish or push unless the user asked for that exact action now.
- Edit original dumps, the uninstalled library, `backups/accepted/` or `work/` research inputs.
- Invent an offset, signature, struct layout, licence, author or AI-provenance claim.
- Use MHXX or PC layouts for Switch, or Ghidra bytes for signatures.
- Write `msr APSR_g` / `APSR_nzcvqg`, hold game pointers after a callback, do file I/O or locking inside a hook, or log every frame.
- Create `_backup` config files, or restore the retired loader, Better Input, renderer, mutex or PC patches.
- Call something "working" or "tested" when it was only built or unit-tested.

## Stop and ask the user when

- The task needs installing, launching or a save/settings change.
- You need a game input that is not in `work/` or `build.local.json` (for example a different game version).
- Two sources disagree about an offset or layout and you cannot resolve it from the original bytes.
- The fix would change behaviour the user did not ask about.
- A promotion is implied but the user never said "ready to distribute" (or equivalent) for that version.

Otherwise keep going, record unknowns in DEVELOPMENT.md, and finish the parts that do not depend on them.

## Common mistakes

| Mistake | Correct approach |
| --- | --- |
| Rebuilding a release to "promote" it | Promotion ships the existing candidate bytes unchanged (playbook P5). |
| Trusting a nonzero `Hook` record | Forge returns one even on failure. Check the trampoline bytes and executable mapping. |
| Hooking a function that starts with `ldr rX,[pc,#N]` | PC-relative instructions break when copied. Pick another site. |
| Reading the local player index from sUserInfo | Use session `0x188ca48` +0x30 (input-and-actions in mhgu-understanding). |
| Using Forge `malloc` for game GUI objects | Use the class DTI's MT allocator so the native destructor frees it correctly. |
| Appending a GUI child without growing the object map | The game indexes the map by the tree count and crashes. Grow map and draw cache together. |
| Fixing `check` failures by editing release folders by hand | Use `package NAME --refresh-support` for doc-only changes. |
| Concluding from an old log or a folder listing | Read the newest log and match installed hashes first (playbook P3). |
| Assuming a test double proves pixels | GPU commands are doubles. Visible output needs a user run. |

## Topic references

| Task | Read |
| --- | --- |
| Step-by-step procedures | [Playbooks](references/playbooks.md) |
| Loader, Rust/C++ APIs, metadata, ABI, standalone builds | [API and builds](references/api-and-builds.md) |
| Detours, trampolines, flags, TLS, transactions, rollback | [Hooks and lifetimes](references/hooks-and-lifetimes.md) |
| Add game-owned GUI objects or extend a native menu | [Native GUI extensions](references/native-gui-extensions.md) |
| ImGui, fonts/textures, damage overlay, INIs, save mounts | [Rendering and settings](references/rendering-and-settings.md) |
| Tests, exports, packaging, legal/support files, commits | [Validation and delivery](references/validation-and-delivery.md) |
| Failed initialization, logs, historical failures, physical Switch | [Diagnostics](references/diagnostics.md) |
| Workspace paths, evidence locations, source coverage | [Workspace and sources](references/workspace-and-sources.md) |

The companion `mhgu-understanding` skill explains game structures, research
tools and resource formats. For GUI plans, read
[Native GUI extensions](references/native-gui-extensions.md) before treating
the quest-row recipe as a solution for another menu.

## Portable use

The Markdown references carry the findings. `agents/openai.yaml` is optional UI
metadata. Commands beginning `./scripts/tool.sh`, `python3 scripts/…` or
`./build.sh` need this workspace and its prerequisites. Without private
executables, fixtures or saved analysis, name the missing input and continue
only with source/host checks. Hardware compatibility remains unconfirmed.
