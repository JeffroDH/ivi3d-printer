080253ac: push     {r3, r4, r5, r6, r7, lr}
080253ae: bl       #0x8024f54
080253b2: cmp      r0, #0
080253b4: bne      #0x802541a
080253b6: bl       #0x8024fbc
080253ba: cbnz     r0, #0x802541a
080253bc: ldr      r5, [pc, #0x70]
080253be: ldrb     r3, [r5]
080253c0: cbz      r3, #0x802541a
080253c2: bl       #0x80238d0
080253c6: ldrb     r1, [r5]
080253c8: ldr      r6, [pc, #0x68]
080253ca: cmp      r1, #3
080253cc: bhi      #0x8025402
080253ce: ldrb     r2, [r6]
080253d0: ldr      r3, [pc, #0x64]
080253d2: ldr      r4, [pc, #0x68]
080253d4: ldrsb.w  r3, [r3, r2, lsl #1]
080253d8: ldrsb.w  r7, [r4]
080253dc: strb     r3, [r4]
080253de: cbz      r3, #0x8025400
080253e0: cmp      r3, #0x7f
080253e2: beq      #0x8025400
080253e4: ldr      r0, [pc, #0x58]
080253e6: rsb.w    r1, r1, #7
080253ea: bl       #0x801af4c
080253ee: ldrsb.w  r3, [r4]
080253f2: cbz      r3, #0x802541c
080253f4: cmp      r3, #0x7f
080253f6: beq      #0x802541c
080253f8: ldr      r0, [pc, #0x48]
080253fa: movs     r1, #0xa
080253fc: bl       #0x8010e30
08025400: strb     r7, [r4]
08025402: cpsid    i
08025404: ldrb     r3, [r5]
08025406: subs     r3, #1
08025408: strb     r3, [r5]
0802540a: ldrb     r3, [r6]
0802540c: adds     r3, #1
0802540e: uxtb     r3, r3
08025410: cmp      r3, #5
08025412: it       hi
08025414: movhi    r3, #0
08025416: strb     r3, [r6]
08025418: cpsie    i
0802541a: pop      {r3, r4, r5, r6, r7, pc}
0802541c: ldr      r0, [pc, #0x28]
0802541e: movs     r1, #0xa
08025420: bl       #0x8011bbc
08025424: ldrsb.w  r3, [r4]
08025428: cmp      r3, #0
0802542a: beq      #0x8025400
0802542c: b        #0x80253f8
0802542e: nop      
08025430: str      r4, [r2, #0x1c]
08025432: movs     r0, #0
08025434: str      r5, [r2, #0x1c]
08025436: movs     r0, #0
08025438: str      r0, [r0, #0x1c]
0802543a: movs     r0, #0
0802543c: ldrsb    r1, [r3, r5]
0802543e: movs     r0, #0
08025440: ldrh     r1, [r3, r7]
08025442: lsrs     r3, r0, #0x20
08025444: asrs     r0, r7, #0xd
08025446: movs     r0, #0
08025448: asrs     r4, r3, #4
0802544a: movs     r0, #0
