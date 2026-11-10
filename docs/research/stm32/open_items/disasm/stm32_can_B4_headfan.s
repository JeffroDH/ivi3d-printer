08019700: push     {r0, r1, r2, lr}
08019702: ldr      r3, [pc, #0x30]
08019704: ldrb     r3, [r3]
08019706: subs     r2, r0, #0
08019708: it       ne
0801970a: movne    r2, #1
0801970c: subs     r3, #0
0801970e: it       ne
08019710: movne    r3, #1
08019712: cmp      r2, r3
08019714: beq      #0x801972e
08019716: movs     r3, #0
08019718: strd     r3, r3, [sp]
0801971c: movs     r1, #2
0801971e: movs     r3, #0xb4
08019720: strb.w   r0, [sp, #1]
08019724: mov      r0, sp
08019726: strb.w   r3, [sp]
0801972a: bl       #0x80192f4
0801972e: add      sp, #0xc
08019730: ldr      pc, [sp], #4
08019734: asrs     r1, r6, #0xc
08019736: movs     r0, #0
