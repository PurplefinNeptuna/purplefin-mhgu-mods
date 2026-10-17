# Original workspace and coverage index

This appendix describes `/mnt/storage2/Programs/MHGU_Modding` on 2026-10-17. Paths and installed state can drift. All other source pointers in this skill are relative to that root. Outside this workspace, provide equivalent source/private inputs explicitly. The skill's Markdown remains usable without them.

## Machine-specific paths

| Purpose | Path |
| --- | --- |
| RomFS dump | `~/.local/share/eden/dump/0100770008DD8000/` |
| Uninstalled mod/input library | `/mnt/storage2/ROM/Switch/cheats/mhgu/` |
| Eden packages | `~/.local/share/eden/load/0100770008DD8000/` |
| Latest Eden log | `~/.local/share/eden/log/eden_log.txt` |
| Ryujinx packages | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/mods/contents/0100770008dd8000/` |
| Ryujinx logs | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/Logs/` |

The supplied dump is RomFS-only. Original main/SDK/loader inputs must come from verified copied executable material. Historical installed hashes in docs are dated evidence. Do not infer today's enabled packages from these paths. The user's interactive shell is fish; shell examples avoid Bash-only variable syntax.

## Coverage and source authority

| Topic / skill reference | Workspace sources and evidence |
| --- | --- |
| API, ABI, lifecycle, build | `tools/forge-local/`, `tools/forge-rs/`, `references/provenance.json`; mod dependency locks, `src/lib.rs`, ABI records, mod-local `scripts/verify.py` |
| Hook pool / state / rollback | Forge `source/forge/hook.c`; Damage Numbers hook/gateway/mailbox source and tests; Key Quest Markers hooks/offers/ARM fixture; Modern Controls and Please do Better transaction/platform source |
| Native GUI extension | `mods/key-quest-markers/DEVELOPMENT.md`, `src/gui.rs`, `src/native.rs`, `mods/key-quest-markers/scripts/gui_layout.py`, `tests/native_adapter.py`, `research/theme-colours.json` |
| Rendering / storage | Damage Numbers `src/render.rs`, `src/config.rs`, runtime/context tests; Key Quest Markers settings/config; Please do Better settings/preferences and overlay gates |
| Validation / delivery | `docs/DEVELOPMENT.md`, per-mod `DISTRIBUTION.json`, `EXPORT.json`, release manifests, `EVIDENCE.json`, `scripts/mod_distribution.py` |
| Diagnostics / historical causes | `docs/RESEARCH.md`, `docs/WORKSPACE_EVIDENCE.json`, each mod's `EVIDENCE.json` and development history; current loader/libnx source for physical feasibility |

Core workspace reading: `AGENTS.md`, `README.md`, `docs/LOCAL_STATE.md`, `docs/DEVELOPMENT.md`, `docs/TOOLS.md`, `docs/RESEARCH.md`. Current source and exact artifact receipts resolve stale narrative claims. Preserve dated evidence instead of rewriting its historical assertions.

Useful evidence locations: `work/shared/game-exefs/`, `work/shared/forge-1.5.1/`, `work/research-tooling/`, per-mod `work/NAME/`, `build/NAME/candidates/`, `build/NAME/releases/`, and `backups/accepted/`. Ignored/private material may be absent from another checkout. Old references such as `docs/FORGE_LOCAL_BRANCH.json` or retired research guides in historical narratives are not current baseline instructions; consult consolidated docs/evidence and Git history.

## Source and acceptance snapshot

Forge 1.5.1 commit `b23e114a23f41c9a8e2fd34b2f4df2a2102d0ee1`; forge-rs 1.5.0 commit `d1865b68e9b194eb3eacc8bd71bbf601a5fac63e`. Native offsets target main SHA-256 `b3935415499549adaf4c0e89822831daa175cfd456a7990791c79be3997645ef`, build `FB08F1D20FD1204FE7070672777F869B`.

| Maintained Switch mod | Snapshot / evidence boundary |
| --- | --- |
| Damage Numbers | r27, accepted Eden/Linux 2026-10-15, unchanged candidate promotion; original third-party placement report unreproduced |
| Key Quest Markers | r17, accepted Eden/Linux 2026-10-15 with and without optional HD; individual state/settings cases not separately enumerated |
| Modern Weapon Controls | r12 stock-loader maintenance, earlier r10 acceptance retained at its exact-byte scope |
| Please do Better | r24-forge151 maintenance; earlier reward-page/overlay evidence retains its own runtime limits |

`EVIDENCE.json.current` and `DISTRIBUTION.json` hold exact versions/hashes/status. Some mod development paragraphs describe preserved older releases. Do not turn this snapshot into a statement about the latest upstream or installed payload.
