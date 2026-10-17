# Diagnose the failing boundary

## Collect current evidence

Identify the requested platform and latest launch first. Preserve its log, exact game/update build, emulator revision, loader version/hash, relevant NRO/assets and launch order. Installation inventory and configured folders alone prove no activation. The user's base/alternative packages are intentionally exclusive; investigate co-activation only when fresh evidence points to it.

Follow the failing stage: module load/imports, metadata/init, signature checks, JIT allocation, branch publication, callback, object/record validation, rendering, visible output, then transitions/persistence. A success at one stage proves nothing about later ones. Use bounded copied diagnostics outside hooks. Never save native pointers for deferred logging.

## Known failures and useful corrections

| Symptom / historical baseline | Cause or strongest finding | Response |
| --- | --- | --- |
| Hook failure after other plugins allocated JIT | Old per-hook CodeMemory pressure, including a recorded Rust Damage Numbers rollback retaining allocations | Verify actual Forge version and allocations. Current 1.5.1 pools at most two chunks; do not restore old loader patches |
| Crashes near Hook/metadata crossing | Historical binding/layout drift | Check compiled ARM32 Hook 24/Jit 28/metadata 70, exports, and callback ABI |
| Native badge constructor failure | Generic DTI placement slot was null | Checked MT allocation plus verified class constructor |
| Freeze after appending GUI child | Linked-tree count exceeded runtime map | Grow map 12 to 13 and cache 152 to 168, preserving aliases/ownership |
| Attached but invisible badge | INIT_PARAM 17/18 misdecoded; Mask 1 entered mask-writing | Immediate value decode and Mask 0, then verify material path |
| Valid title ID rejected | Resource declared Message 352, fixture assumed Text 384 | Derive subclass/getDTI from the resource |
| Controls report active but modifiers fail | Local index read from settings singleton | Read session index and correct player lookup; distinguish all input bit views |
| Fast A repeatedly dry-fires while reload is restricted | Candidate selection used strict current-action check too early | Separate capability selection `(p,1)` from native dispatch restriction `(p,0)`; retain native buffering |
| Number jumps to unrelated world location | Failed position copy became valid `(0,0,0)` | Explicit unavailable position; centre fallback while keeping captured damage |
| Texture/downsample overlay never appears | Reported Please do Better native downsample hooks did not execute | Current independent Forge overlay supersedes that experiment |
| Quest controls fail after DTI extraction | The 2026-10-03 dump completed but affected live game state | Remove extraction plugin and flag, restart, use the saved dump |

Key Quest Markers r17 and Damage Numbers r27 have dated user acceptance on Eden/Linux. This does not establish individual feature coverage, Ryujinx, or physical Switch gameplay. Modern Controls r12 and Please do Better r24-forge151 are stock-loader maintenance builds whose approval does not add a new gameplay run.

## Host crash versus guest/plugin failure

The 2026-10-05 Eden shutdown investigation correlated a host core with `HostTiming`, a null service manager, cheat VM HID lookup, and shutdown ordering. Its scoped conclusion was a probable emulator shutdown race, not evidence against a Forge patch. Cheats-disabled repeated shutdown reproduction remained untested. The logs referenced an older loader and emulator. Use that failure mechanism as a diagnostic example, not a diagnosis of a new crash or a reason to alter current settings.

Compare guest exceptions/hook signatures with host native stacks and matching emulator source. Retain uncertainty when core symbols were reconstructed or reproduction is missing. Never attribute a crash solely to the last co-installed plugin.

## Physical Switch feasibility

The loader is already native ARM32, so no PC-style port is needed. Its upstream README documents Ryujinx installation, including its PPTC/cache requirements. The workspace contains no physical Switch acceptance.

A conceptual CFW per-title arrangement is `sd:/atmosphere/contents/0100770008DD8000/exefs/subsdk1`, `exefs/main.npdm`, and `romfs/nativeNX/plugins/NAME.nro`. This is a feasibility layout, not a validated install recipe. The exact Atmosphère/package environment needs separate verification before deployment.

The concrete open issue is JIT permission/availability. Pinned libnx selects `JitType_CodeMemory` when syscall hints `0x4B` and `0x4C` are usable. Forge explicitly rejects its permission-transition fallback because concurrent slots need RW/RX aliases. The inspected Forge `config.json` omits those two syscalls. Inspect the final shipped `main.npdm`, actual hints, CFW/kernel behavior, and logs before proposing source changes. Editing the JSON alone proves no hardware fix.

An authorized console trial should establish Forge alone, then one NRO at a time, checking boot/load, graphics, controls, settings persistence, transitions, and performance. Retain rollback material and exact hashes. Compilation, import verification, emulator success, and generic CFW loader support do not establish physical compatibility.

Sources: `docs/RESEARCH.md` historical diagnostics; maintained mod development/evidence records; `tools/forge-local/{README.md,config.json}`, `source/forge/{plugin.cpp,hook.c}`, `libs/libnx/nx/source/kernel/jit.c`. Physical feasibility was source-inspected on 2026-10-16 and rechecked against these local files for this compilation; no hardware test occurred.
