# Research playbook: from a question to a verified offset

Follow these steps in order for any "where does the game do X?" question.
Run commands from the workspace root. Write findings into
`mods/NAME/DEVELOPMENT.md` or `work/NAME/` as you go, not only at the end.

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
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from mhgu_binary import main_image
img, _ = main_image(open('work/shared/game-exefs/main', 'rb').read())
off = 0xa2664   # main-relative offset to inspect
print(' '.join(img[off+i:off+i+4][::-1].hex() for i in range(0, 32, 4)))
"
```

`main_image` refuses any file whose SHA-256 or build ID differs from 1.4.0.
The example prints `e92d48f0 ed2d8b02 ...` (`push {r4-r7,r11,lr}`,
`vpush {d8}`), the documented start of the poison tick.

To disassemble, write the window to a scratch file and run:

```sh
llvm-objcopy -I binary -O elf32-littlearm --rename-section=.data=.text,code win.bin win.o
llvm-objdump -d --triple=armv7a win.o
```

Printed addresses are relative to the window start, and `bl` targets are
wrong by that same amount. Add your start offset by hand.

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

## 7. Record the finding

Write one entry per finding in the mod's DEVELOPMENT.md:

```text
Finding: <what the game does>
Where: main+0xNNNNNN (<function name if known>), object field +0xNN
Type/units: <s16 HP points, float seconds, ...>
Evidence: <writer/reader/caller addresses, DTI record, byte window checked>
Status: verified against original NSO | inference (needs <what>)
```

## 8. What not to do

- Do not run the DTI dumper again. The saved dump exists, and the
  2026-10-03 run broke quest controls until restart.
- Do not edit the Ghidra GZF or the original NSO. The editable project is
  `ghidra-projects/MHGU_1.4.0.gpr`.
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
