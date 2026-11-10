0801a748: push     {r4, lr}
0801a74a: ldr      r3, [pc, #0x58]
0801a74c: ldr      r0, [pc, #0x58]
0801a74e: ldrb     r2, [r3]
0801a750: ldr      r3, [pc, #0x58]
0801a752: ldrsh.w  r3, [r3, r2, lsl #1]
0801a756: ldr      r2, [pc, #0x58]
0801a758: cmp      r3, #0
0801a75a: mov.w    r1, #2
0801a75e: ldr      r3, [pc, #0x54]
0801a760: it       ne
0801a762: movne    r3, r2
0801a764: ldr      r2, [pc, #0x50]
0801a766: ite      ne
0801a768: movne    r4, #1
0801a76a: moveq    r4, #2
0801a76c: bl       #0x8026114
0801a770: ldr      r2, [pc, #0x48]
0801a772: ldr      r0, [pc, #0x34]
0801a774: movs     r1, #2
0801a776: bl       #0x8026114
0801a77a: ldr      r0, [pc, #0x44]
0801a77c: mov      r1, r4
0801a77e: bl       #0x802665c
0801a782: mov      r3, r0
0801a784: cbnz     r0, #0x801a794
0801a786: pop.w    {r4, lr}
0801a78a: ldr      r2, [pc, #0x38]
0801a78c: ldr      r0, [pc, #0x18]
0801a78e: movs     r1, #2
0801a790: b.w      #0x8026114
0801a794: pop.w    {r4, lr}
0801a798: ldr      r2, [pc, #0x2c]
0801a79a: ldr      r0, [pc, #0xc]
0801a79c: movs     r1, #3
0801a79e: b.w      #0x8026114
0801a7a2: nop      
0801a7a4: str      r5, [r2, #0x1c]
0801a7a6: movs     r0, #0
0801a7a8: str      r5, [r7, #0x38]
0801a7aa: movs     r0, #0
0801a7ac: str      r0, [r0, #0x1c]
0801a7ae: movs     r0, #0
0801a7b0: blxns    r4
0801a7b2: lsrs     r3, r0, #0x20
0801a7b4: ldrb     r4, [r0, r2]
0801a7b6: lsrs     r3, r0, #0x20
0801a7b8: blxns    r4
0801a7ba: lsrs     r3, r0, #0x20
