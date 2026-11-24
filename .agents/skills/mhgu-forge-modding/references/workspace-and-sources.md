# Original workspace and coverage index

This appendix describes `/mnt/storage2/Programs/MHGU_Modding`. All other source pointers in this skill are relative to that root.

Machine paths (RomFS, library, emulator packages and logs, MHGURecomp) are in the workspace's root `AGENTS.md`, "Runtime evidence and installation paths"; the other local inputs (sealed game files, copied executables, Forge packages, research tooling) are in `docs/LOCAL_STATE.md`. Outside this workspace, supply equivalent inputs explicitly; the skill's Markdown stays usable without them.

## Coverage and source authority

| Topic / skill reference | Workspace sources and evidence |
| --- | --- |
| API, ABI, lifecycle, build | `tools/forge-local/`, `tools/forge-rs/`, `references/provenance.json`; mod dependency locks, `src/lib.rs`, ABI records, mod-local `scripts/verify.py` |
| NRO relocation rules / hardware-test fork | [Build requirements](rust-builds.md#rust-nro-relocation-requirements); per-mod target JSON, `scripts/verify.py`, `research/hardware-link.json`; [Lawrence fork](rust-builds.md#lawrences-hardware-test-loader) |
| Hook pool / state / rollback | Forge `source/forge/hook.c`; Damage Numbers hook/gateway/mailbox source and tests; Key Quest Markers hooks/offers/ARM fixture; Modern Controls and Please do Better transaction/platform source |
| Native GUI extension | `mods/key-quest-markers/DEVELOPMENT.md`, `src/gui.rs`, `src/native.rs`, `mods/key-quest-markers/scripts/gui_layout.py`, `tests/native_adapter.py`, `research/theme-colours.json` |
| Rendering / storage | Damage Numbers `src/render.rs`, `src/config.rs`, runtime/context tests; Key Quest Markers settings/config; Please do Better settings/preferences and overlay gates |
| Validation / delivery | `docs/DEVELOPMENT.md`, per-mod `DISTRIBUTION.json`, `EXPORT.json`, release manifests, `EVIDENCE.json`, `scripts/mod_distribution.py` |
| Diagnostics / historical causes | Each mod's `EVIDENCE.json`, its DEVELOPMENT.md "Do not" list and Git history; current loader/libnx source for physical feasibility |

Core workspace reading: `AGENTS.md`, `README.md`, `docs/LOCAL_STATE.md`, `docs/DEVELOPMENT.md`, `docs/TOOLS.md`. Current source and exact artifact receipts resolve stale narrative claims. Preserve dated evidence instead of rewriting its historical assertions.

Useful evidence locations: `work/shared/game-exefs/`, `work/shared/forge-2.0.0/` (and `forge-1.5.1/`), `work/research-tooling/`, per-mod `work/NAME/`, `build/NAME/candidates/`, and `build/NAME/releases/`. Ignored/private material may be absent from another checkout. Consult the current docs, EVIDENCE.json and Git history.

## Source baselines

Pinned Forge and forge-rs commits: [API and builds](api-and-builds.md) and the root `AGENTS.md`. Native offsets target the main executable identified in the mhgu-understanding skill's `discovery-and-evidence.md`. Per-mod versions, status and hashes are in each mod's `DISTRIBUTION.json` and `EVIDENCE.json`, and the current builds in `docs/LOCAL_STATE.md`.
