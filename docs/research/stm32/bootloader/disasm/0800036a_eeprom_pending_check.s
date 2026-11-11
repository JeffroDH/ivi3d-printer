0800036a: push     {r4, lr}
0800036c: sub      sp, #0x18
0800036e: movs     r0, #0
08000370: str      r0, [sp, #8]
08000372: str      r0, [sp, #0xc]
08000374: str      r0, [sp, #0x10]
08000376: str      r0, [sp, #0x14]
08000378: movs     r4, #0
0800037a: str      r0, [sp, #4]
0800037c: movs     r2, #0x10
0800037e: add      r1, sp, #8
08000380: movs     r0, #0x20
08000382: bl       #0x80003d8
08000386: movs     r2, #0xe
08000388: add      r1, sp, #8
0800038a: add      r0, sp, #4
0800038c: bl       #0x8005912
08000390: ldrb.w   r0, [sp, #0x16]
08000394: ldrb.w   r1, [sp, #0x17]
08000398: orr.w    r0, r0, r1, lsl #8
0800039c: ldrh.w   r1, [sp, #4]
080003a0: cmp      r0, r1
080003a2: bne      #0x80003aa
080003a4: movs     r0, #1
080003a6: add      sp, #0x18
080003a8: pop      {r4, pc}
080003aa: movs     r0, #0
080003ac: b        #0x80003a6
080003ae: movs     r0, r0
