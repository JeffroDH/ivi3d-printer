0802db8c: push     {r4, lr}
0802db8e: movs     r2, #6
0802db90: mov      r4, r0
0802db92: mov.w    r1, #0x1c200
0802db96: ldr      r0, [pc, #0x4c]
0802db98: bl       #0x8010f5c
0802db9c: ldr      r0, [pc, #0x48]
0802db9e: movs     r2, #6
0802dba0: mov.w    r1, #0x1c200
0802dba4: bl       #0x8010f5c
0802dba8: ldr      r0, [pc, #0x40]
0802dbaa: movs     r2, #6
0802dbac: mov.w    r1, #0x1c200
0802dbb0: bl       #0x8010f5c
0802dbb4: ldr      r0, [pc, #0x38]
0802dbb6: movs     r2, #6
0802dbb8: mov.w    r1, #0x1c200
0802dbbc: bl       #0x8010f5c
0802dbc0: movs     r3, #0
0802dbc2: strb     r3, [r4, #0x1a]
0802dbc4: strb     r3, [r4, #0x10]
0802dbc6: str      r3, [r4, #0x1c]
0802dbc8: movs     r3, #0x58
0802dbca: strb.w   r3, [r4, #0x20]
0802dbce: movs     r3, #0x59
0802dbd0: strb.w   r3, [r4, #0x34]
0802dbd4: movs     r3, #0x5a
0802dbd6: strb.w   r3, [r4, #0x48]
0802dbda: movs     r3, #0x45
0802dbdc: strb.w   r3, [r4, #0x5c]
0802dbe0: pop      {r4, pc}
0802dbe2: nop      
0802dbe4: lsls     r4, r4, #0x1b
0802dbe6: movs     r0, #0
0802dbe8: lsrs     r4, r4, #5
0802dbea: movs     r0, #0
0802dbec: lsrs     r4, r4, #0xf
0802dbee: movs     r0, #0
0802dbf0: lsrs     r4, r4, #0x19
0802dbf2: movs     r0, #0
