; A33 Work::jumpToApp @0x4625c — builds A4 02 AA AA AA AA + CRC16/XMODEM(LE) and writes the 8 bytes twice
; source: app.elf
; tool: Capstone 5.0.7 (single tool; cross-checked only against the existing Ghidra 12.x decompile in ivi_fwaudit/out/app.c or ivi/supx_decomp.c)

0004625c: push {r4, r5, r6, r7, lr}
00046260: sub sp, sp, #0x2c
00046264: mov lr, #0
00046268: add r6, sp, #8
0004626c: mvn r2, #0x55
00046270: mov r5, r0
00046274: mvn r7, #0x5b
00046278: mov r4, #2
0004627c: mov ip, lr
00046280: mov r1, r6
00046284: add r0, sp, #0xd
00046288: mov r3, #0xa4
0004628c: str lr, [sp, #0xc]
00046290: str lr, [sp, #0x10]
00046294: strb r7, [sp, #8]
00046298: strb r4, [sp, #9]
0004629c: strb r2, [sp, #0xa]
000462a0: strb r2, [sp, #0xb]
000462a4: strb r2, [sp, #0xc]
000462a8: strb r2, [sp, #0xd]
000462ac: eor ip, ip, r3, lsl #8
000462b0: mov r4, #8
000462b4: lsl r2, ip, #0x10
000462b8: asrs r2, r2, #0x10
000462bc: lsl r2, r2, #0x11
000462c0: eormi ip, r2, #0x10000000
000462c4: eormi ip, ip, #0x210000
000462c8: sub r3, r4, #1
000462cc: lsrmi ip, ip, #0x10
000462d0: lsrpl ip, r2, #0x10
000462d4: ands r4, r3, #0xff
000462d8: bne #0x462b4
000462dc: cmp r1, r0
000462e0: ldrbne r3, [r1, #1]!
000462e4: bne #0x462ac
000462e8: lsr lr, ip, #8
000462ec: mov r2, #8
000462f0: mov r3, #0
000462f4: ldr r0, [r5, #0x3c]
000462f8: mov r1, r6
000462fc: strb ip, [sp, #0xe]
00046300: strb lr, [sp, #0xf]
00046304: bl #0x140dc
00046308: ldr r0, [r5, #0x3c]
0004630c: bl #0x1425c
00046310: mov r2, #8
00046314: mov r3, #0
00046318: ldr r0, [r5, #0x3c]
0004631c: mov r1, r6
00046320: bl #0x140dc
00046324: ldr r0, [r5, #0x3c]
00046328: bl #0x1425c
0004632c: ldr r3, [pc, #0xe4]
00046330: mov r2, #2
00046334: mov r0, sp
00046338: add r3, pc, r3
0004633c: add r1, sp, #0x14
00046340: str r4, [sp, #0x18]
00046344: str r4, [sp, #0x1c]
00046348: str r4, [sp, #0x20]
0004634c: str r2, [sp, #0x14]
00046350: str r3, [sp, #0x24]
00046354: bl #0x13c68
00046358: ldr r1, [pc, #0xbc]
0004635c: add r5, sp, #4
00046360: mov r0, r5
00046364: add r1, pc, r1
00046368: mov r2, #0xc
0004636c: ldr r4, [sp]
00046370: bl #0x14298
00046374: mov r0, r4
00046378: mov r1, r5
0004637c: bl #0x13674
00046380: ldr r0, [sp, #4]
00046384: ldr r3, [r0]
00046388: cmp r3, #0
0004638c: beq #0x463cc
00046390: cmn r3, #1
00046394: beq #0x463ac
00046398: mov r1, #1
0004639c: bl #0x531a4
000463a0: cmp r0, #0
000463a4: ldreq r0, [sp, #4]
000463a8: beq #0x463cc
000463ac: ldr r0, [sp]
000463b0: ldrb r3, [r0, #0x14]
000463b4: cmp r3, #0
000463b8: bne #0x463e8
000463bc: mov r0, sp
000463c0: bl #0x14364
000463c4: add sp, sp, #0x2c
000463c8: pop {r4, r5, r6, r7, pc}
000463cc: mov r1, #2
000463d0: mov r2, #4
000463d4: bl #0x13da0
000463d8: ldr r0, [sp]
000463dc: ldrb r3, [r0, #0x14]
000463e0: cmp r3, #0
000463e4: beq #0x463bc
000463e8: mov r1, #0x20
000463ec: bl #0x13974
000463f0: mov r0, sp
000463f4: bl #0x14364
000463f8: add sp, sp, #0x2c
000463fc: pop {r4, r5, r6, r7, pc}
00046400: mov r0, r5
00046404: bl #0x14ef4
00046408: mov r0, sp
0004640c: bl #0x14364
00046410: bl #0x14040
00046414: b #0x46408
00046418: muleq r0, r4, r8
0004641c: andeq pc, r0, r0, lsl #9
