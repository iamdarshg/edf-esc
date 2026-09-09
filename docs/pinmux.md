# PY32F030K28U6TR pin-mux decision

The selected QFN-32 K2 device can expose the three complementary TIM1 pairs while retaining six ADC inputs, SPI2, throttle capture, hardware break, reset, and SWD. `hardware/pinmux.csv` is the machine-checked allocation. It is based on PY32F030 Datasheet Rev1.3, QFN32 K2 pin definition table 4-2 and alternate-function tables 4-4/4-5.

TIM1 uses PA8/PA7 for CH1/CH1N, PA9/PB0 for CH2/CH2N, and PA10/PB1 for CH3/CH3N. Analog inputs PA0-PA5 cover current, VBUS, three BEMF phases, and one power-stage NTC. SPI2 avoids those pins by using PF0 SCK, PB7 MOSI, PF1 MISO, and PB8 as software NSS. PB4 captures throttle with TIM3_CH1. PA6 is TIM1_BKIN. PA13/PA14 retain SWD and PF2 retains reset.

## Corrected gate-driver fault requirement

DRV8300DRGER has no `nFAULT` output pin. Its UVLO and cross-conduction features act internally but cannot satisfy the prompt's requested gate-driver-fault input. The design therefore monitors the 12 V gate rail with an external supervisor/comparator on PB5 and routes the fast overcurrent comparator directly to PA6/TIM1_BKIN. Firmware reports `GATE_SUPPLY_FAULT`; it must not mislabel that signal as internal DRV8300 diagnostics.

## ADC-resource consequence

All six conveniently routed ADC channels are used. The base build provides one NTC ADC per channel, satisfying the mandatory requirement. A second NTC footprint can be populated through an analog multiplexer option but is not part of the minimum build because it would add cost and sampling complexity.
