; A33 Work::startUpgradeFirmware @0x47614 — checks len field == size-8, ver==2, CRC16 over file[8:]; writes 12-B header (wait C1 E0, 200 polls), 256-B records (wait C2 E0), remainder, 8-B check (wait C3 E0)
; source: app.elf
; tool: Capstone 5.0.7 (single tool; cross-checked only against the existing Ghidra 12.x decompile in ivi_fwaudit/out/app.c or ivi/supx_decomp.c)

00047614: push {r4, r5, r6, r7, r8, sb, sl, fp, lr}
00047618: sub sp, sp, #0xbc
0004761c: add sb, sp, #0x60
00047620: mov r5, #0
00047624: str r0, [sp, #0x24]
00047628: mov r0, sb
0004762c: mov r6, r1
00047630: str r5, [sp, #0x94]
00047634: strh r5, [sp, #0x98]
00047638: strh r5, [sp, #0x9a]
0004763c: bl #0x14214
00047640: ldr r3, [pc, #0xe14]
00047644: add r4, sp, #0x64
00047648: ldr fp, [pc, #0xe10]
0004764c: mov r2, #2
00047650: add r3, pc, r3
00047654: mov r1, sb
00047658: mov r0, r4
0004765c: str r5, [sp, #0xa8]
00047660: str r5, [sp, #0xac]
00047664: str r5, [sp, #0xb0]
00047668: str r2, [sp, #0xa4]
0004766c: str r3, [sp, #0xb4]
00047670: add fp, pc, fp
00047674: bl #0x13f8c
00047678: add r5, sp, #0x88
0004767c: mov r0, r5
00047680: mov r1, r4
00047684: bl #0x13bd8
00047688: ldr r3, [sp, #0x88]
0004768c: add r0, sp, #0x68
00047690: ldr r1, [r3, #0xc]
00047694: ldr r2, [r3, #4]
00047698: add r1, r3, r1
0004769c: add r3, sp, #0x54
000476a0: bl #0x139e0
000476a4: ldr r0, [sp, #0x88]
000476a8: ldr r3, [r0]
000476ac: cmp r3, #0
000476b0: beq #0x47ab0
000476b4: cmn r3, #1
000476b8: beq #0x476d0
000476bc: mov r1, #1
000476c0: bl #0x531a4
000476c4: cmp r0, #0
000476c8: ldreq r0, [sp, #0x88]
000476cc: beq #0x47ab0
000476d0: add r5, sp, #0x6c
000476d4: mov r0, r5
000476d8: mov r1, sb
000476dc: ldr r8, [sp, #0x68]
000476e0: bl #0x13fbc
000476e4: add r0, sp, #0x8c
000476e8: mov r1, r5
000476ec: str r0, [sp, #0x20]
000476f0: bl #0x13bd8
000476f4: ldr r3, [sp, #0x8c]
000476f8: add r0, sp, #0x70
000476fc: ldr r1, [r3, #0xc]
00047700: ldr r2, [r3, #4]
00047704: add r1, r3, r1
00047708: add r3, sp, #0x58
0004770c: bl #0x139e0
00047710: ldr r0, [sp, #0x8c]
00047714: ldr r3, [r0]
00047718: cmp r3, #0
0004771c: beq #0x47ae0
00047720: cmn r3, #1
00047724: beq #0x4773c
00047728: mov r1, #1
0004772c: bl #0x531a4
00047730: cmp r0, #0
00047734: ldreq r0, [sp, #0x8c]
00047738: beq #0x47ae0
0004773c: ldr r1, [pc, #0xd20]
00047740: add r7, sp, #0xa4
00047744: mov r2, r8
00047748: mov r0, r7
0004774c: add r1, pc, r1
00047750: ldr r3, [sp, #0x70]
00047754: bl #0x1386c
00047758: ldr r2, [pc, #0xd08]
0004775c: ldr r3, [sp, #0x70]
00047760: ldr r2, [fp, r2]
00047764: sub r4, r3, #0xc
00047768: cmp r4, r2
0004776c: str r2, [sp, #0x1c]
00047770: bne #0x48270
00047774: add r8, sp, #0x9c
00047778: ldr r0, [sp, #0x6c]
0004777c: ldr r3, [r0]
00047780: cmp r3, #0
00047784: beq #0x47ad0
00047788: cmn r3, #1
0004778c: beq #0x477a4
00047790: mov r1, #1
00047794: bl #0x531a4
00047798: cmp r0, #0
0004779c: ldreq r0, [sp, #0x6c]
000477a0: beq #0x47ad0
000477a4: ldr r3, [sp, #0x68]
000477a8: ldr r1, [sp, #0x1c]
000477ac: sub r4, r3, #0xc
000477b0: cmp r4, r1
000477b4: bne #0x482a8
000477b8: ldr r0, [sp, #0x64]
000477bc: ldr r3, [r0]
000477c0: cmp r3, #0
000477c4: beq #0x47af0
000477c8: cmn r3, #1
000477cc: beq #0x477e4
000477d0: mov r1, #1
000477d4: bl #0x531a4
000477d8: cmp r0, #0
000477dc: ldreq r0, [sp, #0x64]
000477e0: beq #0x47af0
000477e4: ldr r0, [r6]
000477e8: str r0, [sp, #0x74]
000477ec: ldr r3, [r0]
000477f0: cmp r3, #0
000477f4: beq #0x47808
000477f8: cmn r3, #1
000477fc: beq #0x47808
00047800: mov r1, #1
00047804: bl #0x5316c
00047808: add r2, sp, #0x74
0004780c: mov r1, r2
00047810: mov r0, r8
00047814: str r2, [sp, #0x28]
00047818: bl #0x14070
0004781c: mov r0, r8
00047820: mov r1, #1
00047824: bl #0x13b48
00047828: subs r3, r0, #0
0004782c: beq #0x47c64
00047830: ldr lr, [pc, #0xc34]
00047834: ldr r1, [pc, #0xc34]
00047838: ldr r2, [pc, #0xc34]
0004783c: mov r3, #2
00047840: mov ip, #0
00047844: add lr, pc, lr
00047848: str r3, [sp, #0xa4]
0004784c: mov r0, r7
00047850: add r1, pc, r1
00047854: add r2, pc, r2
00047858: mov r3, #0x164
0004785c: str ip, [sp, #0xa8]
00047860: str ip, [sp, #0xac]
00047864: str ip, [sp, #0xb0]
00047868: str lr, [sp, #0xb4]
0004786c: bl #0x1386c
00047870: ldr r2, [pc, #0xc00]
00047874: mov r3, #0
00047878: mov r1, #2
0004787c: add r2, pc, r2
00047880: mov r0, r8
00047884: str r1, [sp, #0xa4]
00047888: str r3, [sp, #0xa8]
0004788c: str r3, [sp, #0xac]
00047890: str r3, [sp, #0xb0]
00047894: str r2, [sp, #0xb4]
00047898: bl #0x1353c
0004789c: mov r3, r1
000478a0: ldr r1, [pc, #0xbd4]
000478a4: mov r2, r0
000478a8: add r1, pc, r1
000478ac: mov r0, r7
000478b0: bl #0x1386c
000478b4: mov r0, #0x100000
000478b8: bl #0x135cc
000478bc: subs r6, r0, #0
000478c0: beq #0x4800c
000478c4: add sl, sp, #0x78
000478c8: mov r0, sl
000478cc: mov r1, r8
000478d0: bl #0x14100
000478d4: ldr r2, [sp, #0x78]
000478d8: ldr r3, [r2]
000478dc: cmp r3, #1
000478e0: bls #0x47b7c
000478e4: ldr r1, [r2, #4]
000478e8: ldrb r2, [r2, #0xb]
000478ec: add r1, r1, #1
000478f0: lsr r2, r2, #7
000478f4: mov r0, sl
000478f8: bl #0x13cf8
000478fc: ldr r3, [sp, #0x78]
00047900: ldr r1, [r3, #0xc]
00047904: add r1, r3, r1
00047908: ldr r2, [r3, #4]
0004790c: mov r0, r6
00047910: bl #0x13ae8
00047914: mov r2, #2
00047918: ldr ip, [pc, #0xb60]
0004791c: ldr r1, [pc, #0xb60]
00047920: str r2, [sp, #0xa4]
00047924: ldr r2, [pc, #0xb5c]
00047928: mov r3, #0
0004792c: add ip, pc, ip
00047930: str r3, [sp, #0xa8]
00047934: str r3, [sp, #0xac]
00047938: str r3, [sp, #0xb0]
0004793c: mov r0, r7
00047940: add r1, pc, r1
00047944: add r2, pc, r2
00047948: mov r3, #0x170
0004794c: str ip, [sp, #0xb4]
00047950: bl #0x1386c
00047954: mov r1, r6
00047958: mov r2, #8
0004795c: add r0, sp, #0x94
00047960: bl #0x13ae8
00047964: ldr r2, [pc, #0xb20]
00047968: mov r3, #0
0004796c: mov r1, #2
00047970: add r2, pc, r2
00047974: str r1, [sp, #0xa4]
00047978: str r3, [sp, #0xa8]
0004797c: str r3, [sp, #0xac]
00047980: str r3, [sp, #0xb0]
00047984: str r2, [sp, #0xb4]
00047988: ldrb r1, [r6, #2]
0004798c: ldrb r2, [r6]
00047990: ldrb r3, [r6, #1]
00047994: str r1, [sp]
00047998: ldrb r1, [r6, #3]
0004799c: str r1, [sp, #4]
000479a0: ldrb r1, [r6, #4]
000479a4: str r1, [sp, #8]
000479a8: ldrb r1, [r6, #5]
000479ac: str r1, [sp, #0xc]
000479b0: ldrb r1, [r6, #6]
000479b4: str r1, [sp, #0x10]
000479b8: ldrb r1, [r6, #7]
000479bc: str r1, [sp, #0x14]
000479c0: ldr r1, [pc, #0xac8]
000479c4: mov r0, r7
000479c8: add r1, pc, r1
000479cc: bl #0x1386c
000479d0: ldr r3, [sp, #0x94]
000479d4: str r3, [sp, #0x2c]
000479d8: mov r2, r3
000479dc: mov r0, r8
000479e0: mov r3, #0
000479e4: mov r4, r2
000479e8: mov r5, r3
000479ec: bl #0x1353c
000479f0: subs r0, r0, #8
000479f4: sbc r1, r1, #0
000479f8: cmp r5, r1
000479fc: cmpeq r4, r0
00047a00: beq #0x47b10
00047a04: ldr r2, [pc, #0xa88]
00047a08: ldr r1, [pc, #0xa88]
00047a0c: mov r0, r7
00047a10: mov ip, #2
00047a14: mov r3, #0
00047a18: add r2, pc, r2
00047a1c: add r1, pc, r1
00047a20: str ip, [sp, #0xa4]
00047a24: str r3, [sp, #0xa8]
00047a28: str r3, [sp, #0xac]
00047a2c: str r3, [sp, #0xb0]
00047a30: str r2, [sp, #0xb4]
00047a34: bl #0x1386c
00047a38: mvn r4, #0
00047a3c: ldr r0, [sp, #0x78]
00047a40: ldr r3, [r0]
00047a44: cmp r3, #0
00047a48: beq #0x47b00
00047a4c: cmn r3, #1
00047a50: beq #0x47a68
00047a54: mov r1, #1
00047a58: bl #0x531a4
00047a5c: cmp r0, #0
00047a60: ldreq r0, [sp, #0x78]
00047a64: beq #0x47b00
00047a68: mov r0, r8
00047a6c: bl #0x13998
00047a70: ldr r0, [sp, #0x74]
00047a74: ldr r3, [r0]
00047a78: cmp r3, #0
00047a7c: beq #0x47ac0
00047a80: cmn r3, #1
00047a84: beq #0x47a9c
00047a88: mov r1, #1
00047a8c: bl #0x531a4
00047a90: cmp r0, #0
00047a94: ldreq r0, [sp, #0x74]
00047a98: beq #0x47ac0
00047a9c: mov r0, sb
00047aa0: bl #0x14238
00047aa4: mov r0, r4
00047aa8: add sp, sp, #0xbc
00047aac: pop {r4, r5, r6, r7, r8, sb, sl, fp, pc}
00047ab0: mov r1, #1
00047ab4: mov r2, #4
00047ab8: bl #0x13da0
00047abc: b #0x476d0
00047ac0: mov r1, #2
00047ac4: mov r2, #4
00047ac8: bl #0x13da0
00047acc: b #0x47a9c
00047ad0: mov r1, #2
00047ad4: mov r2, #4
00047ad8: bl #0x13da0
00047adc: b #0x477a4
00047ae0: mov r1, #1
00047ae4: mov r2, #4
00047ae8: bl #0x13da0
00047aec: b #0x4773c
00047af0: mov r1, #2
00047af4: mov r2, #4
00047af8: bl #0x13da0
00047afc: b #0x477e4
00047b00: mov r1, #1
00047b04: mov r2, #4
00047b08: bl #0x13da0
00047b0c: b #0x47a68
00047b10: mov r2, #2
00047b14: ldr ip, [pc, #0x980]
00047b18: ldr r1, [pc, #0x980]
00047b1c: str r2, [sp, #0xa4]
00047b20: ldr r2, [pc, #0x97c]
00047b24: mov r3, #0
00047b28: add ip, pc, ip
00047b2c: str r3, [sp, #0xa8]
00047b30: str r3, [sp, #0xac]
00047b34: str r3, [sp, #0xb0]
00047b38: mov r0, r7
00047b3c: add r1, pc, r1
00047b40: add r2, pc, r2
00047b44: ldr r3, [pc, #0x95c]
00047b48: str ip, [sp, #0xb4]
00047b4c: bl #0x1386c
00047b50: ldrh r3, [sp, #0x98]
00047b54: cmp r3, #2
00047b58: beq #0x47b90
00047b5c: ldr r2, [pc, #0x948]
00047b60: ldr r1, [pc, #0x948]
00047b64: mov r0, r7
00047b68: mov ip, #2
00047b6c: mov r3, #0
00047b70: add r2, pc, r2
00047b74: add r1, pc, r1
00047b78: b #0x47a20
00047b7c: ldr r1, [r2, #0xc]
00047b80: mov r3, r2
00047b84: cmp r1, #0x10
00047b88: bne #0x478e4
00047b8c: b #0x47904
00047b90: ldr ip, [pc, #0x91c]
00047b94: ldr r1, [pc, #0x91c]
00047b98: ldr r2, [pc, #0x91c]
00047b9c: mov lr, #0
00047ba0: add ip, pc, ip
00047ba4: str r3, [sp, #0xa4]
00047ba8: mov r0, r7
00047bac: add r1, pc, r1
00047bb0: add r2, pc, r2
00047bb4: ldr r3, [pc, #0x904]
00047bb8: str lr, [sp, #0xa8]
00047bbc: str lr, [sp, #0xac]
00047bc0: str lr, [sp, #0xb0]
00047bc4: str ip, [sp, #0xb4]
00047bc8: bl #0x1386c
00047bcc: ldr r3, [sp, #0x2c]
00047bd0: add r1, r6, #8
00047bd4: add ip, r3, #8
00047bd8: mov r0, r1
00047bdc: add ip, r6, ip
00047be0: mov r3, #0
00047be4: cmp r0, ip
00047be8: beq #0x47c20
00047bec: ldrb lr, [r0], #1
00047bf0: mov r2, #8
00047bf4: eor r3, r3, lr, lsl r2
00047bf8: lsl r3, r3, #0x10
00047bfc: asrs r3, r3, #0x10
00047c00: lsl r3, r3, #0x11
00047c04: eormi r3, r3, #0x10000000
00047c08: sub r2, r2, #1
00047c0c: eormi r3, r3, #0x210000
00047c10: ands r2, r2, #0xff
00047c14: lsr r3, r3, #0x10
00047c18: bne #0x47bf8
00047c1c: b #0x47be4
00047c20: ldrh r2, [sp, #0x9a]
00047c24: cmp r2, r3
00047c28: beq #0x47c9c
00047c2c: ldr lr, [pc, #0x890]
00047c30: ldr r1, [pc, #0x890]
00047c34: mov r0, r7
00047c38: mov r4, #2
00047c3c: mov ip, #0
00047c40: add lr, pc, lr
00047c44: add r1, pc, r1
00047c48: str r4, [sp, #0xa4]
00047c4c: str ip, [sp, #0xa8]
00047c50: str ip, [sp, #0xac]
00047c54: str ip, [sp, #0xb0]
00047c58: str lr, [sp, #0xb4]
00047c5c: bl #0x1386c
00047c60: b #0x47a38
00047c64: ldr r2, [pc, #0x860]
00047c68: ldr r1, [pc, #0x860]
00047c6c: mov ip, #2
00047c70: add r2, pc, r2
00047c74: mov r0, r7
00047c78: add r1, pc, r1
00047c7c: str r3, [sp, #0xa8]
00047c80: str r3, [sp, #0xac]
00047c84: str r3, [sp, #0xb0]
00047c88: str ip, [sp, #0xa4]
00047c8c: str r2, [sp, #0xb4]
00047c90: bl #0x1386c
00047c94: mvn r4, #0
00047c98: b #0x47a68
00047c9c: ldr r2, [sp, #0x24]
00047ca0: mov r3, #0
00047ca4: ldr r0, [r2, #0x3c]
00047ca8: mov r2, #0xc
00047cac: bl #0x140dc
00047cb0: ldr r0, [sp, #0x24]
00047cb4: mov r3, #0
00047cb8: strb r3, [r0, #0x48]
00047cbc: mov r1, #0xc8
00047cc0: bl #0x4699c
00047cc4: subs r3, r0, #0
00047cc8: bne #0x47d00
00047ccc: ldr r2, [pc, #0x800]
00047cd0: ldr r1, [pc, #0x800]
00047cd4: mov r0, r7
00047cd8: mov ip, #2
00047cdc: add r2, pc, r2
00047ce0: add r1, pc, r1
00047ce4: str r3, [sp, #0xa8]
00047ce8: str r3, [sp, #0xac]
00047cec: str r3, [sp, #0xb0]
00047cf0: str ip, [sp, #0xa4]
00047cf4: str r2, [sp, #0xb4]
00047cf8: bl #0x1386c
00047cfc: b #0x47a38
00047d00: ldr r0, [pc, #0x7d4]
00047d04: mov r1, #0x20
00047d08: add r0, pc, r0
00047d0c: bl #0x14358
00047d10: str r0, [sp, #0x90]
00047d14: ldr r0, [pc, #0x7c4]
00047d18: mov r1, #0xa
00047d1c: add r0, pc, r0
00047d20: bl #0x14358
00047d24: add r1, sp, #0x90
00047d28: str r1, [sp, #0x3c]
00047d2c: str r0, [sp, #0xa4]
00047d30: mov r1, r7
00047d34: ldr r0, [sp, #0x3c]
00047d38: bl #0x13ef0
00047d3c: ldr r0, [sp, #0xa4]
00047d40: ldr r3, [r0]
00047d44: cmp r3, #0
00047d48: beq #0x480c8
00047d4c: cmn r3, #1
00047d50: beq #0x47d68
00047d54: mov r1, #1
00047d58: bl #0x531a4
00047d5c: cmp r0, #0
00047d60: ldreq r0, [sp, #0xa4]
00047d64: beq #0x480c8
00047d68: ldr r0, [sp, #0x90]
00047d6c: ldr r3, [r0]
00047d70: cmp r3, #0
00047d74: beq #0x480b8
00047d78: cmn r3, #1
00047d7c: beq #0x47d94
00047d80: mov r1, #1
00047d84: bl #0x531a4
00047d88: cmp r0, #0
00047d8c: ldreq r0, [sp, #0x90]
00047d90: beq #0x480b8
00047d94: ldr r2, [sp, #0x2c]
00047d98: sub r2, r2, #0x14
00047d9c: lsrs r3, r2, #8
00047da0: str r2, [sp, #0x4c]
00047da4: str r3, [sp, #0x38]
00047da8: beq #0x48068
00047dac: ldr r1, [pc, #0x730]
00047db0: ldr r2, [pc, #0x730]
00047db4: ldr r3, [pc, #0x730]
00047db8: mov r0, #0
00047dbc: str r0, [sp, #0x34]
00047dc0: add r1, pc, r1
00047dc4: add r2, pc, r2
00047dc8: add r3, pc, r3
00047dcc: mov r5, r0
00047dd0: mov r0, #0x14
00047dd4: str r1, [sp, #0x40]
00047dd8: str r2, [sp, #0x44]
00047ddc: str r3, [sp, #0x48]
00047de0: str r0, [sp, #0x30]
00047de4: b #0x47f44
00047de8: cmn r3, #1
00047dec: beq #0x47e04
00047df0: mov r1, #1
00047df4: bl #0x531a4
00047df8: cmp r0, #0
00047dfc: ldreq r0, [sp, #0x7c]
00047e00: beq #0x47fcc
00047e04: ldr r0, [sp, #0x44]
00047e08: mov r1, #0xa
00047e0c: bl #0x14358
00047e10: str r0, [sp, #0xa4]
00047e14: mov r1, r7
00047e18: add r0, sp, #0x8c
00047e1c: bl #0x13ef0
00047e20: ldr r0, [sp, #0xa4]
00047e24: ldr r3, [r0]
00047e28: cmp r3, #0
00047e2c: beq #0x47fec
00047e30: cmn r3, #1
00047e34: beq #0x47e4c
00047e38: mov r1, #1
00047e3c: bl #0x531a4
00047e40: cmp r0, #0
00047e44: ldreq r0, [sp, #0xa4]
00047e48: beq #0x47fec
00047e4c: mov r2, #0
00047e50: mov r3, #2
00047e54: str r2, [sp, #0xa8]
00047e58: str r2, [sp, #0xac]
00047e5c: str r2, [sp, #0xb0]
00047e60: ldr r0, [sp, #0x3c]
00047e64: ldr r2, [sp, #0x48]
00047e68: add r1, sp, #0x8c
00047e6c: str r2, [sp, #0xb4]
00047e70: str r3, [sp, #0xa4]
00047e74: bl #0x13bd8
00047e78: ldr r3, [sp, #0x90]
00047e7c: add r0, sp, #0x80
00047e80: ldr r1, [r3, #0xc]
00047e84: ldr r2, [r3, #4]
00047e88: add r1, r3, r1
00047e8c: add r3, sp, #0x5c
00047e90: bl #0x139e0
00047e94: ldr r0, [sp, #0x90]
00047e98: ldr r3, [r0]
00047e9c: cmp r3, #0
00047ea0: beq #0x47ffc
00047ea4: cmn r3, #1
00047ea8: beq #0x47ec0
00047eac: mov r1, #1
00047eb0: bl #0x531a4
00047eb4: cmp r0, #0
00047eb8: ldreq r0, [sp, #0x90]
00047ebc: beq #0x47ffc
00047ec0: mov r0, r7
00047ec4: ldr r1, [sp, #0x80]
00047ec8: bl #0x1386c
00047ecc: ldr r3, [sp, #0x80]
00047ed0: ldr r0, [sp, #0x1c]
00047ed4: sub r4, r3, #0xc
00047ed8: cmp r4, r0
00047edc: bne #0x483dc
00047ee0: ldr r0, [sp, #0x8c]
00047ee4: ldr r3, [r0]
00047ee8: cmp r3, #0
00047eec: beq #0x47fdc
00047ef0: cmn r3, #1
00047ef4: beq #0x47f0c
00047ef8: mov r1, #1
00047efc: bl #0x531a4
00047f00: cmp r0, #0
00047f04: ldreq r0, [sp, #0x8c]
00047f08: beq #0x47fdc
00047f0c: mov r0, #0x64
00047f10: bl #0x13b3c
00047f14: ldr r1, [sp, #0x38]
00047f18: ldr r0, [sp, #0x34]
00047f1c: bl #0x13a58
00047f20: mov r1, r0
00047f24: ldr r0, [sp, #0x24]
00047f28: bl #0x51cec
00047f2c: ldr r2, [sp, #0x34]
00047f30: ldr r1, [sp, #0x38]
00047f34: add r2, r2, #0x64
00047f38: cmp r5, r1
00047f3c: str r2, [sp, #0x34]
00047f40: beq #0x48074
00047f44: ldr r1, [sp, #0x24]
00047f48: ldr r2, [sp, #0x30]
00047f4c: ldr r0, [r1, #0x3c]
00047f50: mov r3, #0
00047f54: add r1, r6, r2
00047f58: mov r2, #0x100
00047f5c: bl #0x140dc
00047f60: ldr r2, [sp, #0x30]
00047f64: ldr r0, [sp, #0x24]
00047f68: mov r3, #0
00047f6c: add r2, r2, #0x100
00047f70: strb r3, [r0, #0x48]
00047f74: mov r1, #0xa
00047f78: str r2, [sp, #0x30]
00047f7c: bl #0x469f0
00047f80: subs r3, r0, #0
00047f84: beq #0x4804c
00047f88: ldr r0, [sp, #0x40]
00047f8c: mov r1, #0xc
00047f90: bl #0x14358
00047f94: add r5, r5, #1
00047f98: add r4, sp, #0x7c
00047f9c: str r0, [sp, #0x8c]
00047fa0: mov r1, r5
00047fa4: mov r0, r4
00047fa8: mov r2, #0x10
00047fac: bl #0x13800
00047fb0: add r0, sp, #0x8c
00047fb4: mov r1, r4
00047fb8: bl #0x13ef0
00047fbc: ldr r0, [sp, #0x7c]
00047fc0: ldr r3, [r0]
00047fc4: cmp r3, #0
00047fc8: bne #0x47de8
00047fcc: mov r1, #2
00047fd0: mov r2, #4
00047fd4: bl #0x13da0
00047fd8: b #0x47e04
00047fdc: mov r1, #2
00047fe0: mov r2, #4
00047fe4: bl #0x13da0
00047fe8: b #0x47f0c
00047fec: mov r1, #2
00047ff0: mov r2, #4
00047ff4: bl #0x13da0
00047ff8: b #0x47e4c
00047ffc: mov r1, #1
00048000: mov r2, #4
00048004: bl #0x13da0
00048008: b #0x47ec0
0004800c: ldr ip, [pc, #0x4dc]
00048010: ldr r1, [pc, #0x4dc]
00048014: ldr r2, [pc, #0x4dc]
00048018: mov lr, #2
0004801c: add ip, pc, ip
00048020: mov r0, r7
00048024: add r1, pc, r1
00048028: add r2, pc, r2
0004802c: ldr r3, [pc, #0x4c8]
00048030: str r6, [sp, #0xa8]
00048034: str r6, [sp, #0xac]
00048038: str r6, [sp, #0xb0]
0004803c: str lr, [sp, #0xa4]
00048040: str ip, [sp, #0xb4]
00048044: bl #0x1386c
00048048: b #0x47c94
0004804c: ldr r2, [pc, #0x4ac]
00048050: ldr r1, [pc, #0x4ac]
00048054: mov r0, r7
00048058: mov ip, #2
0004805c: add r2, pc, r2
00048060: add r1, pc, r1
00048064: b #0x47ce4
00048068: ldr r5, [sp, #0x38]
0004806c: mov r3, #0x14
00048070: str r3, [sp, #0x30]
00048074: ldr r0, [sp, #0x4c]
00048078: ands r2, r0, #0xff
0004807c: beq #0x48194
00048080: ldr r1, [sp, #0x2c]
00048084: ldr r0, [sp, #0x30]
00048088: rsb r3, r0, r1
0004808c: cmp r3, r2
00048090: beq #0x481e8
00048094: ldr lr, [pc, #0x46c]
00048098: ldr r1, [pc, #0x46c]
0004809c: mov r0, r7
000480a0: sub r3, r3, #0x10
000480a4: mov r4, #2
000480a8: mov ip, #0
000480ac: add lr, pc, lr
000480b0: add r1, pc, r1
000480b4: b #0x47c48
000480b8: mov r1, #2
000480bc: mov r2, #4
000480c0: bl #0x13da0
000480c4: b #0x47d94
000480c8: mov r1, #2
000480cc: mov r2, #4
000480d0: bl #0x13da0
000480d4: b #0x47d68
000480d8: ldr r0, [pc, #0x430]
000480dc: mov r1, #0xc
000480e0: add r0, pc, r0
000480e4: bl #0x14358
000480e8: str r0, [sp, #0x90]
000480ec: add r1, r5, #1
000480f0: mov r0, r7
000480f4: mov r2, #0x10
000480f8: bl #0x13800
000480fc: ldr r0, [sp, #0x3c]
00048100: mov r1, r7
00048104: bl #0x13ef0
00048108: mov r0, r7
0004810c: bl #0x14ef4
00048110: ldr r0, [pc, #0x3fc]
00048114: mov r1, #0xa
00048118: add r0, pc, r0
0004811c: bl #0x14358
00048120: str r0, [sp, #0xa4]
00048124: mov r1, r7
00048128: ldr r0, [sp, #0x3c]
0004812c: bl #0x13ef0
00048130: mov r0, r7
00048134: bl #0x14ef4
00048138: ldr r2, [pc, #0x3d8]
0004813c: mov r1, #2
00048140: mov r3, #0
00048144: add r2, pc, r2
00048148: str r1, [sp, #0xa4]
0004814c: add r0, sp, #0x84
00048150: ldr r1, [sp, #0x3c]
00048154: str r3, [sp, #0xa8]
00048158: str r3, [sp, #0xac]
0004815c: str r3, [sp, #0xb0]
00048160: str r2, [sp, #0xb4]
00048164: bl #0x49054
00048168: mov r0, r7
0004816c: ldr r1, [sp, #0x84]
00048170: bl #0x1386c
00048174: ldr r0, [sp, #0x84]
00048178: add r1, sp, #0x8c
0004817c: sub r0, r0, #0xc
00048180: bl #0x13e48
00048184: ldr r0, [sp, #0x3c]
00048188: bl #0x14ef4
0004818c: ldr r1, [sp, #0x2c]
00048190: str r1, [sp, #0x30]
00048194: ldr r2, [sp, #0x30]
00048198: ldr r3, [sp, #0x24]
0004819c: add r1, r6, r2
000481a0: ldr r0, [r3, #0x3c]
000481a4: mov r2, #8
000481a8: mov r3, #0
000481ac: bl #0x140dc
000481b0: ldr r0, [sp, #0x24]
000481b4: mov r3, #0
000481b8: strb r3, [r0, #0x49]
000481bc: mov r1, #0xa
000481c0: bl #0x46a98
000481c4: subs r3, r0, #0
000481c8: mov ip, #2
000481cc: mov r0, r7
000481d0: bne #0x4823c
000481d4: ldr r2, [pc, #0x340]
000481d8: ldr r1, [pc, #0x340]
000481dc: add r2, pc, r2
000481e0: add r1, pc, r1
000481e4: b #0x47ce4
000481e8: ldr r2, [sp, #0x30]
000481ec: add r1, r6, r2
000481f0: mov r2, r3
000481f4: ldr r3, [sp, #0x24]
000481f8: ldr r0, [r3, #0x3c]
000481fc: mov r3, #0
00048200: bl #0x140dc
00048204: ldr r0, [sp, #0x24]
00048208: mov r3, #0
0004820c: strb r3, [r0, #0x48]
00048210: mov r1, #0xa
00048214: bl #0x469f0
00048218: subs r3, r0, #0
0004821c: bne #0x480d8
00048220: ldr r2, [pc, #0x2fc]
00048224: ldr r1, [pc, #0x2fc]
00048228: mov r0, r7
0004822c: mov ip, #2
00048230: add r2, pc, r2
00048234: add r1, pc, r1
00048238: b #0x47ce4
0004823c: ldr r2, [pc, #0x2e8]
00048240: ldr r1, [pc, #0x2e8]
00048244: mov r3, #0
00048248: add r2, pc, r2
0004824c: add r1, pc, r1
00048250: str ip, [sp, #0xa4]
00048254: str r3, [sp, #0xa8]
00048258: str r3, [sp, #0xac]
0004825c: str r3, [sp, #0xb0]
00048260: str r2, [sp, #0xb4]
00048264: bl #0x1386c
00048268: mov r4, #0
0004826c: b #0x47a3c
00048270: ldr r2, [pc, #0x2bc]
00048274: sub r0, r3, #4
00048278: ldr r2, [fp, r2]
0004827c: cmp r2, #0
00048280: beq #0x48438
00048284: mvn r1, #0
00048288: bl #0x52b78
0004828c: cmp r0, #0
00048290: add r8, sp, #0x9c
00048294: bgt #0x47778
00048298: mov r0, r4
0004829c: mov r1, r8
000482a0: bl #0x1404c
000482a4: b #0x47778
000482a8: ldr r2, [pc, #0x284]
000482ac: sub r0, r3, #4
000482b0: ldr r2, [fp, r2]
000482b4: cmp r2, #0
000482b8: beq #0x4844c
000482bc: mvn r1, #0
000482c0: bl #0x52b78
000482c4: cmp r0, #0
000482c8: bgt #0x477b8
000482cc: mov r0, r4
000482d0: mov r1, r8
000482d4: bl #0x1404c
000482d8: b #0x477b8
000482dc: mov r0, r4
000482e0: bl #0x14ef4
000482e4: mov r0, sb
000482e8: bl #0x14238
000482ec: bl #0x14040
000482f0: ldr r0, [sp, #0x84]
000482f4: add r1, sp, #0x8c
000482f8: sub r0, r0, #0xc
000482fc: bl #0x13e48
00048300: ldr r0, [sp, #0x3c]
00048304: bl #0x14ef4
00048308: mov r0, sl
0004830c: bl #0x14e6c
00048310: mov r0, r8
00048314: bl #0x13998
00048318: add r0, sp, #0x74
0004831c: bl #0x14ef4
00048320: b #0x482e4
00048324: mov r0, r7
00048328: bl #0x14ef4
0004832c: b #0x48300
00048330: b #0x48324
00048334: b #0x48300
00048338: b #0x48310
0004833c: b #0x48318
00048340: add r0, sp, #0x8c
00048344: bl #0x14e6c
00048348: add r8, sp, #0x9c
0004834c: mov r0, r5
00048350: bl #0x14ef4
00048354: ldr r0, [sp, #0x68]
00048358: mov r1, r8
0004835c: sub r0, r0, #0xc
00048360: bl #0x13e48
00048364: b #0x482dc
00048368: add r8, sp, #0x9c
0004836c: b #0x48354
00048370: add r1, sp, #0x90
00048374: str r1, [sp, #0x3c]
00048378: b #0x48300
0004837c: ldr r0, [sp, #0x70]
00048380: add r8, sp, #0x9c
00048384: sub r0, r0, #0xc
00048388: mov r1, r8
0004838c: bl #0x13e48
00048390: b #0x4834c
00048394: mov r0, r4
00048398: bl #0x14ef4
0004839c: add r0, sp, #0x8c
000483a0: bl #0x14ef4
000483a4: b #0x48308
000483a8: b #0x48308
000483ac: mov r0, r5
000483b0: bl #0x14e6c
000483b4: b #0x482dc
000483b8: b #0x482e4
000483bc: add r8, sp, #0x9c
000483c0: b #0x4834c
000483c4: mov r0, r7
000483c8: bl #0x14ef4
000483cc: b #0x4839c
000483d0: ldr r0, [sp, #0x3c]
000483d4: bl #0x14e6c
000483d8: b #0x4839c
000483dc: ldr r2, [pc, #0x150]
000483e0: add r0, r4, #8
000483e4: ldr r2, [fp, r2]
000483e8: cmp r2, #0
000483ec: beq #0x48424
000483f0: mvn r1, #0
000483f4: bl #0x52b78
000483f8: cmp r0, #0
000483fc: bgt #0x47ee0
00048400: mov r0, r4
00048404: ldr r1, [sp, #0x3c]
00048408: bl #0x1404c
0004840c: b #0x47ee0
00048410: ldr r0, [sp, #0x80]
00048414: ldr r1, [sp, #0x3c]
00048418: sub r0, r0, #0xc
0004841c: bl #0x13e48
00048420: b #0x4839c
00048424: ldr r0, [r3, #-4]
00048428: sub r2, r0, #1
0004842c: str r2, [r3, #-4]
00048430: b #0x483f8
00048434: b #0x4839c
00048438: ldr r0, [r3, #-4]
0004843c: sub r2, r0, #1
00048440: str r2, [r3, #-4]
00048444: b #0x4828c
00048448: b #0x48324
0004844c: ldr r0, [r3, #-4]
00048450: sub r2, r0, #1
00048454: str r2, [r3, #-4]
00048458: b #0x482c4
0004845c: andeq ip, r0, ip, ror r5
00048460: andeq pc, r6, r0, lsr #1
00048464: andeq lr, r0, r4, asr #3
00048468: strdeq r0, r1, [r0], -r4
0004846c: andeq ip, r0, r8, lsl #7
00048470: andeq lr, r0, r8, ror #1
00048474: andeq sp, r0, r8, asr pc
00048478: andeq ip, r0, r0, asr r3
0004847c: muleq r0, r8, r0
00048480: andeq ip, r0, r0, lsr #5
00048484: strdeq sp, lr, [r0], -r8
00048488: andeq sp, r0, r8, ror #28
0004848c: andeq ip, r0, ip, asr r2
00048490: andeq sp, r0, ip, lsl #31
00048494: strheq ip, [r0], -r4
00048498: andeq sp, r0, r4, ror #30
0004849c: andeq ip, r0, r4, lsr #1
000484a0: strdeq sp, lr, [r0], -ip
000484a4: andeq sp, r0, ip, ror #24
000484a8: andeq r0, r0, sb, ror r1
000484ac: andeq ip, r0, ip, asr r0
000484b0: andeq sp, r0, r0, lsr #28
000484b4: andeq ip, r0, ip, lsr #32
000484b8: andeq sp, r0, ip, lsl #27
000484bc: strdeq sp, lr, [r0], -ip
000484c0: andeq r0, r0, pc, ror r1
000484c4: andeq fp, r0, ip, lsl #31
000484c8: andeq sp, r0, r4, ror #26
000484cc: andeq fp, r0, ip, asr pc
000484d0: strheq sp, [r0], -r0
000484d4: strdeq fp, ip, [r0], -r0
000484d8: andeq sp, r0, r4, ror #25
000484dc: ldrdeq sp, lr, [r0], -r0
000484e0: andeq sp, r0, r0, ror #25
000484e4: andeq sp, r0, ip, asr ip
000484e8: andeq sp, r0, r8, lsr ip
000484ec: andeq fp, r0, r4, lsl #28
000484f0: strheq fp, [r0], -r0
000484f4: andeq sp, r0, r4, lsl sb
000484f8: andeq sp, r0, r4, lsl #15
000484fc: andeq r0, r0, sl, ror #2
00048500: andeq fp, r0, r0, ror fp
00048504: andeq sp, r0, r8, lsr #19
00048508: andeq fp, r0, r0, lsr #22
0004850c: andeq sp, r0, ip, ror sb
00048510: andeq sp, r0, ip, lsr sb
00048514: andeq sp, r0, r4, ror #17
00048518: andeq fp, r0, r8, lsl #21
0004851c: strdeq fp, ip, [r0], -r0
00048520: andeq sp, r0, r4, ror #16
00048524: muleq r0, ip, sb
00048528: ldrdeq sp, lr, [r0], -r4
0004852c: andeq fp, r0, r4, lsl #19
00048530: andeq sp, r0, r4, lsl r8
00048534: andeq r0, r0, ip, ror #15
