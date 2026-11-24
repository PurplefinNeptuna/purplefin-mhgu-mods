# Rendering, settings, and filesystem ownership

## Choose the rendering path

Use the native game tree for decorations that must follow an existing menu's transforms, visibility, selection, and destruction. Use Forge's ImGui callbacks for settings and independent overlays. Key Quest Markers renders badges natively and uses ImGui only for settings. Damage Numbers and current Please do Better use Forge overlays.

An overlay that must line up with a HUD part breaks wherever the HUD is moved after the game draws it (gu-native, UIScale): use a native node there ([HUD movers](gui-masks-and-movers.md#hud-movers-gu-native-and-uiscale)). An overlay that follows the 3D world must find the game's picture inside Forge's display, which differs per host, and must not write through ImGui buffer pointers ([Runtimes](runtimes.md#imgui-on-each-host)).

`forge_onImGuiRender` runs inside the plugin UI. Give each settings panel a stable plugin-specific ID and a compact unframed tree, closed by default. Pair each successful TreeNode with TreePop. Keep rendering/update work outside the open-row branch. A plugin without settings needs no panel.

Free-render callbacks execute outside Forge's main window. Use the intended DrawList or matched Begin/End window calls. On `forge_onImGuiInit`, install the provided current context and allocation/free pair before accessing ImGui. Do not assume an old context's fonts or texture handles remain alive.

## Assets and context replacement

Damage Numbers uses file-loaded Open Sans and external RGBA artwork. Ordinary builds copy prepared assets. Raw ImGui bindings are justified for exact glyph ink metrics, texture registration, vertices, and shutdown integration; ordinary draws use forge-rs wrappers.

Check sizes before allocating, detect short reads, close all successful opens, and destroy partial resources. Let the font atlas own transferred file data. Register/unregister texture resources using matching allocators and shutdown callbacks. Use a generation counter that advances on context shutdown even if no texture loaded. A reused context address is not proof of the same lifetime. Repeated initialization of a live context must not duplicate assets. Missing artwork may omit effects while retaining readable numbers. Deduplicate diagnostics across reinitialization.

Damage rendering consumes copied model values. It never follows game identities captured by hooks. Use current display dimensions, actual font metrics, stable overlap placement, and peak animation bounds. Reset placement when epoch, viewport, style, or scale changes. The `mhgu-understanding` damage/camera reference owns the matrix and capture findings.

Damage Numbers keeps valid damage when impact/camera/projection is unavailable by placing it at display centre with ordinary animation/spacing. Missing position is explicit, while a genuine world origin remains valid. Behind-camera and clipped points are skipped for that frame, not centred. Invalid display dimensions prevent drawing. The viewport aspect guard cannot prove that a same-aspect offscreen camera belongs to the presented frame.

Memory: a plugin's `malloc`/`free` resolve to main's exports, so Forge, every plugin, ImGui and the game share one heap.

Forge's NVN backend keeps each ImGui texture twice: its RGBA32 pixels and a GPU pool from `aligned_alloc` (`source/forge/graphics/allocator.cpp`). So a texture costs 8 bytes a texel of that heap. ImGui also bakes every font size used into Forge's shared glyph atlas for the session.

The backend frees a texture in `WantDestroy` once `UnusedFrames` > 0 (`imgui_impl_nvn.cpp`), but ImGui counts `UnusedFrames` only for its own atlases. So a plugin freeing a user texture sets both itself, after the frames that drew it. It then unregisters and destroys the texture once the status reads `Destroyed` (WishFinder `welcome::release`).

## Fonts and text fit

Each host has its own default font ([Runtimes](runtimes.md#imgui-on-each-host)); MHGURecomp's fallback is wider than Roboto, so text laid out to Roboto's widths can overflow. Measure each string with `CalcTextSize` at the size you draw it, wrap or step down through fixed sizes until it fits (WishFinder `welcome::popup`: 28, 24, else 16), and check the longest language. WishFinder's welcome harness (`work/wishfinder/welcome-harness/run.py`, `FONT=default`) renders a page with that fallback font for comparison.

Pictures of native screens show only what the explanation needs. The tester asked WishFinder to drop every imitated page number from its pictures ("the < 1 / 4 > imitation is buggy on other recomp, please remove that because that isnt needed"); the window's own page count stays.

## Session settings and persistence

The workspace default is one primary plugin-specific INI, explicit Save, and defaults for missing/invalid primary input. Never create/read/recover/delete `_backup` configs. Reset and editing normally affect session/draft state until the mod's Save/Apply policy completes. Preserve session settings on failure and report save status without claiming old disk bytes are intact after a failed write.

Use Forge's counted save mount and balance every successful acquisition with release. The mount point is supplied by Forge, rather than guessed from an emulator's host save layout. Validate values, write/flush, read back, and check commit before reporting a checked save as successful. On a failed save keep the session settings; the file on disk is then not guaranteed. Close handles and restore SDK abort/error context on every path. The native SDK file and handle ABI must be verified for ARM32.

The stock Rust helpers have relevant limits: ScopedMount panics on failure, Reader can assert on short reads, Writer can ignore short writes, and checked flush/commit are absent. Key Quest Markers uses narrow checked SDK calls around Forge's mount to meet its stronger contract. Do not silently describe the high-level helpers as checked transactional storage.

**Damage Numbers exception:** its explicitly requested upstream `config::load`, default-file creation, ScopedMount, and Writer behavior is retained. It uses IniSerialize/IniDeserialize, per-field validation/defaults, and an explicit settings Save. Do not replace that accepted policy with the other mods' custom storage design during unrelated work.

Each mod's own settings contract (keys, ranges, Save & apply behaviour) is in its DEVELOPMENT.md; Key Quest Markers and Please do Better are worked examples of the checked-storage pattern above.

## Logs

Emit brief lifetime-deduplicated failure reasons outside hot hooks. Successful frames, hits, reward rows, and ordinary saves do not produce periodic diagnostics. Key Quest Markers keeps one INFO startup line and once-per-reason failures. Closed settings rows must not stop pending diagnostic collection or background work.

Sources: `tools/forge-local/source/forge/graphics.cpp`, `tools/forge-rs/forge/src/{config.rs,mt/fs.rs}`, `mods/damage-numbers/src/{lib.rs,render.rs,config.rs,runtime.rs}`, `mods/key-quest-markers/src/{settings.rs,config.rs}`, `mods/please-do-better/src/settings.rs`, `mods/please-do-better/core/src/preferences.rs` and their development/evidence records.
