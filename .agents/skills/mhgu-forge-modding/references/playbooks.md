# Playbooks: build, change, diagnose, hook

Use these when you know *what* to do but not the exact steps. Run commands from
the workspace root `/mnt/storage2/Programs/MHGU_Modding` unless a step says
"from the mod folder". `NAME` is the mod folder name (for example
`damage-numbers`), `rOLD`/`rNEW` are version labels such as `r35`/`r36`.

Every playbook ends with the same rules: commit locally only after the full
check passes, and never install, launch, edit saves, publish or push unless the
user explicitly asks for that exact action in this task.

## Pick a playbook

| The user asks... | Playbook |
| --- | --- |
| "Make a new mod that does X" | [P1 New Switch plugin](#p1-new-switch-plugin) |
| "Make X also do Y" / "it misses Z" | [P2 Change a mod's behaviour](#p2-change-a-mods-behaviour) |
| "It crashes / does nothing / shows wrong thing" | [P3 Diagnose a user report](#p3-diagnose-a-user-report) |
| "Hook function F" (as part of P1 or P2) | [P4 Add a native hook](#p4-add-a-native-hook) |
| "It works, make it ready to distribute" | [P5 Promote a candidate](playbooks-release.md#p5-promote-a-candidate) |
| "Fix the README/docs" of an already released mod | [P6 Support-only refresh](playbooks-release.md#p6-support-only-refresh) |
| "It's accepted" / a phase closed / "clean it up" | [P7 Consolidate after acceptance](playbooks-release.md#p7-consolidate-after-acceptance) |
| Read another plugin that has no API / update such a bridge | [Bridges to another plugin](plugin-bridges.md) |

## P1 New Switch plugin

1. **Scaffold.** `python3 scripts/mod_distribution.py init NAME --kind plugin`.
   It refuses an existing folder and an invalid name (lowercase words joined by
   `-`). It creates `mods/NAME/` with a C++ `src/plugin.cpp`, `build.sh`,
   Forge/libnx/cimgui pins (`prepare --fetch` downloads them), `mod.json`
   (version `r1`), `DISTRIBUTION.json` (DEVELOPMENT), `EXPORT.json`, tests and
   licence files.
2. **Configure inputs.** From the mod folder: copy `build.local.example.json`
   to `build.local.json` (ignored by Git) and point it at copied inputs. Never
   point it at the original dump or an emulator folder.
3. **Build the empty plugin first.** From the mod folder: `./build.sh doctor`,
   then `./build.sh build`. Fix toolchain problems now, before adding code.
4. **Keep the ABI rules from the scaffold.** `PluginInitParam` (70 bytes, name
   at offset 6) is declared locally with a `static_assert` because Forge
   defines it only in its private `source/forge/plugin.cpp`. That is the one
   allowed local declaration. Everything else comes from Forge headers:
   `#include <forge/log.h>`, `<forge/hook.h>`, `<forge/mem.h>`,
   `<forge/singleton.h>`, `<forge/fs.h>`. Wrap `<forge/mem.h>` in
   `extern "C" { }` (it has no C++ linkage guard). Never hand-declare a Forge
   function. Request version `{1, 5, 1}` in `forge_onLoad`.
   Rust plugin: copy `mods/key-quest-markers/` (target JSON, `build.rs`, `fetch_vendor.py`,
   `.gitignore`, `licenses/`), then `./build.sh fetch` (api-and-builds.md); `init` is C++ only.
   Rust targets must keep `"relocation-model": "pic"` and the GCC pre-link
   args `-nostartfiles`, `-Wl,-z,text` (see api-and-builds.md).
5. **Research.** Follow the `mhgu-understanding` skill. Write every offset you
   rely on, with its source and how you verified it, into `mods/NAME/DEVELOPMENT.md`.
6. **Implement.** Add hooks with [P4](#p4-add-a-native-hook). Keep game logic in
   small pure functions so host tests can call them without the game.
7. **Settings (only if needed).** One closed-by-default tree row in
   `forge_onImGuiRender`, one primary INI, explicit Save. See
   rendering-and-settings.md. No settings means an empty `forge_onImGuiRender`.
8. **Test.** Add host tests in `tests/`, then from the mod folder:
   `./build.sh test --host`, `./build.sh test`, `./build.sh verify`.
9. **Write the README** with the release README standard in `docs/DEVELOPMENT.md`
   (Requirements, Installation, Usage, Update and removal). Run it through the
   humanizer skill. Candidate ZIPs ship this README.
10. **Register the candidate** in `DISTRIBUTION.json`: `version`,
    `package_name`, `archive` = `NAME-rN-candidate.zip`, `candidate` =
    `build/NAME/candidates/rN/delivery`, `candidate_builder` = `scripts/build.py`,
    and a `gamebanana` record (copy the shape from another mod; fill AI
    disclosure truthfully). Status stays `DEVELOPMENT`.
11. **Package and check.** `python3 scripts/mod_distribution.py package NAME`,
    then `python3 scripts/mod_distribution.py check`. Both must pass.
12. **Commit** (see [Finish](playbooks-release.md#finish-every-playbook)) and report with the
    [report template](playbooks-release.md#report-template).

## P2 Change a mod's behaviour

1. Read `mods/NAME/AGENTS.md`, `DEVELOPMENT.md` and `DISTRIBUTION.json`.
   Note the current version and status.
2. **Choose the version.** If the current version is READY_TO_DISTRIBUTE or
   was ever handed to the user for testing, any runtime change needs `rNEW`.
   If it is an unrun DEVELOPMENT candidate nobody has tested, you still create
   `rNEW` when its bytes were already packaged; the old candidate folder stays
   as it is.
3. **Preserve the released bytes.** If you are replacing a READY release,
   copy its `build/NAME/releases/rOLD/` folder and the mod's
   `DISTRIBUTION.json`/`EVIDENCE.json` into
   `backups/accepted/NAME/rOLD-before-<short-change-name>/` before editing.
   Agents never edit or delete anything in `backups/accepted/`, but the user may clear
   it, so nothing may depend on it.
4. **Bump every version string.** Find them with
   `grep -rn 'rOLD' mods/NAME --exclude-dir=vendor --exclude-dir=__pycache__`.
   Typical places: `mod.json`, `DISTRIBUTION.json` (`version`, `archive`,
   `candidate`, payload `source` paths, `reason`), `scripts/paths.py`
   (build/work folders), `scripts/build.py` (archive name, manifest version),
   the plugin name label in `forge_onLoad`, the startup log line, tests that
   assert the label, `README.md`. Leave dated records in EVIDENCE.json alone. If this version removes a feature, control or
   mode, also grep its words in `src/`, `core/src/` and log strings, and fix
   every comment, name and message that still describes it.
5. Make the change. If it needs a new hook, use [P4](#p4-add-a-native-hook).
   Add or update a host test that fails without your change.
   - **One structural change per candidate.** If you have two fixes, ship the
     one the last run proved and hold the other. Don't stack a new candidate
     on one the user hasn't run. Replace that candidate instead, and tell the
     user which one to run.
   - **Test the state after your writes.** When the change writes game state
     (links, flags, cache pointers), build the fixture's tree, run your write
     on it, and then run two things over the result: a port of the native
     consumer (for GUI trees, the decompiled walker) and your own code that
     runs on later frames (per-frame readers, apply, restore). Assert what
     they produce: for a walker, every node visited exactly once, every enter
     entry matched by its exit, and the exact cache length. A fixture that
     only checks the state before your writes proves nothing about them.
   - **Trace the consumer of each native write.** Name the function that reads
     the field and any dirty bit or cache in front of it. No host fixture can
     cover game code, so this is the only check before a run.
6. From the mod folder: `./build.sh build`, `./build.sh test`, `./build.sh verify`.
7. Update `DISTRIBUTION.json` `reason` and evidence summary, `DEVELOPMENT.md`
   (replace the one current-state paragraph at the top, correct the facts in
   their sections, and add any refuted approach to "Do not". No run logs),
   and `docs/LOCAL_STATE.md`. That row holds current status, the release path
   and the payload hash only; dated run results belong in `EVIDENCE.json`. Say
   `Gameplay NOT RUN`.
8. **Review the premise before asking for a run.** Re-read what this version
   assumes against the decompile or bytes, and against the tester's own words.
   If it fails, withdraw the candidate and say why; this has saved whole runs.
9. `python3 scripts/mod_distribution.py package NAME`, then `... check`.
10. Commit and report.

## P3 Diagnose a user report

Do not change code until step 5.

1. **Which run?** Ask or determine: emulator (Eden, Ryujinx, MHGURecomp,
   real Switch), date/time, which mod version they think they ran.
2. **Read the newest log**, not an old one:
   Eden `~/.local/share/eden/log/eden_log.txt`; Ryubing 1.3.3
   `/mnt/storage2/Programs/Ryubing-1.3.3/app/portable/Logs/` (newest file;
   Ryujinx-Nextendo counts as a superset, so test on Ryubing);
   MHGURecomp `/mnt/storage2/Programs/MHGURecomp/recomplog.txt` (its `run.sh`
   replaces it each launch). Copy it to
   `work/NAME/runs/rN-<emulator>-<YYYY-MM-DD>.txt` before anything else,
   because the next launch overwrites it. Eden also keeps only a rolling
   100 MiB window, so a long session can lose a build's lines while it runs.
   Ask for a copy after every run, and for the tester's exact words.
3. **Match the bytes.** `sha256sum` the installed NRO/assets (read-only) and
   compare with `DISTRIBUTION.json` payload hashes and the candidate folder.
   If they differ, the report is about a different build; say so.
4. **Find the failing stage.** Walk this list and stop at the first stage the
   log does not prove: module loaded -> `forge_onInit` startup line -> hooks
   installed (no "restored originals") -> hook entered -> classification /
   decision -> object or draw created -> visible on screen -> survives menu and
   scene changes -> settings persist after restart. Compare with the known
   failures table in diagnostics.md.
   - **Check the gate against the log.** When a validation gate fails, open
     its code and list every assumption it makes (which node is whose parent,
     child or sibling; field meanings; sizes). For each one, find the logged
     value that confirms or refutes it. Write refuted assumptions into the
     research notes as refuted *before* changing code. Then grep the mod's
     code comments, DEVELOPMENT.md and README for the refuted claim and fix
     them in the same change. The mod's own tree and sample lines often
     already answer the question.
   - **Log says it worked, the user saw no change?** The log measures the
     wrong thing, or the run never reached values where the effect shows.
     Find what it misses before writing code; never explain the report away.
     A forced-value candidate settles it (SKILL.md, Common mistakes).
   - **Same build, new gate later in the run** (for example after a quest
     ends) means a stale pointer, not a new layout. Find where the object is
     destroyed and clear the capture there.
   - **Two candidates in a row failed on validation gates?** Stop building
     candidates. Never relax, delete or redefine a gate so the next build gets
     further: a gate that fails on live data means the model behind it is
     wrong. Go back to static research (decompiled code, original bytes), and
     report the blocker if that research cannot settle it.
   - **Two candidates in a row with no visible effect?** This counts as two
     gate failures, even when every logged gate passed. Stop and go back to
     static research. The next candidate is a forced-value one whose effect
     the eye cannot miss.
   - **The mechanism works and only a value is unknown?** Give the tester a
     session-only tuner instead of rebuilding per guess: one closed Plugin UI
     row, sliders that write a draft, Apply and Reset, and a line saying which
     state is live. Bake the accepted value into the build and remove the panel
     with P7. Check that an untouched control leaves the same state as Reset.
   - **One hypothesis per candidate.** Before the user runs a candidate,
     write in the report what they will see and which logged values will
     confirm it. A run that matches neither prediction refutes the
     hypothesis; do not reinterpret it afterwards.
5. **Reproduce statically.** Write a host or ARM fixture that fails the same
   way with the old build (`mods/key-quest-markers/tests/native_adapter.py` shows the method). Then fix with [P2](#p2-change-a-mods-behaviour).
6. If you cannot tell which stage fails, build a diagnostic candidate (its own
   version, bounded logs outside hooks, at ERROR level because stock Forge
   filters below ERROR) and ask the user to run it. Say exactly what to do and
   which log to send back.
7. Report what the log proves, what it does not, and the next step.

## P4 Add a native hook

1. **Find the function** with the research tools (mhgu-understanding skill):
   `./scripts/tool.sh research find QUERY --kind functions`. Convert the Ghidra
   address: `main_offset = ghidra_address - 0x009c9000`.
2. **Read the original bytes** at that offset from the copied main NSO through
   `scripts/mhgu_binary.py` `main_image()` (it checks the hash and decompresses
   segments). Do not read bytes from Ghidra: one text byte differs.
3. **Check the first 8 bytes can be moved.** Forge copies them into a
   trampoline without relocating. Reject the site if either instruction is
   PC-relative (`ldr rX,[pc,...]`, `adr`, `b`, `bl`), or if anything branches
   to the second instruction. A typical safe entry is `push {...}` followed by
   `sub sp, sp, #N`.
4. **Write the contract down** in DEVELOPMENT.md: offset, function purpose,
   arguments and return value, callers, whether it is an entry hook or an
   interior tap, and which registers your code reads.
5. **GE/flags audit.** Scan the hooked function and its continuation for
   `SEL`, `MRS`, `MSR` and parallel add/subtract instructions. If none, GE is
   dead there; write that result down. Restore flags with `msr APSR_nzcvq`
   only. Never use `APSR_g` or `APSR_nzcvqg` (Ryujinx cannot translate them).
6. **Add a signature window**: the exact original bytes your code expects,
   checked before any hook is installed. Startup must refuse to install when
   they differ. A pre/post-only entry hook also accepts another plugin's Forge
   hook over the first eight bytes, once the whole function has been read
   ([Chaining](hooks-and-lifetimes.md#chaining-onto-another-plugins-hook)).
7. **Install all-or-nothing.** All hooks for one feature succeed, or roll back
   the ones you installed and stay disabled. Check each returned trampoline
   (original 8 bytes, then `e51ff004`, then target+8).
8. **Inside the hook**: copy numbers out, never keep game pointers past the
   callback, never do file I/O or take locks, never log every call.
9. Count pool use: each ordinary hook takes a 16-byte slot; Forge has at most
   two 16 KiB chunks shared by all plugins.
10. Add a fixture that runs the hook path (host double or Unicorn ARM test).
