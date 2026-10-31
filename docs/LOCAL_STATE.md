# Local state

Workspace baseline updated 2026-10-15: stock Switch Forge 1.5.1 and forge-rs
1.5.0, on branch `main`. GURecomp, Forge PC and the `-pc` ports were retired on
2026-10-30 because MHGURecomp loads the Switch NROs. Merged task branches, obsolete
source forks and the old release worktree are removed; their tips are recorded
in [COMPACTION.json](COMPACTION.json) and remain reachable through main or archive
tags. This file describes workspace sources and deliveries, not current
emulator activation.

## Deliveries

Each mod's DISTRIBUTION.json is authoritative. "Packaged" means a local,
unpublished ZIP; approval is not a gameplay result. Release history, design and
manual checks are in each mod's DEVELOPMENT.md; exact validation and runtime
records are in its EVIDENCE.json.

| Mod | Current | Acceptance scope |
| --- | --- | --- |
| Damage Numbers | r36 READY_TO_DISTRIBUTE (2026-10-30) | Hits outside the camera view stay hidden until the camera turns to them instead of showing at screen centre. Release `build/damage-numbers/releases/r36/damage-numbers-r36.zip`, promoted unchanged from the candidate (approval and archive in `backups/accepted/damage-numbers/r36-distribution-approved/`). User reports an Eden run (log not retained); r37-projection-ab, a diagnostic with r36's display code, ran docked on Eden and looked right. Handheld unreported. Release r35 is archived at `backups/accepted/damage-numbers/r35-before-hidden-offscreen/`. r27 was the last user-tested build before this. |
| Key Quest Markers | r18 READY_TO_DISTRIBUTE (2026-10-18) | Link rebuild of the Eden/Linux-accepted r17. HD is optional. Ryujinx and Switch hardware unconfirmed. |
| Modern Sharpness Gauge | r53 DEVELOPMENT, Phase 5 (2026-10-31); r44 READY_TO_DISTRIBUTE shipped 2026-10-30 | r44 (forge-modding P7, consolidation) was approved and shipped unchanged: release `build/modern-sharpness-gauge/releases/r44/modern-sharpness-gauge-r44.zip`, sha256 `ee23ed17c52d84bbcc4ffdee3fac73d80099132bef84ede238162795705b0022`, preserved in `backups/accepted/modern-sharpness-gauge/r44-distribution-approved/`. Its acceptance is the single Eden run of 2026-10-30 (installed NRO matching the packaged payload: 209 cut lines on bar rect 110 38 238 166 with `feed=128`, box widths 18 / 54 / 90 px at 0 / 5000 / 10000 bp, three insertions with a 5-entry map and 9-record cache, three links-lost teardowns each followed by a new insertion, no guest exception; tester reported the cut where r43 put it with the HD Project on, which closed the HD question). r45 added the plan's Phase 5 copy and **froze the game about five seconds into both quest launches** of its 2026-10-31 Eden run: the insertion printed no line on any path and the guest faulted on a null read at the gauge's first draw (`work/modern-sharpness-gauge/runs/r45-eden-2026-10-31-frozen.txt`). Root cause: it built the copy by calling the class's vtable slot 0x00 as a constructor, which `cGUIObjTexture` does not have. r46 builds the same copy on the Key Quest Markers-verified path for this class (DTI allocator slot 0x20 with `(bytes, align, dti id)`, zeroed 304-byte block, standalone constructor main+0xa4f60c), writes the bar's atlas rectangle as floats, and frees a failed copy once. Placement, geometry, storage (6-word map, 88-byte/11-record draw block) and the accepted cut are unchanged. 22 host fixtures pass; verify PASSED with the same 21 signature windows; r46 Gameplay NOT RUN. Open: the MT `color` word's byte order (alpha byte position is an inference), the copy under the glow's edge, the draw walker's thread, and native hardware/Ryujinx. r46 ran clean on Eden 2026-10-31 (76 lines, 68 cut lines, one insertion, one area-change teardown, no fault) and its copy refused itself at stage 52: `records=9 dim=0x0`, so the gauge looked exactly as shipped. Root cause read from the decompiles: the `Texture` setter returns early with `+0x104 = 0` when the resource at +0x78 is 0, and it resolves ids through `*(obj+0x64)+0xe8` (`main+0xb80fd0`), a word the class constructor zeroes. r47 ran (48 lines, no fault): `records=11 dim=0x44246540 dim_tex=0x519bbab0 dim_flags=0x20a0001` - the copy exists and its texture resolved. `dim_flags=0x20a0001` is the class constructor's own default (main+0xa4d0d8 writes 0x020a0001 at +0x54), so the line proves construction, not drawing. Nothing of it appeared in the sharpness gauge; the noisy dark translucent block in that run's photo is read as the copy's drawing, which is an inference: r47 wrote the bar's rect corner (110, 38) into the copy's local position at +0x80/+0x84 and wrote its atlas window from words read as integers, so the copy sampled around v = 1.13e9, outside the 88x24 sheet. The bar's own window, decoded from the log's float words, is [0, 280, 88, 304] in the top band and [0, 304, 88, 328] in the orange one: the `u` pair is the whole 88-column sprite and `v` steps by tier. r48 ran (67 lines, 62 cut lines, no fault): `records=11 dim=0x48043500 dim_tex=0x5194bab0 dim_flags=0x20a0001` - built with its texture resolved, and **nothing of it in the sharpness gauge**. The grey band with the slanted tip in the tester's r48 photo is the Dual Blade's demon gauge, a row this mod does not touch: the tester named that band, above the sharpness gauge's red cropped blade. The layout fact: a `cGUIObjTexture` is laid out from its position pair (`+0x80/+0x84`) and authored pair (`+0xb4/+0xb8`) when the walker visits it, after this mod's callback, so per-frame rectangle writes lose; r48 also wrote a screen corner into parent-space offsets. r49 moves the quad in the bar's own space: position = the bar's position + the kept width, authored width = the hidden blade's width, the bar's y and band height. r49 moves the quad in the bar's own space (position = the bar's position + the kept width, authored width = the hidden blade's width). r50 logs that quad under every cut line (`fill copy rect=... pos=... authored=...`) so the next run reports the placement from the log. r50 ran clean and its quad line proves the placement (`fill copy rect=157 38 200 166 pos=47 authored=43` at ratio_bp=4133), with the bar's window reading [0, 280, 88, 304] and [0, 304, 88, 328]. `Txt_sharp`'s record settles the axis: Size 88x24, atlas `0,280,88,304`, tier bands along `v`; the blade's length is `u`. The `tex=0 156 87 440` numbers quoted in earlier records are in no log and the readings built on them are replaced. r51 takes the hidden columns from the bar's own band, drawn from the cut's right edge to the tip; r51 was never run. **Geometry tuning stops at r52, the forced-visibility candidate:** the copy is built with Key Quest Markers' complete recipe (its twelve style setters in its order and values, the texture id last, then `mTextureRect` main+0xa4fb58 given a pointer to the bar's live four floats), gets one set of values written once and never again (the bar's position pair +32.0 on y, the bar's authored 88x24, opaque magenta `0xFFFF00FF`), and is never written per frame: `write_dim` and the `fill copy` line are deleted. The mask's enter now reads the copy's and the bar's own rect, effective rect, 16-word matrix, position pair and authored pair before any write and prints them with the floats as floats. Prediction: a magenta full-length blade 32 units under the sharpness gauge, no pulse; confirmed by `pos=284.0 256.0`, `size=88.0 24.0`, a rect 88 by 24, the matrix's x row 1.0 and `eff=` equal to `rect=`. If those land and nothing shows, the next step is static research on the walker main+0xa494a0 for why a sibling of the scissor mask is not emitted - not r53. 23 host fixtures pass; verify PASSED with 33 signature windows (the twelve setter windows Key Quest Markers verifies are now checked here). **r52 ran on Eden 2026-10-31 and the copy is on screen:** a full-length magenta blade under the sharpness gauge, steady through sharpness drops and recoveries and across areas (`work/modern-sharpness-gauge/visual/r52/r52-magenta-photo.webp`, sha256 `a6fc2f82b722d66c76642666b4e47e1b17c76841148d993f10bce31453e4e638`; the log was not retained). That proves the node type, the Key Quest Markers recipe and the mask-sibling link draw, and the colour it came out in proves the MT `color` byte order is alpha, blue, green, red. **r53 is the design step:** the tester's colour `#202326` = `0xFF262320`, and the shadow written every frame from the accepted cut geometry in the units its own quad uses - the position pair is the bar's pair moved by the kept width (1:1 with the rect, the r8 log), the authored pair is the hidden length in authored units (`px * 88 / rect width`, the accepted runs log authored 88 against a 128 px rect), the atlas column at the cut's edge in the band the bar draws. At 0% on the measured bar: 18 units along, 49.5 wide, column 12; at 50%: 54, 24.75, column 37; at 100%: 1 unit; no gauge: width 0. The read-back stays. Prediction: a dark grey-blue shadow in the gauge's band from the cut's edge to the tip, steady, no glow, no pulse; the copy's `pos=`/`size=` lines confirm it. **r54 (the shadow behind the gauge) ran on Eden 2026-10-31 as a REGRESSION and is out:** one insertion, then 8 ms later `root.child=0x0 bar.parent=0x0` with 17104 links-lost lines to the log end, 17105 HUD-absent lines and zero fill lines, so the mask was disabled every frame and the gauge never clipped (`work/modern-sharpness-gauge/runs/r54-eden-2026-10-31.txt`, sha256 `26ae7bdb1e151959a7ba00534438460b07263dd12128baef8ee0e03827e8b87f`). The layering research it produced stands: paint order is walk order (main+0xa494a0 emits and consumes in visit order, no sort, no z value) and the GUI file's `Priority` (bar 0, glow 1, edge 2) ordered the chain at build time and is never read by the walker - so the layer is reachable by link order, and the position that draws the shadow before the bar is the position that broke the row. **The active candidate is r53, the fallback:** r52's proven tree shape (mask as the controller's first child, shadow as the mask's sibling, drawn last, outside the scissor) with the shadow carved to the part of the blade past the cut in `#202326` (`0xFF262320`, the alpha-blue-green-red order r52 proved). Source restored to r53 and rebuilt: the NRO hash matched the packaged candidate byte for byte (`bda3f7a1e70006a8e16c2a3b74f0b3e686f8ce4f177bcfc773f410565a031e6e`). 22 host fixtures pass; verify PASSED with 33 signature windows. r53 Gameplay NOT RUN. Candidate `build/modern-sharpness-gauge/candidates/r53/delivery/modern-sharpness-gauge-r53-candidate.zip`, sha256 `3130d2c0e8a12fdc602a5f23b4b81adb65895aed14e1f7edfd01e866e5b982ab`. |
| Modern Weapon Controls | r12 READY_TO_DISTRIBUTE | Stock-Forge maintenance build approved after static validation; no new gameplay run. |
| Please do Better | r24-forge151 READY_TO_DISTRIBUTE | Stock-Forge maintenance build approved after static validation; no new gameplay run. |
| Shared Urgent Quests | r1 DEVELOPMENT candidate (2026-10-21), gameplay NOT RUN | Records a rank-up urgent clear for an online client when the urgent is on that client's own board. Needs a two-instance session test. |
| HD Project, wiki cheats, DTI dumper support | LOCAL_ONLY | Local integrations. |

Candidates are under `build/NAME/candidates/VERSION/`, packaged releases under
`build/NAME/releases/VERSION/`. Superseded and accepted deliveries are preserved
unchanged under `backups/accepted/NAME/`, named after the change that replaced
them (for example `r30-before-status-damage/`).

Open device reports: Damage Numbers placement on real Switch and Android in
handheld mode (reported against r28; testers' exact loader/plugin hashes were
not supplied). Neither r29-diagnostics nor r30 was run on an affected device.
The r28 and r18 rebuilds do not bundle or verify the updated loader.

## Inputs and runtime paths

| Purpose | Path |
| --- | --- |
| Game dump/RomFS | `~/.local/share/eden/dump/0100770008DD8000/` |
| Sealed base game (v0) | `/mnt/storage2/ROM/Switch/Game/Monster Hunter Generations Ultimate™ [0100770008DD8000][v0]).xci` |
| Sealed 1.4.0 update (v262144) | `/mnt/storage2/ROM/Switch/Update+DLC/MONSTER HUNTER GENERATIONS ULTIMATE [0100770008DD8800][v262144].nsp` |
| Keys for the XCI/NSP | `/mnt/storage2/ROM/Switch/keys+firmware/` |
| Uninstalled library | `/mnt/storage2/ROM/Switch/cheats/mhgu/` |
| Eden packages | `~/.local/share/eden/load/0100770008DD8000/` |
| Eden log | `~/.local/share/eden/log/eden_log.txt` |
| Ryujinx-Nextendo packages | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/mods/contents/0100770008dd8000/` |
| Ryujinx-Nextendo logs | `/mnt/storage2/Programs/Ryujinx-nextendo/portable/Logs/` |
| Copied native inputs | `work/shared/game-exefs/` |
| Official Forge package/input | `work/shared/forge-1.5.1/` |
| Ghidra and saved DTI | `work/research-tooling/` |

The supplied dump is RomFS-only. Eden made it on 2026-10-01 while loading the
update from its external content folder (`Update+DLC/`), so it should hold base
and 1.4.0 merged; no file has been compared against the base yet. The update's
code is the copy in `work/shared/game-exefs/`. Library target is game 1.4.0, cheat build
FB08F1D20FD1204F, NSO FB08F1D20FD1204FE7070672777F869B. Verify actual launch
version/build before executable work. Folder presence proves no activation.
Trust the user's alternative-mod activation choices; investigate overlap only
when fresh evidence implicates it. After a reported run, inspect that emulator's
latest log before concluding.

HD resource priorities are in
[CLEANUP_HD_PROJECT.md](CLEANUP_HD_PROJECT.md). DTI extraction is not enabled
for gameplay. There is no automated in-game suite.

## Evidence and recovery

[COMPACTION.json](COMPACTION.json) records source revisions, archive/payload
hashes, removed paths, validation and space measurements for the 2026-10-15
cleanup. [WORKSPACE_EVIDENCE.json](WORKSPACE_EVIDENCE.json) preserves dated
workspace research and original migration receipts. Historical installed hashes
and settings are dated evidence, not a statement about current activation.
The recovery tag is `cleanup/before-stock-forge-20261015`; Git history is intact.
