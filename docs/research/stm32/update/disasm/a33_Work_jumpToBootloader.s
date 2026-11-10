; A33 Work::jumpToBootloader @0x46aec — writes 'M997\n' (literal @0x558f8), sleeps 500 ms, polls for 5-byte reply C4 ?? B0; 3 tries
; source: app.elf (= /userapp/app/IVI-Main-Controller, md5 1339cf97f887753b618c6cf7f2af1e73), ARM mode, vaddr=fileoff+0x8000
; tool: Capstone 5.0.7 (single tool; cross-checked only against the existing Ghidra 12.x decompile in ivi_fwaudit/out/app.c or ivi/supx_decomp.c)

00046aec: ldr r3, [pc, #0x220]
00046af0: push {r4, r5, r6, r7, r8, lr}
00046af4: add r3, pc, r3
00046af8: sub sp, sp, #0x28
00046afc: mov r4, r0
00046b00: ldm r3, {r0, r1}
00046b04: mov r5, #3
00046b08: add r7, sp, #0xc
00046b0c: str r0, [sp, #0xc]
00046b10: strh r1, [sp, #0x10]
00046b14: mvn r2, #0
00046b18: mov r0, sp
00046b1c: mov r1, r7
00046b20: bl #0x13d28
00046b24: ldr r3, [sp]
00046b28: ldr r8, [r4, #0x3c]
00046b2c: ldr r2, [r3]
00046b30: cmp r2, #1
00046b34: bls #0x46be4
00046b38: ldr r1, [r3, #4]
00046b3c: ldrb r2, [r3, #0xb]
00046b40: add r1, r1, #1
00046b44: lsr r2, r2, #7
00046b48: mov r0, sp
00046b4c: bl #0x13cf8
00046b50: ldr ip, [sp]
00046b54: ldr r1, [ip, #0xc]
00046b58: ldr r2, [ip, #4]
00046b5c: mov r0, r8
00046b60: add r1, ip, r1
00046b64: asr r3, r2, #0x1f
00046b68: bl #0x140dc
00046b6c: mov r0, #0x1f4
00046b70: bl #0x139d4
00046b74: mov r0, r4
00046b78: bl #0x46758
00046b7c: mov r0, r4
00046b80: mov r1, #0xa
00046b84: bl #0x46948
00046b88: cmp r0, #0
00046b8c: strb r0, [r4, #0x45]
00046b90: bne #0x46bf8
00046b94: ldr r0, [sp]
00046b98: ldr r2, [r0]
00046b9c: cmp r2, #0
00046ba0: beq #0x46bd4
00046ba4: cmn r2, #1
00046ba8: beq #0x46bc0
00046bac: mov r1, #1
00046bb0: bl #0x531a4
00046bb4: cmp r0, #0
00046bb8: ldreq r0, [sp]
00046bbc: beq #0x46bd4
00046bc0: subs r5, r5, #1
00046bc4: bne #0x46b14
00046bc8: ldrb r0, [r4, #0x45]
00046bcc: add sp, sp, #0x28
00046bd0: pop {r4, r5, r6, r7, r8, pc}
00046bd4: mov r1, #1
00046bd8: mov r2, #4
00046bdc: bl #0x13da0
00046be0: b #0x46bc0
00046be4: ldr r1, [r3, #0xc]
00046be8: mov ip, r3
00046bec: cmp r1, #0x10
00046bf0: bne #0x46b38
00046bf4: b #0x46b58
00046bf8: ldr r2, [pc, #0x118]
00046bfc: add r5, sp, #4
00046c00: mov r3, #0
00046c04: mov ip, #2
00046c08: add r2, pc, r2
00046c0c: mov r0, r5
00046c10: add r1, sp, #0x14
00046c14: str ip, [sp, #0x14]
00046c18: str r3, [sp, #0x18]
00046c1c: str r3, [sp, #0x1c]
00046c20: str r3, [sp, #0x20]
00046c24: str r2, [sp, #0x24]
00046c28: bl #0x13c68
00046c2c: ldr r1, [pc, #0xe8]
00046c30: add r7, sp, #8
00046c34: mov r0, r7
00046c38: add r1, pc, r1
00046c3c: mov r2, #0x11
00046c40: ldr r8, [sp, #4]
00046c44: bl #0x14298
00046c48: mov r0, r8
00046c4c: mov r1, r7
00046c50: bl #0x13674
00046c54: ldr r0, [sp, #8]
00046c58: ldr r3, [r0]
00046c5c: cmp r3, #0
00046c60: beq #0x46cd4
00046c64: cmn r3, #1
00046c68: beq #0x46c80
00046c6c: mov r1, #1
00046c70: bl #0x531a4
00046c74: cmp r0, #0
00046c78: ldreq r0, [sp, #8]
00046c7c: beq #0x46cd4
00046c80: ldr r0, [sp, #4]
00046c84: ldrb r3, [r0, #0x14]
00046c88: cmp r3, #0
00046c8c: bne #0x46ce4
00046c90: mov r0, r5
00046c94: bl #0x14364
00046c98: ldr r0, [sp]
00046c9c: ldr r2, [r0]
00046ca0: cmp r2, #0
00046ca4: beq #0x46cc4
00046ca8: cmn r2, #1
00046cac: beq #0x46bc8
00046cb0: mov r1, #1
00046cb4: bl #0x531a4
00046cb8: cmp r0, #0
00046cbc: ldreq r0, [sp]
00046cc0: bne #0x46bc8
00046cc4: mov r1, #1
00046cc8: mov r2, #4
00046ccc: bl #0x13da0
00046cd0: b #0x46bc8
00046cd4: mov r1, #2
00046cd8: mov r2, #4
00046cdc: bl #0x13da0
00046ce0: b #0x46c80
00046ce4: mov r1, #0x20
00046ce8: bl #0x13974
00046cec: b #0x46c90
00046cf0: mov r0, r7
00046cf4: bl #0x14ef4
00046cf8: mov r0, r5
00046cfc: bl #0x14364
00046d00: mov r0, sp
00046d04: bl #0x14e6c
00046d08: bl #0x14040
00046d0c: b #0x46cf8
00046d10: b #0x46d00
00046d14: strdeq lr, pc, [r0], -ip
00046d18: andeq ip, r0, r4, asr #31
00046d1c: andeq lr, r0, r4, lsr #25
