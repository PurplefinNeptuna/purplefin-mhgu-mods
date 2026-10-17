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

Typical nesting is collision 0, melee 6/tap 5, final damage 1. Join final damage to the closest matching collision/monster scope, then pop only the returning scope. Camera viewport 3/tap 4 is a separate route. The Forge skill owns the assembly/TLS lifetime procedure.

## Interpret outcome and owner

Positive finalized HP contribution is display damage; native type 0x1d healing is excluded. Preserve physical hitzone separately from damage weighting. The shared tint rule is bounce first, otherwise physical HZV>=45 weak colour, lower/unknown ordinary colour. Unknown HZV is represented as-1. Affinity uses a separate critical field: native 1 negative, 2 positive, other none. Critical state does not make an arbitrary hitzone weak.

Separate source (Attack, Monster, Object, Tick) from owner (local hunter/Palico, remote hunter/Palico, unknown). Current admission accepts direct attacks from the local hunter/Palico, admitted monster/object damage independently, and suppresses Tick. Resolve native source tags conservatively; do not count every unexplained hit as local.

Local hunter identity uses session+0x30 and the four-player table from [Input and actions](input-and-actions.md). Native kind 0/3 ownership first compares hunter identities. A companion's work entry/master index distinguishes local from remote Palico. Missing objects/unsupported tags remain unknown. Display consumers compare copied identity values and never dereference them later.

Bounce feedback copies both player attack entries and associates the one active entry with finalized damage using attack identity/counter and the captured scope. Do not recolour all simultaneous hits because one feedback slot says bounce. Epoch+serial+target+producer identity support duplicate suppression. Reset display epoch when player/camera context changes.

Current fixed capacities are 64 capture scopes, 16 producer mailboxes×256 records, 256 pending events, 128 visible numbers, 512 recent identities. Pool exhaustion/overflow is bounded; queued data remains independent of thread-local object teardown. These are implementation limits, not native game counts.

## Camera snapshot and projection

Within viewport scope, +0x24 points to a camera whose audited vtable is main+`0x1730d0c`. Check mappings/class and copy view/projection arrays and rectangle while native arguments are alive. Never retain matrix pointers for the render callback. Record the camera/viewport and actual display dimensions when diagnosing resolution-dependent placement.

Native matrices use row-vector conventions. The current adapter constructs a row-major world-to-clip matrix suitable for column-vector projection:

```text
world_to_clip[row*4+col] = sum(view[col*4+k] * projection[k*4+row], k=0,1,2,3)
clip = world_to_clip * [world_x, world_y, world_z, 1]
```

Require finite values, positive display dimensions, and w>0.00001. Native clip bounds are x/y in[-w, w], z in[0, w]. Map pixels as `x0+(x/w+1)*width/2`, `y0+(1-y/w)*height/2`; screen Y points down.

The native rectangle must be origin-aligned, positive, and within 2% of display aspect. Native width/height can differ from display under resolution scaling. Requiring equal dimensions incorrectly rejects valid scaling. Conversely, a same-aspect offscreen view can pass this guard, so it does not prove presentation-target ownership.

r27 represents failed/nonfinite impact capture as unavailable position while retaining scope/return-chain integrity. A genuine captured `(0,0,0)` remains valid. Missing/stale/invalid camera and clipped/behind-camera projection use centre fallback with ordinary animation/overlap. Invalid display dimensions still suppress drawing. Do not replace a failed read with world origin.

## Presentation and validation limits

Styles Wilds, Rise, Classic share ownership/tint rules and stable stored IDs. Rise weak colour is `#F0B41E`, normal `#FFFFFF`, confirmed bounce `#808080`; critical effects remain independent. Placement reserves peak animation/glyph bounds and caches per-hit offsets so later numbers do not jitter. Text advance and actual visible ink bounds serve different purposes.

Host tests cover nesting, missing positions, real origin, matrices, clipping, 720p/900p/1080p/1440p, styles, concurrency, and context lifetime. ARM fixtures exercise compiled gateways with clobbering helpers; renderer fixtures compare actual ImGui commands/pixels. Neither identifies a live reporter's camera or proves GPU/game behavior.

The user accepted r27 on Eden/Linux 2026-10-15; exact candidate bytes were promoted. A third-party r3 placement report remains unreproduced. For an authorized reproduction, compare a stationary hit/camera at 1.0× and 1.25×, then camera rotation and each style, preserving video, fresh log, and matched loader/plugin/assets. Do not claim every fallback branch was manually accepted.

Sources: `mods/damage-numbers/src/{signatures.rs,gateway.S,runtime.rs,render.rs}`, `core/src/{capture.rs,mailbox.rs,lib.rs,presentation.rs}`, tests, `DEVELOPMENT.md`, `EVIDENCE.json`; read-only projection research under `work/damage-numbers/projection-r27/native/` when present.
