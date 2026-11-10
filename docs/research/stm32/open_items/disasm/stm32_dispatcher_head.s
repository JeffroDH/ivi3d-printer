080230f8: push     {r4, r5, r6, lr}
080230fa: ldr      r6, [pc, #0x254]
080230fc: movs     r3, #1
080230fe: ldrb     r5, [r6]
08023100: strb     r3, [r6]
08023102: ldr      r3, [pc, #0x250]
08023104: ldrb     r3, [r3]
08023106: cmp      r3, #0x4d
08023108: mov      r4, r0
0802310a: beq.w    #0x8023224
0802310e: cmp      r3, #0x54
08023110: beq.w    #0x80238c0
08023114: cmp      r3, #0x47
08023116: bne      #0x8023176
08023118: ldr      r3, [pc, #0x23c]
0802311a: ldr      r3, [r3]
0802311c: cmp      r3, #0x3d
0802311e: bgt      #0x802316a
08023120: cmp      r3, #0
08023122: blt      #0x8023176
08023124: cmp      r3, #0x3d
08023126: bhi      #0x8023176
08023128: tbb      [pc, r3]
0802312c: cmp      r1, #0x29
0802312e: adds     r5, #0x35
08023130: movs     r5, #0x3e
08023132: movs     r5, #0x25
08023134: movs     r5, #0x25
08023136: movs     r5, #0x25
08023138: movs     r5, #0x25
0802313a: movs     r5, #0x25
0802313c: movs     r5, #0x25
0802313e: movs     r5, #0x25
08023140: cmp      r7, #0x25
08023142: movs     r5, #0x25
08023144: movs     r5, #0x25
08023146: add      r1, r8
08023148: ldr      r2, [pc, #0x11c]
0802314a: movs     r5, #0x4d
0802314c: str      r5, [r4, r0]
0802314e: movs     r5, #0x25
08023150: movs     r5, #0x25
08023152: movs     r5, #0x25
08023154: movs     r5, #0x25
08023156: movs     r5, #0x79
08023158: movs     r5, #0x25
0802315a: movs     r5, #0x25
0802315c: movs     r5, #0x25
0802315e: movs     r5, #0x25
08023160: strh     r5, [r4, r4]
08023162: ldr      r6, [r2, r5]
08023164: ldrsh    r4, [r3, r5]
08023166: str      r2, [r4, #0x54]
08023168: ldr      r0, [r5, #0x34]
0802316a: cmp      r3, #0x5b
0802316c: beq      #0x8023210
0802316e: cmp      r3, #0x5c
08023170: beq      #0x8023218
08023172: cmp      r3, #0x5a
08023174: beq      #0x8023208
08023176: ldr      r0, [pc, #0x1e4]
08023178: bl       #0x8024b50
0802317c: b        #0x802318a
0802317e: eor      r3, r3, #1
08023182: and      r0, r3, #1
08023186: bl       #0x8024238
0802318a: cmp      r4, #0
0802318c: bne.w    #0x802371e
08023190: bl       #0x8025038
08023194: b        #0x802371e
08023196: sub.w    ip, r3, #2
0802319a: rsbs.w   r0, ip, #0
0802319e: adc.w    r0, r0, ip
080231a2: bl       #0x802456c
080231a6: b        #0x802318a
080231a8: bl       #0x80246d0
080231ac: b        #0x802318a
080231ae: bl       #0x801cfd0
080231b2: b        #0x802318a
080231b4: bl       #0x8022a68
080231b8: b        #0x802318a
080231ba: bl       #0x801e758
080231be: b        #0x802318a
080231c0: bl       #0x801ddc8
080231c4: b        #0x802318a
080231c6: bl       #0x8024b58
080231ca: b        #0x802318a
080231cc: bl       #0x801ed88
080231d0: b        #0x802318a
080231d2: bl       #0x8023b68
080231d6: b        #0x802318a
080231d8: bl       #0x8023bfc
080231dc: b        #0x802318a
080231de: bl       #0x8023c02
080231e2: b        #0x802318a
080231e4: bl       #0x8023c06
080231e8: b        #0x802318a
080231ea: bl       #0x8023c0a
080231ee: b        #0x802318a
080231f0: bl       #0x8023c0e
080231f4: b        #0x802318a
080231f6: bl       #0x8023c14
080231fa: b        #0x802318a
080231fc: bl       #0x8022b08
08023200: b        #0x802318a
08023202: bl       #0x8022bc8
08023206: b        #0x802318a
08023208: ldr      r3, [pc, #0x154]
0802320a: movs     r2, #0
0802320c: strb     r2, [r3]
0802320e: b        #0x802318a
08023210: ldr      r3, [pc, #0x14c]
08023212: movs     r2, #0xf
08023214: strb     r2, [r3]
08023216: b        #0x802318a
08023218: bl       #0x8023c20
0802321c: b        #0x802318a
0802321e: bl       #0x801d840
08023222: b        #0x802318a
08023224: ldr      r3, [pc, #0x130]
08023226: ldr      r3, [r3]
08023228: cmp.w    r3, #0x122
0802322c: beq.w    #0x80237d6
08023230: bgt.w    #0x8023558
08023234: cmp      r3, #0x9b
08023236: bgt.w    #0x80234d0
0802323a: cmp      r3, #0x4a
0802323c: bgt.w    #0x8023364
08023240: cmp      r3, #0x12
08023242: bgt.w    #0x80234b8
08023246: cmp      r3, #0
08023248: blt      #0x8023176
0802324a: cmp      r3, #0x12
0802324c: bhi      #0x8023176
0802324e: adr      r2, #4
08023250: ldr.w    pc, [r2, r3, lsl #2]
08023254: adds     r6, #0xcf
08023256: lsrs     r2, r0, #0x20
08023258: adds     r6, #0xcf
0802325a: lsrs     r2, r0, #0x20
0802325c: adds     r1, #0x77
0802325e: lsrs     r2, r0, #0x20
08023260: adds     r6, #0xd5
08023262: lsrs     r2, r0, #0x20
08023264: adds     r6, #0xdd
08023266: lsrs     r2, r0, #0x20
08023268: adds     r6, #0xe5
0802326a: lsrs     r2, r0, #0x20
0802326c: adds     r1, #0x77
0802326e: lsrs     r2, r0, #0x20
08023270: adds     r1, #0x77
08023272: lsrs     r2, r0, #0x20
08023274: adds     r1, #0x77
08023276: lsrs     r2, r0, #0x20
08023278: adds     r1, #0x77
0802327a: lsrs     r2, r0, #0x20
0802327c: adds     r1, #0x77
0802327e: lsrs     r2, r0, #0x20
08023280: adds     r1, #0x77
08023282: lsrs     r2, r0, #0x20
08023284: adds     r1, #0x77
08023286: lsrs     r2, r0, #0x20
08023288: adds     r1, #0x77
0802328a: lsrs     r2, r0, #0x20
0802328c: adds     r1, #0x77
0802328e: lsrs     r2, r0, #0x20
08023290: adds     r1, #0x77
08023292: lsrs     r2, r0, #0x20
08023294: adds     r1, #0x77
08023296: lsrs     r2, r0, #0x20
08023298: adds     r6, #0xeb
0802329a: lsrs     r2, r0, #0x20
0802329c: adds     r7, #0x65
0802329e: lsrs     r2, r0, #0x20
080232a0: subw     r3, r3, #0xb5f
080232a4: cmp      r3, #4
080232a6: bhi.w    #0x802389c
080232aa: tbh      [pc, r3, lsl #1]
080232ae: lsls     r2, r7, #0xb
080232b0: lsls     r5, r7, #0xb
080232b2: lsls     r0, r0, #0xc
080232b4: lsls     r3, r0, #0xc
080232b6: lsls     r6, r0, #0xc
080232b8: mvn      r1, #0x7d0
080232bc: add      r3, r1
080232be: cmp      r3, #9
080232c0: bhi.w    #0x8023176
080232c4: adr      r2, #4
080232c6: ldr.w    pc, [r2, r3, lsl #2]
080232ca: nop      
080232cc: subs     r0, #0x43
080232ce: lsrs     r2, r0, #0x20
080232d0: adds     r1, #0x77
080232d2: lsrs     r2, r0, #0x20
080232d4: adds     r1, #0x77
080232d6: lsrs     r2, r0, #0x20
080232d8: adds     r1, #0x77
080232da: lsrs     r2, r0, #0x20
080232dc: subs     r0, #0x4f
080232de: lsrs     r2, r0, #0x20
080232e0: subs     r0, #0x55
080232e2: lsrs     r2, r0, #0x20
080232e4: subs     r0, #0x49
080232e6: lsrs     r2, r0, #0x20
080232e8: adds     r1, #0x77
080232ea: lsrs     r2, r0, #0x20
080232ec: adds     r1, #0x77
080232ee: lsrs     r2, r0, #0x20
080232f0: subs     r0, #0x5b
080232f2: lsrs     r2, r0, #0x20
080232f4: mvn      r2, #0x1f4
080232f8: add      r3, r2
080232fa: cmp      r3, #3
080232fc: bhi.w    #0x8023806
08023300: tbh      [pc, r3, lsl #1]
08023304: lsls     r4, r0, #0xa
08023306: lsls     r7, r0, #0xa
08023308: lsls     r2, r1, #0xa
0802330a: lsls     r5, r1, #0xa
0802330c: sub.w    r3, r3, #0x190
08023310: cmp      r3, #0xc
08023312: bhi.w    #0x8023176
08023316: adr      r2, #4
08023318: ldr.w    pc, [r2, r3, lsl #2]
0802331c: adds     r7, #0xe9
0802331e: lsrs     r2, r0, #0x20
08023320: adds     r7, #0xef
08023322: lsrs     r2, r0, #0x20
08023324: adds     r7, #0xf5
08023326: lsrs     r2, r0, #0x20
08023328: adds     r1, #0x77
0802332a: lsrs     r2, r0, #0x20
0802332c: adds     r1, #0x77
0802332e: lsrs     r2, r0, #0x20
08023330: adds     r1, #0x77
08023332: lsrs     r2, r0, #0x20
08023334: adds     r1, #0x77
08023336: lsrs     r2, r0, #0x20
08023338: adds     r1, #0x77
0802333a: lsrs     r2, r0, #0x20
0802333c: adds     r1, #0x77
0802333e: lsrs     r2, r0, #0x20
08023340: adds     r1, #0x77
08023342: lsrs     r2, r0, #0x20
08023344: adds     r1, #0x8b
08023346: lsrs     r2, r0, #0x20
08023348: adds     r1, #0x77
0802334a: lsrs     r2, r0, #0x20
0802334c: adds     r7, #0xfb
0802334e: lsrs     r2, r0, #0x20
08023350: ldrsh    r6, [r7, r1]
08023352: movs     r0, #0
08023354: ldrsh    r4, [r0, r4]
08023356: movs     r0, #0
08023358: ldrsh    r0, [r4, r4]
0802335a: movs     r0, #0
0802335c: ldrsh    r0, [r6, r4]
0802335e: movs     r0, #0
