# Where quest lists come from

## Where the quest list comes from

Bytes unless marked upstream, which means read in a recompilation project's source and not reproduced here.

| Step | Where | Facts |
| --- | --- | --- |
| Area type | Session cell `0x188ca48` (through GOT word `0x1838bb4`), byte +0x4c | 0 Hub, 1..6 villages, 7 Pub (upstream). A quest writes 255 there (`0x6be048`, old value kept at +0x50); `0x6be09c` restores it |
| List job | Start `0x3b7fd8`, thread `0x3b7cf8`, loop `0x3b7de8`, finished `0x3b8070` | Frees and reallocates the 3456-byte list at +0x24, reads the area byte once. +0x28 count, +0x2c cursor, +0x30 state (0 load, 1 wait, 2 finished); at most 32 unready, 864 total. Starting a job destroys a running one's thread object |
| Filter | `0x3b8090(list, quest, type)`, one caller `0x3b7ea8` | Decides whether a quest is listed for the area type (`cmp r2,#7`) |
| Quest file | `loc\quest\questData\questData_%07d` (`0x1563ab7`), DTI `rQuestData` cell `0x188ab98` (GOT `0x183c984`), resource manager cell `0x2126a64` (GOT `0x1839450`), read in the job at `0x3b7e64`/`0x3b7e58` | Loaded through `sResource::create(this, dti, path, mode)` (vtable +0x30, `0xbcad18`): mode bit 0 `loadBlocking` `0xbcb0d0`, bit 1 `loadAsync` `0xbcb6bc`. A cached hit raises the count at +0x48. An async load is not ready when `create` returns |
| Lookup | `0x3ba50c(selector, quest)`, 19 callers | The scan at `0x3ba56c` skips an entry until its +0x50 bit 0 is set (loaded), then compares record +8 |
| Selector | Cell `0x188ae38` (GOT `0x1838d74`, caller `0xfdb8`) | Holds the lists, urgent pools and Special Permit groups below |
| Categories | Build `0x3b85d8`, fill `0x3bb318`, get `0x3bc96c` (reads area byte +0x4c, range 0..7), rebuild `0x3ba8fc` (caller `0x6bcafc`) | Quest lists per category; pool index for an urgent depends only on quest-ID ranges (`0x3bc5f0`), so host and client agree |

Availability `0x54af8c(id, 0xff, 0)` returns 1 for DLC IDs (`0x3b9870`). For other quests it asks the progression script `0x3b2174`, whose module is at +0x8d0 of the cell behind it: with the module null, `0x3d7ee4` writes answer 0 at `0x3d7ffc` unless its +0x8dc cache holds the flag.

The special-encounter bit at owner +0x35d4 is saved by `0x51d94c`, and which record of a pair a save enables differs by save. So the result depends on when it is asked. `aResult` slot 7 `0x6a1fd4` loads the module and slot 9 `0x8e48` unloads it. `aVillage` loads it at `0x10618` (`0x506fec`) and unloads it at `0x106a0`.

An area load's list job can run while the module is still unloaded. The job `0xfc1c` is the stage's loading method (slot 0x74, also called from `0xd8f0`), and `0x10548` is a later slot. That is inference from the order; no run has logged it. It also needs the special encounter bits (above). It reads the local save, never the host's.

The module is rCommonScript `script\check_quest_unlocked` (`loc/arc/village/common.arc`), run by query `0x3d7e90` through the script VM `0x3d17f8` with the quest in `[WORK0]`: each case requires quests cleared and story flags (save `+0x500`) set.

NPC talk tables (`loc/arc/npc/talk.arc`) set those flags when their quest and flag conditions hold, which is how a clear followed by dialogue unlocks a quest. Opcodes, record layouts and the talk evaluator are in [Unlock script and talk tables](#unlock-script-and-talk-tables). In 1.4.0 every key quest's unlock needs only key or urgent quests; 479 other quests unlock something. One rank-up urgent needs more: The Scorching Blade (601, Village ★5) needs 504, 508 and 510 and their chief request lines 219, 220, 224, 225, 229, 230, 318, 323 and 328, none in a key category.

Felyne ingredients are granted only by a talk row's mAction2 (switch `0x247c58`, `0x3f1380`), on 28 quests' clears. Hunter Arts come from two loops, both gated per art by check `0x3efb30`: talk rows (`0x3f0c3c`) and a loop with no talk row (`0x3ea6e8`). The checks need 78 quests' clears; see [Hunter Art grants](#unlock-script-and-talk-tables).

## Downloaded event quests

The game lists event quests (lists 15..17) only while their row is open: `0x54dcac` starts a save job (`0x3dfa2c`), then `0x3bc234(selector, code)` lists the job's set at `[[0x188ad90] + 0xb4]`. That set is empty at any other time, so memory does not show every event quest.

They live in the game's save file `system`. Header word 0x30 gives a shared section (`0xb281`), whose +0x4618 starts 200 slots of 0x1c00 bytes, each `{u32 quest, u32 size, ARC}`. A tester's save had 165 used, 46 of them G rank, and the game lists those 46. The rest of `system`: three hunter sections, at the offsets header words 0x34, 0x38 and 0x3c give ([Save data](save-data.md#the-system-files-header)); end word 0x1c = 0x4eb898.

No code constant was found for 0x4618 or 0xf899 (movw search). Offset and slot count were read from saves, not from code, so count a slot only when it holds the ARC magic and an event ID. Listing rule (`0x3bc234`): millions digit 1, ten-thousands digit not 2, and `(id / 100) % 100` is 0, 1 or 10 for star codes 1, 3, 4.

## Unlock script and talk tables

A quest is unlocked by the first case of the unlock script labeled with it, or through a conversation that sets a flag such a case loads, directly or through further conversations. Level-gated ingredient rows depend on no clear. The 92-art base set on flag 847 has no quest condition, but each of its arts still passes check `0x3efb30` first, and many cases there load a quest clear. Only mAction1 writes flags; mAction2 rows look like item and count (`1, 1875, 3`). The script module loads only in some scenes and talk tables per NPC.

| Source | Verified behaviour |
| --- | --- |
| `script\check_quest_unlocked` (rCommonScript, `village/common.arc`) | sCommonScript (0x8e8 bytes) query 0x3d7e90 runs it with the quest in `[WORK0]`, cached per quest at +0x8e0. Records: u32 index, u8 command, two strings; header f32 1.0, count. |
| VM 0x3d17f8 | Command - 1 indexes the jump table at 0x3d5874. 0x0e labels a case (compare at 0x3d1a0c); a body ends at 0x23 (or 0x24 at a switch boundary). 0xa1 requires A == B, 0xa7 A >= B (failure returns 0 at 0x3d5cac); 0x03 returns 1 (0x3d5cdc). Every body returns, so the first matching case decides. |
| VM loads | 0x75..0x78 load quest cleared (0x523da4); 0x40..0x43 load story flag bit P of `[0x18390e0]+0x500`; 0x50 adds, 0x52 sets. Loaded values are only compared == 1 or counted >= N, so a clear never locks a quest. 0x7e loads the Hub/G tier (+0x3e2 of the progression record, handler 0x3d234c). 0x9e and 0xa8 load other values (handlers 0x3d245c, 0x3d4f94, unread); 0x07, 0x13 and 0x16 share branch-style handlers (0x3d187c, 0x3d1b44, unread). |
| rNpcTalkData (`npc/talk.arc`, 171 tables) | 37-byte packed records (cNpcTalkData fields). Quest = param plus `[10000,100000,40000][fixed-10002]` for fixed 10002..10004 (table via literal at 0x2464f0). Action switch at 0x2479d8 on mAction1: 1 and 4 set flag mAction1Param in the same array (0x247a14), 2 clears; mAction2 writes no flag. |
| Tag evaluator 0x2451c8 | Returns 1 when a tag holds: 1 flag set, 2 not set, 11 quest cleared, 12 not cleared, 13 Village key check (`0x526d28` → `0x3b1a18`), 14 Hub/G key check (`0x526d48`). Kinds 16..18 share the handlers of 1, 2, 11; 30..33 always hold. |
| Hunter Art grants | Two loops set an art's owned bit (+0xd24) when the player lacks it (0x524040) and check 0x3efb30 returns 1. Grant 0x3f0c3c serves talk rows: callers 0x3f1020..0x3f12b4 hold the 92-art base set and nine sets, 118 arts; tag kinds 46..53 call them in mode 1, which only checks. Loop 0x3ea6e8 walks 44 other arts with no talk row, from 0x38669c (called at 0x384968, in the quest result code by address; inference). |
| Hunter Art check 0x3efb30 | Switch on art - 2 (189 cases, table 0x3efb84). 93 of the 162 granted arts reach quest cleared 0x523da4 with one quest in r1, 78 quests in all; r1 enters as 0x18899. Arts 24 and 138 need 100505 and 100603 only while the Hub/G tier (+0x3e2) is at most 3 and 4. Other cases read story flags; flags 24, 1007 and 1400 come from urgent quests 402, 713 and 10768. |
| mAction2 grants (switch 0x247c58, kinds 1..26) | 4 Wycademy points (DialogMsg 92); 5..8 `0x523a80` point counters; 9..16, 24, 25 Hunter Arts sets through `0x3f0c3c` mode 0 (DialogMsg 100/101; mode 1 from the tag evaluator only checks them); 17..21 ingredient groups through `0x3f1380` (DialogMsg 73); 22 Poogie/Moofy costumes (25/26); 23 shop music (112). The grant functions have no other direct or table callers. |
| Talk selector 0x243d00 | A table splits into conversations ending at a row whose page attribute is 2, 7, 8, 10, 14 or 15 (mask 0x3161 at 0x243e48). One plays when the tags of its first row and of every following row up to one whose first tag is 0 hold (0x2443ec). Kinds 16..21, 119, 147 OR with the tag before; 15 only continues. |
| Talk progress and runner 0x246b1c | Village progress byte (+0x3e0, read at 0x243c2c): 0 any, 1..20 equal, 21..40 at least value-20, 41..60 at most value-40. The runner applies every row's actions without checking tags. |
| Other flag writers | Helper 0x244f14 (43 callers), the script VM (clear only, 0x3d2e1c) and the progress table 0x3f1778 (flags 233..239) write no unlock-chain flag except 1503, set in-quest at 0x3aee44. |
