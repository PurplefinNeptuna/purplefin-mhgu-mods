# Monster Hunter Generations Ultimate modding

MHGU Switch (`0100770008DD8000`) modding on Eden and Ryujinx/Linux.
Native Forge PC conversions target GURecomp on Linux x64 and Windows x64.

## Mods

| Mod | Local release | Source and documentation |
| --- | --- | --- |
| Damage Numbers | r25 | [Guide and development](mods/damage-numbers/README.md) |
| Damage Numbers PC | r2 DEVELOPMENT candidate | [Guide and development](mods/damage-numbers-pc/README.md) |
| Damage Numbers (Rust) | r1 DEVELOPMENT candidate | [Guide and development](mods/damage-numbers-rs/README.md) |
| Modern Weapon Controls | r11 | [Guide and development](mods/modern-weapon-controls/README.md) |
| Key Quest Markers | r2 | [Guide and development](mods/key-quest-markers/README.md) |
| Modern Weapon Controls PC | r1 | [Guide and development](mods/modern-weapon-controls-pc/README.md) |
| Key Quest Markers PC | r1 | [Guide and development](mods/key-quest-markers-pc/README.md) |
| Please do Better | r19-savehint | [Guide and development](mods/please-do-better/README.md) |
| Please do Better PC | r1 DEVELOPMENT candidate | [Guide and development](mods/please-do-better-pc/README.md) |

The ready releases and Rust development candidate are locally packaged and unpublished. Each mod's
`DISTRIBUTION.json` controls its status and payload hashes. Forge, HD Project,
wiki cheats and DTI dumper support remain LOCAL_ONLY. Verify all current records
with `python3 scripts/mod_distribution.py check`.

## Workspace

- [Project instructions](AGENTS.md) and [local state](docs/LOCAL_STATE.md)
- [Tools and launchers](docs/TOOLS.md), [reference map](docs/REFERENCES.md) and [code research](docs/RESEARCH_TOOLING.md)
- [Maintained Forge source](docs/FORGE_LOCAL_BRANCH.md), [runtime evidence](docs/FORGE_RUNTIME_EVIDENCE.md) and [plugin rules](docs/FORGE_PLUGIN_GUIDELINES.md)
- [HD Project ownership and merge order](docs/CLEANUP_HD_PROJECT.md)
- [GURecomp Linux setup and runtime](docs/GURECOMP_LOCAL_SETUP.md), [evidence receipt](docs/GURECOMP_LOCAL_RUNTIME.json) and [plugin port research](docs/GURECOMP_MOD_PORTABILITY.md)
- [Distribution rules](docs/DISTRIBUTION_STANDARD.md) and [standalone development](docs/STANDALONE_MODS.md)

Start a mod with its local `build.sh`; copy and hash game inputs before editing.
Stage replacements under `build/<name>/romfs/nativeNX/` using original relative
paths. The dump, uninstalled library and emulator installation directories are
listed in local state. Preparation and packaging do not install or publish.

Current technical decisions and validation limits live with each mod.
Superseded experiment/release notes remain recoverable from Git history.
