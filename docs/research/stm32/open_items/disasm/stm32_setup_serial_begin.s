0801ac80: push     {r4, r5, lr}
0801ac82: ldr      r0, [pc, #0x1c0]
0801ac84: ldr      r5, [pc, #0x1c0]
0801ac86: sub      sp, #0x14
0801ac88: bl       #0x8026650
0801ac8c: ldr      r0, [pc, #0x1b8]
0801ac8e: mov.w    r1, #0x1c200
0801ac92: bl       #0x8011d20
0801ac96: bl       #0x80190e4
0801ac9a: add.w    r4, r0, #0x3e8
0801ac9e: mov      r0, r5
0801aca0: bl       #0x8011d28
0801aca4: cbnz     r0, #0x801acb0
0801aca6: bl       #0x80190e4
0801acaa: subs     r0, r0, r4
0801acac: cmp      r0, #0
0801acae: blt      #0x801ac9e
0801acb0: movs     r2, #6
0801acb2: mov.w    r1, #0x1c200
0801acb6: ldr      r0, [pc, #0x194]
0801acb8: bl       #0x8019914
0801acbc: bl       #0x80190e4
