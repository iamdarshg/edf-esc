# Layout intent and routing constraints

The 98 × 58 mm outline is divided into a left ESC A power cell, a narrow central
control/auxiliary corridor, and a right ESC B power cell. Battery leads star-split
outside the PCB. `BAT_A±` and `BAT_B±` never merge into a board-level motor-current
bus; only low-current auxiliary returns meet at the defined logic star.

Each phase row places three high-side and three low-side PDFN 5×6 devices around a
short local phase polygon. A driver output fans to three equal-length branches,
each terminating in its own 4.7 Ω resistor at the MOSFET gate. Source sense returns
to the driver separately from load copper. Bootstrap capacitor loops must fit
inside the driver/half-bridge cell, with no via in the high-current commutation
loop unless the via array is explicitly modeled.

The current board is not yet routed to this standard. Final routing must enforce:

- 0.5 mm minimum 6S power clearance, increased wherever routing space allows;
- no phase copper below MCU, INA190, SPI, throttle, SWD, or Kelvin routes;
- paired Kelvin traces from the exact copper-shunt boundaries, guarded by quiet
  reference copper and never sharing a current-carrying via;
- high-frequency ceramics directly across each half-bridge local bus loop;
- driver GVDD and bootstrap capacitors adjacent to their pins;
- front-only test points for every gate, phase, bus, current, BEMF, break, and rail;
- at least 1 mm copper-to-edge clearance and isolated M3 keepouts;
- mask openings and mechanical datum holes that register the CNC copper profiles;
- no thermal relief on cable lands or reinforcement interfaces;
- a local via array at each power-pad transition, with drill/aspect ratio accepted
  by the selected JLCPCB four-layer process.

KiCad net classes in `hardware/net-classes.json` are the minimum starting values,
not proof of current capacity. Final current capability depends on the soldered
C110 bars, joints, cable termination, airflow, switching losses, and measured
temperature rise.
