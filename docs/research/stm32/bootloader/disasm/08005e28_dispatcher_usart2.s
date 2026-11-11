08005e28: push     {r1, r2, r3, r4, r5, lr}
08005e2a: movs     r0, #0
08005e2c: str      r0, [sp, #8]
08005e2e: movs     r4, #0
08005e30: str      r0, [sp]
08005e32: str      r0, [sp, #4]
08005e34: ldr      r0, [pc, #0x1f0] ; [0x08006028]=0x20000020
08005e36: ldrb     r0, [r0]
08005e38: cmp      r0, #2
08005e3a: bne      #0x8005e8c
08005e3c: movs     r0, #0xc4
08005e3e: strb.w   r0, [sp]
08005e42: movs     r0, #5
08005e44: strb.w   r0, [sp, #1]
08005e48: ldr      r0, [pc, #0x1e0] ; [0x0800602c]=0x20000000
08005e4a: ldrb     r0, [r0]
08005e4c: strb.w   r0, [sp, #2]
08005e50: movs     r0, #0
08005e52: str      r0, [sp, #8]
08005e54: movs     r2, #3
08005e56: mov      r1, sp
08005e58: add      r0, sp, #8
08005e5a: bl       #0x8005912
08005e5e: ldrh.w   r0, [sp, #8]
08005e62: uxtb     r0, r0
08005e64: strb.w   r0, [sp, #3]
08005e68: ldrh.w   r0, [sp, #8]
08005e6c: lsrs     r0, r0, #8
08005e6e: strb.w   r0, [sp, #4]
08005e72: movs     r1, #5
08005e74: mov      r0, sp
08005e76: bl       #0x8006224
08005e7a: movs     r0, #0xe0
08005e7c: ldr      r1, [pc, #0x1ac] ; [0x0800602c]=0x20000000
08005e7e: str      r0, [r1]
08005e80: movs     r0, #0
08005e82: ldr      r1, [pc, #0x1a4] ; [0x08006028]=0x20000020
08005e84: strb     r0, [r1]
08005e86: ldr      r1, [pc, #0x1a8] ; [0x08006030]=0x2000001c
08005e88: str      r0, [r1]
08005e8a: pop      {r1, r2, r3, r4, r5, pc}
08005e8c: ldr      r0, [pc, #0x198] ; [0x08006028]=0x20000020
08005e8e: ldrb     r0, [r0]
08005e90: cmp      r0, #1
08005e92: beq      #0x8005e9a
08005e94: mov.w    r0, #-1
08005e98: b        #0x8005e8a
08005e9a: ldr      r0, [pc, #0x190] ; [0x0800602c]=0x20000000
08005e9c: ldr      r0, [r0]
08005e9e: cmp      r0, #0xe0
08005ea0: beq      #0x8005ef4
08005ea2: movs     r0, #0xc0
08005ea4: strb.w   r0, [sp]
08005ea8: movs     r0, #5
08005eaa: strb.w   r0, [sp, #1]
08005eae: ldr      r0, [pc, #0x17c] ; [0x0800602c]=0x20000000
08005eb0: ldrb     r0, [r0]
08005eb2: strb.w   r0, [sp, #2]
08005eb6: movs     r0, #0
08005eb8: str      r0, [sp, #8]
08005eba: movs     r2, #3
08005ebc: mov      r1, sp
08005ebe: add      r0, sp, #8
08005ec0: bl       #0x8005912
08005ec4: ldrh.w   r0, [sp, #8]
08005ec8: uxtb     r0, r0
08005eca: strb.w   r0, [sp, #3]
08005ece: ldrh.w   r0, [sp, #8]
08005ed2: lsrs     r0, r0, #8
08005ed4: strb.w   r0, [sp, #4]
08005ed8: movs     r1, #5
08005eda: mov      r0, sp
08005edc: bl       #0x8006224
08005ee0: movs     r0, #0xe0
08005ee2: ldr      r1, [pc, #0x148] ; [0x0800602c]=0x20000000
08005ee4: str      r0, [r1]
08005ee6: movs     r0, #0
08005ee8: ldr      r1, [pc, #0x13c] ; [0x08006028]=0x20000020
08005eea: strb     r0, [r1]
08005eec: ldr      r1, [pc, #0x140] ; [0x08006030]=0x2000001c
08005eee: str      r0, [r1]
08005ef0: subs     r0, r0, #1
08005ef2: b        #0x8005e8a
08005ef4: movs     r0, #0
08005ef6: ldr      r1, [pc, #0x138] ; [0x08006030]=0x2000001c
08005ef8: str      r0, [r1]
08005efa: ldr      r1, [pc, #0x12c] ; [0x08006028]=0x20000020
08005efc: strb     r0, [r1]
08005efe: ldr      r0, [pc, #0x134] ; [0x08006034]=0x20000018
08005f00: ldr      r0, [r0]
08005f02: subs     r2, r0, #2
08005f04: ldr      r1, [pc, #0x130] ; [0x08006038]=0x200001bc
08005f06: add      r0, sp, #8
08005f08: bl       #0x8005912
08005f0c: ldr      r0, [pc, #0x124] ; [0x08006034]=0x20000018
08005f0e: ldr      r0, [r0]
08005f10: subs     r0, r0, #2
08005f12: ldr      r1, [pc, #0x124] ; [0x08006038]=0x200001bc
08005f14: ldrb     r1, [r1, r0]
08005f16: ldr      r0, [pc, #0x11c] ; [0x08006034]=0x20000018
08005f18: ldr      r0, [r0]
08005f1a: subs     r0, r0, #1
08005f1c: ldr      r2, [pc, #0x118] ; [0x08006038]=0x200001bc
08005f1e: ldrb     r0, [r2, r0]
08005f20: orr.w    r4, r1, r0, lsl #8
08005f24: ldrh.w   r0, [sp, #8]
08005f28: cmp      r0, r4
08005f2a: beq      #0x8005f6e
08005f2c: movs     r0, #0xc0
08005f2e: strb.w   r0, [sp]
08005f32: movs     r0, #5
08005f34: strb.w   r0, [sp, #1]
08005f38: movs     r0, #0xe4
08005f3a: strb.w   r0, [sp, #2]
08005f3e: movs     r0, #0
08005f40: str      r0, [sp, #8]
08005f42: movs     r2, #3
08005f44: mov      r1, sp
08005f46: add      r0, sp, #8
08005f48: bl       #0x8005912
08005f4c: ldrh.w   r0, [sp, #8]
08005f50: uxtb     r0, r0
08005f52: strb.w   r0, [sp, #3]
08005f56: ldrh.w   r0, [sp, #8]
08005f5a: lsrs     r0, r0, #8
08005f5c: strb.w   r0, [sp, #4]
08005f60: movs     r1, #5
08005f62: mov      r0, sp
08005f64: bl       #0x8006224
08005f68: mov.w    r0, #-1
08005f6c: b        #0x8005e8a
08005f6e: ldr      r0, [pc, #0xc8] ; [0x08006038]=0x200001bc
08005f70: ldrb     r0, [r0]
08005f72: subs     r0, #0xa0
08005f74: cmp      r0, #5
08005f76: bhs      #0x8005fe2
08005f78: tbb      [pc, r0]
08005f7c: lsrs     r3, r0, #0xc
08005f7e: movs     r3, #0x17
08005f80: movs     r7, r5
08005f82: movs     r0, #0xc0
08005f84: strb.w   r0, [sp]
08005f88: ldr      r0, [pc, #0xa0] ; [0x0800602c]=0x20000000
08005f8a: ldrb     r0, [r0]
08005f8c: strb.w   r0, [sp, #2]
08005f90: b        #0x8005ff2
08005f92: movs     r0, #0xc1
08005f94: strb.w   r0, [sp]
08005f98: bl       #0x80062b4
08005f9c: ldr      r1, [pc, #0x8c] ; [0x0800602c]=0x20000000
08005f9e: str      r0, [r1]
08005fa0: mov      r0, r1
08005fa2: ldrb     r0, [r0]
08005fa4: strb.w   r0, [sp, #2]
08005fa8: b        #0x8005ff2
08005faa: movs     r0, #0xc2
08005fac: strb.w   r0, [sp]
08005fb0: bl       #0x8006260
08005fb4: ldr      r1, [pc, #0x74] ; [0x0800602c]=0x20000000
08005fb6: str      r0, [r1]
08005fb8: mov      r0, r1
08005fba: ldrb     r0, [r0]
08005fbc: strb.w   r0, [sp, #2]
08005fc0: b        #0x8005ff2
08005fc2: movs     r0, #0xc3
08005fc4: strb.w   r0, [sp]
08005fc8: bl       #0x800632c
08005fcc: ldr      r1, [pc, #0x5c] ; [0x0800602c]=0x20000000
08005fce: str      r0, [r1]
08005fd0: mov      r0, r1
08005fd2: ldrb     r0, [r0]
08005fd4: strb.w   r0, [sp, #2]
08005fd8: b        #0x8005ff2
08005fda: ldr      r0, [pc, #0x60] ; [0x0800603c]=0x08010000
08005fdc: bl       #0x8005b08
08005fe0: b        #0x8005ff2
08005fe2: movs     r0, #0xe1
08005fe4: ldr      r1, [pc, #0x44] ; [0x0800602c]=0x20000000
08005fe6: str      r0, [r1]
08005fe8: mov      r0, r1
08005fea: ldrb     r0, [r0]
08005fec: strb.w   r0, [sp, #2]
08005ff0: nop      
08005ff2: nop      
08005ff4: movs     r0, #0
08005ff6: str      r0, [sp, #8]
08005ff8: movs     r0, #5
08005ffa: strb.w   r0, [sp, #1]
08005ffe: movs     r2, #4
08006000: mov      r1, sp
08006002: add      r0, sp, #8
08006004: bl       #0x8005912
08006008: ldrh.w   r0, [sp, #8]
0800600c: uxtb     r0, r0
0800600e: strb.w   r0, [sp, #3]
08006012: ldrh.w   r0, [sp, #8]
08006016: lsrs     r0, r0, #8
08006018: strb.w   r0, [sp, #4]
0800601c: movs     r1, #5
0800601e: mov      r0, sp
08006020: bl       #0x8006224
08006024: movs     r0, #0
08006026: b        #0x8005e8a
08006028: movs     r0, r4
0800602a: movs     r0, #0
0800602c: movs     r0, r0
0800602e: movs     r0, #0
08006030: movs     r4, r3
08006032: movs     r0, #0
08006034: movs     r0, r3
08006036: movs     r0, #0
08006038: lsls     r4, r7, #6
0800603a: movs     r0, #0
0800603c: movs     r0, r0
0800603e: lsrs     r1, r0, #0x20
