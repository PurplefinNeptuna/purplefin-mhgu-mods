# MHGU modding workspace

Host: Linux; the user's interactive shell is fish. MHGU Switch title ID is
0100770008DD8000, game 1.4.0. No automated in-game suite exists.
Start with README.md and docs/LOCAL_STATE.md, then read only what the task needs:

| Task | Read |
| --- | --- |
| New or changed mod, builds, settings/INIs, packaging, release READMEs | docs/DEVELOPMENT.md, then the mod's AGENTS.md and DEVELOPMENT.md |
| Forge plugin code, hooks, ABI, NRO builds, GUI insertion, ImGui, input/keybinds, reading game files, host differences (Recomp, gu-native) | `.agents/skills/mhgu-forge-modding/SKILL.md` (step-by-step: its `references/playbooks.md`) |
| A mod's settings in the game's Options (Mod Options) or topics in the game's help | `mods/purple-lib/API.md`; copy from Purple-lib Tester (every feature) and Please do Better (a shipping mod's page); rules in forge-modding `references/plugin-apis.md`, "A library that calls its clients" |
| Game code, Ghidra/DTI, resources, IDs, native GUI research, menus and screens | `.agents/skills/mhgu-understanding/SKILL.md` (step-by-step: its `references/research-playbook.md`). It holds only what the game does |
| How one of our mods works, or building something like it | "How each mod works" in the forge-modding `SKILL.md` (each mod's `docs/worked/`); a game window on another screen or in a quest: `references/gui-screen-reuse.md` |
| Toolbox (START_TOOLS.sh, scripts/tool.sh), Ghidra, ARC/GMD/Kuriimu2, models | docs/TOOLS.md |
| HD Project resources, merge order, ownership | mods/hd-project/README.md |
| User-facing prose (READMEs, guides) | `.agents/skills/humanizer/SKILL.md` and the release README standard in docs/DEVELOPMENT.md |

## Always

- **Baselines.** Switch: unmodified Forge 2.0.0 (Fexty's fork of Jeffi's
  Forge) at `tools/forge-local/`, commit `fd03ecb4c4ad16a02edb508c5a9b7731b84008d3`.
  Rust: forge-rs 2.0.0 at `tools/forge-rs/`, commit
  `112e0e032ad72db992870989384aba65331978c2`. Every mod still vendors
  forge-rs 1.5.0 and targets Forge 1.5.1 (each mod's `dependencies.lock.json`). PC: [MHGURecomp](https://github.com/morerokk/MHGURecomp)
  loads the same Switch Forge NROs, so there are no separate PC builds. Both
  baselines are submodules; update them from their official remotes. Each mod
  is its own private repo, `PurplefinNeptuna/mhgu-NAME`, checked out as the
  submodule `mods/NAME`; `hd-project`, `wiki-cheats` and `dti-dumper-support`
  are untracked local folders. History was rewritten on 2026-11-11 (vendor
  trees, retired mods, `backups/`, personal email and home path removed) and on
  2026-11-24 (mods moved to their own repos); older commit hashes resolve only
  in `/mnt/storage2/Programs/MHGU_Modding-pre-rewrite.git` and
  `/mnt/storage2/Programs/MHGU_Modding-pre-split.git`. Never create duplicate clones/worktrees
  or restore the retired loader, Better Input, renderer, mutex or PC patches,
  GURecomp or Forge PC ports.
- **Authorization.** Preparing work never installs, activates, launches an
  emulator, changes emulator settings, edits saves, publishes or pushes. Commit
  validated, coherent changes locally after checking staged paths, run
  `python3 scripts/mod_distribution.py check` first and keep the custom hooks.
  A mod change is committed in the mod's repo first, then its new pointer in
  the main repo, whose hook checks that mod's packages.
- **Preserve** unrelated work, original dumps, library inputs, saves and research
  inputs in `work/`. `backups/` is an optional local archive: agents do not delete
  it, the user may clear it, and nothing may depend on it. Each mod's last
  gameplay-accepted build stays under `build/NAME/` (see docs/LOCAL_STATE.md).
- **Scripted edits.** Prefer the edit tool. Append with `open(p, 'a')` or
  `cat >>`. Never write `open(p, 'w').write(open(p).read() + x)`: the `'w'`
  empties the file before the read runs. `work/` is gitignored, so nothing can
  undo a lost note there. Run `wc -l` before and after any scripted rewrite,
  and stop if the count dropped when it should have grown.
- **Tool names.** Call only the tools you were given, by their exact names:
  files are read with `read` (`file_path`, `offset`, `limit`), not `read_file`.
- **Evidence.** Keep source, build, package, installation, activation, user
  acceptance and runtime evidence separate. Never present one as another.
  Quote log values verbatim; a number that is not in the log is invented. Quote
  the tester's requirement verbatim too, and build to those words rather than a
  paraphrase. An empty search counts only after the tool finds a known positive.
- **Short source files.** Under 600 lines, one topic per file. A change that would pass
  that splits the file first, in its own behaviour-neutral commit. Files already longer
  may only shrink ("Source file size" in docs/DEVELOPMENT.md; the pre-commit hook checks).
  Every added or changed line holds one statement and stays within 120 characters, so never
  meet the limit by packing code onto fewer lines.
- **Tests outside source.** Rust tests go in the crate's `tests/` folder (`core/tests/*.rs`), never in a
  `#[cfg(test)]` block inside `src/`. Python and ARM tests stay in the mod's `tests/`. The pre-commit
  hook refuses an added `#[cfg(test)]` line (`scripts/code_rules.py`). WishFinder still has inline
  tests in 14 files; move a file's tests out when you change that file.
- **Know a test's cost before running it.** An emulator test that hooks every instruction in Python
  is slow; hook only the addresses it handles (KQM's `tests/native_adapter.py`: 152 s to 5 s). Run the
  one step you need, once. Prove a timing or measuring command on a
  fast step first: this shell is zsh without `bc` or `/usr/bin/time`, so time with Python's `time`
  around `subprocess.run`.
- **Humanize user-facing text (hard rule).** Every new or changed README, guide,
  release note, setting label, tooltip, in-game window or message, and log line a
  player reads MUST go through the full process in
  `.agents/skills/humanizer/SKILL.md` (read the whole file; mark the tells, draft,
  check, final) before it is built, packaged or committed. Show the final text to
  the user in the reply. No exception for short or temporary text. Read the skill
  file directly if the Skill tool does not list it.
- **American English (hard rule).** Every new or changed word in user-facing text, docs, comments
  and commit messages uses American spelling: color, gray, behavior, center, organize. The
  pre-commit hooks refuse British spellings on added or changed lines (`scripts/spelling_rules.py`:
  Markdown lines and string literals). A test that feeds British input marks the line above with
  `spelling: allow`. Fix older British text when you next edit that line.
- **Every language.** A change to a mod's user-facing text goes into every language
  file it ships, in the same change.
- **Research first.** Search saved Ghidra/DTI before gameplay code:
  `./scripts/tool.sh research find QUERY --kind functions` (or symbols/types/dti);
  `research xref`, `word`, `dis` and `vtable` read the checked main directly.
  Imported base is 0x009c9000; subtract it for Forge offsets, but not from vtable
  or DTI words, which are already main-relative. One text byte and some imported
  type layouts differ from the target, so verify against real bytes.
- **Answer from the source.** A question about what a mod or the game does is
  answered from the code that decides it, read in full, not from its docs. When
  the answer also depends on game data (RomFS rows, a save, an ini), read that
  data before answering. A reply never ends with "I didn't read X" or "to be
  sure I'd need Y" when X or Y can be read now: read it first.
- **Test the explanation.** Before writing down why something happened, name the data
  that would disprove it and look. Read-only ground truth is cheap: a save file, a mod's
  ini, a RomFS row. Values off by one constant across unrelated cases are a base or encoding
  question first. Checks: mhgu-understanding research playbook, step 6.
- **Base and unit at every boundary.** Every level, index or count that crosses a function,
  file or plugin has a stated base and unit. Game box and row levels count from 0; RomFS
  and the screen count from 1 (mhgu-understanding `references/equipment-box.md`).
- **Keys have two ends.** A key built here and compared there: read both ends, for every
  screen or state that reaches the comparison. A test whose fake builds the value proves
  nothing about the real consumer, so drive the compiled producer or real bytes.
- **Reuse proven paths.** When another mod here already does it (the game's language, the Korean patch, a
  save cache), read that mod's whole path and the skill reference first, then port the logic, helpers
  included, never a constant lifted out of it. Test the port on the same real data.
- **Calls have limits and answers.** Before calling an API in a loop, read its queue depth
  and limits. Check every return value, and report (sound, log, UI) what actually happened.
- **A measured rule covers what was measured.** State which rows, levels or screens a rule
  was checked on, and check the cases it is about to be applied to. A count in a doc is
  recomputed from the shipped artifact whenever that artifact changes.
- **Native writes.** Before writing a game field by hand, find what reads it and
  what gates that read, and use a setter if one exists. A value that reads back
  has been stored, not consumed.
- **Hook guards.** An entry hook that only runs code before or after the original
  stacks on another plugin's Forge hook, so it must not refuse one. Read the whole
  function to confirm that it is only that. Every other kind of hook keeps the
  exact-bytes gate (see "Chaining" in the forge-modding hooks reference).
- **Forge first.** Use Forge headers and APIs before private substitutes, and
  document each verified gap beside the workaround.
- **Refutations travel.** When a finding contradicts an earlier one, `grep -rn` for the old
  claim and correct every copy (skill references, DEVELOPMENT.md, the plan) in the same
  commit. A skill reference holds facts verified in bytes or a run, each with its source;
  the rest says "inference". Checks for premises, conflicting readings, partial matches
  and failed cross-checks: mhgu-understanding research playbook, step 6.
- **Versions.** A change to the runtime (NRO, data files, any payload the game loads)
  gets a new version. A change that leaves the runtime as it is (READMEs, notices, the
  API book, example code in the API kit, and `manifest.json` metadata such as the
  GameBanana link or description) ships in the current version:
  `python3 scripts/mod_distribution.py package NAME --refresh-support`. Wire a
  new payload into build, verify and package only in the phase that ships it.
  `DISTRIBUTION.json` is authoritative.
  Start, promote, withdraw and roll back only with `scripts/mod_lifecycle.py`, never by
  hand. Every `./build.sh` runs through the candidate guard ("Version and status changes"
  in docs/DEVELOPMENT.md); when it refuses, start a new version, never work around it.
- **No compatibility with unreleased versions (hard rule).** Keep backward compatibility only with
  what a READY_TO_DISTRIBUTE or PUBLISHED release wrote or read (its `DISTRIBUTION.json` status).
  An INI key, value, file format, API shape or setting that only DEVELOPMENT candidates ever had
  gets no fallback, migration or alias: rename or drop it freely, and remove any such code you find.
- **manifest.json.** Every new candidate or release ships the mod-manager
  `manifest.json` beside `romfs/`, registered as a payload (format: "Releases" in
  docs/DEVELOPMENT.md; rules: `scripts/mod_manifest.py`); `package` refuses one
  without it. Only each mod's last `manifest.txt` version re-packages with it.

## Getting work done

- New mod: `python3 scripts/mod_distribution.py init NAME --kind plugin`, then
  before its first commit make `mods/NAME` its own repo (private
  `PurplefinNeptuna/mhgu-NAME`) and add it as a submodule, so its source never
  enters the main repo. Then
  work through "New plugin: definition of done" in docs/DEVELOPMENT.md.
- Phased plans (`work/*/PLAN.md`): finish the current phase completely,
  including its exit evidence and any candidate packaging it asks for. Then
  report what the next phase needs. Do a plan's numbered steps in order, as
  written. Never swap one for something weaker (a timer for a destruction
  hook, a copied constant for a derived size). If a step can't be done, leave
  out the code that depends on it and report that step as the blocker. When a
  step finishes, update that step and every section that restates its facts, so
  the plan never contradicts itself.
- Before reporting work done, review it as someone else's change: "Review before you
  report" in forge-modding `references/validation-and-delivery.md`. Passing tests are not that review.
- When the user accepts a behaviour or closes a phase, run forge-modding P7
  (consolidate after acceptance) before new features or promotion: remove
  test scaffolding, stale wording and run history from source and README.
- A failed validation gate is evidence that your model is wrong. Check it
  against the logged values, and never loosen it to get further. After two
  gate failures in a row, go back to static research (forge-modding P3 step 4).
- When a tool refuses, read its error and the code that raised it before
  treating the refusal as a rule. Missing registration is not a prohibition.
- Record unknowns and keep going on the parts that don't depend on them. Never
  invent signatures, offsets, layouts, licenses or AI provenance.

## Writing project docs

Agents read these docs at the start of a task, small models included, so they
describe the project as it is now, not how it got here.

| Content | Goes in |
| --- | --- |
| Current state, commands, files, open items of one mod | `mods/NAME/DEVELOPMENT.md` |
| What the game does, found by any mod | The matching `mhgu-understanding` reference, with no mod named; its source in forge-modding `references/knowledge-sources.md` |
| How a mod works, hooks and designs | Its page in `mods/NAME/docs/worked/`, listed in forge-modding `SKILL.md` |
| A refuted approach | One line in that file's "Do not" list: what not to do and why |
| Run results: hashes, log counts, tester quotes | `mods/NAME/EVIDENCE.json` |
| Tester steps and log-line meanings, current version only | `mods/NAME/TESTING.md` |
| What a mod user needs | `mods/NAME/README.md` |
| A rule that holds across mods | The matching skill reference |
| Research in progress | `work/NAME/` |

- **Edit in place.** When a fact changes, correct it where it stands. Never add a
  dated section, per-run heading, "corrections" list, superseded paragraph or
  release table. Git keeps the old text.
- **State the fact, not the run.** Write "bit 17 is transform dirty, gate at
  main+0xa4969c", not "the r57 run showed". Name a version only when the version
  is the fact, such as which build was accepted.
- **One current-state paragraph.** Replace it for each version; never extend it with
  "rN is rM with…". It names the current build, its run state and the last accepted build,
  in 150 words or fewer. Design facts go in their sections, runs in `EVIDENCE.json`.
- **docs/LOCAL_STATE.md is a snapshot**: one short row per mod (version, status, run state,
  path). Replace the row; no history, quotes or hashes (hashes are in each build's `SHA256SUMS`).
- **The tester** is "the tester" or they/them, never he or she.
- **One home per fact.** Link instead of copying. When you remove a section or
  file, fix what points at it.
- **Size.** Keep a `DEVELOPMENT.md` under 500 lines and other project docs under
  350. Over that, merge facts and drop narrative. Don't split a file to hide it.
- **`work/` notes.** Write standing facts from the start, by topic, with no dated or
  per-pass headings: the pre-commit hook never sees `work/`, so nothing else stops it. `work/` is gitignored,
  so don't rewrite an existing note until the user agrees and a copy is archived.
- **Bulk pruning.** List the files and proposed cuts first, and cut only after the
  user reviews them. Confirm that every address in the old text still appears
  somewhere before you commit.

The pre-commit hook refuses per-run and dated headings, files over these sizes, and the history
checks in `scripts/doc_rules.py` (current-state length, version chains, previous-release history, long table cells).
In `.agents/skills/` it also refuses a sentence over 40 words, a line over 600 characters and a title
repeated as the first section heading. Split a long sentence into short ones, a list or a table, never
into a chain of clauses.

## Runtime evidence and installation paths

- RomFS: `/mnt/storage2/Programs/MHGURecomp/data/romfs/` (MHGURecomp's copy of the 1.4.0 RomFS). The Eden dump at
  `~/.local/share/eden/dump/0100770008DD8000/` keeps only `exefs` and `nso`.
- Uninstalled library: `/mnt/storage2/ROM/Switch/cheats/mhgu/`.
- Eden packages: `~/.local/share/eden/load/0100770008DD8000/`;
  log: `~/.local/share/eden/log/eden_log.txt`.
- Ryubing 1.3.3 (latest stable; what Ryujinx reporters run), the Ryujinx test
  target: `/mnt/storage2/Programs/Ryubing-1.3.3/app/Ryujinx`, portable data in
  `app/portable/` (mods `portable/mods/contents/0100770008dd8000/`, logs
  `portable/Logs/`, MHGU save `portable/bis/user/save/0000000000000001/`).
  Build steps are in docs/TOOLS.md. The user starts it with
  `/mnt/storage2/Programs/Ryubing-1.3.3/run.sh`, which copies the Eden save in
  and, after exit, back to Eden (Eden backups in `save-backups/eden/`), and
  copies each Eden mod folder's `exefs`/`romfs` into Ryubing's mods. Enabled
  state in `portable/games/0100770008dd8000/mods.json` is Ryubing's own; only a
  mod new to that file starts with Eden's state. Never
  symlink the save: LibHac deletes and renames slot `0` on every commit.
- Ryujinx-Nextendo: `/mnt/storage2/Programs/Ryujinx-nextendo/portable/Logs/` and
  `portable/mods/contents/0100770008dd8000/` under that installation. By the
  user's decision it counts as a superset of Ryubing: a mod that works on
  Ryubing is taken to work there, so install and test on Ryubing, not here.
- MHGURecomp: `/mnt/storage2/Programs/MHGURecomp/`, Linux build (source at
  `references/MHGURecomp/`). Each mod is a folder under `mods/` beside the
  executable, NROs at `mods/NAME/romfs/nativeNX/plugins/`, ordered by
  `mods/load_order.txt`; saves are in `~/.local/share/MHGURecomp/save/save_0/`.
  The user starts it with `/mnt/storage2/Programs/MHGURecomp/run.sh`, which
  copies the Eden save in and back (backups in `save-backups/eden/`), copies
  each Eden mod's `romfs` into `mods/` except those in its `EXCLUDE` list.
  Enabled state in `load_order.txt` is Recomp's own (`EXCLUDE` mods forced
  off); only a mod new to that file starts with Eden's state. Its log is
  `recomplog.txt` beside the executable, replaced each run: `run.sh` tees the
  launcher and game output there, so the game's own `log.txt` is not written.
- So Eden's `load/` folder is the one source of mod files for all three
  emulators: a mod added or updated there reaches Ryubing and MHGURecomp at
  their next `run.sh` launch. Enabling or disabling a mod in Eden does not
  reach a host that already lists it; toggle it in that host.
- Never use a dual-GPU launcher: one of this machine's GPUs is assigned to a VM.

Folder presence proves no activation, and library contents are not installed
mods. After a reported run or failure, read that emulator's latest log and
correlate the launched mods, build, hashes and exceptions before concluding.
Trust that the user does not co-activate alternative base packages. Inspect
co-activation only when fresh evidence implicates it, and say so first. Do not
schedule monitoring unless asked.
