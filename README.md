# MHGU modding

Mods and modding tools for Monster Hunter Generations Ultimate 1.4.0 on Switch, run on the Eden
and Ryujinx emulators. The mods are [Forge](https://github.com/Fexty12573/forge) plugins, built
against Forge 1.5.1. On PC, [MHGURecomp](https://github.com/morerokk/MHGURecomp) loads the same
plugins.

## The mods

Each mod lives in its own repository under `mods/`. Lock-on Target's is public; the others
aren't yet, so their folders stay empty in a clone until each one is published.

| Mod | What it does |
| --- | --- |
| Damage Numbers | Shows damage numbers at each impact, with physical and elemental damage combined, in Wilds, Rise or Classic style. |
| Key Quest Markers | Adds Rise-style badges to key and urgent quests, coloured by whether you still need them to progress. |
| [Lock-on Target](https://github.com/PurplefinNeptuna/mhgu-lock-on-target) | Keeps the target camera on the monster the game targets and hides the target reticle. Tap the target button to turn the lock off, and hold R to aim freely. |
| Modern Weapon Controls | Moves weapon actions from R to ZR and keeps R for sprinting while sheathed. |
| Multiplayer Roaming | Lets you visit the villages, the bedrooms, the Palico ranch and the Soaratorium during an online session without leaving it. |
| Please do Better | Gives reward slots granted by Luck a white frame. It can also force Miraculous Luck and multiply item quantities. |
| Purple-lib | Lets other mods put their settings in the game's Options window and add topics to its help screens. It changes nothing by itself. |
| Shared Urgent Quests | Lets you clear a Hub urgent quest by joining someone else's session. |
| Skin Loader | Puts an installed skin on the armor your hunter wears. Only the look changes. |
| Village Quests in Hub | Lets you post Village quests from the Hub or the Hunters' Pub, so other hunters can join. |
| WishFinder | Keeps a wishlist from the smithy, adds up the materials, and pins the quests that give what you're short of. |
| WishFinder bridge for My Weapon Tree | Copies My Weapon Tree's wish list into WishFinder. |
| World Sharpness Gauge | Turns the sharpness bar into a gauge like the one in Monster Hunter: World. |

## What's here

- `scripts/`: the toolbox (`scripts/tool.sh`), research tools for the game's code, and the checks
  the mods are built and packaged with.
- `.agents/skills/`: notes for coding agents. `mhgu-understanding` covers how the game works
  (code, resources, menus) and `mhgu-forge-modding` covers writing Forge plugins.
- `templates/standalone/`: the scaffold a new mod starts from.
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) has the development rules,
  [docs/TOOLS.md](docs/TOOLS.md) the tool setup, and [AGENTS.md](AGENTS.md) the instructions
  agents work by.

## Getting started

Clone with submodules to get the Forge and forge-rs baselines, then turn on the commit hooks:

```sh
git clone --recursive https://github.com/PurplefinNeptuna/purplefin-mhgu-mods.git
cd purplefin-mhgu-mods
scripts/install_hooks.sh
```

Each mod builds with its own `./build.sh`; run `./build.sh fetch` once to download its pinned
dependencies. `python3 scripts/mod_distribution.py check` checks every mod's records and packages.
Building and packaging never install or publish anything.

## License

The scripts, docs and skills here are under the MIT License ([LICENSE](LICENSE)). Each mod has
its own license in its folder.
