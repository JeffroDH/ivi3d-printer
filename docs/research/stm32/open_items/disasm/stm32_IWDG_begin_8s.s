0802fca0: ldr      r3, [pc, #0x34]
0802fca2: push     {r4}
0802fca4: sub.w    r4, r1, #0x7d
0802fca8: cmp      r4, r3
0802fcaa: bhi      #0x802fcd2
0802fcac: ldr      r3, [pc, #0x2c]
0802fcae: ldr      r4, [r3, #0x74]
0802fcb0: orr      r4, r4, #1
0802fcb4: str      r4, [r3, #0x74]
0802fcb6: ldr      r4, [r3, #0x74]
0802fcb8: lsls     r4, r4, #0x1e
0802fcba: bpl      #0x802fcb6
0802fcbc: ldr      r3, [pc, #0x20]
0802fcbe: movw     r4, #0xcccc
0802fcc2: str      r4, [r3]
0802fcc4: ldr      r3, [pc, #0x1c]
0802fcc6: movs     r4, #1
0802fcc8: strb     r4, [r3]
0802fcca: ldr      r4, [sp], #4
0802fcce: b.w      #0x802fc08
0802fcd2: ldr      r4, [sp], #4
0802fcd6: bx       lr
0802fcd8: b        #0x802fd62
0802fcda: lsls     r3, r6, #7
0802fcdc: subs     r0, #0
0802fcde: ands     r2, r0
0802fce0: adds     r0, #0
0802fce2: ands     r0, r0
0802fce4: ldr      r1, [r7, #0x58]
0802fce6: movs     r0, #0
0802fce8: ldr      r3, [pc, #0xc]
0802fcea: ldrb     r3, [r3]
