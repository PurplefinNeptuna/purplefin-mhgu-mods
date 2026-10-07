# Monster Hunter Generations Ultimate modding

MHGU Switch (`0100770008DD8000`) modding on Eden/Linux; prepared 2026-10-01.
Dump/library inspection was read-only.

Current Eden `forge-patched` accepts base Better Input through its integrated
in-memory adapter. Preserve `tools/forge-local/` on `codex/forge-legacyctx14`.
[Source, runtime fingerprints and maintained recipes](docs/FORGE_LOCAL_BRANCH.md).
Retired mod folders, recipes and workspace artifacts have been removed;
tracked originals remain in Git history.

- HD Project cleanup and merge order: [docs/CLEANUP_HD_PROJECT.md](docs/CLEANUP_HD_PROJECT.md)
- Agent/project guidance: [AGENTS.md](AGENTS.md)
- Local baseline and package selections: [docs/LOCAL_STATE.md](docs/LOCAL_STATE.md)
- Wiki workflow and tool references: [docs/REFERENCES.md](docs/REFERENCES.md)
- Distribution standard and validation: [docs/DISTRIBUTION_STANDARD.md](docs/DISTRIBUTION_STANDARD.md)
- Installed tools and launch instructions: [docs/TOOLS.md](docs/TOOLS.md)
- Ghidra database and DTI dumper: [docs/RESEARCH_TOOLING.md](docs/RESEARCH_TOOLING.md)
- Modern weapon controls and English help: [r11 ready to distribute](mods/modern-weapon-controls/RELEASE.md)
- Progression key quest title markers: [r2 ready to distribute](mods/key-quest-markers/README.md)
- Please do Better: [r16 ready to distribute](mods/please-do-better/README.md), with earlier marker confirmation scoped to r14
- Open-only damage numbers: [r20 ready to distribute](mods/damage-numbers/RELEASE.md)
- Controls recheck against saved DTI/Ghidra evidence: [review](docs/MODERN_CONTROLS_RECHECK.md)

“Ready to distribute” requires a verified ZIP and support files under
`build/<mod>/releases/<version>/`. [Distribution standard](docs/DISTRIBUTION_STANDARD.md)
and `python3 scripts/mod_distribution.py check` enforce the same rules for all
current and future mods. Publication requires its own download URL and date.

Dump: `~/.local/share/eden/dump/0100770008DD8000/`. Uninstalled library: `/mnt/storage2/ROM/Switch/cheats/mhgu/`. Eden
packages: `~/.local/share/eden/load/0100770008DD8000/`. The 2026-10-01 report said inactive;
inventory/baseline/activation are separate in `docs/LOCAL_STATE.md`. Offline
[repository](https://github.com/RTHKKona/MHGU-Modding) and [wiki](https://github.com/RTHKKona/MHGU-Modding/wiki) snapshots in `references/`
contain research, templates, resource indexes and IDs; revisions:
`references/provenance.json`.

For the first mod, identify the target archive, copy it into `work/<name>/`,
record its hash, extract and edit the needed resource, then repack and validate.
Stage the resulting package in `build/<name>/romfs/nativeNX/...` with the
original relative path. Keep a description and reproducible edit recipe in
`mods/<name>/`.

The toolkit is installed locally. Run `./START_TOOLS.sh` for the desktop
launcher. Archive, conversion, audio, and startup smoke checks are in
`docs/TOOLS.md`, including tool-specific limits.

Initial workspace preparation did not change original game files, existing
mods, saves or Eden settings. Subsequent Forge compatibility work passed
automated and user-run in-game checks; its exact scope is recorded above.
The cleanup branch is `codex/cleanup-forge-hd-project`; the local Forge repository
has its own patch branch and commit. Re-inspect other enabled mods before
combining packages.

Future mods start as independent source folders. See [standalone development](docs/STANDALONE_MODS.md) for scaffolding, manual builds and export. The current cleanup releases have fresh static/compiled evidence and no new gameplay run.
