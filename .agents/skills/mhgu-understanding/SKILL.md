---
name: mhgu-understanding
description: What Monster Hunter Generations Ultimate 1.4.0 (Switch) itself does - game code, RomFS resources, IDs, native objects, GUI trees, menus, quests, equipment, input, damage, cameras, rewards, sounds, multiplayer and file formats. Includes a step-by-step research playbook (search saved Ghidra/DTI, convert addresses, read original bytes, prove meaning, record findings). Use to find or interpret anything in the game. Holds no mod or plugin knowledge; for that use mhgu-forge-modding. Not for MHXX or PC engine layouts.
---

# MHGU Understanding

Research MHGU Switch 1.4.0, title `0100770008DD8000`, main build ID `FB08F1D20FD1204FE7070672777F869B`. Offsets belong to this exact executable, not other game versions.

This skill is **only what the game does**: code, fields, formats, IDs. It names no mod. How a plugin uses these facts, what other mods change, how hosts differ and which run proved a fact are in the companion `mhgu-forge-modding` skill. A new game fact goes here, whichever mod found it. Label it bytes, run or inference, and add its source to that skill's `references/knowledge-sources.md`.

## Start here

1. For any "where/how does the game do X" question, follow the [Research playbook](references/research-playbook.md) step by step.
2. Check the topic reference below first; the answer may already be verified.
3. Record each finding with its source, offset kind, type/units, verification and remaining uncertainty.

## Game data

These are read-only originals. Copy a file into the scratchpad or `work/NAME/` before extracting, unpacking or editing it.

| Location | What it holds | Use it for |
| --- | --- | --- |
| `/mnt/storage2/Programs/MHGURecomp/data/romfs/` | Every game resource (ARC archives in `nativeNX/arc/`, GUI, tables, per-language text), 12 GB, no code. A copy of the 1.4.0 RomFS. | Finding and reading resources: `find DUMP/romfs -iname '*NAME*'` |
| `work/shared/game-exefs/` | The 1.4.0 code only: `main` (the game), `sdk`, `subsdk0`, `rtld`, `main.npdm`. The `forge` file there is the loader, not game code. | Instruction bytes and signatures. Read `main` with `scripts/mhgu_binary.py` `main_image()`, which refuses any other version. |
| `work/research-tooling/` | Saved Ghidra project/export and DTI index built from that `main` | Search first: `./scripts/tool.sh research find QUERY --kind functions` |
| `/mnt/storage2/ROM/Switch/Game/`, the XCI with title ID `0100770008DD8000` and `[v0]` | Sealed base game (v0) | Rarely needed: an original the dump lacks |
| `/mnt/storage2/ROM/Switch/Update+DLC/`, the NSP with title ID `0100770008DD8800` and `[v262144]` | Sealed 1.4.0 update, about 193 MiB (v262144). Mostly a RomFS patch: a binary delta that only works applied onto the base RomFS, not a folder of files. | Rarely needed. Its resource changes are in the dump and its code is in `game-exefs/`. |
| `/mnt/storage2/ROM/Switch/keys+firmware/` | Keys needed to open the XCI/NSP | Only with the two files above |

Opening the XCI/NSP needs hactool. Only its source is in `tools/hactool-source/`; build it and extract into the scratchpad.

## Address conventions

| Form | Meaning | Example |
| --- | --- | --- |
| Ghidra address | Address in the saved database (image base `0x009c9000`) | `0x01177f68` |
| main+0xNNNN | Main-relative offset = Ghidra address − `0x009c9000`. Used everywhere in these skills | main+`0x7aef68` |
| +0xNN | Field offset inside an object. Never subtract the image base | `monster+0x1428` |
| Vtable word / DTI `get`, `set`, `vft` | Already main-relative. Never subtract the Ghidra base from these | Texture slot 0x38 holds `0xa4e628` |
| Decompiled `param_1[0x38]` on an `int *` | Indexed in words: byte offset = index × 4. Written pointer arithmetic is already in bytes | `param_1[0x38]` is `+0xe0` |
| Cell 0xNNNN | Main-relative address of a global pointer to a singleton | session cell `0x188ca48` |
| GOT word 0xNNNN | A word that holds a cell's address: code loads it, then loads the cell, then the object, one load more than from the cell. Reading the GOT word once gives the pointer's address, not the object | GOT word `0x1838bb4` holds the address of cell `0x188ca48`; `*(*(0x1838bb4))` is the session |
| ID / index / row | Object ID, lookup index, table row and resource ID are different numbers; keep them in separate columns | |

## Rules

- Verify against the copied, hash-checked original NSO (`work/shared/game-exefs/main`). Ghidra text differs from it at one byte, and some imported type layouts are wrong.
- Names, wiki fields, decompiler variables and file presence are leads, not proof.
- An empty search is evidence only once the same tool has found a known positive. A broken cross-reference script once reported "no `bl` site" for every target; `research xref` replaces it. A probe that logs nothing counts the same way: one on `0x4eef00` with no positive control sent a sound investigation the wrong way for about a hundred builds.
- Follow writer, reader, callers and destructor before claiming what a field means or who owns an object.
- A runtime object and its serialized resource record can have different layouts. Map the offsets through the resource's load (vtable slot 0x2c and its per-record reader): `itemData` is 44 bytes in the file and 56 in memory, so a code offset read on the file gives a wrong field.
- Do not run DTI extraction, launch the game, edit saves or touch original dumps. Reuse the saved indexes. New runtime evidence needs the user to run something.
- Say "inference" when evidence is indirect, and name what would confirm it.
- MHGU is a last-generation game, and quests are not seamless: a quest map is split into numbered areas, with a loading screen between them. Do not assume what that does to an object; measure each one. The sharpness gauge's HUD row lasts a whole quest.
  - That is inference: its row ends sit beside the game's save commits and testers report area changes and faints with no re-insertion, but no log line marks an area change. Other objects are unmeasured. The cGUIObjRoot destructor slot 0x04 fired in no saved log.
  - `setAnimationId` `0xa38828` destroys a row's controller and map and builds new ones (called from `0x54504c` and `0x5451fc`), and whether that is the path a row's end takes is unread.

## Choose a reference

| Question | Read |
| --- | --- |
| How do I go from a question to a verified offset? | [Research playbook](references/research-playbook.md) |
| Where is the code/data? Ghidra, DTI, IDs and resource search | [Discovery and evidence](references/discovery-and-evidence.md) |
| Local paths and reference snapshots | [Workspace and sources](references/workspace-and-sources.md) |

**GUI**

| Question | Read |
| --- | --- |
| GUI file layout, properties, identifying a row, keyframes | [GUI resources](references/gui-resources.md) |
| Which screens and rows are mapped (counter, quest detail, Quest Info, smithy, HUD, start menu, pouch, rewards, popup, guide) | [GUI screens](references/gui-screens.md) |
| Object classes, sizes, setters, runtime fields, flag bits, ownership | [GUI objects](references/gui-objects.md) |
| Draw walker, draw block, coordinates, colours, message text (line breaks, colour tags, no clipping), reward frames | [GUI drawing](references/gui-drawing.md) |
| Which thread runs the GUI | [GUI threads](references/gui-threads.md) |
| How the save is mounted, written and committed; the save mutex; why a commit fails | [Save data](references/save-data.md) |

**Menus and screens**

| Question | Read |
| --- | --- |
| Start menu internals and pages, list objects, the page cursor (`0x54edec`/`0x54ee34`), in town or in a quest | [Start menu](references/start-menu.md) |
| Options window, Help | [Options and Help](references/options-and-help.md) |
| Item Pouch and Equipment screens, how items enter the pouch | [Pouch and equipment screens](references/pouch-and-equipment-screens.md) |
| Button guide, centre popup | [Guide and popups](references/guide-and-popups.md) |
| Making a game window (`cUIObject`) outside its own screen | [GUI objects](references/gui-objects.md#ui-objects-outside-their-screen) |
| Smithy top menu and list screens | [Smithy window](references/smithy-window.md#smithy-top-menu) |

**Quests**

| Question | Read |
| --- | --- |
| Key quests, urgents, special encounters, completion, recording a clear online | [Quest progression](references/quest-progression.md) |
| How quest lists are built, the unlock script, talk tables, downloaded event quests | [Quest lists](references/quest-lists.md) |
| The counter's rank and star pages | [Counter pages](references/counter-pages.md) |
| Quest detail panel, quest board, Quest Info, the running quest | [Quest detail pages](references/quest-detail-pages.md) |
| Rewards, carves, captures, breaks, gathering, fishing and their files | [Quest files](references/quest-files.md) |
| Luck, reward pages, guarantees, quantities, appraisal | [Rewards and Luck](references/rewards-and-luck.md) |

**Equipment**

| Question | Read |
| --- | --- |
| Box slots, equipped gear, level base, weapon category | [Equipment box](references/equipment-box.md) |
| Weapon craft, upgrade and derive tables | [Weapon crafting data](references/weapon-crafting-data.md) |
| Smithy window fields and code, prices, kinsects, loaded tables | [Smithy window](references/smithy-window.md) |
| Stat getters, decorations, skills, itemData layouts, rarity, armor names | [Equipment stats](references/equipment-stats.md) |
| Armor archives, file IDs, loading, MRL materials, armor textures, which hunter is local | [Hunter armor](references/armor-models.md) |
| Sharpness points, tiers, tables, the HUD row | [Sharpness](references/sharpness.md) |

**Gameplay, sound, network and files**

| Question | Read |
| --- | --- |
| Input views, button glyphs, local player and weapon, target camera, reload | [Input and actions](references/input-and-actions.md) |
| How monster HP falls, every damage route, shells and siege weapons | [Damage](references/damage.md) |
| Camera objects, matrices, projection, applied display size | [Cameras](references/cameras.md) |
| NVN function table, shader package, unlit shader, color grading, gradient overlays, bloom | [Rendering](references/rendering.md) |
| Menu sounds, sound data, request slots | [Sounds](references/sounds.md) |
| Pickup and BBQ jingles | [Jingles](references/jingles.md) |
| Motion sound events (MSS) | [Motion sounds](references/motion-sounds.md) |
| Sessions, member state, who spawns for whom, travel codes, functions that take an entry hook | [Multiplayer and areas](references/multiplayer-and-areas.md), by address in [Multiplayer findings](references/multiplayer-findings.md) |
| The game's allocators and what a full one does | [Allocators](references/allocators.md) |
| ARC, GMD and texture layouts, language codes, how the resource manager shares files | [File formats](references/file-formats.md) |
| Which tools edit a resource, which wiki `.bt` templates fit | [Resource editing](references/resource-editing.md) |

For a GUI question, establish instance-to-animation-to-object ownership and distinguish resource IDs from table rows before proposing reuse. File presence, suggestive names and setter lookup do not establish unused objects or a working rendering mechanism.

## Portable use

These Markdown files contain the findings without requiring a particular agent tool. Workspace commands need the original checkout, tool runtimes and private inputs. When inputs are missing, explain what cannot be checked and use the documented method with equivalent inputs. Do not invent game bytes.
