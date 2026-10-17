# Input representations and native actions

These offsets and decisions are scoped to Switch 1.4.0 and the maintained Modern Weapon Controls research. The original controls mod changes local native command views; it does not replace the game's complete input system.

## Keep representations separate

| View | Verified masks / fields |
| --- | --- |
| Combat conversion (`0x3de4b0`, table `0x162aa24`) | X 0x20, R 0x40, B 0x80, A 0x100, ZL 0x200, ZR 0x800, Y 0x10 |
| Menu JoyData | R 0x200, ZR 0x800 |
| Forge/Npad | Use its actual bindings, not combat/menu masks |
| sFestaPad cell `0x188c670` | Gameplay held/previous/pressed/released +0x6b9c/+0x6ba0/+0x6ba4/+0x6ba8 |
| Same pad, menu view | Held/previous/pressed +0x6bf4/+0x6bf8/+0x6bfc |

sUserInfo cell `0x1897f78` supplies settings. Control byte+0x446c=2 means displayed Control Type 3, and original shoulder assignment+0x446e=0. Native R accessor `0x65f93c` returns 0x40 for assignment 0, else 0x800. Its PC-relative prologue was deliberately not hooked.

## Find the local player and weapon

Read session pointer cell `0x188ca48`, then local hunter index+0x30 in range 0..3. Read sPlayer cell `0x1885b58`, then player pointer+0x1c+4*index. Never obtain that index from sUserInfo. Native helpers `0x3f8398`/`0x276278` support this chain. Validate each mapping and pointer.

Player+0x13c4 is weapon pointer; weapon ID+0x4d4 uses 0 GS, 1 SnS, 2 Hammer, 3 Lance, 4 HBG, 6 LBG, 7 LS, 8 SA, 9 GL, 10 Bow, 11 DB, 12 HH, 13 IG, 14 CB, 15 Prowler; 5 is unused. Player+0x2749 bit 0 is draw state (getter `0x2a2444`). IDs are not a contiguous 14-weapon ordinal.

The combat gate reproduces `0x3a5ed0(selector5, thirdArg1)` using byte at `*main[0x188ad90]+0x50`. States 4, 5, 6, 7, 9 block combat; 8 does not. Imported mState+0x4c is another field. Treat entry/exit transitions as state changes, including hold quarantine until release.

## Native processing order

`0x2a79cc` copies input, preprocesses modifiers, applies Arts, checks mode/camera gates, then classifies shared/weapon commands. Player logical held/previous/pressed halfwords are +0x13f4/+0x13f6/+0x13f8; full/high-bit fields +0x13fc/+0x1400/+0x1404. Prior presses +0x13fa/+0x1408 are already logical and must not be remapped twice.

Current hooks observe modifier preprocessing `0x27e774`, shared classification `0x27ca28`, closed quest-menu chat `0x678894`, general getter `0x285e2c`, and eligibility `0x2ecefc`. Physical ZR becomes native weapon R, physical R supplies sheathed sprint in the scoped local getter, Y retains sheathe/Valor, and ZL+new X/A/B selects Art 64/65/66 in that priority.

Consume Art inputs even if the Art is unavailable. Preserve pending native requests and the Art words +0x143c/+0x1440, which survive the normal 0x28-byte clear. Prevent the legacy R+A+B path from creating a new Art request while preserving an existing Art 1 latch. Combination buffer/timer+0x1444/+0x1448 and R timer/state +0x144c/+0x1454 need owned transition cleanup.

General command flag 0 is shared with drawn states, so changing it globally breaks weapon modifiers. Nonlocal players pass through without clearing local history. Village input must not reuse quest snapshots. Open menus/camera remain native. Quest-menu outer state 1 is the closed-menu chat context; outer 2 is open, inner 0 root and inner 1 submenu. Suppress only the closed combat ZR chat path.

## Empty-magazine reload

HBG/LBG classifiers `0x117eb58`/`0x118c920` emit X weapon flags 5/21 and A 4/20 at player +0x1424, separate from general flags +0x1414. Selected ammo slot/magazine/capacity are bytes+0x2b80/+0x2b82/+0x2b84. Native reserve getter `0x2ffba0` handles Normal 1's special reserve and signed slot quantities; do not derive reloadability from magazine alone.

`cPlCmdExec` 32 bytes contains four u16 action/condition fields, four s32 args, three s16 frame fields and padding. `cPlCmdTbl` 28 has length +8/capacity +12/row-pointer array +20; `cPlCmd` 24 has resource +8 and frame floats+12/+16/+20. Native table/row/resource conversion is at `0x26d42c`/`0x26d018`/`0x2731b4`. The evaluator has a 48-byte acceptance cache and checks row active byte+4.

The maintained conversion requires an original-accepted empty-shot row, drawn local bowgun, fresh buffered logical A edge, empty magazine at the press, reloadable reserve, matching active native reload row/frame window, and no competing eligible X action. Replace the complete local Exec, retaining native evaluation/buffering, animation, refill, and timing. Restore temporary X flag views immediately. Holds through the last shot do not create a fresh conversion.

Reload postcondition helper `0x2ad534(p,1)` checks capability while skipping only the current-action restriction. Candidate selection uses that form; the unchanged native evaluator later applies `(p,0)` for dispatch. r9's early strict check could fall back to dry fire during restrictions; r10 separated selection and dispatch and was user-accepted. This does not authorize skipping native restrictions or directly starting animations.

Unknown rows, ambiguous duplicates, unsupported postconditions, missing reserve, different timing, or lost ownership retain native behavior. Retain a replacement only while its native row/cache remains valid; cancel owned latches on menu/settings/sheathing transitions.

Sources: `mods/modern-weapon-controls/src/`, especially game-input/bowgun/transaction headers, `DEVELOPMENT.md`, `src/game_signatures.h`, native tests, `RUNTIME_RESULTS.json`, `EVIDENCE.json`. Better Input is optional co-installed history, not a dependency inferred from activation. Static coverage of 84 weapon/style combinations and 8 Prowler biases is not an exhaustive gameplay run.
