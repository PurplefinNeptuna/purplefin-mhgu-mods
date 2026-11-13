# Other people's mods: what they touch and how to coexist

Players run our plugins beside these. Each entry says what the mod changes,
where that meets our code, and what to do. Facts come from the named mod's
files, logs and our runs; each line names its source in our docs. A build ID or
version named here is the one read; another build can differ.

## Rules that hold for all of them

- Never key behaviour off another mod's file name, ini keys, log lines or hook
  list: they change between builds (KatSmithy's file was renamed once).
  Detect a plugin by `app:/nativeNX/plugins/NAME.nro` existing, and read its
  memory only for one pinned build ID ([Plugin bridges](plugin-bridges.md)).
- Entry hooks that only run before or after the original accept a foreign
  Forge hook over the first eight bytes ([Hooks and lifetimes](hooks-and-lifetimes.md#chaining-onto-another-plugins-hook)).
- Read a foreign NRO's `movw`/`movt` constants and immediates to find its
  candidate hook sites before a run; they are candidates, not proven sites.
- Some mods install late (first update, or after a delay). A rule as weak as
  "install at the first update" loses a guarded site to nobody and wins it
  from them. WishFinder waits for the foreign hook and installs on top.

## Definitive Edition (MHGU Definitive Edition 2.0.0)

An IPS patch for main (`FB08F1D20FD1204FE7070672777F869B.ips`, 252 records)
plus its own `subsdk1` (loaded at main+`0x2715000`; main image `0x2147000`,
then subsdk0 `0x5ce000`). Source: `github.com/Scrimas/MHGU-Definitive-Edition`.

| Site | DE's word | Effect on us |
| --- | --- | --- |
| `0x3b7de8` (quest list job loop) and `0x3b2194` (in quest script query `0x3b2174`) | `e28ff790` (`add pc, pc, #0x2400000`) | Village Quests in Hub accepts that exact word there (`core::install::DEFINITIVE_EDITION`) |
| `0xb80fd0` (atlas lookup) | `e28ff771` (`add pc, pc, #0x1c40000`), to subsdk1 +0xabfd8 -> wrapper +0x2b6c -> +0xb610, which claims only ids with top 24 bits `0x4d4800` | WishFinder calls the lookup (ids 9 and 21) and still gets the game's record; it checks the record's id, size and texture word |
| `0x3a3874` (capture and break record, subsdk1 +0x72bc) | Serves its own monsters from `mhgu_de/*.bin` | See `mhgu-understanding` quest files |
| Its `0x3a3874` lookup (subsdk1 +0x72bc; module text size 0xf20bc, rodata 0xf3000, data 0x103000) | Checks sections <= 18, records <= 106, builds a 468-byte cBui cached per package (mHagiLv + 1 at 0x1913f4, records at 0x18ffd8), returns 0 with neither chunk (`work/wishfinder/DEFINITIVE_EDITION.md`) | |
| File hook (subsdk1 +0x5e44) | Serves only its own `FILE` chunk ids, 0 below `0x10700` | |

It appends 223 weapon process steps and 140 armor pieces to the loaded tables
(17061 rows in WishFinder's table), raises rItemData to 3055 records, adds 39
quests with stand-in bosses and three stages, and ships no `result.arc`. Read
tables from the loaded game or the layered RomFS, never from base-game counts.
Source: `mods/wishfinder/DEVELOPMENT.md` (Other mods in the checked windows,
Definitive Edition's stand-in quests), `mods/village-quests-in-hub/DEVELOPMENT.md`.

## KatLib, KatSmithy and UIScale

No released source; read from their NROs, inis, logs and our runs.

- **KatLib** (`katlib.nro`) offers `katlib_register_hook` and a pad filter
  (`katlib_register_pad_filter`) that can mask the game's menu-pressed word
  `sFestaPad+0x6bfc`. It keeps a stack of GUI instances being drawn (`0x4138`).
- **UIScale** edits a sprite in the uploaded matrix block at
  `*(ctx+4)+0x18bc` after the GUI publishers, keyed per instance (`0x13b8`),
  so the node's own matrix stays unscaled ([HUD movers](native-gui-extensions.md#hud-movers-gu-native-and-uiscale)).
  A copy node under the same instance gets the same transform.
- **On Eden** KatLib, UIScale and BetterBox all fail to load with
  `0x00000616`, because all three NROs have an all-zero build ID. On MHGURecomp
  they load.
- **KatSmithy** (`katsmithy.nro`, read at build b4171947…) replaces the
  smithy's weapon tree and armor lists with its own ImGui drawing (foreground
  draw list, the game's icons registered as textures), so there are no native
  rows to decorate there. It exports nothing beyond Forge's entry points, and
  its state is bss.
  - Guarded probes, registered through KatLib in its first update: `0x6f1ae8`
    (`E92D41F0 E24DD018`), `0x6f31d8`, `0x55e4f8`, `0x2831e0`. It refuses a
    target whose first words differ (its log says `NOT hooked`), so a hook of
    ours placed first disables its smithy. Install on top of it instead.
  - Unguarded sites built as immediates: `0x3de4f8` (nav), `0x6f7220` (upgrade
    screen driver), `0xbc0e98` (preview viewport), `0x86d34c` (pad poll),
    `0x6f2c90` (category setter), `0x70301c` (upgrade pay). Its earlier
    `smithyrise.nro` also hooked `0x86e1b4`, `0x86d588`, `0x86d7b4`, `0x86dc98`,
    `0x1c33c`, `0x1c358`, `0xa3da50`, `0xa37988` and `0xa4f420`.
  - Its ini (`katsmithy.ini` in the save folder) keeps `nav_direct`,
    `upgrade_direct`, `hide_locked`, `owned_icons`, `rotstick = 1` (right
    stick axis rotates the preview; the click is free).
  - It borrows a weapon id for one frame for the preview, so read its node from
    `forge_onUpdate` and require the same value twice.
  - Our bridge reads two bss words and hooks its `ImDrawList_AddRectFilled`
    GOT slot for one pinned build: `mods/wishfinder-katsmithy-bridge/DEVELOPMENT.md`;
    everything read from that build (draw helpers, tree records, armor cells) is
    in `work/wishfinder-katsmithy-bridge/FINDINGS.md`.

Source: `mods/wishfinder/DEVELOPMENT.md` (The smithy's other owners),
`mods/world-sharpness-gauge/DEVELOPMENT.md` (Following a rescaled bar, Open items).

## My Weapon Tree

Replaces weapon crafting, upgrades and armor crafting. It hooks the smithy
update `0x6f1ae8` in its `forge_onInit`, only if the entry still has its
original bytes. It leaves smithy state 5 and state 7 with +0x5c below 7 to the
game. Written in Rust; its wish list, lines, levels and armor pieces live in
its image at offsets that move per release (0.50, 0.55, 0.59, 0.60 are mapped).
Layout and the update procedure: `mods/wishfinder-mwt-bridge/DEVELOPMENT.md`,
`scripts/mwt_layout.py`.

## Others

| Mod | What to know | Source |
| --- | --- | --- |
| MHGU DPS Meter v1.2.0 | Holds Damage Numbers' hook 0 and 1 constants and window `0x276278`; chains over existing branches after the first update, so it stacks on ours without meeting our load check | `mods/damage-numbers/DEVELOPMENT.md` |
| Pixel Cheats "Hunter Speed x5" | Writes `sFestaUnit` (`0x2126f48`) +0x58 -> +0x14b0, the same local-hunter chain Lock-on Target uses | `mods/lock-on-target/DEVELOPMENT.md` |
| Eden cheat engine | Writes 12 times a second (`CHEAT_ENGINE_NS = 1000000000 / 12`), so a cheat that relies on a value running out between writes works on Eden and not on MHGURecomp, which writes every frame | As above |
| HD Project | Replaces atlases (not `HD_cmn_icon_GSM_NOMIP`) and `common_eng.arc`; Eden takes the alphabetically first of two replacements, so never ship a competing ARC: insert natively instead. Merge order Base -> HD Project -> Z_Balanced -> others | `mods/key-quest-markers/DEVELOPMENT.md`, `mods/modern-weapon-controls/DEVELOPMENT.md`, `docs/CLEANUP_HD_PROJECT.md` |
| Modern Weapon Controls (ours) | Ships a double-size `HD_cmn_icon_GSM_NOMIP` (1024x2048), so read atlas sizes from the header | `mods/wishfinder/DEVELOPMENT.md` |
| Wishlist | Key Quest Markers r20 ran beside it on Eden |
| Faster Field Hunter | Uses the centre popup and popup icons; leads from its code are in `mhgu-understanding` menus-and-screens | `work/wishfinder/POPUP_PLAN.md` | `mods/key-quest-markers/DEVELOPMENT.md` |
| MHGURecomp's own Village feature | Runs beside Village Quests in Hub (with its `hpscale.c`); the tester reports our mod fixes some of its problems | `mods/village-quests-in-hub/DEVELOPMENT.md` |
