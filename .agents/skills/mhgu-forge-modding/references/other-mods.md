# Other people's mods: what they touch and how to coexist

Players run our plugins beside these. Each entry says what the mod changes, where that meets our code, and what to do. Facts come from the named mod's files, logs and our runs; each line names its source in our docs. A build ID or version named here is the one read; another build can differ.

## Rules that hold for all of them

- Never key behaviour off another mod's file name, ini keys, log lines or hook list: they change between builds (KatSmithy's file was renamed once). Detect a plugin by `app:/nativeNX/plugins/NAME.nro` existing, and read its memory only for one pinned build ID ([Plugin bridges](plugin-bridges.md)).
- Entry hooks that only run before or after the original accept a foreign Forge hook over the first eight bytes ([Hooks and lifetimes](hooks-and-lifetimes.md#chaining-onto-another-plugins-hook)).
- Read a foreign NRO's `movw`/`movt` constants and immediates to find its candidate hook sites before a run; they are candidates, not proven sites.
- Some mods install late (first update, or after a delay). A rule as weak as "install at the first update" loses a guarded site to nobody and wins it from them. WishFinder waits for the foreign hook and installs on top.

## Definitive Edition

Version 3.0.0 patches main through an IPS and adds its own `subsdk1`, quests, maps and items. Every patched site and its effect on our mods: [Definitive Edition](definitive-edition.md).

## KatLib, KatSmithy and UIScale

No released source; read from their NROs, inis, logs and our runs.

- **KatLib** (`katlib.nro`) offers `katlib_register_hook` and a pad filter (`katlib_register_pad_filter`) that can mask the game's menu-pressed word `sFestaPad+0x6bfc`. It keeps a stack of GUI instances being drawn (`0x4138`).
- **UIScale** edits a sprite in the uploaded matrix block at `*(ctx+4)+0x18bc` after the GUI publishers, keyed per instance (`0x13b8`), so the node's own matrix stays unscaled ([HUD movers](gui-masks-and-movers.md#hud-movers-gu-native-and-uiscale)). A copy node under the same instance gets the same transform.
- **On Eden** KatLib, UIScale and BetterBox all fail to load with `0x00000616`, because all three NROs have an all-zero build ID. On MHGURecomp they load.
- **KatSmithy** (`katsmithy.nro`, read at build b4171947…) replaces the smithy's weapon tree and armor lists with its own ImGui drawing (foreground draw list, the game's icons registered as textures), so there are no native rows to decorate there. It exports nothing beyond Forge's entry points, and its state is bss.
  - Guarded probes, registered through KatLib in its first update: `0x6f1ae8` (`E92D41F0 E24DD018`), `0x6f31d8`, `0x55e4f8`, `0x2831e0`. It refuses a target whose first words differ (its log says `NOT hooked`), so a hook of ours placed first disables its smithy. Install on top of it instead.
  - Unguarded sites built as immediates: `0x3de4f8` (nav), `0x6f7220` (upgrade screen driver), `0xbc0e98` (preview viewport), `0x86d34c` (pad poll), `0x6f2c90` (category setter) and `0x70301c` (the upgrade). It calls the upgrade directly from its tree with the window still in the Forge list's state 3, so the screen does not describe the upgrade. Its hook set has changed between builds.
  - Its ini (`katsmithy.ini` in the save folder) keeps `nav_direct`, `upgrade_direct`, `hide_locked`, `owned_icons`, `rotstick = 1` (right stick axis rotates the preview; the click is free).
  - It borrows a weapon id for one frame for the preview, so read its node from `forge_onUpdate` and require the same value twice.
  - Our bridge read two bss words and hooked its `ImDrawList_AddRectFilled` GOT slot for one pinned build. It is retired, since KatSmithy 8f93b and later call WishFinder themselves; see `mods/wishfinder-katsmithy-bridge/DEVELOPMENT.md` (in Git at `2888d72`). Everything read from that build (draw helpers, tree records, armor cells) is in `work/wishfinder-katsmithy-bridge/FINDINGS.md`.

Source: [WishFinder and other mods](../../../../mods/wishfinder/docs/worked/wishfinder-other-mods.md), [World Sharpness Gauge](../../../../mods/world-sharpness-gauge/docs/worked/sharpness-gauge.md).

## My Weapon Tree

Replaces weapon crafting, upgrades and armor crafting. It hooks the smithy update `0x6f1ae8` in its `forge_onInit`, only if the entry still has its original bytes. It leaves smithy state 5 and state 7 with +0x5c below 7 to the game. Written in Rust; its wish list, lines, levels and armor pieces live in its image at offsets that move per release (0.50, 0.55, 0.59, 0.60 are mapped). Layout and the update procedure: [the bridge](../../../../mods/wishfinder-mwt-bridge/docs/worked/mwt-bridge.md), `scripts/mwt_layout.py`.

## Others

| Mod | What to know | Source |
| --- | --- | --- |
| MHGU DPS Meter v1.3.1 | Chains over existing branches at Damage Numbers' hooks 0 and 1 (`0x170968`, `0x9d6f8`; Eden log), so it stacks on ours without meeting our load check | `mods/damage-numbers/DEVELOPMENT.md` |
| Pixel Cheats "Hunter Speed x5" | Writes `sFestaUnit` (`0x2126f48`) +0x58 -> +0x14b0, the same local-hunter chain Lock-on Target uses | `mods/lock-on-target/DEVELOPMENT.md` |
| Eden cheat engine | Writes 12 times a second (`CHEAT_ENGINE_NS = 1000000000 / 12`), so a cheat that relies on a value running out between writes works on Eden and not on MHGURecomp, which writes every frame | As above |
| HD Project | Replaces atlases (not `HD_cmn_icon_GSM_NOMIP`) and `common_eng.arc`; Eden takes the alphabetically first of two replacements, so never ship a competing ARC: insert natively instead. Merge order Base -> HD Project -> Z_Balanced -> others | `mods/key-quest-markers/DEVELOPMENT.md`, `mods/modern-weapon-controls/DEVELOPMENT.md`, `mods/hd-project/README.md` |
| Modern Weapon Controls (ours) | Ships a double-size `HD_cmn_icon_GSM_NOMIP` (1024x2048), so read atlas sizes from the header | `mods/wishfinder/DEVELOPMENT.md` |
| Faster Field Hunter | Uses the centre popup and popup icons; leads from its code are in [Leads read from other mods](#leads-read-from-other-mods-unverified-in-our-main) | `work/wishfinder/POPUP_PLAN.md` | `mods/key-quest-markers/DEVELOPMENT.md` |
| MHGURecomp's own Village feature | Runs beside Village Quests in Hub (with its `hpscale.c`); the tester reports our mod fixes some of its problems | `mods/village-quests-in-hub/DEVELOPMENT.md` |

## What KatSmithy and My Weapon Tree showed about smithy data

All 700 material groups KatSmithy logged in `work/wishfinder/runs/r10-recomp-2026-11-07.txt` (tables 03, 04, 06, 07, 08, 10, 12, 13) equal a create row's four items exactly. They are 163 distinct rows (`work/wishfinder-katsmithy-bridge/rise_vs_wcd.py`). The 2026-11-09 log has 25 distinct groups, and `work/wishfinder-katsmithy-bridge/rise_vs_path.py` reproduces this count:

- 22 equal the matching row of `work/wishfinder/inputs/weaponPath.bin` at the number and level named.
- 2 equal that number's create row at its own level.
- One is KatSmithy leaving one of four items out: `Clero Blade 1` omits 582x4, which the game's own row carries.

KatSmithy prints only the four items, never the row's pieces. Its `FULL layout type=N` is the weapon table N, not the equip type.

What My Weapon Tree 0.55 reads is built in memory, from that plugin's own code (copied in `mods/wishfinder-mwt-bridge/core/src/lib.rs::level`):

- Each class has a `{ptr, len}` pair of 80-byte level entries.
- An entry holds the name `{ptr,len}` at words 0/1, a craft list `{ptr,len}` at 6/7 and an upgrade list `{ptr,len}` at 10/11.
- List elements are 8 bytes, `{u16 id, u8 kind, u8 0, u32 count}`, with the parent link in `kind`. 0 is an item; 1..15 names the weapon that level comes from, in table `kind - 1`, at `id = number << 8 | level`.

That shape is MWT's reader's, not a fact about the RomFS files above.

**The window names the selected weapon, not its level.** What is reliable across a co-installed weapon-tree mod is category (`+0x5c` u16) and number (`+0x5c` high half, repeated at `+0x5e` u16). The game and the mod agree on those. The row's `+9` level byte belongs to whatever row the game last built for that slot.

Over 30 right-stick presses on 2026-11-09, the category and number matched KatSmithy's own `5C=`/`5E=` in every one. The row's level byte matched its tree level in none. That mod rewrites the displayed rows and leaves the level field alone (`DIRECT rows(+2) before: 0001 000B 001A … m2 after 6F53E4: 005B 0086 0085 0084 0008 0051 0000 0000 cur=4 page=4 5E=8`).

Untried alternative: the entry array at window `+0x1f80 + index*0x30` (`+0xcc` class, `+0xd0` level).

## Merge ownership and companions

Resource priority is Base -> HD Project -> Z_Balanced -> others. Later changed resources win whole; unchanged resources retain lower improvements. Same-path ARC conflicts need internal resource merging, not choosing one archive wholesale. Preserve language/controller/icon selections, matching font/texture pairs, and base companions. Choose one FPS/FOV variant. V4 donors are retired.

The HD cleanup's 7,931-file reproduction and 407-resource comparisons are static/deployment evidence from that operation. They do not establish current activation or every visual improvement. Read actual ownership/manifests before touching shared resources.

## Leads read from other mods (unverified in our main)

### Faster Field Hunter

Read from that third-party mod's code (`work/wishfinder/POPUP_PLAN.md`); check each in the bytes before use.

- It queues item lines through `0x5b521c(window, 0, 9, item, ...)` (message 9, an item name). It keeps each request id, the window's counter +0x58 & 0x3ff, in a 32-slot ring. Each frame it takes the shown window (+0x70, id at +8) and acts when that id is in the ring and within 64 of the counter.
- Window timing floats at +0x64/+0x68 (hold, early; meaning open); a pane's x/y +0x90/+0x94 and scale +0xa0/+0xa4, a root's x/y +0x40/+0x44.
- Popup icons are `cUIOPopIcon` (DTI `0x189e698`, vtable from `0x1774710 + 0x70`). The setup is a `cUIObjectSetupParam` block (`0x570688`) with +0x38 = 0x4000000, +0x3c = 0 and a word from `0x163e4a0`. The icon is created by `0x65c1e0(parent, dti, param, 0x202)` (parent through `0x183a954`), and the block destroyed with `0x570688 + 0x88`. Slot +0x54 is normally `0x60eba0`.

### Charge Blade to 4G

The Charge Blade to 4G mod blocks events with `opcode=0x66 / bank=0` by player, command and frame (`references/MHGU-Charge-Blade-To-4G/docs/Plugins.md`). When it played a request through the player's sequence object (bank 0, attach 2), the game crashed (`docs/Presentation.md`). So prefer a swap to a new call: change the request on a copy of the event and run the executor on it.
