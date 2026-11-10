; STM32 USBD_LL_Init @0x08018BC8 — PCD Instance = 0x50000000 (USB_OTG_FS, PA11/PA12), embedded PHY: the USB-C CDC port is the MCU's native USB FS
; source: supx_raw.bin
; tool: Capstone 5.0.7 (single tool; cross-checked only against the existing Ghidra 12.x decompile in ivi_fwaudit/out/app.c or ivi/supx_decomp.c)

08018bc8: push     {r4, r5, r6, lr}
08018bca: mov      r4, r0
08018bcc: bl       #0x8018e00
08018bd0: ldr      r0, [pc, #0x64]
08018bd2: movs     r3, #4
08018bd4: str      r3, [r0, #4]
08018bd6: movs     r3, #0
08018bd8: strd     r3, r3, [r0, #0x24]
08018bdc: strd     r3, r3, [r0, #0x1c]
08018be0: str      r3, [r0, #0x14]
08018be2: mov.w    r2, #0x50000000
08018be6: str      r3, [r0, #0x30]
08018be8: str      r3, [r0, #0x10]
08018bea: str      r3, [r0, #0x2c]
08018bec: str      r3, [r0, #0x34]
08018bee: str.w    r4, [r0, #0x404]
08018bf2: movs     r3, #2
08018bf4: str.w    r0, [r4, #0x2c0]
08018bf8: str      r2, [r0]
08018bfa: str      r3, [r0, #0x18]
08018bfc: str      r3, [r0, #0xc]
08018bfe: bl       #0x8013ca8
08018c02: cbz      r0, #0x8018c0e
08018c04: ldr      r0, [pc, #0x34]
08018c06: mov.w    r1, #0x1f8
08018c0a: bl       #0x8016e7e
08018c0e: ldr      r4, [pc, #0x30]
