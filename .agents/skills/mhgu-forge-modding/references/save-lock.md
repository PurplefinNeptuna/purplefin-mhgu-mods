# Save lock

How a plugin writes into the save without breaking the game's own save. The game facts behind it, with addresses, are in the understanding [Save data](../../mhgu-understanding/references/save-data.md). The research trail is `work/save-guard/notes.md`.

## Why

- Every game save op runs under the recursive mutex `sSavedata +0xe80`, on the save worker thread or inline on the requester.
- The SDK's commit (`nn::fs::detail::FileSystemAccessor::Commit`) refuses to commit while any file on the `savedata` mount is open for write, from any thread (2002-6457). The check runs inside the game, so it holds on every host.
- A plugin's write handle open while the game commits makes the game drop that save. The player sees "An unknown error has occurred." (status 9, `SaveLoadMsg` 64).
- Forge's `unmountSaveData` commits on every unmount, before any lock (`tools/forge-local/source/forge/fs.cpp`). The mount count itself is safe: it is always locked by `sSavedata +4`.
- Reads are harmless: a read handle never blocks a commit, and Forge's commit at a read's unmount just fails while the game writes.

## The rule

Hold `sSavedata +0xe80` from the mount to the unmount of every write, the commit included.

- Take it with `nn::os::TryLockMutex`, never `LockMutex`: the game thread must not wait on the save worker. When it fails, keep the work and try again later.
- Check the object first. Cell main+`0x2120320` must hold a pointer to an object whose first word is main+`0x17897f8` (sSavedata's object vtable). When it does not, write nothing and log it once.
- Unlock on the same thread that locked. `forge_onUpdate` runs after the game's update returns, so it is never inside an inline save op. The ImGui callbacks run from Forge's present hook, possibly on another thread; TryLock works there too.
- Both imports are in the game's SDK: `_ZN2nn2os12TryLockMutexEPNS0_9MutexTypeE` and `_ZN2nn2os11UnlockMutexEPNS0_9MutexTypeE`. MHGU Recomp binds plugin imports to the game's own SDK, so they resolve there as well.

## Recipe

Port WishFinder's, accepted on Eden in r148 and on MHGU Recomp in r149. Copy the whole path, not the constants alone.

- `mods/wishfinder/src/save_lock.rs`: `SaveLock::take() -> Option<SaveLock>` does the object check and the TryLock, logs once for a missing lock and once for a wait, and unlocks in `Drop`.
- `mods/wishfinder/src/config.rs`: `write_saved` takes the lock before `forge::fs::savedata::mount()` and lets it drop after `unmount()`. A busy lock returns `SAVE_BUSY`.
- The same file, `impl Files for Storage`: `mount()` takes the lock first and keeps it in the `Storage`, and `unmount()` releases it after unmounting. A busy lock reads as "storage not available yet", which the settings code already retries once a second.
- `mods/wishfinder/src/settings/builds.rs`: `write_or_keep` puts a file that met `SAVE_BUSY` on a pending list, and `write_pending` retries it once a second.
- Its log lines, humanized: "WishFinder waited for the game to finish saving before saving its own files" and "WishFinder can't find the game's save lock, so it won't save its files yet".

## Test

Make the native adapter enforce the rule, as WishFinder's does (`tests/adapter/fakes.py`, `setup.py`, `start.py`, `pins.py`).

- Give the plugin an sSavedata: its cell `GAME+0x2120320` points at an object whose first word is `GAME+0x17897f8`.
- Fake `TryLockMutex` and `UnlockMutex` on that object's `+0xe80`. A `game_saving` flag makes TryLock fail.
- Assert, in every case, that each write-mode `OpenFile` and each `CommitSaveData` happens while the lock is held, and that the unlock comes after the unmount.
- Add one case that changes something while `game_saving` is set: nothing is written then, and it is written on the next second.

A run proves the live lock when a write happens. The mod writes nothing on a failed object check, so a file timestamp inside the session shows the lock was taken.

## Our mods' save writers

forge-rs's `fs` module only reads (plus the counted mount), so each writer has its own `nn::fs` calls. In order of risk:

| Mod | Writes | From | Lock |
| --- | --- | --- | --- |
| Skin Loader | converted skin archives `SkinLoader/skins/FOLDER/*.arc` and `source.bin`, one skin per update (`src/saved.rs`); `skin_loader.ini` (`src/skins.rs`). It holds Forge's mount for the session | `forge_onUpdate` | r19 and later |
| WishFinder | `WishFinder/wishfinder.ini`, `wishfinder_quests.bin` (up to 4 MiB), `welcome.bin` (`src/config.rs`) | `forge_onUpdate` | r148 and later |
| Damage Numbers | `damage_numbers.ini` through forge-rs `Writer` with `ScopedMount` (`src/config.rs`) | free-render callback | not yet |
| Key Quest Markers | `key_quest_markers.ini` (`src/config.rs`) | its Plugin UI "Save & apply"; Purple-lib Mod Options close, saved from `forge_onUpdate` | r25 and later |
| Please do Better | `please_do_better.ini` (`src/settings.rs`) | `forge_onImGuiRender`, `forge_onImGuiFreeRender` | not yet |

- Skin Loader keeps the save mounted all session, and a mount opens no file. It takes the lock for each settings read or write. It also takes it for each update that may convert a skin or remove old copies.
- Damage Numbers uses forge-rs `Writer`, which commits inside. Take the lock before its `ScopedMount` and drop it after.
- The two remaining ini writers save only on an explicit Save, so their window is tiny; they come last, at each mod's next version.
- Purple-lib, Purple-lib Tester, World Sharpness Gauge, Modern Weapon Controls, Lock-on Target, Multiplayer Roaming, Shared Urgent Quests, Village Quests in Hub, imgui-meter and the MWT bridge write nothing into the save.

When a mod gains the lock, change its row here in the same commit.

## Open

- When the game itself saves (after quests, on area loads, from the menu) is not traced. It would show which plugin writes can ever meet a game save.
- `sFestaMain +0x34`, which picks the inline or the worker path, is unread at runtime. The lock covers both.
- Which thread presents frames on each host, and so runs the ImGui callbacks.
