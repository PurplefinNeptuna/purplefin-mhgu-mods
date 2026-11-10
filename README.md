# MHGU modding

Monster Hunter Generations Ultimate 1.4.0 for Switch (Eden/Ryujinx), built on
upstream Forge **1.5.1**. On PC, [MHGURecomp](https://github.com/morerokk/MHGURecomp)
loads the same Forge NROs.

| Mod | Release | Guide |
| --- | --- | --- |
| Damage Numbers | r42 | [Install](mods/damage-numbers/README.md) |
| Key Quest Markers | r20 | [Install](mods/key-quest-markers/README.md) |
| Lock-on Target | r2 | [Install](mods/lock-on-target/README.md) |
| Modern Weapon Controls | r15 | [Install](mods/modern-weapon-controls/README.md) |
| Multiplayer Roaming | r15 | [Install](mods/online-roaming/README.md) |
| Please do Better | r29 | [Install](mods/please-do-better/README.md) |
| Shared Urgent Quests | r2 | [Install](mods/shared-urgent-quests/README.md) |
| Village Quests in Hub | r5 | [Install](mods/village-quests-in-hub/README.md) |
| Wishlist | r45 | [Install](mods/wishlist/README.md) |
| Wishlist bridge for KatSmithy | r15 | [Install](mods/wishlist-katsmithy-bridge/README.md) |
| World Sharpness Gauge | r70 | [Install](mods/world-sharpness-gauge/README.md) |

Each mod's DISTRIBUTION.json controls delivery status and hashes. Current
candidates and acceptance scope are summarised in
[docs/LOCAL_STATE.md](docs/LOCAL_STATE.md). HD Project, wiki cheats and DTI
extraction support are local integrations.

- [Instructions](AGENTS.md), [local paths/state](docs/LOCAL_STATE.md)
- [Development and distribution](docs/DEVELOPMENT.md)
- [Tools and references](docs/TOOLS.md)
- [Code, DTI and native GUI research](docs/RESEARCH.md)
- [HD ownership and merge order](docs/CLEANUP_HD_PROJECT.md)
- [Compaction and preserved-artifact receipt](docs/COMPACTION.json)

Use mod-local build.sh commands. Inspect all deliveries with
`python3 scripts/mod_distribution.py check`. Builds and packaging do not install,
activate or publish. Superseded source remains in Git. Each mod's last gameplay-accepted build stays
under build/, and backups/ is an optional local archive. Update upstream
repositories in place.
