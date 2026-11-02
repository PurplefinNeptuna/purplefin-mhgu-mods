---
name: mhgu-understanding
description: Find and interpret Monster Hunter Generations Ultimate 1.4.0 Switch game code, RomFS resources, IDs, native objects, quests, input, damage, cameras and rewards. Includes a step-by-step research playbook (search saved Ghidra/DTI, convert addresses, read original bytes, prove meaning, record findings), address conventions, and topic references for planning plugins or verified resource edits. Not for MHXX or PC engine layouts.
---

# MHGU Understanding

Research MHGU Switch 1.4.0, title `0100770008DD8000`, main build ID
`FB08F1D20FD1204FE7070672777F869B`. Offsets belong to this exact executable,
not other game versions. Knowledge dated 2026-11-01.

## Start here

1. For any "where/how does the game do X" question, follow the
   [Research playbook](references/research-playbook.md) step by step.
2. Check the topic reference below first; the answer may already be verified.
3. Record each finding with its source, offset kind, type/units, verification
   and remaining uncertainty.

## Game data

These are read-only originals. Copy a file into the scratchpad or `work/NAME/`
before extracting, unpacking or editing it.

| Location | What it holds | Use it for |
| --- | --- | --- |
| `~/.local/share/eden/dump/0100770008DD8000/romfs/` | Every game resource (ARC archives in `nativeNX/arc/`, GUI, tables, per-language text), 12 GB, no code. Eden dumped it on 2026-10-01 with the 1.4.0 update loaded, so it should be base and update merged; no file has been compared against the base yet. | Finding and reading resources: `rg --files DUMP/romfs \| rg NAME` |
| `work/shared/game-exefs/` | The 1.4.0 code only: `main` (the game), `sdk`, `subsdk0`, `rtld`, `main.npdm`. `forge` is Forge 1.5.1's `subsdk9`, not game code. | Instruction bytes and signatures. Read `main` with `scripts/mhgu_binary.py` `main_image()`, which refuses any other version. |
| `work/research-tooling/` | Saved Ghidra project/export and DTI index built from that `main` | Search first: `./scripts/tool.sh research find QUERY --kind functions` |
| `/mnt/storage2/ROM/Switch/Game/Monster Hunter Generations Ultimate™ [0100770008DD8000][v0]).xci` | Sealed base game (v0) | Rarely needed: an original the dump lacks |
| `/mnt/storage2/ROM/Switch/Update+DLC/MONSTER HUNTER GENERATIONS ULTIMATE [0100770008DD8800][v262144].nsp` | Sealed 1.4.0 update, about 193 MiB (v262144; Eden logs it as "v0.4.0"). Mostly a RomFS patch: a binary delta that only works applied onto the base RomFS, not a folder of files. | Rarely needed. Its resource changes are in the dump and its code is in `game-exefs/`; nothing else is missing. |
| `/mnt/storage2/ROM/Switch/keys+firmware/` | Keys needed to open the XCI/NSP | Only with the two files above |
| `/mnt/storage2/ROM/Switch/cheats/mhgu/` | Uninstalled mod/cheat library | Not the game, and not installed mods |

Opening the XCI/NSP needs hactool. Only its source is in `tools/hactool-source/`;
build it and extract into the scratchpad.

## Address conventions

| Form | Meaning | Example |
| --- | --- | --- |
| Ghidra address | Address in the saved database (image base `0x009c9000`) | `0x01177f68` |
| main+0xNNNN | Main-relative offset = Ghidra address − `0x009c9000`. Used everywhere in these skills and in hook code | main+`0x7aef68` |
| +0xNN | Field offset inside an object. Never subtract the image base | `monster+0x1428` |
| Vtable word / DTI `get`, `set`, `vft` | Already main-relative. Never subtract the Ghidra base from these | Texture slot 0x38 holds `0xa4e628` |
| Decompiled `param_1[0x38]` on an `int *` | Indexed in words: byte offset = index × 4. Written pointer arithmetic is already in bytes | `param_1[0x38]` is `+0xe0` |
| Cell 0xNNNN | Main-relative address of a global pointer to a singleton | session cell `0x188ca48` |
| ID / index / row | Object ID, lookup index, table row and resource ID are different numbers; keep them in separate columns | |

## Rules

- Verify against the copied, hash-checked original NSO (`work/shared/game-exefs/main`).
  Ghidra text differs from it at one byte, and some imported type layouts are wrong.
- Names, wiki fields, decompiler variables and file presence are leads, not proof.
- An empty search is evidence only once the same tool has found a known positive.
  A broken cross-reference script reported "no `bl` site" for every target through
  the whole of World Sharpness Gauge's research. `research xref` replaces it.
- Follow writer, reader, callers and destructor before claiming what a field means or who owns an object.
- A runtime object and its serialized resource record can have different layouts.
- Do not run DTI extraction, launch the game, edit saves or touch original dumps.
  Reuse the saved indexes. New runtime evidence needs the user to run something.
- Say "inference" when evidence is indirect, and name what would confirm it.
- MHGU is a last-generation game, and quests are not seamless: a quest map is split into
  numbered areas, with a loading screen between them. Do not assume what that does to an
  object; measure each one. The sharpness gauge's HUD row lasts a whole quest. That is
  inference: its row ends sit beside the game's save commits and testers report area
  changes and faints with no re-insertion, but no log line marks an area change (see
  Lifecycle in `mods/world-sharpness-gauge/DEVELOPMENT.md`). Other objects are unmeasured.
  Any row can still die, so a plugin keeps a liveness check and drops its addresses on
  failure. The cGUIObjRoot destructor slot 0x04 fired in no saved log. `setAnimationId`
  `0xa38828` destroys a row's controller and map and builds new ones (called from
  `0x54504c` and `0x5451fc`), and whether that is the path a row's end takes is unread.

## Choose a reference

| Question | Read |
| --- | --- |
| How do I go from a question to a verified offset? | [Research playbook](references/research-playbook.md) |
| Where is the code/data? Ghidra, DTI, IDs and resource search details | [Discovery and evidence](references/discovery-and-evidence.md) |
| How do GUI resources, properties, trees, maps and caches work? | [Native GUI](references/native-gui.md) |
| Where are sharpness points, tiers, tables and the sharpness HUD row? | [Sharpness](references/sharpness.md) |
| How do key quests, urgents, completion and progression relate? | [Quests and progression](references/quests-and-progression.md) |
| Which input representation/player/state is this? How does reload buffering work? | [Input and actions](references/input-and-actions.md) |
| Where do damage, HP loss, ownership, hitzones and camera matrices come from? | [Damage and cameras](references/damage-and-cameras.md) |
| How do Luck, reward pages, quantities and appraisal work? | [Rewards and Luck](references/rewards-and-luck.md) |
| Which tools/formats edit a resource, which wiki `.bt` templates match real files? | [Resources and tooling](references/resources-and-tooling.md) |
| Original local paths and topic-to-source coverage | [Workspace and sources](references/workspace-and-sources.md) |

For native GUI plans as well as implementation, read [Native GUI](references/native-gui.md).
Establish instance-to-animation-to-object ownership and distinguish resource IDs
from table rows before proposing reuse. File presence, suggestive names and
setter lookup do not establish unused objects or a working rendering mechanism.
Keep unresolved feasibility separate from the user's chosen visual design.

## Portable use

These Markdown files contain the findings without requiring a particular agent
tool. Workspace commands need the original checkout, tool runtimes and private
inputs. When inputs are missing, explain what cannot be checked and use the
documented method with equivalent inputs. Do not invent game bytes.

The companion `mhgu-forge-modding` skill owns plugin implementation, hook
safety, GUI insertion, settings, builds and delivery.
