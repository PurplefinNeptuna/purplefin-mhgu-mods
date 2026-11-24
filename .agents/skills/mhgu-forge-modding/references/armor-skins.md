# Armor mods and skins

Skin Loader is the worked example (`mods/skin-loader/`: `src/hooks.rs`, `core/src/convert.rs`, `scripts/make_skin.py`). The game's side is in `mhgu-understanding` [Hunter armor](../../mhgu-understanding/references/armor-models.md).

- An armor mod's download usually holds these same five archives at `romfs/nativeNX/arc/player/com/f/NNN/`
  (replacing an existing armor's look), sometimes an `exefs` IPS too. Its entries keep the `plNNN` names.
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
- Ported textures can be far brighter than stock: Labubu's body averages 167 of 255 in luminance, Leather's 84.
