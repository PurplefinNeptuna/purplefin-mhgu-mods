# MHGU modding workspace

Start with README.md, docs/LOCAL_STATE.md, docs/DEVELOPMENT.md, docs/TOOLS.md
and docs/RESEARCH.md. Host: Linux; the user's interactive shell is fish.
MHGU Switch title ID is 0100770008DD8000, game 1.4.0. No automated in-game suite exists.

## Supported sources and scope

- Switch: **unmodified upstream Forge 1.5.1**, `tools/forge-local/`, commit
  `b23e114a23f41c9a8e2fd34b2f4df2a2102d0ee1`. Native ARM32 Hook is 24 bytes,
  Jit 28; use actual headers and compiler-derived ABI checks.
- Rust: forge-rs 1.5.0 at `tools/forge-rs/`, commit
  `d1865b68e9b194eb3eacc8bd71bbf601a5fac63e`; converter 1.4.1 is a separate tool.
- PC: **stock Forge PC 0.2.1**, `tools/forge-pc-local/`. All `<name>-pc` mods stay
  separate and default build/verify/package requires Linux SO and Windows DLL.
- Update existing checkouts directly from their official remotes. Do not create
  duplicate upstream folders/worktrees. Historical commits belong in Git.
  Retired loader/Better Input/renderer/mutex/PC support patches are not baselines.
- Preserve unrelated work, original dumps, library inputs and saves. Preparation
  authorizes no installation, activation, emulator launch/settings, save edit,
  publication or push. Commit validated coherent changes locally after checking
  staged paths; preserve custom hooks and run the full distribution check.

## Runtime evidence and installation paths

- Dump/RomFS: `~/.local/share/eden/dump/0100770008DD8000/`.
- Uninstalled library: `/mnt/storage2/ROM/Switch/cheats/mhgu/`.
- Eden packages: `~/.local/share/eden/load/0100770008DD8000/`;
  log: `~/.local/share/eden/log/eden_log.txt`.
- Ryujinx-Nextendo: `/mnt/storage2/Programs/Ryujinx-nextendo/portable/Logs/` and
  `portable/mods/contents/0100770008dd8000/` under that installation.
- GURecomp: `/mnt/storage/Games/GURecomp/`; exported game is
  `Game/MONSTER HUNTER GENERATIONS ULTIMATE/`. Read its `user/log/suyu_log.txt`,
  `user/recomp_report.txt` and `mods/0100770008DD8000/Forge/forge.log` after a run.

Folder presence proves no activation. Library contents are not installed mods.
Trust that the user does not co-activate alternative base/PC packages; inspect
co-activation only when fresh specific evidence implicates it, explaining that
first. After a reported run/failure, read that emulator's latest log and correlate
actual launch mods, version/build, hashes and exceptions before concluding.
Do not schedule monitoring unless requested. Separate source/build/package,
installation, activation, user acceptance and exhaustive runtime evidence.

GURecomp operational knowledge belongs here and in docs/GURECOMP.md. Use its
process-local `SDL3_DYNAMIC_API=/usr/lib/libSDL3.so.0` workaround for the verified
0.3.1-test menu failure before proposing a rebuild. Verify the current library
and fresh log on regression. Source-only export does not repair bundled SDL.

## Implementation and research

Use docs/DEVELOPMENT.md for standalone layouts, native APIs, settings and release
rules. Read applicable mod instructions. Source folders own their recipes,
tests, dependency snapshots, export allowlists, notices and licenses. No sibling
mod, personal path, installed emulator or parent history is a build dependency.
Keep mod-local commands authoritative; do not recreate obsolete root forwarders.

Search saved Ghidra/DTI before gameplay implementation:
`./scripts/tool.sh research find QUERY --kind functions` (or symbols/types/dti).
Exports: `work/research-tooling/ghidra-export/`; DTI: `work/research-tooling/dti/`.
Preserve the GZF, annotations and copied original executables. Imported base
is 0x009c9000; subtract it for Forge offsets. One changed text byte and conflicting
imported type layouts exist; verify bytes/layouts against the real target.
DTI inherited/repeated names need `vft_kind` filtering. Saved DTI covers 3152
classes/66752 properties; dumping broke quest controls until removal/restart.
Keep dumper/flag removed during play. New extraction needs separate runtime
scope, save backups, retained logs, package/flag removal and restart.

Use Forge facilities before writing private substitutes. Document verified API
gaps. Explain substantial functions, complex data flow, native offsets/registers,
units, thresholds, unsafe caller contracts, ownership/lifetimes, nested hooks,
TLS borrows and rollback beside the code. Preserve pinned assembly and third-party
bytes during comments-only work. Avoid comments that merely repeat code.
Never require APSR_g/APSR_nzcvqg writes; preserve NZCVQ and all live state. Audit
GE liveness at every hook/continuation and choose a different site if necessary.

Settings use a closed compact unframed tree under Plugin UI, paired TreePop and
stable IDs. No settings means no panel. Background callbacks continue with rows
closed. Diagnostics belong in brief lifetime-deduplicated logs outside hot hooks.
Use primary-only INIs, explicit saves and balanced counted mounts/handles;
never create/read/recover/delete `_backup` configs. Damage Numbers has the
explicit upstream forge-rs config/default-creation/ScopedMount/Writer exception.

Native GUI work starts at docs/RESEARCH.md and Key Quest Markers DEVELOPMENT.md.
Preserve native child ownership, 13-object maps and 168-byte draw caches. INIT_PARAM
kinds17/18 are immediate bool/u32; colour textures use Mask0. Counter title
binding4/ID6 is cGUIObjMessage (CRC 0x2fb82eae, 352 bytes), not cGUIObjText 384.
Derive fixture classes/getDTI from actual resources. Keep the accepted 32×32
original-emblem geometry and progression behavior during unrelated edits.

## Resources and distribution

Copy/hash dump/library inputs before editing; preserve unknown fields and
unrelated resources. ARC changes need supported MHGU tools, original repacking
baselines, re-extraction and content/inventory comparisons. Merge priority is
Base -> HD Project -> Z_Balanced -> others; unchanged resources preserve lower
improvements. Keep font/texture pairs and base companions; V4 donors are retired.
Ownership: docs/CLEANUP_HD_PROJECT.md. Choose one FPS/FOV variant and preserve
language/controller/icon selections. Stage `romfs/nativeNX/...`, `exefs/`, or
`cheats/<build-id>.txt` directly inside the package. Library identifiers
FB08F1D20FD1204F and FB08F1D20FD1204FE7070672777F869B do not verify a live build.

DISTRIBUTION.json is authoritative. Runtime changes get new versions. Follow
complete ZIP/support/notices/GameBanana rules in docs/DEVELOPMENT.md; package via
`scripts/mod_distribution.py package NAME` and run its full `check` before commits
or readiness claims. Preserve accepted artifacts in backups/accepted/; unique
research inputs stay in work/. Current guides are concise; dated machine evidence
retains original hashes/claims in owner EVIDENCE.json and WORKSPACE_EVIDENCE.json.
Recheck the live GameBanana policy before publication; never invent AI provenance.

Use .agents/skills/humanizer/SKILL.md for user-facing prose; keep technical names,
paths, hashes, code and validation claims exact. Toolbox/CLI: START_TOOLS.sh and
scripts/tool.sh. See docs/TOOLS.md for private runtimes, GMD limitations, Kuriimu2
path aliases and model-export limits. There is no verified general keyed-GMD
round trip or GLTF-to-MHGU exporter.
