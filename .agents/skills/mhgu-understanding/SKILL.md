---
name: mhgu-understanding
description: Find and interpret Monster Hunter Generations Ultimate 1.4.0 Switch game code, RomFS resources, IDs, native objects, quests, input, damage, cameras and rewards. Includes a step-by-step research playbook (search saved Ghidra/DTI, convert addresses, read original bytes, prove meaning, record findings), address conventions, and topic references for planning plugins or verified resource edits. Not for MHXX or PC engine layouts.
---

# MHGU Understanding

Research MHGU Switch 1.4.0, title `0100770008DD8000`, main build ID
`FB08F1D20FD1204FE7070672777F869B`. Offsets belong to this exact executable,
not other game versions. Knowledge dated 2026-10-20.

## Start here

1. For any "where/how does the game do X" question, follow the
   [Research playbook](references/research-playbook.md) step by step.
2. Check the topic reference below first; the answer may already be verified.
3. Record each finding with its source, offset kind, type/units, verification
   and remaining uncertainty.

## Address conventions

| Form | Meaning | Example |
| --- | --- | --- |
| Ghidra address | Address in the saved database (image base `0x009c9000`) | `0x01177f68` |
| main+0xNNNN | Main-relative offset = Ghidra address − `0x009c9000`. Used everywhere in these skills and in hook code | main+`0x7aef68` |
| +0xNN | Field offset inside an object. Never subtract the image base | `monster+0x1428` |
| Cell 0xNNNN | Main-relative address of a global pointer to a singleton | session cell `0x188ca48` |
| ID / index / row | Object ID, lookup index, table row and resource ID are different numbers; keep them in separate columns | |

## Rules

- Verify against the copied, hash-checked original NSO (`work/shared/game-exefs/main`).
  Ghidra text differs from it at one byte, and some imported type layouts are wrong.
- Names, wiki fields, decompiler variables and file presence are leads, not proof.
- Follow writer, reader, callers and destructor before claiming what a field means or who owns an object.
- A runtime object and its serialized resource record can have different layouts.
- Do not run DTI extraction, launch the game, edit saves or touch original dumps.
  Reuse the saved indexes. New runtime evidence needs the user to run something.
- Say "inference" when evidence is indirect, and name what would confirm it.

## Choose a reference

| Question | Read |
| --- | --- |
| How do I go from a question to a verified offset? | [Research playbook](references/research-playbook.md) |
| Where is the code/data? Ghidra, DTI, IDs and resource search details | [Discovery and evidence](references/discovery-and-evidence.md) |
| How do GUI resources, properties, trees, maps and caches work? | [Native GUI](references/native-gui.md) |
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
safety, GUI insertion, settings, builds and delivery. `mhgu-pc-modding` covers
GURecomp/Forge PC ports.
