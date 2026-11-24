# Which thread runs the GUI

## Threads

Threads (static reading of 1.4.0 main; no run has logged a thread). Chain from the game's frame update to the draw walker, each link read from bytes or a decompile:

1. main+0x3da8fc is `sFestaMain::move`, the frame update.
2. `sFestaMain::move` (main+0x3da8fc) calls field +0x38250's slot 0x1c inline. That field is allocated at 0x44bb18 bytes in `sFestaMain::DTI::newInstance`, the size of `sFestaRender`. Its slot 0x1c main+0x3deb8c branches to main+0xbc2904.
3. main+0xbc2904 calls slot 0x34 of the global at 0x2126f48 inline at main+0xbc2a94 and main+0xbc2c2c, passing its draw context. The same global is read at main+0x3ea0e0 by sFestaUnit's slot 0x34, main+0x3ea0b0.
4. main+0x3ea0b0 loops the unit groups and calls each unit's slot 0x30 directly, no job.
5. uGUI's slot 0x30 main+0x919760 calls its slot 0x58 or 0x5c at main+0x919854. Those end in branches to main+0xa34070 (main+0x919ce0, main+0x91a050).
6. main+0xa34070 calls instance slot 0x3c at main+0xa341c8. cGUIInstAnimation's slot 0x3c is main+0xa39300, whose `bl` at main+0xa39664 is the walker main+0xa494a0.
7. The walker's only other direct branch, main+0xa56a20, is a vtable slot (word at main+0x178fc18) that forwards a node's +0xcc controller to the walker: a nested walk, reached from inside a walk.

So the walker and a mask's enter run inside `sFestaMain::move`.

Other threads:

- sRender's own thread: created in main+0xbbca50, entry main+0xbbd7fc, frame body main+0xbbe9c8, handoff events at +0x1c4 and +0x1e0. Its body issues graphics calls. None of the sUnit slot 0x34 sites is in it.
- Worker queue: main+0xba67b4 enqueues, workers are made in main+0xba45c0. `sFestaMain::move` queues one job per frame at main+0x3dadd4, entry main+0x3daf88: fields +0x382ec, +0x38364, +0x38314, +0x38318. By allocation size those are sPop 232, sOtodokeService 88, sShell 30108 and sUIObject 56 (inference from size). Nothing was seen that waits for this job, so it can outlast the update.
- sUIObject's slot 0x1c main+0x65c108 prunes its list and calls entries' slot 0x04, so it destroys objects on that job. The class list is `cUIO*`; uGUI's parents are uFestaGUI, uGUI, uCoord.
- main+0xba62a8 runs batches and waits for them: synchronous, so it does not extend past its caller.

Not closed:

- 13 more functions call sUnit's slot 0x34 (main+0x8aa280 .. main+0x9ad854), and 10 other slot 0x3c call sites sit in main+0xa3d6d0 .. main+0xa54650. Their callers were not traced to a thread entry.
- Whether a gauge row's owner is a `cUIO*` object on the sUIObject job. The area-change teardown path is still unproven, so a destructor running beside the update is not excluded.
- Confirmation needs a run that records the current thread in the walker and after `sFestaMain::move` returns.
