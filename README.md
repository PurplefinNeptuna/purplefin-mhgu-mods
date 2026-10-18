# MHGU modding

Monster Hunter Generations Ultimate 1.4.0 for Switch (Eden/Ryujinx) and native
GURecomp PC ports. Switch development uses upstream Forge **1.5.1**; PC uses
stock Forge PC **0.2.1**.

| Mod | Release | Guide |
| --- | --- | --- |
| Damage Numbers | r30 | [Install](mods/damage-numbers/README.md) |
| Key Quest Markers | r18, hardware-test candidate | [Install](mods/key-quest-markers/README.md) |
| Modern Weapon Controls | r12 | [Install](mods/modern-weapon-controls/README.md) |
| Please do Better | r24-forge151 | [Install](mods/please-do-better/README.md) |
| Damage Numbers PC | r3 | [Install](mods/damage-numbers-pc/README.md) |
| Key Quest Markers PC | r1 | [Install](mods/key-quest-markers-pc/README.md) |
| Modern Weapon Controls PC | r1 | [Install](mods/modern-weapon-controls-pc/README.md) |
| Please do Better PC | r1 | [Install](mods/please-do-better-pc/README.md) |

Each mod's DISTRIBUTION.json controls delivery status and hashes. Damage Numbers
r30 is READY_TO_DISTRIBUTE following user approval, with device testing unconfirmed.
Key Quest Markers r18 remains a DEVELOPMENT candidate.
Earlier accepted releases are preserved under backups/accepted/.
Other platform and maintenance-build acceptance retains its recorded scope.
PC runtime bytes are preserved.
HD Project, wiki cheats and DTI extraction support are local integrations.

- [Instructions](AGENTS.md), [local paths/state](docs/LOCAL_STATE.md)
- [Development and distribution](docs/DEVELOPMENT.md)
- [Tools and references](docs/TOOLS.md)
- [Code, DTI and native GUI research](docs/RESEARCH.md)
- [GURecomp setup and ports](docs/GURECOMP.md)
- [HD ownership and merge order](docs/CLEANUP_HD_PROJECT.md)
- [Compaction and preserved-artifact receipt](docs/COMPACTION.json)

Use mod-local build.sh commands. Inspect all deliveries with
`python3 scripts/mod_distribution.py check`. Builds and packaging do not install,
activate or publish. Superseded source remains in Git; accepted deliveries are
preserved under backups/accepted/. Update upstream repositories in place.
