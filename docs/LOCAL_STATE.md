# Local baseline

## Current workspace: 2026-10-07

Great Luck plugin research is in
[GREAT_LUCK_FORGE_HANDOFF.md](GREAT_LUCK_FORGE_HANDOFF.md).
[Please do Better r12](../mods/please-do-better/README.md) is a local DEVELOPMENT
candidate correcting native scissor sentinel handling. R11's matching user
screenshot/log show ten bound extras, zero highlights and 16,653 captures rejected
at the clip check. R12 reproduces the original intersection/sentinel/viewport
substitution and retains bounded emulator logging, optional live forcing,
preferences and compact diagnostics. Visible alignment remains pending.
Prior candidates, installed packages and maintained Forge are preserved.
No installation, launch, real save/settings edit or publication is included.
Crafting/unlocks stay outside scope.

Eight maintained mods remain: damage-numbers r17, key-quest-markers r1 and
modern-weapon-controls r10 are READY_TO_DISTRIBUTE; forge-patched, hd-project,
wiki-cheats and dti-dumper-support are LOCAL_ONLY; please-do-better is DEVELOPMENT. Each current
`mods/<name>/DISTRIBUTION.json` is authoritative.

Eden uses adapter-enabled `forge-patched` and base Better Input. The user has
played damage numbers r17 on Eden and Ryujinx. Current evidence is in
[the Forge source/runtime record](FORGE_LOCAL_BRANCH.md) and the mods' runtime
records. Cleanup removes retired workspace trees and preserves current release
payloads. It performs no installation or emulator change.

The inventories and observations below are historical dated snapshots.
Paths in historical snapshots may describe packages outside this workspace or
artifacts subsequently removed. They do not describe current status or activation.

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

## 2026-10-06 damage numbers r17 NZCVQ compatibility candidate

R17 applies the eight-site GE-liveness audit by replacing all nine gateway
`msr APSR_nzcvqg, r2` instructions with `msr APSR_nzcvq, r2`. This removes
the plugin's unsupported `APSR_g` write on the inspected unmodified Ryujinx
translator. GE is left as set by helpers; the audited continuations do not
consume it. NZCVQ, integer/VFP registers, FPSCR, stack arguments and return
state retain their preservation contract. New hooks require a new audit.

Fresh gateway checks passed 9,287 checks across 2,025 calls, including all
16 GE patterns with preserving and clobbering helpers. The production capture
suite passed 347 checks. Host, settings, asset and real-ImGui checks passed.
Binary comparison proves exactly nine executable instruction changes against
r16, with other executable bytes, initialized data, imports, BSS and segment
sizes unchanged. Font, effects and rendered output retain r16's appearance.

Clean package: `build/damage-numbers/releases/r17/damage-numbers-r17.zip`.
It contains only `damage-number/romfs/nativeNX/plugins/damage_numbers_capture.nro`;
notices, README, checksums and provenance remain beside the ZIP. Reopening,
checksums and deterministic repeated packaging passed. NRO: 155,648 bytes
(152KiB), SHA-256
`1eb78f3430f6c5c5ce1f60a382fa8bd4fc18ee56cf267649b95a94a462115ea4`.
ZIP SHA-256:
`5d6165f8b8b40c4de0e3eafb71cefb5de9a713317b68542b37a5484dbd638fe8`.

Status at preparation: validated compatibility candidate, with gameplay
confirmation then pending. The subsequent runtime-confirmation section below
records the user-confirmed r17 gameplay on both emulators.
The brief restart/quest/return check is in
`mods/damage-numbers/RYUJINX_COMPATIBILITY.md`. Installed Eden and Ryujinx
plugins still match r16 on fresh reads. R16 artifacts are preserved in
`backups/damage-numbers/r16-before-r17-ge-20261006/` and its release directory.
No installed package, emulator, cache, setting or save was changed. The separate
Forge menu/popups rendering handoff remains open.

## 2026-10-06 damage numbers r17 runtime confirmation

The user confirmed r17 working on both Eden and Ryujinx-based emulators.
Fresh installed-file hashes in both locations match the released r17 NRO.
The latest logs were reviewed and copied with hashes under
`backups/damage-numbers/r17-runtime-confirmation-20261006/`. They identify
MHGU 1.4.0/main build `FB08F1D20FD1204FE7070672777F869B` and contain no
`APSR_g` failure. Eden logs plugin/capture/ImGui startup; Ryujinx logs the
enabled `damage-number` and original `forge`/`better-inputs` packages.
Detailed launch sets and separate emulator diagnostics remain in
`mods/damage-numbers/RUNTIME.md`; clean shutdown and every fork are not claimed.

The authoritative `DISTRIBUTION.json` remains `READY_TO_DISTRIBUTE`, now with
fresh user-confirmed gameplay evidence for both emulators. Release metadata
and adjacent support files are refreshed with a verified prior-delivery backup.
The r17 NRO and clean ZIP bytes are unchanged. No installed package, emulator,
setting or save was modified; nothing was launched or published.

## 2026-10-06: initial distribution marking (historical)

The user directed that all three mods be marked `READY_TO_DISTRIBUTE`:

- Modern weapon controls r10: `build/modern-weapon-controls/releases/r10/`.
- Key Quest Markers r1: `build/key-quest-markers/key-quest-markers-r1.zip`.
- Damage Numbers r17: `build/damage-numbers/releases/r17/`.

These are local packages; none was published by this update. The earlier
r17 candidate status above is historical. Runtime payloads and recorded test
results are preserved. R17 gameplay is confirmed on both emulators in the
runtime-confirmation record above; the distribution-label update itself did
not run another gameplay test.
The quest marker ZIP loses its experimental filename without changing its
bytes. Prior package metadata is preserved under
`backups/distribution-status-20261006/`.


## 2026-10-06: enforced distribution standard

The authoritative record is now `mods/<mod>/DISTRIBUTION.json` for all 15 mods.
The shared packager and full workspace checker enforce
[DISTRIBUTION_STANDARD.md](DISTRIBUTION_STANDARD.md). Controls r10, quest markers
r1 and damage numbers r17 retain distribution approval and recorded coverage.
Quest markers now delivers under `build/key-quest-markers/releases/r1/` with
one named `key-quest-markers/` runtime folder inside its ZIP. The NRO is unchanged.
Only current registered deliveries remain under active `releases/` directories;
r16 and the old layouts/metadata are preserved with hashes under
`backups/distribution-standard-20261006/`. The earlier flat quest ZIP path is
historical. The local pre-commit check is installed. No runtime, emulator, save,
installation or publication change is part of this standardization.


## 2026-10-06: component retirement correction

Per user instruction, the separate patched Better Input, controls UI, Long Sword
prototype and Ryujinx APSR GE repair are retired. The original Better Input
adapter entry is also retired as a standalone mod because its implementation
is incorporated into current Eden `forge-patched`. Its source/tests/replay patch
remain maintained. The UI recipe and Long Sword parsers/scaffolding remain
shared build dependencies of modern weapon controls r10.

Fresh Eden fingerprints match the adapter-enabled Forge and base Better Input;
the latest Eden log confirms in-memory adaptation. Current fingerprints and
historical source-baseline distinctions are in
[the adapter record](FORGE_LOCAL_BRANCH.md). Ryujinx's listed old
patched packages are not changed or treated as active by this correction.

Future plugins must avoid requiring APSR_g, with GE-liveness/state-preservation
review required at new hook sites. This retires the emulator patch without
assuming the old eight-site GE audit applies to new hooks. No source component,
rollback record, installed package, emulator or save is removed or changed.
