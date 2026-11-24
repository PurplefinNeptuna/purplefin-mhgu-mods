# Gameplay recipes from shipped mods

## Target camera tap (Lock-on Target)

Lock-on Target does what clarkekoko's lock-on and No Target Reticle cheats do with two replacing hooks. The tap logic detour runs the cheat's version for the local hunter: a tap flips a lock flag, and while it is on only bit 0 is raised, every frame, except while weapon R (`+0x13f4 & 0x65f93c()`) is held. The reticle check `0x190d4` returns 0. Layout and install: `mods/lock-on-target/docs/worked/hooks.md`.

Running the window out every frame (0.001 before the original) also raises bit 24 through the countdown path, and the user found that ruined aiming. The earlier "Lock-on Target V1" cheat gates on `[main+0x184ddc8]` != 0 and writes 5.0 through `[main+0x2126f48]` -> +0x58. It works on Eden only because Eden's cheat engine writes 12 times a second, so the window keeps running out; written every frame, it never fires. The end path `0x5584a0([...])` == 1 clears bit 6 (tail call `0x285ec4`); bit 6 is set at `0x27ee04`.

The target crosshair's zoom-in animation replaying while locked looks like a twitch. The reticle draw is `0x61ecc0`, called only from `0x61e95c` (input-and-actions.md, Target camera tap). Its panel class is unconfirmed: lead `cUIOCPanelTargetCamera` (DTI size 0x58, vtable `0x177a4d0`), which does not hold `0x61e95c`'s caller `0x61e20c`.

## Remapping weapon input (Modern Weapon Controls)

Current hooks observe modifier preprocessing `0x27e774`, shared classification `0x27ca28`, closed quest-menu chat `0x678894`, general getter `0x285e2c`, and eligibility `0x2ecefc`. Physical ZR becomes native weapon R, physical R supplies sheathed sprint in the scoped local getter, Y retains sheathe/Valor, and ZL+new X/A/B selects Art 64/65/66 in that priority.

Consume Art inputs even if the Art is unavailable. Preserve pending native requests and the Art words +0x143c/+0x1440, which survive the normal 0x28-byte clear. Prevent the legacy R+A+B path from creating a new Art request while preserving an existing Art 1 latch. Combination buffer/timer+0x1444/+0x1448 and R timer/state +0x144c/+0x1454 need owned transition cleanup.

General command flag 0 is shared with drawn states, so changing it globally breaks weapon modifiers. Nonlocal players pass through without clearing local history. Village input must not reuse quest snapshots. Open menus/camera remain native. Quest-menu outer state 1 is the closed-menu chat context; outer 2 is open, inner 0 root and inner 1 submenu. Suppress only the closed combat ZR chat path.

## Empty-magazine reload (Modern Weapon Controls)

The maintained conversion requires an original-accepted empty-shot row, drawn local bowgun, fresh buffered logical A edge, empty magazine at the press, reloadable reserve, matching active native reload row/frame window, and no competing eligible X action. Replace the complete local Exec, retaining native evaluation/buffering, animation, refill, and timing. Restore temporary X flag views immediately. Holds through the last shot do not create a fresh conversion.

Candidate selection uses that form; the unchanged native evaluator later applies `(p,0)` for dispatch. r9's early strict check could fall back to dry fire during restrictions; r10 separated selection and dispatch and was user-accepted. This does not authorize skipping native restrictions or directly starting animations.

Unknown rows, ambiguous duplicates, unsupported postconditions, missing reserve, different timing, or lost ownership retain native behavior. Retain a replacement only while its native row/cache remains valid; cancel owned latches on menu/settings/sheathing transitions.

Forge's singleton map is built once before `sApp_run`, so objects constructed later are missing from it; check the native cells instead.
