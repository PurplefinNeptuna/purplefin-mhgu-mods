# Local baseline

## Current packages: 2026-10-02 cleanup

Split `forge-patched` / `better-inputs-patched` retain tested
hashes/configuration. HD Project replaces V4. HD
Project/Z_Balanced/modern-control follow Base -> HD Project -> Z_Balanced ->
others, with accepted markers/help/crosshair. [Cleanup](CLEANUP_HD_PROJECT.md).

Configured disabled list was empty before migration; deployment removes stale
uncounted entries. Configuration does not prove runtime activation.
[Historical acceptance](FORGE_BETTER_INPUTS_COMPAT_RUNTIME.md). New split/visual set awaits an in-game check.

Keep rollback/backups outside Eden. Inventory, activation snapshot and backup
location: `local-state.json` and deployment report. Source dump/library, saves
and renderer settings are preserved. Below: historical preparation inventories.

Dump inspected 2026-10-01T15:41:35.466591+07:00; mod inventories refreshed 2026-10-01T16:30:58.286682+07:00 (Asia/Jakarta). Activation status comes from the user; Eden configuration was not inspected.

## Game dump

- Path: `~/.local/share/eden/dump/0100770008DD8000/`
- Contains `romfs/nativeNX/`; no ExeFS was present.
- Files: 35,531; total file bytes: 12,311,983,212 (about 12.31 GB).
- ARC files: 14,511; GMD text resources: 11,999; TEX files: 1,778.
- NativeNX directories include `arc`, `loc`, `table`, `system`, `sound`, `movie`, and language folders `eng`, `fre`, `ger`, `ita`, `spa`, `chS`, `chT`.
- Observed `loc/arc/resident.arc` begins `41 52 43 00 11 00 c5 00` (ARC magic and an observed version field of 17). This sample does not validate all archive contents.
- Installed game version/build, update inclusion, and dump completeness are unverified.

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
- Pixel Cheats has separate Ryujinx and Yuzu distributions. Eden compatibility is untested.

The FPS and Pixel cheat filenames use `FB08F1D20FD1204F`. The 4K/2K patch declares title `0100770008DD8000`, version 1.4.0, and NSO ID `FB08F1D20FD1204FE7070672777F869B`. These describe the package targets, not the actual running game.

`Z_Balanced` (renamed from `Z_HD Balanced`) contains 30 replacement ARCs,
including player quest/shell resources, `loc/arc/resident.arc`,
`eng/arc/title_eng.arc`, and two weapon resources. Its internal edits and
provenance are unknown. Its filenames do not prove it is cosmetic. Check exact
replacement paths and internal resources against selected packages before
combining mods; runtime interactions still need inspection.

`Weakness Icons English` contains one replacement:
`romfs/nativeNX/eng/arc/resident_eng.arc`. Its internal edits are uninspected.

The DLC injector ZIP contains a Windows executable plus `system`/`system_backup` save files. The save editor ZIP contains a Windows executable. Neither was extracted or run.

## Preparation status

- Public reference repository and wiki downloaded; revisions in `references/provenance.json`.
- `python3`, `git`, `dotnet`, `wine`, `ffmpeg`, and `7z` were found on PATH. This does not verify modding-tool compatibility.
- `blender` and `010editor` were not found on PATH during initialization.
  Blender is installed locally; 010 Editor was not installed.
- The full local toolkit and smoke checks are in [TOOLS.md](TOOLS.md).
- Initial preparation did not install mods. Later authorized development and
  cleanup installed the selected packages; deployment reports record the changes.
  Saves and unrelated emulator settings remain preserved.
- Mod-specific build recipes and host tests now exist under `scripts/` and
  `mods/`; there is no automated in-game test suite. Git was initialized on
  `main` on 2026-10-01. The workspace sources, recipes, and documentation are
  being recorded in coherent local commits on 2026-10-02; generated outputs,
  game assets, tools, and backups remain ignored.

Machine-readable metadata: [local-state.json](local-state.json). Re-inspect relevant files before editing; counts can change.

## 2026-10-05 damage numbers support update

Open Sans r14 is now the sole supported damage-number edition. A fresh installed
plugin hash matches `be263fbebf8fe2057514aabda07c12724bb0706aad2592ee1c3761100603f158`;
this observation verifies its bytes, not current runtime activation. Private
asset recipes are removed and their payloads archived under workspace backups.
No installation, emulator change or save write is part of retirement. Current
commands and provenance: [retirement record](../mods/damage-numbers/RETIREMENT.md).

## 2026-10-05 final damage numbers r15 release

R15 is finished and ready for distribution, with 1.0 = 20px at 720p / 30px at
1080p. All 324 compiled ARM32 checks and the final host/visual/provenance checks
passed. NRO SHA-256: `7c112c6bf497207f8bdf475687bab3b0056c0726ac4db1707db8f8adc01e07da`.
The installed r14 plugin remains preserved; r15 is packaged separately with
notices and checksums. Current [release notes](../mods/damage-numbers/RELEASE.md).
No new Eden run, save change or installation is part of final packaging.

Final ZIP SHA-256:
`deab7227711afb6f268f5a1c520b85fc027419cf07429a8e9f4be25a09e45828`
(`build/damage-numbers/releases/r15/damage-numbers-r15.zip`). The one-NRO
inventory and content were verified after reopening the archive. Adjacent
notices, final-size README and checksums were verified separately. A second
packaging run produced identical bytes.

R15 packaging correction: the installable ZIP now contains only
`damage-number/romfs/nativeNX/plugins/damage_numbers_capture.nro`, matching
modern-control's runtime-only layout. README, full combined `NOTICES.txt`,
provenance/audit release manifest and checksums remain adjacent. The original
document-filled ZIP is preserved in workspace backups. A fresh installed-file
read now matches r15 (`7c112c6bf497207f8bdf475687bab3b0056c0726ac4db1707db8f8adc01e07da`);
this packaging correction did not replace installed files.

## 2026-10-05 reported overlay corruption

The user reports temporary number/menu corruption when Forge is open while
damage numbers are alive. Source inspection identified missing cumulative
draw-list offsets in Forge's NVN renderer. This is a confirmed code defect and
the leading explanation; no corrected build or runtime confirmation exists yet.
The prior r15 fixtures did not cover this combined GPU-rendering case.
Next-session context, baseline hashes, proposed fix and focused validation:
[renderer handoff](FORGE_IMGUI_DAMAGE_CORRUPTION_HANDOFF.md). No installed files
or rendering code were changed during documentation.

## 2026-10-05 damage numbers r16 compression candidate

The authorized lossless compression trial passed 338 compiled ARM32 checks,
919 core/presentation checks, mailbox stress, 23 transaction scenarios,
ASan/UBSan codec bounds/fuzz checks and the complete open-asset audit.
The accepted RGBA artwork, font, real-ImGui textures, draw output and preview
match r15 byte for byte. NRO: 155,648 bytes (152KiB), down from 262,144 (256KiB).
BSS, imported APIs and steady-state rendering are unchanged. Host decoding is
about 0.14ms once per ImGui context; no new gameplay or live FPS measurement
is claimed.

Clean archive: `build/damage-numbers/releases/r16/damage-numbers-r16.zip`.
Only the runtime NRO belongs in its `damage-number/` folder; README, combined
notices, checksums and provenance remain beside the ZIP. The smaller NRO's
ZIP is 79,992 bytes, versus r15's 69,877, because DN-LZ1 compresses less
well a second time. This affects distribution size, not extracted runtime
payload size. Source and performance details: `mods/damage-numbers/COMPRESSION.md`.

NRO SHA-256: `5f59506f88d5156ed8db7cffd5747651717b3bab7ecdfd398800a0402fe4f33e`.
Installed r15 remains `7c112c6bf497207f8bdf475687bab3b0056c0726ac4db1707db8f8adc01e07da`;
Forge and Better Input fingerprints are unchanged. Nothing was installed or
launched. R15 rollback/provenance is preserved in
`backups/damage-numbers/r15-before-compression-20261005/`. The separate Forge
multi-draw-list visual-corruption handoff remains open.

## 2026-10-05 damage numbers release cleanup

R16 is now the only package under `build/damage-numbers/releases/`. Superseded
releases, old candidates, historical probe reports and pre-cleanup r16
provenance were archived with verified hashes at
`backups/damage-numbers/release-cleanup-20261005/`. No rollback files were
deleted. The retirement note labels r14 as historical and links to the current
release. [Cleanup inventory](DAMAGE_NUMBERS_RELEASE_CLEANUP.md) records the paths.

The documentation-only rebuild retained the exact validated 152KiB NRO and
all 338 ARM results. The clean runtime-only ZIP also retains its previous hash;
checksums, CRC, inventory and member bytes pass. R16 remains ready to distribute
with notices beside the ZIP and the known Forge overlay issue documented.
The installed NRO now matches r16 on a fresh read, without proving activation
or new gameplay coverage. Cleanup wrote no installed files and changed no
Forge/Better Input settings or saves. No installation, launch or publication
was performed by this task.
