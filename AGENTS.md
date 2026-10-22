# MHGU modding workspace

Host: Linux; the user's interactive shell is fish. MHGU Switch title ID is
0100770008DD8000, game 1.4.0. No automated in-game suite exists.
Start with README.md and docs/LOCAL_STATE.md, then read only what the task needs:

| Task | Read |
| --- | --- |
| New or changed mod, builds, settings/INIs, packaging, release READMEs | docs/DEVELOPMENT.md, then the mod's AGENTS.md and DEVELOPMENT.md |
| Forge plugin code, hooks, ABI, NRO builds, GUI insertion | `.agents/skills/mhgu-forge-modding/SKILL.md` (step-by-step: its `references/playbooks.md`) |
| Forge PC / GURecomp plugins and ports | `.agents/skills/mhgu-pc-modding/SKILL.md`, docs/GURECOMP.md |
| Game code, Ghidra/DTI, resources, IDs, native GUI research | `.agents/skills/mhgu-understanding/SKILL.md` (step-by-step: its `references/research-playbook.md`), docs/RESEARCH.md, Key Quest Markers DEVELOPMENT.md for GUI |
| Toolbox (START_TOOLS.sh, scripts/tool.sh), ARC/GMD/Kuriimu2, models | docs/TOOLS.md |
| HD Project resources, merge order, ownership | docs/CLEANUP_HD_PROJECT.md |
| GURecomp runs and logs | docs/GURECOMP.md |
| User-facing prose (READMEs, guides) | `.agents/skills/humanizer/SKILL.md` and the release README standard in docs/DEVELOPMENT.md |

## Always

- **Baselines.** Switch: unmodified Forge 1.5.1 (Fexty's fork of Jeffi's
  Forge) at `tools/forge-local/`, commit `b23e114a23f41c9a8e2fd34b2f4df2a2102d0ee1`.
  Rust: forge-rs 1.5.0 at `tools/forge-rs/`, commit
  `d1865b68e9b194eb3eacc8bd71bbf601a5fac63e`. PC: stock Forge PC 0.2.1 at
  `tools/forge-pc-local/`, with separate `<name>-pc` mods. Update checkouts from
  their official remotes. Never create duplicate clones/worktrees or restore the
  retired loader, Better Input, renderer, mutex or PC patches.
- **Authorization.** Preparing work never installs, activates, launches an
  emulator, changes emulator settings, edits saves, publishes or pushes. Commit
  validated, coherent changes locally after checking staged paths, run
  `python3 scripts/mod_distribution.py check` first and keep the custom hooks.
- **Preserve** unrelated work, original dumps, library inputs, saves, accepted
  artifacts in `backups/accepted/` and research inputs in `work/`.
- **Evidence.** Keep source, build, package, installation, activation, user
  acceptance and runtime evidence separate. Never present one as another.
- **Research first.** Search saved Ghidra/DTI before gameplay code:
  `./scripts/tool.sh research find QUERY --kind functions` (or symbols/types/dti).
  Imported base is 0x009c9000; subtract it for Forge offsets. One text byte and
  some imported type layouts differ from the target, so verify against real bytes.
- **Forge first.** Use Forge headers and APIs before private substitutes, and
  document each verified gap beside the workaround.
- **Versions.** Runtime changes get a new version. `DISTRIBUTION.json` is authoritative.

## Getting work done

- New mod: `python3 scripts/mod_distribution.py init NAME --kind plugin`, then
  work through "New plugin: definition of done" in docs/DEVELOPMENT.md.
- Phased plans (`work/*/PLAN.md`): finish the current phase completely,
  including its exit evidence and any candidate packaging it asks for. Then
  report what the next phase needs.
- A failed validation gate is evidence that your model is wrong. Check it
  against the logged values, and never loosen it to get further. After two
  gate failures in a row, go back to static research (forge-modding P3 step 4).
- When a tool refuses, read its error and the code that raised it before
  treating the refusal as a rule. Missing registration is not a prohibition.
- Record unknowns and keep going on the parts that don't depend on them. Never
  invent signatures, offsets, layouts, licenses or AI provenance.

## Runtime evidence and installation paths

- Dump/RomFS: `~/.local/share/eden/dump/0100770008DD8000/`.
- Uninstalled library: `/mnt/storage2/ROM/Switch/cheats/mhgu/`.
- Eden packages: `~/.local/share/eden/load/0100770008DD8000/`;
  log: `~/.local/share/eden/log/eden_log.txt`.
- Ryujinx-Nextendo: `/mnt/storage2/Programs/Ryujinx-nextendo/portable/Logs/` and
  `portable/mods/contents/0100770008dd8000/` under that installation.
- GURecomp: `/mnt/storage/Games/GURecomp/`; exported game is
  `Game/MONSTER HUNTER GENERATIONS ULTIMATE/`. Read its `user/log/suyu_log.txt`,
  `user/recomp_report.txt` and `mods/0100770008DD8000/Forge/forge.log` after a run.
  For the verified 0.3.1-test menu failure, use the process-local
  `SDL3_DYNAMIC_API=/usr/lib/libSDL3.so.0` workaround before proposing a rebuild.

Folder presence proves no activation, and library contents are not installed
mods. After a reported run or failure, read that emulator's latest log and
correlate the launched mods, build, hashes and exceptions before concluding.
Trust that the user does not co-activate alternative base/PC packages. Inspect
co-activation only when fresh evidence implicates it, and say so first. Do not
schedule monitoring unless asked.
