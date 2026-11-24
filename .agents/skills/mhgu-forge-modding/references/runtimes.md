# Runtimes: what changes between Switch, emulators and ports

One NRO runs on five hosts. Most bugs that show on one host only come from a row
in the table below. Check each row your plugin touches before you ship.

| Host | Runs the game | Runs plugins | Forge it gets |
| --- | --- | --- | --- |
| Switch | Native ARM32 | Stock Forge 2.0.0 (`subsdk9`); 1.5.1 where players have not updated | Stock |
| Eden | Emulated ARM | Stock Forge in the emulated process | Stock |
| Ryubing 1.3.3 (and Ryujinx-Nextendo) | Emulated ARM | Stock Forge in the emulated process | Stock |
| MHGURecomp (PC, Linux/Windows) | Recompiled to host code | An ARM interpreter | Its own HLE of Forge's exports (`references/MHGURecomp/runtime/forge.c`, `forge_imgui.c`) |
| gu-native (Android, Windows) | Recompiled to host code, a fork of MHGURecomp's runtime | Same interpreter | Same HLE plus its own renderer (`/mnt/storage2/Programs/gu-native/src`, local checkout `9a1aef7`; the HUD findings below were read at upstream `c7fc45a`) |

The tester runs Eden, Ryubing and MHGURecomp. Nobody here runs gu-native or a
Switch, so findings for those two come from source and user reports only. Say so.

## Before you ship: one check per row

1. **Instructions.** Run the build's instruction gates (`verify.py`). Ryubing
   1.3.3 cannot run QADD/QSUB (`saturating_add`/`saturating_sub` emit them).
   MHGURecomp's interpreter aborts on NEON three-register-different forms other
   than VMULL/VMLAL/VMLSL (`VADDW` comes from widened compares). Fixes are in
   [Diagnostics](diagnostics.md).
2. **SVCs.** MHGURecomp's kernel ends the process on an unimplemented svc: no
   CreateCodeMemory/ControlCodeMemory (0x4B, 0x4C), no
   SetProcessMemoryPermission (0x73). QueryMemory 6 and GetInfo 0x29 are
   implemented; FlushProcessDataCache 0x5F returns success and does nothing
   (`runtime/kernel.c`), which is harmless because Recomp sees code changes
   only through Forge calls.
3. **Code writes.** On MHGURecomp only Forge hook and patch calls change game
   code. A plain store into `main`'s text is never seen. A hook inside a
   function makes Recomp interpret that whole function for the session, so keep
   interior hooks off per-draw paths (texture draw `0xa4fc9c` is one). Details:
   [Hooks and lifetimes](hooks-and-lifetimes.md#on-mhgurecomp).
4. **Screen geometry.** Forge's ImGui display is not the game's picture on
   every host. See [ImGui on each host](#imgui-on-each-host).
5. **HUD placement.** gu-native and UIScale move HUD quads after the game draws
   them. See [HUD movers (gu-native and UIScale)](gui-masks-and-movers.md#hud-movers-gu-native-and-uiscale).
6. **Input.** Forge's input comes from the host, once per rendered frame. See
   [Input and keybinds](input-and-keybinds.md).
7. **Fonts.** Each host's default ImGui font differs. See
   [Rendering](rendering-and-settings.md#fonts-and-text-fit).

## ImGui on each host

| Question | Switch, Eden, Ryubing | MHGURecomp | gu-native |
| --- | --- | --- | --- |
| What `io.DisplaySize` covers | The swapchain allocation. In handheld the game may present a smaller crop of it | The host surface, scaled over the whole window | The whole window. The game's picture is fitted centred inside it, letterboxed when shapes differ (`device.c` `backend_present`) |
| Where the game's real picture is | sFestaRender applied size +0xb8/+0xbc (`0x300a6cd8` type ID) | Same words hold the internal render size, which is not the overlay's size | Projection shape `m[5]/m[0]`, fitted in the window |
| Can a plugin read draw-list buffers | Yes | No. `ImDrawList` is a guest mirror of a host object; `VtxBuffer.Data`, `CmdBuffer.Data` and other `ImVector` data words read 0 while `Size` is real | Same as MHGURecomp |
| ImGui objects a plugin can hold | Heap only | 8192 mirrors shared by all plugins (`MAXM`, `forge_imgui.c:138`). Full pool: every plugin's drawing stops, with one log line naming nobody | Same pool code |
| Default font | Roboto Medium | Roboto only when a mod layer ships `nativeNX/forge/fonts/Roboto-Medium.ttf`, else ImGui's wider vector default | A mod layer's Roboto, else Android's `/system/fonts/Roboto-Medium.ttf` or `RobotoStatic-Regular.ttf`, else ImGui's vector default (`overlay.cpp`) |
| Temporal jitter in the game's projection | None | FSR writes per-frame jitter into projection m[8]/m[9] (`camera_jitter.c`) | Has `runtime/hle/camera_jitter.c` too (not read) |

What to do:

- **Find your coordinate space once per frame.** Damage Numbers is the worked
  example ([crop and projection](../../../../mods/damage-numbers/docs/worked/damage-view.md)): it detects Recomp by the zero
  `CmdBuffer.Data` after NewFrame, uses Forge's display size there, uses the
  applied crop elsewhere, and when the projection's shape differs from the
  display by more than 2% places the picture as the largest centred rectangle
  of that shape.
- **Zero m[8]/m[9] before projecting** a world point with the game's
  projection. The game leaves them 0, and Recomp's FSR puts jitter there, which
  makes overlay text shake.
- **Never write through `ImVector::Data`.** Pass offsets to ImGui calls
  instead. Damage Numbers' vertex edits land on the null page on Recomp, so its
  Wilds and Rise styles lose their outline stretch there (not fixed).
- **Free every ImGui object you create**, or the shared Recomp pool drains. Use
  `mods/imgui-meter` to count mints and frees per plugin.
- **Do not hook the ImGui implementation** to observe other plugins: Recomp's
  HLE stubs are not functions, so Forge refuses the hook. Rewrite the plugin's
  own `R_ARM_JUMP_SLOT` instead (imgui-meter, KatSmithy bridge).

## Input on each host

When input updates and where an edge is valid: [Input and keybinds](input-and-keybinds.md#timing-where-an-edge-is-valid).

| | Switch, Eden, Ryubing | MHGURecomp | gu-native |
| --- | --- | --- | --- |
| Source | `nn::hid`: handheld, else player 1 (`input.cpp`) | The host pad state; keyboard from SDL | Same HLE code (`forge.c`) |
| Forge menu key | `[menu] key` in Forge's `config.ini`: Insert (73) in the shipped `data/config.ini`, F9 (66) only if no ini is found; keyboard only. Ryujinx needs "Direct Keyboard Access" in its input settings | Insert (73) by default, the same ini key if a mod ships Forge's config, or "Open the Forge menu" in the port's Mods tab | Not read |
| Game input while Forge's menu is open | Still reaches the game | Blocked: the game gets no controller input (README) | Not read |
| Extra calls | None | Mouse, keybind and `forge_graphics_isMenuOpen` ([Input and keybinds](input-and-keybinds.md#mhgurecomp-extras)) | `forge_graphics_isMenuOpen` only, at `9a1aef7` |

## Other plugins

Other people's plugins differ by host too. KatLib and UIScale load on
MHGURecomp but fail on Eden with `0x00000616` beside BetterBox, because all
three ship an all-zero build ID. MHGU Definitive Edition 3.0.0 is an IPS plus a
`subsdk1`; its words inside your windows are listed per mod (Village Quests in
Hub, WishFinder). Load order rules per host are in
[Hooks and lifetimes](hooks-and-lifetimes.md).


## Common mistakes

| Mistake | Correct approach |
| --- | --- |
| Using `Input::is_button_pressed` in `forge_onUpdate` or a game hook | Forge updates input once per rendered frame, so the edge repeats or is lost. Read `is_button_down` and keep your own previous state there ([Input and keybinds](input-and-keybinds.md)). |
| Expecting Forge to hide a press from the game | It never does. Blank the game's pad records after `sPad::move` while your window owns input, and on MHGURecomp 0.17 the input views too ([Input and keybinds](input-and-keybinds.md), blocking step 5). |
| Telling Switch players to open Forge's menu with a button | Stock Forge 1.5.1 and 2.0.0 open it with a keyboard key only (Insert in its shipped config). Give console players another way to change a setting. |
| Importing MHGURecomp's extra calls (`forge_input_getMouse`, `setKeybind`, `isMenuOpen`) | Stock Forge does not export them, so the import check fails on Switch and emulators. No optional-import method is researched. |
| Placing ImGui drawing from HUD node positions, or cutting a HUD sprite with a scissor | gu-native and UIScale move HUD quads after the game draws them. Use the sprite's own geometry at its draw ([HUD movers](gui-masks-and-movers.md#hud-movers-gu-native-and-uiscale)). |
| Treating Forge's `io.DisplaySize` as the game's picture | It is the swapchain (Switch), the window surface (MHGURecomp) or the whole window with a letterboxed picture inside (gu-native) ([Runtimes](#imgui-on-each-host)). |
| Writing through `ImDrawList` `VtxBuffer.Data` or other `ImVector` data | On MHGURecomp and gu-native those read 0 (guest mirrors), so the write hits the null page. Pass offsets to ImGui calls. |
| Creating ImGui objects every frame without destroying them | MHGURecomp shares one 8192-slot mirror pool among all plugins; when it fills, every plugin's drawing stops. Count with `mods/imgui-meter`. |
| Using `i32::saturating_add`/`saturating_sub` | They compile to QADD/QSUB, which Ryubing 1.3.3 cannot run, and `-dsp` does not stop them in ARM mode. Use plain or u32-capped arithmetic and gate the build ([Diagnostics](diagnostics.md)). |
| Laying out ImGui text to Roboto's widths only | MHGURecomp falls back to a wider font. Measure and fall back to smaller sizes ([Rendering](rendering-and-settings.md#fonts-and-text-fit)). |

Sources: `tools/forge-local/source/forge/{input.cpp,graphics.cpp,config.c}`;
`references/MHGURecomp/{README.md,runtime/forge.c,runtime/forge_imgui.c,runtime/overlay.cpp,runtime/kernel.c}`
(read at `dafb590`; the mirror pool, overlay, kernel and input-view claims rechecked at 0.19.0, `471b3b9`); gu-native source as above; `mods/damage-numbers/DEVELOPMENT.md`,
`mods/imgui-meter/DEVELOPMENT.md`, `mods/world-sharpness-gauge/DEVELOPMENT.md`,
`mods/online-roaming/DEVELOPMENT.md`, `mods/please-do-better/DEVELOPMENT.md`.
