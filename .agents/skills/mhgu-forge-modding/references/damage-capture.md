# Capturing damage from a plugin

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

Local hunter identity uses session+0x30 and the four-player table from [Input and actions](../../mhgu-understanding/references/input-and-actions.md). Native kind 0/3 ownership first compares hunter identities. A companion's work entry/master index distinguishes local from remote Palico. Missing objects/unsupported tags remain unknown. Display consumers compare copied identity values and never dereference them later.

Bounce feedback copies both player attack entries and associates the one active entry with finalized damage using attack identity/counter and the captured scope. Do not recolour all simultaneous hits because one feedback slot says bounce. Epoch+serial+target+producer identity support duplicate suppression. Reset display epoch when player/camera context changes.

Current fixed capacities are 64 capture scopes, 16 producer mailboxes×256 records, 256 pending events, 128 visible numbers, 512 recent identities. Pool exhaustion/overflow is bounded; queued data remains independent of thread-local object teardown. These are implementation limits, not native game counts.

## Presentation and validation limits

Damage Numbers' styles, colours, placement and test coverage are that mod's contract: `mods/damage-numbers/DEVELOPMENT.md`. Host and ARM fixtures prove neither a live reporter's camera nor GPU output. To reproduce a placement report, compare a stationary hit with a stationary camera at 1.0x and 1.25x, then rotate the camera, with video, a fresh log and matched loader, plugin and asset hashes.

## Placing numbers from a camera

Damage Numbers accepts only `uQuestCamera`: with `uVillageCamera` accepted (r46, MHGURecomp), village samples reached the mod but lagged the view (user report), cause unknown.

Calling the native projection main+`0x18a48` from `forge_onUpdate` instead of capturing in the viewport scope was measured and rejected: 6 of 64 hits within 2 px, median 7.2 px, max 102.4 px, growing with camera motion (`work/damage-numbers/projection-call/RESEARCH.md`).

On Switch and the emulators use the applied visible size, not Forge's ImGui DisplaySize. MHGU can present a smaller crop of an unchanged swapchain (handheld mode), so DisplaySize can say 1920x1080 while 1280x720 is visible. Read sFestaRender (exact-type ID `0x300a6cd8`) inherited mDisplaySize at +0xb8/+0xbc each frame; +0xb0/+0xb4 are requested values that may still be pending. Native main+`0xbc0874` calls SetCrop main+`0x86a24c` and then updates that pair. The user reported the handheld case fixed on Switch and Android (build and hashes not stated; Damage Numbers `EVIDENCE.json`). On MHGURecomp those words hold the internal render size while ImGui draws over the whole window, so use Forge's display size there (Damage Numbers detects Recomp by the zero `CmdBuffer.Data` after NewFrame; [Runtimes](runtimes.md#imgui-on-each-host)).

The native rectangle must be origin-aligned and positive. When its shape is within 2% of the display's, the display is the view. Otherwise the projection decides: `[5]/[0]` (the picture's shape) must match the viewport (bars around the picture, as gu-native draws) or the display (a window resized after the 3D picture was made), and the view is the largest centred rectangle of that shape; anything else is rejected. Native width/height can differ from display under resolution scaling. Requiring equal dimensions incorrectly rejects valid scaling. Conversely, a same-aspect offscreen view can pass this guard, so it does not prove presentation-target ownership.

Represent a failed or non-finite impact capture as an unavailable position while retaining scope/return-chain integrity. A genuine captured `(0,0,0)` remains valid. A missing position or a missing, stale or invalid camera uses the display centre with ordinary animation and overlap. A position a usable camera clips, including behind the camera, is skipped for that frame only and reappears at its world position if the camera turns to it; never move it to the centre. Invalid display dimensions still suppress drawing. Do not replace a failed read with world origin.
