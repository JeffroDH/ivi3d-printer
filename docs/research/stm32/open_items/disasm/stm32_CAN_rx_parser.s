08019390: push     {r4, lr}
08019392: ldr      r1, [pc, #0xe0]
08019394: ldrb     r2, [r1]
08019396: cmp      r2, #0xa7
08019398: mov      r3, r1
0801939a: bhi      #0x80193b2
0801939c: cmp      r2, #0x9f
0801939e: bls      #0x80193b6
080193a0: subs     r2, #0xa0
080193a2: cmp      r2, #7
080193a4: bhi      #0x80193b6
080193a6: tbb      [pc, r2]
080193aa: asrs     r7, r0, #0x10
080193ac: add      r6, r7
080193ae: lsls     r6, r0, #0x18
080193b0: ldrh     r6, [r2, r5]
080193b2: cmp      r2, #0xc0
080193b4: beq      #0x801946e
080193b6: pop      {r4, pc}
080193b8: ldr      r2, [pc, #0xbc]
080193ba: ldrb     r1, [r3, #1]
080193bc: strb     r1, [r2]
080193be: ldrb     r1, [r3, #2]
080193c0: strh     r1, [r2, #2]
080193c2: ldrb     r1, [r3, #3]
080193c4: ldrb     r3, [r3, #4]
080193c6: strb     r3, [r2, #1]
080193c8: ldr      r3, [pc, #0xb0]
080193ca: strh     r1, [r2, #4]
080193cc: movs     r2, #1
080193ce: strb     r2, [r3]
080193d0: b        #0x80193b6
080193d2: ldr      r2, [pc, #0xac]
080193d4: ldr      r0, [r3]
080193d6: ldr      r1, [r3, #4]
080193d8: mov      r4, r2
080193da: stm      r4!, {r0, r1}
080193dc: ldrb     r3, [r2, #1]
080193de: ldr      r1, [pc, #0xa4]
080193e0: ubfx     r0, r3, #4, #1
080193e4: strb     r0, [r1]
080193e6: ldr      r1, [pc, #0xa0]
080193e8: ubfx     r0, r3, #0, #1
080193ec: strb     r0, [r1]
080193ee: ldr      r1, [pc, #0x9c]
080193f0: ubfx     r0, r3, #1, #1
080193f4: strb     r0, [r1]
080193f6: ldr      r1, [pc, #0x98]
080193f8: ubfx     r0, r3, #2, #1
080193fc: strb     r0, [r1]
080193fe: ldr      r1, [pc, #0x94]
08019400: ubfx     r0, r3, #3, #1
08019404: strb     r0, [r1]
08019406: ldr      r1, [pc, #0x90]
08019408: ubfx     r0, r3, #5, #1
0801940c: strb     r0, [r1]
0801940e: ldr      r1, [pc, #0x8c]
08019410: ubfx     r3, r3, #6, #1
08019414: strb     r3, [r1]
08019416: ldr      r3, [pc, #0x88]
08019418: ldr      r1, [r2, #4]
0801941a: str      r1, [r3]
0801941c: ldr      r3, [pc, #0x84]
0801941e: ldrb     r2, [r2, #2]
08019420: strb     r2, [r3]
08019422: ldr      r3, [pc, #0x84]
08019424: b        #0x80193cc
08019426: ldr.w    r2, [r3, #1]
0801942a: ldr      r3, [pc, #0x74]
0801942c: str      r2, [r3]
0801942e: ldr      r3, [pc, #0x7c]
08019430: b        #0x80193cc
08019432: ldrb     r0, [r3, #2]
08019434: ldrb     r1, [r3, #1]
08019436: ldr      r2, [pc, #0x78]
08019438: orr.w    r1, r1, r0, lsl #8
0801943c: strh     r1, [r2]
0801943e: ldrb     r0, [r3, #4]
08019440: ldrb     r1, [r3, #3]
08019442: orr.w    r1, r1, r0, lsl #8
08019446: strh     r1, [r2, #2]
08019448: ldrb     r1, [r3, #6]
0801944a: ldrb     r3, [r3, #5]
0801944c: orr.w    r3, r3, r1, lsl #8
08019450: strh     r3, [r2, #4]
08019452: ldr      r3, [pc, #0x60]
08019454: b        #0x80193cc
08019456: ldrb     r2, [r3, #1]
08019458: ldr      r3, [pc, #0x28]
0801945a: strb     r2, [r3]
0801945c: ldr      r3, [pc, #0x58]
0801945e: b        #0x80193cc
08019460: ldrb     r2, [r3, #1]
08019462: ldrb     r3, [r3, #2]
08019464: orr.w    r3, r3, r2, lsl #8
08019468: ldr      r2, [pc, #0x50]
0801946a: strh     r3, [r2]
0801946c: b        #0x80193b6
0801946e: ldrb     r2, [r1, #1]
08019470: ldr      r3, [pc, #0x10]
08019472: b        #0x80193ce
08019474: asrs     r3, r7, #0xc
08019476: movs     r0, #0
08019478: asrs     r2, r4, #0xc
0801947a: movs     r0, #0
0801947c: asrs     r7, r5, #0xb
0801947e: movs     r0, #0
08019480: asrs     r0, r4, #0xd
08019482: movs     r0, #0
08019484: asrs     r2, r5, #0xd
08019486: movs     r0, #0
08019488: asrs     r0, r4, #0xc
0801948a: movs     r0, #0
0801948c: asrs     r1, r6, #0xc
0801948e: movs     r0, #0
08019490: asrs     r0, r5, #0xc
08019492: movs     r0, #0
08019494: asrs     r2, r7, #0xc
08019496: movs     r0, #0
08019498: asrs     r1, r5, #0xd
0801949a: movs     r0, #0
0801949c: asrs     r4, r6, #0xb
0801949e: movs     r0, #0
080194a0: asrs     r4, r5, #0xc
080194a2: movs     r0, #0
080194a4: asrs     r1, r7, #0xc
080194a6: movs     r0, #0
080194a8: asrs     r0, r5, #0xd
080194aa: movs     r0, #0
080194ac: asrs     r0, r6, #0xc
080194ae: movs     r0, #0
080194b0: asrs     r2, r6, #0xc
080194b2: movs     r0, #0
080194b4: asrs     r0, r7, #0xc
080194b6: movs     r0, #0
080194b8: asrs     r3, r5, #0xd
080194ba: movs     r0, #0
080194bc: asrs     r2, r6, #0xb
080194be: movs     r0, #0
