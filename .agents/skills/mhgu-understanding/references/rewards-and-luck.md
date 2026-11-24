# Reward generation, Luck and result pages

## Native count and item selection

Luck affects expansion of reward slot counts. It does not directly reroll the item table into better items. Native selector main+`0x3822bc` returns threshold 22 normally, 8 Horrible Luck, 16 Bad Luck, 25 Good Luck, 28 Great/Bounty-equivalent Luck, 31 Miraculous Luck. The compared roll is `randU16 & 31`, in 0..31. Expansion succeeds when **roll < threshold**. Larger rolls cause failure; equality also fails.

Main count `0x381fec` retains quest guarantees, RemAddFrameA/B, meal checks 0x10/0x11, an eight-slot cap, and zero-to-one clamp. Secondary count `0x382e1c` starts at two, with six comparisons up to slot eight. Main generation `0x38211c` uses the resulting count and native item selection. Absent tables generate no items. A slot-count counterfactual using observed rolls does not establish which items a rerun would have selected.

Exact instruction sites:

| Site | Instruction / role |
| --- | --- |
| `0x3822dc` | `bl 0xe0da0; mov r5,#31`: conditional Miraculous check |
| `0x4d17f4` | `bl 0x26fe08; mov r5,#1`: second cheat check |
| `0x3820d0` | `and r0,#31; cmp r5,r0`: main comparison |
| `0x3820b4` | `mov r5,r0; cmp r4,#7`: selected threshold and initial main count |
| `0x382edc`, `0x382efc`, `0x382f1c`, `0x382f3c`, `0x382f5c`, `0x382f7c` | `mov r7,#2..7; cmp r6,r0`: the secondary comparisons |
| `0x381fec` | Main count entry: `push {r4,r5,r6,lr}` then a PC-relative literal load (literal at main+`0x382100`), so a trampoline cannot copy it; resume at `0x381ff4` |
| `0x384848` / `0x384408` | Result update / destruction |

## Which rewards a quest guarantees

`getMainRewards` `0x381d30` and `generateRewards` `0x38211c`: a flag-1 or flag-4 frame forces its first entry into the first slot whatever its weight, so a displayed weight is not the chance. Sub `0x382c18` never forces and needs the subquest. Extra `0x38236c` sets slots and a condition by frame flag (meanings marked inference rest on quest names; the writers are unread):

| Flag | Slots | Condition | Meaning |
| --- | --- | --- | --- |
| 1 | forced first | | Guaranteed (first nonzero-weight entry, in rem1 or rem2) |
| 3 | 1 | None | Always rolled; guaranteed when its nonzero-weight entries are one item, item 0 excluded |
| 5 | 3 | `sQuest+0x52` is 0 or 3 | Not repelled |
| 48 | 2 | Same | Not repelled |
| 6..15 | 1 | `+0x98` >= 1..10 | Inference: targets hunted |
| 16..24 | 1 | `+0x99` >= 10..50 by 5 | Inference: small monsters culled |
| 25..35 | 1 | `+0x9a` >= 10..90 | Delivered items (`0x3b3db0` sums share-box counts) |
| 36 / 37 | 1 | `+0x1742` == 0 / == 1 | Inference: arena result |
| 38..47 | 1 | Average of two questPlus percentages >= 10..100, and not repelled | Inference: damage dealt |

`0x3aeda4` sets `+0x52` to 2 when monster HP falls to `mGekitaiHp`, so 1 and 2 mean repelled. Reward file layouts: [Quest files](quest-files.md).

**Chance per draw.** A reward's chance per draw is its weight over the sum of its frame's live
weights (weight above 0; an item 0 row counts, since it rolls nothing). It is not the chance of the reward screen: a frame draws once
per slot it fills (inference from the slot counts above), and the forced first entry ignores its weight.

## Capture attribution by array/index

UI builder `0x3874e0` copies generated four-byte `(u16 item, u16 amount)` entries. Audited copy windows begin `0x3875bc`, `0x3878e0`, `0x387b00`, `0x388084`, targeting known player arrays/indices. Item IDs can repeat with different quantities. Attribution uses observed generation, exact caller/copy destination, snapshots, and index, not a search for the first matching ID.

The four copies, with their end (exclusive), source register and destination:

| Copy | Source | Destination | After |
| --- | --- | --- | --- |
| `0x3875bc..0x387680` | r7 | `*(ui+0x5c)` slots 0..7 | main wrapper `0x381d30` |
| `0x3878e0..0x3879a4` | r7 | the same | main wrapper `0x381d30` |
| `0x387b00..0x387bc4` | r6 | `*(ui+0x5c)+32` slots 8..15 | direct main generation |
| `0x388084..0x388144` | r5 | `*(ui+0x64)+32` slots 8..15 | secondary `0x382e1c` |

State 1's `0x384af0` can grow the main reward array to 16 or 48 entries before its call `0x384fc0` reaches builder `0x3874e0`; copy loops `0x384bf0..0x384c24` and `0x384c7c..0x384cb0` keep indices, then free the old allocation.

Native list copy `0x623c08` copies min(source count, capacity) by index. Items are inline at list +0x60; that field is not an item-array pointer. Flags at +0x120 come from a separate descriptor. Result update `0x384848` observes reward states 2..5 at +0x3c; departure/destruction invalidates provenance. If array growth frees the old allocation, snapshot before original execution and verify the new prefix without rereading freed memory.

## Result page layout

Builder `0x3874e0`, collection `0x388ee8`, and constructor `0x3839bc` establish:

| Page | UI array pointer / count | Capacity | Source / quantity scope |
| --- | --- | --- | --- |
| 0, also arena selectors 4/5 | +0x5c / +0x60 | 48 normal, 16 arena | Main A/B, special, break/capture; player multiplier |
| 1 | +0x64 / +0x68 | 48 | Subquest, free-hunt, bonus, break/capture overflow; player multiplier |
| 2 | +0x6c / +0x70 | 8 | Player extra items copied from result save-state +0xae0; multiplier |
| 3 | +0x74 / +0x78 | 16 or 32 | Palico gathered/stolen items; unchanged |

Companion gathering comes from save-state +0xaf0; stolen items use `0x382ffc`. Companion count +0xb17 controls page 3 row count at UI +0x158, two rows per companion. Pouch/box items already received during a quest are outside these result arrays.
