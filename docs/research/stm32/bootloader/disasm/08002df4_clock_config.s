08002df4: push     {r4, r5, r6, lr}
08002df6: movs     r0, #5
08002df8: ldr      r1, [pc, #0x134] ; [0x08002f30]=0x40023c00
08002dfa: ldr      r1, [r1]
08002dfc: bic      r1, r1, #0xf
08002e00: orrs     r1, r0
08002e02: ldr      r2, [pc, #0x12c] ; [0x08002f30]=0x40023c00
08002e04: str      r1, [r2]
08002e06: nop      
08002e08: nop      
08002e0a: mov      r0, r2
08002e0c: ldr      r0, [r0]
08002e0e: and      r0, r0, #0xf
08002e12: cmp      r0, #5
08002e14: beq      #0x8002e1a
08002e16: bl       #0x80006a2
08002e1a: mov.w    r0, #0x4000
08002e1e: ldr      r1, [pc, #0x114] ; [0x08002f34]=0x40007000
08002e20: ldr      r1, [r1]
08002e22: bic      r1, r1, #0x4000
08002e26: orrs     r1, r0
08002e28: ldr      r2, [pc, #0x108] ; [0x08002f34]=0x40007000
08002e2a: str      r1, [r2]
08002e2c: nop      
08002e2e: nop      
08002e30: ldr      r0, [pc, #0x104] ; [0x08002f38]=0x40023800
08002e32: ldr      r0, [r0]
08002e34: orr      r0, r0, #0x10000
08002e38: ldr      r1, [pc, #0xfc] ; [0x08002f38]=0x40023800
08002e3a: str      r0, [r1]
08002e3c: nop      
08002e3e: nop      
08002e40: nop      
08002e42: ldr      r0, [pc, #0xf4] ; [0x08002f38]=0x40023800
08002e44: ldr      r0, [r0]
08002e46: ubfx     r0, r0, #0x11, #1
08002e4a: cmp      r0, #0
08002e4c: beq      #0x8002e40
08002e4e: mov.w    r0, #0x400000
08002e52: movs     r1, #4
08002e54: movs     r2, #0xa8
08002e56: movs     r3, #0
08002e58: orr.w    r4, r0, r1
08002e5c: orr.w    r4, r4, r2, lsl #6
08002e60: ldr      r5, [pc, #0xd4] ; [0x08002f38]=0x40023800
08002e62: adds     r5, r5, #4
08002e64: ldr      r5, [r5]
08002e66: ldr      r6, [pc, #0xd4] ; [0x08002f3c]=0xffbf8000
08002e68: ands     r5, r6
08002e6a: orrs     r4, r5
08002e6c: ldr      r5, [pc, #0xc8] ; [0x08002f38]=0x40023800
08002e6e: adds     r5, r5, #4
08002e70: str      r4, [r5]
08002e72: mov      r4, r5
08002e74: ldr      r4, [r4]
08002e76: bic      r4, r4, #0x30000
08002e7a: orrs     r4, r3
08002e7c: str      r4, [r5]
08002e7e: nop      
08002e80: mov.w    r3, #0x7000000
08002e84: orr.w    r4, r0, r1
08002e88: orr.w    r4, r4, r2, lsl #6
08002e8c: orrs     r4, r3
08002e8e: ldr      r5, [r5]
08002e90: ldr      r6, [pc, #0xac] ; [0x08002f40]=0xf0bf8000
08002e92: ands     r5, r6
08002e94: orrs     r4, r5
08002e96: ldr      r5, [pc, #0xa0] ; [0x08002f38]=0x40023800
08002e98: adds     r5, r5, #4
08002e9a: str      r4, [r5]
08002e9c: nop      
08002e9e: nop      
08002ea0: subs     r0, r5, #4
08002ea2: ldr      r0, [r0]
08002ea4: orr      r0, r0, #0x1000000
08002ea8: subs     r1, r5, #4
08002eaa: str      r0, [r1]
08002eac: nop      
08002eae: nop      
08002eb0: nop      
08002eb2: ldr      r0, [pc, #0x84] ; [0x08002f38]=0x40023800
08002eb4: ldr      r0, [r0]
08002eb6: ubfx     r0, r0, #0x19, #1
08002eba: cmp      r0, #0
08002ebc: beq      #0x8002eb0
08002ebe: movs     r0, #0
08002ec0: ldr      r1, [pc, #0x74] ; [0x08002f38]=0x40023800
08002ec2: adds     r1, #8
08002ec4: ldr      r1, [r1]
08002ec6: bic      r1, r1, #0xf0
08002eca: orrs     r1, r0
08002ecc: ldr      r2, [pc, #0x68] ; [0x08002f38]=0x40023800
08002ece: adds     r2, #8
08002ed0: str      r1, [r2]
08002ed2: nop      
08002ed4: mov.w    r0, #0x1400
08002ed8: mov      r1, r2
08002eda: ldr      r1, [r1]
08002edc: bic      r1, r1, #0x1c00
08002ee0: orrs     r1, r0
08002ee2: str      r1, [r2]
08002ee4: nop      
08002ee6: mov.w    r0, #0x8000
08002eea: mov      r1, r2
08002eec: ldr      r1, [r1]
08002eee: bic      r1, r1, #0xe000
08002ef2: orrs     r1, r0
08002ef4: str      r1, [r2]
08002ef6: nop      
08002ef8: movs     r0, #2
08002efa: mov      r1, r2
08002efc: ldr      r1, [r1]
08002efe: bic      r1, r1, #3
08002f02: orrs     r1, r0
08002f04: str      r1, [r2]
08002f06: nop      
08002f08: nop      
08002f0a: nop      
08002f0c: ldr      r0, [pc, #0x28] ; [0x08002f38]=0x40023800
08002f0e: adds     r0, #8
08002f10: ldr      r0, [r0]
08002f12: and      r0, r0, #0xc
08002f16: cmp      r0, #8
08002f18: bne      #0x8002f0a
08002f1a: ldr      r0, [pc, #0x28] ; [0x08002f44]=0x0a037a00
08002f1c: bl       #0x8002468
08002f20: movs     r0, #0
08002f22: bl       #0x8000f94
08002f26: cbz      r0, #0x8002f2c
08002f28: bl       #0x80006a2
08002f2c: pop      {r4, r5, r6, pc}
08002f2e: movs     r0, r0
08002f30: subs     r4, #0
08002f32: ands     r2, r0
08002f34: strb     r0, [r0]
08002f36: ands     r0, r0
08002f38: subs     r0, #0
08002f3a: ands     r2, r0
08002f3c: strh     r0, [r0]
