# Cameras and projection

## Camera snapshot and projection

Within viewport scope, +0x24 points to the camera: `uQuestCamera` (vtable main+`0x1730d0c`) in quests, `uVillageCamera` (main+`0x1730e10`) in the village (saved DTI; both `uFestaCamera`, as is `uSubSceneCamera` main+`0x1730d90`). Check mappings/class and copy view/projection arrays and rectangle while native arguments are alive. Never retain matrix pointers for the render callback. Record the camera/viewport and actual display dimensions when diagnosing resolution-dependent placement.

The perspective builder main+`0x7c617c` stores `cot(fov/2)/aspect` at `[0]` and `cot(fov/2)` at `[5]`, so `[5]/[0]` is the picture's shape; it leaves m[8]/m[9] at 0 (a host upscaler may write jitter there).

Native matrices use row-vector conventions. The current adapter constructs a row-major world-to-clip matrix suitable for column-vector projection:

```text
world_to_clip[row*4+col] = sum(view[col*4+k] * projection[k*4+row], k=0,1,2,3)
clip = world_to_clip * [world_x, world_y, world_z, 1]
```

Require finite values, positive display dimensions, and w>0.00001. Native clip bounds are x/y in[-w, w], z in[0, w]. Map pixels as `x0+(x/w+1)*width/2`, `y0+(1-y/w)*height/2`; screen Y points down.

The game can present a smaller crop of an unchanged swapchain (handheld mode). sFestaRender (exact-type ID `0x300a6cd8`) keeps the applied size in its inherited mDisplaySize at +0xb8/+0xbc; +0xb0/+0xb4 are requested values that may still be pending. Native main+`0xbc0874` calls SetCrop main+`0x86a24c` and then updates that pair.
