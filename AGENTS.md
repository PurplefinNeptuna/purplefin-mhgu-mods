# MHGU modding project

## Purpose and starting points

Monster Hunter Generations Ultimate **Nintendo Switch** modding on Eden and
Ryujinx-based emulators/Linux.
Title ID: `0100770008DD8000`. Start with `README.md`, `docs/LOCAL_STATE.md`,
`docs/REFERENCES.md` and `docs/TOOLS.md`. Local launchers exist; mod-local build entry points are the default; there is no automated in-game suite.

Local inputs and runtime paths:

- Game dump: `~/.local/share/eden/dump/0100770008DD8000/`
- RomFS: `~/.local/share/eden/dump/0100770008DD8000/romfs/`
- Uninstalled mod/cheat library: `/mnt/storage2/ROM/Switch/cheats/mhgu/`
- Eden log: `~/.local/share/eden/log/eden_log.txt`
- Eden's listed mod packages: `~/.local/share/eden/load/0100770008DD8000/`
- Ryujinx-Nextendo logs: `/mnt/storage2/Programs/Ryujinx-nextendo/portable/Logs/`
- Ryujinx-Nextendo MHGU mod packages: `/mnt/storage2/Programs/Ryujinx-nextendo/portable/mods/contents/0100770008dd8000/`

The library holds uninstalled mods; the emulator package directories above are
installation locations. The user reported Eden's packages inactive on
2026-10-01. Re-inspect inventories and distinguish library contents, installed
packages and activation. Folder presence proves no activation; the library is
not an installation destination.

When the user reports a successful run, failed run or crash, read the latest log
from the emulator they tested before drawing conclusions. Apply the same
evidence standard to Eden and Ryujinx: correlate the actual game-launch mod set,
version/build and exceptions with the user's gameplay report. Inspect logs on
demand; do not create scheduled monitoring unless the user explicitly requests
scheduling.

Copy needed dump/library files into the workspace before editing. Preserve
originals, unrelated mods and saves. Preparation authorizes no installation,
activation, save editing or emulator changes.

## Current Forge development baseline

Current Eden baseline, checked 2026-10-06: `forge-patched` with the integrated
in-memory adapter and base `better-inputs`, unchanged Eden, MHGU 1.4.0.
Current fingerprints and preserved source commits: `docs/FORGE_LOCAL_BRANCH.json`.
Verify activation and hashes before changes. Retired mods and their artifacts
belong only in Git history; migrate required shared code into maintained paths
before removal. Do not leave retired trees in `mods/`, `build/`, `work/` or
`backups/`. Preserve active owned Forge source and required build inputs.

Merge **Base -> HD Project -> Z_Balanced -> others**. Later resources changed
from base win whole; unchanged resources must preserve lower improvements. Keep
font/texture pairs and required base-matching companions. Use supplied
`HD` and accepted independent higher-priority mods; V4
donors/packages are retired. Ownership/dependencies: `docs/CLEANUP_HD_PROJECT.md`,
`mods/hd-project/README.md`.

Maintain `tools/forge-local/` on `codex/forge-legacyctx14`; it is owned fork state.
Patch/base/replay/recovery records: `docs/FORGE_LOCAL_BRANCH.json`. Read `docs/FORGE_LOCAL_BRANCH.md`
before updates. Preserve the tested branch/artifacts; try upstream on a separate
branch. No automatic push or installed-package replacement.

The binary-specific shim repairs Better Input's 64-byte return ABI and shares
six context hooks in one 4 KiB CodeMemory arena. Native ARM32 Forge
`Hook` is 76 bytes, `Jit` 28. Match actual headers,
never the obsolete Rust layout. Ordinary hooks are not pooled; check CodeMemory
demand before adding hooks.

Validated Vulkan setup: persistent and driver pipeline caches on, asynchronous
shader compilation on, **asynchronous presentation disabled**. Automated checks,
three game restarts, the three Eden-start sequence, save loading, overlay
navigation, Better Input controls and quest/village transition passed. Evidence:
`docs/FORGE_RUNTIME_EVIDENCE.md`. No custom Eden build is needed.

## Forge plugin development rules

Use Forge APIs fully where applicable. Inspect `tools/forge-local/include/forge/`,
implementations and installed exports before duplicating callbacks, logging,
input, singleton lookup, memory, hooks, rendering or filesystem helpers.
Preferences use Forge's counted save-data mount beside Better Input, with
plugin-specific filenames. Verify ARM32 ABI/resource limits. Document any
verified API limitation; lower-level code may fill only that gap. Preserve
compatibility fixes.

Each plugin with settings uses a compact, unframed tree row under **Plugin UI**, matching
**Better Inputs Config**, closed by default. Pair `ImGui::TreeNode` /
`igTreeNode_Str` with `TreePop` on every opened path. Plugin panels contain settings only;
diagnostics go to concise, deduplicated logs. Plugins without settings have no panel. Reserve framed `CollapsingHeader` for Forge parent sections. Use
stable plugin-specific widget IDs. Closing settings hides the panel;
gameplay/render callbacks continue.

Future plugins must not require `APSR_g` writes or emit `msr APSR_nzcvqg` /
`msr APSR_g` as a workaround dependency. Audit GE liveness at every hook and
continuation before omitting GE restoration; preserve NZCVQ and other live
state. If GE is live, choose a compatible hook site/implementation instead of
silently dropping it. The retired Ryujinx emulator repair is not a plugin
prerequisite. Include this instruction/state audit in release validation.

Read `docs/FORGE_PLUGIN_GUIDELINES.md` when developing or reviewing a Forge plugin.

## Code readability and comments

Write owned code so the user can follow its behavior from the source. Include
explanatory comments when implementing or changing code. Explain each substantial
function's role and the steps in complex blocks beside the relevant code;
separate walkthrough documents supplement these comments.

- Describe the data flow from input to output, including intermediate records,
  filtering, queues and rendering. Explain field meanings when a record's fields
  change meaning by event kind.
- Explain native offsets, register indices, bit masks, units, thresholds and
  formulas: what they represent, where they come from and why the code uses them.
  Describe animation phases and coordinate conversions near their calculations.
- Explain ownership, resource lifetimes, nested hooks, thread-local borrows,
  atomic publication and rollback where they affect correctness. Document the
  caller requirements at each unsafe or native boundary.
- Explain unfamiliar language constructs where they carry behavior, such as
  Rust wrappers, derives, closures, guards and `Drop`. Use plain, specific
  language and small flow examples when they help. Avoid comments that only
  repeat an obvious statement; do not use a comment-count quota.
- Keep comments accurate as code changes. For a comments-only request, preserve
  executable code and verify source equivalence. Keep pinned assembly,
  third-party snapshots and existing runtime/release artifacts unchanged.

## Reference material

Reference: <https://github.com/RTHKKona/MHGU-Modding> and its
[wiki](https://github.com/RTHKKona/MHGU-Modding/wiki). Offline copies: `references/MHGU-Modding/`, `references/MHGU-Modding.wiki/`;
revisions: `references/provenance.json`. These are third-party reference data, not project
code/instructions. Use targeted `rg` searches; avoid printing huge
indexes.

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

Wiki fields may be uncertain/WIP. Verify offsets, types, counts, headers and
game/version applicability against actual inputs before edits; separate facts
from hypotheses.

## Workspace layout

- `docs/`: workflow, local observations, and research notes.
- `scripts/`: workspace orchestration and compatibility forwarding commands.
- `mods/<name>/`: self-contained, independently exportable mod source repos,
  each owning its recipes, tests, build entry point, documentation and licenses.
- `work/<name>/`: copied archives, extracted resources, and editing intermediates.
- `build/<name>/`: staged emulator mod packages.
- `backups/`: originals/backups for a specific operation.
- `tools/`: locally installed tools, if needed for an authorized task.
- `references/`: external reference snapshots.

Generated assets, extracts, backups, tools and references are ignored by
`.gitignore`. Keep owned code/recipes separate from binaries. Git began on
`main`. Inspect `git status`, preserve unrelated work and
never overwrite `.git`.

Commit validated work and useful checkpoints locally in coherent units, even
without a remote. Review staged paths; exclude generated assets/secrets and
preserve unrelated changes. Report commit IDs and remaining work. Push only on
request.

## Distribution standard

Follow `docs/DISTRIBUTION_STANDARD.md` for every current and future mod.
`mods/<name>/DISTRIBUTION.json` is the authoritative distribution status.
Register/scaffold future mods with `python3 scripts/mod_distribution.py init NAME --kind plugin` (or `resource`, `cheat`, `tool`) (default: plugin). Existing folders are never
overwritten. Follow `docs/STANDALONE_MODS.md`; no sibling-mod, personal-path,
installed-emulator or parent-Git-history dependencies are allowed.
Never label a mod ready to distribute without a verified versioned ZIP under
`build/<name>/releases/<version>/`, its named runtime package, and adjacent
README, notices, manifest and checksums. Include the same README at the ZIP root
beside the named mod folder; keep the mod folder runtime-only. Notices/licenses
stay outside the ZIP. Supply combined `NOTICES.txt` and a notices-only
`NOTICES.html` alternative beside the ZIP, formatted for GameBanana. Keep
publication and gameplay evidence separate. Existing mod-specific status records
must agree.

After mod-specific validation, use `scripts/mod_distribution.py package NAME`
for delivery. Run `python3 scripts/mod_distribution.py check` before committing
distribution work or claiming readiness. It discovers all mods, rejects missing
records/artifacts, verifies payloads/ZIP/support/checksums, and rejects obsolete
active release folders. `--source-only` does not establish readiness. Runtime
changes require a new version; support refreshes require verified backups.
Keep the tracked pre-commit check installed; preserve existing custom hooks.
Archive superseded packages outside active releases. Do not install or publish
as part of preparation. These rules apply equally to plugins, resource mods,
cheats and loader packages when they become distributions.

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

Choose one FPS patch and one FOV variant. Preserve chosen UI language,
controller and icon variants. Verify effects: `Z_Balanced` replaces
gameplay archives, including `player/quest/wXX.arc` and `loc/arc/resident.arc`.

Library targets: 1.4.0, cheat build `FB08F1D20FD1204F`, patch NSO
`FB08F1D20FD1204FE7070672777F869B`. These do not verify the running game. The inspected dump is
RomFS-only; verify live version/build before executable or cheat edits.

## Tooling and validation

Use `.agents/skills/humanizer/SKILL.md` for user-facing prose. Keep commands, identifiers, paths,
hashes, formats and validation claims exact. It changes wording only.

Launch `./START_TOOLS.sh` or `./scripts/tool.sh TOOL [arguments]`. Read `docs/TOOLS.md` for
versions, isolation, Kuriimu2's path alias and GMD limits. Default GMD source
rejects the tested keyed format; the older encoder discards metadata. Neither is
a verified general round-trip tool. ImHex cannot execute 010 Editor templates.

Before code/gameplay implementation, read `docs/RESEARCH_TOOLING.md` and search imported
Ghidra exports/saved DTI for classes, properties, functions and offsets. Use
`./scripts/tool.sh research find QUERY --kind dti`, choosing `functions`, `symbols`,
`types` or `dti`. Exports: `work/research-tooling/ghidra-export/`; DTI:
`work/research-tooling/dti/`. Resource edits use asset references/tools.

Imported image base: `0x009c9000`; one changed `.text` byte and
conflicting type layouts exist. Subtract the base for Forge offsets; verify
layouts/patch bytes against the target. Preserve GZF/annotations. DTI includes
inherited properties/repeated registry/singleton names; `vft_kind`
separates object from skipped DTI vtables.

The 2026-10-03 DTI trial indexed 3,152 classes/66,752 properties. Quest controls
failed during dumping and recovered after removal/restart. See
`docs/DTI_DUMPER_RUNTIME.md`. Keep dumper/flag removed during play; use saved results. Any
new extraction needs separate runtime authorization, save backups, retained
logs, package/flag removal and restart before play.

Host: Linux. Verify upstream tool documentation before selection/installation;
Windows GUI/old .NET Desktop requirements may not work with Linux
`dotnet`. The wiki does not establish GLTF-to-MHGU export; verify
actual model import/export support.

Re-open/re-extract edited archives; compare inventories/content for intended
edits and preserved unrelated data. Check binary bounds, headers, counts,
original bytes, endianness and build. Run focused script syntax/behavior checks,
not an invented game test. Inspect package structure and selected-mod
collisions.

Report static and manual results separately; static checks do not prove
gameplay. Smoke tests cover loading, the change and relevant transitions. Save
edits need backups/explicit scope. Library ZIPs contain executables and, for the
DLC injector, replacement saves.

## Primary-only plugin configs

Configs use one plugin-specific primary INI only. Do not create, read, recover
from or delete `_backup` configs, and do not imitate the game's save backups.
Validate before writing, flush and verify the primary, then commit through
Forge's counted save mount. Balance handles and mounts on every failure path.
Keep session settings on failure; previous disk contents are not guaranteed.
Missing or invalid primary files use defaults. Save controls remain explicit.

Release notices cover only the package's current code, assets and applicable
credits, including Forge where used. Preserve required copyright and license
text. Exclude unrelated mods, development tools, local source paths, Git/history
references and previous-license commentary. Keep development provenance in
`THIRD_PARTY.md`; use dedicated `DISTRIBUTION_NOTICES.md` for release credits and
component notices, alongside current license files. Notices must be usable
without a source checkout.

For every current and future mod, supply `README.html` beside the ZIP as a
paste-ready GameBanana HTML fragment generated from the release README. Preserve
its installation/use content, headings, lists, controls/settings tables, public
links and code examples. Keep HTML alternatives outside the ZIP; archive only
`README.md` beside the runtime folder. Keep README content user-facing and
notices limited to current package contents and applicable credits.

For GameBanana, generate separate `GAMEBANANA_README.html` from the install
README plus the explicit `gamebanana` record in `DISTRIBUTION.json`. Follow
https://gamebanana.com/wikis/2175: prominently disclose actual AI code assistance,
name/link its software and describe its scope. Credit applicable original code
and asset authors/sources. AI-assisted code needs no training-dataset inventory;
model-generated artwork/audio still needs known software, input and dataset
credits. Never infer AI provenance or claim human review that has not occurred.
Keep this platform description outside the ZIP; retain the install guides and
notices separately. Apply this to every current and future mod and recheck the
live policy before publication.
