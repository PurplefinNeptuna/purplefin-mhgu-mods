# Bridges to another plugin

A bridge is a plugin that reads another plugin's memory and passes what it finds to one
of ours, when the other plugin has no API. The worked example is
`mods/wishfinder-mwt-bridge`: it reads My Weapon Tree's wish list and calls WishFinder's
`sync`, from the table WishFinder hands it. Its DEVELOPMENT.md has the exact layout and the update procedure; this
page has the method. Prefer an API in the other plugin: a bridge breaks on every release
of it.

## Find the other plugin at run time

- Every NRO is loaded before any `forge_onInit`, so look plugins up in `forge_onInit` or
  later, never by load order ([Plugin order](hooks-and-lifetimes.md#plugin-order)).
- Our libraries are not looked up at all: a mod exports `wishfinder_on_register` or
  `purplelib_on_register`, and WishFinder (r70 and later) or Purple-lib calls it with a table of
  its functions ([API and builds](plugin-apis.md#a-library-that-calls-its-clients-purple-lib),
  `mods/wishfinder/API.md`). Do not use `nn::ro::LookupSymbol`: it resolves only the game's own
  modules and finds nothing in a loaded plugin, and Forge exports no plugin symbol lookup.
- A third-party plugin that exports a function of its own can be found by that name in
  its NRO symbol table (`mods/wishfinder-katsmithy-bridge/core/src/lib.rs::nro_symbol`, retired; in Git at `2888d72`, found
  KatLib's `katlib_version`).
- A plugin that exports nothing is found by its NRO build ID: walk `svcQueryMemory` for an
  R-X mapping whose first bytes are an NRO header (`NRO0` at +0x10) with the expected
  build ID at +0x40. Refuse any other build; offsets differ per build.
- Read its memory only after `svcQueryMemory` shows the whole range readable, and copy
  values out. Read a list twice and compare when the other plugin may be changing it.

## Read an NRO on the host

Header, all u32: +0x04 MOD0 offset, +0x18 file size, +0x20/+0x24 text offset/size,
+0x28/+0x2c ro offset/size, +0x30/+0x34 data offset/size, +0x38 bss size, +0x40 build ID
(32 bytes; the first 20 are the SHA-1). Segments load at their file offsets, so a file
offset is an offset from the loaded base. Relative relocations store base-0 offsets in
place: the file read as memory at base 0 already has every pointer resolved, which is
how the bridge's host test uses the real file.

## Find a static or table in Rust ARM32 code

Rust PIC code never stores a static's address as a word: it loads a literal and adds pc.

```
ldr rT, [pc, #lit]      ; word & 0x0f7f0000 == 0x051f0000, lit = imm12, U bit 23
add rD, pc, rT          ; word & 0x0fff0ff0 == 0x008f0000  -> address = add + 8 + literal
ldr rD, [pc, rT]        ; word & 0x0fff0ff0 == 0x079f0000  -> loads the word there
```

So a search for the address as a literal, ADR or section-base arithmetic finds nothing.
Decode the pairs instead (`mods/wishfinder-mwt-bridge/scripts/mwt_layout.py`,
`pc_relative`). Then:

1. Anchor on a string the other plugin prints near the data, such as a debug line
   ("goal(s), "). `bytes.find` gives its address in ro; the pairs give the code that
   computes it.
2. Walk back to the function's `push {…, lr}` (`word & 0xffffc000 == 0xe92d4000`). The
   pc-relative data addresses computed in that function are its statics; the
   `ldr rX, [rD, #imm]` offsets after each one show which fields it reads.
3. For tables, list every pc-relative data address in the whole text and keep those whose
   bytes have the shape you expect. Prove each predicate on the old build first: it must
   find the known address and nothing else.
4. Check field meanings against the game's own data where you can (the bridge matched
   every weapon row to `weaponProcessW*`), and record which facts are only inferred.

Rust layout facts that break naive shape checks: an empty slice or Vec stores a dangling
pointer equal to its element alignment (1, 2, 4 or 8) with length 0, and an empty `&str`
is pointer 1, length 0; `&str` is {ptr, len}; `Vec` is {cap, ptr, len}; static arrays of
records sit in the data segment and point into ro.

## Keep the bridge updatable

- Put every build-specific value in one file (the bridge's `core/src/lib.rs`) and make
  generators and tests read them from there.
- Ship a finder script that prints those values for any build, proven on the known build,
  and have `test` compare the code's constants with what the finder reads from the
  configured file.
- Keep the other plugin's file in `work/NAME/inputs/VERSION/`, never in a scratchpad.

## Call the other plugin's API safely

- Read the callee's queue and limits before calling it in a loop. A hand-off mailbox holds a fixed
  number of requests per update, and `forge_onUpdate` drains it once. Size it for the largest batch
  the data produces (`wishfinder_add`: one slot per list entry).
- Check every return value, and let it decide the log line and the tone. A partial write that plays
  the success tone looks like a working feature. For a toggle, a partial remove followed by the next
  press adds the rest back, so the list can never empty.
- A value the API hands over and something else later compares (a WishFinder key) needs its two ends
  read: which screens build it and what level base each uses.

## Share one list between plugins

When several plugins and the player add to one list, record who added each entry and remove only what nobody else holds. WishFinder keeps chain ends (`target`), the player's own entries (`own`) and plugin adds not yet classed (`fresh`, settled after an update with no requests); removing a chain end takes only steps that are not targets, not own and needed by no other target (`mods/wishfinder/core/src/store.rs`). A list without these marks loses a step the player listed alone when a chain that shares it goes. Test with the real data and the real producer, not a fake: two chains that share their first steps, removed in either order, with a shared step listed alone first, across a save and reload (WishFinder `weapon_path.rs` `two_chains_sharing_their_first_steps`).

## A plugin that guards its hook sites

Some plugins check the first words of each site before they hook it and refuse when the
words differ (KatSmithy logs `GUARD MISMATCH ... NOT hooked`). Read its guard list (an
embedded default ini, a save-folder ini) before planning any hook, and rank the options:

1. **No hook in the bridge.** If one of our plugins already runs at a site the other plugin
   also hooks, that plugin publishes the values as an export and the bridge only calls it.
2. A hook at a site the other plugin never guards.
3. A guarded site, only under the chaining rule of
   [Hooks and lifetimes](hooks-and-lifetimes.md): install after the other plugin's Forge
   branch (`0xe51ff004`) is there, or after a fixed wait when its probe is switched off.

Worked example, WishFinder and KatSmithy (`work/wishfinder-katsmithy-bridge/PLAN.md`): the
bridge needs the smithy node the player stands on. KatSmithy guards `0x6f1ae8`,
`0x6f31d8`, `0x55e4f8` and `0x2831e0`. Hooking the window factory `0x55e4f8` to capture
the window would be option 3 on a second guarded site. WishFinder's own hook at `0x6f1ae8`
already chains after KatSmithy's (KatSmithy logs `guard OK` and `installed` for all
four), so WishFinder exports `wishfinder_smithy_node` and the bridge takes no hook: option 1.
The guard evidence is then that no `GUARD MISMATCH` line appears in the run's log.

When the user asks for a version-agnostic bridge, read no state out of the other plugin's
NRO: the layout moves with every build (the My Weapon Tree bridge reads it only because it
pins one build ID), and KatSmithy also renamed its file
(`smithyrise.nro` to `katsmithy.nro`) and changed its hook set between builds.

If the user gives up version-agnostic instead, pin the build ID and read as little as possible. A bss word has no file bytes
but is readable at run time. Prefer a word the plugin derives from the value, so a check can reject a wrong build: KatSmithy's
selection detector `game + 0x1eef*id + 0x19919*level` fits one level or none. Have a finder script print the offsets for any
build (`mods/wishfinder-katsmithy-bridge/scripts/kat_layout.py`, retired; in Git at `2888d72`).
