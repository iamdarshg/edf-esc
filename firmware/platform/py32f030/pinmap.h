#ifndef EDF_ESC_PY32_PINMAP_H
#define EDF_ESC_PY32_PINMAP_H

/* Encoded as port_index * 16 + pin_number: A=0, B=1, F=5. */
enum {
    PIN_CURRENT_ADC = 0,       /* PA0 ADC_IN0 */
    PIN_VBUS_ADC = 1,          /* PA1 ADC_IN1 */
    PIN_BEMF_U_ADC = 2,        /* PA2 ADC_IN2 */
    PIN_BEMF_V_ADC = 3,        /* PA3 ADC_IN3 */
    PIN_BEMF_W_ADC = 4,        /* PA4 ADC_IN4 */
    PIN_NTC_ADC = 5,           /* PA5 ADC_IN5 */
    PIN_TIM1_BKIN = 6,         /* PA6 AF2 */
    PIN_TIM1_CH1N = 7,         /* PA7 AF2 */
    PIN_TIM1_CH1 = 8,          /* PA8 AF2 */
    PIN_TIM1_CH2 = 9,          /* PA9 AF2 */
    PIN_TIM1_CH3 = 10,         /* PA10 AF2 */
    PIN_SWDIO = 13,            /* PA13 */
    PIN_SWCLK = 14,            /* PA14 */
    PIN_TIM1_CH2N = 16,        /* PB0 AF2 */
    PIN_TIM1_CH3N = 17,        /* PB1 AF2 */
    PIN_THROTTLE = 20,         /* PB4 TIM3_CH1 AF1 */
    PIN_GATE_SUPPLY_FAULT = 21,/* PB5 GPIO input */
    PIN_SPI2_MOSI = 23,        /* PB7 AF1 */
    PIN_SPI2_CS = 24,          /* PB8 GPIO */
    PIN_SPI2_SCK = 80,         /* PF0 AF0 */
    PIN_SPI2_MISO = 81,        /* PF1 AF0 / input when CS high */
    PIN_NRST = 82,             /* PF2 */
};

_Static_assert(PIN_TIM1_CH1 != PIN_TIM1_CH1N, "CH1 complementary pin collision");
_Static_assert(PIN_TIM1_CH2 != PIN_TIM1_CH2N, "CH2 complementary pin collision");
_Static_assert(PIN_TIM1_CH3 != PIN_TIM1_CH3N, "CH3 complementary pin collision");
_Static_assert(PIN_SPI2_MISO != PIN_SPI2_MOSI, "SPI pin collision");
_Static_assert(PIN_TIM1_BKIN != PIN_THROTTLE, "break/throttle collision");

#endif
