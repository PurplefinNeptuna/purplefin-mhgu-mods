---
name: mhgu-forge-modding
description: Develop, change, debug, build, package and release native ARM32 Forge plugins (.nro) for Monster Hunter Generations Ultimate 1.4.0 on Switch, Eden, Ryujinx and MHGURecomp (PC). Step-by-step playbooks for new plugins, behaviour changes, user bug reports, adding hooks, consolidation after acceptance, promotion and doc refreshes, plus reference material on Forge/forge-rs APIs, hooks, native GUI insertion, ImGui rendering, input and keybinds, reading game files and textures, differences between Switch, emulators, MHGURecomp and gu-native, settings and release evidence.
---

# MHGU Forge Modding

Target: MHGU Switch 1.4.0, title `0100770008DD8000`, main build ID
`FB08F1D20FD1204FE7070672777F869B`. Loader: stock Forge 2.0.0 (Fexty's fork),
forge-rs 2.0.0; mods not yet moved target 1.5.1 and 1.5.0.

This skill is **how a plugin does things**: builds, hooks, GUI insertion,
rendering, input, files, hosts, other mods, delivery, and how each of our mods
works. What the game itself does (offsets, fields, formats, IDs) is in the
companion `mhgu-understanding` skill, which names no mod. When a fact here needs
a game detail, it links there instead of copying it. A new game fact goes there;
its source goes in [Knowledge sources](references/knowledge-sources.md).

## Start here

1. Read the workspace `AGENTS.md`, then `mods/NAME/AGENTS.md`, the top of
   `mods/NAME/DEVELOPMENT.md` and `mods/NAME/DISTRIBUTION.json` (authoritative status and
   hashes).
2. Pick the matching procedure in [Playbooks](references/playbooks.md) and
   follow it step by step. Each step names the exact command or file.
3. Open a topic reference below only when a step needs it. Before shipping
   anything, run the checklist in [Runtimes](references/runtimes.md).
4. Finish with the playbook's commit steps and report template.

## Game data

Where the RomFS, executables, Ghidra project and sealed files are: "Game data" in the `mhgu-understanding` skill. They are read-only; copy a file into the scratchpad or `work/NAME/` before unpacking or editing it.

## Words used in this skill

| Term | Meaning |
| --- | --- |
| NSO / `main` | The game's compressed executable. Read it with `scripts/mhgu_binary.py` `main_image()`, never by seeking into the file. |
| NRO | A Forge plugin binary, loaded from `romfs/nativeNX/plugins/`. |
| main+0xNNNN / main-relative | Offset from the start of the game's main module. All offsets in these skills use this form. |
| Ghidra address | Address in the saved Ghidra database. Subtract `0x009c9000` to get main-relative. |
| Object offset (+0xNN) | Field position inside a game object. Never subtract the image base from it. |
| DTI | The game's runtime class metadata (name, size, properties, vtable). It describes a class; it is not an instance. |
| Hook / detour | Forge replaces the first 8 bytes of a function with a jump to your code. |
| Trampoline | Forge's copy of those 8 bytes plus a jump back, used to call the original. |
| Interior tap | A hook in the middle of a function, not at its entry. Needs full register preservation. |
| GE / NZCVQ | ARM status flag groups. Restore NZCVQ; never write GE (`APSR_g`). |
| Candidate | A packaged DEVELOPMENT build under `build/NAME/candidates/rN/`. |
| Release | A READY_TO_DISTRIBUTE build under `build/NAME/releases/rN/`. |
| Accepted | The user reported it working on a named emulator for an exact payload NRO hash. A ZIP hash moves with any README refresh, so it does not identify a build. |

## Hard rules

**Always**
- Give every runtime change a new version `rN`. Old candidates and releases stay byte-for-byte.
- Verify every offset against the original NSO bytes before using it.
- Before writing a native field by hand, find what reads it and what gates that read. If a setter exists, use it. A field that reads back your value has only been stored; World Sharpness Gauge wrote fields nothing consumed in three separate rounds.
- Use Forge headers and APIs first. When you must go lower, write the verified gap next to the code.
- Keep PIC and `-nostartfiles` / `-Wl,-z,text` in every Rust/GCC NRO target.
- Install hooks all-or-nothing, with signature checks before any write and rollback on failure. A pre/post-only entry hook accepts another plugin's Forge hook over its first eight bytes ([Chaining](references/hooks-and-lifetimes.md#chaining-onto-another-plugins-hook)).
- Copy values out of game memory inside the hook; render and log from copies later.
- Run `python3 scripts/mod_distribution.py check` before every commit.
- Say exactly what was validated and what was not.

**Never**
- Install, enable, launch an emulator, change emulator settings, edit saves, publish or push unless the user asked for that exact action now.
- Edit original dumps, the uninstalled library, `backups/accepted/` or `work/` research inputs.
- Invent an offset, signature, struct layout, licence, author or AI-provenance claim.
- Use MHXX or PC layouts for Switch, or Ghidra bytes for signatures.
- Write `msr APSR_g` / `APSR_nzcvqg`, hold game pointers after a callback, do file I/O or locking inside a hook, or log every frame.
- Create `_backup` config files, or restore the retired loader, Better Input, renderer, mutex or PC patches.
- Call something "working" or "tested" when it was only built or unit-tested.
- Write run IDs (`r23`), run narratives or refuted approaches in source
  comments, or tester instructions in README.md. Refuted approaches go in
  DEVELOPMENT.md's "Do not" list, run results in `EVIDENCE.json`, and tester
  steps in `TESTING.md`. "Writing project docs" in the workspace `AGENTS.md` has
  the full rules.

## Stop and ask the user when

- The task needs installing, launching or a save/settings change.
- You need a game input that is not in `work/` or `build.local.json` (for example a different game version).
- Two sources disagree about an offset or layout and you cannot resolve it from the original bytes.
- The fix would change behaviour the user did not ask about.
- A promotion is implied but the user never said "ready to distribute" (or equivalent) for that version.

Otherwise keep going, record unknowns in DEVELOPMENT.md, and finish the parts that do not depend on them.

## Common mistakes

Topic-specific mistakes live with their topic: native GUI in [Native GUI extensions](references/gui-mistakes.md#common-mistakes), hosts, input and ImGui in [Runtimes](references/runtimes.md#common-mistakes). The rows below hold for every task.

| Mistake | Correct approach |
| --- | --- |
| Rebuilding a release to "promote" it | Promotion ships the existing candidate bytes unchanged (playbook P5). |
| Trusting a nonzero `Hook` record | Forge returns one even on failure. Check the trampoline bytes and executable mapping. |
| Hooking a function that starts with `ldr rX,[pc,#N]` | PC-relative instructions break when copied. Pick another site. |
| Refusing to load because another plugin hooked the same entry | A pre/post-only hook chains onto it. Read the whole function to confirm the hook is only that, then accept the foreign hook. |
| Reading the local player index from sUserInfo | Use session `0x188ca48` +0x30 (input-and-actions in mhgu-understanding). |
| Shipping a texture or table extracted from the game | Read it from the user's `app:/nativeNX/` at run time, sized from the file header, because other mods may replace it ([Game files at runtime](references/game-files-at-runtime.md)). |
| Fixing `check` failures by editing release folders by hand | Use `package NAME --refresh-support` for doc-only changes. |
| Pointing release `notices` at a `vendor/` license file | Fetched vendor is untracked. Copy the license into `licenses/` and list that path. |
| Comparing NROs built in different folders | Rust NROs embed absolute source paths. Build both at one path ([Rust dependencies](references/rust-builds.md#rust-dependencies)). |
| Proving a dependency change with an equal NRO alone | Host test harnesses compile for x86_64, where C `char` is signed. Run `test --host` too. |
| Concluding from an old log or a folder listing | Read the newest log and match installed hashes first (playbook P3). |
| Assuming a test double proves pixels | GPU commands are doubles. Visible output needs a user run. |
| Shipping one candidate per failed gate, adjusting the gate each time | Check each gate assumption against the logged values (playbook P3 step 4). After two gate failures in a row, return to static research. |
| Explaining a "looks like vanilla" report with a theory that makes the feature invisible by construction | The user's eyes decide the "visible on screen" stage. A positive log with a negative visual report means the log measures the wrong thing, or the run never reached values where the effect shows. Test with forced values. |
| Testing a visual mechanism only with live data | Build a forced-value candidate first, with extremes the eye cannot miss (for example 0/25/50/100%). Connect live data after the user sees each step, then remove the forced path with P7. |
| Rebuilding once per guess at a visual value | If no native model gives the value, ship a session-only tuner (P3 step 4): one run with a tuner found what four builds of photo measuring did not. |
| Working from a task's paraphrase of the tester | Copy the tester's words into the plan and `TESTING.md`, and check the build against those. A rewording once had the requirement backwards. |
| Leaving test controls, probes, "record" helpers and their log lines in after the user accepts | Every experiment is scaffolding. Run P7 after acceptance: delete what nothing live reads, fix stale names and messages. |
| Storing a value the user dialled in as absolute screen pixels | Store it relative to the rect it was measured on (offset or fraction), with a host test reproducing the accepted output. |
| Justifying each line with what run rN printed | A comment states the current contract. The evidence lives in EVIDENCE.json and Git. |
| Putting tester steps, log-line guides or stage-code tables in README.md | README.md is for mod users. Put tester material in `mods/NAME/TESTING.md` and the report. |
| Prepending a new "Current state:" paragraph per version, or extending it with "rN is rM with…" | Replace the one paragraph (150 words, enforced by `scripts/doc_rules.py`). Run logs do not go in DEVELOPMENT.md: put the fact in its section and a refuted approach in "Do not". |
| Changing a user's design decision so a candidate looks different | Design decisions belong to the user. Report the blocker and ask; never hide, drop or swap a designed element to get a visible change. |
| Reading numbers from a log that prints float fields as raw bits | Log floats as floats. Quote log values verbatim; a number that is not in the log is invented. |
| Explaining a mismatch with the first story that fits | Find data that would disprove it, then look. "One level low on three weapons, because the weapon in hand is not read" cannot be true of three weapons; a save file showed the field counts from 0. |
| Mixing bases across a boundary | Game box bits and smithy row `+9` count from 0, RomFS `mLevel` and the screen from 1. Convert once, at the boundary, and say so in the signature's comment. |
| Calling a plugin API once per item in one update and ignoring the answer | Read the queue size first. An 8-slot mailbox dropped most of a 15-step line, and the success tone still played. |
| Taking a constant from another mod without the helper that reads it | Port the whole path. Skin Loader took WishFinder's `0x1838bb4` but not its second load, read a static byte, and showed Korean in a Chinese game. Check the skill reference and the game's reader first. |
| Laying out a Unicorn probe's memory from your own reading of an address | Lay it out from the game's reader (disassembly) or real bytes, and use data a wrong reading would trip on (the base game's English table, whose binary bytes look like Hangul). Skin Loader's probe mirrored the missing load and passed. |
| Testing a key with a fake that builds the same key | The test agrees with itself. Assert against what the real finish path produces, in the native adapter. |
| Stretching a rule from the rows it was measured on | "Create row wins" was true at level 1 and wrong for the 127 create rows above it. Run a rule over the whole table and read the branch counts. |
| Treating an empty search as proof nothing references a function | Run the tool on a known positive first. A broken script's "no `bl` site" stood for weeks. Use `research xref` and `research word`, and check both. |
| Treating a hook that logged nothing as proof the function did not run | Log a call you know happens through the same hook first. A silent `0x4eef00` hook with no positive control sent WishFinder's sound research the wrong way for about a hundred builds; the function only ever runs for the BBQ Spit. |

## Topic references

| Task | Read |
| --- | --- |
| Step-by-step: new plugin, change, diagnose, add a hook | [Playbooks](references/playbooks.md) |
| Step-by-step: promote, support refresh, consolidate, finish, report | [Release playbooks](references/playbooks-release.md) |
| Loader, Rust/C++ APIs, metadata, ABI, standalone builds | [API and builds](references/api-and-builds.md) |
| Rust NRO relocations, fetched dependencies, the hardware-test loader | [Rust builds](references/rust-builds.md) |
| Plugin-to-plugin exports; a library that calls its clients | [Plugin APIs](references/plugin-apis.md) |
| Put a mod's settings in the game's Options (Mod Options) or its topics in the game's help | `mods/purple-lib/API.md`, then [Plugin APIs](references/plugin-apis.md#a-library-that-calls-its-clients-purple-lib) |
| Detours, trampolines, flags, TLS, transactions, rollback | [Hooks and lifetimes](references/hooks-and-lifetimes.md) |
| Game functions known to take a hook, and their pitfalls | [Hook sites](references/hook-sites.md) |
| Add game-owned GUI objects to a native tree | [GUI insertion](references/gui-insertion.md) |
| Reparent nodes, masks, cached quads, HUD movers, a row's end | [GUI masks and movers](references/gui-masks-and-movers.md) |
| Reuse a game screen, add pages to a panel, borrow a window, guide entries | [GUI screen reuse](references/gui-screen-reuse.md) |
| Native GUI mistakes to check before a build | [GUI mistakes](references/gui-mistakes.md) |
| ImGui, fonts/textures, INIs, save mounts | [Rendering and settings](references/rendering-and-settings.md) |
| What differs on Switch, Eden, Ryubing, MHGURecomp and gu-native | [Runtimes](references/runtimes.md) |
| Forge input, hotkeys, owning a press, Forge's menu key, MHGURecomp mouse/keybind calls | [Input and keybinds](references/input-and-keybinds.md) |
| Remapping weapon input, tap windows, replacing a native command | [Gameplay recipes](references/gameplay-recipes.md) |
| Capturing damage and placing numbers from a camera | [Damage capture](references/damage-capture.md) |
| Changing rewards safely | [Reward editing](references/reward-editing.md) |
| Armor mods, renaming their files, skins | [Armor skins](references/armor-skins.md) |
| Reading RomFS files, ARC entries, text and textures; writing into the save; CJK fonts; a one-time message window | [Game files at runtime](references/game-files-at-runtime.md) |
| Read another plugin's memory when it has no API (bridges) | [Plugin bridges](references/plugin-bridges.md) |
| Coexisting with KatLib/KatSmithy/UIScale, My Weapon Tree, DPS Meter, HD Project and others | [Other mods](references/other-mods.md) |
| MHGU Definitive Edition: what it patches, its quests | [Definitive Edition](references/definitive-edition.md) |
| Unverified leads read from other mods' code | [Leads from other mods](references/other-mods-leads.md) |
| Tests, exports, packaging, legal/support files, commits | [Validation and delivery](references/validation-and-delivery.md) |
| Failed initialization, logs, historical failures, physical Switch | [Diagnostics](references/diagnostics.md) |
| Workspace paths and evidence locations | [Workspace and sources](references/workspace-and-sources.md) |
| Which mod or run proved a game fact | [Knowledge sources](references/knowledge-sources.md) |

## How each mod works

Read the mod's page before changing it, and copy from the closest one when building something similar. Each mod's `DEVELOPMENT.md` keeps its current state, commands, files, "Do not" list and open items.

| Mod | Worked example |
| --- | --- |
| Damage Numbers | [Capture](references/worked/damage-capture.md), [crop, projection, assets](references/worked/damage-view.md) |
| ImGui Meter | [Counting a plugin's ImGui calls](references/worked/imgui-meter.md) |
| Key Quest Markers | [Classification and badges](references/worked/quest-badges.md) |
| Lock-on Target, Shared Urgent Quests, Village Quests in Hub | [Small hook mods](references/worked/small-hooks.md) |
| Modern Weapon Controls | [Remap and hooks](references/worked/weapon-controls.md), [bowgun reload](references/worked/bowgun-reload.md) |
| Multiplayer Roaming | [Design and hooks](references/worked/multiplayer-roaming.md) |
| Please do Better | [Capture and attribution](references/worked/reward-capture.md), [hooks and multiplier](references/worked/reward-multiplier.md) |
| Purple-lib | [Hooks and Options window](references/worked/purple-lib-window.md), [API, registry, help](references/worked/purple-lib-registry.md), [its clients](references/worked/mod-options-clients.md) |
| Skin Loader | [Paths, attach, skin files](references/worked/skin-loader.md), [raw skins, text, sync](references/worked/skin-loader-save.md) |
| WishFinder | [Hunter's Notes](references/worked/wishfinder-notes.md), [smithy page](references/worked/wishfinder-smithy.md), [upgrades and kinsects](references/worked/wishfinder-smithy-upgrades.md), [quest rows and pages](references/worked/wishfinder-quests.md), [guide, popups, jingle](references/worked/wishfinder-guide.md), [welcome window](references/worked/wishfinder-welcome.md), [API, save, hooks](references/worked/wishfinder-api.md), [tables](references/worked/wishfinder-tables.md), [other mods](references/worked/wishfinder-other-mods.md) |
| WishFinder bridge for My Weapon Tree | [Layout and update](references/worked/mwt-bridge.md) |
| World Sharpness Gauge | [Insertion and cut](references/worked/sharpness-gauge.md), [fill per tier](references/worked/sharpness-fill.md) |
| GE and cache audits across mods | [Audits](references/worked/ge-audits.md) |

For GUI plans, read [GUI insertion](references/gui-insertion.md) before treating
the quest-row recipe as a solution for another menu.

## Portable use

The Markdown references carry the findings. `agents/openai.yaml` is optional UI
metadata. Commands beginning `./scripts/tool.sh`, `python3 scripts/…` or
`./build.sh` need this workspace and its prerequisites. Without private
executables, fixtures or saved analysis, name the missing input and continue
only with source/host checks. Hardware compatibility remains unconfirmed.
