# Sounds and jingles

Static reading of the 1.4.0 main and RomFS, plus the MHGU Recomp runs named.
Source: `work/wishfinder/NOTICES.md`; decoded samples in
`work/wishfinder/sound-samples/`.

## Playing a menu sound

`0x54f260(kind, id)` picks one of the sound-manager calls by kind: 0 `0x4eeb78` with an id, 1 `0x4eec94`, 4 `0x4ef2c4`, 6 `0x4eed04` (bank 0..6 in all). The native cursor `0x54ee98` calls the kind functions directly. Bank 0 ids the game uses most: 2 (356 sites), 1, 6, 3, 13, 4, 14, 7, 10, 16, 31, 9, 15, 21, 27, 30; bank 1 uses ids 101..194.

The smithy uses `0x54f260(0, n)` with 1 accept, 2 cancel, 3 deny (heard in WishFinder). Which kind is cursor move and which page turn is unread. How n becomes a sound is open: `0x4eeb78(sound, n)` only queues n at slot +0x10 on `mpResSeSys` (+0xc0 of `sSoundControl`, DTI vft `0x17696a0`) for `0x887648`. Reading n as a `snd_sys_com` request id is unsupported: n = 43 (request `lb_sys_chat_reception`) played nothing in a quest, and request 2 is `sys_moji`, not cancel.

## Sound data

- Menu sounds are `sound\se\system` in `loc/arc/resident.arc`: 36 waves (type `0x79c47b59`), bank `snd_sys_com` (SBKR, `0x15d782fb`, 50 entries naming the waves in order, some twice) and request table `snd_sys_com` (SRQR, `0x1bcc4966`, 57 records of 0x84 bytes from 0x34: u16 request id at +0, u16 bank entry at +0x12). Requests include 1 `sys_kettei`, 3 `sys_box_get`, 5 `sys_saywindow_important`, 6 `sys_cancel`, 7 `sys_bubu`, 9 `sys_info`, 14 `sys_mix_success`.
- Quest common sounds are `sound\se\com\wav` in `loc/arc/quest.arc` (148 waves).
- Waves are DSP-ADPCM, mono or stereo (byte 4 = channels; stereo interleaved in 0x100-byte blocks): +0x10 a build date, +0x18 16 LE s16 coefficients, +0x60 nibble count, +0x64 sample rate, data from +0x78 in 8-byte frames. `work/wishfinder/sound-samples/dsp2wav.py ARC PREFIX OUTDIR` decodes them.

## Jingles

- `sSoundControl` +0xc8 is `mpResSeJingle`. The pickup jingles are the realtime jingles, one per `arc/sound/rt_jNN.arc` (`sound\rt_j%02d`, built by `0x15339c`): 01 `item_non`, 02 `item_gets`, 03 `item_gets02`, 04 `katamari`, 05 `egg_get`, 06 `egg_lost`, 07 `mix`, 08 `fish_get`, 09 `trophy`, 10 `retire`. Stereo at 44.1 or 48 kHz.
- Only three functions queue a jingle in `sSoundControl`'s request slots (kind byte 2): `0x4eede8(sound, id, arg)` (one caller, shop music id + 11), `0x4eee68` (one caller, fixed id 1) and `0x4eef00(sound, kind)` (pickup kind 0 -> 2 `item_gets`, 1 -> 3 `item_gets02`, 2/3/130/131 -> 4 `katamari`, 4 -> 5 `egg_get`, else nothing).
- `0x4eef00`'s callers (`0x2d55e0`, `0x2d5688`, `0x2d5734`, `0x2d5778`) are the hunter's item-get pose, a switch on player +0x32d8 (0..4), `| 0x80` when player byte +7 is clear. The item is added earlier, through player slot 0x360.
- The gather jingle is not code-driven: a needed gather in a quest called neither `0x4eef00` nor the quest hunter's add-item `0x3015e0`, and no new entry appeared in the request slots at +0xec. It most likely comes from the motion's sound events (data, `sound\call\pl`). The realtime slots at +0x9ec change constantly; their +0xc is a running handle, not a sound number.
