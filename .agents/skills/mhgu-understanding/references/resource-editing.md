# Find and edit resources without losing data

## Locate the input

Use `rg --files` on a dump or copied extraction and targeted `rg -n` on indexes. The offline `CFileIndex.md` maps ARC containers and internal resources. Search a basename, internal path, extension/type hash, and language variant. Its Windows separators are index notation; Linux paths and case must match actual files.

```sh
rg -n -m 8 'itemData|weapon07BaseData' references/MHGU-Modding.wiki/CFileIndex.md
rg --files references/MHGU-Modding/templates references/MHGU-Modding/weapon_MV_Index
```

| Target | Search location / reference lead |
| --- | --- |
| Monster files | `nativeNX/arc/enemy/em*.arc`, Monster-IDs, Monster-Modding, templates |
| Weapons/actions | `nativeNX/arc/player/quest/wXX.arc/player/param`, weapon ID lists, `weapon_MV_Index/`, command/attack templates |
| Armor models | `nativeNX/arc/player/com/m` or `/f`, piece-specific ARC files |
| Item/armor tables | MHGU `nativeNX/loc/arc/resident.arc/table`; MHXX wiki examples may use a different root |
| Quest groups/counter | Exact common ARC variant and internal QSG/GUI entry, Quest-IDs, native quest readers |
| Text | GMD messages, language-specific entries, localized resident archives |
| Fonts | `nativeNX/<language>/GUI/02_common/font/font_festa.gfd` plus matching resident TEX pages |
| Audio | Audio-Index and Audio-Files-And-Extensions, STQR metadata and actual encoded stream |

Wiki table claims are leads, not all locally validated formats. itemPreData combination inputs refer to table positions, not necessarily item IDs. Preserve header counts and unknown fields and verify against the actual resource/native consumer before editing. The wiki documents some weapon durations in 60-Hz units despite 30fps rendering, while other values are seconds. Determine each field's units rather than scaling all parameters alike.

## Wiki `.bt` templates checked against 1.4.0

`python3 scripts/check_wiki_templates.py [ROMFS]` tests 27 of the 66 templates in `references/MHGU-Modding/templates/` against the RomFS dump: header plus count times packed record size must equal the file size (run 2026-10-20). A fit proves record size only, not field names or meanings. The other 39 (variable or nested layouts such as `stqr`, `mfx`, `xfs`, otomo skill files, audio) are untested.

| Status | Templates |
| --- | --- |
| Fit every file | `arc` (same layout as `mhgu_assets.read_arc`), `wpd`, `wcd`, `wXXm`, `itemData` (44), `itemPreData` (24), `alchemyData`, `amlt`, `amskl`, `amslt`, `sem`, `slt`, `ssjje`, `sup`, `tril`, `skd`, `emsizetbl`; `gui` magic/version only on all 1,972 files, body unverified |
| Fit some files | Weapon templates, below. `gmd` fits 11,514 unkeyed files, but misses all 485 keyed files and reads the file name as entry 0; use `tools/gmd` instead. `rem` fits 6,553 files; `guestRemData` shares the type with a 67-byte record |
| Wrong | `apd` armor recipes: template 38 bytes, all five `armorCreateA0x` files use 42. `ot_lvl` record fits, but real files start with `00 00 80 3F`, not the listed ID bytes |
| No file found | `itemPreTypeData` hash `63D62424` is absent from the dump |

Weapon tables in `loc/arc/resident.arc/table`, real record size per family:

| Table | Template fits | No template (real size) |
| --- | --- | --- |
| `weaponXXBaseData` | `w00d` (33): GS, SnS, Hammer, Lance, LS, Bow, HH; `w04d` (32): HBG, LBG | SA, GL, DB, IG, CB (34) |
| `weaponXXLevelData` | `w00d_lvl` (15): GS, SnS, Hammer, Lance, LS, IG; `w04d_lvl` (100): HBG, LBG | GL, HH (16); SA, DB, CB (17); Bow (31) |

Never apply a template to a family it misses. Derive missing fields from Ghidra/DTI first, then add the family to the script.

## ARC copy/edit/repack

Copy and SHA-256 the original before editing. Keep the containing archive, entry inventory, payload hashes, and original repack baseline. Never edit the only dump/library copy.

```sh
./scripts/tool.sh salad extract work/my-mod/quest.arc
# Edit the intended copied entry.
./scripts/tool.sh salad inject-recursive work/my-mod --move-originals
```

Scope recursive inject to the mod's work directory. `--move-originals` keeps `original_data`; leave automatic backup deletion off. Scratch `inject` uses defaults unsuitable for preserving an existing archive. Re-extract the rebuilt ARC and compare entry names/types/counts, changed data, and every unrelated payload. A successful tool exit is insufficient.

SaladSoftware 2.4.2 no-edit smoke repacks of copied Barioth/localized quests were byte-identical, with 468/328 resources; a changed-entry check preserved unrelated payloads. Those results apply to those inputs. Large shader root ARC resource length required a 30-bit field; an ordinary 24-bit helper cannot silently handle every archive.

Kuriimu2 uses MT Framework / MT ARC, plugin ID `5a2dfcb6-60d6-4783-acd1-bc7fb4a65f38`. Launch through `./scripts/tool.sh kuriimu PATH` or `kuriimu-cli` for the correct working directory/private runtime. If its GUI misreads a Linux absolute path, use the printed temporary workspace alias. CLI archive context needs `back-to-main` before `exit`.

## Text, fonts, and textures

```sh
./scripts/tool.sh gmd decode --out work/my-mod/text-json work/my-mod/text.gmd
./scripts/tool.sh gmd encode --out work/my-mod/text-rebuilt work/my-mod/text-json/text.gmd.json
./scripts/tool.sh revil mtf_tex_to_dds --platform NSW work/my-mod/texture.tex
```

Classify GMD format before conversion. npm gmd 0.2.0 dropped 19 metadata fields from keyed `CharMakeMsg_eng.gmd`. The newer/default build rejects it with `Mobile format not implemented`. Non-keyed `spt_act_base_eng.gmd` round-tripped byte-identically. General keyed-GMD editing remains unverified; JSON export can omit bucket data. A few purpose-built bounded text changes do not establish a general encoder.

Native fonts pair GFD glyph mapping/metrics with TEX atlas pages. Altering page images without updating Unicode/page/position/advance/size data breaks text. The offline font tutorial describes packed glyph fields and layout adjustments. Validate the real header and entry stride before editing. Larger glyphs can require companion line/window textures. Preserve language and controller prompts while merging font assets.

The item icon atlas `GUI\99_texture\HD_cmn_icon_GSM_NOMIP` is in every language's `<lang>/arc/resident_<lang>.arc` (type `0x241f5deb`): grey RGBA8 art in the `rTexture` and block-linear layouts of [File layouts](file-formats.md#file-layouts). The base game's is 512x1024 (2,097,176 bytes unpacked); a replaced atlas can be 1024x2048 (8 MiB), so never assume the size.

It holds each icon twice: 32-texel cells from the top (`mIconType`, ten to a row), and 48-texel cells from y 416 in the same order. All are scaled with the width. Checked on cells 2, 13, 21 and 36 at both sizes. Some cells are drawn differently per language: cell 9 (ore) in German, Italian and Spanish.

BC formats tile 4x4 blocks (8 bytes BC1, 16 bytes BC3): `HD_questCounter_BM_NOMIP` (1024x1024), `HD_lobby00_BM_NOMIP`, `HD_window_BM_MQ_NOMIP` and `HD_custom_pnl2_BM_NOMIP` (512x512) are BC3 in `resident_eng.arc`, decoded and checked by eye.

GMD text tables (layout in the table below): `resident_<lang>.arc` `weapon13MsgData`, `itemData`, `CommonMsg` and `StartMenuMsg` have the same string count in all seven languages. So an index names the same text in each. `CommonMsg` 0 is the price format `%dz`. A `weapon13MsgData` without the language suffix is a different 4-string table.

Quest names are string 0 of `loc/arc/quest/*.arc` `<lang>\quest\questData\questData_<id 7 digits>_<lang>`. Logical GUI atlas coordinates need not equal physical HD pixels. Preserve texture descriptors, format, dimensions, mip/swizzle/platform requirements and alpha. DDS/PNG export alone does not prove a valid reinjected TEX.

Compare unchanged roundtrip and then verify the edited in-game consumer.

## Models, gameplay tables, and audio

Revil `mod_to_gltf` converts a copied MOD for inspection; a smoke test produced GLB imported by Blender as 18 meshes. Blender GLTF/GLB import provides no general MHGU MOD exporter. Wiki MaxScripts require compatible licensed 3ds Max. No verified GLTF-to-MHGU exporter is available. Do not promise a roundtrip from a successful preview.

Titanbreak targets known monster HP/rage/loot/stagger/resident data; MHGUQuestEditor targets supported quest data. The wiki lists monster size, AI, new-monster and speed questions with incomplete knowledge. A tool name or visible field does not prove support for every version/resource.

IFRIT wrappers handle Opus/DSP/Capcom ADPCM encoding. Match channel count, sample rate, format, and loop metadata:

```sh
./scripts/tool.sh ffmpeg -i work/my-mod/music.wav -ar 48000 -ac 2 -f s16le work/my-mod/music.raw
./scripts/tool.sh nxaenc -r 48000 -c 2 -i work/my-mod/music.raw -o work/my-mod/music.opus
./scripts/tool.sh adpcm work/my-mod/effect.wav work/my-mod/effect.adpcm
./scripts/tool.sh stqr
```

An encoded tone/header check establishes encoding, not music-loop/STQR correctness. The Windows batch hub is not the Linux entrypoint. Existing wrappers use private Wine paths and explicit path translation.

## Tool limits and evidence

`START_TOOLS.sh` and `scripts/tool.sh` own launcher commands. Pax browses ARC/textures, ImHex edits bytes, Revil converts supported formats, GIMP edits imagery, Blender inspects models, and Audacity edits audio. 010Editor `.bt` files are format references for ImHex, not executable ImHex templates.

Private runtimes avoid changing host packages: Kuriimu2's matching .NET 3.1.32 starts its GUI, while a .NET 9 substitution crashed it; ImHex requires its private 0700 runtime path; Pax uses private LLVM 19 libraries. In another environment re-establish prerequisites rather than copying absolute paths.
