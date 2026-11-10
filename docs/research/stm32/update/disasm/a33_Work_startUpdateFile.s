; A33 Work::startUpdateFile @0x48538 — new QSerialPort ttyUSB0, open(ReadWrite) retried every 50 ms, setRequestToSend(false) @0x48a9c, setDataTerminalReady(true) @0x48b7c, setBaudRate(115200=0x1c200,AllDirections) @0x48bbc, setFlowControl(None) @0x48bc8, jumpToBootloader x4 @0x48bd4, startUpgradeFirmware @0x48cd4, jumpToApp @0x48d1c
; source: app.elf
; tool: Capstone 5.0.7 (single tool; cross-checked only against the existing Ghidra 12.x decompile in ivi_fwaudit/out/app.c or ivi/supx_decomp.c)

00048538: push {r4, r5, r6, r7, r8, sb, sl, fp, lr}
0004853c: ldr r2, [pc, #0xaa8]
00048540: sub sp, sp, #0x54
00048544: add r3, sp, #0x34
00048548: add sb, sp, #0x3c
0004854c: str r3, [sp, #4]
00048550: mov ip, #2
00048554: add r2, pc, r2
00048558: add lr, sp, #0x38
0004855c: mov r8, r0
00048560: mov r6, r1
00048564: mov r0, r3
00048568: mov r1, sb
0004856c: mov r3, #0
00048570: str r2, [sp, #0x4c]
00048574: str lr, [sp, #8]
00048578: str ip, [sp, #0x3c]
0004857c: str r3, [sp, #0x40]
00048580: str r3, [sp, #0x44]
00048584: str r3, [sp, #0x48]
00048588: bl #0x13c68
0004858c: ldr r1, [pc, #0xa5c]
00048590: ldr r5, [pc, #0xa5c]
00048594: add r0, sp, #0x38
00048598: add r1, pc, r1
0004859c: mov r2, #0xc
000485a0: add r5, pc, r5
000485a4: ldr r4, [sp, #0x34]
000485a8: bl #0x14298
000485ac: mov r0, r4
000485b0: add r1, sp, #0x38
000485b4: bl #0x13674
000485b8: ldr r0, [sp, #0x38]
000485bc: ldr r3, [r0]
000485c0: cmp r3, #0
000485c4: beq #0x4871c
000485c8: cmn r3, #1
000485cc: beq #0x485e0
000485d0: mov r1, #1
000485d4: bl #0x531a4
000485d8: cmp r0, #0
000485dc: beq #0x48718
000485e0: ldr r4, [sp, #0x34]
000485e4: ldrb r3, [r4, #0x14]
000485e8: cmp r3, #0
000485ec: bne #0x48704
000485f0: bl #0x13698
000485f4: mov r1, r0
000485f8: mov r0, r4
000485fc: bl #0x13adc
00048600: ldr r0, [sp, #0x34]
00048604: ldrb r3, [r0, #0x14]
00048608: cmp r3, #0
0004860c: bne #0x48758
00048610: add r0, sp, #0x34
00048614: bl #0x14364
00048618: add r3, r8, #0x28
0004861c: str r3, [sp, #0xc]
00048620: mov r3, #1
00048624: strb r3, [r8, #0x24]
00048628: ldr r0, [sp, #0xc]
0004862c: mov r1, r6
00048630: bl #0x13d34
00048634: ldr r2, [pc, #0x9bc]
00048638: mov r3, #0
0004863c: add r2, pc, r2
00048640: mov ip, #2
00048644: add r0, sp, #0x34
00048648: mov r1, sb
0004864c: str r2, [sp, #0x4c]
00048650: str ip, [sp, #0x3c]
00048654: str r3, [sp, #0x40]
00048658: str r3, [sp, #0x44]
0004865c: str r3, [sp, #0x48]
00048660: bl #0x13c68
00048664: ldr r1, [pc, #0x990]
00048668: add r0, sp, #0x38
0004866c: add r1, pc, r1
00048670: mov r2, #0x19
00048674: ldr r4, [sp, #0x34]
00048678: bl #0x14298
0004867c: mov r0, r4
00048680: add r1, sp, #0x38
00048684: bl #0x13674
00048688: ldr r0, [sp, #0x38]
0004868c: ldr r3, [r0]
00048690: cmp r3, #0
00048694: beq #0x48730
00048698: cmn r3, #1
0004869c: beq #0x486b0
000486a0: mov r1, #1
000486a4: bl #0x531a4
000486a8: cmp r0, #0
000486ac: beq #0x4872c
000486b0: ldr r0, [sp, #0x34]
000486b4: ldrb r3, [r0, #0x14]
000486b8: cmp r3, #0
000486bc: bne #0x4874c
000486c0: ldr r3, [r6]
000486c4: add r0, sp, #0x34
000486c8: ldr r1, [r3, #0xc]
000486cc: ldr r2, [r3, #4]
000486d0: add r1, r3, r1
000486d4: bl #0x143b8
000486d8: ldr r0, [sp, #0x34]
000486dc: ldrb r3, [r0, #0x14]
000486e0: cmp r3, #0
000486e4: bne #0x489e4
000486e8: add r0, sp, #0x34
000486ec: bl #0x14364
000486f0: ldrb r3, [r8, #0x24]
000486f4: cmp r3, #0
000486f8: bne #0x48764
000486fc: add sp, sp, #0x54
00048700: pop {r4, r5, r6, r7, r8, sb, sl, fp, pc}
00048704: mov r0, r4
00048708: mov r1, #0x20
0004870c: bl #0x13974
00048710: ldr r4, [sp, #0x34]
00048714: b #0x485f0
00048718: ldr r0, [sp, #0x38]
0004871c: mov r1, #2
00048720: mov r2, #4
00048724: bl #0x13da0
00048728: b #0x485e0
0004872c: ldr r0, [sp, #0x38]
00048730: mov r1, #2
00048734: mov r2, #4
00048738: bl #0x13da0
0004873c: ldr r0, [sp, #0x34]
00048740: ldrb r3, [r0, #0x14]
00048744: cmp r3, #0
00048748: beq #0x486c0
0004874c: mov r1, #0x20
00048750: bl #0x13974
00048754: b #0x486c0
00048758: mov r1, #0x20
0004875c: bl #0x13974
00048760: b #0x48610
00048764: ldr r2, [pc, #0x894]
00048768: mov r3, #0
0004876c: add r2, pc, r2
00048770: mov ip, #2
00048774: add r0, sp, #0x34
00048778: mov r1, sb
0004877c: str r2, [sp, #0x4c]
00048780: str ip, [sp, #0x3c]
00048784: str r3, [sp, #0x40]
00048788: str r3, [sp, #0x44]
0004878c: str r3, [sp, #0x48]
00048790: bl #0x13c68
00048794: ldr r1, [pc, #0x868]
00048798: add r0, sp, #0x38
0004879c: add r1, pc, r1
000487a0: mov r2, #0x19
000487a4: ldr r4, [sp, #0x34]
000487a8: bl #0x14298
000487ac: mov r0, r4
000487b0: add r1, sp, #0x38
000487b4: bl #0x13674
000487b8: ldr r0, [sp, #0x38]
000487bc: ldr r3, [r0]
000487c0: cmp r3, #0
000487c4: beq #0x48d60
000487c8: cmn r3, #1
000487cc: beq #0x487e0
000487d0: mov r1, #1
000487d4: bl #0x531a4
000487d8: cmp r0, #0
000487dc: beq #0x48d5c
000487e0: ldr r0, [sp, #0x34]
000487e4: ldrb r3, [r0, #0x14]
000487e8: cmp r3, #0
000487ec: bne #0x48d7c
000487f0: ldrb r3, [r8, #0x24]
000487f4: ldr r1, [pc, #0x80c]
000487f8: cmp r3, #0
000487fc: add r1, pc, r1
00048800: ldreq r1, [pc, #0x804]
00048804: addeq r1, pc, r1
00048808: bl #0x13524
0004880c: ldr r0, [sp, #0x34]
00048810: ldrb r3, [r0, #0x14]
00048814: cmp r3, #0
00048818: bne #0x48d8c
0004881c: add r0, sp, #0x34
00048820: bl #0x14364
00048824: mov r0, #0xc
00048828: bl #0x13b60
0004882c: mov r1, #0
00048830: mov r4, r0
00048834: bl #0x14220
00048838: cmp r4, #0
0004883c: str r4, [r8, #0x3c]
00048840: beq #0x48ef8
00048844: add sl, sp, #0x10
00048848: mov r0, sl
0004884c: add r4, sp, #0x14
00048850: bl #0x13f80
00048854: mov r0, r4
00048858: bl #0x13c08
0004885c: ldr r3, [sp, #0x14]
00048860: str r3, [sp, #0x3c]
00048864: ldr r2, [r3, #8]
00048868: ldr ip, [r3, #0xc]
0004886c: ldr r1, [pc, #0x79c]
00048870: add ip, ip, #4
00048874: add r2, r2, #4
00048878: ldr r1, [r5, r1]
0004887c: add r2, r3, r2, lsl #2
00048880: mov r0, r4
00048884: add r3, r3, ip, lsl #2
00048888: mov r7, #1
0004888c: str r2, [sp, #0x40]
00048890: str r1, [sp, #0x14]
00048894: str r3, [sp, #0x44]
00048898: str r7, [sp, #0x48]
0004889c: bl #0x45368
000488a0: ldr r2, [sp, #0x48]
000488a4: cmp r2, #0
000488a8: beq #0x48980
000488ac: ldr r3, [sp, #0x40]
000488b0: ldr r1, [sp, #0x44]
000488b4: cmp r3, r1
000488b8: addne r4, sp, #0x18
000488bc: addne r6, r8, #0x38
000488c0: bne #0x48908
000488c4: b #0x48980
000488c8: cmn r2, #1
000488cc: beq #0x488e0
000488d0: mov r1, #1
000488d4: bl #0x531a4
000488d8: cmp r0, #0
000488dc: beq #0x48fbc
000488e0: cmp fp, #0
000488e4: bne #0x48954
000488e8: ldr r3, [sp, #0x40]
000488ec: ldr r1, [sp, #0x44]
000488f0: add r3, r3, #4
000488f4: mov r2, #1
000488f8: str r3, [sp, #0x40]
000488fc: str r7, [sp, #0x48]
00048900: cmp r3, r1
00048904: beq #0x48980
00048908: cmp r2, #0
0004890c: ldr r5, [r3]
00048910: beq #0x488f0
00048914: mov r0, r4
00048918: mov r1, r5
0004891c: bl #0x13ab8
00048920: mov r0, r4
00048924: mov r1, r6
00048928: bl #0x143e8
0004892c: mov fp, r0
00048930: ldr r0, [sp, #0x18]
00048934: ldr r2, [r0]
00048938: cmp r2, #0
0004893c: bne #0x488c8
00048940: mov r1, #2
00048944: mov r2, #4
00048948: bl #0x13da0
0004894c: cmp fp, #0
00048950: beq #0x488e8
00048954: mov r1, r5
00048958: mov r0, sl
0004895c: bl #0x13cec
00048960: ldr r2, [sp, #0x48]
00048964: ldr r3, [sp, #0x40]
00048968: eor r2, r2, #1
0004896c: add r3, r3, #4
00048970: cmp r2, #0
00048974: str r2, [sp, #0x48]
00048978: str r3, [sp, #0x40]
0004897c: bne #0x48fb4
00048980: mov r0, sb
00048984: bl #0x45368
00048988: ldr r0, [r8, #0x3c]
0004898c: mov r1, sl
00048990: bl #0x13aa0
00048994: ldr r0, [r8, #0x3c]
00048998: mov r1, #3
0004899c: ldr r3, [r0]
000489a0: ldr r3, [r3, #0x34]
000489a4: blx r3
000489a8: cmp r0, #0
000489ac: bne #0x489f0
000489b0: bl #0x14184
000489b4: str r0, [sp, #0x3c]
000489b8: mov r1, #0x32
000489bc: mov r0, sb
000489c0: bl #0x14448
000489c4: mov r4, r0
000489c8: bl #0x14184
000489cc: cmp r0, r4
000489d0: bge #0x48994
000489d4: mov r0, #0
000489d8: mov r1, #0xa
000489dc: bl #0x13950
000489e0: b #0x489c8
000489e4: mov r1, #0x20
000489e8: bl #0x13974
000489ec: b #0x486e8
000489f0: ldr r2, [pc, #0x61c]
000489f4: add r4, sp, #0x1c
000489f8: mov r3, #0
000489fc: mov ip, #2
00048a00: add r2, pc, r2
00048a04: mov r0, r4
00048a08: mov r1, sb
00048a0c: str ip, [sp, #0x3c]
00048a10: str r3, [sp, #0x40]
00048a14: str r3, [sp, #0x44]
00048a18: str r3, [sp, #0x48]
00048a1c: str r2, [sp, #0x4c]
00048a20: bl #0x13c68
00048a24: ldr r1, [pc, #0x5ec]
00048a28: add r5, sp, #0x2c
00048a2c: mov r0, r5
00048a30: add r1, pc, r1
00048a34: mov r2, #3
00048a38: ldr r6, [sp, #0x1c]
00048a3c: bl #0x14298
00048a40: mov r0, r6
00048a44: mov r1, r5
00048a48: bl #0x13674
00048a4c: ldr r0, [sp, #0x2c]
00048a50: ldr r3, [r0]
00048a54: cmp r3, #0
00048a58: beq #0x48a78
00048a5c: cmn r3, #1
00048a60: beq #0x48a84
00048a64: mov r1, #1
00048a68: bl #0x531a4
00048a6c: cmp r0, #0
00048a70: ldreq r0, [sp, #0x2c]
00048a74: bne #0x48a84
00048a78: mov r1, #2
00048a7c: mov r2, #4
00048a80: bl #0x13da0
00048a84: ldr r0, [sp, #0x1c]
00048a88: ldrb r3, [r0, #0x14]
00048a8c: cmp r3, #0
00048a90: bne #0x48e8c
00048a94: ldr r0, [r8, #0x3c]
00048a98: mov r1, #0
00048a9c: bl #0x13b24
00048aa0: cmp r0, #0
00048aa4: ldr r0, [sp, #0x1c]
00048aa8: beq #0x48d50
00048aac: ldr r1, [pc, #0x568]
00048ab0: add r1, pc, r1
00048ab4: bl #0x13524
00048ab8: ldr r0, [sp, #0x1c]
00048abc: ldrb r3, [r0, #0x14]
00048ac0: cmp r3, #0
00048ac4: bne #0x48e98
00048ac8: mov r0, r4
00048acc: bl #0x14364
00048ad0: ldr r2, [pc, #0x548]
00048ad4: add r4, sp, #0x20
00048ad8: mov r3, #0
00048adc: mov ip, #2
00048ae0: add r2, pc, r2
00048ae4: mov r0, r4
00048ae8: mov r1, sb
00048aec: str ip, [sp, #0x3c]
00048af0: str r3, [sp, #0x40]
00048af4: str r3, [sp, #0x44]
00048af8: str r3, [sp, #0x48]
00048afc: str r2, [sp, #0x4c]
00048b00: bl #0x13c68
00048b04: ldr r1, [pc, #0x518]
00048b08: add r5, sp, #0x30
00048b0c: mov r0, r5
00048b10: add r1, pc, r1
00048b14: mov r2, #3
00048b18: ldr r6, [sp, #0x20]
00048b1c: bl #0x14298
00048b20: mov r0, r6
00048b24: mov r1, r5
00048b28: bl #0x13674
00048b2c: ldr r0, [sp, #0x30]
00048b30: ldr r3, [r0]
00048b34: cmp r3, #0
00048b38: beq #0x48b58
00048b3c: cmn r3, #1
00048b40: beq #0x48b64
00048b44: mov r1, #1
00048b48: bl #0x531a4
00048b4c: cmp r0, #0
00048b50: ldreq r0, [sp, #0x30]
00048b54: bne #0x48b64
00048b58: mov r1, #2
00048b5c: mov r2, #4
00048b60: bl #0x13da0
00048b64: ldr r0, [sp, #0x20]
00048b68: ldrb r3, [r0, #0x14]
00048b6c: cmp r3, #0
00048b70: bne #0x48ea4
00048b74: ldr r0, [r8, #0x3c]
00048b78: mov r1, #1
00048b7c: bl #0x1422c
00048b80: cmp r0, #0
00048b84: ldr r0, [sp, #0x20]
00048b88: beq #0x48d44
00048b8c: ldr r1, [pc, #0x494]
00048b90: add r1, pc, r1
00048b94: bl #0x13524
00048b98: ldr r0, [sp, #0x20]
00048b9c: ldrb r3, [r0, #0x14]
00048ba0: cmp r3, #0
00048ba4: bne #0x48eb0
00048ba8: mov r0, r4
00048bac: bl #0x14364
00048bb0: ldr r0, [r8, #0x3c]
00048bb4: ldr r1, [pc, #0x470]
00048bb8: mov r2, #3
00048bbc: bl #0x13e3c
00048bc0: ldr r0, [r8, #0x3c]
00048bc4: mov r1, #0
00048bc8: bl #0x13cc8
00048bcc: mov r5, #4
00048bd0: mov r0, r8
00048bd4: bl #0x46aec
00048bd8: mov r4, r0
00048bdc: mov r0, #0xc8
00048be0: bl #0x139d4
00048be4: cmp r4, #0
00048be8: bne #0x48cb8
00048bec: ldr r3, [pc, #0x43c]
00048bf0: add r5, sp, #0x28
00048bf4: mov r2, #2
00048bf8: add r3, pc, r3
00048bfc: mov r1, sb
00048c00: mov r0, r5
00048c04: str r4, [sp, #0x40]
00048c08: str r4, [sp, #0x44]
00048c0c: str r4, [sp, #0x48]
00048c10: str r2, [sp, #0x3c]
00048c14: str r3, [sp, #0x4c]
00048c18: bl #0x13c68
00048c1c: ldr r1, [pc, #0x410]
00048c20: add r0, sp, #0x38
00048c24: add r1, pc, r1
00048c28: mov r2, #0x13
00048c2c: ldr r4, [sp, #0x28]
00048c30: bl #0x14298
00048c34: mov r0, r4
00048c38: add r1, sp, #0x38
00048c3c: bl #0x13674
00048c40: ldr r0, [sp, #0x38]
00048c44: ldr r2, [r0]
00048c48: cmp r2, #0
00048c4c: beq #0x48e60
00048c50: cmn r2, #1
00048c54: beq #0x48c6c
00048c58: mov r1, #1
00048c5c: bl #0x531a4
00048c60: cmp r0, #0
00048c64: ldreq r0, [sp, #0x38]
00048c68: beq #0x48e60
00048c6c: ldr r0, [sp, #0x28]
00048c70: ldrb r2, [r0, #0x14]
00048c74: cmp r2, #0
00048c78: bne #0x48e7c
00048c7c: ldr r1, [pc, #0x3b4]
00048c80: add r1, pc, r1
00048c84: bl #0x13524
00048c88: ldr r0, [sp, #0x28]
00048c8c: ldrb r3, [r0, #0x14]
00048c90: cmp r3, #0
00048c94: bne #0x48eec
00048c98: mov r0, r5
00048c9c: bl #0x14364
00048ca0: mov r0, r8
00048ca4: bl #0x45dd8
00048ca8: mov r0, r8
00048cac: mov r1, #1
00048cb0: bl #0x51d30
00048cb4: b #0x48d34
00048cb8: subs r5, r5, #1
00048cbc: bne #0x48bd0
00048cc0: ldr r1, [sp, #0xc]
00048cc4: mov r0, sb
00048cc8: bl #0x139ec
00048ccc: mov r0, r8
00048cd0: mov r1, sb
00048cd4: bl #0x47614
00048cd8: mov r4, r0
00048cdc: ldr r0, [sp, #0x3c]
00048ce0: ldr r3, [r0]
00048ce4: cmp r3, #0
00048ce8: beq #0x48d98
00048cec: cmn r3, #1
00048cf0: beq #0x48d08
00048cf4: mov r1, #1
00048cf8: bl #0x531a4
00048cfc: cmp r0, #0
00048d00: ldreq r0, [sp, #0x3c]
00048d04: beq #0x48d98
00048d08: cmp r4, #0
00048d0c: bne #0x48dac
00048d10: mov r0, #0x12c
00048d14: bl #0x139d4
00048d18: mov r0, r8
00048d1c: bl #0x4625c
00048d20: mov r0, #0x12c
00048d24: bl #0x139d4
00048d28: mov r0, r8
00048d2c: mov r1, #0
00048d30: bl #0x51d30
00048d34: mov r0, sl
00048d38: bl #0x13f5c
00048d3c: add sp, sp, #0x54
00048d40: pop {r4, r5, r6, r7, r8, sb, sl, fp, pc}
00048d44: ldr r1, [pc, #0x2f0]
00048d48: add r1, pc, r1
00048d4c: b #0x48b94
00048d50: ldr r1, [pc, #0x2e8]
00048d54: add r1, pc, r1
00048d58: b #0x48ab4
00048d5c: ldr r0, [sp, #0x38]
00048d60: mov r1, #2
00048d64: mov r2, #4
00048d68: bl #0x13da0
00048d6c: ldr r0, [sp, #0x34]
00048d70: ldrb r3, [r0, #0x14]
00048d74: cmp r3, #0
00048d78: beq #0x487f0
00048d7c: mov r1, #0x20
00048d80: bl #0x13974
00048d84: ldr r0, [sp, #0x34]
00048d88: b #0x487f0
00048d8c: mov r1, #0x20
00048d90: bl #0x13974
00048d94: b #0x4881c
00048d98: mov r1, #2
00048d9c: mov r2, #4
00048da0: bl #0x13da0
00048da4: cmp r4, #0
00048da8: beq #0x48d10
00048dac: ldr r2, [pc, #0x290]
00048db0: add r5, sp, #0x24
00048db4: mov r3, #0
00048db8: mov ip, #2
00048dbc: add r2, pc, r2
00048dc0: mov r1, sb
00048dc4: mov r0, r5
00048dc8: str ip, [sp, #0x3c]
00048dcc: str r3, [sp, #0x40]
00048dd0: str r3, [sp, #0x44]
00048dd4: str r3, [sp, #0x48]
00048dd8: str r2, [sp, #0x4c]
00048ddc: bl #0x13c68
00048de0: ldr r1, [pc, #0x260]
00048de4: add r0, sp, #0x34
00048de8: add r1, pc, r1
00048dec: mov r2, #0x17
00048df0: ldr r6, [sp, #0x24]
00048df4: bl #0x14298
00048df8: mov r0, r6
00048dfc: add r1, sp, #0x34
00048e00: bl #0x13674
00048e04: ldr r0, [sp, #0x34]
00048e08: ldr r2, [r0]
00048e0c: cmp r2, #0
00048e10: beq #0x48ec0
00048e14: cmn r2, #1
00048e18: beq #0x48e2c
00048e1c: mov r1, #1
00048e20: bl #0x531a4
00048e24: cmp r0, #0
00048e28: beq #0x48ebc
00048e2c: ldr r0, [sp, #0x24]
00048e30: ldrb r2, [r0, #0x14]
00048e34: cmp r2, #0
00048e38: bne #0x48edc
00048e3c: mov r1, r4
00048e40: bl #0x137b8
00048e44: ldr r0, [sp, #0x24]
00048e48: ldrb r3, [r0, #0x14]
00048e4c: cmp r3, #0
00048e50: beq #0x48c98
00048e54: mov r1, #0x20
00048e58: bl #0x13974
00048e5c: b #0x48c98
00048e60: mov r2, #4
00048e64: mov r1, #2
00048e68: bl #0x13da0
00048e6c: ldr r0, [sp, #0x28]
00048e70: ldrb r2, [r0, #0x14]
00048e74: cmp r2, #0
00048e78: beq #0x48c7c
00048e7c: mov r1, #0x20
00048e80: bl #0x13974
00048e84: ldr r0, [sp, #0x28]
00048e88: b #0x48c7c
00048e8c: mov r1, #0x20
00048e90: bl #0x13974
00048e94: b #0x48a94
00048e98: mov r1, #0x20
00048e9c: bl #0x13974
00048ea0: b #0x48ac8
00048ea4: mov r1, #0x20
00048ea8: bl #0x13974
00048eac: b #0x48b74
00048eb0: mov r1, #0x20
00048eb4: bl #0x13974
00048eb8: b #0x48ba8
00048ebc: ldr r0, [sp, #0x34]
00048ec0: mov r2, #4
00048ec4: mov r1, #2
00048ec8: bl #0x13da0
00048ecc: ldr r0, [sp, #0x24]
00048ed0: ldrb r2, [r0, #0x14]
00048ed4: cmp r2, #0
00048ed8: beq #0x48e3c
00048edc: mov r1, #0x20
00048ee0: bl #0x13974
00048ee4: ldr r0, [sp, #0x24]
00048ee8: b #0x48e3c
00048eec: mov r1, #0x20
00048ef0: bl #0x13974
00048ef4: b #0x48c98
00048ef8: ldr r3, [pc, #0x14c]
00048efc: ldr r1, [pc, #0x14c]
00048f00: mov r2, #2
00048f04: add r3, pc, r3
00048f08: mov r0, sb
00048f0c: add r1, pc, r1
00048f10: str r2, [sp, #0x3c]
00048f14: str r3, [sp, #0x4c]
00048f18: str r4, [sp, #0x40]
00048f1c: str r4, [sp, #0x44]
