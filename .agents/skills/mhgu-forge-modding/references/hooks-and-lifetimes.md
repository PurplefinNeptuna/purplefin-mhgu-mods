# Hooks, native state, and lifetimes

Offsets refer to the verified MHGU Switch 1.4.0 main. Discover targets through saved analysis, then verify original executable bytes. [Diagnostics](diagnostics.md) explains evidence collection when installation fails.

## Select and verify a site

Record function purpose, callers, ARM/Thumb state, displaced instructions, arguments/return values, live registers/flags, and continuation. Function-entry AAPCS hooks and interior taps have different preservation contracts. Search every caller of a changed helper.

Ordinary ARM Forge hooks replace eight bytes with `0xE51FF004` (`ldr pc,[pc,#-4]`) and a detour address. The returned trampoline copies the displaced bytes and appends the same literal branch plus target+8. The pinned implementation copies instructions without a general relocation engine. Choose position-independent pairs or supply an explicitly verified relocation. PC-relative loads, branches, and partial instruction boundaries cannot be copied blindly. Do not infer Thumb safety from an ARM fixture.

Before publication, verify title/build scope, complete supporting signatures, checked address arithmetic, alignment, mapping permissions, nonoverlap, reserved hook ranges (a pre/post-only entry hook [may share a site](#chaining-onto-another-plugins-hook)), and instruction forms. A library filename/build ID is insufficient. Check the returned original pointer, executable mapping, displaced words, return instruction, and continuation.

Forge returns a `Hook` record even when creation fails; nonzero target/detour fields do not prove success. Supply and validate the original output where the installation needs a callable original. All hooks required for one feature must succeed before enabling it.

## Chaining onto another plugin's hook

An entry hook that only runs code before or after the original needs no guard against another plugin's Forge hook on the same entry. It must not refuse the site, list it as occupied, or disable itself when a later plugin covers its branch. Forge copies the foreign `ldr pc,[pc,#-4]` and its literal into the new trampoline as a pair, and that pair is position-independent, so the call runs newest hook, older hook, then the game's function from target+8.

Read the whole function and your detour before classing a hook this way. All of these must hold:

- Every path through the detour calls the original exactly once, with the arguments it received, and returns its result. A detour that skips the original, or changes an argument or the result, is not pre/post-only.
- It is an entry hook. Interior taps and direct patches depend on the exact bytes they replace.
- The function's callers and body were read: its return paths, tail calls, and anything branching to entry+4 (P4 step 3).
- The post part tolerates a foreign hook that skipped the game's function. It must check what it reads rather than assume the body ran.

What changes is narrow. The window still compares every byte past the first eight, and the build checks stay, so a different game build is still refused. Only the exact pair `e51ff004` plus any literal is accepted in those eight bytes; any other difference is a mismatch. Run the P4 step 3 relocation check against the original NSO bytes, and compare the trampoline against the live words captured just before hooking. `window_matches` in `mods/world-sharpness-gauge/core/src/lib.rs` is the current form, with a fixture covering all four cases. Copy it, since no mod builds against a sibling.

## Pool and publication behavior

At pinned Forge 1.5.1, `hook.c` owns at most two 16 KiB CodeMemory chunks. Slots align to eight bytes and are never reused. A normal eight-byte ARM displacement needs a 16-byte trampoline. Damage Numbers' eleven hooks use 176 bytes; the two quest-badge hooks use 32 bytes. Context hooks also allocate a 44-byte stub, rounded to 48, in addition to any original trampoline.

Forge requires simultaneous RW/RX aliases and rejects the permission-transition JIT fallback. Slots remain Forge-owned for process lifetime, including after a later plugin installation failure. Dropping a Rust `Hook` record does not release them. Repeated installation/retry is not a harmless cleanup strategy.

The loader synchronizes executable writes, but its public wrapper does not expose every checked publication/cache/rollback result. Maintained mods verify readback and synchronization around their own transactions. Private detour arenas exist only for documented requirements the public wrapper cannot meet. Do not add a second hook engine just to avoid understanding the existing one.

Successful ARM cache maintenance does not establish an emulator's translated-code freshness. Keep target instruction/readback checks separate from observed behavior under the exact emulator build. Ryujinx's pinned upstream Forge instructions require disabling PPTC and purging the listed caches, but executing those settings changes still needs task authorization.

Prepare originals before branch publication. In a checked private ARM transaction, write the destination literal before the LDR-PC opcode, flush/invalidate the appropriate aliases, issue barriers, and read back. This does not suspend other game threads or make a two-word write atomic. Concurrent cheats patching the same site remain a conflict.

## Registers, flags, and VFP

Preserve NZCVQ and all state live at the chosen boundary. Interior capture gateways may need all GPRs, LR, SP, d0 through d31, and FPSCR even where an ordinary function call permits clobbering. Retain original stack arguments and eight-byte call alignment. Never require `MSR APSR_g` or `MSR APSR_nzcvqg` in this workspace.

Audit GE producers/consumers through every displaced span, hook helper, native call, and continuation. `SEL` may consume GE. `MSR APSR_nzcvq` preserves NZCVQ without restoring GE; it neither clears GE nor proves it is dead. Existing eleven-site damage and quest-hook audits are site/build-specific. If GE cannot remain correct without unsupported writes, choose another site.

Hard-VFP native setters can take floats in s-registers. An `extern "C"` integer/pointer signature does not substitute for that contract. Use an audited ABI shim or verified field writes plus native dirty flags. Verify branch-with-link LR effects as well as general registers when replacing call sites.

## Nesting and ownership

Damage capture saves a 328-byte frame: continuation scratch 0, CPSR/FPSCR 8/12, d16 through d31 at 16, d0 through d15 at 144, r0 through r12/LR at 272. Around hooks record the caller before replacing LR, then pop the matching scope on return. Camera/HZV taps read registers before displaced code destroys the values. The exact frame belongs to this implementation.

Release mutable TLS borrows before invoking the native original, which may reenter the same hook. Never hold a Rust mutable reference across that path. Quest offers use a stack-owned frame containing UI identity and at most sixteen copied IDs, connected to nested row calls by SDK TLS. A guard restores the previous value, including on nested entry. No resource pointer/frame escapes the synchronous update.

Damage uses static mailboxes independent of TLS teardown: 16 producers, 256 records each, 64 capture scopes. A producer owns its slot and the consumer owns its cursor. Atomic words/publication tickets reject torn reads; overflow and pool exhaustion have bounded pass-through/drop behavior. Keep copied numeric evidence, not borrowed game objects, in asynchronous render queues.

## Rollback

Snapshot originals before modification. Roll back owned writes in reverse order, comparing each current word/pair against original and owned replacement. Restore partial publication only when ownership is proven. Leave foreign bytes untouched. Cache synchronization and readback are part of restoration even if a word already equals the original.

Upstream Patch objects snapshot current bytes and may restore on Drop when enabled. Keep rollback snapshots disabled outside controlled restoration so teardown cannot overwrite foreign patches. Retain valid original continuations and storage reachable from any residual branch. Incomplete restoration disables the feature, reports restart required, and stops live retry. Maintained mods do not provide hot uninstall/reload.

Sources: `tools/forge-local/source/forge/hook.c`; `mods/damage-numbers/src/{gateway.S,hooks.rs,runtime.rs}`, `core/src/{capture.rs,mailbox.rs}`, native pool/hook/ARM tests; `mods/key-quest-markers/src/{hooks.rs,offers.rs}` and ARM fixtures; `mods/please-do-better/core/src/{hooks.rs,platform.rs}`, `mods/please-do-better/src/gateway.S`; each mod's `DEVELOPMENT.md`.
