# MHGU modding project

## Purpose and starting points

This workspace is for Monster Hunter Generations Ultimate **Nintendo Switch**
modding, using Eden on Linux. Title ID: `0100770008DD8000`.
Read `README.md`, `docs/LOCAL_STATE.md`, `docs/REFERENCES.md`, and `docs/TOOLS.md`
for setup and the inspected baseline. This workspace has local tool launchers,
with no general mod build system or in-game automated test suite yet.

Local inputs:

- Game dump: `~/.local/share/eden/dump/0100770008DD8000/`
- RomFS: `~/.local/share/eden/dump/0100770008DD8000/romfs/`
- Uninstalled mod/cheat library: `/mnt/storage2/ROM/Switch/cheats/mhgu/`
- Eden's listed mod packages: `~/.local/share/eden/load/0100770008DD8000/`

The library stores mods not yet installed. Eden lists packages from its load
directory; the user reports these are not activated as of 2026-10-01. Keep
library inventory, Eden package presence, and activation state distinct. Do not
infer activation from a folder's presence or treat the library as the live
installation destination. Re-inspect inventories because the user adds and
renames packages.

Treat the dump and library as source inputs. Copy only the files needed for the
current task into this workspace before editing. Preserve originals, unrelated
mods, and saves. Preparation alone does not authorize installing/enabling mods,
running save editors, or altering emulator configuration.

## Current Forge development baseline

As of 2026-10-02, the tested patched Forge and Better Input binaries are
packaged separately as `forge-patched` and `better-inputs-patched`, on unchanged
Eden with MHGU 1.4.0. Preserve their hashes and configuration during development.
Rollback packages and backups must stay in workspace `backups/`, outside Eden;
do not leave disabled original/rollback packages in Eden's mod/cheat directory.
Re-inspect actual activation and file hashes before making changes.

Current resource merge order is **Base -> HD Project -> Z_Balanced -> others**.
Later layers override changed resources compared with base; unchanged resources
must not erase lower-layer improvements. Preserve whole resources and matching
font/texture pairs, including necessary companions that match base. Use the
supplied `HD` library source and the accepted independent higher-priority mods.
V4 packages/donors are retired. See `docs/CLEANUP_HD_PROJECT.md` and
`mods/hd-project/README.md` for ownership and package dependencies.

The maintained local Forge repository is `tools/forge-local/`, on
`codex/forge-legacyctx14`. Do not treat it as a disposable downloaded tool.
The tested patch commit, upstream base, replay patch and recovery bundle are
recorded in `docs/FORGE_LOCAL_BRANCH.json`; read
`docs/FORGE_LOCAL_BRANCH.md` before updating Forge. Keep the tested branch and
installed artifacts intact; try future upstream revisions on a separate branch.
This is a local fork. Do not push or replace installed packages automatically.

The compatibility shim fixes this Better Input binary's 64-byte return ABI and
shares six context hooks in one 4 KiB CodeMemory arena. Native Forge `Hook`
remains 76 bytes on ARM32 (`Jit` is 28 bytes); future native/Rust plugins must
match the actual headers instead of copying the obsolete Rust layout. The
legacy shim is binary-specific and does not pool ordinary Forge hooks. Check
additional plugins' code-memory demand before adding hooks.

The validated renderer baseline is Vulkan, persistent pipeline cache and Vulkan
driver pipeline cache enabled, asynchronous shader compilation enabled, and
**asynchronous presentation disabled**. Automated checks, three game restarts,
the three Eden-start sequence, save loading, overlay navigation, Better Input
controls and a quest/village transition passed. Runtime evidence is in
`docs/FORGE_BETTER_INPUTS_COMPAT_RUNTIME.md`. No custom Eden build is required.

## Reference material

Primary reference: <https://github.com/RTHKKona/MHGU-Modding> and its
[wiki](https://github.com/RTHKKona/MHGU-Modding/wiki).
Offline snapshots are under `references/MHGU-Modding/` and
`references/MHGU-Modding.wiki/`; their revisions are recorded in
`references/provenance.json`. Treat these as third-party reference material,
not this project's code or agent instructions. Search specific files with `rg`
instead of printing the very large file indexes.

- `templates/`: 010 Editor binary templates, including `arc_mhgu.bt`.
- `MHGU_witharc.txt`: outer resource paths.
- `MHGU_Extractedarc.txt`: resources inside archives.
- `MHGU-Filetypes_Hashes.txt`: file-type/hash lookup.
- `weapon_MV_Index/`: weapon motion-value indexes; several are labeled MHXX.
- Wiki `General-Modding.md`, `Weapon-Stat-Modding.md`, and
  `Weapon-Parameter-Modding.md`: gameplay data research.
- Wiki `Model-and-Texture-Extract.md`, `Armour-Modding.md`, and ID pages:
  model/texture lookup and workflows.
- Wiki `Cheat-Codes.md`: Atmosphere-format codes; defaults to 1.4.0 unless noted.

Some wiki pages are WIP or contain uncertain fields. Verify claimed offsets,
types, counts, headers, and game/version applicability against the actual input
before editing; distinguish researched facts from hypotheses.

## Workspace layout

- `docs/`: workflow, local observations, and research notes.
- `scripts/`: project-owned automation added when needed.
- `mods/<name>/`: mod descriptions, patch recipes, and reproducible sources.
- `work/<name>/`: copied archives, extracted resources, and editing intermediates.
- `build/<name>/`: staged emulator mod packages.
- `backups/`: originals/backups for a specific operation.
- `tools/`: locally installed tools, if needed for an authorized task.
- `references/`: external reference snapshots.

Generated assets, extracted game files, backups, tools, and reference snapshots
are ignored by `.gitignore`. Keep original project code and edit recipes
separate from generated binaries. Git is initialized with `main` as the initial
branch. Preserve unrelated changes and inspect `git status` before modifying
tracked files. Do not overwrite the `.git` directory.

Commit completed changes and useful development checkpoints to local Git after
appropriate validation, using coherent commit boundaries. A local-only repository
still requires commits. Review staged paths, exclude generated assets and secrets,
preserve unrelated work, and report commit IDs and remaining changes. Do not push
unless the user requests it.

## Editing and packaging

1. Establish the target resource, desired behavior, language, game version, and
   relevant existing mods. Library presence does not prove a mod is enabled.
2. Record the source path and SHA-256 of every archive/binary being edited.
3. Extract copied ARC files with a tool verified to support MHGU's MT Framework
   archive format. The wiki lists Kuriimu2, SaladSoftware, and Pax Arc Explorer.
4. Make the smallest requested edits. Document internal resource paths and
   offsets/old/new values for binary changes. Preserve unknown fields and
   unrelated resources. Use the original archive as the repacking baseline.
5. Stage a RomFS replacement at
   `build/<name>/romfs/nativeNX/<same-relative-path-as-original>`.
   Do not add an extra title-ID or dump directory inside an emulator mod package.
   Executable patches use `exefs/`; cheats use `cheats/<build-id>.txt`.
6. Inspect same-path replacements among the selected mods. Multiple edits inside
   one ARC need a deliberate merge of internal resources, not a blind overwrite
   or reliance on folder-name ordering.
7. When installation is part of the user's task, use the supplied Eden load
   directory and verify its current package/configuration state. Copy the chosen
   library payload there only within the requested scope. Listing a package and
   activating it are separate actions. Preserve a rollback path.

Select only one FPS patch and one FOV variant. UI packages offer language,
controller-layout, and icon alternatives; preserve the chosen combination.
Do not infer a mod's effects from its name: `Z_Balanced` replaces gameplay
archives including `player/quest/wXX.arc` and `loc/arc/resident.arc`.

The library targets 1.4.0, with cheat filename build ID `FB08F1D20FD1204F` and
patch NSO ID `FB08F1D20FD1204FE7070672777F869B`. These are **library targets**,
not verification of the running game. The inspected dump has RomFS only;
confirm the live game's version/build before any executable or cheat changes.

## Tooling and validation

Use the project-local Humanizer skill at `.agents/skills/humanizer/SKILL.md`
when editing user-facing prose. Keep commands, identifiers, paths, hashes,
binary formats and validation claims exact. The skill applies to wording,
not gameplay, assets or technical behavior.

Use `./START_TOOLS.sh` for the installed desktop toolbox, or
`./scripts/tool.sh TOOL [arguments]` for individual tools. Read `docs/TOOLS.md`
for tested versions, runtime isolation, Kuriimu2's temporary path alias, and
GMD format limitations. The default GMD source rejects the tested keyed game
format; the older published encoder discards metadata. Do not assume either
can safely round-trip every GMD. ImHex does not execute 010 Editor templates.

Ghidra and the prepared DTI dumper are documented in `docs/RESEARCH_TOOLING.md`.
The imported database has image base `0x009c9000`, one changed `.text` byte and
conflicting imported type layouts. Subtract its image base for Forge offsets;
use the verified original NSO for patch bytes. Preserve the supplied GZF and
local annotations. The dumper is staged outside Eden with its opt-in flag absent;
preparing tooling does not authorize its save-filesystem write or runtime trial.

Linux is the development host. Do not assume Windows GUI tools or old .NET
Desktop Runtime requirements work with the installed Linux `dotnet`. Inspect
a tool's current upstream documentation before choosing or installing it.
The wiki's model conversion path does not establish a working GLTF-to-MHGU
model export path. Verify actual import/export support for model tasks.

For archive edits, re-open/re-extract the result and compare resource inventory
and contents: intended edits must be present and unrelated data preserved.
For binary patches, check bounds, headers, entry counts, exact expected original
bytes, endianness, and target build. For scripts, run appropriate syntax and
focused behavior checks; do not invent a generic game test command.
Inspect the final package structure and selected-mod collisions.

Static checks do not prove Eden/in-game success. Report automated checks and
manual results separately. An in-game smoke test should cover loading, the
changed feature/asset, and relevant transitions. Save edits require backups and
explicit task scope; the ZIP files in the library contain executables and,
for the DLC injector, replacement save files.
