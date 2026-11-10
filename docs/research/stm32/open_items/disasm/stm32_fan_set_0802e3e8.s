0802e3e8: cmp      r0, #1
0802e3ea: bhi      #0x802e410
0802e3ec: cbnz     r0, #0x802e402
0802e3ee: ldr      r3, [pc, #0x24]
0802e3f0: ldrb     r3, [r3]
0802e3f2: cmp      r3, #3
0802e3f4: bne      #0x802e410
0802e3f6: cbz      r1, #0x802e3fe
0802e3f8: movs     r0, #1
0802e3fa: b.w      #0x80196c8
0802e3fe: b.w      #0x80196c8
0802e402: cbz      r1, #0x802e40a
0802e404: movs     r0, #1
0802e406: b.w      #0x8019700
0802e40a: mov      r0, r1
0802e40c: b.w      #0x8019700
0802e410: bx       lr
0802e412: nop      
0802e414: str      r0, [r0, #0x3c]
0802e416: movs     r0, #0
