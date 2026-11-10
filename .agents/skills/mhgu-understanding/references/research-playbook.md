# Research playbook: from a question to a verified offset

Follow these steps in order for any "where does the game do X?" question.
Run commands from the workspace root. Write findings into
`mods/NAME/DEVELOPMENT.md` or `work/NAME/` as you go, not only at the end, as
standing facts rather than a log ("Writing project docs" in the workspace `AGENTS.md`).

## 1. Write the question as something observable

Bad: "find poison". Good: "which native function subtracts poison damage from
monster HP, and where is the amount stored before it is subtracted?" Decide
which kind of answer you need:

| Kind | Example | Where to look first |
| --- | --- | --- |
| Runtime behaviour | When HP falls, who owns a hit | Ghidra functions, then DTI fields |
| Runtime object field | Monster HP offset | DTI properties, then the code that reads it |
| Packed resource | Item table, GUI layout | Resource tools ([Resources and tooling](resources-and-tooling.md)) |
| Text | Quest names | GMD files |
| ID mapping | Quest ID to group | Offline wiki ID lists, then the native reader |

## 2. Check what is already known

1. Search these skills' references for the topic.
2. Read the related mod's DEVELOPMENT.md (`mods/*/DEVELOPMENT.md`): damage,
   cameras and HP in Damage Numbers; quests and GUI in Key Quest Markers;
   input in Modern Weapon Controls; rewards in Please do Better.
3. `grep -rn 'KEYWORD' docs/RESEARCH.md work/*/` for older notes.

Reuse a documented offset only after checking it in step 5.

## 3. Search the saved indexes

```sh
./scripts/tool.sh research status
./scripts/tool.sh research find 'poison' --kind functions --limit 20
./scripts/tool.sh research find 'hp_vital' --kind dti --limit 10
./scripts/tool.sh research find 'uShellSt006' --kind symbols --limit 10
```

- `--kind` is one of `functions`, `symbols`, `types`, `dti` (default: all).
- Matching is case-insensitive substring search over JSON lines; it can hit
  field names. No match does not mean the code does not exist. Try class
  names (`uEnemy`, `sQuest`), DTI property names (`mParam.hp_vital`) and
  string literals.
- For a field you know (for example a DTI property offset), search Ghidra for
  code that reads that offset from the right object type.

## 4. Get decompiled code for specific addresses

1. Create `work/NAME/ghidra-targets.txt`: one **main-relative** `0x` offset per
   line, with a `#` comment saying why.
2. Close the Ghidra GUI project if it is open.
3. `./scripts/tool.sh research export --targets work/NAME/ghidra-targets.txt`
4. Read `work/research-tooling/ghidra-export/summary.json` →
   `research_targets` (symbols, containing function, references) and
   `work/research-tooling/ghidra-export/function_<offset>.c` (decompiled C).

Each run replaces the previous target output. Do not add your offsets to
`scripts/ghidra/ExportMhguResearch.java`.

## 5. Convert and verify addresses

| You have | Convert |
| --- | --- |
| Ghidra address `0x01177f68` | main-relative = `0x01177f68 - 0x009c9000` = `0x007aef68` |
| main-relative offset | runtime address = actual main base + offset (Forge supplies the base) |
| Object field `+0x1428` | Leave as is; it is relative to an object pointer |

Read the original instruction bytes from the verified copied NSO. Never use
Ghidra bytes for signatures (offset `0x283710` differs).

```sh
./scripts/tool.sh research dis 0xa2664 0x20     # disassemble at a main-relative offset
./scripts/tool.sh research xref 0xa2664         # ARM b/bl sites reaching it
./scripts/tool.sh research word 0xa4ba94        # stored words equal to it: vtables, DTI
./scripts/tool.sh research vtable 0x178fcc8 32  # a vtable's code offsets by slot
```

These read `main` through `main_image`, which refuses any file whose SHA-256 or
build ID differs from 1.4.0. The `dis` example starts `push {r4, r5, r6, r7,
r11, lr}`, `vpush {d8}`, the documented start of the poison tick. Disassembly
prints words byte-swapped: `e92d4830` is the memory bytes `30 48 2d e9`, and a
signature window is written in memory order. `b`/`bl` targets in a `dis` listing
are relative to the window, so read them with `xref` instead.

Use these three traps as checks on any address or field you read:

- Vtable words and DTI `get`/`set` values are already main-relative. Subtracting
  the Ghidra base from one gives a real-looking address in unrelated code, and
  World Sharpness Gauge drew conclusions from three of those.
- A decompiled `param_1[0x38]` on an `int *` is byte offset `0xe0`.
- A global slot is loaded as `ldr rX, [pc, #imm]` then, possibly several instructions later,
  `ldr rY, [pc, rX]`. Match the first with `word & 0x0f7f0000 == 0x051f0000` (bit 23 set adds `imm`,
  clear subtracts it), find the second as the next `word & 0x0fff0ff0 == 0x079f0000` whose low
  nibble is `rX`, and compute `slot = second + 8 + word(first + 8 ± imm)`. Using the wrong second
  address, or stopping a few words ahead, gave two wrong slots in the equipment-box research.
- `xref` lists direct branches only. Before calling a function unreferenced, run
  `word` too. Run any new or borrowed search tool on a known positive first.

## 6. Prove the meaning

A function name or decompiled variable name is a guess. Establish meaning by:

1. **Writer and reader.** Find the code that writes the field and the code
   that consumes it. For HP: main+0x9d6f8 adds to part counters; the monster
   update main+0x97ddc sums them and subtracts from `work+0x370`.
2. **Callers.** Use the references in `summary.json`. Every caller must agree
   with your interpretation of the arguments.
3. **Types and sizes.** Confirm a field's width from the load/store instruction
   (`ldrsh` = signed 16-bit, `ldr` = 32-bit, `vldr` = float).
4. **Lifetime.** Find who allocates and who frees an object before keeping a
   pointer or adding to it.
5. **Cross-check DTI** for class sizes and property offsets, filtering
   `vft_kind == "object"` for instance vtables.

If something is still an inference (for example "this branch is the mount
finisher"), write the word *inference* and say what evidence would confirm it.

Checks that catch the usual wrong turns:

- **A premise needs its own evidence.** In "X, which is why Y", X is a claim too. "Equipped
  gear sits in the box array, which is why armor has its own types" had no source; My Weapon
  Tree's doc says types 1..5 are *box* armor. A tester's requirement ("an equipped weapon
  counts as owned") is a rule to build to, not a fact about where the game keeps it.
- **Two readings that disagree are both kept, with what would settle them.** Do not invent a
  bridge between them ("the box view carries the same pair four bytes earlier"). Write both,
  their sources, and the read that decides (here: the code that indexes the array).
- **A size or count that fits is a lead.** `2368 = 74 * 32` matched the `.wpd` record size;
  the call was a memset, not a load.
- **A partial match states its remainder.** 588 of 632 is "588 match, 44 differ", and the
  claim covers the 588 only until the 44 are explained. Here they were the matching script
  pairing each log group with the wrong node; matched against every row, all 700 groups fit.
- **A failed cross-check means your model is wrong, not the reference.** Never re-label the
  reference ("its panel is its own construction") to drop the check. Try the next
  hypothesis against the same check (worked example 2).
- **An explanation predicts something else.** Before writing "X because Y", name another case Y
  would change, and check it. "Owned is one low because the weapon in hand is unread" predicts
  that only the carried weapon is wrong; six listed weapons were (worked example 3).
- **Offsets are a base question first.** Values off by one constant across unrelated records mean
  a 0-based field or an encoding. Rule that out before looking for missing reads.
- **Read-only ground truth beats theory.** A save file, an ini the game or a mod wrote, and RomFS
  rows are free to read and cannot flatter the model. Compare them with the tester's own list.
- **Know what a measurement covers.** "Matches KatSmithy's log" covers the rows it printed. A rule
  applied to a whole table is checked over the whole table, with the count of each branch printed.
- **A layout is proved by its bytes, not its comment.** Dump one row in hex next to the claimed
  stride; a stride that only fits by eye is a lead.
- **A refutation travels.** When a finding contradicts an earlier one, `rg` for the old claim
  and correct every copy (skill references, DEVELOPMENT.md, the plan) in the same commit.

## 7. Record the finding

Write one entry per finding in the mod's DEVELOPMENT.md:

```text
Finding: <what the game does>
Where: main+0xNNNNNN (<function name if known>), object field +0xNN
Type/units: <s16 HP points, float seconds, ...>
Evidence: <writer/reader/caller addresses, DTI record, byte window checked>
Status: verified against original NSO | inference (needs <what>)
```

Before you write it down or commit, answer each line. Any "no" means fix it first.

1. Does every "because", "so" or "which is why" have its own source in the Evidence line?
2. If two sources disagree, did you write both and the read that would decide, not a story
   that joins them?
3. Is a count stated with what did not match ("588 of 632; 44 differ")?
4. Did a check fail and get dropped, softened or relabelled? Then undo that and change your
   hypothesis instead.
5. Does this contradict anything already written? `rg` the old claim across
   `.agents/skills`, `mods/*/DEVELOPMENT.md` and the task's `work/` notes, and correct each copy.
6. Is it a fact about the game, or the tester's rule for the feature? Keep them apart.
7. Does the conclusion depend on something you still list as open? Then state it as conditional
   ("counts it only if the index means kind 0"), and the step is not done. Call it done only when
   nothing it rests on is open.
8. Did you read a table or data words by eye from a listing? Print them with a script over
   `main_image()` and quote that output.

9. Does this explanation predict something you have not looked at? Look at it first.
10. Is every level, index and count labelled with the base it counts from, on both sides of the use?

## 8. What not to do

- Do not run the DTI dumper again. The saved dump exists, and the
  2026-10-03 run broke quest controls until restart.
- Do not edit the Ghidra GZF or the original NSO. The editable project is
  `work/research-tooling/ghidra-projects/MHGU_1.4.0.gpr`.
- Do not use MHXX or PC offsets for Switch, or wiki fields without checking a
  real file.
- Do not launch the game to "check quickly". Ask the user for a run instead.

## Worked example: why poison damage showed no number

1. Question: which code reduces monster HP for poison, if not the hit handler?
2. Known: HP falls in the monster update main+0x97ddc, which subtracts part
   counters and then the s16 pending amount at `work+0x5d66`.
3. Search: writers of `+0x5d66`. The poison tick main+0xa2664 clears it, and
   while `work+0x5e08 & 2` is set it advances a timer at `work+0x5ca8` and
   stores the poison table's s16 `+0xc` there at each interval.
4. Verify: bytes at 0xa2664 are `push {r4-r7,r11,lr}`, `vpush {d8}` (no PC
   use, safe to displace). No `SEL`/`MRS`/`MSR` in the function body.
5. Result: an around hook at 0xa2664 reads `work+0x5d66` after the original
   returns. That became Damage Numbers hook 8.

## Worked example 2: which table holds the craft cost

1. Question: which RomFS rows hold the materials of a weapon's level-1 craft?
2. Known: `weaponProcessW<table>.wpd` and `weaponCreateW<table>.wcd`, layouts verified by
   file size. KatSmithy's run log prints each node's materials (`RISE mat id=... need=...`).
3. First hypothesis, the `.wpd` row `(number, 1)`: no level-1 group in the log matches.
   Wrong move taken here: calling KatSmithy's panel "its own construction" and dropping the
   check. Right move: keep the check, change the hypothesis.
4. Second hypothesis, the `.wcd` row keyed `(mLevel, mNo)`: 588 of 632 groups matched
   under the first pairing of log groups to nodes. The misses were checked, not waved through:
   matched against every create row of the open table, all 700 groups fit exactly
   (`work/wishfinder-katsmithy-bridge/rise_vs_wcd.py`).
5. Result: the craft row is the `.wcd` row, 163 distinct rows over 8 tables. The earlier lines "`.wcd mNo` is a create-entry index" and
   "the window loads `.wpd` records" are corrected wherever they were written.

## Worked example 3: why owned levels read one low

1. Report: three weapons the tester owns at levels 5, 3 and 2 were answered as 4, 2 and 1.
2. First explanation: the weapon in hand was never read. It was also a real bug, so it looked
   confirmed. Wrong move: fixing it and stopping. It predicts that only the carried weapon is
   wrong, and a player carries one weapon.
3. Check against ground truth: every weapon the tester listed, found in the save file read-only
   (44-byte records). All six hold the shown level minus one.
4. Confirm in bytes: `main+0x6f9f00` loads the smithy row's byte at `+9` and `main+0x6f9f08`
   shifts it straight into the record's level bits. Saved upgrade keys hold 1 and 6 where the
   matching RomFS process rows are levels 2 and 7, so the row byte counts from 0 as well.
5. Result: three separate bugs came from the one wrong assumption: owned levels, step keys that
   could never match a finish, and names one level ahead. Two independent bugs can share a symptom.
