# Current and voltage calibration

Use a traceable four-wire reference shunt and meter. Do not infer calibration
from PCB geometry alone.

For each channel, force 0 A and store the averaged INA190 ADC offset. Apply at
least five current points over the permitted low-power range in both directions
where the setup allows it. Fit `I = gain × (ADC - offset)` and record residual,
temperature, reference-shunt certificate, supply voltage, operator, and firmware
hash. Reject calibration if any point differs by more than 3% before full-power
work.

Measure the Kelvin-to-Kelvin PCB-shunt voltage independently to obtain actual
resistance. Record cold resistance and resistance after thermal equilibrium.
The starting copper coefficient is 0.0039/K, but compensation remains disabled
until measured temperature correlation supports it.

Calibrate VBUS at 3S, 4S, 5S, and 6S-equivalent bench voltages below the source
current limit. Verify the raw ADC node stays below the MCU absolute maximum under
captured switching overshoot, including clamp current through the 1 kΩ series
resistor.
