# Multiplayer findings, by address

## Findings

All main-relative on 1.4.0, read from the bytes; "inference" marks what the bytes don't settle.

| Finding | Where | Evidence |
| --- | --- | --- |
| Online flag, getter and setter | `net+0x63e`, `0x227ba8`, `0x22c624` | Bytes |
| Leave flow start `(ui, op)`. Ignores a request while `ui+0x58` is 1, except op 11 | `0x1ced60` | Bytes |
| Op 14 and 15 flows push prompt 146 or 148, wait 135, clear 188, finish 115. They do nothing but end the session | `0x1d3408`, `0x1d3488`; 188 calls `0x1ce2d8` | Bytes |
| State 115 stores result 3 in `ui+0x54` when it is 0 | `0x1d86fc` | Bytes |
| Destination menu, place picked: state 0x14 and op 14 | `0x794034` | Bytes |
| Menu state 0x14 polls `ui+0x54`: 3 writes the travel code, 4 goes back to the lobby's group | `0x793bd0` | Bytes |
| Destination groups `+0x6b0` 0..3 hold the villages and bedrooms, and group 2's third choice is the ranch; group 6 is the Soaratorium (area 6), its choices on screen Soaratorium, Your Room and Lab. Which village is which is inference from the user's list and the menu's shape | `0x793bf8`, `0x794110`, table `0x159f170` | Bytes, inference; group 6 from the user's screenshots |
| Transition state 0 asks op 15 for any class but `aVillage00Online` (`0x184c910`) and `aVillage07Online` (`0x184ccf0`), through the decoder, so a request with code 0 asks nothing | `0x6bd7d0..0x6bd83c` | Bytes |
| A walking exit stores its record at `sVillage+0x2d0`, with its ID at `+0x2e0` and 1 at `+0x2e1`. With the flag on, any ID but 3, 4, 25, 26 or 255 asks op 14 with code 0. Without it, the same exit takes the path above and asks nothing | setter `0x50cb48`, gate `0x6bd7a4..0x6bd7cc`, `0x6bdd60..0x6bdd84` | Bytes |
| Exit ID to destination: 2 the current village or area 1, 3 Hub, 4 Hub preparation, 25 Pub, 26 Pub preparation, 7 area 5, 27 and 28 area 6. 5 goes to transition state 9, unread | table `0x6bdb58`, `0x6bdbe4..0x6bdc74` | Bytes |
| Gate exit type 6 sets `+0x2f0` to 0 in area 1 and 1 in area 6 (`0x29831c`). Scene state 5 then writes `aVillage00Offline` or `aVillage07Offline` to `+0x1e8` and the area to `+0x1ec`, with no flag check, and the exit uses them in place of its own flag-checked choice. Mode 4 skips the leave request | `0x6bcca8..0x6bcd88`, `0x6bdc20..0x6bdc78`, `0x6bd790` | Bytes |
| The Offline class has no `+0x3d1` wrapper, so a hunter arriving that way sees nobody until an Online class loads | `0x6c0550`, `0x274a78` | Bytes, and the user's report |
| The gate's second button, also on type 6, opens the host and join page with no session check | `0x28dd60..0x28ddcc`, `0x79867c` | Bytes |
| Scene state 1 polls the decoder every frame, so a code written anywhere starts the trip | `0x6bd110..0x6bd1c0` | Bytes |
| Disconnect is menu page 11. Past the prompt, state 2 waits for the flag and writes 1 or 17 only in sub-area 0 or 1 of a lobby, so elsewhere it waits forever | `0x797954`, `0x797a74..0x797bc4` | Bytes, and the user's report |
| Spawn gate: `sVillage+0x3d1`, own state 1, peer state 1, member present, data ready, empty slot; then `0x275a68(players, member, 1, data)` and vtable `+0x254`. No scene test | `0x274a78..0x274cac` | Bytes |
| Peer's state 2 removes their otomo (`0x25a01c`) and kills their unit (vtable `+0x40`). The player update clears a dead unit's slot | `0x22e388..0x22e3d0`, `0x274a00` | Bytes |
| Own state change broadcasts, tagged with no place; only state 1 asks a reply, which goes back to the asker alone | `0x22dbd8`, `0x22debc`, `0x201478` | Bytes |
| `netPlMemberState.mAttr` is a serialized u32 of which native code reads only the low byte | DTI, `0x20afb8`, `0x2013c0` | Bytes |
| `netPlData.mAttr` (+0x578, u32): `0x202764`, `0x202640`, `0x202a34` and `0x203508` copy their third argument (ask reply, 0 or 1) into it; receivers `0x202894` and the Prowler one test bit 0 only, and `0x274400` keeps the data only to +0x560. | `0x202b30`, `0x202854`, `0x202968`, `0x2037dc` | Bytes |
| Message routing: a target above 63 with a group byte reaches a member only when flag bits 16.. (`+0x2fda` halfword) overlap it. Bit 19 is group 8 | `0xb2c2d8`, `0xb2c440` | Bytes |
| The member flags are at `[0x21267d4]+0x208`, then `+8`, then `+0x2fd8 + member * 296` | `0x22d9cc..0x22da3c`, `0xb2c2cc` | Bytes |
| Position and action packets target `0x840`, group 8. Member state, area moves and hunter data go to everyone | `0x200ed8`, `0x200d54`, `0x2011a8`, `0x1e5250` | Bytes |
| State 1 sets bit 19, state 2 clears it, and own changes apply to members in state 1 | `0x22d938..0x22de50` | Bytes |
| Hunter data is `netPlData`, stored by `0x274400`, which marks it ready. Only member state 0 clears that, so it outlasts scenes. `0x227d68(_, ask reply, target)` sends it, and native code calls that only for a state 1 message, so state 2 carries none. A receiver asked to reply sends its own back to the asker alone | `0x2012d4..0x201344`, `0x201454`, `0x202968..0x2029dc`, `0x227d68`, `0x2776d4` | Bytes, and the log: data arrives just before each state 1 |
| The position sender runs in play modes 1, 7 and 27, with no scene test | `0x28ce44..0x28ced0` | Bytes |
| A hunter unit is built with `+0x272d` 1, and the spawn loop stores 0 through vtable `+0x254`. Position packets for it are dropped while it is 0 (vtable `+0x250`) | `0x28bc50`, `0x274b2c`, `0x2689a8`, `0x200fec..0x201000` | Bytes |
| First-packet handshake: a remote hunter and otomo, once loaded, each send RPC 24 to the owner once, with attribute bit 0 and 1. The owner stores them at `net+0xaa0` and `+0xaa4` per member. With a companion in its own otomo data, the owner sends RPC 25 only when both are set. Receiving it stores 1 in `+0x272d` | `0x28cd38..0x28cd74`, `0x265344`, `0x20c998`, `0x28cc98..0x28cd20`, `0x2041a8..0x2041d8` | Bytes, and the user's report of unseen hunters |
| Otomo loop: no otomo found for the member (`0x258e18`), present, data at `sOtomo+0x15ac + member * 0x560` ready and with flag bit 0, then `0x259894(otomo, member, data, 1)`, which needs their hunter | `0x258c58..0x258dcc`, `0x2598b8` | Bytes |
| Gear UI calls `0x22e474`, which sets `net+0x1625a`. The network update then broadcasts hunter data, in play mode 1, 7 or 8, with no reply asked. A hunter and Prowler switch does the same. The receiver stores it and never rebuilds a live unit. Only `0x27697c` rebuilds one, for the local player's own unit | `0x22e474`, `0x227440..0x227480`, `0x746cac`, `0x2028f8`, `0x27697c` | Bytes, and the user's report |
| `netPlData` holds the data block at `+8`. Block: seven equipment slots of 0x2c bytes from `+0x1c`, starting with kind, base number and layered number; `mCharParam` at `+0x4d4`, whose first byte is the weapon type, 15 a Prowler; `mPartsColor` at `+0x4e0`; flags at `+0x504`; `mColorAnimFlag` at `+0x508` | DTI, `0x2028e8`, `0x26e618`, `0x2036f0` | Bytes, DTI |
| Hunter draw conditions (vtable `+0x248`): loaded, `+0x1054` equal to the local hunter's, `+0x1470` 0, `+0x146e` nonzero, and for a remote hunter `+0x272e`, which its update sets once `+0x272d` is nonzero and float `+0x4f4` isn't above 0. Which of these decides drawing is unproven: `+0x248` has other readers too | `0x28e040`, `0x27c2a0`, `0x28cdf4`, `0x53a0d8` | Bytes |
| `netPlAreaMove` is sent once, at arrival, as a broadcast, and applied only if the unit exists then. It sets stage flag, area and position, and starts idle through vtable `+0x370`. So a player already in place receives a newcomer's, and the newcomer never receives theirs | `0x277938`, `0x2011b8..0x2012cc`, `0x28e2c8` | Bytes |
| Quests run with the area reading 255 and use the same unit slots | `0x275a68`, user's run | Bytes, log |
| The four op 14 callers are the transition, the destination menu, the lobby menu's other lobby and page 11 | `0x6bd83c`, `0x794060`, `0x79520c`, `0x7979ac` | Bytes |
| Transition state 1 polls `ui+0x54`: 3 or 4 continues | `0x6bd850` | Bytes |
| Op 15 has one caller. The 17 callers of `0x1ced60` pass 1, 3, 4, 8, 9, 10, 11, 14, 15, 16, 17 and 18 | `0x6bd83c` | Bytes, `research xref` |
| Travel codes: 5,6 area 1; 7,8 area 2; 9,10 area 3; 11,12 area 4; 13 area 5; 14..16 area 6 sub-areas 0..2. 1,4 Hub and 17,20 Pub pick the online class from the flag; every other code has one fixed class | decoder `0x6bff98` | Bytes |
| Lobby menu: only choosing the lobby the session is not in calls op 14. From anywhere else, a live session writes the code directly. So a trip back needs no leave skip, and the native way out of a session stays | `0x795020..0x7951e0`, `0x79537c` | Bytes; matches the user's report that the lobby can't be switched online |
| Common scene load publishes own member state: 1 at sub-area 0 of a lobby, else 2. Slot 0x18 of `aVillage01`..`06` all branch to it | `0xfc1c`, `0x102a0` | Bytes |
| Lobby to preparation area uses the same transition with a live session, passing a different mode to `0x4dad64`. Scene exit clearing other hunters' units is inference from that and the user's report; the destroy call is not traced | `0x6bd8c4` | Bytes, inference |
| Airship online check: `bne` skips prompt state 7 and its session close, and continues in state 8 | `0x6db85c..0x6db8b0`, close at `0x6db554` | Bytes |
| Name tags: `cUIOLobbyHeadUpUI` update (slot 0x4c, `b 0x5c74b0`) hides rows 0, 1, 2, 3 and 5. With `0x507b04(2)`, online and an `aVillage00Online` or `aVillage07Online` scene it runs the tag loop `0x5c7638`. Without `0x507b04(2)`, it returns in area 5 and otherwise calls `0x5c86a4(ui, 0)`, which only handles this player's icon | `0x5c74b0..0x5c7618` | Bytes |
| `0x507b04(2)` is area 0 or 7 at sub-area 0 or 1 | `0x507b04` | Bytes |
| The tag loop covers each member's unit by `0x274ce4`, with no scene test, and reads the mode through `0x73824c` | `0x5c7638..0x5c7ce4` | Bytes |
| L: `uUILobbyHud` update flips `+0x38` when `0x7380ec` passes. That gate reads the flags at `+0x44`, built with no scene test from the online flag, the player's action, `sVillage+0x2c9` (a per-frame busy flag) and play mode 1 | `0x737148..0x737190`, `0x737290`, `0x5096c8` | Bytes |
| The common load creates `uUILobbyHud` in `sUI+0x150` through `0x55e334`, its only caller. It owns the head-up object. It stays live in a village | `0x10100`, `0x55e3e8..0x55e420`, `0x737024` | Bytes, and the user's report |
| The Change Name Display hint needs `0x508984(2)` or `hud+0x44` value 4, both lobby tests, so it stays hidden elsewhere | `0x73768c` | Decompile |
| Village counter accept takes the offline path, state 16, whatever the flag says | `0x781f74`, `0x78251c` | Bytes. The departure afterwards is unread |
