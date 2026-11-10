08020bd4: ldr      r3, [pc, #0x94]
08020bd6: ldr      r3, [r3]
08020bd8: ubfx     r0, r3, #0x12, #1
08020bdc: lsls     r3, r3, #0xd
08020bde: push     {r4, lr}
08020be0: bpl      #0x8020c0c
08020be2: ldr      r3, [pc, #0x8c]
08020be4: ldrb     r2, [r3, #0x12]
08020be6: cmp      r2, #0
08020be8: beq      #0x8020c64
08020bea: ldr      r3, [pc, #0x88]
08020bec: ldr      r1, [r3]
08020bee: adds     r3, r1, r2
08020bf0: ldrb     r2, [r1, r2]
08020bf2: sub.w    r1, r2, #0x30
08020bf6: cmp      r1, #9
08020bf8: bls      #0x8020c08
08020bfa: cmp      r2, #0x2e
08020bfc: bne      #0x8020c4a
08020bfe: ldrb     r2, [r3, #1]
08020c00: subs     r2, #0x30
08020c02: cmp      r2, #9
08020c04: it       hi
08020c06: movhi    r3, #0
08020c08: ldr      r2, [pc, #0x6c]
08020c0a: str      r3, [r2]
08020c0c: cbz      r0, #0x8020c68
08020c0e: ldr      r3, [pc, #0x68]
08020c10: ldr      r3, [r3]
08020c12: cbz      r3, #0x8020c68
08020c14: bl       #0x801c89c
08020c18: cmp      r0, #0
08020c1a: blt      #0x8020c68
08020c1c: bl       #0x801c89c
08020c20: cmp      r0, #0xff
08020c22: bgt      #0x8020c68
08020c24: bl       #0x801c89c
08020c28: uxtb     r4, r0
08020c2a: cmp      r4, #1
08020c2c: bne      #0x8020c68
08020c2e: ldr      r0, [pc, #0x4c]
08020c30: bl       #0x8011d24
08020c34: ldr      r0, [pc, #0x44]
08020c36: mov.w    r1, #0x1c200
08020c3a: bl       #0x8011d20
08020c3e: mov      r1, r4
08020c40: ldr      r0, [pc, #0x3c]
08020c42: pop.w    {r4, lr}
08020c46: b.w      #0x8026ac0
08020c4a: cmp      r2, #0x2d
08020c4c: beq      #0x8020c52
08020c4e: cmp      r2, #0x2b
08020c50: bne      #0x8020c64
08020c52: ldrb     r2, [r3, #1]
08020c54: sub.w    r1, r2, #0x30
08020c58: cmp      r1, #9
08020c5a: bls      #0x8020c08
08020c5c: cmp      r2, #0x2e
08020c5e: bne      #0x8020c64
08020c60: ldrb     r2, [r3, #2]
08020c62: b        #0x8020c00
08020c64: movs     r3, #0
08020c66: b        #0x8020c08
08020c68: pop      {r4, pc}
08020c6a: nop      
08020c6c: ldrsh    r0, [r5, r4]
08020c6e: movs     r0, #0
08020c70: ldrsh    r6, [r0, r4]
08020c72: movs     r0, #0
08020c74: ldrsh    r0, [r0, r4]
08020c76: movs     r0, #0
08020c78: ldrsh    r4, [r5, r4]
08020c7a: movs     r0, #0
08020c7c: asrs     r4, r3, #4
08020c7e: movs     r0, #0
08020c80: str      r4, [r2, #0x3c]
08020c82: movs     r0, #0
