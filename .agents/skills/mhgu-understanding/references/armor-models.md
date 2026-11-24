# Hunter armor: files, loading and drawing

What the game does to put an armor piece on a hunter, from the archive on disk to the model on screen, and what
an armor mod's files look like. Offsets are main-relative, 1.4.0. "Bytes" was read from the executable or real
files, "run" was seen in the game (Skin Loader, Eden and MHGU Recomp), "inference" is unchecked. Skin Loader is
the worked example (`mods/skin-loader/`: `src/hooks.rs`, `core/src/convert.rs`, `scripts/make_skin.py`); its
mod-specific choices are in its DEVELOPMENT.md.

## Armor archives

- One archive per part and armor number: `nativeNX/arc/player/com/{f|m}/NNN/{helm,body,arm,wst,leg}.arc`
  (female 571 numbered folders, male 565, numbers 1 to 747; `f/vo` and `m/vo` hold voices). 5,368 archives in
  the 1.4.0 RomFS. ARC layout: [Resources and tooling](resources-and-tooling.md#formats-a-plugin-reads).
- Entry names: `player\mod\{f|m}\plNNN\{f|m}_PARTNNN<rest>`, for example `player\mod\f\pl001\f_body001` (model
  and material share the name, the type tells them apart) and `..._BM` textures. Shared textures live in
  `player\mod\common\` (`f_skin_BM`, `m_skin_BM`, `env_p000_BM`) and appear in many archives. Bytes, every
  armor archive.
- Types (DTI id = the ARC type word; names from the DTI index):

  | Type word | Class | Ext | In which parts (1.4.0 counts) |
  | --- | --- | --- | --- |
  | `0x58a15856` | `rModel` | MOD | every part (helm 1081, body 1079, leg 1072, arm 1061, wst 1027) |
  | `0x2749c8a8` | `rMaterial` | MRL | beside every MOD |
  | `0x241f5deb` | `rTexture` | TEX | 17,862 entries |
  | `0x66c89ed2` | `rPlayerPartsDisp` | | helm only, 1081 |
  | `0x535d969f` | `rCnsTinyChain` | CTC | helm 374, wst 220, body 172, arm 20 |
  | `0x0026e7ff` | `rChainCol` | CCL | helm only, 153 |

- An armor mod's download usually holds these same five archives at `romfs/nativeNX/arc/player/com/f/NNN/`
  (replacing an existing armor's look), sometimes an `exefs` IPS too. Its entries keep the `plNNN` names.

## How a piece is requested

- `0x2875c0(hunter, part, model)` is the only direct request of kinds 42 (male) and 44 (female); parts 0..4 are
  body, arm, wst, leg, helm. It calls `0x27b34c(hunter, part + 16, kind, part, model)`, which releases the
  slot's old request at `hunter + 0x2644 + slot * 4`, calls `0x1529a8(manager, kind, ...)` and stores the new
  archive there. Its callers `0x2899fc` and `0x28a30c` store the real model at `part + 0x137c` first, so the
  model argument of `0x2875c0` changes only which archive loads. Bytes.
- `0x15339c(self, out, kind, part, model)` formats the path after `arc\` that `0x1529a8` builds: kind 42
  `player\com\m\%03d\%s`, kind 44 `player\com\f\%03d\%s`, `part` indexing the names at `0x173e650`. Its
  `sprintf` site `0x153b60` (`add r0, sp, #12; mov r2, r8`, model in r8) is shared by both kinds and is where
  Skin Loader formats `skins\FOLDER\PART` instead. MHGU Definitive Edition replaces the first word of
  `0x15339c` with `add pc, pc, #imm`, so its entry cannot take a Forge hook. Bytes, run.
- `0x2899fc(hunter, slot, model)` changes one part (28 call sites in 10 functions) and returns 0 while the part's
  state at `+0x1378` is above 1. `0x287454` sets bit `slot` of hunter `+0x2460` for an empty slot, which uses
  the hunter's default model. Bytes.
- Part fields: `+0x137c` the model it is changing to, `+0x1380` the installed model (`0x289670` moves it there
  and sets `+0x137c` to -1, so `+0x137c` is not the worn model), `+0x1378` the state. Bytes, run.
- The game loads an archive from any path under `arc\`, not only numbered folders: `arc\skins\FOLDER\PART`
  loads (run).

## How a piece is attached: file IDs

- `0x288d10(hunter, slot, part)`, called only from the part state machine `0x288954`, attaches the part's files
  and moves it to state 4. It finds the MOD by **file ID**, not through the archive: `0x286658(hunter, female,
  slot, model)` returns `table[slot] + model`, then `sFestaFileLoader::getResource` `0x152960` looks the ID up in
  the file table `0x15a0ce0` (67,280 entries of `{~crc32(internal path), type}`) and finds the loaded resource.
  Bytes.
- MOD ID bases (`0x1628480` male, `0x162849c` female; body, arm, wst, leg, helm): male 2558, 4158, 5758, 7358,
  8958; female 3358, 4958, 6558, 8158, 9758. Leather's female body is 3359. Every female armor MOD is in the
  table. CTC (`0x286694`), CCL (`0x286808`) and the helm's `rPlayerPartsDisp` (`0x286960`) are found by ID too,
  each resolver called only from `0x288d10`. MRL and TEX are not in the table. Bytes.
- A model gets its MRL by its own path (`0xb49854`), and an MRL gets its textures by the paths inside it, so
  those two need no file ID. Bytes.
- Consequence, run on Eden: renaming textures and the MRL's texture paths works (the MOD keeps `plNNN`);
  renaming the MOD too makes every ID lookup return null, `0x3071f8` stores the null at `part + 0x1384`, state
  4 skips installing the model, the armor is not drawn and the game freezes at the save screen.
- So a piece under another name must be attached by hand after `0x288d10`: find its MOD, CTC, CCL and display
  file by path hash with the resource manager's find (vtable `+0x38` of the object in cell `0x2126a64`; never
  loads, returns the resource with its count raised) and set them with `0x3071f8`, `0x307238`, `0x307278` and
  hunter `+0x23a8` (Skin Loader's attach hook). Run.
- Open: when a body piece makes the helm follow its model (`0x28a30c`), an empty helm slot keeps the real
  model.

## Loading and sharing

- `rArchive::load` `0xb39f58` reads the table (`count * 0x50` bytes) and passes each row's own internal name
  down; the archive's own path is not part of the key. `sResource::precreate` `0xbca058` and `create`
  `0xbca65c` drop one leading `\`, collapse doubled `\`, take `MtCRC::getCRC(path, -1)` (no case folding) and key
  the resource by `{crc, dti id}`. A live match whose `mState & 0x50` is 0 gets `mRefCount + 1` and is returned,
  and the new archive's bytes are not used; `decodeProc` `0xbc790c` never decodes over a loaded resource. Bytes.
- So two archives whose entries share a name share one loaded file: an unconverted armor mod placed elsewhere
  and the real armor it replaces (or two mods for the same armor number) show whichever loaded first. Anything
  that must show beside the original needs its own internal names. Bytes, inference for what the player sees.
- The path filter at `sResource +0x13040` can redirect any load, including to `savedata:`
  ([Resources and tooling](resources-and-tooling.md#how-the-resource-manager-loads-and-shares-files)).

## Renaming an armor mod's files (the converter rule)

Checked with `make_skin.py` on 18 real armor mods and the plugin's `core::convert` against it:

- An entry or MRL texture path matching `player\mod\[fm]\pl<digits>\[fm]_PART<digits><rest>` becomes
  `skins\FOLDER\PART<rest>`; anything else keeps its name (`player\mod\common\...`, a mod's own extra names
  such as `f_2b_leotard`). Results of 64 bytes or more do not fit the field.
- MOD files are not changed: they name their materials by `crc(name) & 0x7fffffff`, which the MRL's material
  table matches. Texture rows in the MRL hold paths in fixed 64-byte fields.
- Repacking: each entry is one zlib stream, unpacked size in `flags & 0x1fffffff`. A rewritten MRL can go back
  as stored (uncompressed) deflate blocks; other entries are copied packed. The game loads both (run).
- `player\mod\common\` textures keep their names and stay shared with the game, which is safe only while a mod's
  copy equals the stock file (true in all 16 converted skins checked).
- Gender comes from the `\f\` or `\m\` in the names; an archive whose parts mix genders is not one armor.

## Material files (MRL, version 0x22)

- Header: `MRL\0`, version `0x22`; material count +8, texture count +0xc, texture table offset +0x14 (rows of
  0x4c, nonzero type word at +0, path at +0xc), material table offset +0x18. Offsets are file-relative on disk;
  `rMaterial`'s load (`0xb4570c`, vtable `0x1792da4` +0x2c) relocates them after reading and loads each texture
  by its path through the manager's vtable +0x30. Bytes.
- Material rows (0x3c): class hash, name hash `crc(name) & 0x7fffffff`, block size, three render-state hashes,
  command info (count in the low 12 bits), a sort word, block offset at +0x34. A block is commands of 12 bytes
  `{kind in bits 0..3, value, shader object}`, then the constant buffers they point to. Kinds: 0 option, 1 buffer
  (value is its offset in the block), 2 sampler, 3 texture (1-based texture row). A shader object's top 20 bits
  are `~crc32(name) & 0xfffff` of a name in `nativeNX/system/app_shader/AppShaderPackage.mfx`. Bytes.
- `nDraw::MaterialConstant` ignores the scene's light. Ported armor uses it for whole parts or heads; stock armor
  only for 4 glowing pieces. `nDraw::MaterialStd` is the lit one. An unlit material's `CBMaterial`
  `fReflectiveColor` is 1, which the lit shader's cube map turns to chrome. `CBMaterial` starts with
  `fDiffuseColor` (inference from the shader package's field order). Bytes, run for the look.

## Textures in armor

- Part colour maps are DXT5/BC3 (TEX format byte +0xd `0x17`); `_BM+A` masks are BC4 (`0x19`). Data is the last
  `u32 @ +0x10` bytes, 16-byte blocks in the Switch block order; a block's two RGB565 end colours are at +8 and
  +10, so scaling those changes colour without decoding. TEX header: [Resources and
  tooling](resources-and-tooling.md#formats-a-plugin-reads).
- Ported textures can be far brighter than stock: Labubu's body averages 167 of 255 in luminance, Leather's 84.
- Changing colour at load: `rTexture`'s load `0xb51464` reads the pixel buffer with `MtStream::read`
  (`0xb5189c`, buffer r5, size r6) and builds the GPU texture after (`0xb0804c`, `0xb0915c`); a tap at
  `0xb518a0` sees every 2D texture's pixels once, on any host that runs the game's loader. r10 is the header
  from +4 (`[r10, #8]` the format word), the `rTexture` at `[sp, #0x2c]`. Textures already loaded keep their
  pixels, so a change shows only after the game frees and reloads them. Bytes, run (Skin Loader Brightness and
  Saturation).

## Which hunter is which

- Hunter `+0x13c8` is the creator's type: 0 the quest hunter, 1 the village hunter, 2 and 3 the shared preview
  (`0x2761e0`, `0x2762a0`; the save screen and the smithy use type 2), 4 and 5 others (screens not traced).
  Vtable `+0x164` is female. Bytes, run for types 0, 1, 2.
- The creator `0x275a68` sets `+0x13cc` bit 0 only on the local unit, before its armor loads; bit 3 marks a
  Prowler. It writes the member index at `+0x1051` and stores the unit at `sPlayer + 0x1c + member * 4`. So a
  type 0 or 1 hunter without bits 0 and 3 is another player's. Bytes.
- A type 2 or 3 preview is the save screen while no local live hunter exists, and the smithy's otherwise.
  Bytes, run.

Sources: `mods/skin-loader/DEVELOPMENT.md`, `work/skin-loader/{DESIGN.md,resource-sharing.md}`,
`mods/skin-loader/scripts/make_skin.py`, a scan of every `nativeNX/arc/player/com/*/*/*.arc` in the 1.4.0 RomFS,
`work/research-tooling/dti/dti.jsonl` for type names.
