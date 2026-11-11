08000566: push     {r4, lr}
08000568: sub      sp, #0x18
0800056a: movs     r4, #0
0800056c: movs     r0, #0
0800056e: str      r0, [sp, #0x14]
08000570: str      r0, [sp, #4]
08000572: str      r0, [sp, #8]
08000574: str      r0, [sp, #0xc]
08000576: str      r0, [sp, #0x10]
08000578: nop      
0800057a: b        #0x8000586
0800057c: add.w    r0, r4, #0x61
08000580: add      r1, sp, #4
08000582: strb     r0, [r1, r4]
08000584: adds     r4, r4, #1
08000586: cmp      r4, #0x10
08000588: blt      #0x800057c
0800058a: movs     r0, #0x55
0800058c: strb.w   r0, [sp, #4]
08000590: movs     r0, #0xaa
08000592: strb.w   r0, [sp, #5]
08000596: movs     r2, #0xe
08000598: add      r1, sp, #4
0800059a: add      r0, sp, #0x14
0800059c: bl       #0x8005912
080005a0: ldrh.w   r0, [sp, #0x14]
080005a4: uxtb     r0, r0
080005a6: strb.w   r0, [sp, #0x12]
080005aa: ldrh.w   r0, [sp, #0x14]
080005ae: lsrs     r0, r0, #8
080005b0: strb.w   r0, [sp, #0x13]
080005b4: movs     r2, #0x10
080005b6: add      r1, sp, #4
080005b8: movs     r0, #0x20
080005ba: bl       #0x8000456
080005be: movs     r0, #0
080005c0: add      sp, #0x18
080005c2: pop      {r4, pc}
080005c4: nop      
