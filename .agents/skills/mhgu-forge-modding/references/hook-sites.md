# Game functions that take a hook

## Hook points and pitfalls

Entry points that take an entry hook cleanly (two PC-independent words, reached by `bl` or a vtable): leave flow `0x1ced60`, destination menu `0x7939cc`, travel decode `0x6bff98`, disconnect page `0x797954`, host and join page `0x79867c`, player update `0x274710`, network send `0xbbabf4` (reads a stack argument), member state receive `0x201390`, hunter data stored `0x274400`, head-up update `0x5c74b0` (reached by a branch; whether MHGURecomp can hook it is unknown). The transition's entry `0x6bd720` cannot take one (`add r11, sp, #24` in its first words); the walking-exit op is picked by `mov r6, #1` at `0x6bdd78` and read at `0x6bd830`. The airship's online prompt is the `bne` at `0x6db868` (target `0x6db8a4`).

- Scene code a village shares has online checks that skip an offline-only step or apply only in hub or quest flow: `0x6bce80`, `0x6bcf7c`, `0x6bd1f8`, `0x6bd938`, `0x6bdc50`, `0x6bde98`, `0x6c02d8`. 232 call sites read the online flag; most are unread.
- Never write `net+0xa90` or `sVillage+0x3d1` by hand: the common load publishes them and replies read the table at `0x2013f0`.
- `0x6c0400` sends RPC 113, a separate `0x18b8`-byte record that never reaches `0x274400`; hunter data goes through `0x227d68`.
- `sVillage+0x2f0` is not the session's lobby: the lobby menu overwrites it from any scene, and `0x1d7c98` picks the return after a host leaves or a network error from it.
- The lobby menu's first option from a village (`0x795250`) sets page 3 directly; its outcome with a live session is unread.
- The area byte reads 255 while a scene unloads, so "not a lobby" is not "outside a lobby" during a fade.
- A hunter created without its otomo never takes a position: the owner withholds the first packet until both have asked.
