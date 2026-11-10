00038880: add r1, pc, r1
00038884: bl #0x44578
00038888: mov r2, #0x66
0003888c: mov r3, #3
00038890: add r6, sp, #0x12c
00038894: stm sp, {r2, r3}
00038898: mov r0, r6
0003889c: ldr r2, [pc, #0x868]
000388a0: ldr r3, [pc, #0x868]
000388a4: bl #0x142ec
000388a8: ldr r2, [sp, #0x12c]
000388ac: ldr r3, [r4, #0x90]
000388b0: mov r0, r6
000388b4: str r2, [r4, #0x90]
000388b8: str r3, [sp, #0x12c]
000388bc: bl #0x14ef4
