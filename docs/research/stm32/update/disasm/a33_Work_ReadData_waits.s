; A33 Work::ReadData/wait_* @0x46758..0x46aec — accumulate bytes via waitForReadyRead(10); parse only when exactly 5 bytes
; source: app.elf
; tool: Capstone 5.0.7 (single tool; cross-checked only against the existing Ghidra 12.x decompile in ivi_fwaudit/out/app.c or ivi/supx_decomp.c)

00046758: push {r4, r5, r6, lr}
0004675c: sub sp, sp, #0x18
00046760: ldr r1, [r0, #0x3c]
00046764: mov r4, r0
00046768: mov r0, sp
0004676c: bl #0x14100
00046770: add r5, sp, #4
00046774: ldr r0, [r4, #0x3c]
00046778: mov r1, #0xa
0004677c: ldr r2, [r0]
00046780: ldr r3, [r2, #0x5c]
00046784: blx r3
00046788: subs r3, r0, #0
0004678c: beq #0x467e4
00046790: mov r0, r5
00046794: ldr r1, [r4, #0x3c]
00046798: bl #0x14100
0004679c: mov r0, sp
000467a0: mov r1, r5
000467a4: bl #0x141cc
000467a8: ldr r0, [sp, #4]
000467ac: ldr r2, [r0]
000467b0: cmp r2, #0
000467b4: beq #0x467d4
000467b8: cmn r2, #1
000467bc: beq #0x46774
000467c0: mov r1, #1
000467c4: bl #0x531a4
000467c8: cmp r0, #0
000467cc: bne #0x46774
000467d0: ldr r0, [sp, #4]
000467d4: mov r1, #1
000467d8: mov r2, #4
000467dc: bl #0x13da0
000467e0: b #0x46774
000467e4: ldr r0, [sp]
000467e8: ldr r2, [r0, #4]
000467ec: cmp r2, #0
000467f0: beq #0x4683c
000467f4: cmp r2, #4
000467f8: mov lr, #2
000467fc: ble #0x4686c
00046800: ldr ip, [pc, #0x130]
00046804: ldr r1, [pc, #0x130]
00046808: add ip, pc, ip
0004680c: add r0, sp, #4
00046810: add r1, pc, r1
00046814: str r3, [sp, #8]
00046818: str r3, [sp, #0xc]
0004681c: str r3, [sp, #0x10]
00046820: str lr, [sp, #4]
00046824: str ip, [sp, #0x14]
00046828: bl #0x1386c
0004682c: ldr r0, [sp]
00046830: ldr r3, [r0, #4]
00046834: cmp r3, #5
00046838: beq #0x468bc
0004683c: ldr r3, [r0]
00046840: cmp r3, #0
00046844: beq #0x468a8
00046848: cmn r3, #1
0004684c: beq #0x46864
00046850: mov r1, #1
00046854: bl #0x531a4
00046858: cmp r0, #0
0004685c: ldreq r0, [sp]
00046860: beq #0x468a8
00046864: add sp, sp, #0x18
00046868: pop {r4, r5, r6, pc}
0004686c: ldr ip, [pc, #0xcc]
00046870: ldr r1, [pc, #0xcc]
00046874: add ip, pc, ip
00046878: add r0, sp, #4
0004687c: add r1, pc, r1
00046880: str r3, [sp, #8]
00046884: str r3, [sp, #0xc]
00046888: str r3, [sp, #0x10]
0004688c: str lr, [sp, #4]
00046890: str ip, [sp, #0x14]
00046894: bl #0x1386c
00046898: ldr r0, [sp]
0004689c: ldr r3, [r0]
000468a0: cmp r3, #0
000468a4: bne #0x46848
000468a8: mov r1, #1
000468ac: mov r2, #4
000468b0: bl #0x13da0
000468b4: add sp, sp, #0x18
000468b8: pop {r4, r5, r6, pc}
000468bc: ldr r3, [r0]
000468c0: cmp r3, #1
000468c4: bls #0x4690c
000468c8: ldr r1, [r0, #4]
000468cc: ldrb r2, [r0, #0xb]
000468d0: add r1, r1, #1
000468d4: lsr r2, r2, #7
000468d8: mov r0, sp
000468dc: bl #0x13cf8
000468e0: ldr r3, [sp]
000468e4: ldr r1, [r3, #0xc]
000468e8: add r1, r3, r1
000468ec: mov r0, r4
000468f0: mov r2, #5
000468f4: bl #0x46420
000468f8: ldr r0, [r4, #0x3c]
000468fc: mov r1, #1
00046900: bl #0x13dc4
00046904: ldr r0, [sp]
00046908: b #0x4683c
0004690c: ldr r1, [r0, #0xc]
00046910: mov r3, r0
00046914: cmp r1, #0x10
00046918: bne #0x468c8
0004691c: b #0x468e8
00046920: mov r0, sp
00046924: bl #0x14e6c
00046928: bl #0x14040
0004692c: mov r0, r5
00046930: bl #0x14e6c
00046934: b #0x46920
00046938: andeq sp, r0, r4, asr #7
0004693c: strheq pc, [r0], -r8
00046940: andeq sp, r0, r8, asr r3
00046944: andeq pc, r0, ip, asr #32
00046948: push {r4, r5, r6, lr}
0004694c: subs r6, r1, #0
00046950: mov r5, r0
00046954: movgt r4, #0
00046958: bgt #0x4696c
0004695c: b #0x46990
00046960: bl #0x139d4
00046964: cmp r4, r6
00046968: beq #0x46990
0004696c: mov r0, r5
00046970: bl #0x46758
00046974: ldrb r3, [r5, #0x46]
00046978: mov r0, #0xa
0004697c: cmp r3, #0
00046980: add r4, r4, #1
00046984: beq #0x46960
00046988: mov r0, r3
0004698c: pop {r4, r5, r6, pc}
00046990: ldrb r3, [r5, #0x46]
00046994: mov r0, r3
00046998: pop {r4, r5, r6, pc}
0004699c: push {r4, r5, r6, lr}
000469a0: subs r6, r1, #0
000469a4: mov r5, r0
000469a8: movgt r4, #0
000469ac: bgt #0x469c0
000469b0: b #0x469e4
000469b4: bl #0x139d4
000469b8: cmp r4, r6
000469bc: beq #0x469e4
000469c0: mov r0, r5
000469c4: bl #0x46758
000469c8: ldrb r3, [r5, #0x47]
000469cc: mov r0, #0xa
000469d0: cmp r3, #0
000469d4: add r4, r4, #1
000469d8: beq #0x469b4
000469dc: mov r0, r3
000469e0: pop {r4, r5, r6, pc}
000469e4: ldrb r3, [r5, #0x47]
000469e8: mov r0, r3
000469ec: pop {r4, r5, r6, pc}
000469f0: push {r4, r5, r6, lr}
000469f4: subs r6, r1, #0
000469f8: mov r5, r0
000469fc: movgt r4, #0
00046a00: bgt #0x46a14
00046a04: b #0x46a38
00046a08: bl #0x139d4
00046a0c: cmp r4, r6
00046a10: beq #0x46a38
00046a14: mov r0, r5
00046a18: bl #0x46758
00046a1c: ldrb r3, [r5, #0x48]
00046a20: mov r0, #0xa
00046a24: cmp r3, #0
00046a28: add r4, r4, #1
00046a2c: beq #0x46a08
00046a30: mov r0, r3
00046a34: pop {r4, r5, r6, pc}
00046a38: ldrb r3, [r5, #0x48]
00046a3c: mov r0, r3
00046a40: pop {r4, r5, r6, pc}
00046a44: push {r4, r5, r6, lr}
00046a48: subs r6, r1, #0
00046a4c: mov r5, r0
00046a50: movgt r4, #0
00046a54: bgt #0x46a68
00046a58: b #0x46a8c
00046a5c: bl #0x139d4
00046a60: cmp r4, r6
00046a64: beq #0x46a8c
00046a68: mov r0, r5
00046a6c: bl #0x46758
00046a70: ldrb r3, [r5, #0x49]
00046a74: mov r0, #0xa
00046a78: cmp r3, #0
00046a7c: add r4, r4, #1
00046a80: beq #0x46a5c
00046a84: mov r0, r3
00046a88: pop {r4, r5, r6, pc}
00046a8c: ldrb r3, [r5, #0x49]
00046a90: mov r0, r3
00046a94: pop {r4, r5, r6, pc}
00046a98: push {r4, r5, r6, lr}
00046a9c: subs r6, r1, #0
00046aa0: mov r5, r0
00046aa4: movgt r4, #0
00046aa8: bgt #0x46abc
00046aac: b #0x46ae0
00046ab0: bl #0x139d4
00046ab4: cmp r4, r6
00046ab8: beq #0x46ae0
00046abc: mov r0, r5
00046ac0: bl #0x46758
00046ac4: ldrb r3, [r5, #0x49]
00046ac8: mov r0, #0xa
00046acc: cmp r3, #0
00046ad0: add r4, r4, #1
00046ad4: beq #0x46ab0
00046ad8: mov r0, r3
00046adc: pop {r4, r5, r6, pc}
00046ae0: ldrb r3, [r5, #0x49]
00046ae4: mov r0, r3
00046ae8: pop {r4, r5, r6, pc}
