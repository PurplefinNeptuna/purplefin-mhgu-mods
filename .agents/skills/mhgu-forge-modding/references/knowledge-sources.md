# Where the game knowledge came from

The understanding skill states what the game does and labels it bytes, run or inference. This page says which mod, run or file proved it, so a fact can be rechecked.

## By understanding page

| Page | Sources |
| --- | --- |
| native-gui | `mods/key-quest-markers/{DEVELOPMENT.md,EVIDENCE.json}`, `src/gui.rs`, `mods/key-quest-markers/scripts/gui_layout.py`, `tests/{resource.py,native_adapter.py}`, `research/theme-colours.json`; `mods/please-do-better/DEVELOPMENT.md` native geometry/shader findings. |
| quests-and-progression | `mods/key-quest-markers/core/src/lib.rs`, `src/{native.rs,offers.rs,gui.rs}`, `scripts/{quest_unlocks.py,urgent_chain.py}`, `DEVELOPMENT.md` native classification/special urgents/talk selector, ARM adapter tests, `EVIDENCE.json`; saved Ghidra/DTI and copied resources. Runtime base-game and optional-HD acceptance is dated 2026-10-15 on Eden/Linux; individual quest-state coverage is not exhaustive. |
| multiplayer-and-areas | `mods/online-roaming/DEVELOPMENT.md`, `mods/shared-urgent-quests/DEVELOPMENT.md`. |
| resources-and-tooling | `docs/TOOLS.md`, `mods/hd-project/README.md`, shared ARC/GMD tests and build receipts; offline wiki CFileIndex, Weapon-Parameter-Modding, Item-Editing, Font-Editing, Model-and-Texture-Extract, audio pages; `references/MHGU-Modding/templates/` (checked by `scripts/check_wiki_templates.py`) and `weapon_MV_Index/`. Wiki claims not verified locally retain lead status. |
| damage-and-cameras | `mods/damage-numbers/src/{signatures.rs,gateway.S,runtime.rs,render.rs}`, `core/src/{capture.rs,mailbox.rs,lib.rs,presentation.rs}`, tests, `DEVELOPMENT.md`, `EVIDENCE.json`; read-only projection research under `work/damage-numbers/projection-r27/native/` when present. |
| rewards-and-luck | `mods/please-do-better/DEVELOPMENT.md` count, copy, layout and reward-page sections; `core/src/{attribution.rs,quantity.rs,mode.rs}`, `src/{runtime.rs,gateway.S}`, native tests, `research/{patch-sites.json,highlight-fixtures.json}`, `EVIDENCE.json`; original main and retained reward-page receipts when available. |
| quest-files | `mods/wishfinder/{DEVELOPMENT.md,core/src/quest_build.rs,core/src/quests.rs,core/src/definitive_edition.rs}`, `mods/wishfinder/scripts/generate_quests.py`, `work/wishfinder/` notes above. |
| armor-models | `mods/skin-loader/DEVELOPMENT.md`, `work/skin-loader/{DESIGN.md,resource-sharing.md}`, `mods/skin-loader/scripts/make_skin.py`, a scan of every `nativeNX/arc/player/com/*/*/*.arc` in the 1.4.0 RomFS, `work/research-tooling/dti/dti.jsonl` for type names. |
| discovery-and-evidence | `docs/TOOLS.md`, `scripts/{research_tools.py,mhgu_binary.py,dti_dumper.py}`, `scripts/ghidra/`, saved summary/provenance, `mods/dti-dumper-support/README.md`, `references/MHGU-Modding.wiki/`, and `references/MHGU-Modding/`. [Workspace and sources](workspace-and-sources.md) provides snapshot revisions and machine paths. |
| input-and-actions | `mods/modern-weapon-controls/core/src/` (input, binding, bowgun and install), `src/`, `DEVELOPMENT.md`, `core/src/signatures.rs`, native tests, `RUNTIME_RESULTS.json`, `EVIDENCE.json`. Static coverage of 84 weapon/style combinations and 8 Prowler biases is not an exhaustive gameplay run. |
| sharpness | `mods/world-sharpness-gauge/{DEVELOPMENT.md,core/src/lib.rs,src/insert.rs}`; `work/world-sharpness-gauge/{PHASE0_RESEARCH.md,PHASE2_RESEARCH.md,PHASE5_RESEARCH.md,hud0-sharpness.json}`. |
| rendering | `work/skin-loader/render-fix-study.md` and `render-tools/` (shaders translated with MHGURecomp's `translate.c`, the game's NVN name order); `references/MHGU-Character-Render-Fix/src/render_fix.c` (slot list and package layout, read for leads); Skin Loader r19 to r22 runs on MHGU Recomp and Eden (`mods/skin-loader/EVIDENCE.json` runtime_r19 to runtime_r22_eden). |
| file-formats (MtFile paths) | `./scripts/tool.sh research dis` of `MtFile::canonicalizePath` `0x8292ec` and `MtFile::open` `0x82b1ec` in the checked 1.4.0 main; `work/skin-loader/FEATURES-PLAN.md` phase 2. |
| save-data | `work/save-guard/notes.md` (static: main's disassembly and MOD0 relocations, the decompressed `sdk` and its symbols); `tools/forge-local/source/forge/fs.cpp`; `references/eden/src/core/hle/service/filesystem/fsp/fs_i_filesystem.cpp`; WishFinder `src/save_lock.rs` and its adapter fakes; the lock taken live on Eden (WishFinder r148, `EVIDENCE.json` runtime_r148_eden_2026_11_25). |

## By topic

| Topic | First sources to inspect |
| --- | --- |
| Discovery / executable identity | `docs/TOOLS.md`, `scripts/{research_tools.py,mhgu_binary.py}`, `work/research-tooling/ghidra-export/summary.json`, DTI provenance |
| DTI trial / limitations | `mods/dti-dumper-support/README.md`, `scripts/dti_dumper.py` |
| Native GUI | Key Quest Markers `src/{gui.rs,native.rs}`, `mods/key-quest-markers/scripts/gui_layout.py`, `tests/native_adapter.py`, `research/theme-colours.json`; Please do Better native geometry research |
| Sharpness | World Sharpness Gauge `DEVELOPMENT.md`, `core/src/lib.rs`, `src/insert.rs`; `work/world-sharpness-gauge/PHASE*_RESEARCH.md` |
| Quests / progression | Key Quest Markers `core/src/lib.rs`, `src/{native.rs,offers.rs}`, native tests and `DEVELOPMENT.md` |
| Input / actions | Modern Weapon Controls `src/`, `core/src/`, native fixtures, `core/src/signatures.rs`, `DEVELOPMENT.md`, `RUNTIME_RESULTS.json` |
| Damage / cameras | Damage Numbers `src/signatures.rs`, `core/src/{capture.rs,lib.rs,presentation.rs,mailbox.rs}`, tests, `work/damage-numbers/projection-r27/` |
| Rewards / Luck | Please do Better `src/runtime.rs`, `core/src/{quantity.rs,attribution.rs}`, native fixtures, `DEVELOPMENT.md`, research/layout receipts |
| Resource/tool workflows | `docs/TOOLS.md`, tool wrappers/tests, offline wiki/templates/indexes, `mods/hd-project/README.md` |
| Exact current release/evidence scope | Each mod's `DISTRIBUTION.json` / `EVIDENCE.json` |

Current instructions and source establish present implementation. Dated evidence retains original hashes/claims. Mod development documents include older investigations, so check the current release/source before copying a colour, loader assumption, fixed key count, hook recipe, or unresolved-state workaround. Superseded materials live in Git or accepted backups.

Sound samples, `sbkr.py`, `srqr_map.py ARC KEY` (every request, group, key and wave) and `dsp2wav.py ARC PREFIX OUTDIR` are in `work/wishfinder/sound-samples/`; the MSS decoder is `work/wishfinder/mss.py`. Addresses in MHGURecomp's source are the game's plus `0x200000`.
