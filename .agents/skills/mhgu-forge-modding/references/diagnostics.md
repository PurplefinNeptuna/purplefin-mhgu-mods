# Diagnose the failing boundary

## Collect current evidence

Identify the requested platform and latest launch first. Preserve its log, exact game/update build, emulator revision, loader version/hash, relevant NRO/assets and launch order. Installation inventory and configured folders alone prove no activation. The user's base/alternative packages are intentionally exclusive; investigate co-activation only when fresh evidence points to it.

Follow the failing stage: module load/imports, metadata/init, signature checks, JIT allocation, branch publication, callback, object/record validation, rendering, visible output, then transitions/persistence. A success at one stage proves nothing about later ones. Use bounded copied diagnostics outside hooks. Never save native pointers for deferred logging.

## Known failures and useful corrections

| Symptom / historical baseline | Cause or strongest finding | Response |
| --- | --- | --- |
| NRO load crashes while applying dynamic relocations | r17/r27 Rust NROs each had six executable-text relocation targets from GCC startup routines despite PIC | Follow [NRO relocation requirements](api-and-builds.md#rust-nro-relocation-requirements): exclude GCC startup objects, enforce `-z text`, inspect final destinations and preserve linker output |
| `FATAL: interp: unsupported neon 3diff` on MHGURecomp | Recomp interprets NRO code, and `three_diff` in its `runtime/interp.c` accepts only VMULL, VMLAL and VMLSL. LLVM vectorizes a widening u32-to-u64 add over an array into `VADDW` | Disassemble the NRO text at the logged address minus the plugin's load address, and write the loop so it does not widen, or remove it. Scan the built NRO for `vaddw` before a Recomp run |
| `FATAL: unimplemented svc 0x4b` on MHGURecomp | Recomp's `runtime/kernel.c` has no CreateCodeMemory or ControlCodeMemory (0x4B, 0x4C), and an unknown SVC aborts the game instead of returning an error. Only a plugin with a private CodeMemory arena reaches this | Use Forge's hooks, whose trampolines Recomp provides. Plugins that use only SVCs 0x6, 0x29 and 0x5F run there |
| `Failed to load plugin ...: 0x00000616` on Eden | Result module 22 (RO) description 3, which reads as already loaded. The loader keys modules on the NRO build ID at header +0x40, and KatLib, UIScale and BetterBox all ship an all-zero ID, so only one of them loads (the description's meaning is from memory, not checked against Eden source) | Compare build IDs across the plugins folder. Ship every plugin with a unique build ID |
| Ryubing log ends at `PC:` after the stack and registers, with no error line; the PC is in an unnamed module | Undefined instruction. Ryubing 1.3.3's A32 decoder has no QADD, QSUB, QDADD, QDSUB, QSUB16, QASX or QSAX (it has QADD16, UQADD8/16, UQSUB8/16), and Rust's `i32::saturating_add`/`saturating_sub` emit QADD/QSUB. `-dsp` does not stop them: in ARM mode LLVM gates them on v5TE | Find the plugin as below. Replace the op with plain or u32-capped arithmetic, and reject the rest in `verify.py` (Wishlist and Damage Numbers have the gate) |
| Ryubing `Invalid memory access at virtual address 0x0000000000000000`, PC `main+0xb349c0`, LR `main+0xa4923c`, soon after a row insertion; or a GUI instance walk (`main+0x91c134`, `X[03]` `main+0x91bff8`) calling a zero vtable slot | The row's draw block was replaced and the old one freed while its objects still animated through `+0x64` into its prefix (World Sharpness Gauge r67) | Copy the prefix and move the pointers before freeing ([Native GUI extensions](native-gui-extensions.md)) |
| Hook failure after other plugins allocated JIT | Old per-hook CodeMemory pressure, including a recorded Rust Damage Numbers rollback retaining allocations | Verify actual Forge version and allocations. Current 1.5.1 pools at most two chunks; do not restore old loader patches |
| Crashes near Hook/metadata crossing | Historical binding/layout drift | Check compiled ARM32 Hook 24/Jit 28/metadata 70, exports, and callback ABI |
| Native badge constructor failure | Generic DTI placement slot was null | Checked MT allocation plus verified class constructor |
| Freeze after appending GUI child | Linked-tree count exceeded runtime map | Grow map 12 to 13 and cache 152 to 168, preserving aliases/ownership |
| Attached but invisible badge | INIT_PARAM 17/18 misdecoded; Mask 1 entered mask-writing | Immediate value decode and Mask 0, then verify material path |
| Valid title ID rejected | Resource declared Message 352, fixture assumed Text 384 | Derive subclass/getDTI from the resource |
| Controls report active but modifiers fail | Local index read from settings singleton | Read session index and correct player lookup; distinguish all input bit views |
| Fast A repeatedly dry-fires while reload is restricted | Candidate selection used strict current-action check too early | Separate capability selection `(p,1)` from native dispatch restriction `(p,0)`; retain native buffering |
| Number jumps to unrelated world location | Failed position copy became valid `(0,0,0)` | Explicit unavailable position; centre fallback while keeping captured damage |
| Numbers placed correctly docked but displaced in handheld (Switch, Android) | Game presents a smaller crop of the same swapchain; ImGui DisplaySize is the full allocation | Project with sFestaRender applied mDisplaySize +0xb8/+0xbc (Damage Numbers r30); no affected-device confirmation yet |
| No number for kinsect, poison, blast or mount damage | Those never pass the hit handler, or kinsect tags were unclassified | Dedicated hooks 8–10 and the kinsect tag rule (Damage Numbers r31+; see mhgu-understanding damage reference) |
| Texture/downsample overlay never appears | Reported Please do Better native downsample hooks did not execute | Current independent Forge overlay supersedes that experiment |
| Quest controls fail after DTI extraction | The 2026-10-03 dump completed but affected live game state | Remove extraction plugin and flag, restart, use the saved dump |
| Inserted mask hides the gauge; box reads `left == right` | Recycled anchor modes at mask +0xa0, an empty x row at +0x10, then a width fed from an animated field | The field table in [Native GUI extensions](native-gui-extensions.md#clip-with-a-scissor-mask) |
| Gauge gone in the next quest, row never rebuilt | Nodes reachable through two chains were freed twice and poisoned the allocator | End the old chain at root +0x6c |
| Game freezes on inserting a built node, no insertion line on any path | Texture vtable slot 0x00 called as a constructor (r45) | Standalone constructor main+0xa4f60c on a zeroed block |
| Copy built with `dim=0x0`, refused at its texture step | `Texture` setter returned early: +0x78 unset, or +0x64 zero | Write both first, run the setter last |
| New node laid out at `rect=0 0 128 128`, matrix never composed | Bit 17 cleared on a node or a parent | Keep bit 17 on every node you add |
| Atlas or colour writes land in the log and the sprite never changes | The quad is cached and nothing marked it dirty | Use the setter |

## Read a log and a photo

Run-independent noise in Eden logs, not evidence against a plugin unless something else connects it: `maxwell_3d.cpp:392 ... assert method == executing_macro + 1` (r62's began 6271 s before the mod's insertion), and a PANIC or host `Unhandled SIGSEGV` shortly after `ForceStop: Force stopping EmuThread` (r59's was 7 ms later, with `nn::hid::VibrationNode::Update()` in its backtrace). Check timing against the mod's own lines before setting a line aside.

A row's death reads as words turning to freed-heap fill at unchanged addresses: `0x727272`, `0xffffff`, `0xffeaeaea`, `0xff7f7f7f`, `0x4d4d4d`. A rect of `0 0 0 0` comes first. A captured pointer whose word reads one of these is gone, and live relinked pointers there mean the row is mid-teardown (r28).

To measure a photo, use the log as the ruler: fit the image scale on two logged box edges, then read the ink against it (r35 gave 1.4 image px per GUI px, r41's fit landed within 1 to 2 image px on all four crops). Downscaled crops carry a few px of noise, so don't treat a single measurement as a mechanism.

Key Quest Markers r17 and Damage Numbers r27 have dated user acceptance on Eden/Linux. This does not establish individual feature coverage, Ryujinx, or physical Switch gameplay. Modern Controls r12 and Please do Better r24-forge151 are stock-loader maintenance builds whose approval does not add a new gameplay run.

## Read a Ryubing crash

Ryubing (`KProcess.cs`, `Syscall.cs`) prints `Guest stack trace` and `Guest CPU registers` for three guest faults and adds a line for two of them: `Invalid memory access at virtual address ...` for a bad access and `The guest program broke execution!` for `svcBreak`. An undefined instruction adds nothing, so a log that ends at `PC:` is one. `PC` is the start of the translated block, not the faulting instruction, and on ARM32 `X[13]`/`X[14]` are SP and LR. Eden logs an unmapped access (`Unmapped Read`, `Unmapped @`) and keeps running, so a latent bad access can pass on Eden and stop Ryubing.

Ryubing names only the game module, as `Rabbit_RoApplicationMTFMasterReleaseNX.nss:OFFSET` (main-relative), and `mhguForge:OFFSET`. Plugin NROs show as bare addresses. `mhguForge:0x4af4` is the return address in `forge_plugin_onUpdateHook` after a plugin's `forge_onUpdate`. Forge maps NROs page-aligned, so match the low 12 bits of `PC` and of the return address on the stack against each installed NRO: a call at return address minus 4 whose callee contains `PC`.

## Host crash versus guest/plugin failure

The 2026-10-05 Eden shutdown investigation correlated a host core with `HostTiming`, a null service manager, cheat VM HID lookup, and shutdown ordering. Its scoped conclusion was a probable emulator shutdown race, not evidence against a Forge patch. Cheats-disabled repeated shutdown reproduction remained untested. The logs referenced an older loader and emulator. Use that failure mechanism as a diagnostic example, not a diagnosis of a new crash or a reason to alter current settings.

Compare guest exceptions/hook signatures with host native stacks and matching emulator source. Retain uncertainty when core symbols were reconstructed or reproduction is missing. Never attribute a crash solely to the last co-installed plugin.

## Physical Switch feasibility

The loader is already native ARM32, so no PC-style port is needed. Its upstream README documents Ryujinx installation, including its PPTC/cache requirements. The workspace contains no physical Switch acceptance.

A conceptual CFW per-title arrangement is `sd:/atmosphere/contents/0100770008DD8000/exefs/subsdk1`, `exefs/main.npdm`, and `romfs/nativeNX/plugins/NAME.nro`. This is a feasibility layout, not a validated install recipe. The exact Atmosphère/package environment needs separate verification before deployment.

The concrete open issue is JIT permission/availability. Pinned libnx selects `JitType_CodeMemory` when syscall hints `0x4B` and `0x4C` are usable. Forge explicitly rejects its permission-transition fallback because concurrent slots need RW/RX aliases. The inspected Forge `config.json` omits those two syscalls. Inspect the final shipped `main.npdm`, actual hints, CFW/kernel behavior, and logs before proposing source changes. Editing the JSON alone proves no hardware fix.

That permission concern describes the pinned stock loader. The separately reviewed [Lawrence hardware-test fork](api-and-builds.md#lawrences-hardware-test-loader) adds CodeMemory permissions and protected-code-write/startup fixes. Its source documents `sd:/forge-loader.log`; collect that file and the exact loader/NRO hashes after an authorized trial. The source comparison supports expected 1.5.1 API compatibility, while hardware acceptance remains unconfirmed. Both the loader and NRO must satisfy their own relocation requirements.

An authorized console trial should establish Forge alone, then one NRO at a time, checking boot/load, graphics, controls, settings persistence, transitions, and performance. Retain rollback material and exact hashes. Compilation, import verification, emulator success, and generic CFW loader support do not establish physical compatibility.

Sources: `docs/RESEARCH.md`; maintained mod development and evidence records; `tools/forge-local/{README.md,config.json}`, `source/forge/{plugin.cpp,hook.c}`, `libs/libnx/nx/source/kernel/jit.c`. Physical feasibility was source-inspected on 2026-10-16 and rechecked against these local files for this compilation; no hardware test occurred.
