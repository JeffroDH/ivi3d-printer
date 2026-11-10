0802620c: vldr     s15, [r0, #8]
08026210: vcmp.f32 s15, #0
08026214: vmrs     apsr_nzcv, fpscr
08026218: push     {r4, lr}
0802621a: mov      r4, r0
0802621c: beq      #0x802624c
0802621e: ldrb     r3, [r0]
08026220: cmp      r3, #3
08026222: bne      #0x802623e
08026224: bl       #0x8019368
08026228: vldr     s15, [pc, #0x24]
0802622c: vcmpe.f32 s0, s15
08026230: vmrs     apsr_nzcv, fpscr
08026234: ite      gt
08026236: movgt    r0, #1
08026238: movle    r0, #0
0802623a: bl       #0x8019700
0802623e: ldrb     r0, [r4]
08026240: cmp      r0, #1
08026242: bne      #0x802624c
08026244: pop.w    {r4, lr}
08026248: b.w      #0x8019700
0802624c: pop      {r4, pc}
0802624e: nop      
08026250: movs     r0, r0
08026252: tst      r0, r4
08026254: push     {r4, lr}
08026256: mov      r4, r0
08026258: bl       #0x80190e4
0802625c: ldr      r3, [r4, #0xc]
0802625e: subs     r0, r0, r3
08026260: cmp.w    r0, #0x3e8
08026264: bls      #0x8026272
08026266: mov      r0, r4
08026268: bl       #0x802620c
0802626c: bl       #0x80190e4
08026270: str      r0, [r4, #0xc]
08026272: pop      {r4, pc}
