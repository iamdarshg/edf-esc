# EDF-ESC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a reproducible, reviewable KiCad 9 dual-ESC prototype, bare-metal PY32 firmware, sourcing package, calculations, manufacturing outputs, and staged bring-up documentation.

**Architecture:** A mirrored 98 x 58 mm four-layer board keeps each 150 A-class branch local and independent while sharing only auxiliary supplies and logic ground. Host-testable motor-control/protocol code is separated from PY32 register access, and deterministic generators/checkers make electrical calculations and release artifacts auditable.

**Tech Stack:** KiCad 9 and `kicad-cli`, C11/CMake, Python 3.12/pytest, JLCPCB Gerber/CPL/BOM conventions, GNU Arm Embedded toolchain where available.

**Spec:** `docs/superpowers/specs/2026-09-08-edf-esc-design.md`

## Global Constraints

- PCB outline is 98 mm x 58 mm and never exceeds 100 mm x 60 mm.
- Four copper layers; all bodies, connectors, pads, and reinforcement are top-side only.
- Two independent 6S power paths; no common PCB segment carries combined motor current.
- Exactly 36 SFS06R025GF MOSFETs, three per switch, with one resistor per gate.
- Default firmware PWM is 16 kHz and full-power operation is locked behind characterization.
- JLCPCB/LCSC is primary; Mouser is the verified secondary source.
- Automated checks do not constitute a validated 150 A continuous rating.

---

### Task 1: Reproducible engineering calculations and source ledger

**Files:**
- Create: `pyproject.toml`, `edf_esc/__init__.py`, `edf_esc/calculations.py`, `tests/test_calculations.py`
- Create: `calculations/inputs.yaml`, `calculations/report.md`, `docs/sources.md`

**Interfaces:**
- Produces: `gate_metrics(qg_c, count, source_a, sink_a, frequency_hz)`, `fet_losses(current_a, rds_hot_ohm, voltage_v, tr_s, tf_s, frequency_hz)`, `copper_resistance(length_m, width_m, thickness_m, layers)`, and `buck_ripple(vin_v, vout_v, current_a, frequency_hz, inductance_h)`.

- [ ] Write tests asserting 243 nC group charge, current-limited edge times, positive loss scaling, 0.10 milliohm shunt geometry tolerance, and buck inductor ripple.
- [ ] Run `python -m pytest tests/test_calculations.py -v` and confirm missing-module failure.
- [ ] Implement dimensionally explicit calculations and YAML-to-Markdown report generation.
- [ ] Run the test again and confirm all assertions pass.
- [ ] Record manufacturer document URL, revision/date, SHA-256 when archived, and which design fact each source supports.
- [ ] Commit with `git commit -m "feat: add reproducible electrical calculations"`.

### Task 2: BOM, pin mux, and design-rule contracts

**Files:**
- Create: `bom/edf-esc.csv`, `bom/alternates.csv`, `hardware/pinmux.csv`, `hardware/net-classes.json`
- Create: `edf_esc/contracts.py`, `tests/test_contracts.py`

**Interfaces:**
- Produces: parsers that validate reference counts, mandatory columns, exact part identities, six complementary PWM signals, analog channels, SPI/SWD/fault coexistence, and top-side-only placement policy.

- [ ] Write failing tests for 36 MOSFETs, two drivers/MCUs/current amplifiers, mandatory distributor fields, duplicate MCU pins, missing functions, and forbidden back-side footprints.
- [ ] Run `python -m pytest tests/test_contracts.py -v` and verify the fixtures fail for missing implementation.
- [ ] Implement CSV/JSON validators and populate the pin-mux evidence table from the exact QFN-32 datasheet/reference manual.
- [ ] Populate priced sourcing rows with capture dates; mark unavailable facts as `validation_required` rather than inventing them.
- [ ] Re-run contract tests and commit with `git commit -m "feat: freeze BOM and pin-mux contracts"`.

### Task 3: KiCad library and schematic

**Files:**
- Create: `hardware/edf-esc.kicad_pro`, `hardware/edf-esc.kicad_sch`
- Create: `hardware/lib/edf-esc.kicad_sym`, `hardware/lib/edf-esc.pretty/*.kicad_mod`
- Create: `hardware/sym-lib-table`, `hardware/fp-lib-table`, `tests/test_kicad_structure.py`

**Interfaces:**
- Consumes: BOM identities and verified pin mapping.
- Produces: annotated hierarchical schematic sheets for power input, ESC A, ESC B, auxiliary rails, and control/debug.

- [ ] Write structural tests that reject absent sheets, missing gate resistors, incorrect MOSFET count, missing Kelvin/calibration nodes, missing BEMF channels, and unconnected safety nets.
- [ ] Run `python -m pytest tests/test_kicad_structure.py -v` and confirm failure because the schematic does not exist.
- [ ] Create verified symbols/footprints from mechanical drawings, including exposed pads and courtyard/paste rules.
- [ ] Create the complete hierarchical schematic, annotate it, and assign footprints.
- [ ] Run structural tests and `kicad-cli sch erc -o build/erc.rpt hardware/edf-esc.kicad_sch`; review every exclusion in `docs/erc-review.md`.
- [ ] Commit with `git commit -m "feat: add complete dual ESC schematic"`.

### Task 4: Four-layer PCB and mechanical reinforcement

**Files:**
- Create: `hardware/edf-esc.kicad_pcb`, `hardware/mechanical/*.dxf`, `hardware/mechanical/reinforcement.csv`
- Create: `tests/test_pcb_policy.py`, `docs/layout.md`

**Interfaces:**
- Produces: a routed board with mirrored local power loops, explicit layer stack, net classes, via arrays, exposed copper zones, and CNC copper profiles.

- [ ] Write failing checks for board bounds, four layers, no bottom-side items, no shared combined-current net, driver-to-gate geometry, local bulk capacitors, top test pads, edge clearance, and reinforcement-profile dimensions.
- [ ] Run the policy test and confirm it fails because the board is absent.
- [ ] Place and route ESC A, mirror electrical intent for ESC B without copying net identities, then place central auxiliary supplies and controls.
- [ ] Add zones, thermal-via arrays, solder-mask openings, keepouts, silkscreen safety labels, mounting holes, and top reinforcement features.
- [ ] Run `kicad-cli pcb drc -o build/drc.rpt hardware/edf-esc.kicad_pcb`, inspect 3D clearance, and resolve all non-waived violations.
- [ ] Commit with `git commit -m "feat: route four-layer dual ESC board"`.

### Task 5: Host-tested control core and SPI protocol

**Files:**
- Create: `firmware/common/*.c`, `firmware/include/edf_esc/*.h`, `firmware/tests/*.c`, `firmware/CMakeLists.txt`
- Create: `host/protocol.py`, `tests/test_protocol.py`, `docs/protocol.md`

**Interfaces:**
- Produces: `esc_step()`, `commutation_apply_sector()`, `protection_evaluate()`, `crc8()`, frame encode/decode, telemetry schema, and deterministic state transitions.

- [ ] Write failing C tests for six valid sectors, safe invalid-sector output, alignment/ramp/handoff, 100 ms control loss, overcurrent tiers, overtemperature, UV/OV, stall/desync, and emergency stop.
- [ ] Write failing Python tests for sync, payload length, CRC rejection, command round trips, and MISO-release semantics.
- [ ] Run `ctest --test-dir build/firmware --output-on-failure` and `python -m pytest tests/test_protocol.py -v`; confirm expected failures.
- [ ] Implement the smallest nonblocking control core and binary protocol that passes each test.
- [ ] Re-run both suites, use sanitizers for the host C build, and commit with `git commit -m "feat: implement tested ESC control core"`.

### Task 6: PY32F030 platform firmware

**Files:**
- Create: `firmware/platform/py32f030/*.c`, `firmware/platform/py32f030/*.h`, `firmware/esc_a/config.h`, `firmware/esc_b/config.h`, `firmware/toolchain-arm-none-eabi.cmake`
- Create: `docs/firmware.md`, `docs/flash-and-debug.md`

**Interfaces:**
- Consumes: common control core and frozen pin map.
- Produces: TIM1 complementary PWM/deadtime/break, timer-triggered ADC sampling, throttle capture, SPI slave, watchdog, and SWD firmware images.

- [ ] Add compile-time assertions tying peripheral pins/channels to the pin-mux contract and tests that both channel configs retain conservative limits.
- [ ] Confirm the target build fails before platform functions are defined.
- [ ] Implement reset/startup, clocks, GPIO safe state, TIM1, ADC, comparators/break, input capture, SPI, watchdog, and fault ISR without blocking motor-control delays.
- [ ] Build both variants with warnings as errors, inspect map files for 64 KB flash/8 KB SRAM limits, and generate `.elf`, `.hex`, and `.bin` artifacts.
- [ ] Commit with `git commit -m "feat: add PY32 dual-channel firmware targets"`.

### Task 7: Manufacturing, calibration, and bring-up package

**Files:**
- Create: `scripts/release.sh`, `scripts/check_release.py`, `manufacturing/README.md`
- Create: `docs/bring-up.md`, `docs/calibration.md`, `docs/thermal-characterization.md`, `validation/ledger.csv`
- Generate: `manufacturing/gerbers/*`, `manufacturing/drill/*`, `manufacturing/edf-esc-bom.csv`, `manufacturing/edf-esc-cpl.csv`, `manufacturing/SHA256SUMS`

**Interfaces:**
- Produces: one-command deterministic release package and staged test forms for modes 1-5.

- [ ] Write failing release checks for required files, nonempty plots, matching references, board dimensions, top-side CPL entries, and hash-manifest integrity.
- [ ] Generate Gerbers, drills, position files, BOM, schematic PDF, assembly/fabrication drawings, and STEP model using `kicad-cli`.
- [ ] Document four-wire shunt calibration, BEMF observation, deadtime/ringing capture, BEC loads at 2/4/6/8 A, and abort criteria.
- [ ] Run release checks from a clean build directory twice and compare hashes for deterministic source-derived outputs.
- [ ] Commit with `git commit -m "build: add manufacturing and bring-up package"`.

### Task 8: Final audit and public release

**Files:**
- Create: `README.md`, `LICENSE`, `.github/workflows/ci.yml`, `CHANGELOG.md`
- Modify: validation/status badges only from actual command results.

**Interfaces:**
- Produces: public repository with reproducible CI and explicit prototype status.

- [ ] Map every source-prompt requirement to a file/test in `docs/requirements-traceability.md` and fail CI for uncovered mandatory rows.
- [ ] Run full pytest, host C tests/sanitizers, both embedded builds, ERC, DRC, release generation, archive inspection, and `git diff --check`.
- [ ] Confirm README never claims validated current or BEC performance and gives staged safety instructions before file links.
- [ ] Create the public `iamdarshg/EDF-ESC` repository, push `main`, and verify the remote commit equals the locally audited commit.
- [ ] Publish release artifacts only when the validation status inside them matches the repository status.
