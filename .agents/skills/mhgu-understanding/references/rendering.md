# Rendering: NVN table, shaders and post-processing

Offsets are main-relative, MHGU 1.4.0. Each fact names its source: bytes, a translated shader, or a run.

## The NVN function table

- The game calls NVN through a table of 478 pointers at main+`0x191f700`..`0x191fe78`, in BSS (writable). Its loader fills it at startup in the order of the game's `nvn*` name strings (main+`0x154b65b`..`0x1571bb6`). Bytes; slot names fit one base for 22 slots taken from a working Recomp plugin.
- Slots used so far: `nvnCommandBufferBeginRecording` `0x191fc48`, `BindProgram` `0x191fc78`, `BindUniformBuffer` `0x191fc84`, `BindTexture` `0x191fc9c`, `DrawArrays` `0x191fcd0`, `DrawElementsBaseVertex` `0x191fcd8`, `UpdateUniformBuffer` `0x191fd9c`, `nvnTexturePoolRegisterTexture` `0x191f870`, `nvnQueuePresentTexture` `0x191f7c8`. The memory pool, buffer and texture builders' `SetDevice` are at `0x191f820`, `0x191f8a4` and `0x191f8e8`.
- On MHGU Recomp the entries are the host's own stubs; on Eden they point into the game's NVN driver code. Run (Recomp and Eden).
- In gameplay the game draws only through `DrawArrays` (full-screen and 2D) and `DrawElementsBaseVertex` (models). It never calls the instanced, indirect or plain `DrawElements` entries, `BindUniformBuffers`, `BindTextures` or `UpdateUniformBuffer`. Run.
- A texture handle's low 20 bits are its texture pool slot. `rTexture +0xd0` (`mpTexture`) points to an `nDraw::Texture`, whose word at +0x34 is that slot. Run: a skin's albedo slot is the one its draws bind.
- Uniform buffer and vertex addresses are 32-bit CPU addresses on MHGU Recomp and 64-bit GPU addresses (unreadable) on Eden. Run.

## Shaders

- The compiled shaders are `nativeNX/sa/NX/root.arc`, entry `sc\NX\root` (type `rShaderPackage`, `SPK\0`, 6311 programs). Its first 0xdf20c bytes are tables, the rest code. `AppShaderPackage.mfx` holds names and constant-buffer layouts only. Bytes.
- In memory, the package resource is at `*(*(main+0x2126afc) + 274748)`. Record i is 18 words at data word 4106 + 18 i: fragment shader object at [9], program object at [14] (its NVNprogram at +8). A shader object has vtable main+`0x1837710`, code at word [22] and its GLSLC control section (magic `0x98761234`) at word [24]. Run on both hosts.
- On Eden the code is GPU memory; the control section is CPU memory on every host. Run.
- NVN uniform binding i appears as `cb(i+3)` in translated shaders.
- The unlit material's shader ("Base Color", FNV-1a 64 over 0x300 bytes `0x96F18A048B1BCADB`, 29 copies) computes `rgb = texture.rgb * cb4[3].rgb * cb3[0][0]` and `a = texture.a * cb4[3].a`, discarding below 0.001. It reads nothing else from `cb4`. Translated shader.
- Its control section (FNV-1a 64 over 0x704 bytes) is `0x966a06f682cc5c7f`. Two full-screen post shaders share it. Bytes.
- On a skin draw `cb4[3]` is 1, 1, 1, 1, and material-file constants (`fDiffuseColor`, `fConstantColor`, `fEmissionColor`, `fAlbedoColor`) do not change it. Run and tester.
- `cb3[0]` is `CBHDRFactor`: compress encode 0.5, decode 2.0. The scene buffer stores color times 0.5. Run.

## Post-processing

- Pass order in a gameplay frame: bloom extract (the scene before grading), grading, bloom (additive), `uMhFilter` gradient overlays, then 2D. Run on Recomp.
- Grading shader: `out = pow(max(0, w * (c * M + t) + (1 - w) * c), gamma)`, M rows `cb4[0..2]`, t `cb4[3]`, w `cb5[0].w`, gamma `cb6`. Translated shader. w and gamma were 1.0 in every area seen. Run.
- `uColorCorrectFilter` (DTI vft `0x178a3e4`) rebuilds its matrix at +0x750 (16 floats) in vtable slot 0x24 (`0x8c6f68`). It starts at identity and multiplies in each enabled corrector with a nonzero type (16 at +64, 64 bytes each; type +0x14, factor +0x20). The uploaded matrix equals it in every area seen. Bytes and run.
- Corrector types, with k = 2 * factor (`0x8c51a0`, jump table `0x8c51dc`):

| Type | Matrix |
| --- | --- |
| 2 | contrast around 0.5: `c' = (c - 0.5) k + 0.5` |
| 4 | per-channel saturation around the RGB mean (weight 1/3) |
| 5 | saturation by factor.x around luma 0.29891, 0.58661, 0.11448 |
| 6 | per-channel level: factor above 0.5 gives `c (1 - t) + t` with t = 2 (factor - 0.5), else `2 factor c` |

- The 242 area schedulers (`stage/mNN?/aNN.arc`, `sdl\mNNaNN?-f`) use types 4 (231), 2 (169), 6 (44) and 5 (2). m05d a02 animates a type 6 corrector 0.5, 0.7, 0.52, 0.5 over 361 frames. Bytes.
- Bloom extract keeps the brightest channel's excess over `cb4[0].w` (1.0) of `rgb / a * cb3[0].w * cb3[0].z`. Bloom adds the blurred result times its color (`uBloomFilter +96`, threshold +116). Translated shaders and run.
- `uBloomFilter` is DTI vft `0x178a484`, 192 bytes. Of the 240 area schedulers, 205 start `mThrethold` at 0.9; m01d a06 keys 0.1 throughout and m01n a10 ends at 0.1. m01d a06 keys `mBloomColor` 0.15; 19 areas start it with a channel at 1.0. Bytes.
- `uMhFilter` (vft `0x177b164`) draws a full-screen quad in vertex colors. Its corners are `mColor[4]` at +48 (R in the low byte; 0 and 1 top, 2 and 3 bottom). Its span is `mTopPos` +68 to `mBottomPos` +70, in rows of 256 from the top. Its blend is `mBreandState` +64. Run: the drawn colors and spans equal these.
- Blend state 15 multiplies by `rgb + 1 - a` (DST_COLOR, ONE_MINUS_SRC_ALPHA); 0 adds `rgb * a` (SRC_ALPHA, ONE). Run. Quest map overlays multiply red by up to about 1.33 and can darken the screen's bottom band to about 0.25.

## Finding the filters

- `sUnit` (cell main+`0x2126f48`) has 32 move lines of 24 bytes from +0x1c. A line's first unit is at +0xc, a unit's next at +0x14 (`sUnit::registerUnit` `0xc067ec`). A unit's class is its vtable (DTI `vft`). Bytes and run.
- Each area's scheduler sets its lights, `uMhFilter` top, middle and bottom, `uColorFog`, `uBloomFilter`, `uColorCorrectFilter` and `uStableShadow`. Many animate within an area. No area uses `uToneMapControl`. Bytes.
