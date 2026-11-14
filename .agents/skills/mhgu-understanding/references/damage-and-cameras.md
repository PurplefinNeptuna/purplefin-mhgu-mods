# Damage capture, ownership, and cameras

The maintained Damage Numbers plugin observes finalized native outcomes and copies evidence. Recomputing damage from attack tables would lose native modifiers and source/owner distinctions. Offsets target the verified Switch 1.4.0 main.

## Observation sites

| Main offset | Captured behavior |
| --- | --- |
| `0x170968` | Collision entry: r1 hit, r2 monster, r3 impact-position pointer |
| `0x09d6f8` | Final damage, observed after original return |
| `0x2a87a8` | Player feedback, associated bounce state |
| `0xb8909c` | Viewport scope containing camera work |
| `0x885844` | Live camera/matrices/viewport tap |
| `0x16dd7c` | Interior melee HZV tap before register restoration |
| `0x16dc6c` | Melee HZV entry, monster association |
| `0x178660` | Shot HZV calculation, copied after return |
| `0x0a2664` | Poison tick: reads pending `work+0x5d66` after return |
| `0x0aac54` | Blast detonation: reads the blast table s16 +0xc at entry |
| `0x09978c` | Mount finisher inside monster update: r4 amount, `[sp+60]` work block |

Typical nesting is collision 0, melee 6/tap 5, final damage 1. All five hit handlers are reached from the collision function, so its scope encloses every hit. Join final damage to the closest matching collision/monster scope, then pop only the returning scope. Camera viewport 3/tap 4 is a separate route. The Forge skill owns the assembly/TLS lifetime procedure.

## Interpret outcome and owner

Positive finalized HP contribution is display damage; native type 0x1d healing is excluded. Preserve physical hitzone separately from damage weighting. The shared tint rule is bounce first, otherwise physical HZV>=45 weak colour, lower/unknown ordinary colour. Unknown HZV is represented as-1. Affinity uses a separate critical field: native 1 negative, 2 positive, other none. Critical state does not make an arbitrary hitzone weak.

Separate source (Attack, Monster, Object, Tick) from owner (local hunter/Palico, remote hunter/Palico, unknown). Current admission accepts direct attacks from the local hunter/Palico, admitted monster/object damage independently, and suppresses Tick. Resolve native source tags conservatively; do not count every unexplained hit as local.

Local hunter identity uses session+0x30 and the four-player table from [Input and actions](input-and-actions.md). Native kind 0/3 ownership first compares hunter identities. A companion's work entry/master index distinguishes local from remote Palico. Missing objects/unsupported tags remain unknown. Display consumers compare copied identity values and never dereference them later.

Bounce feedback copies both player attack entries and associates the one active entry with finalized damage using attack identity/counter and the captured scope. Do not recolour all simultaneous hits because one feedback slot says bounce. Epoch+serial+target+producer identity support duplicate suppression. Reset display epoch when player/camera context changes.

Current fixed capacities are 64 capture scopes, 16 producer mailboxes×256 records, 256 pending events, 128 visible numbers, 512 recent identities. Pool exhaustion/overflow is bounded; queued data remains independent of thread-local object teardown. These are implementation limits, not native game counts.

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

- Shell hit setup main+0x4a2790 (vtable +0x140 on every shell) calls
  main+0x168e98: hit +0x10 = 2, +0xc/+0x70 = shell, +0x6e = 2, +0x6d = subtype.
  It then reads the owner character `*(*(shell+0x136c)+0xc)` and its type byte
  +0x1052: 0 hunter -> +0x6e=0, +0x70=hunter; 2 Palico -> +0x6e=3; 1 monster
  -> +0x6e=1. Any other type leaves +0x6e=2 and +0x70=shell.
- Character constructor main+0x53985c stores its second argument at +0x1052.
- Shell spawn queue main+0x48c4f0; requests are {vtable, id, flag, owner, ...}.

### Ballista (proven player-owned)

- Player action main+0x2d9ad8 (uPlayerQuest shared action) uses the gimmick at
  player+0x32d0 and the loaded ammo item (+0x2520): items 0x6c2 and 0xa4d spawn
  request 0x1c, item 0x6c3 spawns 0x1d, each with owner = the hunter.
- Request allocators main+0x4628f8 / 0x4632ec sit in uShellPlcom_008 / _009
  code; both classes derive from uShellPlcom_BallistaShell (DTI codes 0x8978 /
  0x8979). Stage setup main+0x4feb40 preloads 0x1c/0x1d for ballista maps.
- uShellPlcom_008 slot 0x16c (main+0x462da8) calls hit setup with subtype 8.
  Result: tags (2, 8, 0), hit+0x70 = hunter.
- Damage Numbers: owner resolves to the hunter; source_outcome gives
  Object, which is shown for every player. Hits use the main handler, so the final-damage
  site captures them. uShellPlcom_009 has no hit setup found (it tracks a monster at
  +0x15a8); it may not deal damage itself.

### Stage-owned shells (not linked to a player)

- Stage setup main+0x4feb40 allocates uStageShellOwner (0x1370 bytes,
  constructor main+0x51c440 -> main+0x53985c(obj, 9): type 9) at map+0x314.
  Map/quest code (main+0x4feb40, 0x4fed98, 0x50362c) queues stage shells
  0x191, 0x193, 0x195, 0x196, 0x199 with that owner.
- Type 9 is not handled by main+0x4a2790, so hits keep tags (2, subtype, 2)
  with +0x70 = the shell. uShellSt002 uses subtype 8 (main+0x492668).
- Damage Numbers shows these as object damage (owner type 9, map-fired shells).

### Per weapon

- Rail cannon: netShRailCannon is sent by main+0x497040 inside uShellSt006,
  driven by aMap10/25/26/27 code (main+0x503c7c). Stage shell, stage owner.
- Cannon: cMediateCannon methods act on the local player; the player request
  main+0x2aabc4 forwards to a stage-side object (stage manager +0x9c74, virtual
  +0x20). The player spawns no cannon shell. Firing shell not traced; stage-owned
  by inference.
- Huge cannon: mediator identical in shape to the cannon; not traced further.
- Dragonator: quest data cQuestPlus mIsGekiryu (+12), mGekiryuStartTime (+14),
  mGekiryuReuseTime (+16), beside fort HP. Hit path not traced.

Not established: which stage shell id belongs to which weapon, the cannon and
huge cannon projectile classes, and the Dragonator hit. A one-run log of
rejected hit tags in a siege quest would settle them.

## Camera snapshot and projection

Within viewport scope, +0x24 points to the camera: `uQuestCamera` (vtable main+`0x1730d0c`) in quests, `uVillageCamera` (main+`0x1730e10`) in the village (saved DTI; both `uFestaCamera`, as is `uSubSceneCamera` main+`0x1730d90`). Damage Numbers accepts the first two. Accepting the village camera is static evidence until a run logs the preview anchored in the world there. Check mappings/class and copy view/projection arrays and rectangle while native arguments are alive. Never retain matrix pointers for the render callback. Record the camera/viewport and actual display dimensions when diagnosing resolution-dependent placement.

The perspective builder main+`0x7c617c` stores `cot(fov/2)/aspect` at `[0]` and `cot(fov/2)` at `[5]`, so `[5]/[0]` is the picture's shape; it leaves m[8]/m[9] at 0 (a host upscaler may write jitter there). Calling the native projection main+`0x18a48` from `forge_onUpdate` instead of capturing in the viewport scope was measured and rejected: 6 of 64 hits within 2 px, median 7.2 px, max 102.4 px, growing with camera motion (`work/damage-numbers/projection-call/RESEARCH.md`).

Native matrices use row-vector conventions. The current adapter constructs a row-major world-to-clip matrix suitable for column-vector projection:

```text
world_to_clip[row*4+col] = sum(view[col*4+k] * projection[k*4+row], k=0,1,2,3)
clip = world_to_clip * [world_x, world_y, world_z, 1]
```

Require finite values, positive display dimensions, and w>0.00001. Native clip bounds are x/y in[-w, w], z in[0, w]. Map pixels as `x0+(x/w+1)*width/2`, `y0+(1-y/w)*height/2`; screen Y points down.

On Switch and the emulators use the applied visible size, not Forge's ImGui DisplaySize. MHGU can present a smaller crop of an unchanged swapchain (handheld mode), so DisplaySize can say 1920x1080 while 1280x720 is visible. Read sFestaRender (exact-type ID `0x300a6cd8`) inherited mDisplaySize at +0xb8/+0xbc each frame; +0xb0/+0xb4 are requested values that may still be pending. Native main+`0xbc0874` calls SetCrop main+`0x86a24c` and then updates that pair. No affected device has confirmed the handheld case. On MHGURecomp those words hold the internal render size while ImGui draws over the whole window, so use Forge's display size there (Damage Numbers detects Recomp by the zero `CmdBuffer.Data` after NewFrame; [Runtimes](../../mhgu-forge-modding/references/runtimes.md#imgui-on-each-host)).

The native rectangle must be origin-aligned and positive. When its shape is within 2% of the display's, the display is the view. Otherwise the projection decides: `[5]/[0]` (the picture's shape) must match the viewport (bars around the picture, as gu-native draws) or the display (a window resized after the 3D picture was made), and the view is the largest centred rectangle of that shape; anything else is rejected. Native width/height can differ from display under resolution scaling. Requiring equal dimensions incorrectly rejects valid scaling. Conversely, a same-aspect offscreen view can pass this guard, so it does not prove presentation-target ownership.

Represent a failed or non-finite impact capture as an unavailable position while retaining scope/return-chain integrity. A genuine captured `(0,0,0)` remains valid. A missing position or a missing, stale or invalid camera uses the display centre with ordinary animation and overlap. A position a usable camera clips, including behind the camera, is skipped for that frame only and reappears at its world position if the camera turns to it; never move it to the centre. Invalid display dimensions still suppress drawing. Do not replace a failed read with world origin.

## Presentation and validation limits

Damage Numbers' styles, colours, placement and test coverage are that mod's contract: `mods/damage-numbers/DEVELOPMENT.md`. Host and ARM fixtures prove neither a live reporter's camera nor GPU output. To reproduce a placement report, compare a stationary hit with a stationary camera at 1.0x and 1.25x, then rotate the camera, with video, a fresh log and matched loader, plugin and asset hashes.

Sources: `mods/damage-numbers/src/{signatures.rs,gateway.S,runtime.rs,render.rs}`, `core/src/{capture.rs,mailbox.rs,lib.rs,presentation.rs}`, tests, `DEVELOPMENT.md`, `EVIDENCE.json`; read-only projection research under `work/damage-numbers/projection-r27/native/` when present.
