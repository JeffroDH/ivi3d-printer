080256a4: push     {r3, r4, r5, lr}
080256a6: movs     r0, #0x50
080256a8: bl       #0x801c7c4
080256ac: cbnz     r0, #0x80256c0
080256ae: movs     r1, #1
080256b0: bl       #0x802e3e8
080256b4: movs     r1, #1
080256b6: pop.w    {r3, r4, r5, lr}
080256ba: mov      r0, r1
080256bc: b.w      #0x802e3e8
080256c0: movs     r0, #0x50
080256c2: bl       #0x801c840
080256c6: cbnz     r0, #0x80256f0
080256c8: movs     r4, #0
080256ca: movs     r0, #0x41
080256cc: bl       #0x801c7c4
080256d0: cbz      r0, #0x802570c
080256d2: ldr      r3, [pc, #0x3c]
080256d4: ldrb     r5, [r3]
080256d6: movs     r0, #0x53
080256d8: bl       #0x801c840
080256dc: cbz      r0, #0x80256e4
080256de: bl       #0x801c89c
080256e2: uxth     r5, r0
080256e4: mov      r1, r5
080256e6: mov      r0, r4
080256e8: pop.w    {r3, r4, r5, lr}
080256ec: b.w      #0x802e3e8
080256f0: bl       #0x801c89c
080256f4: cmp      r0, #0
080256f6: blt      #0x80256c8
080256f8: bl       #0x801c89c
080256fc: cmp      r0, #0xff
080256fe: bgt      #0x802570a
08025700: bl       #0x801c89c
08025704: uxtb     r4, r0
08025706: cmp      r4, #1
08025708: bls      #0x80256ca
0802570a: pop      {r3, r4, r5, pc}
0802570c: movs     r5, #0xff
0802570e: b        #0x80256d6
08025710: ldr      r0, [r5, #0x4c]
08025712: movs     r0, #0
08025714: push     {r3, lr}
08025716: movs     r1, #0
08025718: mov      r0, r1
0802571a: bl       #0x802e3e8
0802571e: pop.w    {r3, lr}
08025722: movs     r1, #0
08025724: movs     r0, #1
08025726: b.w      #0x802e3e8
0802572a: movs     r0, r0
0802572c: push     {r4, lr}
0802572e: ldr      r3, [pc, #0x3c]
