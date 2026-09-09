#include "edf_esc/platform.h"
#include "pinmap.h"
#include "config.h"

_Static_assert(EDF_ESC_DEFAULT_PWM_HZ >= 12000u && EDF_ESC_DEFAULT_PWM_HZ <= 24000u,
               "PWM must remain in the characterized evaluation range");
_Static_assert(EDF_ESC_DEFAULT_POLE_COUNT == 4u, "prototype default must match Rocket 4092");
_Static_assert(EDF_ESC_HIGH_POWER_UNLOCKED == 0, "prototype firmware must boot power-locked");
_Static_assert(EDF_ESC_SPI_CS_PIN == PIN_SPI2_CS, "configuration must match frozen pin map");

char platform_channel_identity(void) { return EDF_ESC_CHANNEL_ID; }
