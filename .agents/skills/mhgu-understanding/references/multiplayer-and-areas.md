# Multiplayer sessions, areas and travel

How the game moves a hunter between villages, lobbies and quests, and who it shows to whom. Read from the 1.4.0 bytes; [Multiplayer findings](multiplayer-findings.md) has every address and its evidence, and this page is the map. Area type values are in [Where the quest list comes from](quest-lists.md#where-the-quest-list-comes-from).

## Summary

- Native code separates players by member state: 1 on a lobby's main floor (sub-area 0), 2 elsewhere. Only state 1 spawns peers, routes position packets (bit 19, group 8) and asks for hunter data.
- Hunter data (`netPlData`) is stored by `0x274400` and outlasts scenes; a live unit is never rebuilt from new data.
- A remote hunter moves only after a two-RPC handshake that needs its otomo too.
- Trips are travel codes written for the decoder `0x6bff98`, which scene state 1 polls every frame; the leave flow `0x1ced60` only reports a result in `ui+0x54`.
- `netPlMemberState.mAttr` is a u32 of which native code reads only the low byte, so the upper bits are free.
- `netPlData.mAttr` (hunter data, message +0x578) is the builders' reply flag; receivers test only bit 0.

## Scenes, areas and lobby packets

Static research from `work/hub-area-sync/FINDINGS.md` (bytes, not run):

| Finding | Where |
| --- | --- |
| Session (`sGameControl` in Ghidra, cell `0x188ca48`): area type +0x4c, sub-area +0x4d, previous +0x50/+0x4f | Travel `0x6bdfd0` |
| Writers of +0x4c: constructors `0x3f7848`/`0x3f7a60`, result `0x6a2380`, title `0x6a6e34`, travel `0x6bdfd0` (a scan 0x80 bytes after each cell load; another writer is possible) | |
| Area to scene class: 0 `aVillage00Online/Offline`, 7 `aVillage07Online/Offline` (by the online flag), 1..6 `aVillage01..06` regardless | `0x12750` |
| Travel request `sVillage+0x398` (0..20) is decoded to class, area, sub-area at scene +0xc4/+0xc8/+0xc9 | `0x6bff98` |
| Request writers: `uUILobbyStartMenu` (`0x7939cc`, `0x794e88`, `0x797954`), `uUIAirship` `0x6db2f8`, network state machine `0x1d7cc8` | |
| Airship online: message 39 category 7, state 7; accept may call session close `0x1e7384` | `0x6db85c`, `0x6db534..0x6db554` |
| Online scene wrappers: slot 0x1c enter `0x6bcae8` sends RPC 113 (`0x6c0400`); slot 0x24 end `0x10680` clears `sVillage+0x3d1` (`0x6c0588`). `aVillage01`/`04` thunk to the same bases (`0xfc1c`, `0x10680`, `0x6bcae8`, `0x6bcb54`) | |
| Spawn loop detail: own member flag `net+0xa90+i*4`, empty slot `sPlayer+0x1c+i*4`, member present `0x22d8b4`, data ready `sPlayer+0x1b5c+i*0x560` +0x504 bit 3; otomo gate `0x258bc8`. Member state setter `0x22d8f4(net, i, state)`; a peer's state 2 destroys its player (lookup `0x276748`, vcall +0x40) | `0x274a78..0x274cac` |
| Local player in every scene: `0x2758a4` calls creator `0x275a68` with type 1 | |
| Another player's hunter: the creator `0x275a68` writes the member index at hunter `+0x1051` and sets `+0x13cc` bit 0 only on the local unit, before its armor loads (bit 3 marks a Prowler), so a type 0 or 1 hunter without bits 0 and 3 is another player's ([Hunter armor](armor-models.md#which-hunter-is-which)) | |
| `netPlAreaMove` `0x201128`/`0x2011b8` channel 11 (pos xyz, `mVectorY`, `mAreaNo`, `mStageMvFlag`, read at `0x20ab14`); `netPlPositionLobby` `0x200d78`/`0x200efc` channel 13; `netPlActionLobby` `0x200cf4` channel 12. No lobby RPC field names a scene | |
| `mAreaNo` is player +0x1054, fed from sub-area +0x4d by relocate `0x2778cc` (callers `0x6bf4`, `0x102cc`, `0x6a0cd0`). `mStageMvFlag` is player +0x1470: 4 on scene exit (`0x6bd9dc`), 2 on a sub-area move (`0x6bd428`, which publishes no state); receiving 4 hides the weapons (`0x2827bc`) | |
| Position send `0x28ce34..0x28ced0` gates on local player, `sVillage+0x1e0` in {1, 7, 27}, timer > 8 | |
| Leave flow: `0x1ced60(ui, op)` (`ui = 0x677880()`) starts state machine `0x1cee88`; op 14 -> state 114, op 15 -> 116. Other op 14 callers: `0x78c994`, `0x790638`, `0x790804`, `0x79088c`, `0x790b40`, `0x79520c`, `0x795498`, `0x796bdc`, `0x7979ac`, `0x797c90`, `0x797e7c`, `0x798224` | |
| Option list `0x570c18` enables by progress and sub-area with no network test. `sVillage+0x2f0`: 0 Hub, 1 Pub, written by `0x794e88`. Unread member-state readers: `0x292268`, `0x296980` | |

## Recording a quest clear

See [Recording a clear online](quest-progression.md#recording-a-clear-online): an online joiner never records a rank-up urgent.

## Hook points and pitfalls

Entry points that take an entry hook cleanly (two PC-independent words, reached by `bl` or a vtable):

| Function | Address |
| --- | --- |
| Leave flow | `0x1ced60` |
| Destination menu | `0x7939cc` |
| Travel decode | `0x6bff98` |
| Disconnect page | `0x797954` |
| Host and join page | `0x79867c` |
| Player update | `0x274710` |
| Network send | `0xbbabf4` (reads a stack argument) |
| Member state receive | `0x201390` |
| Hunter data stored | `0x274400` |
| Head-up update | `0x5c74b0` (reached by a branch; whether MHGURecomp can hook it is unknown) |

The transition's entry `0x6bd720` cannot take one (`add r11, sp, #24` in its first words); the walking-exit op is picked by `mov r6, #1` at `0x6bdd78` and read at `0x6bd830`. The airship's online prompt is the `bne` at `0x6db868` (target `0x6db8a4`).

- Scene code a village shares has online checks that skip an offline-only step or apply only in hub or quest flow: `0x6bce80`, `0x6bcf7c`, `0x6bd1f8`, `0x6bd938`, `0x6bdc50`, `0x6bde98`, `0x6c02d8`. 232 call sites read the online flag; most are unread.
- Never write `net+0xa90` or `sVillage+0x3d1` by hand: the common load publishes them and replies read the table at `0x2013f0`.
- `0x6c0400` sends RPC 113, a separate `0x18b8`-byte record that never reaches `0x274400`; hunter data goes through `0x227d68`.
- `sVillage+0x2f0` is not the session's lobby: the lobby menu overwrites it from any scene, and `0x1d7c98` picks the return after a host leaves or a network error from it.
- The lobby menu's first option from a village (`0x795250`) sets page 3 directly; its outcome with a live session is unread.
- The area byte reads 255 while a scene unloads, so "not a lobby" is not "outside a lobby" during a fade.
- A hunter created without its otomo never takes a position: the owner withholds the first packet until both have asked.
