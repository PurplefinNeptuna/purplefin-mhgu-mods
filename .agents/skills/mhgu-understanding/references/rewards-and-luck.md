# Reward generation, Luck, and result pages

## Native count and item selection

Luck affects expansion of reward slot counts. It does not directly reroll the item table into better items. Native selector main+`0x3822bc` returns threshold 22 normally, 8 Horrible Luck, 16 Bad Luck, 25 Good Luck, 28 Great/Bounty-equivalent Luck, 31 Miraculous Luck. The compared roll is `randU16 & 31`, in 0..31. Expansion succeeds when **roll < threshold**. Larger rolls cause failure; equality also fails.

Main count `0x381fec` retains quest guarantees, RemAddFrameA/B, meal checks 0x10/0x11, an eight-slot cap, and zero-to-one clamp. Secondary count `0x382e1c` starts at two, with six comparisons up to slot eight. Main generation `0x38211c` uses the resulting count and native item selection. Absent tables generate no items. A slot-count counterfactual using observed rolls does not establish which items a rerun would have selected.

The maintained force mode changes only the audited conditional Miraculous checks at `0x3822dc` and `0x4d17f4`. Natural mode calls the original helper with original state. Forced mode supplies the cheat-equivalent result while preserving audited LR/register/flag behavior. Do not globally falsify every skill query or assume all reward paths use Luck.

## Capture attribution by array/index

UI builder `0x3874e0` copies generated four-byte `(u16 item, u16 amount)` entries. Audited copy windows begin `0x3875bc`, `0x3878e0`, `0x387b00`, `0x388084`, targeting known player arrays/indices. Item IDs can repeat with different quantities. Attribution uses observed generation, exact caller/copy destination, snapshots, and index, not a search for the first matching ID.

Native list copy `0x623c08` copies min(source count, capacity) by index. Items are inline at list +0x60; that field is not an item-array pointer. Flags at +0x120 come from a separate descriptor. Result update `0x384848` observes reward states 2..5 at +0x3c; departure/destruction invalidates provenance. If array growth frees the old allocation, snapshot before original execution and verify the new prefix without rereading freed memory.

Luck attribution identifies observed additional slots, not an intrinsic quality of each item. Unknown generation routes publish no attribution. Current highlighting uses the independent Forge overlay and guarded native slot/frame geometry, replacing retired downsample-transfer experiments.

## Result page layout

Builder `0x3874e0`, collection `0x388ee8`, and constructor `0x3839bc` establish:

| Page | UI array pointer / count | Capacity | Source / quantity scope |
| --- | --- | --- | --- |
| 0, also arena selectors 4/5 | +0x5c / +0x60 | 48 normal, 16 arena | Main A/B, special, break/capture; player multiplier |
| 1 | +0x64 / +0x68 | 48 | Subquest, free-hunt, bonus, break/capture overflow; player multiplier |
| 2 | +0x6c / +0x70 | 8 | Player extra items copied from result save-state +0xae0; multiplier |
| 3 | +0x74 / +0x78 | 16 or 32 | Palico gathered/stolen items; unchanged |

Companion gathering comes from save-state +0xaf0; stolen items use `0x382ffc`. Companion count +0xb17 controls page 3 row count at UI +0x158, two rows per companion. Pouch/box items already received during a quest are outside these result arrays.

## Once-per-result quantity policy

The implemented player multiplier is 1..5. A single atomic mode word stores force_miraculous bit 0 and multiplier-1 in bits 1..3. Generation scopes latch that word, including nested calls. Builder entry captures all player pointers/counts; return preflights every included page before writing any quantity.

Preflight verifies unchanged metadata, capacity, alignment, writable bounds, disjoint ownership including Palico storage, valid zero/zero empty pairs, signed quantities, and captured preimages. Any failure leaves every included quantity unchanged and defers a deduplicated reason to update-time logging. Success updates amount halfwords only, preserving item IDs, indices, slot counts, RNG and attribution, and reconciles pending snapshots.

A result-object latch records the completed attempt even at 1x or on failure. Repeated builders/settings changes cannot rescale the same result. Destructor `0x384408` clears the owning gameplay context latch before that UI address can be reused. Lost TLS/capture ownership never authorizes retrospective writes. Collection, list refresh, and rendering are not scaling entrypoints.

Collection and appraisal enqueue `0x3c6c6c` read quantities as signed shorts. Reject products above 32767; at 5x the largest valid input is 6553. Appraisal loops once per amount, appending IDs at save-state +0xb08 with count +0xb16, capped at 150 entries. Preserve that cap and document possible truncation. Displayed multiplication alone does not verify inventory or appraisal acceptance.

## Verify without broadening claims

Existing native count fixtures cover 1,092 deterministic cases comparing natural counts/RNG consumption and cheat-equivalent forced behavior. Array/list tests preserve duplicate-ID distinctions, indices, untouched tails, and failure atomicity. Static validation does not substitute for collection/storage/gameplay acceptance.

Manual scenarios include 1x and 2..5x, both Luck modes, guaranteed rewards, subquest/free-hunt/overflow/extra pages, unchanged Palico/pouch/box, Take All/Send to Box/partial stacks/full storage, appraisal quantities, slider edits while results are visible, and consecutive quests/settings persistence. The r23/r24 distribution records preserve their scoped loading/approval evidence; do not mark this entire matrix completed from them.

Sources: `mods/please-do-better/DEVELOPMENT.md` count, copy, layout and reward-page sections; `src/{attribution.h,quantity.h,mode.h,runtime.cpp,gateway.S}`, native tests, `research/{patch-sites.json,highlight-fixtures.json}`, `EVIDENCE.json`; original main and retained reward-page receipts when available.
