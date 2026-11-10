# Peripheral usage map (GD32E230F4 image, evidence = instruction addresses)

Register names/bit meanings: GD32E23x User Manual (`/workspace/gd32-manual.txt`). Pin numbers: GD32E230xx datasheet tables 2-8 (TSSOP20) / 2-9 (LGA20) (from the LCSC-hosted copy; same pin table also appears in GigaDevice's Rev 3.x).

## Exhaustive peripheral list
The 64 literal pool words are the only peripheral addresses loaded from flash; GPIOA's base is also made arithmetically (`movs r0,#9; lsls r0,#27` = 0x48000000). Peripherals touched: **RCU, FMC (wait states only), GPIOA, GPIOB, ADC, SysTick, NVIC/SCB (priority, VTOR)**. That's all of them.

**Not used:** USART0/1, I2C0/1, SPI0/1, all TIMERs, DMA, EXTI, RTC, FWDGT/WWDGT, CMP, CRC, PMU. No literal points into any of these, and none of their clock-enable bits is set. No peripheral IRQ is enabled, and all 32 IRQ vectors go to `b .` (0x080000F2).

## RCU (clocks)
| Evidence | Action |
|---|---|
| 0x08000190–0x080001FA (SystemInit) | IRC8MEN=1 and wait for IRC8MSTB. Reset CFG0/CFG1/CFG2/CTL1 to defaults, disable HXTAL/CKM/PLL/IRC28M, RCU_INT=0 |
| 0x08000FC4–0x0800108C | IRC8M → PLL source IRC8M/2 (PLLSEL=0), PLLMF=0b10001 (×18) → **72 MHz** SYSCLK, SCS=PLL. AHB/APB1/APB2 prescalers ÷1 (fields written unchanged). **No external crystal is used** (HXTAL is never enabled) |
| 0x08001020 | FMC_WS.WSCNT = 2 wait states |
| 0x08000F74 `rcu_periph_clock_enable` args | 0x511 = AHBEN.PAEN (GPIOA); 0x512 = AHBEN.PBEN (GPIOB); 0x600 = APB2EN.CFGCMPEN (SYSCFG/CMP clock only; SYSCFG/CMP registers are never written); 0x609 = APB2EN.ADCEN |
| 0x08000DEC (arg 6) | ADC clock: RCU_CFG0.ADCPSC=10b, CFG2.ADCSEL=1, CFG2.ADCPSC[2]=0 → CK_ADC = APB2/6 = **12 MHz** |
| .data 0x20000000 | SystemCoreClock = 72,000,000 (initial value at 0x08001138) |

## GPIO (everything that is configured)
| Pin | TSSOP20 pin | LGA20 pin | Configuration (evidence) | Runtime use | Likely board meaning (hypothesis) |
|---|---|---|---|---|---|
| **PA1** | 7 | 4 | Input with **pull-up** (0x08000B12) | Read through `pa1_is_high` 0x08000B18. Low = pressed (50 ms debounce at 0x08000BDA) | **Power/user button**, active-low |
| **PA2** | 8 | 5 | Output push-pull 50 MHz, set high at init (0x08000B5A–0x08000B6E) | Low in standby (0x08000BCA), high when on (0x08000BF6/0x08000D72), toggled while the button is held (0x08000B8C) | **Status/power LED** (LED_CTL?) |
| **PA3** | 9 | 6 | **Analog**, ADC_IN3 (0x08000378) | Average of 10 samples; ≤1985 counts triggers the shutdown path (0x080007D8) | Voltage sense (supply/brown-out sense or a host "power-down" level) |
| **PA4** | 10 | 7 | Output PP 50 MHz (pull-down bit also set), driven low at init (0x08000926, 0x0800096A, 0x0800098A) | High at power-on (0x08000BFE). Low 10 ms after PB1 at power-off | Power-rail enable #1 (switched off last) |
| **PB1** | 14 | 11 | Output PP 50 MHz (pull-down bit set), low at init (0x08000934, 0x08000976, 0x08000990) | High at power-on (0x08000C04). Low first at power-off (0x08000C5A/0x08000CD6/0x08000D4A) | Power-rail enable #2 (switched off first) |
| **PA6** | 12 | 9 | Input floating (0x08000958) | Read only in the low-voltage path. High extends the hold time from 3000 to 6000 ms (0x08000C36–0x08000C42) | Input from another CPU/board ("need more time"?) |
| **PA7** | 13 | 10 | Output PP 50 MHz, low at init (0x0800094C, 0x08000982, 0x08000994) | Set high once PA3 drops below the threshold (0x08000AF0) and never cleared again | Output to another CPU ("power fail" flag?) |
| PA13/PA14 | 19/20 | 16/17 | Untouched (reset default = SWDIO/SWCLK) | — | SWD test points DIO/CLK |
| NRST | 4 | 1 | — | — | RST# test point |
| PA0, PA5, PA9, PA10, PF0, PF1 | 6, 11, 17, 18, 2, 3 | 3, 8, 14, 15, 19, 20 | Untouched (reset = floating input) | — | Unused by firmware (may still be wired) |

## ADC
- 0x08000360 init: continuous mode (CTL1.CTN, 0x080006F4 arg 2), ETSRC=SWRCST and ETERC=1, right alignment, routine length 1, rank0=CH3 at 239.5 cycles, 12-bit (DRES=0), ADCON, delay 1 ms, then calibration (RSTCLB, then CLB).
- 0x0800084C read: rank0=CH3 at **7.5 cycles** (overrides init), SWRCST, clear EOC, poll EOC with a 1,000,000-iteration timeout, read ADC_RDATA (returns -1 on timeout).
- 0x080008D0: mean of 10 readings. 0x080007D8: threshold `<= 0x7C1` (1985/4095 ≈ 48.5% of VREF, ≈1.60 V if VDDA = 3.3 V. VDDA isn't measured).

## SysTick / NVIC / SCB
- SysTick_Config(72 MHz/1000) gives a 1 ms tick (0x080010AC). The ISR at 0x08000180 decrements `g_delay_ms` and increments `g_tick_ms`.
- NVIC_SetPriority(SysTick) is set to 3, then to 0. No NVIC_ISER write, so no peripheral interrupts are enabled.
- SCB_VTOR = 0x08000000 (0x08000DA0).

## Memory use (SRAM, 4 KiB available)
| Address | Var | Evidence |
|---|---|---|
| 0x20000000 | g_SystemCoreClock (.data = 72000000) | 0x080010B0 |
| 0x20000004 | g_btn_last (.data = 1) | main |
| 0x20000008 | g_delay_ms | 0x08000814/0x08000830 |
| 0x2000000C | g_press_tick | 0x08000C96, 0x08000D0A |
| 0x20000010 | g_blink_count | 0x08000C9E, 0x08000CC8, 0x08000D32 |
| 0x20000014 | g_mode (written 2 and then 0; **never read**) | 0x08000BC2, 0x08000C1C |
| 0x20000018 | g_tick_ms | 0x080010E0/0x080010E8 |
| 0x20000020–0x2000041F | stack (0x400 bytes). Initial SP = 0x20000420 | vector[0], region table zero-init length 0x418 |
| 0x20000420–0x20000FFF | unused (~3 KiB) | — |
