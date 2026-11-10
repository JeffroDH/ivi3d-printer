; STM32 flash-EEPROM (STM32duino stm32_eeprom.c style) @0x0801A2FC..0x0801A3E8: sector-select (2 @0x08008000 / 3 @0x0800C000, default 3), buffer fill (memcpy 0x4000), flush = HAL_FLASH_Unlock, HAL_FLASHEx_Erase(sectors, 1 sector, VR=2), word program loop, Lock
; source: supx_raw.bin
; tool: Capstone 5.0.7 (single tool; cross-checked only against the existing Ghidra 12.x decompile in ivi_fwaudit/out/app.c or ivi/supx_decomp.c)

0801a2fc: ldr      r3, [pc, #0xc]
0801a2fe: movs     r2, #2
0801a300: str      r2, [r3]
0801a302: ldr      r3, [pc, #0xc]
0801a304: ldr      r2, [pc, #0xc]
0801a306: str      r2, [r3]
0801a308: bx       lr
0801a30a: nop      
0801a30c: lsls     r4, r1, #7
0801a30e: movs     r0, #0
0801a310: lsls     r0, r1, #7
0801a312: movs     r0, #0
0801a314: strh     r0, [r0]
0801a316: lsrs     r0, r0, #0x20
0801a318: ldr      r3, [pc, #0xc]
0801a31a: movs     r2, #3
0801a31c: str      r2, [r3]
0801a31e: ldr      r3, [pc, #0xc]
0801a320: ldr      r2, [pc, #0xc]
0801a322: str      r2, [r3]
0801a324: bx       lr
0801a326: nop      
0801a328: lsls     r4, r1, #7
0801a32a: movs     r0, #0
0801a32c: lsls     r0, r1, #7
0801a32e: movs     r0, #0

; (continued in pieces; literal pools shown as resolved words)
0801a334: ldr      r3, [pc, #4]
0801a336: ldrb     r0, [r3, r0]
0801a338: bx       lr
0801a33a: nop      
0801a340: ldr      r3, [pc, #4]
0801a342: strb     r1, [r3, r0]
0801a344: bx       lr
0801a346: nop      
0801a34c: push     {r3, lr}
0801a34e: ldr      r3, [pc, #0x10]
0801a350: ldr      r0, [pc, #0x10]
0801a352: ldr      r1, [r3]
0801a354: mov.w    r2, #0x4000
0801a358: bl       #0x8031400
0801a35c: pop      {r3, pc}
0801a35e: nop      
0801a368: push.w   {r4, r5, r6, r7, r8, lr}
0801a36c: ldr      r3, [pc, #0x68]
0801a36e: sub      sp, #0x18
0801a370: ldr      r7, [r3]
0801a372: movs     r3, #0
0801a374: strd     r3, r3, [sp]
0801a378: movs     r3, #2
0801a37a: str      r3, [sp, #0x14]
0801a37c: ldr      r3, [pc, #0x5c]
0801a37e: ldr      r3, [r3]
0801a380: str      r3, [sp, #0xc]
0801a382: movs     r3, #1
0801a384: add.w    r6, r7, #0x3fc0
0801a388: str      r3, [sp, #0x10]
0801a38a: bl       #0x8012bf0
0801a38e: mov      r1, sp
0801a390: add      r0, sp, #4
0801a392: adds     r6, #0x3f
0801a394: bl       #0x8012dd0
0801a398: cbz      r0, #0x801a3cc
0801a39a: mov.w    r4, #-1
0801a39e: bl       #0x8012c14
0801a3a2: mov      r0, r4
0801a3a4: add      sp, #0x18
0801a3a6: pop.w    {r4, r5, r6, r7, r8, pc}
0801a3aa: ldr.w    r2, [r8, r4]
0801a3ae: movs     r3, #0
0801a3b0: mov      r1, r5
0801a3b2: movs     r0, #2
0801a3b4: bl       #0x8012c7c
0801a3b8: cbnz     r0, #0x801a3c6
0801a3ba: adds     r5, #4
0801a3bc: adds     r4, #4
0801a3be: cmp      r5, r6
0801a3c0: bls      #0x801a3aa
0801a3c2: movs     r4, #0
0801a3c4: b        #0x801a39e
0801a3c6: add.w    r5, r7, #0x4000
0801a3ca: b        #0x801a3be
0801a3cc: ldr.w    r8, [pc, #0x10]
0801a3d0: mov      r5, r7
0801a3d2: mov      r4, r0
0801a3d4: b        #0x801a3be
0801a3d6: nop      
; literal @0801a30c = 0x200001cc
; literal @0801a310 = 0x200001c8
; literal @0801a314 = 0x08008000
; literal @0801a328 = 0x200001cc
; literal @0801a32c = 0x200001c8
; literal @0801a330 = 0x0800c000
; literal @0801a360 = 0x200001c8
; literal @0801a364 = 0x2000173c
; literal @0801a3d8 = 0x200001c8
; literal @0801a3dc = 0x200001cc
; literal @0801a3e0 = 0x2000173c
; .data init image: 0x200001c8 = 0x0800c000 (addr), 0x200001cc = 3 (sector)
; 0x08012bf0=HAL_FLASH_Unlock (KEY1 0x45670123 literal @0x08012c10), 0x08012dd0=HAL_FLASHEx_Erase, 0x08012c7c=HAL_FLASH_Program(TYPEPROGRAM_WORD=2), 0x08012c14=HAL_FLASH_Lock [I: HAL names by structure]
