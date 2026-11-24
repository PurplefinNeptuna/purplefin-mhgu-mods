# Input and keybinds in a plugin

A plugin can read buttons two ways. Pick one per purpose and never mix their bit
masks.

| You want | Read | Why |
| --- | --- | --- |
| A plugin hotkey or a plugin window's controls | Forge input (`forge_input_*`, Rust `forge::input::Input`) | Physical buttons from the host, same API everywhere |
| To change what the game does with a press (remaps, buffering) | The game's own pad views and player command fields | Logical, after the game's button config. Facts: `mhgu-understanding` [Input and actions](../../mhgu-understanding/references/input-and-actions.md) |
| To stop the game seeing a press | Both: read with Forge, blank the game's pad records | Forge never consumes a press |

## Forge input API

`isDown`, `isPressed`, `isReleased` per `ForgeButton`; `getStickL`/`getStickR`
(-1..1); `isConnected`; `getTouch`; keyboard `isKeyDown`/`isKeyPressed`/`isKeyReleased`
and `isShiftDown`/`isCtrlDown`/`isAltDown`. Header `forge/input.h`; Rust
`forge::input::{Button, Key, Input}`. `forge_graphics_isMenuVisible()` (Rust
`Graphics::is_menu_visible`) says whether Forge's own window is open.

Stock Forge reads handheld first, else player 1 (`input.cpp` `forge_input_update`),
and only FullKey, Handheld and JoyDual styles. A second controller is not seen.

## Timing: where an edge is valid

Forge refreshes its state in `ImGui_ImplNVN_NewFrame`, once per presented frame,
not once per game update. MHGURecomp does the same before Forge draws, so a
plugin sees the previous frame's state there.

- In `forge_onImGuiRender` / `forge_onImGuiFreeRender`, `isPressed` gives one
  edge per frame. WishFinder's welcome window reads its controls there.
- In `forge_onUpdate` or a game hook, `isPressed` can repeat (two updates
  between frames) or be missed (two frames between updates). Read `isDown` and
  keep your own previous state in the callback that consumes it. Village Quests
  in Hub does this for L/R in its counter hook (`counter_update`,
  `newly_pressed`).

## Owning a press

Forge does not hide a press from the game, so a plugin window that uses A, B or
the D-pad would also move the game's cursor. WishFinder's welcome window blocks
the game this way:

1. Hook after `sPad::move` (inside `sFestaPad::move`, before the game builds its
   gameplay and menu views from the pad records).
2. While blocked, zero each `sPad::Pad` record's `On/Old/Trg/Rel/Chg/Rep`,
   sticks and triggers. Offsets: [Input and actions](../../mhgu-understanding/references/input-and-actions.md).
3. Keep blocking until every button is up after the window closes (or a frame
   limit), so the closing press does not reach the game.
4. End the block if no frame renders for a while (60 pad updates), so a hidden
   window cannot lock the game.
5. On MHGURecomp 0.17 with game actions on (`[Actions] Enable=1`, its default),
   the records are not enough: its outer hooks on the view translators
   `0x3de4b0`/`0x3de4f8` replace their answer with its own bindings' buttons, and
   it writes town actions into the menu view around the town avatar's controls
   `0x792728` (`runtime/hle/input_view.c`, 0.17.5/0.17.6 source). Also empty both
   views after `sFestaPad::move` `0x3ddf1c` (cur and pressed 0, released = prev,
   repeats +0x6c34/+0x6c3c 0) and the menu view's words during `0x792728`. Its
   outer layer runs before every plugin hook, so a plugin hook sees what it
   wrote. Purple-lib r22 does this (`mods/purple-lib/src/input.rs`); a held window kept the game still on Eden and MHGURecomp 0.17.5 (user report), the town path untested.

On MHGURecomp, while Forge's own menu is open the game gets no controller input
at all; on Switch and the emulators it still does. Ignore your hotkeys while
`isMenuVisible()` is true.

On MHGURecomp (0.16.1, `runtime/overlay.cpp`: `g_open = open || g_settings_open`,
then `if (!g_open) pad = {}`), ImGui gets no controller input while its overlay
(its settings or the Forge menu) is closed; real Forge feeds ImGui's gamepad
navigation every frame (`imgui_impl_nvn.cpp`, `UpdateGamepadNav`). Its
`forge_input_isDown`/`isPressed` read the pad every frame either way
(`runtime/forge.c`, `input_frame`). So a plugin's own free-render window reads
its buttons with Forge's input, not ImGui navigation: Purple-lib Tester's action
window does, as WishFinder's welcome window does.

On original Forge (Switch, Eden, Ryujinx) ImGui's gamepad navigation is fed every
frame, menu open or not, and Y is ImGui's `NavGamepadMenu` key
(`imgui_impl_nvn.cpp` maps `ForgeButton_Y` to `ImGuiKey_GamepadFaceLeft`;
`imgui_internal.h`: "Toggle menu layer. Hold to enable Windowing"): holding Y
opens ImGui's window switcher and L/R move the focus between windows
(`imgui.cpp` `NavUpdateWindowing`). Keep Y out of a plugin window's controls; the
input hold does not stop it, since ImGui reads Forge's input.

## Choosing a button

- **Scope the hotkey to a screen.** The game uses every button somewhere. Ship
  hotkeys that act only on one screen and state: Village Quests in Hub reads L/R
  only in the quest counter's states 0..2; WishFinder and its KatSmithy bridge
  read R3 only on smithy list screens.
- **Show it in the game's button guide** with a guide extra entry, and choose
  L/R or ZL/ZR icons from the game's shoulder-swap byte, as the start menu does
  ([Button guide and popups](gui-screen-reuse.md#button-guide-and-popups);
  icon IDs in [Input and actions](../../mhgu-understanding/references/input-and-actions.md#button-names-and-icons)).
- **Forge buttons are physical, game views are logical.** A player with the
  swapped shoulder layout presses physical ZR for the game's R. If your hotkey
  must match a game action, read the game's view or the config bytes.
- **Check other plugins' use.** KatSmithy polls the pad at `0x86d34c` and uses
  the right stick's axis (not its click) to rotate the smithy preview. KatLib
  offers a pad filter (`katlib_register_pad_filter`) that can mask the game's
  menu-pressed word at `+0x6bfc`. Read their ini and imports before claiming a
  button is free.
- **Debounce long actions.** One press that queues many API calls must check
  each call's answer (the KatSmithy bridge's line add ends on the deny tone with
  the count logged when a mailbox refuses).

## Forge's own menu

Stock Forge 1.5.1 and 2.0.0 toggle its window on a **keyboard** key only:
`[menu] key` in `nativeNX/forge/config.ini`. The `data/config.ini` Forge ships
sets 73 (Insert); 66 (F9) is only the fallback when no ini is read (`graphics.cpp`
`Graphics::render`, `config.c`, `include/forge/input.h`). On Ryujinx the key
reaches the game only with "Direct Keyboard Access" on (Forge's README). A Switch player with no
keyboard cannot open it, so a setting a player must reach on console needs
another way in (an in-game row, an ini). MHGURecomp opens it with Insert (73)
by default or from "Open the Forge menu" on its settings' Mods tab, and closes it
with the game's cancel button or Start + Back.

## MHGURecomp extras

MHGURecomp's HLE exports calls stock Forge does not have
(`runtime/forge.c`, README "For mod makers"):

| Call | Does |
| --- | --- |
| `forge_input_getMouse(x, y, buttons)` | Pointer in 1280x720 screen pixels and buttons; false while captured, Forge's menu is open or off the picture |
| `forge_input_getMouseMove(dx, dy)` | Movement since last frame, also while the hunt camera holds the mouse; 0 while Forge's menu is open |
| `forge_input_setMouseFree(bool)` | Release capture while a mod's own menu is open |
| `forge_input_setKeybind(row, keys)` | Give a `[Keybinds]` row of `mhgurecomp.ini` other keys for now (up to two); NULL gives it back. Last caller wins. Refuses the chat key and reserved keys (Esc, Insert, F1, F7..F12) |
| `forge_input_getKeybind` / `getModKeybind` | The player's keys for a row / a mod's temporary keys |
| `forge_input_getKeyPressed(out, size)` | The first key pressed since last frame, by its ini name, for a mod's rebinding menu |
| `forge_graphics_isMenuOpen()` | Same as `isMenuVisible` |

No mod here uses them. Stock Forge does not export them, and each mod's
`verify` checks strong imports against Forge 1.5.1's exports, so a plain import
fails there. A way to import them optionally has not been researched.

Sources: `tools/forge-local/source/forge/{input.cpp,graphics.cpp,config.c}`,
`graphics/imgui_impl_nvn.cpp:753`; `tools/forge-rs/forge/src/{input.rs,graphics.rs}`;
`references/MHGURecomp/runtime/forge.c` (commit `dafb590`);
WishFinder [welcome window](worked/wishfinder-welcome.md), [button guide](worked/wishfinder-guide.md),
`mods/village-quests-in-hub/{DEVELOPMENT.md,src/lib.rs}`,
`mods/wishfinder-katsmithy-bridge/DEVELOPMENT.md` (retired; in Git at `2888d72`).
