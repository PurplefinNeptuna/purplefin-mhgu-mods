# How monster HP falls

Offsets target the verified Switch 1.4.0 main.

## How monster HP actually falls

HP lives at `work+0x370` (max `+0x374`), where `work = *(monster+0x1428)`. The network sync record `nFestaNetwork::netEmMasterChange` (DTI `mParam.hp_vital`, s32) is filled by main+`0xcba54` from `work+0x370`, and maps the root position to `work+0x40/44/48`. Regeneration helpers main+`0x9ce9c`/`0x9cf7c` clamp HP against the maximum.

Hits do not subtract HP directly: main+`0x9d6f8` adds each hit to a part counter `work+0x488+part*2`, and the per-frame monster update main+`0x97ddc` subtracts the sum, then subtracts and clears the s16 pending amount `work+0x5d66`. All five hit handlers are reached from the collision function `0x170968`: main+`0x171350` by call and `0x172bf0`/`0x173a24`/`0x174c0c`/`0x176ad0` by tail branch from `0x170a20..0x170ab0`, so the collision scope encloses every hit. Damage that never passes through the hit handler needs its own site:

| Damage | Native path | How it is observed |
| --- | --- | --- |
| Kinsect | The w13 shell hit setup main+`0x4816c0` calls the shared shell hit initialiser (vtable +0x140, main+`0x4a2790`) with subtype 1, then rewrites the entry: +0x10 = 6, +0xc = kinsect, +0x6e = 0, +0x70 = owner hunter (main+`0x4a1b6c`) | Collision path; tags (6, 1, 0) with a known owner are Attack |
| Poison | Tick main+`0xa2664` clears `work+0x5d66`; while `work+0x5e08 & 2` it advances the timer `work+0x5ca8` and at each interval stores the poison table's s16 +0xc in `work+0x5d66`. Its tail branch at `0xa2740` returns through LR; its caller is `0xc8ddc` (2,056 bytes) | Read `work+0x5d66` after the tick returns |
| Blast | Detonation main+`0xaac54` gets the blast table `(*(monster+0x75ec)+100)+0x54` (getter main+`0x71078`), returns early when null, else resets the blast point and adds the table's s16 +0xc to the part counter directly, bypassing `0x9d6f8` | Read the same table at entry |
| Mount | Hits on a ridden monster (main+`0x812a8`: ride action states or category 0xd) go to main+`0x170adc`, which adds them to the rider's mount gauge (main+`0x2f6778`), not HP. In category 0xd the monster update reaches main+`0x99764`, loads a fixed amount from monster data +0x8c (x1.5 when singleton query main+`0x49938` returns >= 2), subtracts it at `0x9979c` and sets action 0x2b. Mount point `work+0x5d9a` (DTI `nori_dmg_point`, updated by main+`0xa3528`). | r4 (amount) and `[sp+60]` (work block) at `0x9978c`. "Finisher" is an inference; no string names the branch |
| Map-fired shells | `0x4a2790` rewrites owner fields only for hunters, Palicoes and monsters. Shells of the map's `uStageShellOwner` (character type 9, main+`0x51c440` -> main+`0x53985c`) keep secondary kind 2 with the shell at +0x70; the rail cannon (`uShellSt006`, main+`0x497040`) is one | Owner `*(*(shell+0x136c)+0xc)` with type 9: tags (2, any, 2) are Object damage |
| Ballista | Tags (2, 8, 0) with the hunter at +0x70 | Already Object |

`0x9978c` is reached by fall-through and from the `blt` at `0x99770`, where r4 already holds the unscaled amount; nothing branches to `0x99790`.

Aerial vault (jump) buildup is s16 `work+0x5d8e` (DTI `mParam.jump_dmg_point`; threshold +0x5d90, decay float +0x5d94, trigger count byte +0x5d98; its table is getter `0x71078`'s result +0x48, +0x4c is mount); whether a vault lowers HP is unresolved (`work/damage-numbers/vault-research.md`).

Cannon, huge cannon and Dragonator projectiles are not traced (`work/damage-numbers/siege-weapons-research.md`). Status and stage records carry no owner, and a status position is the monster root, not an impact point.

To see every HP loss, compare HP between frames: `sEnemy::Instance` (main+`0x1851fe0`) lists up to ten monsters at +0x1c, and `getMonsterInMap` main+`0x5ceb4` reads the same slots. Damage the game captured but never subtracted (HP floors, capture limits) never shows as a loss.

## Shells and siege weapons

Static research, not run (`work/damage-numbers/siege-weapons-research.md`; main-relative).

### Shared mechanism

- Shell hit setup main+0x4a2790 (vtable +0x140 on every shell) calls main+0x168e98: hit +0x10 = 2, +0xc/+0x70 = shell, +0x6e = 2, +0x6d = subtype. It then reads the owner character `*(*(shell+0x136c)+0xc)` and its type byte +0x1052: 0 hunter -> +0x6e=0, +0x70=hunter; 2 Palico -> +0x6e=3; 1 monster -> +0x6e=1. Any other type leaves +0x6e=2 and +0x70=shell.
- Character constructor main+0x53985c stores its second argument at +0x1052.
- Shell spawn queue main+0x48c4f0; requests are {vtable, id, flag, owner, ...}.

### Ballista (proven player-owned)

- Player action main+0x2d9ad8 (uPlayerQuest shared action) uses the gimmick at player+0x32d0 and the loaded ammo item (+0x2520): items 0x6c2 and 0xa4d spawn request 0x1c, item 0x6c3 spawns 0x1d, each with owner = the hunter.
- Request allocators main+0x4628f8 / 0x4632ec sit in uShellPlcom_008 / _009 code; both classes derive from uShellPlcom_BallistaShell (DTI codes 0x8978 / 0x8979). Stage setup main+0x4feb40 preloads 0x1c/0x1d for ballista maps.
- uShellPlcom_008 slot 0x16c (main+0x462da8) calls hit setup with subtype 8. Result: tags (2, 8, 0), hit+0x70 = hunter.
- Hits use the main handler. uShellPlcom_009 has no hit setup found (it tracks a monster at +0x15a8); it may not deal damage itself.

### Stage-owned shells (not linked to a player)

- Stage setup main+0x4feb40 allocates uStageShellOwner (0x1370 bytes, constructor main+0x51c440 -> main+0x53985c(obj, 9): type 9) at map+0x314. Map/quest code (main+0x4feb40, 0x4fed98, 0x50362c) queues stage shells 0x191, 0x193, 0x195, 0x196, 0x199 with that owner.
- Type 9 is not handled by main+0x4a2790, so hits keep tags (2, subtype, 2) with +0x70 = the shell. uShellSt002 uses subtype 8 (main+0x492668).

### Per weapon

- Rail cannon: netShRailCannon is sent by main+0x497040 inside uShellSt006, driven by aMap10/25/26/27 code (main+0x503c7c). Stage shell, stage owner.
- Cannon: cMediateCannon methods act on the local player; the player request main+0x2aabc4 forwards to a stage-side object (stage manager +0x9c74, virtual +0x20). The player spawns no cannon shell. Firing shell not traced; stage-owned by inference.
- Huge cannon: mediator identical in shape to the cannon; not traced further.
- Dragonator: quest data cQuestPlus mIsGekiryu (+12), mGekiryuStartTime (+14), mGekiryuReuseTime (+16), beside fort HP. Hit path not traced.

Not established: which stage shell id belongs to which weapon, the cannon and huge cannon projectile classes, and the Dragonator hit. A one-run log of rejected hit tags in a siege quest would settle them.
