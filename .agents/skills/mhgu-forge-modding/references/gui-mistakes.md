# Native GUI: common mistakes

## Common mistakes

| Mistake | Correct approach |
| --- | --- |
| Taking a pointer field's type from its DTI name | Find a game function that reads it: `sQuest` `mpQuestData` is the `cQuestData` itself, and `getData` on it read quest ID 0 (WishFinder r130). |
| Testing a lookup with an input whose wrong reading looks like a valid one | An in-quest case with a quest that lists nothing passed while the lookup read nothing. Choose inputs where a wrong reading gives a different output. |
| Using Forge `malloc` for game GUI objects | Use the class DTI's MT allocator so the native destructor frees it correctly. |
| Sizing a row's map or cache with fixed numbers | Another plugin may have added children first. Size both from the live tree ([A row another plugin also extends](gui-insertion.md#a-row-another-plugin-also-extends)). |
| Appending a GUI child without growing the object map | The game indexes the map by the tree count and crashes. Grow map and draw cache together. |
| Freeing or zeroing a row's draw block prefix when growing it | Objects animate through `+0x64` pointers into it. Copy the prefix and move those pointers first (see above). |
| Reading tree shape from a `.gui` file's child index | The runtime links (+0x68 child, +0x6c sibling, +0x70 parent) are authoritative. In hud0 `sharp`, the three textures are siblings directly under the controller. |
| Copying another row's or mod's layout (cache size, flag bits, map aliases) and calling it "proven" | Only native code that reads the field for this class proves it. Label everything else as inference in code comments too. |
| Keeping a captured instance after a quest or scene ends | Clear it at the destruction path. An unchanged address does not prove the object is still alive. |
| Assuming how long a HUD object lives | Measure it. The sharpness gauge's row lasts a quest and other objects are unmeasured, so keep a liveness check, drop every captured address when it fails, and redo per-row setup on the next object. The cGUIObjRoot slot 0x04 destructor fired in no saved log, so do not rely on it (`mhgu-understanding` Rules). |
| Using a timer, frame counter or "no sample for N calls" as proof that an object is still alive (or already gone) | Write to or free a game object only while a native lookup made in the same callback finds it, or before a hooked teardown runs. Without that, leave the restore code out (the game's destructor owns what is linked into its tree) and report the missing teardown path. |
| Reparenting nodes with hand-written +0x68/+0x6c/+0x70 links | List every link the walker and the native teardown follow on each moved node and on its old neighbours, and say where each new value comes from. Prefer the native linkers `0xa48460` and `0xa4844c`, and end the old chain: a node reachable twice is freed twice (see above). Prove the tree with a walker port over the post-write state (playbook P2 step 5). |
| Checking a row's liveness only from a callback that row owns | A freed node's handler stops being called, so the check goes silent. Check read-only from a callback that keeps running (the draw walker), and write only where the game hands over a live object. |
| Re-reading the row after insertion with gates written for the tree before it | Each per-frame path after a write must accept the tree your write produced. Fixture it (playbook P2 step 5). |
| Deriving draw geometry from a node rect whose relation to the drawn sprite is unproven, or citing a setter probe as proof of clipping | Label such geometry inference. Shared render state read at an arbitrary moment proves only that the setter ran, not that it was active during the target draw. |
| Leaving out steps of an in-repo precedent (such as the KQM badge's construction) | Compare your code with the precedent field by field. Name every skipped step and the native code that makes it unnecessary (see above). |
| Logging the values you wrote and calling that placement evidence | Read back the game's own output (rect +`0xe0`, matrix +`0x10..+0x4c`, size) at the next callback, after the native layout has run. A constructor default read back proves only that the constructor ran, and a field you wrote reads back whether or not anything consumes it. |
| Writing screen pixels into a node's local position or size | Those fields are local, and later writes to them may be inert. Move geometry with a mask, and treat a node's rect as a layout box, not as its sprite. |
| Interpreting a screenshot | Name each HUD element in the photo and confirm it with the user or a baseline shot of the accepted build (the Dual Blades demon gauge was once misread as the mod's own node for three builds). A user's correction about one element does not extend to others. An artefact that appears or disappears between builds is evidence; never discard it. |

Sources: `mods/wishfinder/DEVELOPMENT.md` and `src/{gui.rs,native.rs,hooks.rs}`; `mods/key-quest-markers/src/{gui.rs,native.rs,offers.rs}`, `mods/key-quest-markers/scripts/gui_layout.py`, `tests/{resource.py,native_adapter.py,arm.py}`, `research/theme-colours.json`, `DEVELOPMENT.md`, `EVIDENCE.json`; `mods/world-sharpness-gauge/src/insert.rs` and its `DEVELOPMENT.md`.  Native addresses in the mask, cache and flag sections were rechecked against the original bytes on 2026-11-01.
