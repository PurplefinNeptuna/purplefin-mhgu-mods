# Multiplayer sessions, areas and travel

How the game moves a hunter between villages, lobbies and quests, and who it
shows to whom. Read from the 1.4.0 bytes for Multiplayer Roaming
(`mods/online-roaming/DEVELOPMENT.md` Findings has every address and its
evidence; this page is the map). Area type values are in
[Quests and progression](quests-and-progression.md#where-the-quest-list-comes-from).

## Session and member state

| Fact | Where |
| --- | --- |
| Online flag | `net+0x63e`, getter `0x227ba8`, setter `0x22c624` |
| Member state | Published by the common scene load (`0xfc1c`, `0x102a0`): 1 on a lobby's main floor (sub-area 0), else 2. A state change broadcasts; only state 1 asks a reply, sent back to the asker alone (`0x22dbd8`, `0x22debc`, `0x201478`) |
| Peer leaves (state 2) | Removes their otomo (`0x25a01c`) and kills their unit (vtable +0x40) |
| Spawn gate | `sVillage+0x3d1`, own state 1, peer state 1, member present, data ready, empty slot; then `0x275a68(players, member, 1, data)` and vtable +0x254. No scene test (`0x274a78..0x274cac`) |
| Routing | A packet target above 63 with a group byte reaches a member only when its flag bits 16.. overlap (`0xb2c2d8`). Position and action packets target `0x840`, group 8 = bit 19. State 1 sets bit 19, state 2 clears it. Member flags at `[0x21267d4]+0x208`, `+8`, `+0x2fd8 + member*296` |
| Hunter data | `netPlData`, stored by `0x274400` (marks it ready; only member state 0 clears that). Sent by `0x227d68(_, ask reply, target)`, natively only for a state 1 message. Data block at +8: seven 0x2c equipment slots from +0x1c, `mCharParam` +0x4d4 (first byte weapon type, 15 Prowler), `mPartsColor` +0x4e0 |
| Gear change | Gear UI `0x22e474` sets `net+0x1625a`; the next network update broadcasts hunter data with no reply asked. The receiver stores it and never rebuilds a live unit |
| First-packet handshake | A loaded remote hunter and otomo each send RPC 24 once; the owner stores them at `net+0xaa0`/`+0xaa4` and sends RPC 25 when both are set; receiving it sets `+0x272d`. Position packets are dropped while it is 0 |
| Area move | `netPlAreaMove` is broadcast once, at arrival, and applied only if the unit already exists, so a newcomer never receives the others' |
| Quests | Run with the area byte 255 and the same unit slots |

`netPlMemberState.mAttr` is a serialized u32 of which native code reads only the low byte, so the upper bits can carry a mod's own data.

## Travel

| Fact | Where |
| --- | --- |
| Leave flow `(ui, op)` | `0x1ced60`; its only product callers read is `ui+0x54` (3 continue, 4 back). Ignores requests while `ui+0x58` is 1, except op 11. Ops 14 and 15 only end the session |
| Travel codes (decoder `0x6bff98`) | 5,6 area 1; 7,8 area 2; 9,10 area 3; 11,12 area 4; 13 area 5; 14..16 area 6; 1,4 Hub and 17,20 Pub pick the Online or Offline class by the flag |
| Scene state 1 | Polls the decoder every frame, so a code written anywhere starts the trip (`0x6bd110..0x6bd1c0`) |
| Walking exits | Record at `sVillage+0x2d0`, ID at +0x2e0. Exit IDs: 2 current village or area 1, 3 Hub, 4 Hub preparation, 25 Pub, 26 Pub preparation, 7 area 5, 27/28 area 6 (table `0x6bdb58`) |
| Disconnect | Menu page 11; past the prompt it writes a code only in sub-area 0 or 1 of a lobby, so elsewhere it waits forever (`0x797a74..0x797bc4`) |
| Village quest counter accept | Takes the offline path, state 16, whatever the flag (`0x781f74`, `0x78251c`) |

Name tags: `cUIOLobbyHeadUpUI` update (`0x5c74b0`) runs the tag loop `0x5c7638` only online in `aVillage00Online`/`aVillage07Online` at sub-area 0 or 1 (`0x507b04(2)`); the loop itself has no scene test.

## Recording a quest clear

See [Quests and progression](quests-and-progression.md#recording-a-clear-online): an online joiner never records a rank-up urgent.

Sources: `mods/online-roaming/DEVELOPMENT.md`, `mods/shared-urgent-quests/DEVELOPMENT.md`.
