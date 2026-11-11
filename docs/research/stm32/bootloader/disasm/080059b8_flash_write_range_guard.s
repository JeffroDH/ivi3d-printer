080059b8: push.w   {r4, r5, r6, r7, r8, sb, sl, lr}
080059bc: mov      r4, r0
080059be: mov      r7, r1
080059c0: mov      r6, r2
080059c2: mov      r5, r4
080059c4: mov.w    sb, #0
080059c8: mov      r8, sb
080059ca: add.w    sl, r4, r6
080059ce: ldr      r0, [pc, #0x6c] ; [0x08005a3c]=0x08010000
080059d0: cmp      r4, r0
080059d2: blo      #0x80059da
080059d4: ldr      r0, [pc, #0x68] ; [0x08005a40]=0x0807ffff
080059d6: cmp      r4, r0
080059d8: blo      #0x80059e2
080059da: mov.w    r0, #-1
080059de: pop.w    {r4, r5, r6, r7, r8, sb, sl, pc}
080059e2: cbz      r7, #0x80059ec
080059e4: cbz      r6, #0x80059ec
080059e6: and      r0, r6, #3
080059ea: cbz      r0, #0x80059f2
080059ec: mov.w    r0, #-1
080059f0: b        #0x80059de
080059f2: ldr      r0, [pc, #0x50] ; [0x08005a44]=0x2000000c
080059f4: ldr      r0, [r0]
080059f6: adds     r0, r0, #1
080059f8: ldr      r1, [pc, #0x48] ; [0x08005a44]=0x2000000c
080059fa: str      r0, [r1]
080059fc: mov      r0, r1
080059fe: ldr      r0, [r0]
08005a00: cmp      r0, #1
08005a02: ble      #0x8005a0c
08005a04: mov      r0, r1
08005a06: ldr      r0, [r0]
08005a08: adds     r0, r0, #1
08005a0a: str      r0, [r1]
08005a0c: b        #0x8005a32
08005a0e: add.w    r0, r7, r8
08005a12: ldr.w    sb, [r0]
08005a16: mov      r2, sb
08005a18: movs     r3, #0
08005a1a: mov      r1, r5
08005a1c: movs     r0, #2
08005a1e: bl       #0x8000b04
08005a22: cbnz     r0, #0x8005a2c
08005a24: adds     r5, r5, #4
08005a26: add.w    r8, r8, #4
08005a2a: b        #0x8005a32
08005a2c: mov.w    r0, #-1
08005a30: b        #0x80059de
08005a32: cmp      r5, sl
08005a34: blo      #0x8005a0e
08005a36: movs     r0, #0
08005a38: b        #0x80059de
08005a3a: movs     r0, r0
08005a3c: movs     r0, r0
08005a3e: lsrs     r1, r0, #0x20
08005a40: vtbl.8   d16, {d15}, d7
08005a44: movs     r4, r1
08005a46: movs     r0, #0
