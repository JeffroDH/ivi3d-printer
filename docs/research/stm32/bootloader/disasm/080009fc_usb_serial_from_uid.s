080009fc: push     {r4, r5, r6, lr}
080009fe: ldr      r0, [pc, #0x28] ; [0x08000a28]=0x1fff7a10
08000a00: ldr      r4, [r0]
08000a02: adds     r0, r0, #4
08000a04: ldr      r5, [r0]
08000a06: adds     r0, r0, #4
08000a08: ldr      r6, [r0]
08000a0a: add      r4, r6
08000a0c: cbz      r4, #0x8000a24
08000a0e: movs     r2, #8
08000a10: ldr      r1, [pc, #0x18] ; [0x08000a2c]=0x2000005a
08000a12: mov      r0, r4
08000a14: bl       #0x8002238
08000a18: movs     r2, #4
08000a1a: ldr      r1, [pc, #0x10] ; [0x08000a2c]=0x2000005a
08000a1c: adds     r1, #0x10
08000a1e: mov      r0, r5
08000a20: bl       #0x8002238
08000a24: pop      {r4, r5, r6, pc}
08000a26: movs     r0, r0
08000a28: ldrb     r0, [r2, #8]
08000a2a: subs     r7, r7, #7
08000a2c: lsls     r2, r3, #1
08000a2e: movs     r0, #0
