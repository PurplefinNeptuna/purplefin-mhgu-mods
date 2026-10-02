# Installed modding toolkit

Installed locally on 2026-10-01. Double-click `START_TOOLS.sh` and choose
**Execute**, or run `./START_TOOLS.sh` from a terminal. Select a tool and click
**Launch selected tool**. Startup output appears in the launcher's log.
Closing the launcher leaves independently opened tool windows available.

All downloaded applications, runtimes, Python/Node dependencies, and Wine
files are under `tools/`. Tool settings use `tools/state/` where supported.
GIMP, FFmpeg, Wine, Node, and the system compiler/Qt installation were already
available and are reused. No system packages were installed.

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
| Wiki model plugins | MHGU MaxScript import/export resources | `./scripts/tool.sh model-plugins` |
| Wiki binary templates | 010 Editor `.bt` reference files | `./scripts/tool.sh templates` |

Application versions and source commits are recorded in
[tool-versions.json](tool-versions.json). Download hashes are recorded in
`tools/downloads/download-manifest.json`. GitHub release digests were checked
when provided; Blender's official SHA-256 and .NET's official SHA-512 were
checked. Locally recorded hashes without an upstream digest are inventory
records, not independent authenticity verification.

## ARC workflow

Copy the needed original ARC into `work/<mod>/`. For example:

```bash
./scripts/tool.sh salad extract work/my-mod/quest.arc
# Edit files inside work/my-mod/quest_arc/.
./scripts/tool.sh salad inject-recursive work/my-mod --move-originals
```

The last command scans recursively and rebuilds all matching ARC/extracted-folder
pairs in the selected directory. Keep that directory scoped to the intended
mod. `--move-originals` retains originals in `original_data`; do not enable
automatic backup deletion. Avoid SaladSoftware's scratch `inject` command for
existing game archives because it uses default archive settings.

Kuriimu2 requires its bundled plugin directory as the working directory; the
launcher handles this. It also misinterprets paths starting `/mnt/...`.
The launcher prints a temporary workspace alias under `/tmp/mhgu-kuriimu-.../workspace`.
Use that address in its Open/Save dialogs. The alias points to the same project
files and is removed when the tool exits. When a workspace file is passed as a
launcher argument, its path is rewritten automatically:

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

Verify the specific GMD format before editing. The published npm package 0.2.0
dropped 19 metadata fields on the tested keyed `CharMakeMsg_eng.gmd`; the newer
source rejects that format with `Mobile format not implemented`. The default
launcher uses the newer source. A non-keyed `spt_act_base_eng.gmd` passed a
byte-identical decode/encode round trip. Do not use either encoder for keyed
GMDs without a verified preservation workflow. Metadata-bearing formats that
the source accepts also need scrutiny: its JSON adapter omits bucket data.

IFRIT's Windows batch hub uses Windows-specific commands. On Linux, use the
installed encoder wrappers and the HTML STQR editor:

```bash
./scripts/tool.sh ffmpeg -i work/my-mod/music.wav -ar 48000 -ac 2 -f s16le work/my-mod/music.raw
./scripts/tool.sh nxaenc -r 48000 -c 2 -i work/my-mod/music.raw -o work/my-mod/music.opus
./scripts/tool.sh adpcm work/my-mod/effect.wav work/my-mod/effect.adpcm
./scripts/tool.sh stqr
```

`nxaenc` and `adpcm-encoder` run the upstream executables through Wine in
`tools/wine-ifrit`; paths are translated automatically. `adpcm` uses IFRIT's
Python conversion to generate Capcom ADPCM with the native FFmpeg and the
Wine encoder. Match the original asset's channel, sample rate, and loop format
before making a replacement. Music looping/STQR edits remain a separate step.

Blender importing a converted GLTF/GLB does not provide an MHGU `.mod` exporter.
The supplied MHGU MaxScript plugins require a compatible licensed 3ds Max
installation. 3ds Max, Photoshop, and 010 Editor were not installed. ImHex cannot
execute 010 Editor `.bt` templates; those templates remain format references.

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
