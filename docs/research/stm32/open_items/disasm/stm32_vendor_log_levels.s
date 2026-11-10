08026114: push     {r2, r3}
08026116: push     {r0, r1, r4, r5, r6, lr}
08026118: ldr      r5, [pc, #0x44]
0802611a: ldr      r6, [pc, #0x48]
0802611c: ldrb     r2, [r5]
0802611e: cmp      r2, r1
08026120: mov      r4, r1
08026122: bls      #0x802612a
08026124: ldrb     r3, [r6]
08026126: cmp      r3, r1
08026128: bhi      #0x8026156
0802612a: add      r3, sp, #0x1c
0802612c: ldr      r2, [sp, #0x18]
0802612e: ldr      r0, [pc, #0x38]
08026130: str      r3, [sp, #4]
08026132: mov.w    r1, #0x100
08026136: bl       #0x80326fc
0802613a: ldrb     r3, [r5]
0802613c: cmp      r3, r4
0802613e: bhi      #0x8026148
08026140: ldr      r1, [pc, #0x24]
08026142: ldr      r0, [pc, #0x28]
08026144: bl       #0x80118be
08026148: ldrb     r3, [r6]
0802614a: cmp      r3, r4
0802614c: bhi      #0x8026156
0802614e: ldr      r1, [pc, #0x18]
08026150: ldr      r0, [pc, #0x1c]
08026152: bl       #0x80118be
08026156: add      sp, #8
08026158: pop.w    {r4, r5, r6, lr}
0802615c: add      sp, #8
0802615e: bx       lr
08026160: lsls     r0, r7, #7
08026162: movs     r0, #0
08026164: lsls     r1, r7, #7
08026166: movs     r0, #0
08026168: str      r5, [r7, #0x28]
0802616a: movs     r0, #0
0802616c: asrs     r4, r3, #4
0802616e: movs     r0, #0
08026170: asrs     r0, r7, #0xd
08026172: movs     r0, #0
08026174: push     {r0, r1, r2, r4, r5, lr}
08026176: mov      r4, r2
08026178: mov      r5, r1
0802617a: cbz      r1, #0x802619e
0802617c: ldr      r3, [pc, #0x30]
0802617e: ldrb     r3, [r3]
08026180: ldr      r2, [pc, #0x30]
08026182: str      r0, [sp, #4]
08026184: movs     r1, #2
08026186: bl       #0x8026114
0802618a: cmp      r4, #6
0802618c: ldr      r0, [sp, #4]
0802618e: bls      #0x80261a2
08026190: ldr      r2, [pc, #0x24]
08026192: movs     r1, #4
08026194: add      sp, #0xc
08026196: pop.w    {r4, r5, lr}
0802619a: b.w      #0x8026114
0802619e: ldr      r3, [pc, #0x1c]
080261a0: b        #0x802617e
080261a2: cbz      r5, #0x80261ac
080261a4: ldr      r3, [pc, #8]
080261a6: strb     r4, [r3]
080261a8: add      sp, #0xc
080261aa: pop      {r4, r5, pc}
080261ac: ldr      r3, [pc, #0xc]
080261ae: b        #0x80261a6
080261b0: lsls     r1, r7, #7
080261b2: movs     r0, #0
080261b4: ldrb     r5, [r1, r4]
080261b6: lsrs     r3, r0, #0x20
080261b8: ldrb     r3, [r4, r4]
080261ba: lsrs     r3, r0, #0x20
080261bc: lsls     r0, r7, #7
080261be: movs     r0, #0
