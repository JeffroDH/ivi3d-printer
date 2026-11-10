; A33 checkIsFirmwareCanUse fragment @0x41578..0x415f0 — cfNeedUpdate (this+0x1bb) = checkFileMD5(firmware.supx, config2.ini MD5); no controller version compare here
; source: app.elf
; tool: Capstone 5.0.7 (single tool; cross-checked only against the existing Ghidra 12.x decompile in ivi_fwaudit/out/app.c or ivi/supx_decomp.c)

00041300: mov r0, r6
00041304: add r1, pc, r1
00041308: bl #0x14f98
0004130c: ldr r1, [sp, #0x18]
00041310: bl #0x15048
00041314: b #0x410ec
00041318: add r2, sp, #0x4c
0004131c: add r3, sp, #0x48
00041320: str r2, [sp, #0x10]
00041324: str r3, [sp, #0x18]
00041328: ldr r1, [pc, #0x5a0]
0004132c: add r7, sp, #0x3c
00041330: mov r0, r7
00041334: add r1, pc, r1
00041338: add r6, sp, #0x38
0004133c: bl #0x44da8
00041340: cmp r0, #0
00041344: bne #0x41578
00041348: ldr r2, [pc, #0x584]
0004134c: mov r1, #2
00041350: add r4, sp, #0xb8
00041354: mov r3, #0
00041358: add r2, pc, r2
0004135c: str r1, [sp, #0xd8]
...
00041430: mov r0, sb
00041434: bl #0x14364
00041438: ldr r3, [sp, #0x28]
0004143c: ldrb r4, [r3, #0x1ba]
00041440: cmp r4, #0
00041444: bne #0x41454
00041448: ldrb r4, [r3, #0x1bb]
0004144c: cmp r4, #0
00041450: beq #0x415f0
00041454: add r0, sp, #0x74
00041458: bl #0x13d04
0004145c: add r0, sp, #0x70
00041460: bl #0x4510c
00041464: add r0, sp, #0x54
00041468: bl #0x13d04
0004146c: add r0, sp, #0x50
00041470: bl #0x4510c
00041474: ldr r0, [sp, #0x10]
00041478: bl #0x14ef4
0004147c: ldr r0, [sp, #0x18]
00041480: bl #0x14ef4
00041484: ldr r0, [sp, #0x2c]
00041488: bl #0x14ef4
0004148c: mov r0, fp
00041490: bl #0x14ef4
00041494: mov r0, r7
00041498: bl #0x14ef4
0004149c: mov r0, r6
000414a0: bl #0x14ef4
000414a4: mov r0, r4
000414a8: add sp, sp, #0xf4
000414ac: pop {r4, r5, r6, r7, r8, sb, sl, fp, pc}
000414b0: ldr r1, [pc, #0x438]
000414b4: ldr r0, [sp, #0x18]
000414b8: add r1, pc, r1
000414bc: bl #0x44da8
000414c0: cmp r0, #0
000414c4: beq #0x413d0
000414c8: ldr r0, [sp, #0x38]
000414cc: str r0, [sp, #0xc8]
000414d0: bl #0x26420
000414d4: ldr r3, [sp, #0x48]
000414d8: add ip, sp, #0xc8
000414dc: mov r0, r3
000414e0: str ip, [sp, #8]
000414e4: str r3, [sp, #0xd8]
000414e8: bl #0x26420
000414ec: ldr r1, [sp, #8]
000414f0: ldr r0, [sp, #0x28]
000414f4: mov r2, r5
000414f8: bl #0x3fb8c
000414fc: ldr r1, [sp, #0x28]
00041500: add r4, sp, #0xbc
00041504: strb r0, [r1, #0x1ba]
00041508: mov r0, r5
0004150c: bl #0x14ef4
00041510: ldr r0, [sp, #8]
00041514: bl #0x14ef4
00041518: mov r2, #2
0004151c: str r2, [sp, #0xd8]
00041520: ldr r2, [pc, #0x3cc]
00041524: mov r3, #0
00041528: add r2, pc, r2
0004152c: mov r1, r5
00041530: mov r0, r4
00041534: str r3, [sp, #0xdc]
00041538: str r3, [sp, #0xe0]
0004153c: str r3, [sp, #0xe4]
00041540: str r2, [sp, #0xe8]
00041544: bl #0x13c68
00041548: ldr r1, [pc, #0x3a8]
0004154c: mov r0, r4
00041550: add r1, pc, r1
00041554: bl #0x14f98
00041558: ldr r2, [sp, #0x28]
0004155c: ldrb r1, [r2, #0x1ba]
00041560: bl #0x14f44
00041564: mov r0, r4
00041568: bl #0x14364
0004156c: ldr r0, [sp, #0x28]
00041570: bl #0x4a790
00041574: b #0x41438
00041578: ldr r1, [pc, #0x37c]
0004157c: ldr r0, [sp, #0x10]
00041580: add r1, pc, r1
00041584: add r6, sp, #0x38
00041588: bl #0x44da8
0004158c: cmp r0, #0
00041590: beq #0x41348
00041594: ldr r0, [sp, #0x3c]
00041598: str r0, [sp, #0xc8]
0004159c: bl #0x26420
000415a0: ldr r3, [sp, #0x4c]
000415a4: add r2, sp, #0xc8
000415a8: mov r0, r3
000415ac: str r2, [sp, #8]
000415b0: str r3, [sp, #0xd8]
000415b4: bl #0x26420
000415b8: ldr r1, [sp, #8]
000415bc: ldr r0, [sp, #0x28]
000415c0: mov r2, r5
000415c4: bl #0x3fb8c
000415c8: ldr r3, [sp, #0x28]
000415cc: add r6, sp, #0x38
000415d0: strb r0, [r3, #0x1bb]
000415d4: mov r0, r5
000415d8: bl #0x14ef4
000415dc: ldr r0, [sp, #8]
000415e0: bl #0x14ef4
000415e4: ldr r0, [sp, #0x28]
000415e8: bl #0x4a7b4
000415ec: b #0x413b4
000415f0: mov r0, r3
000415f4: bl #0x28518
000415f8: b #0x41454
000415fc: mov r0, r4
