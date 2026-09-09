# EDF-ESC preliminary electrical calculations

> Design estimates only. Values that depend on waveforms, copper plating, airflow, component temperature, or undocumented vendor behavior require measurement before power testing.

## Gate drive

Three 81 nC gates place 243 nC on each DRV8300 output. The 0.75 A source and 1.5 A sink ratings give optimistic lower bounds of 324 ns turn-on and 162 ns turn-off. Actual Miller-plateau edges will differ. A 4.7 ohm resistor per MOSFET is the initial damping value; all 36 footprints permit tuning.

At 12 V, gate-charge power per ESC is `18 * 81 nC * 12 V * f`:

| PWM | One ESC | Both ESCs |
|---:|---:|---:|
| 12 kHz | 0.210 W | 0.420 W |
| 16 kHz | 0.280 W | 0.560 W |
| 20 kHz | 0.350 W | 0.700 W |
| 24 kHz | 0.420 W | 0.840 W |

Using the optimistic 486 ns combined edge time, 25.2 V, and 150 A, one hard-switching group dissipates approximately 11.0, 14.7, 18.4, and 22.0 W at 12, 16, 20, and 24 kHz. Modulation can expose more than one group to hard switching, so layout thermal work uses a 1x-2x bracket until double-pulse measurements replace this estimate. This supports the 16 kHz default and argues against 24 kHz during initial tests.

## MOSFET conduction

Assuming 2.0 milliohm per FET at 25 C and a provisional 1.7 hot multiplier, one three-FET group is 1.13 milliohm. A six-step current path contains one high and one low group, or about 2.27 milliohm before copper and sharing error.

| Phase current | Two-group conduction |
|---:|---:|
| 100 A | 22.7 W |
| 120 A | 32.6 W |
| 150 A | 51.0 W |

These are bridge-level path estimates, not per-FET dissipation. Unequal sharing and temperature feedback are validation risks.

## Copper shunt

One 70 um outer-copper strip 11.6 mm long by 28 mm wide calculates to 99.4 microohm at 20 C. At 150 A it produces 14.9 mV and 2.24 W; INA190A3 gain of 100 produces about 1.49 V. At 100 C the copper model rises by about 31%, so four-wire calibration and temperature compensation are mandatory. Finished plating and soldered reinforcement must stop exactly at the Kelvin boundaries.

## 5 V BEC

For 25.2 V to 5.0 V at 180 kHz with 47 uH, ideal duty is 19.84% and calculated inductor ripple is 0.474 A peak-to-peak. At an 8 A target the ideal inductor peak is 8.24 A, so the selected inductor must retain useful inductance comfortably beyond that current. With a provisional 0.55 V diode drop, diode loss alone is about 3.53 W at 8 A. The BEC therefore requires airflow and 2/4/6/8 A thermal characterization; 8 A is not a guaranteed continuous rating.

## BEMF divider and clamp

The starting divider uses two series 47 kOhm upper resistors and 12 kOhm lower,
followed by 1 kOhm into the ADC clamp. At 25.2 V the open divider output is 2.85
V. A deliberately conservative 60 V phase transient would produce 6.79 V if
unclamped. With a 3.6 V clamp model, the upper/lower Thevenin resistance plus the
1 kOhm series resistor limits current to about 0.274 mA. This proves that a naked
divider is unacceptable; it does not close the gate until the exact PY32
injected-current limit, BAT54 leakage, RC settling, and captured phase overshoot
are verified.

## Mandatory measurements

Measure gate plateau/rise/fall, deadtime, phase-node overshoot, bootstrap droop, DC-link ripple, current-sharing proxy temperatures, four-wire shunt resistance, current-amplifier offset/gain, BEMF settling after blanking, and BEC component temperatures. Replace assumptions in `inputs.yaml` only with traceable measurements in `validation/ledger.csv`.
