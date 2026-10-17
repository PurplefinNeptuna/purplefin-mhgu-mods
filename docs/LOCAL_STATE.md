# Local state

Workspace baseline updated 2026-10-15: stock Switch Forge 1.5.1, forge-rs 1.5.0,
and stock Forge PC 0.2.1. This cleanup changes workspace sources and deliveries;
it does not inspect or change current emulator activation.

The workspace now uses `main`. Merged task branches, obsolete local source
forks and the old release worktree are removed. Historical commits remain
reachable through main or archive tags; the cleanup receipt records their tips.

## Deliveries and acceptance

Damage Numbers r29-diagnostics is a temporary DEVELOPMENT candidate for the
reported Switch/Android placement issue. The user reports r28 displays damage
on real Switch and a phone emulator, with correct-looking values and misplaced
positions. Exact tester loader/plugin hashes were not supplied. The diagnostic
build adds bounded copied camera/hit logs and screen markers without changing
camera admission, damage, animation or placement rules. It has no runtime
acceptance. r28 output remains intact, with record copies and delivery hashes in
`backups/accepted/damage-numbers/r28-before-projection-diagnostics/`.

On 2026-10-18, Key Quest Markers r18 and Damage Numbers r28 became DEVELOPMENT
hardware-test candidates. Both retain PIC and add `-nostartfiles` / `-Wl,-z,text`.
Their accepted r17/r27 releases and records are preserved under
`backups/accepted/NAME/VERSION-before-hardware-link/`; original candidate trees
remain intact. Gameplay and assets are unchanged apart from build identification.
At candidate creation, neither rebuild had a runtime test. The later r28
report is recorded above. The updated loader is not bundled or verified.
The r17/r27 acceptance statements below describe the prior builds.

DISTRIBUTION.json in each mod is authoritative. Damage Numbers r26 and Key Quest
Markers r15 replace the C++ Switch projects with fully renamed Rust implementations.
Modern Weapon Controls r12 and Please do Better r24-forge151 target stock Forge.
The user approved distribution of these maintenance builds after validation;
there is no new gameplay run. Earlier accepted payloads and their evidence remain
under backups/accepted/ and the per-mod EVIDENCE.json collections.

All four PC mods retain their accepted Linux/Windows payloads. Linux user
acceptance is scoped to the recorded binaries; Windows gameplay remains untested.
See README.md in each source folder for installation/use, DEVELOPMENT.md for
implementation/manual scenarios, and its distribution/runtime records for evidence.
Damage Numbers r27 is READY_TO_DISTRIBUTE after the user reported it working
well and approved promotion on 2026-10-15. The tested NRO and assets were promoted
unchanged. Current installed Eden hashes match that candidate. The original
third-party placement report remains unreproduced; individual fallback cases
and other platforms were not separately confirmed. The accepted r26 delivery
and tested r27 candidate remain under `backups/accepted/damage-numbers/`.

Key Quest Markers r17 is READY_TO_DISTRIBUTE following user-confirmed Eden/Linux
testing of the unchanged candidate. Other platforms remain unconfirmed. It uses
the game UI colours for the existing three saved colour controls. It preserves the original 32×32
emblem, Y3, X365/329 and title widths299/263. Defaults are green
#006305 for keys, red #A30000 for urgents and grey for completed/old
quests. Edits require Save & apply. The r15 release is
preserved under backups/accepted/key-quest-markers/r15-before-colours/. The game
owns native children and draw-cache/map allocations.
r17 also removes the old success/row ERROR diagnostics; startup is one INFO
line and genuine failures remain deduplicated. The user also confirmed it works
without the HD Project on 2026-10-15. HD is optional.

## Inputs and runtime paths

| Purpose | Path |
| --- | --- |
| Game dump/RomFS | `~/.local/share/eden/dump/0100770008DD8000/` |
| Uninstalled library | `/mnt/storage2/ROM/Switch/cheats/mhgu/` |
| Eden packages | `~/.local/share/eden/load/0100770008DD8000/` |
| Eden log | `~/.local/share/eden/log/eden_log.txt` |
| Ryujinx-Nextendo packages | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/mods/contents/0100770008dd8000/` |
| Ryujinx-Nextendo logs | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/Logs/` |
| Copied native inputs | `work/shared/game-exefs/` |
| Official Forge package/input | `work/shared/forge-1.5.1/` |
| Ghidra and saved DTI | `work/research-tooling/` |

The supplied dump is RomFS-only. Library target is game 1.4.0, cheat build
FB08F1D20FD1204F, NSO FB08F1D20FD1204FE7070672777F869B. Verify actual launch
version/build before executable work. Folder presence proves no activation.
Trust the user's alternative-mod activation choices; investigate overlap only
when fresh evidence implicates it. After a reported run, inspect that emulator's
latest log before concluding.

GURecomp installation/export paths, SDL3 override and native-port limits are in
[GURECOMP.md](GURECOMP.md). HD resource priorities are in
[CLEANUP_HD_PROJECT.md](CLEANUP_HD_PROJECT.md). DTI extraction is not enabled
for gameplay. There is no automated in-game suite.

## Evidence and recovery

[COMPACTION.json](WORKSPACE_EVIDENCE.json) records source revisions, archive/payload
hashes, removed paths, validation and space measurements.
[WORKSPACE_EVIDENCE.json](WORKSPACE_EVIDENCE.json) preserves dated workspace
research and original migration receipts. Historical installed hashes and
settings are dated evidence, not a statement about current activation.
The recovery tag is `cleanup/before-stock-forge-20261015`; Git history is intact.
