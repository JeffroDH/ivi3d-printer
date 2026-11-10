08018ebc: cmp      r0, #0x4a
08018ebe: push.w   {r4, r5, r6, r7, r8, lr}
08018ec2: mov      r5, r0
08018ec4: mov      r6, r1
08018ec6: bhi      #0x8018f8a
08018ec8: ldr      r3, [pc, #0xc4]
08018eca: ldrsh.w  r4, [r3, r0, lsl #1]
08018ece: adds     r7, r4, #1
08018ed0: beq      #0x8018f8a
08018ed2: ldr      r1, [pc, #0xc0]
08018ed4: ldr      r7, [pc, #0xc0]
08018ed6: mov      r0, r4
08018ed8: bl       #0x8016c1a
08018edc: cbz      r0, #0x8018f1e
08018ede: ubfx     r1, r4, #4, #4
08018ee2: ldr      r2, [pc, #0xb8]
08018ee4: ldr.w    r0, [r2, r1, lsl #2]
08018ee8: and      r3, r4, #0xf
08018eec: lsr.w    r5, r0, r3
08018ef0: lsls     r5, r5, #0x1f
08018ef2: itttt    pl
08018ef4: movpl    r5, #1
08018ef6: lslpl.w  r3, r5, r3
08018efa: orrpl    r3, r0
08018efc: strpl.w  r3, [r2, r1, lsl #2]
08018f00: mov      r0, r6
08018f02: ldr      r1, [r7]
08018f04: mov.w    r2, #0xc
08018f08: it       mi
08018f0a: movmi    r5, #0
08018f0c: bl       #0x8018e70
08018f10: mov      r2, r5
08018f12: mov      r1, r0
08018f14: mov      r0, r4
08018f16: pop.w    {r4, r5, r6, r7, r8, lr}
08018f1a: b.w      #0x801668c
08018f1e: ldr      r1, [pc, #0x80]
08018f20: mov      r0, r4
08018f22: bl       #0x8016c1a
08018f26: mov      r8, r0
08018f28: cbz      r0, #0x8018f64
08018f2a: ubfx     r1, r4, #4, #4
08018f2e: ldr      r2, [pc, #0x6c]
08018f30: ldr.w    r0, [r2, r1, lsl #2]
08018f34: and      r5, r4, #0xf
08018f38: lsr.w    r3, r0, r5
08018f3c: lsls     r3, r3, #0x1f
08018f3e: itttt    pl
08018f40: movpl    r3, #1
08018f42: lslpl    r3, r5
08018f44: orrpl    r3, r0
08018f46: strpl.w  r3, [r2, r1, lsl #2]
08018f4a: mov      r0, r6
08018f4c: ldr      r1, [r7]
08018f4e: movs     r2, #0xc
08018f50: bl       #0x8018e70
08018f54: ldr      r3, [pc, #0x4c]
08018f56: mov      r2, r0
08018f58: ldr      r1, [r3]
08018f5a: mov      r0, r4
08018f5c: pop.w    {r4, r5, r6, r7, r8, lr}
08018f60: b.w      #0x8016980
08018f64: mov      r0, r5
08018f66: movs     r1, #1
08018f68: bl       #0x8018fa8
08018f6c: ldr      r1, [r7]
08018f6e: mov      r0, r6
08018f70: movs     r2, #8
08018f72: bl       #0x8018e70
08018f76: cmp      r0, #0x7f
08018f78: it       ls
08018f7a: movls    r1, r8
08018f7c: mov      r0, r5
08018f7e: it       hi
08018f80: movhi    r1, #1
08018f82: pop.w    {r4, r5, r6, r7, r8, lr}
08018f86: b.w      #0x801905c
08018f8a: pop.w    {r4, r5, r6, r7, r8, pc}
08018f8e: nop      
08018f90: cmn      r0, r6
08018f92: lsrs     r3, r0, #0x20
08018f94: subs     r6, #0xa0
08018f96: lsrs     r3, r0, #0x20
08018f98: lsls     r0, r0, #7
08018f9a: movs     r0, #0
08018f9c: asrs     r0, r1, #0xb
08018f9e: movs     r0, #0
08018fa0: subs     r6, #0xc4
08018fa2: lsrs     r3, r0, #0x20
08018fa4: lsls     r4, r7, #6
08018fa6: movs     r0, #0
