# Input representations and native actions

Offsets are for Switch 1.4.0.

## Keep representations separate

| View | Verified masks / fields |
| --- | --- |
| Combat conversion (`0x3de4b0`, table `0x162aa24`) | X 0x20, R 0x40, B 0x80, A 0x100, ZL 0x200, ZR 0x800, Y 0x10 |
| Menu JoyData | R 0x200, ZR 0x800 |
| Npad | Physical buttons; never the combat or menu masks |
| sFestaPad cell `0x188c670` | Gameplay held/previous/pressed/released +0x6b9c/+0x6ba0/+0x6ba4/+0x6ba8 |
| Same pad, menu view | Held/previous/pressed +0x6bf4/+0x6bf8/+0x6bfc (pressed = held & ~previous, `0x3de0d4`), repeat +0x6c34; menus that repeat a held D-pad read `pressed | (repeat & 0xf0)` (`0x54c168`..`0x54c178`) |
| Menu bits (table `0x162aa24`, 25 {output, menu bit} pairs read by `0x3de4b0`) | Select 0x1, L3 0x2, R3 0x4, Start 0x8, D-pad 0x10..0x80, L 0x100, R 0x200, ZL 0x400, ZR 0x800, X 0x1000, A 0x2000, B 0x4000, Y 0x8000, sticks from 0x20000. L/R/ZL/ZR depend on `sUserInfo+0x446e` (`0x65f8ec`); `0x65f8c4`/`0x65f914` return the page-left/right buttons (L/R, or ZL/ZR when swapped) |

Where those views come from: `sFestaPad::move` `0x3ddf1c` (object vtable `0x1754954` slot 0x1c) calls `sPad::move` `0xbaade4`. It is that function's only caller (`bl` at `0x3ddf24`). It then builds the gameplay view +0x6b98 and the menu view +0x6bf0 with `0x3de064`. That reads the selected `sPad::Pad` record's `On` (record +0x190; pad 0 at +0x1d0) and derives pressed and released from it.

It skips both views while `sFestaMain` (`0x2126764`) has +0x60 zero and `mPause` (+0x64) set. `sPad::Pad` (DTI, 2896 bytes; eight in `mPad` from +0x40, `Handheld` at +0x5ac0): `On`/`Old`/`Trg`/`Rel`/`Chg`/`Rep` u64 at +400..+440, `Rx`/`Ry`/`Lx`/`Ly` s32 at +448..+460, `Rz/RT` +464, `Lz/LT` +465.

sUserInfo cell `0x1897f78` supplies settings. Control byte+0x446c=2 means displayed Control Type 3, and original shoulder assignment+0x446e=0. Native R accessor `0x65f93c` returns 0x40 for assignment 0, else 0x800. Its prologue is PC-relative.

## Button names and icons

The game draws a button glyph from message table 18, `buttonName` (`resident_<lang>.arc`), joined to a label through CommonMsg 13. IDs: 4 `PAD_L`, 5 `PAD_R`, 14 `PAD_START`, 15 `PAD_SELECT`, 128 `PAD_ZL`, 129 `PAD_ZR`, 130 `ANALOG_LB`, 131 `ANALOG_RB`, 132 `ANALOG_RS`. Which glyph a right-stick click shows in game is unverified.

The icon follows the player's button config, so read it, do not assume it: the start menu's R label (`0x678214`) picks 5 or 129 through `0x65f858`, which reads the shoulder swap byte +0x446e. The guide presets choose L or ZL, R or ZR by byte +0x446c (preset flags `0x1000`/`0x2000`; other flags `0x400` X, `0x800` Y, `0x8000` START). The guide's layout and extra entries: [Button guide](guide-and-popups.md#button-guide).

## Find the local player and weapon

Read session pointer cell `0x188ca48`, then local hunter index+0x30 in range 0..3. Read sPlayer cell `0x1885b58`, then player pointer+0x1c+4*index. Never obtain that index from sUserInfo. Native helpers `0x3f8398`/`0x276278` support this chain. Validate each mapping and pointer.

Player+0x13c4 is weapon pointer; weapon ID+0x4d4 uses 0 GS, 1 SnS, 2 Hammer, 3 Lance, 4 HBG, 6 LBG, 7 LS, 8 SA, 9 GL, 10 Bow, 11 DB, 12 HH, 13 IG, 14 CB, 15 Prowler; 5 is unused. Player+0x2749 bit 0 is draw state (getter `0x2a2444`). IDs are not a contiguous 14-weapon ordinal.

The quest classes `uPlayerQuest00..15` follow the same numbers (no 05), so `uPlayerQuest15` is the Prowler (inference from the matching gap). It has its own action dispatcher (vtable slot 0x318 `0x1207e6c`, actions in `0x1208000..0x1210000`, its gather `0x120cf18` and fishing `0x120e88c`); 00..14 share `0x2cbfcc`. All share the add slots 0x360 `0x3015e0` and 0x364 `0x301784`.

The combat gate reproduces `0x3a5ed0(selector5, thirdArg1)` using byte at `*main[0x188ad90]+0x50`. States 4, 5, 6, 7, 9 block combat; 8 does not. Imported mState+0x4c is another field. Treat entry/exit transitions as state changes, including hold quarantine until release.

## Target camera tap

The local hunter is also reachable as `sFestaUnit` (cell `0x2126f48`) +0x58. Tap logic `0x27e970(hunter)`, 568 bytes, has one caller, `0x2a7b74` in the hunter update `0x2a79cc` (nothing branches to `0x27e974`; `0x2a7b78` reloads r0, so its result is unused).

It reads held/pressed +0x13f4/+0x13f8 (masked with `0x65f8ec()`), hold time f32 +0x1450, and a tap window f32 +0x145c in frames. A press with the window closed sets 12.0 (`movt #0x4140`). `0x53aa84(hunter, &timer, 1.0)` counts it down by frame time (`timer -= hunter[+0x1c] * step`, 1/60 s units).

It sets bits 0, 24 (unless session +0x6f == 1) and 6 of the request bitset +0x1434 (`0x285ea0` set, `0x285ec4` clear, `0x285ee8` test). The window is cleared at `0x27e9f4`, `0x27ea04`, `0x27eaf0`, and every frame when `0x18e50([0x184d750])` != 1 (gate below). Bits 0 and 24 clear at `0x2a7dd8`/`0x2a7de4` when `0x2e0b10(hunter)` == 1; bit 6 in `0x27eccc`.

When the window runs out with no press, the countdown path raises bit 0 and then bit 24 unless session +0x6f == 1 (`0x27eb2c` to `0x27eb48`). A press inside the open window raises the same pair (`0x27eacc` to `0x27eaec`).

Camera gates: cell `0x184d750` holds sFestaCamera (GOT slot `0x1838d90`). `0x18e50(cam)` and `0x18ffc(cam)` both require that `[cam+0x54]`, the current camera, has DTI `0x184d8b8` or derives from it. `0x18ffc` then returns `0x29a58(current)`, else 0. `0x18e50` also needs `0x29868(current)` != 0 and a non-zero `0x29a58(current)` object.

That object must pass vfunc +0x3f4 == 0, byte +0x1054 == byte +0x49 of the object in cell `0x188ca48`, and byte +0x75c0 != 0. It then returns that object's vfunc +0x3c4. So inside the tap logic, past `0x27e990`, `0x18ffc` is never 0 (read from the code, not run).

## Native processing order

`0x2a79cc` copies input, preprocesses modifiers, applies Arts, checks mode/camera gates, then classifies shared/weapon commands. Player logical held/previous/pressed halfwords are +0x13f4/+0x13f6/+0x13f8; full/high-bit fields +0x13fc/+0x1400/+0x1404. Prior presses +0x13fa/+0x1408 are already logical and must not be remapped twice.

General command flag 0 is shared with drawn states.

## Quest menu states

Quest-menu vtable `0x177aeb8`. Opener `0x66fecc` sets outer state +0x38 = 2 and inner +0x48 = 0 (root); inner 1 is a submenu. Outer state 1 is the closed menu, where chat runs through slot 0xc0. A direct `b`/`bl` scan finds 104 callers of the R accessor `0x65f93c` (indirect calls and literal-mask uses excluded).

## Empty-magazine reload

HBG/LBG classifiers `0x117eb58`/`0x118c920` emit X weapon flags 5/21 and A 4/20 at player +0x1424, separate from general flags +0x1414. Selected ammo slot/magazine/capacity are bytes+0x2b80/+0x2b82/+0x2b84. Native reserve getter `0x2ffba0` handles Normal 1's special reserve and signed slot quantities; do not derive reloadability from magazine alone.

`cPlCmdExec` 32 bytes contains four u16 action/condition fields, four s32 args, three s16 frame fields and padding. `cPlCmdTbl` 28 has length +8/capacity +12/row-pointer array +20; `cPlCmd` 24 has resource +8 and frame floats+12/+16/+20. Native table/row/resource conversion is at `0x26d42c`/`0x26d018`/`0x2731b4`. The evaluator has a 48-byte acceptance cache and checks row active byte+4.

Items and objects:

| Address / object | Meaning |
| --- | --- |
| `0x2693a0` / `0x2693ac` | Magazine / capacity getters |
| `0x2ffba0` | Selected-slot reserve; Normal 1 (item 100) returns 30; ammo item types 1/4 use the signed slot count |
| `0x287fec` / `0x19b670` | Pouch-slot lookup; slot limit 50, conditional gunner slots |
| `0x194228` / `0x192530` | `sItem::getItemData` / `rItemData` lookup: count at resource +0x64, entries +0x6c, stride 0x38 |
| `0x2ecefc` | Command eligibility; weapon-button kinds read flags +0x1424 |
| `0x2e9d54`, call at `0x2ea9a8` | Evaluator: frame gating before the predicate, then the same local Exec buffers and dispatches |
| `0x117fd30` / `0x118db40` | HBG/LBG category 0x10 action 1 reload (reserve, capacity, refill, animation); refill for actions 2/3 at `0x117ff0c` / `0x118dd04` |
| `0x11801d4` / `0x118df28` | HBG/LBG category 0x10 action 4 empty shot, animation 0x13f8 |
| Vtable / size | HBG `0x174bdc4`/0x3350, LBG `0x174c694`/0x3360, sItemPouch `0x173f5f8`/0x1ac (cell `0x18584b8`), sItem `0x173f560`/0x23d8, rItemData `0x173f44c`/0x70 (cell `0x18583a8`); command row/resource vtables `0x1747acc`/`0x1747f78`; `rPlBaseCmd` 128 bytes |

The evaluator's acceptance cache is at player +0x24b0. Both bowgun vtables inherit constant-false predicates at +0x234 (`0x280010`) and +0x62c (`0x26985c`). Shared classifier `0x27ca28` queues A at player +0x1444 as 0x200001 and starts the chord timer +0x1448; holding A commits 0x200004 two updates later (a released tap can commit earlier), and only then do the weapon classifiers emit flags 4/20. Command data is XFS inside `w04_m`/`w06_m` and their twelve style archives (2,663 rows); `w04.arc` and `w06.arc` hold none.

Reload postcondition helper `0x2ad534(p,1)` checks capability while skipping only the current-action restriction.
