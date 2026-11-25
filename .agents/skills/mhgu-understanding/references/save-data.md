# Save data

How the game mounts, writes and commits its save, and how a commit can fail. Main-relative offsets on 1.4.0, read from the bytes (`research dis`/`xref`, main's MOD0 relocations for import names) and the `sdk` module's symbol table. One run confirms the cell, the object vtable and the mutex: on Eden a plugin's object check and `TryLockMutex` on `+0xe80` succeeded and its write landed (run). The rest is static.

## sSavedata

- Cell `0x2120320` (GOT slot `0x183938c`). DTI `sSavedata`, parent `cSystem`, 4000 bytes, object vtable `0x17897f8`.
- Constructor `0x8771f0`: the save worker's thread object at **+0xd0c** (thread constructor `0x7bdbb0`, stack 0x8000, vtable `0x1789820`). It calls `InitializeMutex(+0xe80, recursive = true, 0)`, clears `+0xe94` and sets `+0x18 = 1`. Nothing else writes +0x18.
- The mount count is `+0xf1c`. Mount `0x878da0` and every unmount lock the mutex `+4` around it when `+0x18` or the global byte main+`0x212041c` is set. +0x18 is always 1, so the count is always locked.
- Other fields: busy `+0x20`, write status `+0x24`, pending op `+0xe94`, worker event `+0xe64`, path `+0xe98`.

## Save ops

`0x878da0` is the only `MountSaveData` call. The game's other mounts are `MountRom` and `MountSaveDataReadOnly`. Eight functions call it:

| Function | Op | Reached from |
| --- | --- | --- |
| `0x8778cc` | 1 | worker; requester `0x8776fc` |
| `0x877c20` | 2, write: mount, mkdir and commit `0x878f64`, MtFile mode 0x13, write, close, `CommitSaveData`, unmount | worker; requester `0x8775f4` |
| `0x878070` | 3, delete | worker; requester `0x877520` |
| `0x8782c4` | 4 (walk `0x879310`) | worker |
| `0x878414` | 5, rename (`RenameFile` via `0x829b4c`) | worker |
| `0x878638` | 6 | worker |
| `0x878950` | 7 | worker |
| `0x878c24` | file-exists query (`0x82b004`); no write, no `+0xe80` | `0x3e453c` |

- The five `CommitSaveData` calls (thunk `0x13f0db4`) are in ops 2, 3 and 5 and their helpers `0x878f64` and `0x8790a4`.
- The worker loop `0x878a68` (worker vtable slot 0x20) runs `WaitEvent(+0x158)`, then `LockMutex(+0x174)`. It switches on `+0x188` (1 to 7; 8 exits), clears it and unlocks. Worker +0x158, +0x174 and +0x188 are sSavedata +0xe64, +0xe80 and +0xe94.
- A requester returns 8 when busy or when `+0xe98` is empty. It sets busy and sleeps 1 ms (`SleepThread(0xf4240)`) while `+0xe94` is set. Then it runs the op inline under `LockMutex(+0xe80)` when `sFestaMain +0x34` is set (cell `0x2126764`), or posts it to the worker (`+0xe94 = 2`, `SetEvent(+0xe64)`).
- So every game save write runs under the recursive mutex `sSavedata +0xe80`, on the worker or inline on the requester's thread.

## Nothing else writes the save

- The fs write imports (`WriteFile`, `CreateFile`, `SetFileSize`, `FlushFile`, `DeleteFile`, `RenameFile`, `CreateDirectory`, `DeleteDirectoryRecursively`) are called only from the MtFile layer `0x8296e0`..`0x82b674` (vtable near `0x1787c00`).
- The strings `savedata:` (`0x156e00b`) and `savedata:\%s` (`0x1571ea5`) are used only by the ops, their helpers and the path translators `0x8292ec` (`MtFile::canonicalizePath`), `0x82a66c` and `0x83e7f8`.
- The MtFile temp writer `0xbc9c5c` (`%s\temp\%s`) is `sFestaResource` slot +0x2c, under the root `\nativeNX` (read-only RomFS). No call through the resource cell uses that slot.

## A commit fails while any file is open for write

- The SDK's `nn::fs::detail::FileSystemAccessor::Commit` (`sdk+0x54578`) walks the mount's open files (`[accessor +0x24]`). If any has write mode (`tst #2`), it returns `0x327202` (2002-6457, write-mode file not closed) and commits nothing.
- The check is in the game's own SDK, before any request reaches the host. The open-file list belongs to the mount name, so a write handle on any thread blocks every commit on `savedata`.
- On a failed commit, op 2 stores status 9 at `+0x24` (the branch at `0x877ea8`; 2002-6457 is none of its special cases).
- The save flows (`0x3dfafc`..`0x3e64f0`, for example `0x3e1974`) read `+0x24` after an op. A nonzero status picks a message from a nine-entry table: status 4 gives 93, statuses 0 to 8 otherwise give 64, and anything above 8 gives 64.
- The message is `0x55bc4c(cell, 8, id)`, shown through the popup `0x65f190`. Table 8 matches `SaveLoadMsg` (`resident_<lang>.arc`), the only message file whose 64 and 93 are save messages. 64 reads "An unknown error has occurred." and 93 "The save data is corrupt."

So a commit refused because some other code held a write handle shows the player "An unknown error has occurred.", and that save is not committed. Other readers of `+0x24`, not read here: `0x2c7b8`, `0x6a97ac`, `0x6a9cb8`, `0x6aa094`.
