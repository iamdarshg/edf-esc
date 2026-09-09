#ifndef EDF_ESC_PLATFORM_H
#define EDF_ESC_PLATFORM_H

#include "edf_esc/control.h"

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    uint16_t current_adc;
    uint16_t vbus_adc;
    uint16_t bemf_adc[3];
    uint16_t ntc_adc;
} platform_samples_t;

void platform_safe_init(void);
void platform_pwm_configure(uint32_t frequency_hz, uint16_t deadtime_ns);
void platform_apply_outputs(esc_outputs_t outputs, uint16_t duty);
platform_samples_t platform_latest_samples(void);
void platform_spi_release_miso(void);
void platform_watchdog_kick(void);
uint32_t platform_now_us(void);

#endif
