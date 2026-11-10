; STM32 M997 handler @0x080226E8 -> NVIC_SystemReset @0x08019180 (AIRCR=0x05FA0004|PRIGROUP); no RAM/backup-register flag written
; source: supx_raw.bin base 0x08010000, Thumb-2 M-class
; tool: Capstone 5.0.7 (single tool; cross-checked only against the existing Ghidra 12.x decompile in ivi_fwaudit/out/app.c or ivi/supx_decomp.c)

080226e8: push     {r3, lr}
080226ea: ldr      r3, [pc, #0x6c]
080226ec: ldr      r3, [r3]
080226ee: ubfx     r0, r3, #0x12, #1
080226f2: lsls     r3, r3, #0xd
080226f4: bpl      #0x802271e
080226f6: ldr      r3, [pc, #0x64]
080226f8: ldrb     r2, [r3, #0x12]
080226fa: cbz      r2, #0x8022752
080226fc: ldr      r3, [pc, #0x60]
080226fe: ldr      r1, [r3]
08022700: adds     r3, r1, r2
08022702: ldrb     r2, [r1, r2]
08022704: sub.w    r1, r2, #0x30
08022708: cmp      r1, #9
0802270a: bls      #0x802271a
0802270c: cmp      r2, #0x2e
0802270e: bne      #0x8022738
08022710: ldrb     r2, [r3, #1]
08022712: subs     r2, #0x30
08022714: cmp      r2, #9
08022716: it       hi
08022718: movhi    r3, #0
0802271a: ldr      r2, [pc, #0x48]
0802271c: str      r3, [r2]
0802271e: cbz      r0, #0x8022730
08022720: ldr      r3, [pc, #0x40]
08022722: ldr      r0, [r3]
08022724: cbz      r0, #0x8022730
08022726: movs     r2, #0xa
08022728: movs     r1, #0
0802272a: bl       #0x8032584
0802272e: sxth     r0, r0
08022730: pop.w    {r3, lr}
08022734: b.w      #0x8019180
08022738: cmp      r2, #0x2d
0802273a: beq      #0x8022740
0802273c: cmp      r2, #0x2b
0802273e: bne      #0x8022752
08022740: ldrb     r2, [r3, #1]
08022742: sub.w    r1, r2, #0x30
08022746: cmp      r1, #9
08022748: bls      #0x802271a
0802274a: cmp      r2, #0x2e
0802274c: bne      #0x8022752
0802274e: ldrb     r2, [r3, #2]
08022750: b        #0x8022712
08022752: movs     r3, #0
08022754: b        #0x802271a
08022756: nop      
08022758: ldrsh    r0, [r5, r4]
0802275a: movs     r0, #0
0802275c: ldrsh    r6, [r0, r4]
0802275e: movs     r0, #0

08019180: dsb      sy
08019184: ldr      r1, [pc, #0x14]
08019186: ldr      r3, [pc, #0x18]
08019188: ldr      r2, [r1, #0xc]
0801918a: and      r2, r2, #0x700
0801918e: orrs     r3, r2
08019190: str      r3, [r1, #0xc]
08019192: dsb      sy
08019196: nop      
08019198: b        #0x8019196
0801919a: nop      
0801919c: stc      p0, c14, [r0, #-0]
080191a0: movs     r4, r0
080191a2: lsls     r2, r7, #0x17
080191a4: sub      sp, #8
