08005b4c: movs     r4, #0
08005b4e: bl       #0x8000f58
08005b52: bl       #0x8002df4
08005b56: bl       #0x8002718
08005b5a: bl       #0x80003d0
08005b5e: bl       #0x80028c4
08005b62: bl       #0x8002818
08005b66: bl       #0x80027e0
08005b6a: bl       #0x8002980
08005b6e: bl       #0x800036a
08005b72: cbz      r0, #0x8005b76
08005b74: b        #0x8005be6
08005b76: movs     r4, #0
08005b78: b        #0x8005bae
08005b7a: movs     r0, #0x64
08005b7c: bl       #0x8000a30
08005b80: ldr      r0, [pc, #0x8c] ; [0x08005c10]=0x20000020
08005b82: ldrb     r0, [r0]
08005b84: cmp      r0, #2
08005b86: beq      #0x8005b90
08005b88: ldr      r0, [pc, #0x88] ; [0x08005c14]=0x2000008c
08005b8a: ldr      r0, [r0]
08005b8c: cmp      r0, #2
08005b8e: bne      #0x8005bac
08005b90: ldr      r0, [pc, #0x7c] ; [0x08005c10]=0x20000020
08005b92: ldrb     r0, [r0]
08005b94: cmp      r0, #2
08005b96: bne      #0x8005b9e
08005b98: movs     r0, #1
08005b9a: ldr      r1, [pc, #0x7c] ; [0x08005c18]=0x20000010
08005b9c: strb     r0, [r1]
08005b9e: ldr      r0, [pc, #0x74] ; [0x08005c14]=0x2000008c
08005ba0: ldr      r0, [r0]
08005ba2: cmp      r0, #2
08005ba4: bne      #0x8005baa
08005ba6: ldr      r1, [pc, #0x70] ; [0x08005c18]=0x20000010
08005ba8: strb     r0, [r1]
08005baa: b        #0x8005be6
08005bac: adds     r4, r4, #1
08005bae: cmp      r4, #0xa
08005bb0: blt      #0x8005b7a
08005bb2: ldr      r0, [pc, #0x68] ; [0x08005c1c]=0x40023874
08005bb4: ldr      r0, [r0]
08005bb6: ubfx     r0, r0, #0x1c, #1
08005bba: cbz      r0, #0x8005bd6
08005bbc: ldr      r0, [pc, #0x5c] ; [0x08005c1c]=0x40023874
08005bbe: ldr      r0, [r0]
08005bc0: orr      r0, r0, #0x1000000
08005bc4: ldr      r1, [pc, #0x54] ; [0x08005c1c]=0x40023874
08005bc6: str      r0, [r1]
08005bc8: adr      r0, #0x54
08005bca: bl       #0x8006040
08005bce: adr      r0, #0x50
08005bd0: bl       #0x8006590
08005bd4: b        #0x8005be6
08005bd6: ldr      r0, [pc, #0x70] ; [0x08005c48]=0x20000004
08005bd8: ldr      r0, [r0]
08005bda: bl       #0x8005b08
08005bde: adr      r0, #0x6c
08005be0: bl       #0x8006040
08005be4: nop      
08005be6: b        #0x8005c0c
08005be8: ldr      r0, [pc, #0x24] ; [0x08005c10]=0x20000020
08005bea: ldrb     r0, [r0]
08005bec: cbnz     r0, #0x8005bf6
08005bee: ldr      r0, [pc, #0x28] ; [0x08005c18]=0x20000010
08005bf0: ldrb     r0, [r0]
08005bf2: cmp      r0, #1
08005bf4: bne      #0x8005bfa
08005bf6: bl       #0x8005e28
08005bfa: ldr      r0, [pc, #0x18] ; [0x08005c14]=0x2000008c
08005bfc: ldr      r0, [r0]
08005bfe: cbnz     r0, #0x8005c08
08005c00: ldr      r0, [pc, #0x14] ; [0x08005c18]=0x20000010
08005c02: ldrb     r0, [r0]
08005c04: cmp      r0, #2
08005c06: bne      #0x8005c0c
08005c08: bl       #0x8006368
08005c0c: b        #0x8005be8
08005c0e: movs     r0, r0
