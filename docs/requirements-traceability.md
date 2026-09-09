# Requirements traceability

This table distinguishes implemented evidence from remaining work. “Pass” means
an automated structural or software check passes; it does not imply physical
validation.

| Requirement | Evidence | Status |
|---|---|---|
| One board, two independent ESC paths | `hardware/edf-esc.kicad_pcb`, CAD tests | structural pass |
| ≤100 × 60 mm; four layers; top-side only | 98 × 58 generator contract and tests | pass |
| 36 exact MOSFETs; individual gate resistors | BOM, generated PCB, CAD tests | pass |
| DRV8300D, MCU, INA190 per channel | BOM and review CAD | placement only |
| Proven simultaneous MCU pin mux | `hardware/pinmux.csv`, contract tests | pass |
| BEMF sensing and sensorless control | named CAD nets, `sensorless.c`, tests | firmware pass; analog CAD open |
| PWM throttle + shared SPI/separate CS | pin map, `host/protocol.py`, tests | protocol pass; platform open |
| Command-loss and emergency shutdown | `control.c`, native tests | pass |
| Current, thermal, UV/OV, stall protection | `control.c`, native tests | sampled model pass; hardware open |
| 12 V, 5 V BEC, 3.3 V rails | calculations and BOM | detailed CAD open |
| Loss, shunt, gate, and buck calculations | `calculations/report.md`, calculation tests | pass as estimates |
| Complete connected schematic and exact footprints | `docs/cad-status.md` | blocked |
| Fully routed, zero-error DRC PCB | KiCad DRC report | blocked |
| Target PY32 ELF/HEX/BIN | `docs/firmware.md` | blocked |
| JLCPCB BOM/CPL/Gerbers/drill package | release gate | blocked until CAD passes |
| CNC copper reinforcement drawings | `hardware/mechanical/` | preliminary profiles; final cutouts blocked by routing |
| Physical staged validation at 3S/6S/full load | validation ledger | pending hardware |
