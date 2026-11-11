08000a58: push.w   {r4, r5, r6, r7, r8, lr}
08000a5c: mov      r4, r0
08000a5e: mov      r6, r1
08000a60: movs     r7, #1
08000a62: movs     r5, #0
08000a64: nop      
08000a66: ldr      r0, [pc, #0x94] ; [0x08000afc]=0x20001ed4
08000a68: ldrb     r0, [r0, #0x18]
08000a6a: cmp      r0, #1
08000a6c: bne      #0x8000a74
08000a6e: movs     r0, #2
08000a70: pop.w    {r4, r5, r6, r7, r8, pc}
08000a74: movs     r0, #1
08000a76: ldr      r1, [pc, #0x84] ; [0x08000afc]=0x20001ed4
08000a78: strb     r0, [r1, #0x18]
08000a7a: nop      
08000a7c: movw     r0, #0xc350
08000a80: bl       #0x80008f0
08000a84: mov      r7, r0
08000a86: cmp      r7, #0
08000a88: bne      #0x8000aee
08000a8a: subs     r0, r0, #1
08000a8c: str      r0, [r6]
08000a8e: ldr      r0, [r4]
08000a90: cmp      r0, #1
08000a92: bne      #0x8000ab4
08000a94: ldrb     r0, [r4, #0x10]
08000a96: ldr      r1, [r4, #4]
08000a98: bl       #0x8000778
08000a9c: movw     r0, #0xc350
08000aa0: bl       #0x80008f0
08000aa4: mov      r7, r0
08000aa6: ldr      r0, [pc, #0x58] ; [0x08000b00]=0x40023c10
08000aa8: ldr      r0, [r0]
08000aaa: bic      r0, r0, #4
08000aae: ldr      r1, [pc, #0x50] ; [0x08000b00]=0x40023c10
08000ab0: str      r0, [r1]
08000ab2: b        #0x8000aea
08000ab4: ldr      r5, [r4, #8]
08000ab6: b        #0x8000ade
08000ab8: ldrb     r1, [r4, #0x10]
08000aba: mov      r0, r5
08000abc: bl       #0x80006a4
08000ac0: movw     r0, #0xc350
08000ac4: bl       #0x80008f0
08000ac8: mov      r7, r0
08000aca: ldr      r0, [pc, #0x34] ; [0x08000b00]=0x40023c10
08000acc: ldr      r0, [r0]
08000ace: bic      r0, r0, #0xfa
08000ad2: ldr      r1, [pc, #0x2c] ; [0x08000b00]=0x40023c10
08000ad4: str      r0, [r1]
08000ad6: cbz      r7, #0x8000adc
08000ad8: str      r5, [r6]
08000ada: b        #0x8000ae8
08000adc: adds     r5, r5, #1
08000ade: ldrd     r1, r0, [r4, #8]
08000ae2: add      r0, r1
08000ae4: cmp      r0, r5
08000ae6: bhi      #0x8000ab8
08000ae8: nop      
08000aea: bl       #0x8000700
08000aee: nop      
08000af0: movs     r0, #0
08000af2: ldr      r1, [pc, #8] ; [0x08000afc]=0x20001ed4
08000af4: strb     r0, [r1, #0x18]
08000af6: nop      
08000af8: mov      r0, r7
08000afa: b        #0x8000a70
08000afc: subs     r4, r2, #3
08000afe: movs     r0, #0
08000b00: subs     r4, #0x10
08000b02: ands     r2, r0
