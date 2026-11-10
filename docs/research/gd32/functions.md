# GD32E230F4 firmware – function list

Names are inferred (no symbols in the image). Most low-level routines match GigaDevice GD32E23x Standard Peripheral Library / CMSIS code compiled at -O0 (Arm Compiler/Keil style: `__main`, `__scatterload`). Size = bytes up to next function (includes literal pool/padding).

| Address | Name (inferred) | Size | Called/referenced from | Inferred role |
|---|---|---|---|---|
| 0x080000CC | `__main` | 8 | literal@80000f8 | ARM C library entry: SP=0x20000420, then __scatterload (Keil/armcc-style startup) |
| 0x080000D4 | `__rt_entry_jump_main` | 12 | 0x08000114 | loads &main (0x08000B99) and bx; never returns |
| 0x080000E0 | `Reset_Handler` | 18 | vector:Reset | calls SystemInit (0x0800018C) then __main |
| 0x080000F2 | `Default_Handler` | 10 | vector:ADC_CMP_IRQ, vector:DMA_CH0_IRQ, vector:DMA_CH1_2_IRQ, vector:DMA_CH3_4_IRQ, vector:EXTI0_1_IRQ … | b . infinite loop; used by ALL 32 peripheral IRQ vectors (no peripheral interrupts used) |
| 0x080000FC | `__scatterload` | 36 | 0x080000d0 | walks region table 0x08001118..0x08001137 and calls copy/zero handlers, then main |
| 0x08000120 | `HardFault_Handler` | 4 | vector:HardFault | infinite loop |
| 0x08000124 | `NMI_Handler` | 2 | vector:NMI | empty (bx lr) |
| 0x08000126 | `PendSV_Handler` | 2 | vector:PendSV | empty (bx lr) |
| 0x08000128 | `SVC_Handler` | 4 | vector:SVCall | empty (bx lr) |
| 0x0800012C | `SysTick_Config` | 84 | 0x080010bc | CMSIS: LOAD=ticks-1, prio(SysTick)=3, VAL=0, CTRL=7; returns 1 if ticks>0x1000000 |
| 0x08000180 | `SysTick_Handler` | 12 | vector:SysTick | delay_decrement(); tick_increment() |
| 0x0800018C | `SystemInit` | 172 | literal@80000f4 | GD32 SystemInit: IRC8M on, reset RCU cfg, system_clock_config(), VTOR=0x08000000 |
| 0x08000238 | `NVIC_SetPriority` | 136 | 0x08000158, 0x080010d4 | CMSIS ARMv8-M baseline (2 prio bits, <<6); IPR for IRQn>=0, SHPR for system exceptions |
| 0x080002C0 | `adc_calibration_enable` | 56 | 0x080003ca | ADC_CTL1 RSTCLB(bit3) then CLB(bit2), busy-wait each |
| 0x080002F8 | `adc_channel_length_config` | 104 | 0x080003a4 | group 1 (routine): ADC_RSQ0[23:20]=len-1; group 2 branch writes ADC+0x38 (SPL inserted-group code, dead here) |
| 0x08000360 | `adc_init_PA3` | 120 | 0x08000bb6 | ADC clock (APB2EN.ADCEN), ADC clk=APB2/6, PA3 analog, continuous, SW trigger, right-align, 1 ch, CH3 rank0 239.5cyc, 12-bit, ADC on, 1 ms, calibrate |
| 0x080003D8 | `adc_data_alignment_config` | 44 | 0x0800039c | ADC_CTL1.DAL (bit11): 0=right |
| 0x08000404 | `adc_enable` | 28 | 0x080003c0 | set ADC_CTL1.ADCON if clear |
| 0x08000420 | `adc_external_trigger_config` | 136 | 0x080003b6 | ADC_CTL1.ETERC (bit20) for group bit0; bit15 for group bit1 (dead branch) |
| 0x080004A8 | `adc_external_trigger_source_config` | 84 | 0x08000396 | ADC_CTL1.ETSRC[19:17]=source (called with 7<<17 = SWRCST) |
| 0x080004FC | `adc_flag_clear` | 20 | 0x08000868 | ADC_STAT &= ~flag |
| 0x08000510 | `adc_flag_get` | 44 | 0x08000870 | return (ADC_STAT & flag)!=0 |
| 0x0800053C | `adc_regular_channel_config` | 348 | 0x080003ae, 0x0800085c | RSQ0/1/2 rank slot = channel; SAMPT0/1 sample time |
| 0x08000698 | `adc_resolution_config` | 28 | 0x080003bc | ADC_CTL0.DRES[25:24] (0 = 12-bit) |
| 0x080006B4 | `adc_software_trigger_enable` | 64 | 0x08000862 | ADC_CTL1.SWRCST (bit22) for group bit0 |
| 0x080006F4 | `adc_special_function_config` | 188 | 0x08000388 | SM (CTL0 bit8) / bit10 / CTN (CTL1 bit1); called with 2 => continuous mode ON |
| 0x080007B0 | `pb1_write` | 40 | 0x080007f4, 0x08000c04, 0x08000c5a, 0x08000cd6, 0x08000d4a | arg!=0: GPIOB_BOP=1<<1 (PB1 high) else GPIOB_BC=1<<1 (PB1 low) |
| 0x080007D8 | `pa3_low_voltage_check` | 60 | 0x08000c24 | avg10(ADC CH3) <= 1985 (0x7C1) ? {PB1 high; PA7 high; return 1} : return 0 |
| 0x08000814 | `delay_ms` | 28 | 0x080003c6, 0x08000bbe, 0x08000bdc, 0x08000c60, 0x08000cdc … | g_delay=ms; spin until SysTick ISR decrements to 0 |
| 0x08000830 | `delay_decrement` | 28 | 0x08000182 | if (g_delay) g_delay-- (called from SysTick ISR) |
| 0x0800084C | `adc_read_ch3` | 132 | 0x080008e4 | rank0=CH3 @7.5cyc, SW trigger, clear EOC, poll EOC (timeout 1,000,000), return ADC_RDATA or -1 |
| 0x080008D0 | `adc_read_ch3_avg10` | 52 | 0x080007e0 | sum 10 reads / 10 (udiv) |
| 0x08000904 | `gpio_outputs_init` | 164 | 0x08000bae | clk GPIOA+GPIOB; PA4 out pd, PB1 out pd, PA7 out, PA6 in floating; PA4/PB1/PA7 push-pull 50MHz; drive PA4, PB1, PA7 low |
| 0x080009A8 | `gpio_input_bit_get` | 42 | 0x08000b22, 0x08000fa2 | (GPIOx_ISTAT & pin)!=0 |
| 0x080009D2 | `gpio_mode_set` | 144 | 0x0800037e, 0x08000926, 0x08000934, 0x0800094c, 0x08000958 … | GPIOx_CTL 2-bit mode + GPIOx_PUD 2-bit pull per selected pin |
| 0x08000A62 | `gpio_output_options_set` | 142 | 0x0800096a, 0x08000976, 0x08000982, 0x08000b66 | GPIOx_OMODE (PP/OD) + GPIOx_OSPD per pin |
| 0x08000AF0 | `pa7_set_high` | 8 | 0x080007f8 | GPIOA_BOP = 1<<7 |
| 0x08000AF8 | `button_pa1_init` | 32 | 0x08000ba6 | clk GPIOA + SYSCFG(CFGCMP); PA1 input with pull-up |
| 0x08000B18 | `pa1_is_high` | 40 | 0x08000bd0, 0x08000be0, 0x08000c0a, 0x08000c74, 0x08000cac … | return PA1 level (1 = released / pulled up) |
| 0x08000B40 | `led_pa2_init` | 56 | 0x08000bb2 | clk GPIOA; PA2 output push-pull 50MHz; PA2 high |
| 0x08000B78 | `pa2_low` | 12 | 0x08000bca | GPIOA_BC = 1<<2 |
| 0x08000B84 | `pa2_high` | 8 | 0x08000bf6, 0x08000d72 | GPIOA_BOP = 1<<2 |
| 0x08000B8C | `pa2_toggle` | 12 | 0x08000c9a, 0x08000d2e | GPIOA_TG = 1<<2 |
| 0x08000B98 | `main` | 520 | literal@80000d8 | soft-power state machine: standby/wait button -> power on -> monitor button + PA3 voltage |
| 0x08000DA0 | `nvic_vector_table_set` | 32 | 0x0800020a | SCB_VTOR = base | (offset & 0x1FFFFF80) |
| 0x08000DC0 | `pa4_write` | 44 | 0x08000bfe, 0x08000c66, 0x08000ce2, 0x08000d56 | arg!=0: GPIOA_BOP=1<<4 else GPIOA_BC=1<<4 |
| 0x08000DEC | `rcu_adc_clock_config` | 392 | 0x0800036c | switch(0..9) via PC-relative branch table @0x08000E20; called with 6 => ADCPSC=APB2/6, ADCSEL=1 |
| 0x08000F74 | `rcu_periph_clock_enable` | 36 | 0x08000366, 0x0800090a, 0x08000910, 0x08000afc, 0x08000b04 … | REG32(RCU + (p>>6)) |= 1<<(p&0x1F) |
| 0x08000F98 | `pa6_is_high` | 44 | 0x08000c36 | return PA6 level |
| 0x08000FC4 | `system_clock_72m_irc8m` | 224 | 0x080010a6 | IRC8M on (timeout 0x500, hang if fail), FMC_WS=2WS, PLL=IRC8M/2 x18=72MHz, SCS=PLL, wait SCSS |
| 0x080010A4 | `system_clock_config` | 8 | 0x08000200 | wrapper -> system_clock_72m_irc8m |
| 0x080010AC | `systick_config_1ms` | 52 | 0x08000baa | SysTick_Config(SystemCoreClock/1000) (hang on failure); NVIC_SetPriority(SysTick,0) |
| 0x080010E0 | `get_tick_ms` | 8 | 0x08000c2e, 0x08000c46, 0x08000c92, 0x08000d02 | return g_tick (0x20000018) |
| 0x080010E8 | `tick_increment` | 16 | 0x08000186 | g_tick++ (from SysTick ISR) |
| 0x080010F8 | `__scatterload_copy` | 16 | scatter-load region table @0x08001118/0x08001128 | word copy src->dst (len bytes) |
| 0x08001108 | `__scatterload_zeroinit` | 16 | scatter-load region table @0x08001118/0x08001128 | word zero-fill dst (len bytes) |
