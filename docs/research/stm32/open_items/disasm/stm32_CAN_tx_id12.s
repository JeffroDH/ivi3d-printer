080192f4: push     {r4, r5, lr}
080192f6: sub      sp, #0x2c
080192f8: movs     r3, #1
080192fa: str      r3, [sp, #0xc]
080192fc: ldr      r3, [pc, #0x48]
080192fe: ldrb     r3, [r3]
08019300: mov      r2, r0
08019302: movs     r0, #0
08019304: cbz      r3, #0x8019344
08019306: movs     r3, #0x12
08019308: strd     r3, r3, [sp, #0x10]
0801930c: strd     r0, r0, [sp, #0x18]
08019310: ldr      r5, [pc, #0x38]
08019312: str      r1, [sp, #0x20]
08019314: movw     r4, #0x1f5
08019318: mov      r0, r5
0801931a: str      r2, [sp, #4]
0801931c: bl       #0x8012774
08019320: ldr      r2, [sp, #4]
08019322: cbnz     r0, #0x801932e
08019324: subs     r4, #1
08019326: bne      #0x8019318
08019328: mov.w    r0, #-1
0801932c: b        #0x8019340
0801932e: ldr      r0, [pc, #0x1c]
08019330: add      r3, sp, #0xc
08019332: add      r1, sp, #0x10
08019334: bl       #0x80126d4
08019338: subs     r0, #0
0801933a: it       ne
0801933c: movne    r0, #1
0801933e: rsbs     r0, r0, #0
08019340: add      sp, #0x2c
08019342: pop      {r4, r5, pc}
08019344: mov      r0, r3
08019346: b        #0x8019340
08019348: lsls     r4, r0, #7
0801934a: movs     r0, #0
0801934c: asrs     r0, r7, #0xb
0801934e: movs     r0, #0
