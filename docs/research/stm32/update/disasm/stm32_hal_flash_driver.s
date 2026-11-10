; STM32 HAL FLASH driver region 0x08012B00..0x08012E80 — only FLASH_KEYR(+4), SR(+0xC), CR(+0x10), ACR(+0) touched; no OPTKEYR(+8)/OPTCR(+0x14)
; source: supx_raw.bin
; tool: Capstone 5.0.7 (single tool; cross-checked only against the existing Ghidra 12.x decompile in ivi_fwaudit/out/app.c or ivi/supx_decomp.c)

08012b00: movs     r0, #0
08012b02: bx       lr
08012b04: ldrb.w   r0, [r0, #0x35]
08012b08: bx       lr
08012b0a: movs     r0, r0
08012b0c: ldr      r1, [pc, #0x20]
08012b0e: push     {r4, lr}
08012b10: ldr      r4, [r1, #0x10]
08012b12: bic      r4, r4, #0x300
08012b16: str      r4, [r1, #0x10]
08012b18: ldr      r4, [r1, #0x10]
08012b1a: orr      r4, r4, #0x300
08012b1e: str      r4, [r1, #0x10]
08012b20: ldr      r4, [r1, #0x10]
08012b22: orr      r4, r4, #1
08012b26: str      r4, [r1, #0x10]
08012b28: str      r2, [r0]
08012b2a: str      r3, [r0, #4]
08012b2c: pop      {r4, pc}
08012b2e: nop      
08012b30: subs     r4, #0
08012b32: ands     r2, r0
08012b34: ldr      r3, [pc, #0x1c]
08012b36: ldr      r2, [r3, #0x10]
08012b38: bic      r2, r2, #0x300
08012b3c: str      r2, [r3, #0x10]
08012b3e: ldr      r2, [r3, #0x10]
08012b40: orr      r2, r2, #0x200
08012b44: str      r2, [r3, #0x10]
08012b46: ldr      r2, [r3, #0x10]
08012b48: orr      r2, r2, #1
08012b4c: str      r2, [r3, #0x10]
08012b4e: str      r1, [r0]
08012b50: bx       lr
08012b52: nop      
08012b54: subs     r4, #0
08012b56: ands     r2, r0
08012b58: ldr      r3, [pc, #0x1c]
08012b5a: ldr      r2, [r3, #0x10]
08012b5c: bic      r2, r2, #0x300
08012b60: str      r2, [r3, #0x10]
08012b62: ldr      r2, [r3, #0x10]
08012b64: orr      r2, r2, #0x100
08012b68: str      r2, [r3, #0x10]
08012b6a: ldr      r2, [r3, #0x10]
08012b6c: orr      r2, r2, #1
08012b70: str      r2, [r3, #0x10]
08012b72: strh     r1, [r0]
08012b74: bx       lr
08012b76: nop      
08012b78: subs     r4, #0
08012b7a: ands     r2, r0
08012b7c: ldr      r3, [pc, #0x68]
08012b7e: ldr      r2, [r3, #0xc]
08012b80: lsls     r2, r2, #0x1b
08012b82: bpl      #0x8012b92
08012b84: ldr      r1, [pc, #0x64]
08012b86: ldr      r2, [r1, #0x1c]
08012b88: orr      r2, r2, #0x10
08012b8c: str      r2, [r1, #0x1c]
08012b8e: movs     r2, #0x10
08012b90: str      r2, [r3, #0xc]
08012b92: ldr      r2, [r3, #0xc]
08012b94: lsls     r0, r2, #0x1a
08012b96: bpl      #0x8012ba6
08012b98: ldr      r1, [pc, #0x50]
08012b9a: ldr      r2, [r1, #0x1c]
08012b9c: orr      r2, r2, #8
08012ba0: str      r2, [r1, #0x1c]
08012ba2: movs     r2, #0x20
08012ba4: str      r2, [r3, #0xc]
08012ba6: ldr      r3, [pc, #0x40]
08012ba8: ldr      r2, [r3, #0xc]
08012baa: lsls     r1, r2, #0x19
08012bac: bpl      #0x8012bbc
08012bae: ldr      r1, [pc, #0x3c]
08012bb0: ldr      r2, [r1, #0x1c]
08012bb2: orr      r2, r2, #4
08012bb6: str      r2, [r1, #0x1c]
08012bb8: movs     r2, #0x40
08012bba: str      r2, [r3, #0xc]
08012bbc: ldr      r2, [r3, #0xc]
08012bbe: lsls     r2, r2, #0x18
08012bc0: bpl      #0x8012bd0
08012bc2: ldr      r1, [pc, #0x28]
08012bc4: ldr      r2, [r1, #0x1c]
08012bc6: orr      r2, r2, #2
08012bca: str      r2, [r1, #0x1c]
08012bcc: movs     r2, #0x80
08012bce: str      r2, [r3, #0xc]
08012bd0: ldr      r2, [pc, #0x14]
08012bd2: ldr      r3, [r2, #0xc]
08012bd4: lsls     r3, r3, #0x1e
08012bd6: bpl      #0x8012be6
08012bd8: ldr      r1, [pc, #0x10]
08012bda: ldr      r3, [r1, #0x1c]
08012bdc: orr      r3, r3, #0x20
08012be0: str      r3, [r1, #0x1c]
08012be2: movs     r3, #2
08012be4: str      r3, [r2, #0xc]
08012be6: bx       lr
08012be8: subs     r4, #0
08012bea: ands     r2, r0
08012bec: ldr      r0, [r1, #0x5c]
08012bee: movs     r0, #0
08012bf0: ldr      r3, [pc, #0x18]
08012bf2: ldr      r2, [r3, #0x10]
08012bf4: cmp      r2, #0
08012bf6: itttt    lt
08012bf8: ldrlt    r2, [pc, #0x14]
08012bfa: strlt    r2, [r3, #4]
08012bfc: addlt.w  r2, r2, #-0x77777778
08012c00: strlt    r2, [r3, #4]
08012c02: itte     lt
08012c04: ldrlt    r0, [r3, #0x10]
08012c06: lsrlt    r0, r0, #0x1f
08012c08: movge    r0, #0
08012c0a: bx       lr
08012c0c: subs     r4, #0
08012c0e: ands     r2, r0
08012c10: lsls     r3, r4, #4
08012c12: cmp      r7, ip
08012c14: ldr      r2, [pc, #0xc]
08012c16: ldr      r3, [r2, #0x10]
08012c18: orr      r3, r3, #0x80000000
08012c1c: str      r3, [r2, #0x10]
08012c1e: movs     r0, #0
08012c20: bx       lr
08012c22: nop      
08012c24: subs     r4, #0
08012c26: ands     r2, r0
08012c28: push     {r3, r4, r5, r6, r7, lr}
08012c2a: ldr      r3, [pc, #0x48]
08012c2c: ldr      r5, [pc, #0x48]
08012c2e: movs     r2, #0
08012c30: mov      r4, r0
08012c32: str      r2, [r3, #0x1c]
08012c34: bl       #0x8011f40
08012c38: mov      r7, r5
08012c3a: mov      r6, r0
08012c3c: ldr      r3, [r5, #0xc]
08012c3e: lsls     r2, r3, #0xf
08012c40: bmi      #0x8012c5c
08012c42: ldr      r3, [r5, #0xc]
08012c44: lsls     r3, r3, #0x1f
08012c46: itt      mi
08012c48: movmi    r3, #1
08012c4a: strmi    r3, [r5, #0xc]
08012c4c: ldr      r0, [r7, #0xc]
08012c4e: ands     r0, r0, #0xf2
08012c52: beq      #0x8012c64
08012c54: bl       #0x8012b7c
08012c58: movs     r0, #1
08012c5a: b        #0x8012c64
08012c5c: adds     r1, r4, #1
08012c5e: beq      #0x8012c3c
08012c60: cbnz     r4, #0x8012c66
08012c62: movs     r0, #3
08012c64: pop      {r3, r4, r5, r6, r7, pc}
08012c66: bl       #0x8011f40
08012c6a: subs     r0, r0, r6
08012c6c: cmp      r0, r4
08012c6e: bls      #0x8012c3c
08012c70: b        #0x8012c62
08012c72: nop      
08012c74: ldr      r0, [r1, #0x5c]
08012c76: movs     r0, #0
08012c78: subs     r4, #0
08012c7a: ands     r2, r0
08012c7c: push     {r0, r1, r2, r4, r5, r6, r7, lr}
08012c7e: ldr      r6, [pc, #0x80]
08012c80: str      r3, [sp, #4]
08012c82: mov      r4, r2
08012c84: ldrb     r2, [r6, #0x18]
08012c86: cmp      r2, #1
08012c88: mov      r7, r0
08012c8a: mov      r5, r1
08012c8c: beq      #0x8012cfa
08012c8e: movs     r2, #1
08012c90: movw     r0, #0xc350
08012c94: strb     r2, [r6, #0x18]
08012c96: bl       #0x8012c28
08012c9a: cbnz     r0, #0x8012ccc
08012c9c: ldr      r3, [sp, #4]
08012c9e: cbnz     r7, #0x8012cd4
08012ca0: ldr      r3, [pc, #0x60]
08012ca2: ldr      r0, [r3, #0x10]
08012ca4: bic      r0, r0, #0x300
08012ca8: str      r0, [r3, #0x10]
08012caa: ldr      r2, [r3, #0x10]
08012cac: str      r2, [r3, #0x10]
08012cae: ldr      r0, [r3, #0x10]
08012cb0: uxtb     r4, r4
08012cb2: orr      r0, r0, #1
08012cb6: str      r0, [r3, #0x10]
08012cb8: strb     r4, [r5]
08012cba: movw     r0, #0xc350
08012cbe: bl       #0x8012c28
08012cc2: ldr      r2, [pc, #0x40]
08012cc4: ldr      r3, [r2, #0x10]
08012cc6: bic      r3, r3, #1
08012cca: str      r3, [r2, #0x10]
08012ccc: movs     r3, #0
08012cce: strb     r3, [r6, #0x18]
08012cd0: add      sp, #0xc
08012cd2: pop      {r4, r5, r6, r7, pc}
08012cd4: cmp      r7, #1
08012cd6: bne      #0x8012ce2
08012cd8: uxth     r1, r4
08012cda: mov      r0, r5
08012cdc: bl       #0x8012b58
08012ce0: b        #0x8012cba
08012ce2: cmp      r7, #2
08012ce4: bne      #0x8012cf0
08012ce6: mov      r1, r4
08012ce8: mov      r0, r5
08012cea: bl       #0x8012b34
08012cee: b        #0x8012cba
08012cf0: mov      r2, r4
08012cf2: mov      r0, r5
08012cf4: bl       #0x8012b0c
08012cf8: b        #0x8012cba
08012cfa: movs     r0, #2
08012cfc: b        #0x8012cd0
08012cfe: nop      
08012d00: ldr      r0, [r1, #0x5c]
08012d02: movs     r0, #0
08012d04: subs     r4, #0
08012d06: ands     r2, r0
08012d08: ldr      r3, [pc, #0x1c]
08012d0a: ldr      r1, [r3, #0x10]
08012d0c: bic      r1, r1, #0x300
08012d10: str      r1, [r3, #0x10]
08012d12: ldr      r1, [r3, #0x10]
08012d14: orr      r1, r1, #4
08012d18: str      r1, [r3, #0x10]
08012d1a: ldr      r2, [r3, #0x10]
08012d1c: orr.w    r0, r2, r0, lsl #8
08012d20: orr      r0, r0, #0x10000
08012d24: str      r0, [r3, #0x10]
08012d26: bx       lr
08012d28: subs     r4, #0
08012d2a: ands     r2, r0
08012d2c: cbz      r1, #0x8012d3e
08012d2e: cmp      r1, #1
08012d30: beq      #0x8012d6c
08012d32: cmp      r1, #2
08012d34: ite      eq
08012d36: moveq.w  r1, #0x200
08012d3a: movne.w  r1, #0x300
08012d3e: ldr      r3, [pc, #0x34]
08012d40: ldr      r2, [r3, #0x10]
08012d42: bic      r2, r2, #0x300
08012d46: str      r2, [r3, #0x10]
08012d48: ldr      r2, [r3, #0x10]
08012d4a: orrs     r1, r2
08012d4c: str      r1, [r3, #0x10]
08012d4e: ldr      r2, [r3, #0x10]
08012d50: bic      r2, r2, #0xf8
08012d54: str      r2, [r3, #0x10]
08012d56: ldr      r2, [r3, #0x10]
08012d58: orr.w    r0, r2, r0, lsl #3
08012d5c: orr      r0, r0, #2
08012d60: str      r0, [r3, #0x10]
08012d62: ldr      r2, [r3, #0x10]
08012d64: orr      r2, r2, #0x10000
08012d68: str      r2, [r3, #0x10]
08012d6a: bx       lr
08012d6c: mov.w    r1, #0x100
08012d70: b        #0x8012d3e
08012d72: nop      
08012d74: subs     r4, #0
08012d76: ands     r2, r0
08012d78: ldr      r3, [pc, #0x50]
08012d7a: ldr      r2, [r3]
08012d7c: lsls     r1, r2, #0x16
08012d7e: bpl      #0x8012da0
08012d80: ldr      r2, [r3]
08012d82: bic      r2, r2, #0x200
08012d86: str      r2, [r3]
08012d88: ldr      r2, [r3]
08012d8a: orr      r2, r2, #0x800
08012d8e: str      r2, [r3]
08012d90: ldr      r2, [r3]
08012d92: bic      r2, r2, #0x800
08012d96: str      r2, [r3]
08012d98: ldr      r2, [r3]
08012d9a: orr      r2, r2, #0x200
08012d9e: str      r2, [r3]
08012da0: ldr      r3, [pc, #0x28]
08012da2: ldr      r2, [r3]
08012da4: lsls     r2, r2, #0x15
08012da6: bpl      #0x8012dc8
08012da8: ldr      r2, [r3]
08012daa: bic      r2, r2, #0x400
08012dae: str      r2, [r3]
08012db0: ldr      r2, [r3]
08012db2: orr      r2, r2, #0x1000
08012db6: str      r2, [r3]
08012db8: ldr      r2, [r3]
08012dba: bic      r2, r2, #0x1000
08012dbe: str      r2, [r3]
08012dc0: ldr      r2, [r3]
08012dc2: orr      r2, r2, #0x400
08012dc6: str      r2, [r3]
08012dc8: bx       lr
08012dca: nop      
08012dcc: subs     r4, #0
08012dce: ands     r2, r0
08012dd0: push.w   {r3, r4, r5, r6, r7, r8, sb, lr}
08012dd4: ldr      r6, [pc, #0x8c]
08012dd6: ldrb     r3, [r6, #0x18]
08012dd8: cmp      r3, #1
08012dda: mov      r5, r0
08012ddc: mov      r8, r1
08012dde: beq      #0x8012e60
08012de0: movs     r3, #1
08012de2: movw     r0, #0xc350
08012de6: strb     r3, [r6, #0x18]
08012de8: bl       #0x8012c28
08012dec: mov      r4, r0
08012dee: cbnz     r0, #0x8012e1c
08012df0: mov.w    r3, #-1
08012df4: str.w    r3, [r8]
08012df8: ldr      r3, [r5]
08012dfa: cmp      r3, #1
08012dfc: bne      #0x8012e26
08012dfe: ldrb     r0, [r5, #0x10]
08012e00: bl       #0x8012d08
08012e04: movw     r0, #0xc350
08012e08: bl       #0x8012c28
08012e0c: ldr      r2, [pc, #0x58]
08012e0e: ldr      r3, [r2, #0x10]
08012e10: bic      r3, r3, #4
08012e14: mov      r4, r0
08012e16: str      r3, [r2, #0x10]
08012e18: bl       #0x8012d78
08012e1c: movs     r3, #0
08012e1e: strb     r3, [r6, #0x18]
08012e20: mov      r0, r4
08012e22: pop.w    {r3, r4, r5, r6, r7, r8, sb, pc}
08012e26: ldr      r7, [r5, #8]
08012e28: ldr.w    sb, [pc, #0x3c]
08012e2c: ldrd     r2, r3, [r5, #8]
08012e30: add      r3, r2
08012e32: cmp      r3, r7
08012e34: bls      #0x8012e18
08012e36: ldrb     r1, [r5, #0x10]
08012e38: mov      r0, r7
08012e3a: bl       #0x8012d2c
08012e3e: movw     r0, #0xc350
08012e42: bl       #0x8012c28
08012e46: ldr.w    r3, [sb, #0x10]
08012e4a: bic      r3, r3, #0xfa
08012e4e: str.w    r3, [sb, #0x10]
08012e52: cbz      r0, #0x8012e5c
08012e54: str.w    r7, [r8]
08012e58: mov      r4, r0
08012e5a: b        #0x8012e18
08012e5c: adds     r7, #1
08012e5e: b        #0x8012e2c
08012e60: movs     r4, #2
08012e62: b        #0x8012e20
08012e64: ldr      r0, [r1, #0x5c]
08012e66: movs     r0, #0
08012e68: subs     r4, #0
08012e6a: ands     r2, r0
08012e6c: push.w   {r4, r5, r6, r7, r8, sb, sl, fp, lr}
08012e70: ldr      r2, [pc, #0x1b8]
08012e72: ldr.w    r8, [pc, #0x1c0]
08012e76: ldr.w    sb, [pc, #0x1c0]
08012e7a: sub      sp, #0x14
08012e7c: movs     r3, #0
08012e7e: ldr      r4, [r1]
