# Leads read from other mods (unverified in our main)

## Leads from Faster Field Hunter (unverified in our main)

Read from that third-party mod's code (`work/wishfinder/POPUP_PLAN.md`); check each in the bytes before use.

- It queues item lines through `0x5b521c(window, 0, 9, item, ...)` (message 9, an item name). It keeps each request id, the window's counter +0x58 & 0x3ff, in a 32-slot ring. Each frame it takes the shown window (+0x70, id at +8) and acts when that id is in the ring and within 64 of the counter.
- Window timing floats at +0x64/+0x68 (hold, early; meaning open); a pane's x/y +0x90/+0x94 and scale +0xa0/+0xa4, a root's x/y +0x40/+0x44.
- Popup icons are `cUIOPopIcon` (DTI `0x189e698`, vtable from `0x1774710 + 0x70`). The setup is a `cUIObjectSetupParam` block (`0x570688`) with +0x38 = 0x4000000, +0x3c = 0 and a word from `0x163e4a0`. The icon is created by `0x65c1e0(parent, dti, param, 0x202)` (parent through `0x183a954`), and the block destroyed with `0x570688 + 0x88`. Slot +0x54 is normally `0x60eba0`.

## Charge Blade to 4G

The Charge Blade to 4G mod blocks events with `opcode=0x66 / bank=0` by player, command and frame (`references/MHGU-Charge-Blade-To-4G/docs/Plugins.md`). When it played a request through the player's sequence object (bank 0, attach 2), the game crashed (`docs/Presentation.md`). So prefer a swap to a new call: change the request on a copy of the event and run the executor on it.
