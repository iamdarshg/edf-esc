# Firmware architecture and status

Both ESCs use the same C11 control sources. `firmware/esc_a/config.h` and
`firmware/esc_b/config.h` change only channel identity; both retain 16 kHz PWM,
a four-pole motor default, and the compile-time high-power lock.

## Implemented and host-tested

- coast-safe six-step output table;
- `DISARMED -> ALIGN -> OPEN_LOOP_RAMP -> CLOSED_LOOP -> FAULT` state machine;
- switching blanking and hysteretic floating-phase zero-cross detection;
- 30-electrical-degree commutation timing with configurable advance;
- current and temperature duty derating;
- latched hard overcurrent, overtemperature, UV, OV, stall, control-timeout,
  and emergency-stop faults;
- CRC-8 command framing and the shared-SPI MISO release rule;
- compile-time validation of the exact QFN-32 TIM1, ADC, throttle, SPI, break,
  and SWD pin allocation for both channel variants.

Run `make test` for the native test suite. The safety core is deliberately free
of PY32 register access so it can be tested with warnings-as-errors and
sanitizers on a workstation.

## Embedded-build blocker

The repository does not yet contain a vendor startup file, CMSIS device header,
linker script, or completed register-level platform implementation. Therefore it
does not yet emit honest `.elf`, `.hex`, or `.bin` images. Those pieces must be
added from a redistributable Puya SDK revision, then the resulting 64 KiB flash / 8
KiB SRAM map must be checked before the firmware is flashed. The pin contract is
ready, but a host build must not be mislabeled as target firmware.
