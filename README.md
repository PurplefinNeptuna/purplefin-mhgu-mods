# Monster Hunter Generations Ultimate modding

Prepared on 2026-10-01 for the Switch title `0100770008DD8000`, using Eden on
Linux. The supplied dump and existing mod library have been inspected read-only.

**Current runtime baseline, 2026-10-02:** MHGU 1.4.0 uses our tested patched
Forge + patched Better Input package on unchanged Eden. Keep this baseline for
future mods. The source is preserved locally on `codex/forge-legacyctx14` in
`tools/forge-local/`. See [local branch maintenance](docs/FORGE_LOCAL_BRANCH.md)
and [completed runtime tests](docs/FORGE_BETTER_INPUTS_COMPAT_RUNTIME.md).

- Agent/project guidance: [AGENTS.md](AGENTS.md)
- Local baseline and package selections: [docs/LOCAL_STATE.md](docs/LOCAL_STATE.md)
- Wiki workflow and tool references: [docs/REFERENCES.md](docs/REFERENCES.md)
- Installed tools and launch instructions: [docs/TOOLS.md](docs/TOOLS.md)

The game dump lives at
`~/.local/share/eden/dump/0100770008DD8000/`.
The uninstalled mod/cheat library lives at
`/mnt/storage2/ROM/Switch/cheats/mhgu/`.
Eden's listed packages live at
`~/.local/share/eden/load/0100770008DD8000/`;
the initial 2026-10-01 report said they were not activated. Current package
presence, the patched Forge baseline, and activation are
recorded separately in `docs/LOCAL_STATE.md`.
Offline copies of the [reference repository](https://github.com/RTHKKona/MHGU-Modding)
and [wiki](https://github.com/RTHKKona/MHGU-Modding/wiki) are in `references/`.
These contain community research, binary templates, resource indexes, and ID
tables; their commits are recorded in `references/provenance.json`.

For the first mod, identify the target archive, copy it into `work/<name>/`,
record its hash, extract and edit the needed resource, then repack and validate.
Stage the resulting package in `build/<name>/romfs/nativeNX/...` with the
original relative path. Keep a description and reproducible edit recipe in
`mods/<name>/`.

The toolkit is installed locally. Run `./START_TOOLS.sh` for the desktop
launcher. Archive, conversion, audio, and startup smoke checks are documented
in `docs/TOOLS.md`, including tool-specific limits.

Initial workspace preparation did not change original game files, existing
mods, saves or Eden settings. Subsequent Forge compatibility work passed
automated and user-run in-game checks; its exact scope is recorded above.
The workspace Git repository remains on `main`; the local Forge repository
has its own patch branch and commit. Re-inspect other enabled mods before
combining packages.
