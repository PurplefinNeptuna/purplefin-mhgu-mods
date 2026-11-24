# Game allocators

Finding: the game keeps 64 `MtAllocator` pointers in a table, and a class instance is allocated from the row its DTI names. An allocator with no room returns NULL and callers do not check. Where: table at main+`0x18a62e8` (GOT slot `0x183944c`); `MtDti::getAllocator` main+`0x7aa47c` returns `table[(word at dti+0x18 >> 23) & 0x3f]`.

Type/units: `MtAllocator` u32 byte counts `mUsedSize` +0x04, `mMaxUsedSize` +0x08, `mTotalSize` +0x0c; name at +0x10, 32 bytes ending in a NUL.

Evidence: property registration main+`0x7aab08` stores each name string with `object + 12`, `+ 4` and `+ 8` (strings `mTotalSize` `0x156d648`, `mUsedSize` `0x156d653`, `mMaxUsedSize` `0x156d65d`); constructor main+`0x7aa878` formats the name into +0x10 and zeroes the three counters. Status: verified against the original NSO.

That `mUsedSize` moves on every allocation is inference from its name (the alloc bodies are unread); a run that shows it changing confirms it.

Finding: a full allocator crashes at the next unchecked use.

`cUIOEnlargeMap` (the quest map's UI object, DTI at main+`0x189ec78`, 360 bytes) is created by main+`0x61bea8`, which calls allocator slot 0x20 with `(360, 16, the word at dti+0x1c)` and passes the result to constructor main+`0x61bee0`. main+`0x61d6f8` stores the new object at +0x5c and calls its vtable slot 0x1c at main+`0x61d75c` with no NULL test.

On MHGURecomp reads of the null page give 0, so the call goes to address 0: `FATAL: no function at 0 (lr=81d760 nnMain+475478)` (Recomp loads main at `0x200000`). Status: the code path is verified in bytes. That the allocator was full in the recorded crash is inference from the NULL result; the heap table in the log before such a crash confirms or refutes it.
