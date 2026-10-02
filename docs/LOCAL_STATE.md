# Local baseline

## Current Forge baseline: 2026-10-02

The user installed and tested the combined `forge-better-inputs-compat`
package with patched Forge `1.4.1-legacyctx14` and patched Better Input on
MHGU 1.4.0. This is the baseline for future mod development. The original
Forge/Better Input packages remain rollback inputs; keep them disabled when
the combined package is active. Activation is based on the user's successful
tests, not inferred from directory presence. Other mods' activation still
requires inspection.

The live combined package was inspected read-only on 2026-10-02 and matches
the tested artifacts:

- Package: `~/.local/share/eden/load/0100770008DD8000/forge-better-inputs-compat/`.
- `exefs/subsdk9`: SHA-256 `374684063adb939b389f0e4d1c8766c09e52339bfe9eaedadd4a8f44635252a7`.
- `romfs/nativeNX/plugins/better_inputs.nro`: SHA-256 `84b1549aabda3cfd4228e02a9516d16d8d142787b4589191bb84c39cdbcba872`.
- Config currently has log level `error` and overlay key 73 (Insert).
- Renderer: Vulkan; both caches and asynchronous shader compilation on;
  asynchronous presentation off. Eden was not patched.
- Runtime acceptance: rebuilt Forge alone, three game restarts, the three
  Eden-start sequence, save loading, overlay navigation, Better Input controls,
  and a quest/village transition passed (manual outcomes confirmed by the user).
  Saved logs verify one arena and six hooks per combined game boot.

Local branch and future upstream replay: [FORGE_LOCAL_BRANCH.md](FORGE_LOCAL_BRANCH.md).
Evidence: [FORGE_BETTER_INPUTS_COMPAT_RUNTIME.md](FORGE_BETTER_INPUTS_COMPAT_RUNTIME.md).
The inventories below are historical snapshots from initial preparation.

Dump inspected 2026-10-01T15:41:35.466591+07:00; mod inventories refreshed 2026-10-01T16:30:58.286682+07:00 (Asia/Jakarta). Activation status comes from the user; Eden configuration was not inspected.

## Game dump

- Path: `~/.local/share/eden/dump/0100770008DD8000/`
- Contains `romfs/nativeNX/`; no ExeFS was present.
- Files: 35,531; total file bytes: 12,311,983,212 (about 12.31 GB).
- ARC files: 14,511; GMD text resources: 11,999; TEX files: 1,778.
- NativeNX directories include `arc`, `loc`, `table`, `system`, `sound`, `movie`, and language folders `eng`, `fre`, `ger`, `ita`, `spa`, `chS`, `chT`.
- Observed `loc/arc/resident.arc` begins `41 52 43 00 11 00 c5 00` (ARC magic and an observed version field of 17). This sample does not validate all archive contents.
- Installed game version/build, update inclusion, and dump completeness have not been established.

## Eden's listed mod packages

Path: `~/.local/share/eden/load/0100770008DD8000/`
Total: 7,857 files, 1,171,796,495 file bytes.

These packages are listed in Eden's load directory. The user reports they are
**not activated** as of 2026-10-01; folder presence alone does not establish
activation. No emulator configuration was inspected or changed.

| Package | Files | File bytes |
| --- | ---: | ---: |
| 4K-2K Patch | 1 | 376 |
| FOV (Medium) | 1 | 9,057,470 |
| HD Textures v4 | 7,644 | 1,111,629,474 |
| HD UI v4 | 211 | 51,109,175 |

## Uninstalled mod and cheat library

Path: `/mnt/storage2/ROM/Switch/cheats/mhgu/`
Total: 9,304 files, 2,349,208,716 file bytes.

This folder stores mods not yet installed. Keep it separate from Eden's load
directory, even when both contain packages with the same name.

| Package | Files | File bytes |
| --- | ---: | ---: |
| 120FPS Patch | 1 | 109 |
| 4K-2K Patch | 1 | 376 |
| 60FPS Patch | 1 | 110 |
| FOV v4 | 4 | 36,229,880 |
| HD Textures v4 | 7,644 | 1,111,629,474 |
| Pixel Cheats | 9 | 1,752 |
| Update 4.0 | 1,610 | 971,937,230 |
| Weakness Icons English | 1 | 9,137,120 |
| Z_Balanced | 30 | 217,870,947 |

Also present: `Install Tutorial.txt`, `MHGU DLC Injector.zip`, and `MHXXSaveEditor.zip`.

Selection rules from the local installation tutorial:

- Choose either 60 FPS or 120 FPS.
- Choose one FOV: Close, Medium, Far, or Extreme.
- HD UI v4 offers seven languages. Each has PlayStation, Nintendo Switch, or Xbox layouts and HDI/CI icon alternatives.
- Pixel Cheats has separate Ryujinx and Yuzu distributions. Eden compatibility has not been tested.

The FPS and Pixel cheat filenames use `FB08F1D20FD1204F`. The 4K/2K patch declares title `0100770008DD8000`, version 1.4.0, and NSO ID `FB08F1D20FD1204FE7070672777F869B`. These describe the package targets, not the actual running game.

`Z_Balanced` (renamed from `Z_HD Balanced`) contains 30 replacement ARCs, including player quest/shell resources, `loc/arc/resident.arc`, `eng/arc/title_eng.arc`, and two weapon resources. Its internal edits and provenance are unknown. Its filenames do not establish that it is cosmetic. Check exact replacement paths and internal resources against selected packages before combining mods; runtime interactions still need inspection.

`Weakness Icons English` contains one replacement: `romfs/nativeNX/eng/arc/resident_eng.arc`. Its internal edits have not been inspected.

The DLC injector ZIP contains a Windows executable plus `system`/`system_backup` save files. The save editor ZIP contains a Windows executable. Neither was extracted or run.

## Preparation status

- Public reference repository and wiki downloaded; revisions in `references/provenance.json`.
- `python3`, `git`, `dotnet`, `wine`, `ffmpeg`, and `7z` were found on PATH. This does not verify modding-tool compatibility.
- `blender` and `010editor` were not found on PATH during initialization.
  Blender is now installed locally; 010 Editor was not installed.
- The full local toolkit and smoke checks are documented in [TOOLS.md](TOOLS.md).
- This project has not created, installed, or enabled any mods. The existing Eden packages were supplied by the user; no saves or emulator settings were changed by this preparation.
- Mod-specific build recipes and host tests now exist under `scripts/` and
  `mods/`; there is no automated in-game test suite. Git was initialized on
  `main` on 2026-10-01. The workspace sources, recipes, and documentation are
  being recorded in coherent local commits on 2026-10-02; generated outputs,
  game assets, tools, and backups remain ignored.

Machine-readable metadata: [local-state.json](local-state.json). Re-inspect relevant files before editing; counts can change.
