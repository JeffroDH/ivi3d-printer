08005972: push     {r4, r5, lr}
08005974: sub      sp, #0x1c
08005976: mov      r4, r0
08005978: movs     r5, #0
0800597a: movs     r1, #0x14
0800597c: add      r0, sp, #8
0800597e: bl       #0x8000272
08005982: movs     r0, #0
08005984: str      r0, [sp, #4]
08005986: cmp      r4, #4
08005988: bhs      #0x8005990
0800598a: subs     r0, r0, #1
0800598c: add      sp, #0x1c
0800598e: pop      {r4, r5, pc}
08005990: movs     r0, #0
08005992: str      r0, [sp, #8]
08005994: movs     r0, #2
08005996: str      r0, [sp, #0x18]
08005998: str      r4, [sp, #0x10]
0800599a: movs     r0, #1
0800599c: str      r0, [sp, #0x14]
0800599e: add      r1, sp, #4
080059a0: add      r0, sp, #8
080059a2: bl       #0x8000a58
080059a6: cbz      r0, #0x80059ac
080059a8: mov.w    r5, #-1
080059ac: mov      r0, r5
080059ae: b        #0x800598c
