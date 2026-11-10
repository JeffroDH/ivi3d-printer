/*
 * Evidence-based C-like reconstruction of the GD32E230F4 application
 * (flash 0x08000000-0x0800113F; SHA256 540f4967...0167).
 * Every statement here comes from an instruction sequence in gd32e230_annotated.s, cited by address.
 * Names are inferred. Library helpers (gpio_mode_set, adc_*, rcu_*) match the
 * GD32E23x Standard Peripheral Library semantics and are not expanded here.
 * UNCERTAIN = the instructions don't settle the board-level meaning.
 */

/* SRAM globals */
uint32_t SystemCoreClock = 72000000; /* 0x20000000 (.data) */
uint32_t g_btn_last      = 1;        /* 0x20000004 (.data) last sampled PA1 level */
volatile uint32_t g_delay_ms;        /* 0x20000008 */
uint32_t g_press_tick;               /* 0x2000000C */
uint32_t g_blink_count;              /* 0x20000010 */
uint32_t g_mode;                     /* 0x20000014: written, never read */
volatile uint32_t g_tick_ms;         /* 0x20000018 */

void SysTick_Handler(void) {          /* 0x08000180 */
    if (g_delay_ms) g_delay_ms--;     /* 0x08000830 */
    g_tick_ms++;                      /* 0x080010E8 */
}
void delay_ms(uint32_t ms) { g_delay_ms = ms; while (g_delay_ms) ; }   /* 0x08000814 */

#define PA1_high()  gpio_input_bit_get(GPIOA, GPIO_PIN_1)   /* 0x08000B18 (1 = released) */
#define PA6_high()  gpio_input_bit_get(GPIOA, GPIO_PIN_6)   /* 0x08000F98 */
#define PA2_low()   (GPIO_BC(GPIOA)  = GPIO_PIN_2)          /* 0x08000B78 */
#define PA2_high()  (GPIO_BOP(GPIOA) = GPIO_PIN_2)          /* 0x08000B84 */
#define PA2_toggle() (GPIO_TG(GPIOA) = GPIO_PIN_2)          /* 0x08000B8C */
#define PA7_high()  (GPIO_BOP(GPIOA) = GPIO_PIN_7)          /* 0x08000AF0 */
static void PA4_write(int v){ if(v) GPIO_BOP(GPIOA)=GPIO_PIN_4; else GPIO_BC(GPIOA)=GPIO_PIN_4; } /* 0x08000DC0 */
static void PB1_write(int v){ if(v) GPIO_BOP(GPIOB)=GPIO_PIN_1; else GPIO_BC(GPIOB)=GPIO_PIN_1; } /* 0x080007B0 */

static int32_t adc_read_ch3(void) {                       /* 0x0800084C */
    int32_t timeout = 1000000;
    adc_regular_channel_config(0, ADC_CHANNEL_3, ADC_SAMPLETIME_7POINT5);
    adc_software_trigger_enable(ADC_REGULAR_CHANNEL);
    adc_flag_clear(ADC_FLAG_EOC);
    while (!adc_flag_get(ADC_FLAG_EOC) && timeout > 0) timeout--;
    return (timeout <= 0) ? -1 : (int32_t)ADC_RDATA;
}
static uint32_t adc_read_ch3_avg10(void) {               /* 0x080008D0 */
    uint32_t sum = 0;
    for (int i = 0; i < 10; i++) sum += adc_read_ch3();  /* a timeout (-1) isn't handled specially */
    return sum / 10;                                     /* udiv @0x080008FC */
}
static int pa3_low_voltage_check(void) {                  /* 0x080007D8 */
    if (adc_read_ch3_avg10() <= 1985) {                  /* 0x7C1 */
        PB1_write(1);
        PA7_high();
        return 1;
    }
    return 0;
}

static void power_off_and_wait_release(void) {            /* repeated at 0x08000CD2, 0x08000D46 */
    PB1_write(0);
    delay_ms(10);
    PA4_write(0);
    while (!PA1_high()) ;                                /* wait until the button is released */
}

int main(void) {                                         /* 0x08000B98 */
    uint32_t last_blink_tick = 0;                        /* sp+0x28 */
    uint32_t hold_timeout_ms = 3000;                     /* sp+0x24, 0x08000BA2 */

    button_pa1_init();     /* PA1 input pull-up; GPIOA+SYSCFG clocks  (0x08000AF8) */
    systick_config_1ms();  /* (0x080010AC) */
    gpio_outputs_init();   /* PA4,PB1,PA7 outputs low; PA6 input      (0x08000904) */
    led_pa2_init();        /* PA2 output, high                        (0x08000B40) */
    adc_init_PA3();        /* ADC CH3 on PA3, calibrated              (0x08000360) */
    delay_ms(500);
    g_mode = 2;

standby:                                                 /* 0x08000BCA */
    PA2_low();
    for (;;) {                                           /* wait for a debounced press */
        if (!PA1_high()) {
            delay_ms(50);
            if (!PA1_high()) { g_btn_last = 0; break; }
        }
    }
    /* power on                                           0x08000BF6 */
    PA2_high();
    PA4_write(1);
    PB1_write(1);
    while (!PA1_high()) ;                                /* wait for release */
    g_btn_last = 1;
    g_mode = 0;

    for (;;) {                                           /* 0x08000C24 main loop */
        if (pa3_low_voltage_check()) {
            /* latched path: never returns (0x08000C2E-0x08000C6C) */
            uint32_t t0 = g_tick_ms;
            last_blink_tick = t0;
            for (;;) {
                if (PA6_high()) hold_timeout_ms = 6000;
                if (g_tick_ms - t0 > hold_timeout_ms) {
                    PB1_write(0); delay_ms(10); PA4_write(0);   /* repeated each pass */
                }
            }
        }

        uint32_t lvl = PA1_high();
        if (lvl != g_btn_last && g_btn_last == 1) {      /* press edge, 0x08000C8A */
            g_btn_last = 0;
            g_press_tick = g_tick_ms;
            PA2_toggle();
            g_blink_count = 0;
        } else if (PA1_high() != g_btn_last && g_btn_last == 0) { /* release edge, 0x08000CC2 */
            /* note: PA1 is sampled again here */
            g_btn_last = 1;
            if (g_blink_count >= 6) { power_off_and_wait_release(); goto standby; }
        } else if (g_btn_last == 0) {                    /* still held, 0x08000D02 */
            uint32_t now = g_tick_ms;
            if ((now - g_press_tick) % 500 == 0 && last_blink_tick != now) { /* 0x08000D10 */
                last_blink_tick = now;
                PA2_toggle();
                g_blink_count++;
            }
            if (g_blink_count >= 7) { power_off_and_wait_release(); goto standby; }
        } else {                                         /* idle, released, 0x08000D6C */
            g_blink_count = 0;
            PA2_high();
        }
    }
}
/*
 * Timing implied (UNCERTAIN to about +/-1 blink step, because "% 500 == 0" is an exact-match test
 * on a 1 ms tick, and the first step can land at elapsed=0):
 *  - holding the button roughly 3 s turns the system off while it is still held (count reaches 7);
 *  - releasing after roughly 2.5-3 s (count >= 6) also turns it off;
 *  - a shorter press only toggles/blinks the LED, then it goes back to steady on.
 * Unknown: what PA4/PB1/PA3/PA6/PA7 connect to. Firmware alone can't establish that.
 */
