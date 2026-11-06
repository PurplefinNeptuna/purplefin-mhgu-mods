# Original workspace and coverage index

This appendix describes `/mnt/storage2/Programs/MHGU_Modding` on 2026-10-20. Paths and installed state can drift. All other source pointers in this skill are relative to that root. Outside this workspace, provide equivalent source/private inputs explicitly. The skill's Markdown remains usable without them.

## Machine-specific paths

| Purpose | Path |
| --- | --- |
| RomFS | `/mnt/storage2/Programs/MHGURecomp/data/romfs/` (MHGURecomp's copy; the Eden dump keeps only `exefs` and `nso`) |
| Uninstalled mod/input library | `/mnt/storage2/ROM/Switch/cheats/mhgu/` |
| Eden packages | `~/.local/share/eden/load/0100770008DD8000/` |
| Latest Eden log | `~/.local/share/eden/log/eden_log.txt` |
| Ryujinx packages | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/mods/contents/0100770008dd8000/` |
| Ryujinx logs | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/Logs/` |

What each input holds and when to use it: the Game data section of this skill's SKILL.md.

The supplied dump is RomFS-only. Original main/SDK/loader inputs must come from verified copied executable material. Historical installed hashes in docs are dated evidence. Do not infer today's enabled packages from these paths. The user's interactive shell is fish; shell examples avoid Bash-only variable syntax.

## Coverage and source authority

| Topic / skill reference | Workspace sources and evidence |
| --- | --- |
| API, ABI, lifecycle, build | `tools/forge-local/`, `tools/forge-rs/`, `references/provenance.json`; mod dependency locks, `src/lib.rs`, ABI records, mod-local `scripts/verify.py` |
| NRO relocation rules / hardware-test fork | [Build requirements](api-and-builds.md#rust-nro-relocation-requirements); per-mod target JSON, `scripts/verify.py`, `research/hardware-link.json`; [Lawrence fork](api-and-builds.md#lawrences-hardware-test-loader) |
| Hook pool / state / rollback | Forge `source/forge/hook.c`; Damage Numbers hook/gateway/mailbox source and tests; Key Quest Markers hooks/offers/ARM fixture; Modern Controls and Please do Better transaction/platform source |
| Native GUI extension | `mods/key-quest-markers/DEVELOPMENT.md`, `src/gui.rs`, `src/native.rs`, `mods/key-quest-markers/scripts/gui_layout.py`, `tests/native_adapter.py`, `research/theme-colours.json` |
| Rendering / storage | Damage Numbers `src/render.rs`, `src/config.rs`, runtime/context tests; Key Quest Markers settings/config; Please do Better settings/preferences and overlay gates |
| Validation / delivery | `docs/DEVELOPMENT.md`, per-mod `DISTRIBUTION.json`, `EXPORT.json`, release manifests, `EVIDENCE.json`, `scripts/mod_distribution.py` |
| Diagnostics / historical causes | `docs/RESEARCH.md`, `docs/WORKSPACE_EVIDENCE.json`, each mod's `EVIDENCE.json`, its DEVELOPMENT.md "Do not" list and Git history; current loader/libnx source for physical feasibility |

Core workspace reading: `AGENTS.md`, `README.md`, `docs/LOCAL_STATE.md`, `docs/DEVELOPMENT.md`, `docs/TOOLS.md`, `docs/RESEARCH.md`. Current source and exact artifact receipts resolve stale narrative claims. Preserve dated evidence instead of rewriting its historical assertions.

Useful evidence locations: `work/shared/game-exefs/`, `work/shared/forge-1.5.1/`, `work/research-tooling/`, per-mod `work/NAME/`, `build/NAME/candidates/`, and `build/NAME/releases/`. Ignored/private material may be absent from another checkout. Consult the current docs, EVIDENCE.json and Git history.

## Source and acceptance snapshot

Forge 1.5.1 commit `b23e114a23f41c9a8e2fd34b2f4df2a2102d0ee1`; forge-rs 1.5.0 commit `d1865b68e9b194eb3eacc8bd71bbf601a5fac63e`. Native offsets target main SHA-256 `b3935415499549adaf4c0e89822831daa175cfd456a7990791c79be3997645ef`, build `FB08F1D20FD1204FE7070672777F869B`.

| Maintained Switch mod | Snapshot / evidence boundary (2026-10-20) |
| --- | --- |
| Damage Numbers | r35 DEVELOPMENT candidate, gameplay NOT RUN; last release r30 (approval only, no affected-device run); r27 last user-tested on Eden/Linux |
| Key Quest Markers | r18 READY_TO_DISTRIBUTE, link rebuild of r17; r17 accepted Eden/Linux 2026-10-15 with and without optional HD |
| Modern Weapon Controls | r12 stock-loader maintenance, earlier r10 acceptance retained at its exact-byte scope |
| Please do Better | r24-forge151 maintenance; earlier reward-page/overlay evidence retains its own runtime limits |

`EVIDENCE.json.current` and `DISTRIBUTION.json` hold exact versions/hashes/status. Some mod development paragraphs describe preserved older releases. Do not turn this snapshot into a statement about the latest upstream or installed payload.
