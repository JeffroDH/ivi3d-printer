; A33 GlobalFuntions::upgradeFirmwareProcess @0x28814 + Sender::ChangeToUpdateMode @0x22cf8 — sleep 100 ms, Sender sends line 'M997' (literal resolved), Sender::closePort, start Work thread
; source: app.elf
; tool: Capstone 5.0.7 (single tool; cross-checked only against the existing Ghidra 12.x decompile in ivi_fwaudit/out/app.c or ivi/supx_decomp.c)

00028814: push {r4, r5, r6, r7, r8, sb, sl, fp, lr}
00028818: ldr r3, [pc, #0x1a4]
0002881c: sub sp, sp, #0x54
00028820: ldr r1, [pc, #0x1a0]
00028824: add r8, sp, #0x3c
00028828: mov r4, #0
0002882c: mov r5, r0
00028830: mov r2, #2
00028834: add r3, pc, r3
00028838: add r1, pc, r1
0002883c: mov r0, r8
00028840: str r2, [sp, #0x3c]
00028844: str r3, [sp, #0x4c]
00028848: str r4, [sp, #0x40]
0002884c: str r4, [sp, #0x44]
00028850: str r4, [sp, #0x48]
00028854: bl #0x1386c
00028858: mov r0, #0x64
0002885c: bl #0x139d4
00028860: ldr r0, [r5, #0x3c]
00028864: bl #0x22cf8
00028868: ldr r6, [pc, #0x15c]
0002886c: ldr r0, [r5, #0x3c]
00028870: bl #0x1f958
00028874: ldr r2, [pc, #0x154]
00028878: add r6, pc, r6
0002887c: ldr r3, [pc, #0x150]
00028880: ldr r2, [r6, r2]
00028884: str r2, [sp, #0x24]
00028888: str r4, [sp, #0x28]
0002888c: mov r0, #0x10
00028890: ldr r3, [r6, r3]
00028894: ldr r7, [r5, #0x4c]
00028898: str r3, [sp, #0x2c]
0002889c: str r4, [sp, #0x30]
000288a0: bl #0x13b60
000288a4: ldr ip, [pc, #0x12c]
000288a8: ldr r2, [sp, #0x30]
000288ac: mov sb, #1
000288b0: ldr r3, [pc, #0x124]
000288b4: ldr r1, [sp, #0x2c]
000288b8: str sb, [r0]
000288bc: ldr fp, [r6, ip]
000288c0: str r2, [r0, #0xc]
000288c4: add r2, sp, #0x2c
000288c8: str r1, [r0, #8]
000288cc: str fp, [r0, #4]
000288d0: stmib sp, {r0, r4}
000288d4: str r2, [sp]
000288d8: str r4, [sp, #0xc]
000288dc: ldr r3, [r6, r3]
000288e0: mov r1, r7
000288e4: add r2, sp, #0x24
000288e8: str r3, [sp, #0x1c]
000288ec: str r3, [sp, #0x10]
000288f0: mov r0, r8
000288f4: mov r3, r5
000288f8: bl #0x136ec
000288fc: mov r0, r8
00028900: bl #0x13b30
00028904: ldr r2, [pc, #0xd4]
00028908: ldr r3, [pc, #0xd4]
0002890c: ldr r2, [r6, r2]
00028910: str r2, [sp, #0x34]
00028914: str r4, [sp, #0x38]
00028918: mov r0, #0x10
0002891c: ldr r3, [r6, r3]
00028920: ldr sl, [r5, #0x4c]
00028924: str r3, [sp, #0x3c]
00028928: str r4, [sp, #0x40]
0002892c: bl #0x13b60
00028930: ldr r2, [sp, #0x3c]
00028934: ldr r3, [sp, #0x40]
00028938: add r7, sp, #0x20
0002893c: mov r1, sl
00028940: str r2, [r0, #8]
00028944: ldr r2, [sp, #0x1c]
00028948: str r3, [r0, #0xc]
0002894c: stm r0, {sb, fp}
00028950: mov r3, r5
00028954: str r2, [sp, #0x10]
00028958: stmib sp, {r0, r4}
0002895c: add r2, sp, #0x34
00028960: mov r0, r7
00028964: str r8, [sp]
00028968: str r4, [sp, #0xc]
0002896c: bl #0x136ec
00028970: mov r0, r7
00028974: bl #0x13b30
00028978: ldr r0, [r5, #0x1c0]
0002897c: str r0, [sp, #0x20]
00028980: ldr r3, [r0]
00028984: cmp r3, r4
00028988: beq #0x2899c
0002898c: cmn r3, #1
00028990: beq #0x2899c
00028994: mov r1, sb
00028998: bl #0x5316c
0002899c: mov r0, r5
000289a0: mov r1, r7
000289a4: bl #0x4af90
000289a8: mov r0, r7
000289ac: bl #0x14ef4
000289b0: add sp, sp, #0x54
000289b4: pop {r4, r5, r6, r7, r8, sb, sl, fp, pc}
000289b8: mov r0, r7
000289bc: bl #0x14ef4
000289c0: bl #0x14040
000289c4: muleq r2, r8, r3
000289c8: andeq fp, r2, r4, lsl #27
000289cc: muleq r8, r8, lr
000289d0: andeq r0, r0, r8, lsl #18
000289d4: andeq r0, r0, ip, lsr #16
000289d8: strdeq r0, r1, [r0], -r8
000289dc: andeq r0, r0, r8, lsr #17
000289e0: andeq r0, r0, ip, asr r5
000289e4: strheq r0, [r0], -r8

00022cf8: push {r4, r5, lr}
00022cfc: mov r1, #3
00022d00: sub sp, sp, #0xc
00022d04: mov r5, r0
00022d08: ldr r0, [r0, #0xc]
00022d0c: bl #0x13dc4
00022d10: ldr r0, [pc, #0x70]
00022d14: mov r1, #4
00022d18: add r0, pc, r0
00022d1c: bl #0x14358
00022d20: add r4, sp, #8
00022d24: str r0, [r4, #-4]!
00022d28: mov r0, r5
00022d2c: mov r1, r4
00022d30: bl #0x22b38
00022d34: ldr r0, [sp, #4]
00022d38: ldr r3, [r0]
00022d3c: cmp r3, #0
00022d40: beq #0x22d68
00022d44: cmn r3, #1
00022d48: beq #0x22d60
00022d4c: mov r1, #1
00022d50: bl #0x531a4
00022d54: cmp r0, #0
00022d58: ldreq r0, [sp, #4]
00022d5c: beq #0x22d68
00022d60: add sp, sp, #0xc
00022d64: pop {r4, r5, pc}
00022d68: mov r1, #2
00022d6c: mov r2, #4
00022d70: bl #0x13da0
00022d74: add sp, sp, #0xc
00022d78: pop {r4, r5, pc}
00022d7c: mov r0, r4
00022d80: bl #0x14ef4
00022d84: bl #0x14040
00022d88: strheq r1, [r3], -ip
