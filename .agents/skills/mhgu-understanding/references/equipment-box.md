# Equipment box and equipped gear

MHGU 1.4.0. Each fact names its source; "inference" marks what the bytes have not shown.

## Equipment box

Singleton `sEquipBox`, class size 261108: 2000 records of 44 bytes from +0x1c, then 1000 more from +0x157dc, both walked by the save loader `main+0x14b0b0`. Read from +0x20 of the class, a slot holds: type = bits 0..4 and level bits = bits 5..9 of the u16 at slot +0, number = u16 at +2.

The DTI class `cFestaEquip` is 44 bytes. The game's decoder `FUN_00b0803c` reads the type from the u16 at **+4** and the number from **+6**. Its bytes at `main+0x13f03c`: `ldrh r2, [r1, #4]`, `and r3, r2, #31`, `sub r2, r3, #1`, `cmp r2, #23`, `movhi r0, #0`, then `ldrh r2, [r1, #6]`, `b main+0x13c208`. So types **1..23** are valid, 0 is empty, and the data getter is `main+0x13c208(type, number)`.

The smithy writes the level into bits 5..9 of that u16 (`and r1, r1, r2` with `0xfc1f`, `orr r1, r1, r2, lsl #5` at `main+0x6f9ef8`; `bfi r0, r1, #0, #5` at `main+0x7008e4`).

**The level bits count from 0: they hold the shown level minus one.** `main+0x6f9f00` loads the row byte at window `+0x28dd` (row `+9`), and `main+0x6f9f08` shifts it straight into the bits. The tester's save (`system`, read-only, 44-byte records at 0x192fd2..0x1931ee) agrees. The six weapons they listed at shown levels 5, 6, 5, 3, 4 and 2 hold 4, 5, 4, 2, 3 and 1.

So a level-1 weapon holds 0 with a non-zero type, and the row byte counts from 0 too. Saved upgrade keys hold 1 and 6 where the matching process rows are levels 2 and 7 (Sage Rod, General's Bayonet). A third saved key, Full Bolt Chamber, matches no row of its table. RomFS `mLevel`, `deriveLv` and the player's display count from 1.

`cFestaEquip::reset` (`main+0xdac14`) and `::assign` (`main+0xdadf0`) keep bit 15. `::assign` writes type bits 0..4 with `bfi r3, r2, #0, #5`, and level bits 5..9 with `lsr r2, r2, #5` + `bfi r3, r2, #5, #5`. Its `movw r2, #0x83ff` keeps bit 15 of the destination. It then copies `+6`, `+8`, `+10`, `+12`, `+14` and 24 bytes from `+16`.

The array base is **+0x1c**, from the slot getter `main+0x143894(box, kind, index)`:

- It returns 0 when the index is `0xffff` (`movw r0, #0xffff; cmp r5, r0`).
- It checks capacity from the session flags (`ldr r2, [r0, #0x958]` bits 0x15 and 0x16). Kind 0 allows `1000 + 200 × flags + 200 × main+0x525878()`, kind 1 `300 + 200 × flags + 100 × main+0x525878()`.
- Kind 0 then computes `mov r0, #44; mla r0, r5, r0, r8; add r4, r0, #28` (`main+0x14391c`) → `box + 0x1c + index*44`.
- Kind 1 computes `add r0, #988; add r4, r0, #87040` (`main+0x143930`) → `box + 0x157dc + index*44`.

The save loader `main+0x14b0b0` (read, via `main+0x3df2a8` → the memcpy `main+0x13efe30`) and the writer `main+0x14b1c4` (via `main+0x3df378`) touch 2000 records at the first base and 1000 at the second. At the first base they move u16 `+0x20`, u16 `+0x22`, u16 `+0x24`, 6 bytes `+0x26` and 24 bytes `+0x2c`, plus `bl main+0xddd48(box + 0x1c + i*44)`. So the `+0x20` reading and the decoder's `+4`/`+6` are one record (`+0x20` = base + 4).

It also reads a 5440-byte blob at `+254028` and a 1632-byte blob at `+259468` (8 bytes before the class end); the 122,000 bytes between the second array's end (`+132028`) and `+254028` have no reader in those two functions.

The instance slots are all read as `ldr rX, [pc, #imm]` then `ldr rY, [pc, rX]`, whose pc is the second load's address + 8:

| Object | Address | Load → literal |
| --- | --- | --- |
| Box save loader's object | `main+0x1839394` | `main+0x3e77f0` → literal `main+0x3e7944` = `0x1451b94` |
| Equip code's box object (the same) | `main+0x1839394` | `main+0x2633bc` → literal `main+0x2634c8` = `0x15d5fbc` |
| Getter's session object | `main+0x1838d88` | `main+0x1438b4` → literal `main+0x143948` = `0x16f54c4` |
| Hunter status object | `main+0x1838d80` | `main+0x3e782c` → literal `main+0x3e7950` = `0x1451544` |
| Param loader's object | `main+0x1838bbc` | `main+0x3e7840` → literal `main+0x3e7954` = `0x145136c` |

Weapons are types 7..21 except 12: type = weapon table + 7, and there is no table 05. Box armor is types 1..5, part + 1 in head, chest, arms, waist, legs order (`cArmor00Base`..`cArmor04Base` return 1..5 from vtable +0x18), number = armor series. Types 6, 22 and 23 are unnamed, and game code gates the weapon path on them: `main+0x26ee70` `ldrh r0, [r1, #4]; and r0, #31; sub r0, #7; cmp r0, #14; bhi` rejects anything outside 7..21.

**The equipped gear is one box index plus one copied `cFestaEquip` per slot, and the weapon is slot 0.** The type→slot table `main+0xdae68` (`ldr r0, [r1, r0, lsl #2]`, data at `main+0x159fd28`) maps a record's type bits to a slot. The table's words: `0 → 255`, `1..5 → 1..5`, `6 → 6`, `7..22 → 0`, `23 → 1`, `24 → 2`.

The param loader writes types 22, 23 and 24 into entries 0, 1 and 2 when their index is `0xffff` (`main+0x263424`..`main+0x263434`). So those three types are what an empty weapon, head and chest slot hold. What they draw as is not read.

The live gear lives in `nPlayer::cPlayerParam` (1376 bytes). `uPlayerBase + 0x13c4` holds a **pointer** to it (`mpPlParam`).

- The factory `main+0x275d44` computes `base + 0x5bdc + player*1376` with `mov r0, #1376; mla r0, r6, r0, r9` plus `movw r1, #0x5bdc`.
- It stores the pointer at `main+0x275d6c` (again at `main+0x275e1c`), and `main+0x275d78` loads it back before using it. The constructor zeroes the slot at `main+0x27a3f8`.
- The 7 indices are the u16s at `param + 8 + slot*2` (`0xffff` = empty), and the entries are at `param + 0x18 + slot*44`.
- The accessors are `main+0xe100c` / `main+0xe1018` (index) and `main+0xdf814` / `main+0xe0d90` (`mov r2, #44; mla r0, r1, r2, r0; add r0, r0, #20`).

Writer: the equip action `main+0x26eaa8(param, boxIndex, flag)` resolves the box record with `main+0x143894`. It uses kind 1 only when the byte at `param+0x4d4` is 15, otherwise kind 0. `main+0x26f024(param, slot, record, index)` stores the record with `bl main+0xdadf0` and the index with `bl main+0xe1018`. It then recomputes derived state (`main+0x26fa30`, `main+0x26fb00`, `main+0xdee34`, `main+0xe1bbc`, `main+0xe1e7c`, `main+0xe1eec`, `main+0xe79a0`, `main+0xe1fe4`).

Reader: `uPlayerBase::calculateSharpnessType` `main+0x29cdfc` takes entry 0 (`mov r1, #0; bl main+0xdf814`), calls the weapon data getter `main+0x13f03c` and puts bits 5..9 of its `+4` u16 (`ldrh r1, [r6, #4]; ubfx r1, r1, #5, #5`) into that record's vtable `+0xd8`.

The saved hunter status holds the same 7 slots at `status + 0x84` (indices) and `status + 0x94` (entries), resolved with kind 0 by the loader `main+0x2755f0` (`main+0x275670 mov r1, #0; bl main+0x143894`).

**`param + 0x4d4` is the equipped weapon's category: the equipped record's type minus 7.** The store follows the equip: `main+0x26ea70 mov r0, r9; bl main+0xdaea4; main+0x26ea78 cmp r0, #255; main+0x26ea7c strbne r0, [r4, #0x4d4]`. Here `r9` is the record's type bits (`main+0x26e9fc ldrh r0, [r5, #4]; main+0x26ea00 and r0, r0, #31`). `main+0xdaea4` indexes the words at `main+0x159fdcc`: types 0..6 and 23, 24 → 255 (leave the byte), types 7..22 → 0..15. So 15 is type 22's category.

The same byte picks the box kind (the equip action's `cmp r0, #15`) and the player class. `main+0x275afc` (`ldrb r0, [r8, #0x4d4]; cmp r0, #15; bhi main+0x275db4`) jumps 16 ways over the table at `main+0x275b18`. Entry 5 exits: that is the missing weapon table 05. Entry 15 goes to `main+0x276028 mov r0, #13312; bl main+0x2b6894`, where entry 0 goes to `main+0x275b58 mov r0, #13120`.

The factory's second test, `main+0x275d90 ldrb r0, [r8, #0x4d4]; cmp r0, #15`, re-equips 3 entries for 15 (`main+0x276610`: slots 0, 1, 2) and all 7 otherwise (`main+0x276478`).

Type 22 is not a weapon to `main+0x26ee70` (7..21), and it maps to gear slot 0 (`main+0x159fd28`). The equipment data getter `main+0x13c208` sends it to the container at `+0x1d4` (`main+0x13c320`), and types 23, 24 to the one at `+0x1d0` (`main+0x13c2a0`). Type 12 has no case: its table entry jumps to `main+0x13c32c`.

That category 15 is the Prowler's (Otomo, equip type 22) is **inference**: the RomFS pairs `otWeaponData.owp` + `otWeaponCreate.oec` and `otArmorData.oar` + `otArmorCreate.oec`, DTI `uOtomo` and `uOtomoLobby`, and the weapon ID list in [Input and actions](input-and-actions.md#find-the-local-player-and-weapon). No byte names that container.

The 12 bytes `+0x4d4..+0x4df` match, by count and width, DTI `mCharParam[i]` of another class. That class is `nFestaNetwork::netPlData`, with 12 `u8` properties at its `+0x4dc..+0x4e7`; `nPlayer::cPlayerParam` lists none. So that name is inference. `mStyle` (Ghidra type, `+0x4d9`) is the sixth of them. `main+0x26e618`..`main+0x26e674` copy them between params bytewise. The hunter status save carries them at `status + 1360` = `(status + 0x7c) + 0x4d4`, beside those kind-0 indices (`add r1, r10, #1360; mov r2, #12` at `main+0x275730`).

The param loader `main+0x263368` always uses kind 1. Its one caller `main+0x2639ac` loads 84 params at `object + 0x113938 + i*1376` (`main+0x263ba4`..`main+0x263bc4`, `add r6, r6, #1376; cmp r4, #84`). The default-init loop `main+0x2575f0` runs the same 84 × 1376 over `object + 0x13938` and stores 15 in each at `main+0x25a224`.

A hunter's param carries a byte of 0..14 and kind-0 indices, while a param with 15 indexes the 1000-record array. The saved status pairs the byte and the indices in one block, and the smithy equips that `+0x7c` block. The path: `main+0x709954`'s slot `main+0x1838d80` → `main+0x709960 bl main+0x277454` = `add r0, r0, #124` → `main+0x709974 bl main+0x26eaa8`.

The entry is a copy of the box record at that index, so the equipped weapon is also a record in the array the byte's kind selects. That the box keeps the record after equipping is inference: nothing read clears or moves it, and no code that removes a box record was read. Availability helpers that take a `cFestaEquip*`: `main+0xdb5c4` (count) and `main+0x54ff2c` (pouch + box).
