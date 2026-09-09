# Thermal characterization

Characterize one channel first, then both auxiliaries, and only then consider two
motors. Use thermocouples on representative high/low MOSFET cases, PCB beneath
each bank, shunt, bulk capacitors, XL4016, catch diode, BEC inductor, 12 V supply,
and both busbar joints. An IR camera is supplementary; emissivity errors do not
replace contact measurements.

At each current point hold until temperature slope remains below 1 °C over five
minutes or an abort limit is reached. Record airflow and ambient temperature.
Abort on 100 °C PCB/NTC, 90 °C electrolytic case, 110 °C inductor/catch diode,
unexpected >10 °C spread among parallel MOSFETs, worsening ringing, calibration
drift >3%, or any protection event.

Test the BEC separately at 2, 4, 6, then 8 A with 6S input. Log input/output power,
ripple, inductor and diode case temperature, and shutdown behavior. Eight amperes
is a characterization target, not a continuous rating, until this record passes.
