# Installed modding toolkit

Installed 2026-10-01. Double-click `START_TOOLS.sh` > **Execute**, or run
`./START_TOOLS.sh`. Select a tool > **Launch selected tool**. Startup output is
logged; closing the launcher leaves tool windows open.

Downloads, runtimes, Python/Node dependencies and Wine files:
`tools/`; settings: `tools/state/` where supported. Existing GIMP,
FFmpeg, Wine, Node, compiler/Qt are reused; no system packages installed.

## Available tools

| Tool | Role | Launcher |
| --- | --- | --- |
| [SaladSoftware](https://github.com/RTHKKona/SaladSoftware) 2.4.2 | ARC extract/repack GUI and CLI | `./scripts/tool.sh salad` |
| [Pax Arc Explorer](https://github.com/Paxlord/pax_arc_explorer) 0.0.9 | Native ARC browser and texture viewer | `./scripts/tool.sh pax` |
| [Kuriimu2](https://github.com/FanTranslatorsInternational/Kuriimu2/releases/tag/1.2.1) 1.2.1 | ARC/texture editing; GUI and interactive CLI | `./scripts/tool.sh kuriimu` |
| [ImHex](https://github.com/WerWolv/ImHex/releases/tag/v1.38.1) 1.38.1 | Native binary editor | `./scripts/tool.sh imhex` |
| [Blender](https://download.blender.org/release/Blender4.5/) 4.5.14 LTS | Model inspection/editing | `./scripts/tool.sh blender` |
| [Revil Toolset](https://github.com/PredatorCZ/RevilLib/releases/tag/nightly) 2.10.201 | MOD-to-GLTF and TEX-to-DDS, other MT Framework converters | `./scripts/tool.sh revil MODULE INPUT` |
| GIMP 3.2.6 | Image/texture editing; existing system installation | `./scripts/tool.sh gimp` |
| [Audacity](https://github.com/audacity/audacity/releases/tag/Audacity-4.0.1) 4.0.1 | Waveform editing and loop-point selection | `./scripts/tool.sh audacity` |
| [IFRIT](https://github.com/RTHKKona/HBMK-IFRIT) | Opus and DSP/Capcom ADPCM encoding | `nxaenc`, `adpcm-encoder`, `adpcm` launch commands below |
| IFRIT STQR editor | Browser editor for audio metadata | `./scripts/tool.sh stqr` |
| [Titanbreak](https://github.com/RTHKKona/Titanbreak-Tools) | Monster HP, rage, loot, stagger, resident data | `./scripts/tool.sh titanbreak` |
| [MHGUQuestEditor](https://github.com/Fexty12573/MHGUQuestEditor) | Native Linux quest editor built from source | `./scripts/tool.sh quest` |
| [GMD](https://github.com/beeequeue/gmd) | Text decoding/encoding; current upstream source build | `./scripts/tool.sh gmd --help` |
| [Ghidra](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build) 12.1.4 | Imported MHGU 1.4.0 code database, disassembly and decompilation | `./scripts/tool.sh ghidra` |
| [MHGU DTI dumper](https://github.com/Fexty12573/mhgu-dti-dumper) | Runtime reflection results indexed; extraction plugin removed after trial | `./scripts/tool.sh research find QUERY --kind dti` |
| [forge-rs](https://github.com/Fexty12573/forge-rs) 1.4.1 | Rust Forge plugin crates and Cargo scaffold/build command; isolated runtime | `./scripts/tool.sh forge-rs status` |
| Wiki model plugins | MHGU MaxScript import/export resources | `./scripts/tool.sh model-plugins` |
| Wiki binary templates | 010 Editor `.bt` reference files | `./scripts/tool.sh templates` |

[Versions/commits](tool-versions.json); download hashes: `tools/downloads/download-manifest.json`. Checked supplied GitHub
digests, official Blender SHA-256 and .NET SHA-512. Local hashes without
upstream digests establish inventory, not authenticity.

[RESEARCH_TOOLING.md](RESEARCH_TOOLING.md) covers Ghidra/code/type/DTI indexes; consult them before
code/gameplay mods. Imported `.text` has one changed byte and
conflicting types: patch from verified original NSO. Saved DTI: 3,152
classes/66,752 properties (2026-10-03). Dumping broke quest controls;
removal/restart restored them. Keep dumper removed; use saved data.
Evidence/new-trial rules: [DTI_DUMPER_RUNTIME.md](DTI_DUMPER_RUNTIME.md).

[forge-rs setup and commands](FORGE_RS_TOOLING.md) covers the pinned source,
existing private Rust runtime and ARM32 build checks. Read the
[Damage Numbers migration assessment](FORGE_RS_DAMAGE_NUMBERS.md) before using
its hook/config wrappers with the maintained Forge fork.

## ARC workflow

Copy the needed original ARC into `work/<mod>/`. Example:

```bash
./scripts/tool.sh salad extract work/my-mod/quest.arc
# Edit files inside work/my-mod/quest_arc/.
./scripts/tool.sh salad inject-recursive work/my-mod --move-originals
```

The last command recursively rebuilds matching ARC/folder pairs. Scope its
directory to the mod. `--move-originals` keeps `original_data`; leave
automatic backup deletion off. SaladSoftware's scratch `inject` uses
defaults, so avoid it for existing archives.

Launcher sets Kuriimu2's required plugin working directory. For misread
`/mnt/...` paths, use its printed `/tmp/mhgu-kuriimu-.../workspace` alias in Open/Save.
It points to the workspace and disappears on exit; launcher arguments are
rewritten automatically:

```bash
./scripts/tool.sh kuriimu work/my-mod/quest.arc
./scripts/tool.sh kuriimu-cli
```

For manual plugin selection, MHGU archives use **MT Framework / MT ARC**.
Its CLI plugin ID is `5a2dfcb6-60d6-4783-acd1-bc7fb4a65f38`.
The archive CLI context uses `back-to-main` before `exit`.

## Models, textures, text, and audio

```bash
./scripts/tool.sh revil mod_to_gltf work/my-mod/model.mod
./scripts/tool.sh revil mtf_tex_to_dds --platform NSW work/my-mod/texture.tex
./scripts/tool.sh gmd decode --out work/my-mod/text-json work/my-mod/text.gmd
./scripts/tool.sh gmd encode --out work/my-mod/text-rebuilt work/my-mod/text-json/text.gmd.json
```

Verify GMD format first. npm 0.2.0 dropped 19 metadata fields from keyed
`CharMakeMsg_eng.gmd`; newer/default source rejects it with `Mobile format not implemented`.
Non-keyed `spt_act_base_eng.gmd` round-tripped byte-identically. Neither safely
handles keyed GMD without a preservation workflow. Accepted metadata formats
also need review: JSON omits bucket data.

IFRIT's Windows batch hub uses Windows-specific commands. On Linux, use the
installed encoder wrappers and the HTML STQR editor:

```bash
./scripts/tool.sh ffmpeg -i work/my-mod/music.wav -ar 48000 -ac 2 -f s16le work/my-mod/music.raw
./scripts/tool.sh nxaenc -r 48000 -c 2 -i work/my-mod/music.raw -o work/my-mod/music.opus
./scripts/tool.sh adpcm work/my-mod/effect.wav work/my-mod/effect.adpcm
./scripts/tool.sh stqr
```

`nxaenc`/`adpcm-encoder` use Wine in `tools/wine-ifrit`,
translating paths. `adpcm` uses IFRIT Python, native FFmpeg and Wine
to produce Capcom ADPCM. Match channels, sample rate and loop format; music
looping/STQR needs separate edits.

Blender GLTF/GLB import supplies no MHGU `.mod` exporter. MHGU
MaxScripts need licensed compatible 3ds Max. 3ds Max/Photoshop/010 Editor are
uninstalled. ImHex cannot run `.bt`; use templates as format
references.

## Local compatibility adjustments

- Pax uses project-local LLVM 19 C++/unwind libraries from Debian packages.
- ImHex uses a private runtime directory with mode 0700, preserving the host's
  runtime directory permissions and Wayland socket address.
- Kuriimu2 uses private .NET 3.1.32, legacy SSL libraries, and invariant
  globalization. Rolling it forward to .NET 9 started the CLI but crashed its
  GUI; the matching runtime passed the startup check.
- MHGUQuestEditor uses the installed Qt 6 and GCC. Build flags are
  `-fpermissive -fno-char8_t`; `scripts/tool-patches/quest-editor-linux.patch`
  adds explicit Qt index casts and the missing `<ctime>` include. To rebuild:

```bash
cmake -S tools/quest-source -B tools/quest-build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
  '-DCMAKE_CXX_FLAGS=-fpermissive -fno-char8_t'
cmake --build tools/quest-build --parallel 6
```

## Verification performed

- SaladSoftware extracted the copied Barioth and localized quest archives.
  No-edit repacks were byte-identical, covering 468 and 328 resources.
  A test repack changing one resource preserved every unrelated resource.
- Kuriimu2's MT ARC plugin loaded the copied enemy archive through the
  launcher's alias; its GUI passed startup with the matching runtime.
- Revil converted the enemy MOD to GLB and a TEX to DDS. Blender imported the
  GLB with 18 mesh objects.
- NXAenc and AdpcmEncoder encoded a generated 0.2-second tone. The final
  `adpcm` launcher produced a Capcom ADPCM file with a matching mono header.
- GMD preservation checks and limitations are described above.
- SaladSoftware, Pax, Titanbreak, ImHex, Audacity, the native quest editor,
  Kuriimu2, and the toolbox passed brief desktop startup checks. These checks
  establish startup, not full interactive editing or visual layout correctness.
- The copied game inputs' source hashes remained unchanged. Logs and scratch
  samples are in `work/tool-smoke/`; no test output was installed into Eden.

No in-game validation, quest-save validation, texture replacement/import test,
music playback/loop test, or model-export round trip has been performed.

## Cleanup on 2026-10-02

Redundant installers/npm cache were removed after checking installed copies.
`tools/downloads/` retains provenance/checksums; tools/runtimes/pinned
dependencies remain. Evidence: `work/tool-smoke/`; large sample trees are
regenerable. Historical visual outputs are archived outside Eden:
`docs/CLEANUP_HD_PROJECT.md`.
