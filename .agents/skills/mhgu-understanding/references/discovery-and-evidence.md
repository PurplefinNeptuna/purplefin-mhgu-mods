# Discover code, objects, and resources

## Establish the input

| Identity | Verified reference |
| --- | --- |
| Game | MHGU Switch 1.4.0, title `0100770008DD8000` |
| Main NSO SHA-256 | `b3935415499549adaf4c0e89822831daa175cfd456a7990791c79be3997645ef` |
| Build ID | `FB08F1D20FD1204FE7070672777F869B`, zero-padded to the full 32-byte NSO field |
| Cheat filename identifier | `FB08F1D20FD1204F`, shortened and insufficient to verify a live executable |
| Imported Ghidra image base | `0x009c9000` |

An NSO is a segmented executable, not a flat runtime image. Use the existing `main_image` helper, which checks exact hash/build, segment bounds, LZ4 decompression, and recorded segment hashes. Do not seek to a main-relative address directly in a compressed NSO. Verify the running target separately from a copied file.

## Search code before opening a GUI

From the original workspace root:

```sh
./scripts/tool.sh research status
./scripts/tool.sh research find 'MtDti::from' --kind functions --limit 3
./scripts/tool.sh research find 'uPlayerQuest07' --kind symbols --limit 5
./scripts/tool.sh research find '/MTF/MtProperty' --kind types --limit 3
./scripts/tool.sh research find 'cGUIObjTexture' --kind dti --limit 5
```

The search is case-insensitive over JSONL text and can match field names as well as record names. Default kind is all, limit 30. No match does not prove absence from the game; an index may be missing or use another name. Use targeted `rg -n` for exact names/fields and inspect surrounding records. Avoid printing huge file/resource indexes wholesale.

Saved files: `work/research-tooling/ghidra-export/{functions,symbols,types}.jsonl`, `summary.json`, and `work/research-tooling/dti/dti.jsonl`. The import contains 47,986 functions, 2,786 types, and 736,837 symbols, including 3,736 user-defined symbols. Generated labels contribute to the total.

Database address minus imported image base gives the main-relative offset. Example: `MtDti::from` at `0x01177f68` becomes main+`0x007aef68`. At runtime, add the actual main text base. Property offsets are within objects and must not have the image base subtracted.

The imported `.text` differs from original main at offset `0x00283710` (database `0x00c4c710`): original byte `0x49`, database `0x52`. Preserve the supplied database difference; patch/signature bytes come from original main. Data/GOT/initializer differences are not fully normalized. Conflicting annotations include `MtProperty` 56 versus 88 bytes and pointer-width inconsistencies. Validate layout through ARM32 instructions/bindings and actual field access.

The DTI registry main+`0x018a5d7c` and the property-list vtable main+`0x0177e9a0` have code references; they are research targets, not gameplay proof.

Open analysis with `./scripts/tool.sh ghidra`. The preserved GZF is `work/research-tooling/inputs/MHGU_1.4.0.gzf`; editable project is `work/research-tooling/ghidra-projects/MHGU_1.4.0.gpr`. To refresh indexes, close that GUI project and run `./scripts/tool.sh research export`. Export uses read-only/noanalysis mode and copied-main verification. `research import` creates a fresh project and refuses to overwrite an existing one. Preserve annotations and original GZF.

To decompile or cross-reference specific addresses, write your own targets file in the task's work folder (for example `work/<mod>/ghidra-targets.txt`): one main-relative `0x` offset per line, with `#` comments saying why each is there. Then run `./scripts/tool.sh research export --targets work/<mod>/ghidra-targets.txt`. Read each target's symbols, containing function and references in `summary.json` `research_targets`, and function starts' C in `ghidra-export/function_<offset>.c`. Each run replaces the previous target output. Never add task offsets to `scripts/ghidra/ExportMhguResearch.java`; its list holds only the shared baseline.

## Understand DTI records

DTI is class metadata: name, inheritance, size, constructors, properties, and virtual methods. `MtDti::find("cGUIObjTexture")` finds a class descriptor, not a drawable instance. Singleton lookup such as `sMhGUI` locates an existing object. A class descriptor does not guarantee that its generic construction path is valid for every subclass.

Saved runtime extraction has 3,152 records, 3,075 distinct names, 66,752 properties, 2,973 object-vtable and 179 DTI-vtable/skipped records. Names repeat between registry/singleton entries, and properties include inheritance. Filter `vft_kind`: `object` vtables describe instances, `dti` vtables belong to skipped class metadata. Zero callbacks can mean absence. Verify the intended record before using offsets, constructor slots, or sizes.

The dump SHA-256 is `ea4c31e1845ea8f2fa7bda3173de0f324e97148683c12364fabb550e99f1175c`. Vtable/callback addresses are main-relative; property offsets are object-relative bytes. ARM32 dumper checks establish `MtDti` 32, `MtProperty` 56, and property-list view 8. Verify target-specific inheritance/layout rather than using these sizes indiscriminately.

DTI extraction creates/destroys live objects and queries singletons. The 2026-10-03 run produced valid JSON but broke quest controls until plugin/flag removal and restart. Reuse the saved dump. Any new trial needs separate authorization, save backups, exact build checks, retained logs, removal of package/flag, and restart. Output is `savedata:/dti_dump.json`, not RomFS. Index only a copied dump with `./scripts/tool.sh dti-dumper import PATH`.

## Find names, IDs, and serialized data

Use the offline wiki's CFileIndex to connect an internal resource name to its containing ARC. Search the smaller ID lists for items, monsters, quests, and weapon categories, and `weapon_MV_Index/` for attack/motion data. An object ID, quest ID, group category, table position, and file-name hash are different identifiers.

Trace a resource from ARC entry/name/type to its native loader and runtime consumers. For behavioral questions, find the runtime call and compare input/output rather than editing a table based on a suggestive name. The wiki includes MHXX material and WIP fields; mark those as research leads until verified on the supplied MHGU resource.

The GNU build-ID note in main is at `0x172e52c` (namesz 4, descsz 16, type 3), the ID itself at `0x172e53c`. Main SHA-256 `b3935415499549adaf4c0e89822831daa175cfd456a7990791c79be3997645ef`; loaded-memory SHA-256 `24c208c395c65727b21b5fa91af8381396e70cf421b0fcfee0345d8743298110`.

Sources: `docs/TOOLS.md`, `scripts/{research_tools.py,mhgu_binary.py,dti_dumper.py}`, `scripts/ghidra/`, saved summary/provenance, `mods/dti-dumper-support/README.md`, `references/MHGU-Modding.wiki/`, and `references/MHGU-Modding/`. [Workspace and sources](workspace-and-sources.md) provides snapshot revisions and machine paths.
