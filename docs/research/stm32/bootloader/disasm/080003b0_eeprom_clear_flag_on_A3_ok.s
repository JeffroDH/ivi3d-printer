080003b0: push     {r0, r1, r2, r3, r4, lr}
080003b2: ldr      r3, [pc, #0x18] ; [0x080003cc]=0x08006798
080003b4: ldm      r3, {r0, r1, r2, r3}
080003b6: stm.w    sp, {r0, r1, r2, r3}
080003ba: movs     r2, #0x10
080003bc: mov      r1, sp
080003be: movs     r0, #0x20
080003c0: bl       #0x8000456
080003c4: movs     r0, #0
080003c6: add      sp, #0x10
080003c8: pop      {r4, pc}
080003ca: movs     r0, r0
080003cc: str      r0, [r3, #0x78]
080003ce: lsrs     r0, r0, #0x20
