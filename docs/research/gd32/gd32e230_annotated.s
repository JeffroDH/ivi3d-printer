; GD32E230F4 flash image, base 0x08000000, SHA256 540f4967976e390a5a1822347a148b332ee3da78329d03e1880c851ab17f0167
; Recursive-descent disassembly (Capstone 5, Thumb, M-class, ARMv8-M Baseline). Register names from GD32E23x User Manual;
; Cortex-M23 SCS names (SysTick/NVIC/SCB) from ARMv8-M architecture.

; ===== SECTION: VECTOR TABLE 0x08000000-0x080000CB (51 entries) =====
08000000: .word 0x20000420   ; [ 0] Initial_SP               
08000004: .word 0x080000e1   ; [ 1] Reset                    -> Reset_Handler
08000008: .word 0x08000125   ; [ 2] NMI                      -> NMI_Handler
0800000c: .word 0x08000121   ; [ 3] HardFault                -> HardFault_Handler
08000010: .word 0x00000000   ; [ 4] Reserved                 (unused/0)
08000014: .word 0x00000000   ; [ 5] Reserved                 (unused/0)
08000018: .word 0x00000000   ; [ 6] Reserved                 (unused/0)
0800001c: .word 0x00000000   ; [ 7] Reserved                 (unused/0)
08000020: .word 0x00000000   ; [ 8] Reserved                 (unused/0)
08000024: .word 0x00000000   ; [ 9] Reserved                 (unused/0)
08000028: .word 0x00000000   ; [10] Reserved                 (unused/0)
0800002c: .word 0x08000129   ; [11] SVCall                   -> SVC_Handler
08000030: .word 0x00000000   ; [12] Reserved                 (unused/0)
08000034: .word 0x00000000   ; [13] Reserved                 (unused/0)
08000038: .word 0x08000127   ; [14] PendSV                   -> PendSV_Handler
0800003c: .word 0x08000181   ; [15] SysTick                  -> SysTick_Handler
08000040: .word 0x080000f3   ; [16] WWDGT_IRQ                -> Default_Handler
08000044: .word 0x080000f3   ; [17] LVD_IRQ                  -> Default_Handler
08000048: .word 0x080000f3   ; [18] RTC_IRQ                  -> Default_Handler
0800004c: .word 0x080000f3   ; [19] FMC_IRQ                  -> Default_Handler
08000050: .word 0x080000f3   ; [20] RCU_IRQ                  -> Default_Handler
08000054: .word 0x080000f3   ; [21] EXTI0_1_IRQ              -> Default_Handler
08000058: .word 0x080000f3   ; [22] EXTI2_3_IRQ              -> Default_Handler
0800005c: .word 0x080000f3   ; [23] EXTI4_15_IRQ             -> Default_Handler
08000060: .word 0x00000000   ; [24] Reserved                 (unused/0)
08000064: .word 0x080000f3   ; [25] DMA_CH0_IRQ              -> Default_Handler
08000068: .word 0x080000f3   ; [26] DMA_CH1_2_IRQ            -> Default_Handler
0800006c: .word 0x080000f3   ; [27] DMA_CH3_4_IRQ            -> Default_Handler
08000070: .word 0x080000f3   ; [28] ADC_CMP_IRQ              -> Default_Handler
08000074: .word 0x080000f3   ; [29] TIMER0_BRK_UP_TRG_COM_IRQ -> Default_Handler
08000078: .word 0x080000f3   ; [30] TIMER0_Channel_IRQ       -> Default_Handler
0800007c: .word 0x00000000   ; [31] Reserved                 (unused/0)
08000080: .word 0x080000f3   ; [32] TIMER2_IRQ               -> Default_Handler
08000084: .word 0x080000f3   ; [33] TIMER5_IRQ               -> Default_Handler
08000088: .word 0x00000000   ; [34] Reserved                 (unused/0)
0800008c: .word 0x080000f3   ; [35] TIMER13_IRQ              -> Default_Handler
08000090: .word 0x080000f3   ; [36] TIMER14_IRQ              -> Default_Handler
08000094: .word 0x080000f3   ; [37] TIMER15_IRQ              -> Default_Handler
08000098: .word 0x080000f3   ; [38] TIMER16_IRQ              -> Default_Handler
0800009c: .word 0x080000f3   ; [39] I2C0_EV_IRQ              -> Default_Handler
080000a0: .word 0x080000f3   ; [40] I2C1_EV_IRQ              -> Default_Handler
080000a4: .word 0x080000f3   ; [41] SPI0_IRQ                 -> Default_Handler
080000a8: .word 0x080000f3   ; [42] SPI1_IRQ                 -> Default_Handler
080000ac: .word 0x080000f3   ; [43] USART0_IRQ               -> Default_Handler
080000b0: .word 0x080000f3   ; [44] USART1_IRQ               -> Default_Handler
080000b4: .word 0x00000000   ; [45] Reserved                 (unused/0)
080000b8: .word 0x00000000   ; [46] Reserved                 (unused/0)
080000bc: .word 0x00000000   ; [47] Reserved                 (unused/0)
080000c0: .word 0x080000f3   ; [48] I2C0_ER_IRQ              -> Default_Handler
080000c4: .word 0x00000000   ; [49] Reserved                 (unused/0)
080000c8: .word 0x080000f3   ; [50] I2C1_ER_IRQ              -> Default_Handler

; ===== SECTION: CODE / LITERAL POOLS 0x080000CC-0x08001117 =====

; ---------------------------------------------------------------
; FUNCTION __main @ 0x080000cc   refs: literal@80000f8
;   role: ARM C library entry: SP=0x20000420, then __scatterload (Keil/armcc-style startup)
; ---------------------------------------------------------------
080000cc: 0348      ldr      r0, [pc, #0xc]              ; =0x20000420 SRAM initial SP / top of 0x400 stack
080000ce: 8546      mov      sp, r0                      
080000d0: 00f014f8  bl       #0x80000fc                  ; __scatterload

; ---------------------------------------------------------------
; FUNCTION __rt_entry_jump_main @ 0x080000d4   refs: bl@8000114
;   role: loads &main (0x08000B99) and bx; never returns
; ---------------------------------------------------------------
080000d4: 0048      ldr      r0, [pc, #0]                ; =0x08000b99 code ptr -> main
080000d6: 0047      bx       r0                          
080000d8: .word 0x08000b99            ; LITERAL (ref by 080000d4) code ptr -> main
080000dc: .word 0x20000420            ; LITERAL (ref by 080000cc) SRAM initial SP / top of 0x400 stack

; ---------------------------------------------------------------
; FUNCTION Reset_Handler @ 0x080000e0   refs: vector:Reset
;   role: calls SystemInit (0x0800018C) then __main
; ---------------------------------------------------------------
080000e0: 0448      ldr      r0, [pc, #0x10]             ; =0x0800018d code ptr -> SystemInit
080000e2: 8047      blx      r0                          
080000e4: 0448      ldr      r0, [pc, #0x10]             ; =0x080000cd code ptr -> __main
080000e6: 0047      bx       r0                          
080000e8: fee7      .hword               ; b . (unreferenced default-handler stub)
080000ea: fee7      .hword               ; b . (unreferenced default-handler stub)
080000ec: fee7      .hword               ; b . (unreferenced default-handler stub)
080000ee: fee7      .hword               ; b . (unreferenced default-handler stub)
080000f0: fee7      .hword               ; b . (unreferenced default-handler stub)

; ---------------------------------------------------------------
; FUNCTION Default_Handler @ 0x080000f2   refs: vector:ADC_CMP_IRQ, vector:DMA_CH0_IRQ, vector:DMA_CH1_2_IRQ, vector:DMA_CH3_4_IRQ, vector:EXTI0_1_IRQ, vector:EXTI2_3_IRQ ...
;   role: b . infinite loop; used by ALL 32 peripheral IRQ vectors (no peripheral interrupts used)
; ---------------------------------------------------------------
080000f2: fee7      b        #0x80000f2                  ; Default_Handler
080000f4: .word 0x0800018d            ; LITERAL (ref by 080000e0) code ptr -> SystemInit
080000f8: .word 0x080000cd            ; LITERAL (ref by 080000e4) code ptr -> __main

; ---------------------------------------------------------------
; FUNCTION __scatterload @ 0x080000fc   refs: bl@80000d0
;   role: walks region table 0x08001118..0x08001137 and calls copy/zero handlers, then main
; ---------------------------------------------------------------
080000fc: 064c      ldr      r4, [pc, #0x18]             ; =0x08001118 scatter-load region table start
080000fe: 0125      movs     r5, #1                      
08000100: 064e      ldr      r6, [pc, #0x18]             ; =0x08001138 scatter-load region table end
08000102: 05e0      b        #0x8000110                  
08000104: e368      ldr      r3, [r4, #0xc]              
08000106: 07cc      ldm      r4!, {r0, r1, r2}           
08000108: 2b43      orrs     r3, r5                      
0800010a: 0c3c      subs     r4, #0xc                    
0800010c: 9847      blx      r3                          
0800010e: 1034      adds     r4, #0x10                   
08000110: b442      cmp      r4, r6                      
08000112: f7d3      blo      #0x8000104                  
08000114: fff7deff  bl       #0x80000d4                  ; __rt_entry_jump_main
08000118: .word 0x08001118            ; LITERAL (ref by 080000fc) scatter-load region table start
0800011c: .word 0x08001138            ; LITERAL (ref by 08000100) scatter-load region table end

; ---------------------------------------------------------------
; FUNCTION HardFault_Handler @ 0x08000120   refs: vector:HardFault
;   role: infinite loop
; ---------------------------------------------------------------
08000120: ffe7      b        #0x8000122                  
08000122: fee7      b        #0x8000122                  

; ---------------------------------------------------------------
; FUNCTION NMI_Handler @ 0x08000124   refs: vector:NMI
;   role: empty (bx lr)
; ---------------------------------------------------------------
08000124: 7047      bx       lr                          

; ---------------------------------------------------------------
; FUNCTION PendSV_Handler @ 0x08000126   refs: vector:PendSV
;   role: empty (bx lr)
; ---------------------------------------------------------------
08000126: 7047      bx       lr                          

; ---------------------------------------------------------------
; FUNCTION SVC_Handler @ 0x08000128   refs: vector:SVCall
;   role: empty (bx lr)
; ---------------------------------------------------------------
08000128: 7047      bx       lr                          
0800012a: 0000      .hword               ; zero padding

; ---------------------------------------------------------------
; FUNCTION SysTick_Config @ 0x0800012c   refs: bl@80010bc
;   role: CMSIS: LOAD=ticks-1, prio(SysTick)=3, VAL=0, CTRL=7; returns 1 if ticks>0x1000000
; ---------------------------------------------------------------
0800012c: 80b5      push     {r7, lr}                    
0800012e: 84b0      sub      sp, #0x10                   
08000130: 0290      str      r0, [sp, #8]                
08000132: 0298      ldr      r0, [sp, #8]                
08000134: 401e      subs     r0, r0, #1                  
08000136: 000e      lsrs     r0, r0, #0x18               
08000138: 0028      cmp      r0, #0                      
0800013a: 03d0      beq      #0x8000144                  
0800013c: ffe7      b        #0x800013e                  
0800013e: 0120      movs     r0, #1                      
08000140: 0390      str      r0, [sp, #0xc]              
08000142: 13e0      b        #0x800016c                  
08000144: 0298      ldr      r0, [sp, #8]                
08000146: 401e      subs     r0, r0, #1                  
08000148: 0a49      ldr      r1, [pc, #0x28]             ; =0xe000e014 SysTick_LOAD
0800014a: 0860      str      r0, [r1]                    
0800014c: 0020      movs     r0, #0                      
0800014e: c143      mvns     r1, r0                      
08000150: 0322      movs     r2, #3                      
08000152: 0190      str      r0, [sp, #4]                
08000154: 0846      mov      r0, r1                      
08000156: 1146      mov      r1, r2                      
08000158: 00f06ef8  bl       #0x8000238                  ; NVIC_SetPriority
0800015c: 0648      ldr      r0, [pc, #0x18]             ; =0xe000e018 SysTick_VAL
0800015e: 0199      ldr      r1, [sp, #4]                
08000160: 0160      str      r1, [r0]                    
08000162: 0648      ldr      r0, [pc, #0x18]             ; =0xe000e010 SysTick_CTRL
08000164: 0722      movs     r2, #7                      
08000166: 0260      str      r2, [r0]                    
08000168: 0391      str      r1, [sp, #0xc]              
0800016a: ffe7      b        #0x800016c                  
0800016c: 0398      ldr      r0, [sp, #0xc]              
0800016e: 04b0      add      sp, #0x10                   
08000170: 80bd      pop      {r7, pc}                    
08000172: c046      .hword               ; nop (mov r8,r8) alignment padding
08000174: .word 0xe000e014            ; LITERAL (ref by 08000148) SysTick_LOAD
08000178: .word 0xe000e018            ; LITERAL (ref by 0800015c) SysTick_VAL
0800017c: .word 0xe000e010            ; LITERAL (ref by 08000162) SysTick_CTRL

; ---------------------------------------------------------------
; FUNCTION SysTick_Handler @ 0x08000180   refs: vector:SysTick
;   role: delay_decrement(); tick_increment()
; ---------------------------------------------------------------
08000180: 80b5      push     {r7, lr}                    
08000182: 00f055fb  bl       #0x8000830                  ; delay_decrement
08000186: 00f0afff  bl       #0x80010e8                  ; tick_increment
0800018a: 80bd      pop      {r7, pc}                    

; ---------------------------------------------------------------
; FUNCTION SystemInit @ 0x0800018c   refs: literal@80000f4
;   role: GD32 SystemInit: IRC8M on, reset RCU cfg, system_clock_config(), VTOR=0x08000000
; ---------------------------------------------------------------
0800018c: 80b5      push     {r7, lr}                    
0800018e: 82b0      sub      sp, #8                      
08000190: 2048      ldr      r0, [pc, #0x80]             ; =0x40021000 RCU_CTL0 | RCU_CTL0.IRC8MEN=1
08000192: 0168      ldr      r1, [r0]                    
08000194: 0122      movs     r2, #1                      
08000196: 1143      orrs     r1, r2                      
08000198: 0160      str      r1, [r0]                    
0800019a: ffe7      b        #0x800019c                  
0800019c: 1d48      ldr      r0, [pc, #0x74]             ; =0x40021000 RCU_CTL0
0800019e: 0068      ldr      r0, [r0]                    
080001a0: 8007      lsls     r0, r0, #0x1e               ; wait IRC8MSTB (bit1)
080001a2: 0028      cmp      r0, #0                      
080001a4: 01d4      bmi      #0x80001aa                  
080001a6: ffe7      b        #0x80001a8                  
080001a8: f8e7      b        #0x800019c                  
080001aa: 1b48      ldr      r0, [pc, #0x6c]             ; =0x40021004 RCU_CFG0
080001ac: 0168      ldr      r1, [r0]                    
080001ae: 1b4a      ldr      r2, [pc, #0x6c]             ; =0x08ff000c | CFG0 &= 0x08FF000C (reset SCS/prescalers/CKOUT)
080001b0: 1140      ands     r1, r2                      
080001b2: 0160      str      r1, [r0]                    
080001b4: 0168      ldr      r1, [r0]                    
080001b6: 1a4a      ldr      r2, [pc, #0x68]             ; =0x77c2ffff
080001b8: 1140      ands     r1, r2                      
080001ba: 0160      str      r1, [r0]                    
080001bc: 1548      ldr      r0, [pc, #0x54]             ; =0x40021000 RCU_CTL0
080001be: 0168      ldr      r1, [r0]                    
080001c0: 184a      ldr      r2, [pc, #0x60]             ; =0xfef2ffff | CTL0: clear HXTALEN/HXTALBPS/CKMEN/PLLEN
080001c2: 1140      ands     r1, r2                      
080001c4: 0160      str      r1, [r0]                    
080001c6: 1848      ldr      r0, [pc, #0x60]             ; =0x4002102c RCU_CFG1
080001c8: 0168      ldr      r1, [r0]                    
080001ca: 0f22      movs     r2, #0xf                    ; CFG1.PREDV=0
080001cc: 9143      bics     r1, r2                      
080001ce: 0160      str      r1, [r0]                    
080001d0: 1648      ldr      r0, [pc, #0x58]             ; =0x40021030 RCU_CFG2
080001d2: 0168      ldr      r1, [r0]                    
080001d4: 40f20312  movw     r2, #0x103                  ; CFG2: clear USART0SEL/ADCSEL
080001d8: 9143      bics     r1, r2                      
080001da: 0160      str      r1, [r0]                    
080001dc: 0168      ldr      r1, [r0]                    
080001de: 0122      movs     r2, #1                      
080001e0: 1304      lsls     r3, r2, #0x10               ; CFG2.IRC28MDIV=0
080001e2: 9943      bics     r1, r3                      
080001e4: 0160      str      r1, [r0]                    
080001e6: 0168      ldr      r1, [r0]                    
080001e8: d307      lsls     r3, r2, #0x1f               ; CFG2 bit31 (ADCPSC[2])=0
080001ea: 9943      bics     r1, r3                      
080001ec: 0160      str      r1, [r0]                    
080001ee: 1048      ldr      r0, [pc, #0x40]             ; =0x40021034 RCU_CTL1
080001f0: 0168      ldr      r1, [r0]                    
080001f2: 9143      bics     r1, r2                      ; CTL1.IRC28MEN=0
080001f4: 0160      str      r1, [r0]                    
080001f6: 0f48      ldr      r0, [pc, #0x3c]             ; =0x40021008 RCU_INT
080001f8: 0021      movs     r1, #0                      
080001fa: 0160      str      r1, [r0]                    ; RCU_INT=0 (disable clock IRQs)
080001fc: 0192      str      r2, [sp, #4]                
080001fe: 0091      str      r1, [sp]                    
08000200: 00f050ff  bl       #0x80010a4                  ; system_clock_config
08000204: 0198      ldr      r0, [sp, #4]                
08000206: c006      lsls     r0, r0, #0x1b               ; r0 = 1<<27 = 0x08000000 (NVIC_VECTTAB_FLASH)
08000208: 0099      ldr      r1, [sp]                    
0800020a: 00f0c9fd  bl       #0x8000da0                  ; nvic_vector_table_set
0800020e: 02b0      add      sp, #8                      
08000210: 80bd      pop      {r7, pc}                    
08000212: c046      .hword               ; nop (mov r8,r8) alignment padding
08000214: .word 0x40021000            ; LITERAL (ref by 08000190,0800019c,080001bc) RCU_CTL0
08000218: .word 0x40021004            ; LITERAL (ref by 080001aa) RCU_CFG0
0800021c: .word 0x08ff000c            ; LITERAL (ref by 080001ae)
08000220: .word 0x77c2ffff            ; LITERAL (ref by 080001b6)
08000224: .word 0xfef2ffff            ; LITERAL (ref by 080001c0)
08000228: .word 0x4002102c            ; LITERAL (ref by 080001c6) RCU_CFG1
0800022c: .word 0x40021030            ; LITERAL (ref by 080001d0) RCU_CFG2
08000230: .word 0x40021034            ; LITERAL (ref by 080001ee) RCU_CTL1
08000234: .word 0x40021008            ; LITERAL (ref by 080001f6) RCU_INT

; ---------------------------------------------------------------
; FUNCTION NVIC_SetPriority @ 0x08000238   refs: bl@8000158, bl@80010d4
;   role: CMSIS ARMv8-M baseline (2 prio bits, <<6); IPR for IRQn>=0, SHPR for system exceptions
; ---------------------------------------------------------------
08000238: 70b5      push     {r4, r5, r6, lr}            
0800023a: 82b0      sub      sp, #8                      
0800023c: 0246      mov      r2, r0                      
0800023e: 01ab      add      r3, sp, #4                  
08000240: 1870      strb     r0, [r3]                    
08000242: 0091      str      r1, [sp]                    
08000244: 1878      ldrb     r0, [r3]                    
08000246: 40b2      sxtb     r0, r0                      
08000248: 0028      cmp      r0, #0                      
0800024a: 17d4      bmi      #0x800027c                  
0800024c: ffe7      b        #0x800024e                  
0800024e: 01a8      add      r0, sp, #4                  
08000250: 0178      ldrb     r1, [r0]                    
08000252: 49b2      sxtb     r1, r1                      
08000254: 0322      movs     r2, #3                      
08000256: d243      mvns     r2, r2                      
08000258: 1140      ands     r1, r2                      
0800025a: 184b      ldr      r3, [pc, #0x60]             ; =0xe000e400 NVIC_IPR0
0800025c: c958      ldr      r1, [r1, r3]                
0800025e: 0078      ldrb     r0, [r0]                    
08000260: 40b2      sxtb     r0, r0                      
08000262: 8407      lsls     r4, r0, #0x1e               
08000264: e40e      lsrs     r4, r4, #0x1b               
08000266: ff25      movs     r5, #0xff                   
08000268: a540      lsls     r5, r4                      
0800026a: a943      bics     r1, r5                      
0800026c: 009d      ldr      r5, [sp]                    
0800026e: ad01      lsls     r5, r5, #6                  
08000270: edb2      uxtb     r5, r5                      
08000272: a540      lsls     r5, r4                      
08000274: 2943      orrs     r1, r5                      
08000276: 1040      ands     r0, r2                      
08000278: c150      str      r1, [r0, r3]                
0800027a: 1ae0      b        #0x80002b2                  
0800027c: 01a8      add      r0, sp, #4                  
0800027e: 0178      ldrb     r1, [r0]                    
08000280: 0f22      movs     r2, #0xf                    
08000282: 1140      ands     r1, r2                      
08000284: 0839      subs     r1, #8                      
08000286: 0323      movs     r3, #3                      
08000288: db43      mvns     r3, r3                      
0800028a: 1940      ands     r1, r3                      
0800028c: 0a4c      ldr      r4, [pc, #0x28]             ; =0xe000ed1c SCB_SHPR2
0800028e: 0959      ldr      r1, [r1, r4]                
08000290: 0078      ldrb     r0, [r0]                    
08000292: 40b2      sxtb     r0, r0                      
08000294: 8507      lsls     r5, r0, #0x1e               
08000296: ed0e      lsrs     r5, r5, #0x1b               
08000298: ff26      movs     r6, #0xff                   
0800029a: ae40      lsls     r6, r5                      
0800029c: b143      bics     r1, r6                      
0800029e: 009e      ldr      r6, [sp]                    
080002a0: b601      lsls     r6, r6, #6                  
080002a2: f6b2      uxtb     r6, r6                      
080002a4: ae40      lsls     r6, r5                      
080002a6: 3143      orrs     r1, r6                      
080002a8: 1040      ands     r0, r2                      
080002aa: 0838      subs     r0, #8                      
080002ac: 1840      ands     r0, r3                      
080002ae: 0151      str      r1, [r0, r4]                
080002b0: ffe7      b        #0x80002b2                  
080002b2: 02b0      add      sp, #8                      
080002b4: 70bd      pop      {r4, r5, r6, pc}            
080002b6: c046      .hword               ; nop (mov r8,r8) alignment padding
080002b8: .word 0xe000ed1c            ; LITERAL (ref by 0800028c) SCB_SHPR2
080002bc: .word 0xe000e400            ; LITERAL (ref by 0800025a) NVIC_IPR0

; ---------------------------------------------------------------
; FUNCTION adc_calibration_enable @ 0x080002c0   refs: bl@80003ca
;   role: ADC_CTL1 RSTCLB(bit3) then CLB(bit2), busy-wait each
; ---------------------------------------------------------------
080002c0: 8d48      ldr      r0, [pc, #0x234]            ; =0x40012408 ADC_CTL1
080002c2: 0168      ldr      r1, [r0]                    
080002c4: 0822      movs     r2, #8                      
080002c6: 1143      orrs     r1, r2                      
080002c8: 0160      str      r1, [r0]                    
080002ca: ffe7      b        #0x80002cc                  
080002cc: 8a48      ldr      r0, [pc, #0x228]            ; =0x40012408 ADC_CTL1
080002ce: 0068      ldr      r0, [r0]                    
080002d0: 0007      lsls     r0, r0, #0x1c               
080002d2: 0028      cmp      r0, #0                      
080002d4: 01d5      bpl      #0x80002da                  
080002d6: ffe7      b        #0x80002d8                  
080002d8: f8e7      b        #0x80002cc                  
080002da: 8748      ldr      r0, [pc, #0x21c]            ; =0x40012408 ADC_CTL1
080002dc: 0168      ldr      r1, [r0]                    
080002de: 0422      movs     r2, #4                      
080002e0: 1143      orrs     r1, r2                      
080002e2: 0160      str      r1, [r0]                    
080002e4: ffe7      b        #0x80002e6                  
080002e6: 8448      ldr      r0, [pc, #0x210]            ; =0x40012408 ADC_CTL1
080002e8: 0068      ldr      r0, [r0]                    
080002ea: 4007      lsls     r0, r0, #0x1d               
080002ec: 0028      cmp      r0, #0                      
080002ee: 01d5      bpl      #0x80002f4                  
080002f0: ffe7      b        #0x80002f2                  
080002f2: f8e7      b        #0x80002e6                  
080002f4: 7047      bx       lr                          
080002f6: c046      .hword               ; nop (mov r8,r8) alignment padding

; ---------------------------------------------------------------
; FUNCTION adc_channel_length_config @ 0x080002f8   refs: bl@80003a4
;   role: group 1 (routine): ADC_RSQ0[23:20]=len-1; group 2 branch writes ADC+0x38 (SPL inserted-group code, dead here)
; ---------------------------------------------------------------
080002f8: 83b0      sub      sp, #0xc                    
080002fa: 0246      mov      r2, r0                      
080002fc: 02ab      add      r3, sp, #8                  
080002fe: 1870      strb     r0, [r3]                    
08000300: 0191      str      r1, [sp, #4]                
08000302: 1878      ldrb     r0, [r3]                    
08000304: 0128      cmp      r0, #1                      
08000306: 0090      str      r0, [sp]                    
08000308: 04d0      beq      #0x8000314                  
0800030a: ffe7      b        #0x800030c                  
0800030c: 0098      ldr      r0, [sp]                    
0800030e: 0228      cmp      r0, #2                      
08000310: 0fd0      beq      #0x8000332                  
08000312: 1de0      b        #0x8000350                  
08000314: db48      ldr      r0, [pc, #0x36c]            ; =0x4001242c ADC_RSQ0
08000316: 0168      ldr      r1, [r0]                    
08000318: 0f22      movs     r2, #0xf                    
0800031a: 1205      lsls     r2, r2, #0x14               
0800031c: 9143      bics     r1, r2                      
0800031e: 0160      str      r1, [r0]                    
08000320: 0199      ldr      r1, [sp, #4]                
08000322: 0905      lsls     r1, r1, #0x14               
08000324: 0d4b      ldr      r3, [pc, #0x34]             ; =0xfff00000
08000326: c918      adds     r1, r1, r3                  
08000328: 1140      ands     r1, r2                      
0800032a: 0268      ldr      r2, [r0]                    
0800032c: 0a43      orrs     r2, r1                      
0800032e: 0260      str      r2, [r0]                    
08000330: 0fe0      b        #0x8000352                  
08000332: 0948      ldr      r0, [pc, #0x24]             ; =0x40012438 ADC+0x38 (ADC_ISQ in GD32 SPL headers; not documented in this manual rev; dead branch)
08000334: 0168      ldr      r1, [r0]                    
08000336: 0322      movs     r2, #3                      
08000338: 1205      lsls     r2, r2, #0x14               
0800033a: 9143      bics     r1, r2                      
0800033c: 0160      str      r1, [r0]                    
0800033e: 0199      ldr      r1, [sp, #4]                
08000340: 0905      lsls     r1, r1, #0x14               
08000342: 064b      ldr      r3, [pc, #0x18]             ; =0xfff00000
08000344: c918      adds     r1, r1, r3                  
08000346: 1140      ands     r1, r2                      
08000348: 0268      ldr      r2, [r0]                    
0800034a: 0a43      orrs     r2, r1                      
0800034c: 0260      str      r2, [r0]                    
0800034e: 00e0      b        #0x8000352                  
08000350: ffe7      b        #0x8000352                  
08000352: 03b0      add      sp, #0xc                    
08000354: 7047      bx       lr                          
08000356: c046      .hword               ; nop (mov r8,r8) alignment padding
08000358: .word 0x40012438            ; LITERAL (ref by 08000332) ADC+0x38 (ADC_ISQ in GD32 SPL headers; not documented in this manual rev; dead branch)
0800035c: .word 0xfff00000            ; LITERAL (ref by 08000324,08000342)

; ---------------------------------------------------------------
; FUNCTION adc_init_PA3 @ 0x08000360   refs: bl@8000bb6
;   role: ADC clock (APB2EN.ADCEN), ADC clk=APB2/6, PA3 analog, continuous, SW trigger, right-align, 1 ch, CH3 rank0 239.5cyc, 12-bit, ADC on, 1 ms, calibrate
; ---------------------------------------------------------------
08000360: 80b5      push     {r7, lr}                    
08000362: 84b0      sub      sp, #0x10                   
08000364: 1b48      ldr      r0, [pc, #0x6c]             ; =0x00000609 | 0x609 = (0x18<<6)|9 -> RCU_APB2EN bit9 ADCEN
08000366: 00f005fe  bl       #0x8000f74                  ; rcu_periph_clock_enable
0800036a: 0620      movs     r0, #6                      ; 6 = RCU_ADCCK_APB2_DIV6
0800036c: 00f03efd  bl       #0x8000dec                  ; rcu_adc_clock_config
08000370: 0920      movs     r0, #9                      
08000372: c006      lsls     r0, r0, #0x1b               ; r0 = 9<<27 = 0x48000000 GPIOA
08000374: 0321      movs     r1, #3                      
08000376: 0022      movs     r2, #0                      
08000378: 0823      movs     r3, #8                      ; gpio_mode_set(GPIOA, ANALOG=3, NOPULL, PIN_3)
0800037a: 0391      str      r1, [sp, #0xc]              
0800037c: 0292      str      r2, [sp, #8]                
0800037e: 00f028fb  bl       #0x80009d2                  ; gpio_mode_set
08000382: 0220      movs     r0, #2                      ; 2 = ADC_CONTINUOUS_MODE
08000384: 0121      movs     r1, #1                      
08000386: 0191      str      r1, [sp, #4]                
08000388: 00f0b4f9  bl       #0x80006f4                  ; adc_special_function_config
0800038c: 0720      movs     r0, #7                      
0800038e: 4104      lsls     r1, r0, #0x11               ; (7<<17) = ETSRC SWRCST
08000390: 019a      ldr      r2, [sp, #4]                
08000392: 0090      str      r0, [sp]                    
08000394: 1046      mov      r0, r2                      
08000396: 00f087f8  bl       #0x80004a8                  ; adc_external_trigger_source_config
0800039a: 0298      ldr      r0, [sp, #8]                
0800039c: 00f01cf8  bl       #0x80003d8                  ; adc_data_alignment_config
080003a0: 0198      ldr      r0, [sp, #4]                
080003a2: 0199      ldr      r1, [sp, #4]                
080003a4: fff7a8ff  bl       #0x80002f8                  ; adc_channel_length_config
080003a8: 0298      ldr      r0, [sp, #8]                
080003aa: 0399      ldr      r1, [sp, #0xc]              
080003ac: 009a      ldr      r2, [sp]                    
080003ae: 00f0c5f8  bl       #0x800053c                  ; adc_regular_channel_config | rank 0, ADC_CHANNEL_3, sample time 7 (239.5 cyc)
080003b2: 0198      ldr      r0, [sp, #4]                
080003b4: 0199      ldr      r1, [sp, #4]                
080003b6: 00f033f8  bl       #0x8000420                  ; adc_external_trigger_config
080003ba: 0298      ldr      r0, [sp, #8]                
080003bc: 00f06cf9  bl       #0x8000698                  ; adc_resolution_config
080003c0: 00f020f8  bl       #0x8000404                  ; adc_enable
080003c4: 0198      ldr      r0, [sp, #4]                ; delay_ms(1) before calibration
080003c6: 00f025fa  bl       #0x8000814                  ; delay_ms
080003ca: fff779ff  bl       #0x80002c0                  ; adc_calibration_enable
080003ce: 04b0      add      sp, #0x10                   
080003d0: 80bd      pop      {r7, pc}                    
080003d2: c046      .hword               ; nop (mov r8,r8) alignment padding
080003d4: .word 0x00000609            ; LITERAL (ref by 08000364)

; ---------------------------------------------------------------
; FUNCTION adc_data_alignment_config @ 0x080003d8   refs: bl@800039c
;   role: ADC_CTL1.DAL (bit11): 0=right
; ---------------------------------------------------------------
080003d8: 81b0      sub      sp, #4                      
080003da: 0090      str      r0, [sp]                    
080003dc: 0098      ldr      r0, [sp]                    
080003de: 0028      cmp      r0, #0                      
080003e0: 07d0      beq      #0x80003f2                  
080003e2: ffe7      b        #0x80003e4                  
080003e4: f148      ldr      r0, [pc, #0x3c4]            ; =0x40012408 ADC_CTL1
080003e6: 0168      ldr      r1, [r0]                    
080003e8: 40f60002  movw     r2, #0x800                  
080003ec: 1143      orrs     r1, r2                      
080003ee: 0160      str      r1, [r0]                    
080003f0: 06e0      b        #0x8000400                  
080003f2: ee48      ldr      r0, [pc, #0x3b8]            ; =0x40012408 ADC_CTL1
080003f4: 0168      ldr      r1, [r0]                    
080003f6: 40f60002  movw     r2, #0x800                  
080003fa: 9143      bics     r1, r2                      
080003fc: 0160      str      r1, [r0]                    
080003fe: ffe7      b        #0x8000400                  
08000400: 01b0      add      sp, #4                      
08000402: 7047      bx       lr                          

; ---------------------------------------------------------------
; FUNCTION adc_enable @ 0x08000404   refs: bl@80003c0
;   role: set ADC_CTL1.ADCON if clear
; ---------------------------------------------------------------
08000404: e948      ldr      r0, [pc, #0x3a4]            ; =0x40012408 ADC_CTL1
08000406: 0068      ldr      r0, [r0]                    
08000408: c007      lsls     r0, r0, #0x1f               
0800040a: 0028      cmp      r0, #0                      
0800040c: 06d1      bne      #0x800041c                  
0800040e: ffe7      b        #0x8000410                  
08000410: e648      ldr      r0, [pc, #0x398]            ; =0x40012408 ADC_CTL1
08000412: 0168      ldr      r1, [r0]                    
08000414: 0122      movs     r2, #1                      
08000416: 1143      orrs     r1, r2                      
08000418: 0160      str      r1, [r0]                    
0800041a: ffe7      b        #0x800041c                  
0800041c: 7047      bx       lr                          
0800041e: c046      .hword               ; nop (mov r8,r8) alignment padding

; ---------------------------------------------------------------
; FUNCTION adc_external_trigger_config @ 0x08000420   refs: bl@80003b6
;   role: ADC_CTL1.ETERC (bit20) for group bit0; bit15 for group bit1 (dead branch)
; ---------------------------------------------------------------
08000420: 10b5      push     {r4, lr}                    
08000422: 82b0      sub      sp, #8                      
08000424: 0a46      mov      r2, r1                      
08000426: 0346      mov      r3, r0                      
08000428: 01ac      add      r4, sp, #4                  
0800042a: 2070      strb     r0, [r4]                    
0800042c: 6846      mov      r0, sp                      
0800042e: 0170      strb     r1, [r0]                    
08000430: 0078      ldrb     r0, [r0]                    
08000432: 0028      cmp      r0, #0                      
08000434: 1bd0      beq      #0x800046e                  
08000436: ffe7      b        #0x8000438                  
08000438: 01a8      add      r0, sp, #4                  
0800043a: 0078      ldrb     r0, [r0]                    
0800043c: c007      lsls     r0, r0, #0x1f               
0800043e: 0028      cmp      r0, #0                      
08000440: 07d0      beq      #0x8000452                  
08000442: ffe7      b        #0x8000444                  
08000444: d948      ldr      r0, [pc, #0x364]            ; =0x40012408 ADC_CTL1
08000446: 0168      ldr      r1, [r0]                    
08000448: 0122      movs     r2, #1                      
0800044a: 1205      lsls     r2, r2, #0x14               
0800044c: 1143      orrs     r1, r2                      
0800044e: 0160      str      r1, [r0]                    
08000450: ffe7      b        #0x8000452                  
08000452: 01a8      add      r0, sp, #4                  
08000454: 0078      ldrb     r0, [r0]                    
08000456: 8007      lsls     r0, r0, #0x1e               
08000458: 0028      cmp      r0, #0                      
0800045a: 07d5      bpl      #0x800046c                  
0800045c: ffe7      b        #0x800045e                  
0800045e: d348      ldr      r0, [pc, #0x34c]            ; =0x40012408 ADC_CTL1
08000460: 0168      ldr      r1, [r0]                    
08000462: 48f20002  movw     r2, #0x8000                 
08000466: 1143      orrs     r1, r2                      
08000468: 0160      str      r1, [r0]                    
0800046a: ffe7      b        #0x800046c                  
0800046c: 1ae0      b        #0x80004a4                  
0800046e: 01a8      add      r0, sp, #4                  
08000470: 0078      ldrb     r0, [r0]                    
08000472: c007      lsls     r0, r0, #0x1f               
08000474: 0028      cmp      r0, #0                      
08000476: 07d0      beq      #0x8000488                  
08000478: ffe7      b        #0x800047a                  
0800047a: cc48      ldr      r0, [pc, #0x330]            ; =0x40012408 ADC_CTL1
0800047c: 0168      ldr      r1, [r0]                    
0800047e: 0122      movs     r2, #1                      
08000480: 1205      lsls     r2, r2, #0x14               
08000482: 9143      bics     r1, r2                      
08000484: 0160      str      r1, [r0]                    
08000486: ffe7      b        #0x8000488                  
08000488: 01a8      add      r0, sp, #4                  
0800048a: 0078      ldrb     r0, [r0]                    
0800048c: 8007      lsls     r0, r0, #0x1e               
0800048e: 0028      cmp      r0, #0                      
08000490: 07d5      bpl      #0x80004a2                  
08000492: ffe7      b        #0x8000494                  
08000494: c548      ldr      r0, [pc, #0x314]            ; =0x40012408 ADC_CTL1
08000496: 0168      ldr      r1, [r0]                    
08000498: 48f20002  movw     r2, #0x8000                 
0800049c: 9143      bics     r1, r2                      
0800049e: 0160      str      r1, [r0]                    
080004a0: ffe7      b        #0x80004a2                  
080004a2: ffe7      b        #0x80004a4                  
080004a4: 02b0      add      sp, #8                      
080004a6: 10bd      pop      {r4, pc}                    

; ---------------------------------------------------------------
; FUNCTION adc_external_trigger_source_config @ 0x080004a8   refs: bl@8000396
;   role: ADC_CTL1.ETSRC[19:17]=source (called with 7<<17 = SWRCST)
; ---------------------------------------------------------------
080004a8: 83b0      sub      sp, #0xc                    
080004aa: 0246      mov      r2, r0                      
080004ac: 02ab      add      r3, sp, #8                  
080004ae: 1870      strb     r0, [r3]                    
080004b0: 0191      str      r1, [sp, #4]                
080004b2: 1878      ldrb     r0, [r3]                    
080004b4: 0128      cmp      r0, #1                      
080004b6: 0090      str      r0, [sp]                    
080004b8: 04d0      beq      #0x80004c4                  
080004ba: ffe7      b        #0x80004bc                  
080004bc: 0098      ldr      r0, [sp]                    
080004be: 0228      cmp      r0, #2                      
080004c0: 0bd0      beq      #0x80004da                  
080004c2: 15e0      b        #0x80004f0                  
080004c4: b948      ldr      r0, [pc, #0x2e4]            ; =0x40012408 ADC_CTL1
080004c6: 0168      ldr      r1, [r0]                    
080004c8: 0722      movs     r2, #7                      
080004ca: 5204      lsls     r2, r2, #0x11               
080004cc: 9143      bics     r1, r2                      
080004ce: 0160      str      r1, [r0]                    
080004d0: 0199      ldr      r1, [sp, #4]                
080004d2: 0268      ldr      r2, [r0]                    
080004d4: 0a43      orrs     r2, r1                      
080004d6: 0260      str      r2, [r0]                    
080004d8: 0be0      b        #0x80004f2                  
080004da: b448      ldr      r0, [pc, #0x2d0]            ; =0x40012408 ADC_CTL1
080004dc: 0168      ldr      r1, [r0]                    
080004de: 47f20002  movw     r2, #0x7000                 
080004e2: 9143      bics     r1, r2                      
080004e4: 0160      str      r1, [r0]                    
080004e6: 0199      ldr      r1, [sp, #4]                
080004e8: 0268      ldr      r2, [r0]                    
080004ea: 0a43      orrs     r2, r1                      
080004ec: 0260      str      r2, [r0]                    
080004ee: 00e0      b        #0x80004f2                  
080004f0: ffe7      b        #0x80004f2                  
080004f2: 03b0      add      sp, #0xc                    
080004f4: 7047      bx       lr                          
080004f6: c046      .hword               ; nop (mov r8,r8) alignment padding
080004f8: .word 0x40012408            ; LITERAL (ref by 080002c0,080002cc,080002da,080002e6) ADC_CTL1

; ---------------------------------------------------------------
; FUNCTION adc_flag_clear @ 0x080004fc   refs: bl@8000868
;   role: ADC_STAT &= ~flag
; ---------------------------------------------------------------
080004fc: 81b0      sub      sp, #4                      
080004fe: 0090      str      r0, [sp]                    
08000500: 0098      ldr      r0, [sp]                    
08000502: 0d49      ldr      r1, [pc, #0x34]             ; =0x40012400 ADC_STAT
08000504: 0a68      ldr      r2, [r1]                    
08000506: 8243      bics     r2, r0                      
08000508: 0a60      str      r2, [r1]                    
0800050a: 01b0      add      sp, #4                      
0800050c: 7047      bx       lr                          
0800050e: c046      .hword               ; nop (mov r8,r8) alignment padding

; ---------------------------------------------------------------
; FUNCTION adc_flag_get @ 0x08000510   refs: bl@8000870
;   role: return (ADC_STAT & flag)!=0
; ---------------------------------------------------------------
08000510: 82b0      sub      sp, #8                      
08000512: 0190      str      r0, [sp, #4]                
08000514: 6846      mov      r0, sp                      
08000516: 0021      movs     r1, #0                      
08000518: 0170      strb     r1, [r0]                    
0800051a: 0748      ldr      r0, [pc, #0x1c]             ; =0x40012400 ADC_STAT
0800051c: 0068      ldr      r0, [r0]                    
0800051e: 0199      ldr      r1, [sp, #4]                
08000520: 0842      tst      r0, r1                      
08000522: 04d0      beq      #0x800052e                  
08000524: ffe7      b        #0x8000526                  
08000526: 6846      mov      r0, sp                      
08000528: 0121      movs     r1, #1                      
0800052a: 0170      strb     r1, [r0]                    
0800052c: ffe7      b        #0x800052e                  
0800052e: 6846      mov      r0, sp                      
08000530: 0078      ldrb     r0, [r0]                    
08000532: 02b0      add      sp, #8                      
08000534: 7047      bx       lr                          
08000536: c046      .hword               ; nop (mov r8,r8) alignment padding
08000538: .word 0x40012400            ; LITERAL (ref by 08000502,0800051a) ADC_STAT

; ---------------------------------------------------------------
; FUNCTION adc_regular_channel_config @ 0x0800053c   refs: bl@80003ae, bl@800085c
;   role: RSQ0/1/2 rank slot = channel; SAMPT0/1 sample time
; ---------------------------------------------------------------
0800053c: b0b5      push     {r4, r5, r7, lr}            
0800053e: 85b0      sub      sp, #0x14                   
08000540: 0b46      mov      r3, r1                      
08000542: 0446      mov      r4, r0                      
08000544: 04ad      add      r5, sp, #0x10               
08000546: 2870      strb     r0, [r5]                    
08000548: 03a8      add      r0, sp, #0xc                
0800054a: 0170      strb     r1, [r0]                    
0800054c: 0292      str      r2, [sp, #8]                
0800054e: 2878      ldrb     r0, [r5]                    
08000550: 0528      cmp      r0, #5                      
08000552: 18d8      bhi      #0x8000586                  
08000554: ffe7      b        #0x8000556                  
08000556: 4d48      ldr      r0, [pc, #0x134]            ; =0x40012434 ADC_RSQ2
08000558: 0168      ldr      r1, [r0]                    
0800055a: 0191      str      r1, [sp, #4]                
0800055c: 04a9      add      r1, sp, #0x10               
0800055e: 0a78      ldrb     r2, [r1]                    
08000560: 0523      movs     r3, #5                      
08000562: 1c46      mov      r4, r3                      
08000564: 5443      muls     r4, r2, r4                  
08000566: 1f22      movs     r2, #0x1f                   
08000568: a240      lsls     r2, r4                      
0800056a: 019c      ldr      r4, [sp, #4]                
0800056c: 9443      bics     r4, r2                      
0800056e: 0194      str      r4, [sp, #4]                
08000570: 03aa      add      r2, sp, #0xc                
08000572: 1278      ldrb     r2, [r2]                    
08000574: 0978      ldrb     r1, [r1]                    
08000576: 4b43      muls     r3, r1, r3                  
08000578: 9a40      lsls     r2, r3                      
0800057a: 0199      ldr      r1, [sp, #4]                
0800057c: 1143      orrs     r1, r2                      
0800057e: 0191      str      r1, [sp, #4]                
08000580: 0199      ldr      r1, [sp, #4]                
08000582: 0160      str      r1, [r0]                    
08000584: 40e0      b        #0x8000608                  
08000586: 04a8      add      r0, sp, #0x10               
08000588: 0078      ldrb     r0, [r0]                    
0800058a: 0b28      cmp      r0, #0xb                    
0800058c: 1ad8      bhi      #0x80005c4                  
0800058e: ffe7      b        #0x8000590                  
08000590: 3d48      ldr      r0, [pc, #0xf4]             ; =0x40012430 ADC_RSQ1
08000592: 0168      ldr      r1, [r0]                    
08000594: 0191      str      r1, [sp, #4]                
08000596: 04a9      add      r1, sp, #0x10               
08000598: 0a78      ldrb     r2, [r1]                    
0800059a: 0523      movs     r3, #5                      
0800059c: 1c46      mov      r4, r3                      
0800059e: 5443      muls     r4, r2, r4                  
080005a0: 1e3c      subs     r4, #0x1e                   
080005a2: 1f22      movs     r2, #0x1f                   
080005a4: a240      lsls     r2, r4                      
080005a6: 019c      ldr      r4, [sp, #4]                
080005a8: 9443      bics     r4, r2                      
080005aa: 0194      str      r4, [sp, #4]                
080005ac: 03aa      add      r2, sp, #0xc                
080005ae: 1278      ldrb     r2, [r2]                    
080005b0: 0978      ldrb     r1, [r1]                    
080005b2: 4b43      muls     r3, r1, r3                  
080005b4: 1e3b      subs     r3, #0x1e                   
080005b6: 9a40      lsls     r2, r3                      
080005b8: 0199      ldr      r1, [sp, #4]                
080005ba: 1143      orrs     r1, r2                      
080005bc: 0191      str      r1, [sp, #4]                
080005be: 0199      ldr      r1, [sp, #4]                
080005c0: 0160      str      r1, [r0]                    
080005c2: 20e0      b        #0x8000606                  
080005c4: 04a8      add      r0, sp, #0x10               
080005c6: 0078      ldrb     r0, [r0]                    
080005c8: 0f28      cmp      r0, #0xf                    
080005ca: 1ad8      bhi      #0x8000602                  
080005cc: ffe7      b        #0x80005ce                  
080005ce: 2d48      ldr      r0, [pc, #0xb4]             ; =0x4001242c ADC_RSQ0
080005d0: 0168      ldr      r1, [r0]                    
080005d2: 0191      str      r1, [sp, #4]                
080005d4: 04a9      add      r1, sp, #0x10               
080005d6: 0a78      ldrb     r2, [r1]                    
080005d8: 0523      movs     r3, #5                      
080005da: 1c46      mov      r4, r3                      
080005dc: 5443      muls     r4, r2, r4                  
080005de: 3c3c      subs     r4, #0x3c                   
080005e0: 1f22      movs     r2, #0x1f                   
080005e2: a240      lsls     r2, r4                      
080005e4: 019c      ldr      r4, [sp, #4]                
080005e6: 9443      bics     r4, r2                      
080005e8: 0194      str      r4, [sp, #4]                
080005ea: 03aa      add      r2, sp, #0xc                
080005ec: 1278      ldrb     r2, [r2]                    
080005ee: 0978      ldrb     r1, [r1]                    
080005f0: 4b43      muls     r3, r1, r3                  
080005f2: 3c3b      subs     r3, #0x3c                   
080005f4: 9a40      lsls     r2, r3                      
080005f6: 0199      ldr      r1, [sp, #4]                
080005f8: 1143      orrs     r1, r2                      
080005fa: 0191      str      r1, [sp, #4]                
080005fc: 0199      ldr      r1, [sp, #4]                
080005fe: 0160      str      r1, [r0]                    
08000600: 00e0      b        #0x8000604                  
08000602: ffe7      b        #0x8000604                  
08000604: ffe7      b        #0x8000606                  
08000606: ffe7      b        #0x8000608                  
08000608: 03a8      add      r0, sp, #0xc                
0800060a: 0078      ldrb     r0, [r0]                    
0800060c: 0928      cmp      r0, #9                      
0800060e: 17d8      bhi      #0x8000640                  
08000610: ffe7      b        #0x8000612                  
08000612: 2048      ldr      r0, [pc, #0x80]             ; =0x40012410 ADC_SAMPT1
08000614: 0168      ldr      r1, [r0]                    
08000616: 0091      str      r1, [sp]                    
08000618: 03a9      add      r1, sp, #0xc                
0800061a: 0a78      ldrb     r2, [r1]                    
0800061c: 0323      movs     r3, #3                      
0800061e: 1c46      mov      r4, r3                      
08000620: 5443      muls     r4, r2, r4                  
08000622: 0722      movs     r2, #7                      
08000624: a240      lsls     r2, r4                      
08000626: 009c      ldr      r4, [sp]                    
08000628: 9443      bics     r4, r2                      
0800062a: 0094      str      r4, [sp]                    
0800062c: 029a      ldr      r2, [sp, #8]                
0800062e: 0978      ldrb     r1, [r1]                    
08000630: 4b43      muls     r3, r1, r3                  
08000632: 9a40      lsls     r2, r3                      
08000634: 0099      ldr      r1, [sp]                    
08000636: 1143      orrs     r1, r2                      
08000638: 0091      str      r1, [sp]                    
0800063a: 0099      ldr      r1, [sp]                    
0800063c: 0160      str      r1, [r0]                    
0800063e: 1fe0      b        #0x8000680                  
08000640: 03a8      add      r0, sp, #0xc                
08000642: 0078      ldrb     r0, [r0]                    
08000644: 1228      cmp      r0, #0x12                   
08000646: 19d8      bhi      #0x800067c                  
08000648: ffe7      b        #0x800064a                  
0800064a: 1148      ldr      r0, [pc, #0x44]             ; =0x4001240c ADC_SAMPT0
0800064c: 0168      ldr      r1, [r0]                    
0800064e: 0091      str      r1, [sp]                    
08000650: 03a9      add      r1, sp, #0xc                
08000652: 0a78      ldrb     r2, [r1]                    
08000654: 0323      movs     r3, #3                      
08000656: 1c46      mov      r4, r3                      
08000658: 5443      muls     r4, r2, r4                  
0800065a: 1e3c      subs     r4, #0x1e                   
0800065c: 0722      movs     r2, #7                      
0800065e: a240      lsls     r2, r4                      
08000660: 009c      ldr      r4, [sp]                    
08000662: 9443      bics     r4, r2                      
08000664: 0094      str      r4, [sp]                    
08000666: 029a      ldr      r2, [sp, #8]                
08000668: 0978      ldrb     r1, [r1]                    
0800066a: 4b43      muls     r3, r1, r3                  
0800066c: 1e3b      subs     r3, #0x1e                   
0800066e: 9a40      lsls     r2, r3                      
08000670: 0099      ldr      r1, [sp]                    
08000672: 1143      orrs     r1, r2                      
08000674: 0091      str      r1, [sp]                    
08000676: 0099      ldr      r1, [sp]                    
08000678: 0160      str      r1, [r0]                    
0800067a: 00e0      b        #0x800067e                  
0800067c: ffe7      b        #0x800067e                  
0800067e: ffe7      b        #0x8000680                  
08000680: 05b0      add      sp, #0x14                   
08000682: b0bd      pop      {r4, r5, r7, pc}            
08000684: .word 0x4001242c            ; LITERAL (ref by 08000314,080005ce) ADC_RSQ0
08000688: .word 0x40012430            ; LITERAL (ref by 08000590) ADC_RSQ1
0800068c: .word 0x40012434            ; LITERAL (ref by 08000556) ADC_RSQ2
08000690: .word 0x4001240c            ; LITERAL (ref by 0800064a) ADC_SAMPT0
08000694: .word 0x40012410            ; LITERAL (ref by 08000612) ADC_SAMPT1

; ---------------------------------------------------------------
; FUNCTION adc_resolution_config @ 0x08000698   refs: bl@80003bc
;   role: ADC_CTL0.DRES[25:24] (0 = 12-bit)
; ---------------------------------------------------------------
08000698: 81b0      sub      sp, #4                      
0800069a: 0090      str      r0, [sp]                    
0800069c: 4248      ldr      r0, [pc, #0x108]            ; =0x40012404 ADC_CTL0
0800069e: 0168      ldr      r1, [r0]                    
080006a0: 0322      movs     r2, #3                      
080006a2: 1206      lsls     r2, r2, #0x18               
080006a4: 9143      bics     r1, r2                      
080006a6: 0160      str      r1, [r0]                    
080006a8: 0099      ldr      r1, [sp]                    
080006aa: 0268      ldr      r2, [r0]                    
080006ac: 0a43      orrs     r2, r1                      
080006ae: 0260      str      r2, [r0]                    
080006b0: 01b0      add      sp, #4                      
080006b2: 7047      bx       lr                          

; ---------------------------------------------------------------
; FUNCTION adc_software_trigger_enable @ 0x080006b4   refs: bl@8000862
;   role: ADC_CTL1.SWRCST (bit22) for group bit0
; ---------------------------------------------------------------
080006b4: 81b0      sub      sp, #4                      
080006b6: 0146      mov      r1, r0                      
080006b8: 6a46      mov      r2, sp                      
080006ba: 1070      strb     r0, [r2]                    
080006bc: 1078      ldrb     r0, [r2]                    
080006be: c007      lsls     r0, r0, #0x1f               
080006c0: 0028      cmp      r0, #0                      
080006c2: 07d0      beq      #0x80006d4                  
080006c4: ffe7      b        #0x80006c6                  
080006c6: 3948      ldr      r0, [pc, #0xe4]             ; =0x40012408 ADC_CTL1
080006c8: 0168      ldr      r1, [r0]                    
080006ca: 0122      movs     r2, #1                      
080006cc: 9205      lsls     r2, r2, #0x16               
080006ce: 1143      orrs     r1, r2                      
080006d0: 0160      str      r1, [r0]                    
080006d2: ffe7      b        #0x80006d4                  
080006d4: 6846      mov      r0, sp                      
080006d6: 0078      ldrb     r0, [r0]                    
080006d8: 8007      lsls     r0, r0, #0x1e               
080006da: 0028      cmp      r0, #0                      
080006dc: 07d5      bpl      #0x80006ee                  
080006de: ffe7      b        #0x80006e0                  
080006e0: 3248      ldr      r0, [pc, #0xc8]             ; =0x40012408 ADC_CTL1
080006e2: 0168      ldr      r1, [r0]                    
080006e4: 0122      movs     r2, #1                      
080006e6: 5205      lsls     r2, r2, #0x15               
080006e8: 1143      orrs     r1, r2                      
080006ea: 0160      str      r1, [r0]                    
080006ec: ffe7      b        #0x80006ee                  
080006ee: 01b0      add      sp, #4                      
080006f0: 7047      bx       lr                          
080006f2: c046      .hword               ; nop (mov r8,r8) alignment padding

; ---------------------------------------------------------------
; FUNCTION adc_special_function_config @ 0x080006f4   refs: bl@8000388
;   role: SM (CTL0 bit8) / bit10 / CTN (CTL1 bit1); called with 2 => continuous mode ON
; ---------------------------------------------------------------
080006f4: 82b0      sub      sp, #8                      
080006f6: 0a46      mov      r2, r1                      
080006f8: 0190      str      r0, [sp, #4]                
080006fa: 6846      mov      r0, sp                      
080006fc: 0170      strb     r1, [r0]                    
080006fe: 0078      ldrb     r0, [r0]                    
08000700: 0028      cmp      r0, #0                      
08000702: 27d0      beq      #0x8000754                  
08000704: ffe7      b        #0x8000706                  
08000706: 01a8      add      r0, sp, #4                  
08000708: 4078      ldrb     r0, [r0, #1]                
0800070a: c007      lsls     r0, r0, #0x1f               
0800070c: 0028      cmp      r0, #0                      
0800070e: 07d0      beq      #0x8000720                  
08000710: ffe7      b        #0x8000712                  
08000712: 2548      ldr      r0, [pc, #0x94]             ; =0x40012404 ADC_CTL0
08000714: 0168      ldr      r1, [r0]                    
08000716: 40f20012  movw     r2, #0x100                  
0800071a: 1143      orrs     r1, r2                      
0800071c: 0160      str      r1, [r0]                    
0800071e: ffe7      b        #0x8000720                  
08000720: 01a8      add      r0, sp, #4                  
08000722: 4078      ldrb     r0, [r0, #1]                
08000724: 4007      lsls     r0, r0, #0x1d               
08000726: 0028      cmp      r0, #0                      
08000728: 07d5      bpl      #0x800073a                  
0800072a: ffe7      b        #0x800072c                  
0800072c: 1e48      ldr      r0, [pc, #0x78]             ; =0x40012404 ADC_CTL0
0800072e: 0168      ldr      r1, [r0]                    
08000730: 40f20042  movw     r2, #0x400                  
08000734: 1143      orrs     r1, r2                      
08000736: 0160      str      r1, [r0]                    
08000738: ffe7      b        #0x800073a                  
0800073a: 01a8      add      r0, sp, #4                  
0800073c: 0078      ldrb     r0, [r0]                    
0800073e: 8007      lsls     r0, r0, #0x1e               
08000740: 0028      cmp      r0, #0                      
08000742: 06d5      bpl      #0x8000752                  
08000744: ffe7      b        #0x8000746                  
08000746: 1948      ldr      r0, [pc, #0x64]             ; =0x40012408 ADC_CTL1
08000748: 0168      ldr      r1, [r0]                    
0800074a: 0222      movs     r2, #2                      
0800074c: 1143      orrs     r1, r2                      
0800074e: 0160      str      r1, [r0]                    
08000750: ffe7      b        #0x8000752                  
08000752: 26e0      b        #0x80007a2                  
08000754: 01a8      add      r0, sp, #4                  
08000756: 4078      ldrb     r0, [r0, #1]                
08000758: c007      lsls     r0, r0, #0x1f               
0800075a: 0028      cmp      r0, #0                      
0800075c: 07d0      beq      #0x800076e                  
0800075e: ffe7      b        #0x8000760                  
08000760: 1148      ldr      r0, [pc, #0x44]             ; =0x40012404 ADC_CTL0
08000762: 0168      ldr      r1, [r0]                    
08000764: 40f20012  movw     r2, #0x100                  
08000768: 9143      bics     r1, r2                      
0800076a: 0160      str      r1, [r0]                    
0800076c: ffe7      b        #0x800076e                  
0800076e: 01a8      add      r0, sp, #4                  
08000770: 4078      ldrb     r0, [r0, #1]                
08000772: 4007      lsls     r0, r0, #0x1d               
08000774: 0028      cmp      r0, #0                      
08000776: 07d5      bpl      #0x8000788                  
08000778: ffe7      b        #0x800077a                  
0800077a: 0b48      ldr      r0, [pc, #0x2c]             ; =0x40012404 ADC_CTL0
0800077c: 0168      ldr      r1, [r0]                    
0800077e: 40f20042  movw     r2, #0x400                  
08000782: 9143      bics     r1, r2                      
08000784: 0160      str      r1, [r0]                    
08000786: ffe7      b        #0x8000788                  
08000788: 01a8      add      r0, sp, #4                  
0800078a: 0078      ldrb     r0, [r0]                    
0800078c: 8007      lsls     r0, r0, #0x1e               
0800078e: 0028      cmp      r0, #0                      
08000790: 06d5      bpl      #0x80007a0                  
08000792: ffe7      b        #0x8000794                  
08000794: 0548      ldr      r0, [pc, #0x14]             ; =0x40012408 ADC_CTL1
08000796: 0168      ldr      r1, [r0]                    
08000798: 0222      movs     r2, #2                      
0800079a: 9143      bics     r1, r2                      
0800079c: 0160      str      r1, [r0]                    
0800079e: ffe7      b        #0x80007a0                  
080007a0: ffe7      b        #0x80007a2                  
080007a2: 02b0      add      sp, #8                      
080007a4: 7047      bx       lr                          
080007a6: c046      .hword               ; nop (mov r8,r8) alignment padding
080007a8: .word 0x40012404            ; LITERAL (ref by 0800069c,08000712,0800072c,08000760,0800077a) ADC_CTL0
080007ac: .word 0x40012408            ; LITERAL (ref by 080003e4,080003f2,08000404,08000410,08000444,0800045e,0800047a,08000494,080004c4,080004da,080006c6,080006e0,08000746,08000794) ADC_CTL1

; ---------------------------------------------------------------
; FUNCTION pb1_write @ 0x080007b0   refs: bl@80007f4, bl@8000c04, bl@8000c5a, bl@8000cd6, bl@8000d4a
;   role: arg!=0: GPIOB_BOP=1<<1 (PB1 high) else GPIOB_BC=1<<1 (PB1 low)
; ---------------------------------------------------------------
080007b0: 81b0      sub      sp, #4                      
080007b2: 0146      mov      r1, r0                      
080007b4: 6a46      mov      r2, sp                      
080007b6: 1070      strb     r0, [r2]                    
080007b8: 1078      ldrb     r0, [r2]                    
080007ba: 0028      cmp      r0, #0                      
080007bc: 04d0      beq      #0x80007c8                  
080007be: ffe7      b        #0x80007c0                  
080007c0: 0448      ldr      r0, [pc, #0x10]             ; =0x48000418 GPIOB_BOP
080007c2: 0221      movs     r1, #2                      
080007c4: 0160      str      r1, [r0]                    
080007c6: 03e0      b        #0x80007d0                  
080007c8: 7648      ldr      r0, [pc, #0x1d8]            ; =0x48000428 GPIOB_BC
080007ca: 0221      movs     r1, #2                      
080007cc: 0160      str      r1, [r0]                    
080007ce: ffe7      b        #0x80007d0                  
080007d0: 01b0      add      sp, #4                      
080007d2: 7047      bx       lr                          
080007d4: .word 0x48000418            ; LITERAL (ref by 080007c0) GPIOB_BOP

; ---------------------------------------------------------------
; FUNCTION pa3_low_voltage_check @ 0x080007d8   refs: bl@8000c24
;   role: avg10(ADC CH3) <= 1985 (0x7C1) ? {PB1 high; PA7 high; return 1} : return 0
; ---------------------------------------------------------------
080007d8: 80b5      push     {r7, lr}                    
080007da: 84b0      sub      sp, #0x10                   
080007dc: 0020      movs     r0, #0                      
080007de: 0290      str      r0, [sp, #8]                
080007e0: 00f076f8  bl       #0x80008d0                  ; adc_read_ch3_avg10
080007e4: 0290      str      r0, [sp, #8]                
080007e6: 0298      ldr      r0, [sp, #8]                
080007e8: 0949      ldr      r1, [pc, #0x24]             ; =0x000007c1 | threshold 0x7C1 = 1985 counts (~1.60 V if VREF=VDDA=3.3 V)
080007ea: 8842      cmp      r0, r1                      
080007ec: 09d8      bhi      #0x8000802                  
080007ee: ffe7      b        #0x80007f0                  
080007f0: 0120      movs     r0, #1                      
080007f2: 0190      str      r0, [sp, #4]                
080007f4: fff7dcff  bl       #0x80007b0                  ; pb1_write
080007f8: 00f07af9  bl       #0x8000af0                  ; pa7_set_high
080007fc: 0198      ldr      r0, [sp, #4]                
080007fe: 0390      str      r0, [sp, #0xc]              
08000800: 02e0      b        #0x8000808                  
08000802: 0020      movs     r0, #0                      
08000804: 0390      str      r0, [sp, #0xc]              
08000806: ffe7      b        #0x8000808                  
08000808: 0398      ldr      r0, [sp, #0xc]              
0800080a: 04b0      add      sp, #0x10                   
0800080c: 80bd      pop      {r7, pc}                    
0800080e: c046      .hword               ; nop (mov r8,r8) alignment padding
08000810: .word 0x000007c1            ; LITERAL (ref by 080007e8)

; ---------------------------------------------------------------
; FUNCTION delay_ms @ 0x08000814   refs: bl@80003c6, bl@8000bbe, bl@8000bdc, bl@8000c60, bl@8000cdc, bl@8000d50
;   role: g_delay=ms; spin until SysTick ISR decrements to 0
; ---------------------------------------------------------------
08000814: 81b0      sub      sp, #4                      
08000816: 0090      str      r0, [sp]                    
08000818: 0098      ldr      r0, [sp]                    
0800081a: 0b49      ldr      r1, [pc, #0x2c]             ; =0x20000008 SRAM g_delay_ms (.bss)
0800081c: 0860      str      r0, [r1]                    
0800081e: ffe7      b        #0x8000820                  
08000820: 0948      ldr      r0, [pc, #0x24]             ; =0x20000008 SRAM g_delay_ms (.bss)
08000822: 0068      ldr      r0, [r0]                    
08000824: 0028      cmp      r0, #0                      
08000826: 01d0      beq      #0x800082c                  
08000828: ffe7      b        #0x800082a                  
0800082a: f9e7      b        #0x8000820                  
0800082c: 01b0      add      sp, #4                      
0800082e: 7047      bx       lr                          

; ---------------------------------------------------------------
; FUNCTION delay_decrement @ 0x08000830   refs: bl@8000182
;   role: if (g_delay) g_delay-- (called from SysTick ISR)
; ---------------------------------------------------------------
08000830: 0548      ldr      r0, [pc, #0x14]             ; =0x20000008 SRAM g_delay_ms (.bss)
08000832: 0068      ldr      r0, [r0]                    
08000834: 0028      cmp      r0, #0                      
08000836: 05d0      beq      #0x8000844                  
08000838: ffe7      b        #0x800083a                  
0800083a: 0348      ldr      r0, [pc, #0xc]              ; =0x20000008 SRAM g_delay_ms (.bss)
0800083c: 0168      ldr      r1, [r0]                    
0800083e: 491e      subs     r1, r1, #1                  
08000840: 0160      str      r1, [r0]                    
08000842: ffe7      b        #0x8000844                  
08000844: 7047      bx       lr                          
08000846: c046      .hword               ; nop (mov r8,r8) alignment padding
08000848: .word 0x20000008            ; LITERAL (ref by 0800081a,08000820,08000830,0800083a) SRAM g_delay_ms (.bss)

; ---------------------------------------------------------------
; FUNCTION adc_read_ch3 @ 0x0800084c   refs: bl@80008e4
;   role: rank0=CH3 @7.5cyc, SW trigger, clear EOC, poll EOC (timeout 1,000,000), return ADC_RDATA or -1
; ---------------------------------------------------------------
0800084c: 80b5      push     {r7, lr}                    
0800084e: 86b0      sub      sp, #0x18                   
08000850: 1d48      ldr      r0, [pc, #0x74]             ; =0x000f4240 | timeout = 1,000,000
08000852: 0490      str      r0, [sp, #0x10]             
08000854: 0020      movs     r0, #0                      
08000856: 0321      movs     r1, #3                      ; CH3, sample time 1 (7.5 cyc)
08000858: 0122      movs     r2, #1                      
0800085a: 0392      str      r2, [sp, #0xc]              
0800085c: fff76efe  bl       #0x800053c                  ; adc_regular_channel_config
08000860: 0398      ldr      r0, [sp, #0xc]              
08000862: fff727ff  bl       #0x80006b4                  ; adc_software_trigger_enable
08000866: 0220      movs     r0, #2                      ; 2 = ADC_FLAG_EOC
08000868: fff748fe  bl       #0x80004fc                  ; adc_flag_clear
0800086c: ffe7      b        #0x800086e                  
0800086e: 0220      movs     r0, #2                      
08000870: fff74efe  bl       #0x8000510                  ; adc_flag_get
08000874: 0021      movs     r1, #0                      
08000876: 0128      cmp      r0, #1                      
08000878: 0291      str      r1, [sp, #8]                
0800087a: 0cd0      beq      #0x8000896                  
0800087c: ffe7      b        #0x800087e                  
0800087e: 0498      ldr      r0, [sp, #0x10]             
08000880: 0121      movs     r1, #1                      
08000882: 0022      movs     r2, #0                      
08000884: 0028      cmp      r0, #0                      
08000886: 0192      str      r2, [sp, #4]                
08000888: 0091      str      r1, [sp]                    
0800088a: 01dc      bgt      #0x8000890                  
0800088c: 0198      ldr      r0, [sp, #4]                
0800088e: 0090      str      r0, [sp]                    
08000890: 0098      ldr      r0, [sp]                    
08000892: 0290      str      r0, [sp, #8]                
08000894: ffe7      b        #0x8000896                  
08000896: 0298      ldr      r0, [sp, #8]                
08000898: c007      lsls     r0, r0, #0x1f               
0800089a: 0028      cmp      r0, #0                      
0800089c: 04d0      beq      #0x80008a8                  
0800089e: ffe7      b        #0x80008a0                  
080008a0: 0498      ldr      r0, [sp, #0x10]             
080008a2: 401e      subs     r0, r0, #1                  
080008a4: 0490      str      r0, [sp, #0x10]             
080008a6: e2e7      b        #0x800086e                  
080008a8: 0498      ldr      r0, [sp, #0x10]             
080008aa: 0028      cmp      r0, #0                      
080008ac: 04dc      bgt      #0x80008b8                  
080008ae: ffe7      b        #0x80008b0                  
080008b0: 0020      movs     r0, #0                      
080008b2: c043      mvns     r0, r0                      
080008b4: 0590      str      r0, [sp, #0x14]             
080008b6: 03e0      b        #0x80008c0                  
080008b8: 0448      ldr      r0, [pc, #0x10]             ; =0x4001244c ADC_RDATA
080008ba: 0068      ldr      r0, [r0]                    
080008bc: 0590      str      r0, [sp, #0x14]             
080008be: ffe7      b        #0x80008c0                  
080008c0: 0598      ldr      r0, [sp, #0x14]             
080008c2: 06b0      add      sp, #0x18                   
080008c4: 80bd      pop      {r7, pc}                    
080008c6: c046      .hword               ; nop (mov r8,r8) alignment padding
080008c8: .word 0x000f4240            ; LITERAL (ref by 08000850)
080008cc: .word 0x4001244c            ; LITERAL (ref by 080008b8) ADC_RDATA

; ---------------------------------------------------------------
; FUNCTION adc_read_ch3_avg10 @ 0x080008d0   refs: bl@80007e0
;   role: sum 10 reads / 10 (udiv)
; ---------------------------------------------------------------
080008d0: 80b5      push     {r7, lr}                    
080008d2: 82b0      sub      sp, #8                      
080008d4: 0020      movs     r0, #0                      
080008d6: 0190      str      r0, [sp, #4]                
080008d8: 0090      str      r0, [sp]                    
080008da: ffe7      b        #0x80008dc                  
080008dc: 0098      ldr      r0, [sp]                    
080008de: 0928      cmp      r0, #9                      
080008e0: 0adc      bgt      #0x80008f8                  
080008e2: ffe7      b        #0x80008e4                  
080008e4: fff7b2ff  bl       #0x800084c                  ; adc_read_ch3
080008e8: 0199      ldr      r1, [sp, #4]                
080008ea: 0818      adds     r0, r1, r0                  
080008ec: 0190      str      r0, [sp, #4]                
080008ee: ffe7      b        #0x80008f0                  
080008f0: 0098      ldr      r0, [sp]                    
080008f2: 401c      adds     r0, r0, #1                  
080008f4: 0090      str      r0, [sp]                    
080008f6: f1e7      b        #0x80008dc                  
080008f8: 0198      ldr      r0, [sp, #4]                
080008fa: 0a21      movs     r1, #0xa                    
080008fc: b0fbf1f0  udiv     r0, r0, r1                  
08000900: 02b0      add      sp, #8                      
08000902: 80bd      pop      {r7, pc}                    

; ---------------------------------------------------------------
; FUNCTION gpio_outputs_init @ 0x08000904   refs: bl@8000bae
;   role: clk GPIOA+GPIOB; PA4 out pd, PB1 out pd, PA7 out, PA6 in floating; PA4/PB1/PA7 push-pull 50MHz; drive PA4, PB1, PA7 low
; ---------------------------------------------------------------
08000904: 80b5      push     {r7, lr}                    
08000906: 88b0      sub      sp, #0x20                   
08000908: 9a48      ldr      r0, [pc, #0x268]            ; =0x00000511 | 0x511 = AHBEN bit17 PAEN
0800090a: 00f033fb  bl       #0x8000f74                  ; rcu_periph_clock_enable
0800090e: 2348      ldr      r0, [pc, #0x8c]             ; =0x00000512 | 0x512 = AHBEN bit18 PBEN
08000910: 00f030fb  bl       #0x8000f74                  ; rcu_periph_clock_enable
08000914: 0920      movs     r0, #9                      
08000916: c006      lsls     r0, r0, #0x1b               
08000918: 0121      movs     r1, #1                      
0800091a: 0222      movs     r2, #2                      
0800091c: 1023      movs     r3, #0x10                   
0800091e: 0790      str      r0, [sp, #0x1c]             
08000920: 0691      str      r1, [sp, #0x18]             
08000922: 0592      str      r2, [sp, #0x14]             
08000924: 0493      str      r3, [sp, #0x10]             
08000926: 00f054f8  bl       #0x80009d2                  ; gpio_mode_set | gpio_mode_set(GPIOA, OUTPUT, PULLDOWN, PIN_4)
0800092a: 1d48      ldr      r0, [pc, #0x74]             ; =0x48000400 GPIOB_CTL
0800092c: 0390      str      r0, [sp, #0xc]              
0800092e: 0699      ldr      r1, [sp, #0x18]             
08000930: 059a      ldr      r2, [sp, #0x14]             
08000932: 059b      ldr      r3, [sp, #0x14]             
08000934: 00f04df8  bl       #0x80009d2                  ; gpio_mode_set | gpio_mode_set(GPIOB, OUTPUT, PULLDOWN, PIN_1)
08000938: 0020      movs     r0, #0                      
0800093a: 8021      movs     r1, #0x80                   
0800093c: 079a      ldr      r2, [sp, #0x1c]             
0800093e: 0290      str      r0, [sp, #8]                
08000940: 1046      mov      r0, r2                      
08000942: 069b      ldr      r3, [sp, #0x18]             
08000944: 0191      str      r1, [sp, #4]                
08000946: 1946      mov      r1, r3                      
08000948: 029a      ldr      r2, [sp, #8]                
0800094a: 019b      ldr      r3, [sp, #4]                
0800094c: 00f041f8  bl       #0x80009d2                  ; gpio_mode_set | gpio_mode_set(GPIOA, OUTPUT, NOPULL, PIN_7)
08000950: 4023      movs     r3, #0x40                   
08000952: 0798      ldr      r0, [sp, #0x1c]             
08000954: 0299      ldr      r1, [sp, #8]                
08000956: 029a      ldr      r2, [sp, #8]                
08000958: 00f03bf8  bl       #0x80009d2                  ; gpio_mode_set | gpio_mode_set(GPIOA, INPUT, NOPULL, PIN_6)
0800095c: 0320      movs     r0, #3                      
0800095e: 0799      ldr      r1, [sp, #0x1c]             
08000960: 0090      str      r0, [sp]                    
08000962: 0846      mov      r0, r1                      
08000964: 0299      ldr      r1, [sp, #8]                
08000966: 009a      ldr      r2, [sp]                    
08000968: 049b      ldr      r3, [sp, #0x10]             
0800096a: 00f07af8  bl       #0x8000a62                  ; gpio_output_options_set | gpio_output_options_set(GPIOA, PP, 50MHz, PIN_4)
0800096e: 0398      ldr      r0, [sp, #0xc]              
08000970: 0299      ldr      r1, [sp, #8]                
08000972: 009a      ldr      r2, [sp]                    
08000974: 059b      ldr      r3, [sp, #0x14]             
08000976: 00f074f8  bl       #0x8000a62                  ; gpio_output_options_set | gpio_output_options_set(GPIOB, PP, 50MHz, PIN_1)
0800097a: 0798      ldr      r0, [sp, #0x1c]             
0800097c: 0299      ldr      r1, [sp, #8]                
0800097e: 009a      ldr      r2, [sp]                    
08000980: 019b      ldr      r3, [sp, #4]                
08000982: 00f06ef8  bl       #0x8000a62                  ; gpio_output_options_set | gpio_output_options_set(GPIOA, PP, 50MHz, PIN_7)
08000986: 7e48      ldr      r0, [pc, #0x1f8]            ; =0x48000028 GPIOA_BC
08000988: 0499      ldr      r1, [sp, #0x10]             
0800098a: 0160      str      r1, [r0]                    ; PA4 low
0800098c: 054a      ldr      r2, [pc, #0x14]             ; =0x48000428 GPIOB_BC
0800098e: 059b      ldr      r3, [sp, #0x14]             
08000990: 1360      str      r3, [r2]                    ; PB1 low
08000992: 019a      ldr      r2, [sp, #4]                
08000994: 0260      str      r2, [r0]                    ; PA7 low
08000996: 08b0      add      sp, #0x20                   
08000998: 80bd      pop      {r7, pc}                    
0800099a: c046      .hword               ; nop (mov r8,r8) alignment padding
0800099c: .word 0x00000512            ; LITERAL (ref by 0800090e)
080009a0: .word 0x48000400            ; LITERAL (ref by 0800092a) GPIOB_CTL
080009a4: .word 0x48000428            ; LITERAL (ref by 080007c8,0800098c) GPIOB_BC

; ---------------------------------------------------------------
; FUNCTION gpio_input_bit_get @ 0x080009a8   refs: bl@8000b22, bl@8000fa2
;   role: (GPIOx_ISTAT & pin)!=0
; ---------------------------------------------------------------
080009a8: 83b0      sub      sp, #0xc                    
080009aa: 0190      str      r0, [sp, #4]                
080009ac: 0091      str      r1, [sp]                    
080009ae: 0198      ldr      r0, [sp, #4]                
080009b0: 0069      ldr      r0, [r0, #0x10]             
080009b2: 0099      ldr      r1, [sp]                    
080009b4: 0842      tst      r0, r1                      
080009b6: 04d0      beq      #0x80009c2                  
080009b8: ffe7      b        #0x80009ba                  
080009ba: 02a8      add      r0, sp, #8                  
080009bc: 0121      movs     r1, #1                      
080009be: 0170      strb     r1, [r0]                    
080009c0: 03e0      b        #0x80009ca                  
080009c2: 02a8      add      r0, sp, #8                  
080009c4: 0021      movs     r1, #0                      
080009c6: 0170      strb     r1, [r0]                    
080009c8: ffe7      b        #0x80009ca                  
080009ca: 02a8      add      r0, sp, #8                  
080009cc: 0078      ldrb     r0, [r0]                    
080009ce: 03b0      add      sp, #0xc                    
080009d0: 7047      bx       lr                          

; ---------------------------------------------------------------
; FUNCTION gpio_mode_set @ 0x080009d2   refs: bl@800037e, bl@8000926, bl@8000934, bl@800094c, bl@8000958, bl@8000b12 ...
;   role: GPIOx_CTL 2-bit mode + GPIOx_PUD 2-bit pull per selected pin
; ---------------------------------------------------------------
080009d2: 87b0      sub      sp, #0x1c                   
080009d4: 0690      str      r0, [sp, #0x18]             
080009d6: 0591      str      r1, [sp, #0x14]             
080009d8: 0492      str      r2, [sp, #0x10]             
080009da: 0393      str      r3, [sp, #0xc]              
080009dc: 0698      ldr      r0, [sp, #0x18]             
080009de: 0068      ldr      r0, [r0]                    
080009e0: 0190      str      r0, [sp, #4]                
080009e2: 0698      ldr      r0, [sp, #0x18]             
080009e4: c068      ldr      r0, [r0, #0xc]              
080009e6: 0090      str      r0, [sp]                    
080009e8: 02a8      add      r0, sp, #8                  
080009ea: 0021      movs     r1, #0                      
080009ec: 0180      strh     r1, [r0]                    
080009ee: ffe7      b        #0x80009f0                  
080009f0: 02a8      add      r0, sp, #8                  
080009f2: 0088      ldrh     r0, [r0]                    
080009f4: 0f28      cmp      r0, #0xf                    
080009f6: 2cd8      bhi      #0x8000a52                  
080009f8: ffe7      b        #0x80009fa                  
080009fa: 02a8      add      r0, sp, #8                  
080009fc: 0088      ldrh     r0, [r0]                    
080009fe: 0399      ldr      r1, [sp, #0xc]              
08000a00: c140      lsrs     r1, r0                      
08000a02: c807      lsls     r0, r1, #0x1f               
08000a04: 0028      cmp      r0, #0                      
08000a06: 1ed0      beq      #0x8000a46                  
08000a08: ffe7      b        #0x8000a0a                  
08000a0a: 02a8      add      r0, sp, #8                  
08000a0c: 0188      ldrh     r1, [r0]                    
08000a0e: 4900      lsls     r1, r1, #1                  
08000a10: 0322      movs     r2, #3                      
08000a12: 1346      mov      r3, r2                      
08000a14: 8b40      lsls     r3, r1                      
08000a16: 0199      ldr      r1, [sp, #4]                
08000a18: 9943      bics     r1, r3                      
08000a1a: 0191      str      r1, [sp, #4]                
08000a1c: 0599      ldr      r1, [sp, #0x14]             
08000a1e: 0388      ldrh     r3, [r0]                    
08000a20: 5b00      lsls     r3, r3, #1                  
08000a22: 9940      lsls     r1, r3                      
08000a24: 019b      ldr      r3, [sp, #4]                
08000a26: 0b43      orrs     r3, r1                      
08000a28: 0193      str      r3, [sp, #4]                
08000a2a: 0188      ldrh     r1, [r0]                    
08000a2c: 4900      lsls     r1, r1, #1                  
08000a2e: 8a40      lsls     r2, r1                      
08000a30: 0099      ldr      r1, [sp]                    
08000a32: 9143      bics     r1, r2                      
08000a34: 0091      str      r1, [sp]                    
08000a36: 0499      ldr      r1, [sp, #0x10]             
08000a38: 0088      ldrh     r0, [r0]                    
08000a3a: 4000      lsls     r0, r0, #1                  
08000a3c: 8140      lsls     r1, r0                      
08000a3e: 0098      ldr      r0, [sp]                    
08000a40: 0843      orrs     r0, r1                      
08000a42: 0090      str      r0, [sp]                    
08000a44: ffe7      b        #0x8000a46                  
08000a46: ffe7      b        #0x8000a48                  
08000a48: 0298      ldr      r0, [sp, #8]                
08000a4a: 401c      adds     r0, r0, #1                  
08000a4c: 02a9      add      r1, sp, #8                  
08000a4e: 0880      strh     r0, [r1]                    
08000a50: cee7      b        #0x80009f0                  
08000a52: 0198      ldr      r0, [sp, #4]                
08000a54: 0699      ldr      r1, [sp, #0x18]             
08000a56: 0860      str      r0, [r1]                    
08000a58: 0098      ldr      r0, [sp]                    
08000a5a: 0699      ldr      r1, [sp, #0x18]             
08000a5c: c860      str      r0, [r1, #0xc]              
08000a5e: 07b0      add      sp, #0x1c                   
08000a60: 7047      bx       lr                          

; ---------------------------------------------------------------
; FUNCTION gpio_output_options_set @ 0x08000a62   refs: bl@800096a, bl@8000976, bl@8000982, bl@8000b66
;   role: GPIOx_OMODE (PP/OD) + GPIOx_OSPD per pin
; ---------------------------------------------------------------
08000a62: 10b5      push     {r4, lr}                    
08000a64: 86b0      sub      sp, #0x18                   
08000a66: 0c46      mov      r4, r1                      
08000a68: 0590      str      r0, [sp, #0x14]             
08000a6a: 04a8      add      r0, sp, #0x10               
08000a6c: 0170      strb     r1, [r0]                    
08000a6e: 0392      str      r2, [sp, #0xc]              
08000a70: 0293      str      r3, [sp, #8]                
08000a72: 0078      ldrb     r0, [r0]                    
08000a74: 0128      cmp      r0, #1                      
08000a76: 06d1      bne      #0x8000a86                  
08000a78: ffe7      b        #0x8000a7a                  
08000a7a: 0298      ldr      r0, [sp, #8]                
08000a7c: 0599      ldr      r1, [sp, #0x14]             
08000a7e: 4a68      ldr      r2, [r1, #4]                
08000a80: 0243      orrs     r2, r0                      
08000a82: 4a60      str      r2, [r1, #4]                
08000a84: 05e0      b        #0x8000a92                  
08000a86: 0298      ldr      r0, [sp, #8]                
08000a88: 0599      ldr      r1, [sp, #0x14]             
08000a8a: 4a68      ldr      r2, [r1, #4]                
08000a8c: 8243      bics     r2, r0                      
08000a8e: 4a60      str      r2, [r1, #4]                
08000a90: ffe7      b        #0x8000a92                  
08000a92: 0598      ldr      r0, [sp, #0x14]             
08000a94: 8068      ldr      r0, [r0, #8]                
08000a96: 0090      str      r0, [sp]                    
08000a98: 01a8      add      r0, sp, #4                  
08000a9a: 0021      movs     r1, #0                      
08000a9c: 0180      strh     r1, [r0]                    
08000a9e: ffe7      b        #0x8000aa0                  
08000aa0: 01a8      add      r0, sp, #4                  
08000aa2: 0088      ldrh     r0, [r0]                    
08000aa4: 0f28      cmp      r0, #0xf                    
08000aa6: 1ed8      bhi      #0x8000ae6                  
08000aa8: ffe7      b        #0x8000aaa                  
08000aaa: 01a8      add      r0, sp, #4                  
08000aac: 0088      ldrh     r0, [r0]                    
08000aae: 0299      ldr      r1, [sp, #8]                
08000ab0: c140      lsrs     r1, r0                      
08000ab2: c807      lsls     r0, r1, #0x1f               
08000ab4: 0028      cmp      r0, #0                      
08000ab6: 10d0      beq      #0x8000ada                  
08000ab8: ffe7      b        #0x8000aba                  
08000aba: 01a8      add      r0, sp, #4                  
08000abc: 0188      ldrh     r1, [r0]                    
08000abe: 4900      lsls     r1, r1, #1                  
08000ac0: 0322      movs     r2, #3                      
08000ac2: 8a40      lsls     r2, r1                      
08000ac4: 0099      ldr      r1, [sp]                    
08000ac6: 9143      bics     r1, r2                      
08000ac8: 0091      str      r1, [sp]                    
08000aca: 0399      ldr      r1, [sp, #0xc]              
08000acc: 0088      ldrh     r0, [r0]                    
08000ace: 4000      lsls     r0, r0, #1                  
08000ad0: 8140      lsls     r1, r0                      
08000ad2: 0098      ldr      r0, [sp]                    
08000ad4: 0843      orrs     r0, r1                      
08000ad6: 0090      str      r0, [sp]                    
08000ad8: ffe7      b        #0x8000ada                  
08000ada: ffe7      b        #0x8000adc                  
08000adc: 0198      ldr      r0, [sp, #4]                
08000ade: 401c      adds     r0, r0, #1                  
08000ae0: 01a9      add      r1, sp, #4                  
08000ae2: 0880      strh     r0, [r1]                    
08000ae4: dce7      b        #0x8000aa0                  
08000ae6: 0098      ldr      r0, [sp]                    
08000ae8: 0599      ldr      r1, [sp, #0x14]             
08000aea: 8860      str      r0, [r1, #8]                
08000aec: 06b0      add      sp, #0x18                   
08000aee: 10bd      pop      {r4, pc}                    

; ---------------------------------------------------------------
; FUNCTION pa7_set_high @ 0x08000af0   refs: bl@80007f8
;   role: GPIOA_BOP = 1<<7
; ---------------------------------------------------------------
08000af0: bd48      ldr      r0, [pc, #0x2f4]            ; =0x48000018 GPIOA_BOP
08000af2: 8021      movs     r1, #0x80                   
08000af4: 0160      str      r1, [r0]                    
08000af6: 7047      bx       lr                          

; ---------------------------------------------------------------
; FUNCTION button_pa1_init @ 0x08000af8   refs: bl@8000ba6
;   role: clk GPIOA + SYSCFG(CFGCMP); PA1 input with pull-up
; ---------------------------------------------------------------
08000af8: 80b5      push     {r7, lr}                    
08000afa: 1e48      ldr      r0, [pc, #0x78]             ; =0x00000511 | 0x511 = PAEN
08000afc: 00f03afa  bl       #0x8000f74                  ; rcu_periph_clock_enable
08000b00: 40f20060  movw     r0, #0x600                  ; 0x600 = APB2EN bit0 CFGCMPEN (SYSCFG/CMP clock)
08000b04: 00f036fa  bl       #0x8000f74                  ; rcu_periph_clock_enable
08000b08: 0920      movs     r0, #9                      
08000b0a: c006      lsls     r0, r0, #0x1b               
08000b0c: 0021      movs     r1, #0                      
08000b0e: 0122      movs     r2, #1                      
08000b10: 0223      movs     r3, #2                      
08000b12: fff75eff  bl       #0x80009d2                  ; gpio_mode_set | gpio_mode_set(GPIOA, INPUT, PULLUP, PIN_1)
08000b16: 80bd      pop      {r7, pc}                    

; ---------------------------------------------------------------
; FUNCTION pa1_is_high @ 0x08000b18   refs: bl@8000bd0, bl@8000be0, bl@8000c0a, bl@8000c74, bl@8000cac, bl@8000ce8 ...
;   role: return PA1 level (1 = released / pulled up)
; ---------------------------------------------------------------
08000b18: 80b5      push     {r7, lr}                    
08000b1a: 82b0      sub      sp, #8                      
08000b1c: 0920      movs     r0, #9                      
08000b1e: c006      lsls     r0, r0, #0x1b               
08000b20: 0221      movs     r1, #2                      
08000b22: fff741ff  bl       #0x80009a8                  ; gpio_input_bit_get
08000b26: 0128      cmp      r0, #1                      
08000b28: 03d1      bne      #0x8000b32                  
08000b2a: ffe7      b        #0x8000b2c                  
08000b2c: 0120      movs     r0, #1                      
08000b2e: 0190      str      r0, [sp, #4]                
08000b30: 02e0      b        #0x8000b38                  
08000b32: 0020      movs     r0, #0                      
08000b34: 0190      str      r0, [sp, #4]                
08000b36: ffe7      b        #0x8000b38                  
08000b38: 0198      ldr      r0, [sp, #4]                
08000b3a: 02b0      add      sp, #8                      
08000b3c: 80bd      pop      {r7, pc}                    
08000b3e: 0000      .hword               ; zero padding

; ---------------------------------------------------------------
; FUNCTION led_pa2_init @ 0x08000b40   refs: bl@8000bb2
;   role: clk GPIOA; PA2 output push-pull 50MHz; PA2 high
; ---------------------------------------------------------------
08000b40: 80b5      push     {r7, lr}                    
08000b42: 84b0      sub      sp, #0x10                   
08000b44: 0b48      ldr      r0, [pc, #0x2c]             ; =0x00000511
08000b46: 00f015fa  bl       #0x8000f74                  ; rcu_periph_clock_enable
08000b4a: 0920      movs     r0, #9                      
08000b4c: c006      lsls     r0, r0, #0x1b               
08000b4e: 0121      movs     r1, #1                      
08000b50: 0022      movs     r2, #0                      
08000b52: 0423      movs     r3, #4                      
08000b54: 0390      str      r0, [sp, #0xc]              
08000b56: 0292      str      r2, [sp, #8]                
08000b58: 0193      str      r3, [sp, #4]                
08000b5a: fff73aff  bl       #0x80009d2                  ; gpio_mode_set | gpio_mode_set(GPIOA, OUTPUT, NOPULL, PIN_2)
08000b5e: 0322      movs     r2, #3                      
08000b60: 0398      ldr      r0, [sp, #0xc]              
08000b62: 0299      ldr      r1, [sp, #8]                
08000b64: 019b      ldr      r3, [sp, #4]                
08000b66: fff77cff  bl       #0x8000a62                  ; gpio_output_options_set | gpio_output_options_set(GPIOA, PP, 50MHz, PIN_2)
08000b6a: 9f48      ldr      r0, [pc, #0x27c]            ; =0x48000018 GPIOA_BOP
08000b6c: 0199      ldr      r1, [sp, #4]                
08000b6e: 0160      str      r1, [r0]                    ; PA2 high
08000b70: 04b0      add      sp, #0x10                   
08000b72: 80bd      pop      {r7, pc}                    
08000b74: .word 0x00000511            ; LITERAL (ref by 08000908,08000afa,08000b44)

; ---------------------------------------------------------------
; FUNCTION pa2_low @ 0x08000b78   refs: bl@8000bca
;   role: GPIOA_BC = 1<<2
; ---------------------------------------------------------------
08000b78: 9a48      ldr      r0, [pc, #0x268]            ; =0x48000028 GPIOA_BC
08000b7a: 0421      movs     r1, #4                      
08000b7c: 0160      str      r1, [r0]                    
08000b7e: 7047      bx       lr                          
08000b80: .word 0x48000028            ; LITERAL (ref by 08000986) GPIOA_BC

; ---------------------------------------------------------------
; FUNCTION pa2_high @ 0x08000b84   refs: bl@8000bf6, bl@8000d72
;   role: GPIOA_BOP = 1<<2
; ---------------------------------------------------------------
08000b84: 9848      ldr      r0, [pc, #0x260]            ; =0x48000018 GPIOA_BOP
08000b86: 0421      movs     r1, #4                      
08000b88: 0160      str      r1, [r0]                    
08000b8a: 7047      bx       lr                          

; ---------------------------------------------------------------
; FUNCTION pa2_toggle @ 0x08000b8c   refs: bl@8000c9a, bl@8000d2e
;   role: GPIOA_TG = 1<<2
; ---------------------------------------------------------------
08000b8c: 0148      ldr      r0, [pc, #4]                ; =0x4800002c GPIOA_TG
08000b8e: 0421      movs     r1, #4                      
08000b90: 0160      str      r1, [r0]                    
08000b92: 7047      bx       lr                          
08000b94: .word 0x4800002c            ; LITERAL (ref by 08000b8c) GPIOA_TG

; ---------------------------------------------------------------
; FUNCTION main @ 0x08000b98   refs: literal@80000d8
;   role: soft-power state machine: standby/wait button -> power on -> monitor button + PA3 voltage
; ---------------------------------------------------------------
08000b98: 80b5      push     {r7, lr}                    
08000b9a: 8cb0      sub      sp, #0x30                   
08000b9c: 0020      movs     r0, #0                      
08000b9e: 0b90      str      r0, [sp, #0x2c]             
08000ba0: 0a90      str      r0, [sp, #0x28]             
08000ba2: 7748      ldr      r0, [pc, #0x1dc]            ; =0x00000bb8 | hold_timeout = 3000 ms
08000ba4: 0990      str      r0, [sp, #0x24]             
08000ba6: fff7a7ff  bl       #0x8000af8                  ; button_pa1_init
08000baa: 00f07ffa  bl       #0x80010ac                  ; systick_config_1ms
08000bae: fff7a9fe  bl       #0x8000904                  ; gpio_outputs_init
08000bb2: fff7c5ff  bl       #0x8000b40                  ; led_pa2_init
08000bb6: fff7d3fb  bl       #0x8000360                  ; adc_init_PA3
08000bba: 40f2f410  movw     r0, #0x1f4                  ; delay_ms(500)
08000bbe: fff729fe  bl       #0x8000814                  ; delay_ms
08000bc2: 7048      ldr      r0, [pc, #0x1c0]            ; =0x20000014 SRAM g_mode (.bss, write-only)
08000bc4: 0221      movs     r1, #2                      
08000bc6: 0160      str      r1, [r0]                    ; g_mode(0x20000014)=2 (write-only variable)
08000bc8: ffe7      b        #0x8000bca                  
08000bca: fff7d5ff  bl       #0x8000b78                  ; pa2_low | STANDBY: PA2 low
08000bce: ffe7      b        #0x8000bd0                  
08000bd0: fff7a2ff  bl       #0x8000b18                  ; pa1_is_high
08000bd4: 0028      cmp      r0, #0                      
08000bd6: 0dd1      bne      #0x8000bf4                  
08000bd8: ffe7      b        #0x8000bda                  
08000bda: 3220      movs     r0, #0x32                   ; debounce 50 ms
08000bdc: fff71afe  bl       #0x8000814                  ; delay_ms
08000be0: fff79aff  bl       #0x8000b18                  ; pa1_is_high
08000be4: 0028      cmp      r0, #0                      
08000be6: 04d1      bne      #0x8000bf2                  
08000be8: ffe7      b        #0x8000bea                  
08000bea: 6748      ldr      r0, [pc, #0x19c]            ; =0x20000004 SRAM g_btn_last (.data, init 1)
08000bec: 0021      movs     r1, #0                      
08000bee: 0160      str      r1, [r0]                    ; g_btn_last=0 (pressed)
08000bf0: 01e0      b        #0x8000bf6                  
08000bf2: ffe7      b        #0x8000bf4                  
08000bf4: ece7      b        #0x8000bd0                  
08000bf6: fff7c5ff  bl       #0x8000b84                  ; pa2_high | POWER ON: PA2 high, PA4 high, PB1 high
08000bfa: 0120      movs     r0, #1                      
08000bfc: 0790      str      r0, [sp, #0x1c]             
08000bfe: 00f0dff8  bl       #0x8000dc0                  ; pa4_write
08000c02: 0798      ldr      r0, [sp, #0x1c]             
08000c04: fff7d4fd  bl       #0x80007b0                  ; pb1_write
08000c08: ffe7      b        #0x8000c0a                  
08000c0a: fff785ff  bl       #0x8000b18                  ; pa1_is_high | wait for button release
08000c0e: 0028      cmp      r0, #0                      
08000c10: 01d1      bne      #0x8000c16                  
08000c12: ffe7      b        #0x8000c14                  
08000c14: f9e7      b        #0x8000c0a                  
08000c16: 5c48      ldr      r0, [pc, #0x170]            ; =0x20000004 SRAM g_btn_last (.data, init 1)
08000c18: 0121      movs     r1, #1                      
08000c1a: 0160      str      r1, [r0]                    ; g_btn_last=1; g_mode=0
08000c1c: 5948      ldr      r0, [pc, #0x164]            ; =0x20000014 SRAM g_mode (.bss, write-only)
08000c1e: 0021      movs     r1, #0                      
08000c20: 0160      str      r1, [r0]                    
08000c22: ffe7      b        #0x8000c24                  
08000c24: fff7d8fd  bl       #0x80007d8                  ; pa3_low_voltage_check | MAIN LOOP
08000c28: 0028      cmp      r0, #0                      
08000c2a: 20d0      beq      #0x8000c6e                  
08000c2c: ffe7      b        #0x8000c2e                  
08000c2e: 00f057fa  bl       #0x80010e0                  ; get_tick_ms | PA3 low -> latched shutdown loop (never exits)
08000c32: 0a90      str      r0, [sp, #0x28]             
08000c34: ffe7      b        #0x8000c36                  
08000c36: 00f0aff9  bl       #0x8000f98                  ; pa6_is_high
08000c3a: 0028      cmp      r0, #0                      
08000c3c: 03d0      beq      #0x8000c46                  
08000c3e: ffe7      b        #0x8000c40                  
08000c40: 5648      ldr      r0, [pc, #0x158]            ; =0x00001770 | PA6 high -> hold_timeout = 6000 ms
08000c42: 0990      str      r0, [sp, #0x24]             
08000c44: ffe7      b        #0x8000c46                  
08000c46: 00f04bfa  bl       #0x80010e0                  ; get_tick_ms
08000c4a: 0a99      ldr      r1, [sp, #0x28]             
08000c4c: 401a      subs     r0, r0, r1                  
08000c4e: 0999      ldr      r1, [sp, #0x24]             
08000c50: 8842      cmp      r0, r1                      
08000c52: 0bd9      bls      #0x8000c6c                  
08000c54: ffe7      b        #0x8000c56                  
08000c56: 0020      movs     r0, #0                      
08000c58: 0690      str      r0, [sp, #0x18]             
08000c5a: fff7a9fd  bl       #0x80007b0                  ; pb1_write | PB1 low; 10 ms; PA4 low (repeats forever)
08000c5e: 0a20      movs     r0, #0xa                    
08000c60: fff7d8fd  bl       #0x8000814                  ; delay_ms
08000c64: 0698      ldr      r0, [sp, #0x18]             
08000c66: 00f0abf8  bl       #0x8000dc0                  ; pa4_write
08000c6a: ffe7      b        #0x8000c6c                  
08000c6c: e3e7      b        #0x8000c36                  
08000c6e: 4648      ldr      r0, [pc, #0x118]            ; =0x20000004 SRAM g_btn_last (.data, init 1)
08000c70: 0068      ldr      r0, [r0]                    
08000c72: 0590      str      r0, [sp, #0x14]             
08000c74: fff750ff  bl       #0x8000b18                  ; pa1_is_high
08000c78: 0599      ldr      r1, [sp, #0x14]             
08000c7a: 8142      cmp      r1, r0                      
08000c7c: 13d0      beq      #0x8000ca6                  
08000c7e: ffe7      b        #0x8000c80                  
08000c80: 4148      ldr      r0, [pc, #0x104]            ; =0x20000004 SRAM g_btn_last (.data, init 1)
08000c82: 0068      ldr      r0, [r0]                    
08000c84: 0128      cmp      r0, #1                      
08000c86: 0ed1      bne      #0x8000ca6                  
08000c88: ffe7      b        #0x8000c8a                  
08000c8a: 3f48      ldr      r0, [pc, #0xfc]             ; =0x20000004 SRAM g_btn_last (.data, init 1)
08000c8c: 0021      movs     r1, #0                      
08000c8e: 0160      str      r1, [r0]                    ; press edge: g_btn_last=0, g_press_tick=now, toggle PA2, g_blink=0
08000c90: 0491      str      r1, [sp, #0x10]             
08000c92: 00f025fa  bl       #0x80010e0                  ; get_tick_ms
08000c96: 3e49      ldr      r1, [pc, #0xf8]             ; =0x2000000c SRAM g_press_tick (.bss)
08000c98: 0860      str      r0, [r1]                    
08000c9a: fff777ff  bl       #0x8000b8c                  ; pa2_toggle
08000c9e: 3b48      ldr      r0, [pc, #0xec]             ; =0x20000010 SRAM g_blink_count (.bss)
08000ca0: 0499      ldr      r1, [sp, #0x10]             
08000ca2: 0160      str      r1, [r0]                    
08000ca4: 6ae0      b        #0x8000d7c                  
08000ca6: 3848      ldr      r0, [pc, #0xe0]             ; =0x20000004 SRAM g_btn_last (.data, init 1)
08000ca8: 0068      ldr      r0, [r0]                    
08000caa: 0390      str      r0, [sp, #0xc]              
08000cac: fff734ff  bl       #0x8000b18                  ; pa1_is_high
08000cb0: 0399      ldr      r1, [sp, #0xc]              
08000cb2: 8142      cmp      r1, r0                      
08000cb4: 20d0      beq      #0x8000cf8                  
08000cb6: ffe7      b        #0x8000cb8                  
08000cb8: 3348      ldr      r0, [pc, #0xcc]             ; =0x20000004 SRAM g_btn_last (.data, init 1)
08000cba: 0068      ldr      r0, [r0]                    
08000cbc: 0028      cmp      r0, #0                      
08000cbe: 1bd1      bne      #0x8000cf8                  
08000cc0: ffe7      b        #0x8000cc2                  
08000cc2: 3148      ldr      r0, [pc, #0xc4]             ; =0x20000004 SRAM g_btn_last (.data, init 1)
08000cc4: 0121      movs     r1, #1                      
08000cc6: 0160      str      r1, [r0]                    ; release edge: g_btn_last=1
08000cc8: 3048      ldr      r0, [pc, #0xc0]             ; =0x20000010 SRAM g_blink_count (.bss)
08000cca: 0068      ldr      r0, [r0]                    
08000ccc: 0628      cmp      r0, #6                      ; if g_blink>=6 -> power off
08000cce: 12d3      blo      #0x8000cf6                  
08000cd0: ffe7      b        #0x8000cd2                  
08000cd2: 0020      movs     r0, #0                      
08000cd4: 0290      str      r0, [sp, #8]                
08000cd6: fff76bfd  bl       #0x80007b0                  ; pb1_write
08000cda: 0a20      movs     r0, #0xa                    
08000cdc: fff79afd  bl       #0x8000814                  ; delay_ms
08000ce0: 0298      ldr      r0, [sp, #8]                
08000ce2: 00f06df8  bl       #0x8000dc0                  ; pa4_write
08000ce6: ffe7      b        #0x8000ce8                  
08000ce8: fff716ff  bl       #0x8000b18                  ; pa1_is_high
08000cec: 0028      cmp      r0, #0                      
08000cee: 01d1      bne      #0x8000cf4                  
08000cf0: ffe7      b        #0x8000cf2                  
08000cf2: f9e7      b        #0x8000ce8                  
08000cf4: 69e7      b        #0x8000bca                  ; -> STANDBY
08000cf6: 40e0      b        #0x8000d7a                  
08000cf8: 2348      ldr      r0, [pc, #0x8c]             ; =0x20000004 SRAM g_btn_last (.data, init 1)
08000cfa: 0068      ldr      r0, [r0]                    
08000cfc: 0028      cmp      r0, #0                      
08000cfe: 35d1      bne      #0x8000d6c                  
08000d00: ffe7      b        #0x8000d02                  
08000d02: 00f0edf9  bl       #0x80010e0                  ; get_tick_ms
08000d06: 0890      str      r0, [sp, #0x20]             
08000d08: 0898      ldr      r0, [sp, #0x20]             
08000d0a: 2149      ldr      r1, [pc, #0x84]             ; =0x2000000c SRAM g_press_tick (.bss)
08000d0c: 0968      ldr      r1, [r1]                    
08000d0e: 401a      subs     r0, r0, r1                  
08000d10: 2049      ldr      r1, [pc, #0x80]             ; =0x26e978d5 | (elapsed*inv(125)) ror 2 <= 0x0083126E  <=>  elapsed % 500 == 0
08000d12: 4143      muls     r1, r0, r1                  
08000d14: 0220      movs     r0, #2                      
08000d16: c141      rors     r1, r0                      
08000d18: 1f48      ldr      r0, [pc, #0x7c]             ; =0x0083126e
08000d1a: 8142      cmp      r1, r0                      
08000d1c: 0ed8      bhi      #0x8000d3c                  
08000d1e: ffe7      b        #0x8000d20                  
08000d20: 0a98      ldr      r0, [sp, #0x28]             
08000d22: 0899      ldr      r1, [sp, #0x20]             
08000d24: 8842      cmp      r0, r1                      
08000d26: 09d0      beq      #0x8000d3c                  
08000d28: ffe7      b        #0x8000d2a                  
08000d2a: 0898      ldr      r0, [sp, #0x20]             
08000d2c: 0a90      str      r0, [sp, #0x28]             
08000d2e: fff72dff  bl       #0x8000b8c                  ; pa2_toggle | toggle PA2, g_blink++
08000d32: 1648      ldr      r0, [pc, #0x58]             ; =0x20000010 SRAM g_blink_count (.bss)
08000d34: 0168      ldr      r1, [r0]                    
08000d36: 491c      adds     r1, r1, #1                  
08000d38: 0160      str      r1, [r0]                    
08000d3a: ffe7      b        #0x8000d3c                  
08000d3c: 1348      ldr      r0, [pc, #0x4c]             ; =0x20000010 SRAM g_blink_count (.bss)
08000d3e: 0068      ldr      r0, [r0]                    
08000d40: 0728      cmp      r0, #7                      ; held: g_blink>=7 -> power off
08000d42: 12d3      blo      #0x8000d6a                  
08000d44: ffe7      b        #0x8000d46                  
08000d46: 0020      movs     r0, #0                      
08000d48: 0190      str      r0, [sp, #4]                
08000d4a: fff731fd  bl       #0x80007b0                  ; pb1_write
08000d4e: 0a20      movs     r0, #0xa                    
08000d50: fff760fd  bl       #0x8000814                  ; delay_ms
08000d54: 0198      ldr      r0, [sp, #4]                
08000d56: 00f033f8  bl       #0x8000dc0                  ; pa4_write
08000d5a: ffe7      b        #0x8000d5c                  
08000d5c: fff7dcfe  bl       #0x8000b18                  ; pa1_is_high
08000d60: 0028      cmp      r0, #0                      
08000d62: 01d1      bne      #0x8000d68                  
08000d64: ffe7      b        #0x8000d66                  
08000d66: f9e7      b        #0x8000d5c                  
08000d68: 2fe7      b        #0x8000bca                  ; -> STANDBY
08000d6a: 05e0      b        #0x8000d78                  
08000d6c: 0748      ldr      r0, [pc, #0x1c]             ; =0x20000010 SRAM g_blink_count (.bss) | button idle: g_blink=0; PA2 high
08000d6e: 0021      movs     r1, #0                      
08000d70: 0160      str      r1, [r0]                    
08000d72: fff707ff  bl       #0x8000b84                  ; pa2_high
08000d76: ffe7      b        #0x8000d78                  
08000d78: ffe7      b        #0x8000d7a                  
08000d7a: ffe7      b        #0x8000d7c                  
08000d7c: 52e7      b        #0x8000c24                  
08000d7e: c046      .hword               ; nop (mov r8,r8) alignment padding
08000d80: .word 0x00000bb8            ; LITERAL (ref by 08000ba2)
08000d84: .word 0x20000014            ; LITERAL (ref by 08000bc2,08000c1c) SRAM g_mode (.bss, write-only)
08000d88: .word 0x20000004            ; LITERAL (ref by 08000bea,08000c16,08000c6e,08000c80,08000c8a,08000ca6,08000cb8,08000cc2,08000cf8) SRAM g_btn_last (.data, init 1)
08000d8c: .word 0x20000010            ; LITERAL (ref by 08000c9e,08000cc8,08000d32,08000d3c,08000d6c) SRAM g_blink_count (.bss)
08000d90: .word 0x2000000c            ; LITERAL (ref by 08000c96,08000d0a) SRAM g_press_tick (.bss)
08000d94: .word 0x26e978d5            ; LITERAL (ref by 08000d10)
08000d98: .word 0x0083126e            ; LITERAL (ref by 08000d18)
08000d9c: .word 0x00001770            ; LITERAL (ref by 08000c40)

; ---------------------------------------------------------------
; FUNCTION nvic_vector_table_set @ 0x08000da0   refs: bl@800020a
;   role: SCB_VTOR = base | (offset & 0x1FFFFF80)
; ---------------------------------------------------------------
08000da0: 82b0      sub      sp, #8                      
08000da2: 0190      str      r0, [sp, #4]                
08000da4: 0091      str      r1, [sp]                    
08000da6: 0198      ldr      r0, [sp, #4]                
08000da8: 0099      ldr      r1, [sp]                    
08000daa: 034a      ldr      r2, [pc, #0xc]              ; =0x1fffff80
08000dac: 1140      ands     r1, r2                      
08000dae: 0843      orrs     r0, r1                      
08000db0: 0249      ldr      r1, [pc, #8]                ; =0xe000ed08 SCB_VTOR
08000db2: 0860      str      r0, [r1]                    
08000db4: 02b0      add      sp, #8                      
08000db6: 7047      bx       lr                          
08000db8: .word 0x1fffff80            ; LITERAL (ref by 08000daa)
08000dbc: .word 0xe000ed08            ; LITERAL (ref by 08000db0) SCB_VTOR

; ---------------------------------------------------------------
; FUNCTION pa4_write @ 0x08000dc0   refs: bl@8000bfe, bl@8000c66, bl@8000ce2, bl@8000d56
;   role: arg!=0: GPIOA_BOP=1<<4 else GPIOA_BC=1<<4
; ---------------------------------------------------------------
08000dc0: 81b0      sub      sp, #4                      
08000dc2: 0146      mov      r1, r0                      
08000dc4: 6a46      mov      r2, sp                      
08000dc6: 1070      strb     r0, [r2]                    
08000dc8: 1078      ldrb     r0, [r2]                    
08000dca: 0028      cmp      r0, #0                      
08000dcc: 04d0      beq      #0x8000dd8                  
08000dce: ffe7      b        #0x8000dd0                  
08000dd0: 0548      ldr      r0, [pc, #0x14]             ; =0x48000018 GPIOA_BOP
08000dd2: 1021      movs     r1, #0x10                   
08000dd4: 0160      str      r1, [r0]                    
08000dd6: 03e0      b        #0x8000de0                  
08000dd8: 0248      ldr      r0, [pc, #8]                ; =0x48000028 GPIOA_BC
08000dda: 1021      movs     r1, #0x10                   
08000ddc: 0160      str      r1, [r0]                    
08000dde: ffe7      b        #0x8000de0                  
08000de0: 01b0      add      sp, #4                      
08000de2: 7047      bx       lr                          
08000de4: .word 0x48000028            ; LITERAL (ref by 08000b78,08000dd8) GPIOA_BC
08000de8: .word 0x48000018            ; LITERAL (ref by 08000af0,08000b6a,08000b84,08000dd0) GPIOA_BOP

; ---------------------------------------------------------------
; FUNCTION rcu_adc_clock_config @ 0x08000dec   refs: bl@800036c
;   role: switch(0..9) via PC-relative branch table @0x08000E20; called with 6 => ADCPSC=APB2/6, ADCSEL=1
; ---------------------------------------------------------------
08000dec: 10b5      push     {r4, lr}                    
08000dee: 82b0      sub      sp, #8                      
08000df0: 0146      mov      r1, r0                      
08000df2: 01aa      add      r2, sp, #4                  
08000df4: 1070      strb     r0, [r2]                    
08000df6: a848      ldr      r0, [pc, #0x2a0]            ; =0x40021004 RCU_CFG0
08000df8: 0368      ldr      r3, [r0]                    
08000dfa: 4cf20004  movw     r4, #0xc000                 
08000dfe: a343      bics     r3, r4                      
08000e00: 0360      str      r3, [r0]                    
08000e02: 5a48      ldr      r0, [pc, #0x168]            ; =0x40021030 RCU_CFG2
08000e04: 0368      ldr      r3, [r0]                    
08000e06: 5a4c      ldr      r4, [pc, #0x168]            ; =0x7ffefeff
08000e08: 2340      ands     r3, r4                      
08000e0a: 0360      str      r3, [r0]                    
08000e0c: 1078      ldrb     r0, [r2]                    
08000e0e: 0928      cmp      r0, #9                      
08000e10: 0090      str      r0, [sp]                    
08000e12: 00d9      bls      #0x8000e16                  
08000e14: a6e0      b        #0x8000f64                  
08000e16: 0098      ldr      r0, [sp]                    
08000e18: 8100      lsls     r1, r0, #2                  
08000e1a: 01a2      adr      r2, #4                      
08000e1c: 5118      adds     r1, r2, r1                  
08000e1e: 8f46      mov      pc, r1                      ; computed jump into branch table 0x08000E20..0x08000E47 (10 x b.w)
08000e20: 00f012b8  b.w      #0x8000e48                  
08000e24: 00f01cb8  b.w      #0x8000e60                  
08000e28: 00f026b8  b.w      #0x8000e78                  
08000e2c: 00f02eb8  b.w      #0x8000e8c                  
08000e30: 00f03bb8  b.w      #0x8000eaa                  
08000e34: 00f046b8  b.w      #0x8000ec4                  
08000e38: 00f056b8  b.w      #0x8000ee8                  
08000e3c: 00f061b8  b.w      #0x8000f02                  
08000e40: 00f071b8  b.w      #0x8000f26                  
08000e44: 00f07cb8  b.w      #0x8000f40                  
08000e48: 4848      ldr      r0, [pc, #0x120]            ; =0x40021030 RCU_CFG2
08000e4a: 0168      ldr      r1, [r0]                    
08000e4c: 0122      movs     r2, #1                      
08000e4e: 1204      lsls     r2, r2, #0x10               
08000e50: 9143      bics     r1, r2                      
08000e52: 0160      str      r1, [r0]                    
08000e54: 0168      ldr      r1, [r0]                    
08000e56: 40f20012  movw     r2, #0x100                  
08000e5a: 9143      bics     r1, r2                      
08000e5c: 0160      str      r1, [r0]                    
08000e5e: 82e0      b        #0x8000f66                  
08000e60: 4248      ldr      r0, [pc, #0x108]            ; =0x40021030 RCU_CFG2
08000e62: 0168      ldr      r1, [r0]                    
08000e64: 0122      movs     r2, #1                      
08000e66: 1204      lsls     r2, r2, #0x10               
08000e68: 1143      orrs     r1, r2                      
08000e6a: 0160      str      r1, [r0]                    
08000e6c: 0168      ldr      r1, [r0]                    
08000e6e: 40f20012  movw     r2, #0x100                  
08000e72: 9143      bics     r1, r2                      
08000e74: 0160      str      r1, [r0]                    
08000e76: 76e0      b        #0x8000f66                  
08000e78: 8748      ldr      r0, [pc, #0x21c]            ; =0x40021004 RCU_CFG0
08000e7a: 0168      ldr      r1, [r0]                    
08000e7c: 0160      str      r1, [r0]                    
08000e7e: 3b48      ldr      r0, [pc, #0xec]             ; =0x40021030 RCU_CFG2
08000e80: 0168      ldr      r1, [r0]                    
08000e82: 40f20012  movw     r2, #0x100                  
08000e86: 1143      orrs     r1, r2                      
08000e88: 0160      str      r1, [r0]                    
08000e8a: 6ce0      b        #0x8000f66                  
08000e8c: 8248      ldr      r0, [pc, #0x208]            ; =0x40021004 RCU_CFG0
08000e8e: 0168      ldr      r1, [r0]                    
08000e90: 0160      str      r1, [r0]                    
08000e92: 3648      ldr      r0, [pc, #0xd8]             ; =0x40021030 RCU_CFG2
08000e94: 0168      ldr      r1, [r0]                    
08000e96: 0122      movs     r2, #1                      
08000e98: d207      lsls     r2, r2, #0x1f               
08000e9a: 1143      orrs     r1, r2                      
08000e9c: 0160      str      r1, [r0]                    
08000e9e: 0168      ldr      r1, [r0]                    
08000ea0: 40f20012  movw     r2, #0x100                  
08000ea4: 1143      orrs     r1, r2                      
08000ea6: 0160      str      r1, [r0]                    
08000ea8: 5de0      b        #0x8000f66                  
08000eaa: 7b48      ldr      r0, [pc, #0x1ec]            ; =0x40021004 RCU_CFG0
08000eac: 0168      ldr      r1, [r0]                    
08000eae: 44f20002  movw     r2, #0x4000                 
08000eb2: 1143      orrs     r1, r2                      
08000eb4: 0160      str      r1, [r0]                    
08000eb6: 2d48      ldr      r0, [pc, #0xb4]             ; =0x40021030 RCU_CFG2
08000eb8: 0168      ldr      r1, [r0]                    
08000eba: 40f20012  movw     r2, #0x100                  
08000ebe: 1143      orrs     r1, r2                      
08000ec0: 0160      str      r1, [r0]                    
08000ec2: 50e0      b        #0x8000f66                  
08000ec4: 7448      ldr      r0, [pc, #0x1d0]            ; =0x40021004 RCU_CFG0
08000ec6: 0168      ldr      r1, [r0]                    
08000ec8: 44f20002  movw     r2, #0x4000                 
08000ecc: 1143      orrs     r1, r2                      
08000ece: 0160      str      r1, [r0]                    
08000ed0: 2648      ldr      r0, [pc, #0x98]             ; =0x40021030 RCU_CFG2
08000ed2: 0168      ldr      r1, [r0]                    
08000ed4: 0122      movs     r2, #1                      
08000ed6: d207      lsls     r2, r2, #0x1f               
08000ed8: 1143      orrs     r1, r2                      
08000eda: 0160      str      r1, [r0]                    
08000edc: 0168      ldr      r1, [r0]                    
08000ede: 40f20012  movw     r2, #0x100                  
08000ee2: 1143      orrs     r1, r2                      
08000ee4: 0160      str      r1, [r0]                    
08000ee6: 3ee0      b        #0x8000f66                  
08000ee8: 6b48      ldr      r0, [pc, #0x1ac]            ; =0x40021004 RCU_CFG0
08000eea: 0168      ldr      r1, [r0]                    
08000eec: 48f20002  movw     r2, #0x8000                 
08000ef0: 1143      orrs     r1, r2                      
08000ef2: 0160      str      r1, [r0]                    
08000ef4: 1d48      ldr      r0, [pc, #0x74]             ; =0x40021030 RCU_CFG2
08000ef6: 0168      ldr      r1, [r0]                    
08000ef8: 40f20012  movw     r2, #0x100                  
08000efc: 1143      orrs     r1, r2                      
08000efe: 0160      str      r1, [r0]                    
08000f00: 31e0      b        #0x8000f66                  
08000f02: 6548      ldr      r0, [pc, #0x194]            ; =0x40021004 RCU_CFG0
08000f04: 0168      ldr      r1, [r0]                    
08000f06: 48f20002  movw     r2, #0x8000                 
08000f0a: 1143      orrs     r1, r2                      
08000f0c: 0160      str      r1, [r0]                    
08000f0e: 1748      ldr      r0, [pc, #0x5c]             ; =0x40021030 RCU_CFG2
08000f10: 0168      ldr      r1, [r0]                    
08000f12: 0122      movs     r2, #1                      
08000f14: d207      lsls     r2, r2, #0x1f               
08000f16: 1143      orrs     r1, r2                      
08000f18: 0160      str      r1, [r0]                    
08000f1a: 0168      ldr      r1, [r0]                    
08000f1c: 40f20012  movw     r2, #0x100                  
08000f20: 1143      orrs     r1, r2                      
08000f22: 0160      str      r1, [r0]                    
08000f24: 1fe0      b        #0x8000f66                  
08000f26: 5c48      ldr      r0, [pc, #0x170]            ; =0x40021004 RCU_CFG0
08000f28: 0168      ldr      r1, [r0]                    
08000f2a: 4cf20002  movw     r2, #0xc000                 
08000f2e: 1143      orrs     r1, r2                      
08000f30: 0160      str      r1, [r0]                    
08000f32: 0e48      ldr      r0, [pc, #0x38]             ; =0x40021030 RCU_CFG2
08000f34: 0168      ldr      r1, [r0]                    
08000f36: 40f20012  movw     r2, #0x100                  
08000f3a: 1143      orrs     r1, r2                      
08000f3c: 0160      str      r1, [r0]                    
08000f3e: 12e0      b        #0x8000f66                  
08000f40: 5548      ldr      r0, [pc, #0x154]            ; =0x40021004 RCU_CFG0
08000f42: 0168      ldr      r1, [r0]                    
08000f44: 4cf20002  movw     r2, #0xc000                 
08000f48: 1143      orrs     r1, r2                      
08000f4a: 0160      str      r1, [r0]                    
08000f4c: 0748      ldr      r0, [pc, #0x1c]             ; =0x40021030 RCU_CFG2
08000f4e: 0168      ldr      r1, [r0]                    
08000f50: 0122      movs     r2, #1                      
08000f52: d207      lsls     r2, r2, #0x1f               
08000f54: 1143      orrs     r1, r2                      
08000f56: 0160      str      r1, [r0]                    
08000f58: 0168      ldr      r1, [r0]                    
08000f5a: 40f20012  movw     r2, #0x100                  
08000f5e: 1143      orrs     r1, r2                      
08000f60: 0160      str      r1, [r0]                    
08000f62: 00e0      b        #0x8000f66                  
08000f64: ffe7      b        #0x8000f66                  
08000f66: 02b0      add      sp, #8                      
08000f68: 10bd      pop      {r4, pc}                    
08000f6a: c046      .hword               ; nop (mov r8,r8) alignment padding
08000f6c: .word 0x40021030            ; LITERAL (ref by 08000e02,08000e48,08000e60,08000e7e,08000e92,08000eb6,08000ed0,08000ef4,08000f0e,08000f32,08000f4c) RCU_CFG2
08000f70: .word 0x7ffefeff            ; LITERAL (ref by 08000e06)

; ---------------------------------------------------------------
; FUNCTION rcu_periph_clock_enable @ 0x08000f74   refs: bl@8000366, bl@800090a, bl@8000910, bl@8000afc, bl@8000b04, bl@8000b46
;   role: REG32(RCU + (p>>6)) |= 1<<(p&0x1F)
; ---------------------------------------------------------------
08000f74: 10b5      push     {r4, lr}                    
08000f76: 81b0      sub      sp, #4                      
08000f78: 0146      mov      r1, r0                      
08000f7a: 6a46      mov      r2, sp                      
08000f7c: 1080      strh     r0, [r2]                    
08000f7e: 1088      ldrh     r0, [r2]                    
08000f80: 1f22      movs     r2, #0x1f                   
08000f82: 0346      mov      r3, r0                      
08000f84: 1340      ands     r3, r2                      
08000f86: 0122      movs     r2, #1                      
08000f88: 9a40      lsls     r2, r3                      
08000f8a: 8009      lsrs     r0, r0, #6                  
08000f8c: 404b      ldr      r3, [pc, #0x100]            ; =0x40021000 RCU_CTL0
08000f8e: c458      ldr      r4, [r0, r3]                
08000f90: 1443      orrs     r4, r2                      
08000f92: c450      str      r4, [r0, r3]                
08000f94: 01b0      add      sp, #4                      
08000f96: 10bd      pop      {r4, pc}                    

; ---------------------------------------------------------------
; FUNCTION pa6_is_high @ 0x08000f98   refs: bl@8000c36
;   role: return PA6 level
; ---------------------------------------------------------------
08000f98: 80b5      push     {r7, lr}                    
08000f9a: 82b0      sub      sp, #8                      
08000f9c: 0920      movs     r0, #9                      
08000f9e: c006      lsls     r0, r0, #0x1b               
08000fa0: 4021      movs     r1, #0x40                   
08000fa2: fff701fd  bl       #0x80009a8                  ; gpio_input_bit_get
08000fa6: 0128      cmp      r0, #1                      
08000fa8: 04d1      bne      #0x8000fb4                  
08000faa: ffe7      b        #0x8000fac                  
08000fac: 01a8      add      r0, sp, #4                  
08000fae: 0121      movs     r1, #1                      
08000fb0: 0170      strb     r1, [r0]                    
08000fb2: 03e0      b        #0x8000fbc                  
08000fb4: 01a8      add      r0, sp, #4                  
08000fb6: 0021      movs     r1, #0                      
08000fb8: 0170      strb     r1, [r0]                    
08000fba: ffe7      b        #0x8000fbc                  
08000fbc: 01a8      add      r0, sp, #4                  
08000fbe: 0078      ldrb     r0, [r0]                    
08000fc0: 02b0      add      sp, #8                      
08000fc2: 80bd      pop      {r7, pc}                    

; ---------------------------------------------------------------
; FUNCTION system_clock_72m_irc8m @ 0x08000fc4   refs: bl@80010a6
;   role: IRC8M on (timeout 0x500, hang if fail), FMC_WS=2WS, PLL=IRC8M/2 x18=72MHz, SCS=PLL, wait SCSS
; ---------------------------------------------------------------
08000fc4: 83b0      sub      sp, #0xc                    
08000fc6: 0020      movs     r0, #0                      
08000fc8: 0290      str      r0, [sp, #8]                
08000fca: 0190      str      r0, [sp, #4]                
08000fcc: 3048      ldr      r0, [pc, #0xc0]             ; =0x40021000 RCU_CTL0
08000fce: 0168      ldr      r1, [r0]                    
08000fd0: 0122      movs     r2, #1                      
08000fd2: 1143      orrs     r1, r2                      
08000fd4: 0160      str      r1, [r0]                    
08000fd6: ffe7      b        #0x8000fd8                  
08000fd8: 0298      ldr      r0, [sp, #8]                
08000fda: 401c      adds     r0, r0, #1                  
08000fdc: 0290      str      r0, [sp, #8]                
08000fde: 2c48      ldr      r0, [pc, #0xb0]             ; =0x40021000 RCU_CTL0
08000fe0: 0068      ldr      r0, [r0]                    
08000fe2: 0221      movs     r1, #2                      ; poll IRC8MSTB, timeout 0x500
08000fe4: 0840      ands     r0, r1                      
08000fe6: 0190      str      r0, [sp, #4]                
08000fe8: ffe7      b        #0x8000fea                  
08000fea: 0198      ldr      r0, [sp, #4]                
08000fec: 0021      movs     r1, #0                      
08000fee: 0028      cmp      r0, #0                      
08000ff0: 0091      str      r1, [sp]                    
08000ff2: 08d1      bne      #0x8001006                  
08000ff4: ffe7      b        #0x8000ff6                  
08000ff6: 0298      ldr      r0, [sp, #8]                
08000ff8: 40f20051  movw     r1, #0x500                  
08000ffc: 401a      subs     r0, r0, r1                  
08000ffe: 411e      subs     r1, r0, #1                  
08001000: 8841      sbcs     r0, r1                      
08001002: 0090      str      r0, [sp]                    
08001004: ffe7      b        #0x8001006                  
08001006: 0098      ldr      r0, [sp]                    
08001008: c007      lsls     r0, r0, #0x1f               
0800100a: 0028      cmp      r0, #0                      
0800100c: e4d1      bne      #0x8000fd8                  
0800100e: ffe7      b        #0x8001010                  
08001010: 1f48      ldr      r0, [pc, #0x7c]             ; =0x40021000 RCU_CTL0
08001012: 0068      ldr      r0, [r0]                    
08001014: 8007      lsls     r0, r0, #0x1e               
08001016: 0028      cmp      r0, #0                      
08001018: 02d4      bmi      #0x8001020                  
0800101a: ffe7      b        #0x800101c                  
0800101c: ffe7      b        #0x800101e                  
0800101e: fee7      b        #0x800101e                  ; hang if IRC8M not stable
08001020: 1c48      ldr      r0, [pc, #0x70]             ; =0x40022000 FMC_WS
08001022: 0168      ldr      r1, [r0]                    
08001024: 0222      movs     r2, #2                      ; FMC_WS.WSCNT=2
08001026: 1143      orrs     r1, r2                      
08001028: 0522      movs     r2, #5                      
0800102a: 9143      bics     r1, r2                      
0800102c: 0160      str      r1, [r0]                    
0800102e: 1a48      ldr      r0, [pc, #0x68]             ; =0x40021004 RCU_CFG0
08001030: 0168      ldr      r1, [r0]                    
08001032: 0160      str      r1, [r0]                    
08001034: 0168      ldr      r1, [r0]                    
08001036: 0160      str      r1, [r0]                    
08001038: 0168      ldr      r1, [r0]                    
0800103a: 0160      str      r1, [r0]                    
0800103c: 0168      ldr      r1, [r0]                    
0800103e: 174a      ldr      r2, [pc, #0x5c]             ; =0xf7c2ffff | clear PLLSEL/PLLMF/PLLMF4/PLLDV fields
08001040: 1140      ands     r1, r2                      
08001042: 0160      str      r1, [r0]                    
08001044: 0168      ldr      r1, [r0]                    
08001046: 164a      ldr      r2, [pc, #0x58]             ; =0x08040000 | PLLMF=0b10001 (x18), PLLSEL=0 (IRC8M/2)
08001048: 1143      orrs     r1, r2                      
0800104a: 0160      str      r1, [r0]                    
0800104c: 1048      ldr      r0, [pc, #0x40]             ; =0x40021000 RCU_CTL0
0800104e: 0168      ldr      r1, [r0]                    
08001050: 0122      movs     r2, #1                      
08001052: 1206      lsls     r2, r2, #0x18               ; PLLEN
08001054: 1143      orrs     r1, r2                      
08001056: 0160      str      r1, [r0]                    
08001058: ffe7      b        #0x800105a                  
0800105a: 0d48      ldr      r0, [pc, #0x34]             ; =0x40021000 RCU_CTL0
0800105c: 0068      ldr      r0, [r0]                    
0800105e: 8001      lsls     r0, r0, #6                  ; wait PLLSTB
08001060: 0028      cmp      r0, #0                      
08001062: 01d4      bmi      #0x8001068                  
08001064: ffe7      b        #0x8001066                  
08001066: f8e7      b        #0x800105a                  
08001068: 0b48      ldr      r0, [pc, #0x2c]             ; =0x40021004 RCU_CFG0
0800106a: 0168      ldr      r1, [r0]                    
0800106c: 0322      movs     r2, #3                      
0800106e: 9143      bics     r1, r2                      
08001070: 0160      str      r1, [r0]                    
08001072: 0168      ldr      r1, [r0]                    
08001074: 0222      movs     r2, #2                      ; SCS=PLL
08001076: 1143      orrs     r1, r2                      
08001078: 0160      str      r1, [r0]                    
0800107a: ffe7      b        #0x800107c                  
0800107c: 0648      ldr      r0, [pc, #0x18]             ; =0x40021004 RCU_CFG0
0800107e: 0068      ldr      r0, [r0]                    
08001080: 0007      lsls     r0, r0, #0x1c               ; wait SCSS=PLL
08001082: 0028      cmp      r0, #0                      
08001084: 01d4      bmi      #0x800108a                  
08001086: ffe7      b        #0x8001088                  
08001088: f8e7      b        #0x800107c                  
0800108a: 03b0      add      sp, #0xc                    
0800108c: 7047      bx       lr                          
0800108e: c046      .hword               ; nop (mov r8,r8) alignment padding
08001090: .word 0x40021000            ; LITERAL (ref by 08000f8c,08000fcc,08000fde,08001010,0800104c,0800105a) RCU_CTL0
08001094: .word 0x40022000            ; LITERAL (ref by 08001020) FMC_WS
08001098: .word 0x40021004            ; LITERAL (ref by 08000df6,08000e78,08000e8c,08000eaa,08000ec4,08000ee8,08000f02,08000f26,08000f40,0800102e,08001068,0800107c) RCU_CFG0
0800109c: .word 0xf7c2ffff            ; LITERAL (ref by 0800103e)
080010a0: .word 0x08040000            ; LITERAL (ref by 08001046)

; ---------------------------------------------------------------
; FUNCTION system_clock_config @ 0x080010a4   refs: bl@8000200
;   role: wrapper -> system_clock_72m_irc8m
; ---------------------------------------------------------------
080010a4: 80b5      push     {r7, lr}                    
080010a6: fff78dff  bl       #0x8000fc4                  ; system_clock_72m_irc8m
080010aa: 80bd      pop      {r7, pc}                    

; ---------------------------------------------------------------
; FUNCTION systick_config_1ms @ 0x080010ac   refs: bl@8000baa
;   role: SysTick_Config(SystemCoreClock/1000) (hang on failure); NVIC_SetPriority(SysTick,0)
; ---------------------------------------------------------------
080010ac: 80b5      push     {r7, lr}                    
080010ae: 82b0      sub      sp, #8                      
080010b0: 0a48      ldr      r0, [pc, #0x28]             ; =0x20000000 SRAM g_SystemCoreClock (.data, init 72000000)
080010b2: 0068      ldr      r0, [r0]                    
080010b4: 40f2e831  movw     r1, #0x3e8                  ; SystemCoreClock/1000 -> 1 ms SysTick
080010b8: b0fbf1f0  udiv     r0, r0, r1                  
080010bc: fff736f8  bl       #0x800012c                  ; SysTick_Config
080010c0: 0028      cmp      r0, #0                      
080010c2: 02d0      beq      #0x80010ca                  
080010c4: ffe7      b        #0x80010c6                  
080010c6: ffe7      b        #0x80010c8                  
080010c8: fee7      b        #0x80010c8                  ; hang if SysTick_Config failed
080010ca: 0020      movs     r0, #0                      
080010cc: c143      mvns     r1, r0                      
080010ce: 0190      str      r0, [sp, #4]                
080010d0: 0846      mov      r0, r1                      
080010d2: 0199      ldr      r1, [sp, #4]                
080010d4: fff7b0f8  bl       #0x8000238                  ; NVIC_SetPriority
080010d8: 02b0      add      sp, #8                      
080010da: 80bd      pop      {r7, pc}                    
080010dc: .word 0x20000000            ; LITERAL (ref by 080010b0) SRAM g_SystemCoreClock (.data, init 72000000)

; ---------------------------------------------------------------
; FUNCTION get_tick_ms @ 0x080010e0   refs: bl@8000c2e, bl@8000c46, bl@8000c92, bl@8000d02
;   role: return g_tick (0x20000018)
; ---------------------------------------------------------------
080010e0: 0448      ldr      r0, [pc, #0x10]             ; =0x20000018 SRAM g_tick_ms (.bss)
080010e2: 0068      ldr      r0, [r0]                    
080010e4: 7047      bx       lr                          
080010e6: c046      .hword               ; nop (mov r8,r8) alignment padding

; ---------------------------------------------------------------
; FUNCTION tick_increment @ 0x080010e8   refs: bl@8000186
;   role: g_tick++ (from SysTick ISR)
; ---------------------------------------------------------------
080010e8: 0248      ldr      r0, [pc, #8]                ; =0x20000018 SRAM g_tick_ms (.bss)
080010ea: 0168      ldr      r1, [r0]                    
080010ec: 491c      adds     r1, r1, #1                  
080010ee: 0160      str      r1, [r0]                    
080010f0: 7047      bx       lr                          
080010f2: c046      .hword               ; nop (mov r8,r8) alignment padding
080010f4: .word 0x20000018            ; LITERAL (ref by 080010e0,080010e8) SRAM g_tick_ms (.bss)

; ---------------------------------------------------------------
; FUNCTION __scatterload_copy @ 0x080010f8   refs: scatter-load region table @0x08001118/0x08001128
;   role: word copy src->dst (len bytes)
; ---------------------------------------------------------------
080010f8: 02e0      b        #0x8001100                  
080010fa: 08c8      ldm      r0!, {r3}                   
080010fc: 121f      subs     r2, r2, #4                  
080010fe: 08c1      stm      r1!, {r3}                   
08001100: 002a      cmp      r2, #0                      
08001102: fad1      bne      #0x80010fa                  
08001104: 7047      bx       lr                          
08001106: 7047      .hword               ; bx lr (unreferenced)

; ---------------------------------------------------------------
; FUNCTION __scatterload_zeroinit @ 0x08001108   refs: scatter-load region table @0x08001118/0x08001128
;   role: word zero-fill dst (len bytes)
; ---------------------------------------------------------------
08001108: 0020      movs     r0, #0                      
0800110a: 01e0      b        #0x8001110                  
0800110c: 01c1      stm      r1!, {r0}                   
0800110e: 121f      subs     r2, r2, #4                  
08001110: 002a      cmp      r2, #0                      
08001112: fbd1      bne      #0x800110c                  
08001114: 7047      bx       lr                          
08001116: 0000      .hword               ; zero padding

; ===== SECTION: ARM scatter-load region table 0x08001118-0x08001137 =====
08001118: .word 0x08001138,0x20000000,0x00000008,0x080010f8 ; src=08001138 dst=20000000 len=0x8 handler=__scatterload_copy
08001128: .word 0x08001140,0x20000008,0x00000418,0x08001108 ; src=08001140 dst=20000008 len=0x418 handler=__scatterload_zeroinit

; ===== SECTION: .data initial values 0x08001138-0x0800113F (copied to 0x20000000) =====
08001138: .word 0x044aa200   ; -> 0x20000000 = 72000000 (72 MHz; matches GD32 SystemCoreClock)
0800113c: .word 0x00000001   ; -> 0x20000004

; ===== 0x08001140-0x08003FFF: all 0xFF (erased), 11968 bytes =====
