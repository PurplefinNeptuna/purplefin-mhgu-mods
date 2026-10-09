# Monster Hunter Generations Ultimate modding

MHGU Switch (`0100770008DD8000`) modding on Eden and Ryujinx/Linux.

## Mods

| Mod | Local release | Source and documentation |
| --- | --- | --- |
| Damage Numbers | r25 | [Guide and development](mods/damage-numbers/README.md) |
| Modern Weapon Controls | r11 | [Guide and development](mods/modern-weapon-controls/README.md) |
| Key Quest Markers | r2 | [Guide and development](mods/key-quest-markers/README.md) |
| Please do Better | r19-savehint | [Guide and development](mods/please-do-better/README.md) |

These releases are locally packaged and unpublished. Each mod's
`DISTRIBUTION.json` controls its status and payload hashes. Forge, HD Project,
wiki cheats and DTI dumper support remain LOCAL_ONLY. Verify all eight records
with `python3 scripts/mod_distribution.py check`.

## Workspace

- [Project instructions](AGENTS.md) and [local state](docs/LOCAL_STATE.md)
- [Tools and launchers](docs/TOOLS.md), [reference map](docs/REFERENCES.md) and [code research](docs/RESEARCH_TOOLING.md)
- [Maintained Forge source](docs/FORGE_LOCAL_BRANCH.md), [runtime evidence](docs/FORGE_RUNTIME_EVIDENCE.md) and [plugin rules](docs/FORGE_PLUGIN_GUIDELINES.md)
- [HD Project ownership and merge order](docs/CLEANUP_HD_PROJECT.md)
- [Distribution rules](docs/DISTRIBUTION_STANDARD.md) and [standalone development](docs/STANDALONE_MODS.md)

Start a mod with its local `build.sh`; copy and hash game inputs before editing.
Stage replacements under `build/<name>/romfs/nativeNX/` using original relative
paths. The dump, uninstalled library and emulator installation directories are
listed in local state. Preparation and packaging do not install or publish.

Current technical decisions and validation limits live with each mod.
Superseded experiment/release notes remain recoverable from Git history.
