08026274: push     {r0, r1, r4, lr}
08026276: mov      r4, r0
08026278: mov      r0, sp
0802627a: bl       #0x8019508
0802627e: ldrb.w   r3, [sp]
08026282: cmp      r3, #8
08026284: bhi.w    #0x80263c6
08026288: tbb      [pc, r3]
0802628c: lsrs     r5, r0, #0xc
0802628e: strh     r6, [r3, #0x2a]
08026290: ldrh     r1, [r1, #0x2c]
08026292: str      r5, [sp, #0x244]
08026294: lsls     r1, r3, #2
08026296: ldr      r0, [pc, #0x134]
08026298: add      sp, #8
0802629a: pop.w    {r4, lr}
0802629e: b.w      #0x801aeac
080262a2: movs     r3, #1
080262a4: strb     r3, [r4]
080262a6: ldr      r4, [pc, #0x128]
080262a8: ldr      r0, [pc, #0x128]
080262aa: bl       #0x801aeac
080262ae: ldrsb.w  r3, [r4]
080262b2: cbz      r3, #0x8026302
080262b4: cmp      r3, #0x7f
080262b6: beq      #0x8026302
080262b8: ldr      r1, [pc, #0x11c]
080262ba: ldr      r0, [pc, #0x120]
080262bc: bl       #0x80118be
080262c0: ldrsb.w  r3, [r4]
080262c4: cbz      r3, #0x8026314
080262c6: cmp      r3, #0x7f
080262c8: beq      #0x8026314
080262ca: ldr      r0, [pc, #0x114]
080262cc: bl       #0x80261d0
080262d0: ldr      r2, [pc, #0x110]
080262d2: ldr      r1, [pc, #0x114]
080262d4: cmp      r0, #0
080262d6: it       ne
080262d8: movne    r1, r2
080262da: ldr      r0, [pc, #0x100]
080262dc: bl       #0x80118dc
080262e0: ldr      r3, [pc, #0x108]
080262e2: ldr      r0, [pc, #0x10c]
080262e4: ldrb     r1, [r3, #2]
080262e6: bl       #0x801af4c
080262ea: ldrsb.w  r3, [r4]
080262ee: cbz      r3, #0x8026334
080262f0: cmp      r3, #0x7f
080262f2: beq      #0x8026334
080262f4: ldr      r0, [pc, #0xe4]
080262f6: movs     r1, #0xa
080262f8: add      sp, #8
080262fa: pop.w    {r4, lr}
080262fe: b.w      #0x8010e30
08026302: ldr      r1, [pc, #0xd4]
08026304: ldr      r0, [pc, #0xec]
08026306: bl       #0x80118be
0802630a: ldrsb.w  r3, [r4]
0802630e: cmp      r3, #0
08026310: beq      #0x80262c0
08026312: b        #0x80262b8
08026314: ldr      r0, [pc, #0xc8]
08026316: bl       #0x80261d0
0802631a: ldr      r2, [pc, #0xc8]
0802631c: ldr      r1, [pc, #0xc8]
0802631e: cmp      r0, #0
08026320: it       ne
08026322: movne    r1, r2
08026324: ldr      r0, [pc, #0xcc]
08026326: bl       #0x80118dc
0802632a: ldrsb.w  r3, [r4]
0802632e: cmp      r3, #0
08026330: beq      #0x80262e0
08026332: b        #0x80262ca
08026334: ldr      r0, [pc, #0xbc]
08026336: movs     r1, #0xa
08026338: bl       #0x8011bbc
0802633c: ldrsb.w  r3, [r4]
08026340: cmp      r3, #0
08026342: bne      #0x80262f4
08026344: add      sp, #8
08026346: pop      {r4, pc}
08026348: movs     r3, #2
0802634a: strb     r3, [r4]
0802634c: ldr      r0, [pc, #0xa8]
0802634e: ldr      r4, [pc, #0x80]
08026350: bl       #0x801aeac
08026354: ldr      r3, [pc, #0x94]
08026356: ldr      r0, [pc, #0x98]
08026358: ldrb     r1, [r3, #4]
0802635a: bl       #0x801af4c
0802635e: ldrsb.w  r2, [r4]
08026362: cbz      r2, #0x8026384
08026364: cmp      r2, #0x7f
08026366: beq      #0x8026384
08026368: ldr      r0, [pc, #0x70]
0802636a: movs     r1, #0xa
0802636c: bl       #0x8010e30
08026370: ldr      r0, [pc, #0x88]
08026372: bl       #0x8026110
08026376: mov      r1, r0
08026378: ldr      r0, [pc, #0x84]
0802637a: add      sp, #8
0802637c: pop.w    {r4, lr}
08026380: b.w      #0x801af4c
08026384: ldr      r0, [pc, #0x6c]
08026386: movs     r1, #0xa
08026388: bl       #0x8011bbc
0802638c: ldrsb.w  r3, [r4]
08026390: cmp      r3, #0
08026392: beq      #0x8026370
08026394: b        #0x8026368
08026396: movs     r3, #3
08026398: ldr      r0, [pc, #0x68]
0802639a: strb     r3, [r4]
0802639c: b        #0x8026298
0802639e: movs     r3, #3
080263a0: ldr      r0, [pc, #0x64]
080263a2: strb     r3, [r4]
080263a4: b        #0x8026298
080263a6: movs     r3, #3
080263a8: ldr      r0, [pc, #0x60]
080263aa: strb     r3, [r4]
080263ac: b        #0x8026298
080263ae: movs     r3, #3
080263b0: ldr      r0, [pc, #0x5c]
080263b2: strb     r3, [r4]
080263b4: b        #0x8026298
080263b6: movs     r3, #3
080263b8: ldr      r0, [pc, #0x58]
080263ba: strb     r3, [r4]
080263bc: b        #0x8026298
080263be: movs     r3, #3
080263c0: ldr      r0, [pc, #0x54]
080263c2: strb     r3, [r4]
080263c4: b        #0x8026298
080263c6: ldr      r0, [pc, #0x54]
080263c8: b        #0x8026298
080263ca: nop      
080263cc: ldrb     r6, [r7, r7]
080263ce: lsrs     r3, r0, #0x20
080263d0: ldrsb    r1, [r3, r5]
080263d2: movs     r0, #0
080263d4: ldrsh    r3, [r2, r0]
080263d6: lsrs     r3, r0, #0x20
080263d8: ldrsh    r4, [r4, r0]
080263da: lsrs     r3, r0, #0x20
080263dc: asrs     r0, r7, #0xd
080263de: movs     r0, #0
080263e0: str      r1, [r0, #0x3c]
080263e2: movs     r0, #0
080263e4: ldrh     r1, [r5, r0]
080263e6: lsrs     r3, r0, #0x20
080263e8: ldr      r1, [r3, r4]
080263ea: lsrs     r3, r0, #0x20
080263ec: str      r0, [r0, #0x3c]
080263ee: movs     r0, #0
080263f0: ldrsh    r5, [r6, r0]
080263f2: lsrs     r3, r0, #0x20
080263f4: asrs     r4, r3, #4
080263f6: movs     r0, #0
080263f8: ldrsh    r5, [r0, r1]
080263fa: lsrs     r3, r0, #0x20
080263fc: str      r4, [r0, #0x3c]
080263fe: movs     r0, #0
08026400: ldrsh    r4, [r2, r1]
08026402: lsrs     r3, r0, #0x20
08026404: ldrsh    r5, [r4, r1]
08026406: lsrs     r3, r0, #0x20
08026408: ldrsh    r2, [r7, r1]
0802640a: lsrs     r3, r0, #0x20
0802640c: ldrsh    r0, [r2, r2]
0802640e: lsrs     r3, r0, #0x20
08026410: ldrsh    r5, [r4, r2]
08026412: lsrs     r3, r0, #0x20
08026414: ldrsh    r3, [r7, r2]
08026416: lsrs     r3, r0, #0x20
08026418: ldrsh    r1, [r2, r3]
0802641a: lsrs     r3, r0, #0x20
0802641c: ldrsh    r6, [r4, r3]
0802641e: lsrs     r3, r0, #0x20
