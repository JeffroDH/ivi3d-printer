08002f48: ldr      r0, [pc, #0x14] ; [0x08002f60]=0xe000ed88
08002f4a: ldr      r0, [r0]
08002f4c: orr      r0, r0, #0xf00000
08002f50: ldr      r1, [pc, #0xc] ; [0x08002f60]=0xe000ed88
08002f52: str      r0, [r1]
08002f54: mov.w    r0, #0x8000000
08002f58: ldr      r1, [pc, #4] ; [0x08002f60]=0xe000ed88
08002f5a: subs     r1, #0x80
08002f5c: str      r0, [r1]
08002f5e: bx       lr
08002f60: stc      p0, c14, [r8]
