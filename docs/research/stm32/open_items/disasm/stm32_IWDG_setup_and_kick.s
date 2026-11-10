0801a6a4: ldr      r2, [pc, #8]
0801a6a6: ldr      r1, [pc, #0xc]
0801a6a8: ldr      r0, [pc, #0xc]
0801a6aa: b.w      #0x802fca0
0801a6ae: nop      
0801a6b0: b        #0x801a834
0801a6b2: lsls     r3, r6, #7
0801a6b4: asrs     r0, r0, #8
0801a6b6: lsls     r2, r7, #1
0801a6b8: ldr      r0, [r7, #0x58]
0801a6ba: movs     r0, #0
0801a6bc: push     {r3, lr}
0801a6be: ldr      r0, [pc, #0x24]
0801a6c0: bl       #0x802fce8
0801a6c4: ldr      r3, [pc, #0x20]
0801a6c6: ldr      r2, [pc, #0x24]
0801a6c8: ldrsh.w  r3, [r3, #0x3a]
0801a6cc: ubfx     r1, r3, #4, #4
