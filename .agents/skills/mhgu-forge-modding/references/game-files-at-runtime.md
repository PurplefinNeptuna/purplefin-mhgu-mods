# Read game files and textures from a plugin

Use this when a plugin needs the game's data (tables, text, textures) at run
time instead of shipping a copy. WishFinder is the worked example
(`mods/wishfinder/src/config.rs` `GameFiles`, `core/src/{quest_build.rs,texture.rs,imitation.rs}`).
File formats (ARC, GMD, `rTexture`, block-linear) are game facts and live in
`mhgu-understanding` [Resources and tooling](../../mhgu-understanding/references/resources-and-tooling.md#formats-a-plugin-reads).

## Prefer reading the user's files over shipping copies

- Shipping an extracted texture or table copies Capcom data into a release.
  Read it from the user's game at run time instead.
- `app:/nativeNX/...` is the RomFS **with every mod's layer**, so you read what
  the player's game loads: HD Project atlases, Definitive Edition tables, a
  double-size Modern Weapon Controls icon atlas. Take sizes from the file
  header, never from the base game, and expect extra rows.
- A table built from the files is cached beside the save
  (`savedata:/wishfinder_quests.bin`) with a fingerprint of every file read
  (path and size), and rebuilt when it changes.
- When the game already holds the data in memory, read it there instead.
  But some tables are empty in a quest (equipment message cell `0x1856b1c`
  is 0 in a quest), so copy what you need outside quests.

## Files: Forge first, then the SDK

Forge 1.5.1's `fs` module has the counted save mount, the RomFS and save mount
points, `forge_fs_fileExists`, and forge-rs adds `mt::fs` file readers, but no directory listing, offset read, free-space query
or decompression. For those, call the game's `sdk` exports, by mangled name
(`config.rs` has the set): `nn::fs::OpenFile/ReadFile/GetFileSize/CloseFile`,
`OpenDirectory/ReadDirectory/CloseDirectory`, `GetFreeSpaceSize`,
`nn::util::DecompressZlib`, and the SDK's zlib 1.2.8 as
`nnutilZlib_inflateInit_/inflate/inflateEnd`. `verify` checks each one against
the copied `sdk` exports.

ABI notes, verified for ARM32: a `FileHandle` and `FsContext*` are one 32-bit
word (not the ARM64 nnheaders size); i64 offsets take an even register pair or
8-aligned stack slot; `DirectoryEntry` is 0x310 bytes (name 0..0x301, type byte
0x304 with 1 = file, s64 size 0x308); `z_stream` is 56 bytes.

Rules:

- Wrap every SDK file use in `ScopedAutoAbortDisabler` and restore the thread's
  FS context afterwards (`Storage` guard), or a missing file aborts the game.
- Close every successful open on every path (a Drop guard). Close handles
  before the context is restored.
- Check sizes before allocating; refuse short reads and ranges past the file.
- Give zlib Forge's `malloc`/`free` (`zalloc`/`zfree`) so its state is on the
  shared heap whatever the SDK's default is. `DecompressZlib` (sdk `0x42024`, worker `0x42054`, window bits 15) needs a 64 KiB
  work buffer (bump-allocated by sdk `0x41ee0`, NULL past its end) and fails safely when it is short; it reports no length.
- Do file work from `forge_onUpdate` or a worker step, never in a hook or a
  render callback. Split a large build over updates (WishFinder's quest table:
  about 1,850 files over about 232 updates) and show progress.

## Big entries: stream, cut, drop

An 8 MiB atlas must never sit in memory whole. WishFinder's `inflate_each`
reads and inflates 64 KiB at a time and hands each piece to a sink. The
texture sink (`core::texture::Cut`) keeps only the texels or BC blocks its
rectangles cover, decodes those to RGBA, and averages a larger-than-base
texture back to base size. Its peak for twelve pieces of three atlases is
under 1 MiB in one update.

## Texts in the game's language

- The game's language is byte `+0xa5` of the session (cell `0x188ca48`,
  reached through GOT word `0x1838bb4`), as `cQuestData::getMessage` `0x37a2e4` reads it (WishFinder
  `native.rs` `language`). Values and folder codes are in the understanding
  resources reference.
- Read GMD strings from `resident_<code>.arc` (or the language's own archive)
  by index. Check an index is the same in all seven languages by string count
  before relying on it.
- Keep every string you hand to the game alive for the session: its UI keeps
  the address. Keep every published set, because a language change publishes a
  new one while old addresses are still held.
- Plugin text of your own goes in per-language files shipped beside the NRO
  (`romfs/nativeNX/plugins/NAME/lang/`), with English compiled in as the
  fallback. Every language ships in the same change.

## Turning texture pieces into ImGui textures

- Pack pieces into one small atlas (WishFinder: 256x144) and register one
  texture; free the CPU pixels once the texture holds them.
- Cost: Forge's NVN backend keeps RGBA pixels and a GPU copy, 8 bytes a texel
  of the shared heap. Glyph sizes are baked into Forge's shared font atlas for
  the session, so use a few fixed font sizes.
- Release: ImGui counts `UnusedFrames` only for its own atlases. Set
  `WantDestroy` and `UnusedFrames` yourself a few frames after the last draw,
  then unregister and destroy once the status reads `Destroyed`
  (`welcome::release`). See [Rendering](rendering-and-settings.md#assets-and-context-replacement).
- The game multiplies vertex colour by the texel; ImGui does too. Grey art
  tinted by a vertex colour matches the game's own tints.
- On MHGURecomp every ImGui object is a mirror in a shared 8192-slot pool
  ([Runtimes](runtimes.md#imgui-on-each-host)); destroy what you create.

## Native textures instead

A native GUI node draws a texture the row's resource already loads, so it needs
no file read: find the loaded descriptor and logical atlas coordinates
([Native GUI extensions](native-gui-extensions.md#art-colour-and-paired-nodes)).
Atlas lookup `0xb80fd0` returns the loaded record for an id; Definitive
Edition's IPS hooks that site and claims only its own ids (WishFinder
*Other mods in the checked windows*), so check the record's id, size and
texture word.

Sources: `mods/wishfinder/{DEVELOPMENT.md,src/config.rs,src/settings.rs,core/src/quest_build.rs,core/src/texture.rs,core/src/imitation.rs}`,
`mods/damage-numbers/DEVELOPMENT.md` (asset files), `tools/forge-local/source/forge/graphics/imgui_impl_nvn.cpp`.
