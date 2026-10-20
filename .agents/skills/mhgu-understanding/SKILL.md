---
name: mhgu-understanding
description: Find and interpret Monster Hunter Generations Ultimate Switch game code, RomFS resources, IDs, native objects, quests, input, damage, cameras, and rewards. Use for saved Ghidra/DTI research, locating data, and planning verified resource edits. Focuses on MHGU 1.4.0, not MHXX or PC engine layouts.
---

# MHGU Understanding

Research MHGU Switch 1.4.0, title `0100770008DD8000`. This knowledge snapshot is dated 2026-10-17, with HUD identity and clipping guidance updated 2026-10-18. Native offsets below belong to the verified update main, not every game version. Read only the references relevant to the question.

## Research workflow

1. Decide whether the target is runtime behavior, packed resources, localized text, an ID mapping, or live state. A runtime structure and its serialized record can have different layouts.
2. Search saved indexes and existing research before extracting again. Follow the native reader/writer, consumers, and destructor to establish meaning and ownership.
3. Verify against copied, hash-identified originals. An annotation, wiki field, matching name, or fixture alone cannot establish game/version compatibility or visible behavior.
4. Report the finding with its source, offset base, units/types, verification method, and remaining uncertainty. Keep original dumps, libraries, saves, and annotations intact.

For native GUI plans as well as implementation, read [Native GUI](references/native-gui.md). Establish instance-to-animation-to-object ownership and distinguish resource IDs from table rows before proposing reuse. File presence, suggestive names and setter lookup do not establish unused objects or a working rendering mechanism. Keep unresolved feasibility separate from the user's chosen visual design.

## Choose a reference

| Question | Read |
| --- | --- |
| Where is the code/data? How do I search Ghidra, DTI, IDs, and resources? | [Discovery and evidence](references/discovery-and-evidence.md) |
| How do GUI resources, properties, trees, maps, and caches work? | [Native GUI](references/native-gui.md) |
| How do key quests, urgents, completion, and progression relate? | [Quests and progression](references/quests-and-progression.md) |
| Which input representation/player/state is this? How does reload buffering work? | [Input and actions](references/input-and-actions.md) |
| Where do damage, ownership, hitzones, and camera matrices come from? | [Damage and cameras](references/damage-and-cameras.md) |
| How do Luck, reward pages, quantities, and appraisal work? | [Rewards and Luck](references/rewards-and-luck.md) |
| Which tools/formats can edit a resource, which wiki `.bt` templates match real files, and what is unverified? | [Resources and tooling](references/resources-and-tooling.md) |
| Original local paths and topic-to-source coverage | [Workspace and sources](references/workspace-and-sources.md) |

## Portable use

These Markdown files contain the findings without requiring a particular agent tool. Workspace commands require the original checkout, tool runtimes, and explicitly supplied private inputs. Source pointers name workspace-root paths or files beneath a named mod/upstream checkout. When those inputs are missing, explain what cannot be checked and use the documented method with equivalent inputs. Do not invent game bytes or rerun runtime extraction implicitly.

The optional companion `mhgu-forge-modding` skill owns plugin implementation, hook safety, GUI insertion procedures, settings, builds, and delivery. This skill can answer game-research questions independently. New installation, game launch, save edits, and DTI extraction require their own task scope.
