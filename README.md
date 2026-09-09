# EDF-ESC

Open hardware and firmware for a compact 98 mm × 58 mm, four-layer board with
two independent 6S sensorless BLDC/EDF controller channels.

> **Engineering prototype — do not fabricate or connect a battery.** The CAD
> currently contains documented placement placeholders, open nets, and DRC
> violations. It is not a validated 150 A design. See
> [`docs/cad-status.md`](docs/cad-status.md) for the exact blockers.

## Design targets

- two electrically independent power paths; no shared 300 A PCB segment;
- 18 × SFS06R025GF per channel, three devices per switch;
- DRV8300D gate driver and PY32F030K28U6TR controller per channel;
- high-side copper-shunt/INA190A3 current sensing with four-wire calibration;
- sensorless six-step control with PWM throttle and shared SPI/separate CS;
- shared 12 V gate supply, 5 V/8 A characterization-target BEC, and 3.3 V logic;
- JLCPCB/LCSC-first sourcing with Mouser alternatives and top-side assembly;
- top-side CNC copper reinforcement for every high-current path.

## What works today

The calculation engine, BOM/pin-mux contracts, host protocol, commutation table,
startup/control state machine, zero-cross detector, protection model, and both
channel configuration contracts are covered by native tests. KiCad 7.0.11
parses the generated review CAD and exports plots.

```sh
python3 -m venv .venv
.venv/bin/pip install -e '.[test]'
make test
.venv/bin/python -m edf_esc.cad
```

## Repository map

- `hardware/` — deterministic KiCad review project and design-rule contracts
- `firmware/` — tested portable control core and PY32 pin/configuration contract
- `host/` — SPI framing reference
- `bom/` — primary and alternate sourcing tables
- `calculations/` — gate, MOSFET, shunt, copper, and BEC estimates
- `docs/` — architecture, protocol, safety status, and source ledger

The progression to powered testing is intentionally gated: inspection, gate-only
testing, current-limited low-voltage switching, 3S motor testing, restricted 6S,
then thermal/electrical characterization. A numerical current ceiling is not a
continuous-current rating.

## License

MIT. See [`LICENSE`](LICENSE). Component datasheets and vendor SDK files are not
redistributed unless their licenses permit it.
