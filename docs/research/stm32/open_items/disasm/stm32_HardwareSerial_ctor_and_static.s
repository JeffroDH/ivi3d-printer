08010ea0: push     {r3, r4, r5, lr}
08010ea2: movs     r2, #0
08010ea4: mov.w    r3, #0x3e8
08010ea8: strd     r2, r3, [r0, #4]
08010eac: ldr      r3, [pc, #0x88]
08010eae: str      r3, [r0]
08010eb0: ldr      r3, [pc, #0x88]
08010eb2: cmp      r1, r3
08010eb4: mov      r4, r0
08010eb6: mov      r5, r1
08010eb8: bne      #0x8010ed0
08010eba: ldr      r3, [pc, #0x84]
08010ebc: ldrh     r2, [r3, #0x12]
08010ebe: strh.w   r2, [r0, #0x262]
08010ec2: ldrh     r3, [r3, #0x14]
08010ec4: strh.w   r3, [r4, #0x260]
08010ec8: mov      r0, r4
08010eca: bl       #0x8010e84
08010ece: pop      {r3, r4, r5, pc}
08010ed0: ldr      r3, [pc, #0x70]
08010ed2: cmp      r1, r3
08010ed4: bne      #0x8010ee6
08010ed6: ldr      r3, [pc, #0x68]
08010ed8: ldrh.w   r2, [r3, #0x46]
08010edc: strh.w   r2, [r0, #0x262]
08010ee0: ldrh.w   r3, [r3, #0x48]
08010ee4: b        #0x8010ec4
08010ee6: ldr      r3, [pc, #0x60]
08010ee8: cmp      r1, r3
08010eea: bne      #0x8010ef8
08010eec: ldr      r3, [pc, #0x50]
08010eee: ldrh     r2, [r3, #0x1a]
08010ef0: strh.w   r2, [r0, #0x262]
08010ef4: ldrh     r3, [r3, #0x20]
08010ef6: b        #0x8010ec4
08010ef8: ldr      r3, [pc, #0x50]
08010efa: cmp      r1, r3
08010efc: bne      #0x8010f0a
08010efe: ldr      r3, [pc, #0x40]
08010f00: ldrh     r2, [r3, #0x22]
08010f02: strh.w   r2, [r0, #0x262]
08010f06: ldrh     r3, [r3, #0x24]
08010f08: b        #0x8010ec4
08010f0a: ldr      r3, [pc, #0x44]
08010f0c: cmp      r1, r3
08010f0e: bne      #0x8010f1c
08010f10: ldr      r3, [pc, #0x2c]
08010f12: ldrh     r2, [r3, #0x36]
08010f14: strh.w   r2, [r0, #0x262]
08010f18: ldrh     r3, [r3, #0x38]
08010f1a: b        #0x8010ec4
08010f1c: ldr      r1, [pc, #0x34]
08010f1e: mov      r0, r5
08010f20: bl       #0x8016dc8
08010f24: ldr      r1, [pc, #0x30]
08010f26: strh.w   r0, [r4, #0x262]
08010f2a: mov      r0, r5
08010f2c: bl       #0x8016dc8
08010f30: strh.w   r0, [r4, #0x260]
08010f34: b        #0x8010ec8
08010f36: nop      
08010f38: add      r0, r0
08010f3a: lsrs     r3, r0, #0x20
08010f3c: add      r0, r0
08010f3e: ands     r0, r0
08010f40: cmn      r0, r6
08010f42: lsrs     r3, r0, #0x20
08010f44: ldr      r0, [pc, #0]
08010f46: ands     r0, r0
08010f48: ldr      r4, [pc, #0]
08010f4a: ands     r0, r0
08010f4c: str      r0, [r0, r0]
08010f4e: ands     r0, r0
08010f50: asrs     r0, r0, #0x10
08010f52: ands     r1, r0
08010f54: lsls     r4, r7
08010f56: lsrs     r3, r0, #0x20
08010f58: adcs     r0, r0
08010f5a: lsrs     r3, r0, #0x20
08010f5c: push.w   {r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}
08010f60: and      r3, r2, #7
08010f64: subs     r3, #2
08010f66: uxtb     r3, r3
08010f68: cmp      r3, #4
08010f6a: mov      r6, r1
08010f6c: str.w    r1, [r0, #0x27c]
08010f70: it       ls
08010f72: ldrls    r1, [pc, #0x78]
08010f74: strb.w   r2, [r0, #0x278]
08010f78: it       ls
08010f7a: ldrbls   r4, [r1, r3]
08010f7c: and      r3, r2, #0x30
08010f80: it       hi
08010f82: movhi    r4, #0
08010f84: cmp      r3, #0x30
08010f86: mov      r5, r0
08010f88: bne      #0x8010fd2
08010f8a: adds     r4, #1
08010f8c: mov.w    r7, #0x600
08010f90: tst.w    r2, #8
08010f94: ite      ne
08010f96: movne.w  r8, #0x2000
08010f9a: moveq.w  r8, #0
08010f9e: cmp      r4, #8
08010fa0: beq      #0x8010fe0
08010fa2: cmp      r4, #9
08010fa4: beq      #0x8010fe4
08010fa6: ldr      r0, [pc, #0x48]
08010fa8: movw     r1, #0x159
08010fac: bl       #0x8016e7e
08010fb0: add.w    r0, r5, #0x214
08010fb4: mov      r1, r6
08010fb6: str.w    r8, [sp]
08010fba: mov      r3, r7
08010fbc: mov      r2, r4
08010fbe: str      r0, [sp, #0xc]
08010fc0: bl       #0x8017428
08010fc4: ldr      r1, [pc, #0x2c]
08010fc6: ldr      r0, [sp, #0xc]
08010fc8: add      sp, #0x10
08010fca: pop.w    {r4, r5, r6, r7, r8, lr}
08010fce: b.w      #0x80176ac
08010fd2: ands     r7, r2, #0x20
08010fd6: itt      ne
08010fd8: addne    r4, #1
08010fda: movne.w  r7, #0x400
08010fde: b        #0x8010f90
08010fe0: movs     r4, #0
08010fe2: b        #0x8010fb0
08010fe4: mov.w    r4, #0x1000
08010fe8: b        #0x8010fb0
08010fea: nop      
08010fec: mvns     r3, r6
08010fee: lsrs     r3, r0, #0x20
08010ff0: bics     r6, r0
08010ff2: lsrs     r3, r0, #0x20
08010ff4: lsrs     r1, r7, #0x17
08010ff6: lsrs     r1, r0, #0x20
08010ff8: push     {r3, lr}
08010ffa: ldr      r1, [pc, #0x2c]
08010ffc: ldr      r0, [pc, #0x2c]
08010ffe: bl       #0x8010ea0
08011002: ldr      r1, [pc, #0x2c]
08011004: ldr      r0, [pc, #0x2c]
08011006: bl       #0x8010ea0
0801100a: ldr      r1, [pc, #0x2c]
0801100c: ldr      r0, [pc, #0x2c]
0801100e: bl       #0x8010ea0
08011012: ldr      r1, [pc, #0x2c]
08011014: ldr      r0, [pc, #0x2c]
08011016: bl       #0x8010ea0
0801101a: pop.w    {r3, lr}
0801101e: ldr      r1, [pc, #0x28]
08011020: ldr      r0, [pc, #0x28]
08011022: b.w      #0x8010ea0
08011026: nop      
08011028: add      r0, r0
0801102a: ands     r0, r0
0801102c: lsls     r4, r4, #0x11
0801102e: movs     r0, #0
08011030: ldr      r0, [pc, #0]
08011032: ands     r0, r0
08011034: lsls     r4, r4, #0x1b
08011036: movs     r0, #0
08011038: ldr      r4, [pc, #0]
0801103a: ands     r0, r0
0801103c: lsrs     r4, r4, #5
0801103e: movs     r0, #0
08011040: str      r0, [r0, r0]
08011042: ands     r0, r0
08011044: lsrs     r4, r4, #0xf
08011046: movs     r0, #0
08011048: asrs     r0, r0, #0x10
0801104a: ands     r1, r0
0801104c: lsrs     r4, r4, #0x19
0801104e: movs     r0, #0
