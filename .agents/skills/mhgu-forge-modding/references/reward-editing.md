# Changing rewards from a plugin

## Once-per-result quantity policy

The implemented player multiplier is 1..5. A single atomic mode word stores force_miraculous bit 0 and multiplier-1 in bits 1..3. Generation scopes latch that word, including nested calls. Builder entry captures all player pointers/counts; return preflights every included page before writing any quantity.

Preflight verifies unchanged metadata, capacity, alignment, writable bounds, disjoint ownership including Palico storage, valid zero/zero empty pairs, signed quantities, and captured preimages. Any failure leaves every included quantity unchanged and defers a deduplicated reason to update-time logging. Success updates amount halfwords only, preserving item IDs, indices, slot counts, RNG and attribution, and reconciles pending snapshots.

A result-object latch records the completed attempt even at 1x or on failure. Repeated builders/settings changes cannot rescale the same result. Destructor `0x384408` clears the owning gameplay context latch before that UI address can be reused. Lost TLS/capture ownership never authorizes retrospective writes. Collection, list refresh, and rendering are not scaling entrypoints.

Collection and appraisal enqueue `0x3c6c6c` read quantities as signed shorts. Reject products above 32767; at 5x the largest valid input is 6553. Appraisal loops once per amount, appending IDs at save-state +0xb08 with count +0xb16, capped at 150 entries. Preserve that cap and document possible truncation. Displayed multiplication alone does not verify inventory or appraisal acceptance.

## Verify without broadening claims

Existing native count fixtures cover 1,092 deterministic cases comparing natural counts/RNG consumption and cheat-equivalent forced behavior. Array/list tests preserve duplicate-ID distinctions, indices, untouched tails, and failure atomicity. Static validation does not substitute for collection/storage/gameplay acceptance.

Manual scenarios include 1x and 2..5x, both Luck modes, guaranteed rewards, subquest/free-hunt/overflow/extra pages, unchanged Palico/pouch/box, Take All/Send to Box/partial stacks/full storage, appraisal quantities, slider edits while results are visible, and consecutive quests/settings persistence. The r23/r24 distribution records preserve their scoped loading/approval evidence; do not mark this entire matrix completed from them.

## Force mode and highlights

The maintained force mode changes only the audited conditional Miraculous checks at `0x3822dc` and `0x4d17f4`. Natural mode calls the original helper with original state. Forced mode supplies the cheat-equivalent result while preserving audited LR/register/flag behavior. Do not globally falsify every skill query or assume all reward paths use Luck.

Luck attribution identifies observed additional slots, not an intrinsic quality of each item. Unknown generation routes publish no attribution. Current highlighting sets each verified extra-luck slot's native background frame white through its vertex-colour setter; the earlier ImGui overlay and downsample experiments are retired.
