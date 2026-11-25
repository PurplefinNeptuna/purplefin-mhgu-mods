# Read game files and textures from a plugin

Use this when a plugin needs the game's data (tables, text, textures) at run time instead of shipping a copy. WishFinder is the worked example (`mods/wishfinder/src/config.rs` `GameFiles`, `core/src/{quest_build.rs,texture.rs,imitation.rs}`). File formats (ARC, GMD, `rTexture`, block-linear) are game facts and live in `mhgu-understanding` [File layouts](../../mhgu-understanding/references/file-formats.md#file-layouts).

## Prefer reading the user's files over shipping copies

- Shipping an extracted texture or table copies Capcom data into a release. Read it from the user's game at run time instead.
- `app:/nativeNX/...` is the RomFS **with every mod's layer**, so you read what the player's game loads: HD Project atlases, Definitive Edition tables, a double-size Modern Weapon Controls icon atlas. Take sizes from the file header, never from the base game, and expect extra rows.
- A table built from the files is cached beside the save (`savedata:/WishFinder/wishfinder_quests.bin`). Its fingerprint covers every file read (path and size) and the table and cache versions (`quest_build::Fingerprint`), and it is rebuilt when either changes. A new table format raises the versions (WishFinder's version 4 added reward percents). So saved tables are built again without the user deleting anything.
- When the game already holds the data in memory, read it there instead. But some tables are empty in a quest (equipment message cell `0x1856b1c` is 0 in a quest), so copy what you need outside quests.

## Files: Forge first, then the SDK

Forge 1.5.1's `fs` module has the counted save mount, the RomFS and save mount points, `forge_fs_fileExists`, and forge-rs adds `mt::fs` file readers. Forge 2.0.0 adds `forge_fs_openFile`, `getFileSize`, `readFile(handle, offset, …)` and `closeFile` (forge-rs `forge::fs::File`, `read_into`). Neither has writing, directory listing, free-space query or decompression.

For those, call the game's `sdk` exports, by mangled name (`config.rs` has the set): `nn::fs::OpenFile/ReadFile/GetFileSize/CloseFile`, `OpenDirectory/ReadDirectory/CloseDirectory`, `GetFreeSpaceSize`, `nn::util::DecompressZlib`, and the SDK's zlib 1.2.8 as `nnutilZlib_inflateInit_/inflate/inflateEnd`. `verify` checks each one against the copied `sdk` exports.

ABI notes, verified for ARM32:

- A `FileHandle` and `FsContext*` are one 32-bit word (not the ARM64 nnheaders size).
- i64 offsets take an even register pair or 8-aligned stack slot.
- `DirectoryEntry` is 0x310 bytes: name 0..0x301, type byte 0x304 with 1 = file, s64 size 0x308.
- `z_stream` is 56 bytes.

Rules:

- Wrap every SDK file use in `ScopedAutoAbortDisabler` and restore the thread's FS context afterwards (`Storage` guard), or a missing file aborts the game.
- Close every successful open on every path (a Drop guard). Close handles before the context is restored.
- Check sizes before allocating; refuse short reads and ranges past the file.
- Give zlib Forge's `malloc`/`free` (`zalloc`/`zfree`) so its state is on the shared heap whatever the SDK's default is. `DecompressZlib` (sdk `0x42024`, worker `0x42054`, window bits 15) needs a 64 KiB work buffer (bump-allocated by sdk `0x41ee0`, NULL past its end) and fails safely when it is short; it reports no length.
- Do file work from `forge_onUpdate` or a worker step, never in a hook or a render callback. Split a large build over updates (WishFinder's quest table: about 1,850 files over about 232 updates) and show progress.

## Writing into the save

- Keep a plugin's files in its own folder, `savedata:/NAME/` (WishFinder, Skin Loader); never at the save's root. Moving an old root file: read it as a fallback, write it into the folder, delete the root one on save, or MHGU Recomp's `run.sh` copies it back.
- Writes, directories and space: `nn::fs::CreateDirectory`, `DeleteFile`, `DeleteDirectoryRecursively`, `GetFreeSpaceSize`, then `nn::fs::CommitSaveData`; check the free space before a large write (Skin Loader leaves a skin off below its size plus 1 MiB). Write a stamp file last and commit, so a cut-off write is rebuilt next launch.
- The save is not mounted while the game's resource loaders run (probed on Eden and MHGU Recomp). To load from it then, hold Forge's counted mount for the session. Forge counts with the game's own counter (`sSavedata +0xf1c`): the game's save routines commit while the count is held and unmount only at 0, so a held count leaves the game's saving alone (Skin Loader r15 to r18).
- Hold the game's save mutex `sSavedata +0xe80` from the mount to the unmount of every write. The SDK refuses a commit while any file on the mount is open for write, from any thread. A plugin's open write handle then makes the game drop its own save with "An unknown error has occurred." Forge's unmount also commits, so the lock spans it (Forge `fs.cpp`). Take it with `nn::os::TryLockMutex` and try again later when it fails: the game thread must not wait on the save worker. WishFinder's `src/save_lock.rs` does this ([Save data](../../mhgu-understanding/references/save-data.md)).
- To make the game load a file from the save, use the resource path filter (`sResource +0x13040`, in the understanding [How the resource manager loads and shares files](../../mhgu-understanding/references/file-formats.md#how-the-resource-manager-loads-and-shares-files)). Keep it cheap: it runs on every load (Skin Loader's costs 190 instructions on a path it leaves alone).

## Big entries: stream, cut, drop

An 8 MiB atlas must never sit in memory whole. WishFinder's `inflate_each` reads and inflates 64 KiB at a time and hands each piece to a sink. The texture sink (`core::texture::Cut`) keeps only the texels or BC blocks its rectangles cover, decodes those to RGBA, and averages a larger-than-base texture back to base size. Its peak for twelve pieces of three atlases is under 1 MiB in one update.

## Texts in the game's language

- The game's language is byte `+0xa5` of the session: `*(base + 0x188ca48) + 0xa5`, one load from the cell. `cQuestData::getMessage` `0x37a2e4` reaches the same cell through GOT word `0x1838bb4`, so reading from `0x1838bb4` takes two loads (WishFinder `native::session_language`: `cell(SESSION_CELL)` then `memory::word`). One load from the GOT word reads a static byte that never says Chinese (Skin Loader r17). Values, folder codes and the Korean patch check (scan the GMD strings only) are in the understanding [File layouts](../../mhgu-understanding/references/file-formats.md#file-layouts).
- Copy a working reader whole, helpers included, not its constants. Port WishFinder's `session_language` and `imitation::korean` as they are, and test the port on the real tables. Skin Loader r17 showed Korean in a Chinese game. It had pulled a constant out of the helper that dereferences it, and used a byte scan in place of the string reader.
- Read GMD strings from `resident_<code>.arc` (or the language's own archive) by index. Check an index is the same in all seven languages by string count before relying on it.
- Keep every string you hand to the game alive for the session: its UI keeps the address. Keep every published set, because a language change publishes a new one while old addresses are still held.
- Plugin text of your own goes in per-language files shipped beside the NRO (`romfs/nativeNX/plugins/NAME/lang/`), with English compiled in as the fallback. Every language ships in the same change.

## CJK text in an ImGui window

Forge's Roboto has no CJK glyphs, and the host fallback fonts differ.

Ship a subset of Noto Sans CJK beside the NRO, one per language (OFL 1.1, license file and credit in the package). Cut it with `pyftsubset` to printable ASCII plus every character the language's file shows (Skin Loader `scripts/cjk_fonts.py`: 58 to 83 KB each). Have `verify` refuse a font whose cmap lacks one (`scripts/font_cmap.py`, no fontTools needed).

Load it on first use with `ImFontConfig` flag `NoLoadError` (a missing file returns null instead of asserting), push it with `igPushFont(font, 0.0)` around the window, and forget it in `forge_onImGuiInit`, since a new context has none of the old fonts. Names from outside the subset (a skin's `skin.json`) show boxes.

## A message once per launch

Skin Loader's notice (`src/notice.rs`) and WishFinder's welcome window: build the text in `forge_onUpdate` when the data and the game's language are ready and the player is in the game (local hunter nonzero), and draw it in `forge_onImGuiFreeRender`. While it is open, call Purple-lib's `hold_input` every frame so the game ignores the buttons and the closing press.

Close on a new press of A or Enter read with Forge's input (MHGU Recomp feeds no ImGui navigation, [Input](input-and-keybinds.md)); a button already held on the first frame does not count. Pair every Begin, table, wrap and font push with its end whatever Begin returns.

## Turning texture pieces into ImGui textures

- Pack pieces into one small atlas (WishFinder: 256x144) and register one texture; free the CPU pixels once the texture holds them.
- Cost: Forge's NVN backend keeps RGBA pixels and a GPU copy, 8 bytes a texel of the shared heap. Glyph sizes are baked into Forge's shared font atlas for the session, so use a few fixed font sizes.
- Release: ImGui counts `UnusedFrames` only for its own atlases. Set `WantDestroy` and `UnusedFrames` yourself a few frames after the last draw, then unregister and destroy once the status reads `Destroyed` (`welcome::release`). See [Rendering](rendering-and-settings.md#assets-and-context-replacement).
- The game multiplies vertex colour by the texel; ImGui does too. Grey art tinted by a vertex colour matches the game's own tints.
- On MHGURecomp every ImGui object is a mirror in a shared 8192-slot pool ([Runtimes](runtimes.md#imgui-on-each-host)); destroy what you create.

## Native textures instead

A native GUI node draws a texture the row's resource already loads, so it needs no file read: find the loaded descriptor and logical atlas coordinates ([Art, colour and paired nodes](gui-insertion.md#art-colour-and-paired-nodes)). Atlas lookup `0xb80fd0` returns the loaded record for an id; Definitive Edition's IPS hooks that site and claims only its own ids (WishFinder *Other mods in the checked windows*), so check the record's id, size and texture word.

Sources: `mods/skin-loader/{DEVELOPMENT.md,src/saved.rs,src/notice.rs,src/language.rs,scripts/cjk_fonts.py}`, `mods/wishfinder/{DEVELOPMENT.md,src/config.rs,src/settings/mod.rs,src/settings/builds.rs,core/src/quest_build.rs,core/src/texture.rs,core/src/imitation.rs}`, `mods/damage-numbers/DEVELOPMENT.md` (asset files), `tools/forge-local/source/forge/graphics/imgui_impl_nvn.cpp`.
