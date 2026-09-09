# Staged bring-up

Every stage requires an isolated bench, eye protection, a restrained motor,
remote emergency stop, current-limited source, and no loose objects near an EDF.
Record results and artifact hashes in `validation/ledger.csv`.

1. **Unpowered inspection:** verify polarity, isolation between A/B power paths,
   shunt Kelvin boundaries, solder bridges, busbar clearance, and resistance from
   every gate to source. Stop on any unexpected low resistance.
2. **Gate-only power:** omit battery links and power the 12 V/3.3 V rails from
   limited supplies. Verify all six outputs remain off through reset and watchdog,
   then measure high/low gate amplitude and deadtime into dummy capacitive loads.
3. **Low-voltage switching:** use ≤12 V and ≤2 A with an inductive dummy load.
   Capture every switch node, bootstrap voltage, gate-source voltage, ringing,
   and hardware-break latency. Stop for shoot-through, >55 V inferred overshoot,
   unequal parallel-gate behavior, or any reset.
4. **3S motor:** mechanically restrain one motor, one channel at a time, ≤10 A.
   Verify align/ramp, all six BEMF traces, zero-cross handoff, throttle timeout,
   stall handling, and emergency stop.
5. **Restricted 6S:** install approved busbars, begin ≤20 A, and raise load only
   after shunt calibration and thermal soak at the preceding point. Repeat both
   channels separately before simultaneous auxiliary-only operation.
6. **Envelope characterization:** increase current in small steps with logged
   MOSFET/PCB/shunt/capacitor/BEC temperatures and scope captures. The 150 A
   value remains inaccessible until a reviewed safe-operating envelope exists.
