08005b08: push     {r4, lr}
08005b0a: mov      r4, r0
08005b0c: ldr      r2, [pc, #0x24] ; [0x08005b34]=0x2ffe0000
08005b0e: ldr      r0, [r4]
08005b10: and.w    r1, r0, r2
08005b14: adr      r0, #0x20
08005b16: bl       #0x8006040
08005b1a: bl       #0x8006580
08005b1e: ldr      r1, [pc, #0x28] ; [0x08005b48]=0x20000014
08005b20: ldr      r0, [r4, #4]
08005b22: str      r0, [r1]
08005b24: mov      r0, r4
08005b26: bl       #0x800019c
08005b2a: ldr      r0, [pc, #0x1c] ; [0x08005b48]=0x20000014
08005b2c: ldr      r0, [r0]
08005b2e: blx      r0
08005b30: pop      {r4, pc}
08005b32: movs     r0, r0
08005b34: movs     r0, r0
08005b36: cmp      r7, #0xfe
08005b38: strb     r0, [r4, #0xc]
08005b3a: str      r4, [r6, #0x14]
08005b3c: ldr      r3, [r4, #0x34]
08005b3e: movs     r0, #0x3a
08005b40: ldrb     r5, [r4]
08005b42: lsrs     r5, r1, #8
08005b44: movs     r0, r0
08005b46: movs     r0, r0
08005b48: movs     r4, r2
08005b4a: movs     r0, #0
