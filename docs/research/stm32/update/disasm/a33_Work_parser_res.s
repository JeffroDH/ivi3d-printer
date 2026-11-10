; A33 Work::parser_res @0x46420 — 5-byte status frames: b0 in C0..C4, b2 status (E0 ok, E1 cmd unknown, E2 erase err, E3 write err, E4 cmd/check CRC err, E6 data err, B0 in-bootloader)
; source: app.elf
; tool: Capstone 5.0.7 (single tool; cross-checked only against the existing Ghidra 12.x decompile in ivi_fwaudit/out/app.c or ivi/supx_decomp.c)

00046420: push {r4, r5, r6, r7, lr}
00046424: ldrb r2, [r1]
00046428: sub sp, sp, #0x2c
0004642c: and r3, r2, #0xf0
00046430: cmp r3, #0xc0
00046434: mov r4, r1
00046438: mov r6, r0
0004643c: bne #0x465b4
00046440: ldrb r3, [r1, #1]
00046444: ldrb lr, [r1, #2]
00046448: ldrb ip, [r1, #3]
0004644c: ldrb r1, [r1, #4]
00046450: str r1, [sp, #8]
00046454: str lr, [sp]
00046458: ldr r1, [pc, #0x2b0]
0004645c: ldr lr, [pc, #0x2b0]
00046460: add r5, sp, #0x14
00046464: str ip, [sp, #4]
00046468: add lr, pc, lr
0004646c: mov ip, #0
00046470: mov r0, r5
00046474: mov r7, #2
00046478: add r1, pc, r1
0004647c: str r7, [sp, #0x14]
00046480: str ip, [sp, #0x18]
00046484: str ip, [sp, #0x1c]
00046488: str ip, [sp, #0x20]
0004648c: str lr, [sp, #0x24]
00046490: bl #0x1386c
00046494: ldrb r3, [r4]
00046498: sub r3, r3, #0xc0
0004649c: cmp r3, #4
000464a0: addls pc, pc, r3, lsl #2
000464a4: b #0x466c4
000464a8: b #0x464d4
000464ac: b #0x46534
000464b0: b #0x46508
000464b4: b #0x46560
000464b8: b #0x464bc
000464bc: ldrb r3, [r4, #2]
000464c0: cmp r3, #0xb0
000464c4: beq #0x465f4
000464c8: mov r0, #0
000464cc: add sp, sp, #0x2c
000464d0: pop {r4, r5, r6, r7, pc}
000464d4: ldrb r3, [r4, #2]
000464d8: cmp r3, #0xe0
000464dc: beq #0x464c8
000464e0: sub r3, r3, #0xe1
000464e4: cmp r3, #5
000464e8: addls pc, pc, r3, lsl #2
000464ec: b #0x466c4
000464f0: b #0x466a4
000464f4: b #0x46684
000464f8: b #0x46664
000464fc: b #0x46644
00046500: b #0x466c4
00046504: b #0x46604
00046508: ldrb r3, [r4, #2]
0004650c: cmp r3, #0xe0
00046510: moveq r3, #1
00046514: strbeq r3, [r6, #0x48]
00046518: moveq r0, #0
0004651c: beq #0x464cc
00046520: mov r0, #0
00046524: cmp r3, #0xe3
00046528: strbeq r0, [r6, #0x48]
0004652c: add sp, sp, #0x2c
00046530: pop {r4, r5, r6, r7, pc}
00046534: ldrb r3, [r4, #2]
00046538: cmp r3, #0xe0
0004653c: moveq r3, #1
00046540: strbeq r3, [r6, #0x47]
00046544: moveq r0, #0
00046548: beq #0x464cc
0004654c: mov r0, #0
00046550: cmp r3, #0xe2
00046554: strbeq r0, [r6, #0x47]
00046558: add sp, sp, #0x2c
0004655c: pop {r4, r5, r6, r7, pc}
00046560: ldrb r3, [r4, #2]
00046564: cmp r3, #0xe0
00046568: beq #0x466cc
0004656c: cmp r3, #0xe4
00046570: bne #0x464c8
00046574: ldr r3, [pc, #0x19c]
00046578: ldr r1, [pc, #0x19c]
0004657c: mov r4, #0
00046580: mov r0, r5
00046584: mov r2, #2
00046588: add r3, pc, r3
0004658c: add r1, pc, r1
00046590: str r2, [sp, #0x14]
00046594: str r4, [sp, #0x18]
00046598: str r4, [sp, #0x1c]
0004659c: str r4, [sp, #0x20]
000465a0: str r3, [sp, #0x24]
000465a4: bl #0x1386c
000465a8: strb r4, [r6, #0x49]
000465ac: mov r0, r4
000465b0: b #0x464cc
000465b4: ldr ip, [pc, #0x164]
000465b8: ldr r1, [pc, #0x164]
000465bc: mov r2, r3
000465c0: mov lr, #2
000465c4: mov r3, #0
000465c8: add ip, pc, ip
000465cc: add r0, sp, #0x14
000465d0: add r1, pc, r1
000465d4: str lr, [sp, #0x14]
000465d8: str r3, [sp, #0x18]
000465dc: str r3, [sp, #0x1c]
000465e0: str r3, [sp, #0x20]
000465e4: str ip, [sp, #0x24]
000465e8: bl #0x1386c
000465ec: mvn r0, #0
000465f0: b #0x464cc
000465f4: mov r3, #1
000465f8: strb r3, [r6, #0x46]
000465fc: mov r0, #0
00046600: b #0x464cc
00046604: ldr r3, [pc, #0x11c]
00046608: ldr r1, [pc, #0x11c]
0004660c: mov r0, r5
00046610: mov r2, #2
00046614: mov r4, #0
00046618: add r3, pc, r3
0004661c: add r1, pc, r1
00046620: str r2, [sp, #0x14]
00046624: str r4, [sp, #0x18]
00046628: str r4, [sp, #0x1c]
0004662c: str r4, [sp, #0x20]
00046630: str r3, [sp, #0x24]
00046634: bl #0x1386c
00046638: mov r0, r4
0004663c: add sp, sp, #0x2c
00046640: pop {r4, r5, r6, r7, pc}
00046644: ldr r3, [pc, #0xe4]
00046648: ldr r1, [pc, #0xe4]
0004664c: mov r0, r5
00046650: mov r2, #2
00046654: mov r4, #0
00046658: add r3, pc, r3
0004665c: add r1, pc, r1
00046660: b #0x46620
00046664: ldr r3, [pc, #0xcc]
00046668: ldr r1, [pc, #0xcc]
0004666c: mov r0, r5
00046670: mov r2, #2
00046674: mov r4, #0
00046678: add r3, pc, r3
0004667c: add r1, pc, r1
00046680: b #0x46620
00046684: ldr r3, [pc, #0xb4]
00046688: ldr r1, [pc, #0xb4]
0004668c: mov r0, r5
00046690: mov r2, #2
00046694: mov r4, #0
00046698: add r3, pc, r3
0004669c: add r1, pc, r1
000466a0: b #0x46620
000466a4: ldr r3, [pc, #0x9c]
000466a8: ldr r1, [pc, #0x9c]
000466ac: mov r0, r5
000466b0: mov r2, #2
000466b4: mov r4, #0
000466b8: add r3, pc, r3
000466bc: add r1, pc, r1
000466c0: b #0x46620
000466c4: mvn r0, #0
000466c8: b #0x464cc
000466cc: ldr r3, [pc, #0x7c]
000466d0: ldr r1, [pc, #0x7c]
000466d4: mov r4, #0
000466d8: add r3, pc, r3
000466dc: mov r0, r5
000466e0: mov r2, #2
000466e4: add r1, pc, r1
000466e8: str r3, [sp, #0x24]
000466ec: str r2, [sp, #0x14]
000466f0: str r4, [sp, #0x18]
000466f4: str r4, [sp, #0x1c]
000466f8: str r4, [sp, #0x20]
000466fc: bl #0x1386c
00046700: mov r3, #1
00046704: mov r0, r4
00046708: strb r3, [r6, #0x49]
0004670c: b #0x464cc
00046710: muleq r0, ip, r3
00046714: andeq sp, r0, r4, ror #14
00046718: andeq sp, r0, r4, asr #12
0004671c: andeq pc, r0, r4, lsr #6
00046720: andeq sp, r0, r4, lsl #12
00046724: andeq pc, r0, r4, lsr #4
00046728: strheq sp, [r0], -r4
0004672c: andeq pc, r0, ip, ror #4
00046730: andeq sp, r0, r4, ror r5
00046734: andeq pc, r0, r8, lsl r2
00046738: andeq sp, r0, r4, asr r5
