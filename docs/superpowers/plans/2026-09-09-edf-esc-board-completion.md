# EDF-ESC Board Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing EDF-ESC engineering prototype into a complete, pin-accurate, ERC/DRC-clean dual-6S KiCad design with target firmware and reproducible JLCPCB manufacturing outputs, while keeping the public repository honest about unvalidated high-current performance.

**Architecture:** Keep the 98 mm × 58 mm mirrored board: ESC A on the left, ESC B on the right, and low-current auxiliary/control circuitry in the centre. Make a connected KiCad schematic the sole netlist authority, then update the PCB from it; use channel-local high-current loops and top-side CNC copper reinforcement so no PCB segment carries combined motor current. Continue the deterministic Python generators, fail-closed release gate, and shared host-tested firmware core with channel-specific PY32 configuration.

**Tech Stack:** KiCad 9 source format with KiCad 7.0.11 compatibility checks, Python 3.12/pytest, C11, GNU Arm Embedded, JLCPCB/LCSC assembly conventions, Mouser secondary sourcing, Git/GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-08-edf-esc-design.md`

## Global Constraints

- Board outline remains exactly 98 mm × 58 mm and never exceeds 100 mm × 60 mm.
- Four copper layers, 1.6 mm FR4; 2 oz all layers where economical, otherwise 2 oz outer layers and the thickest economical inner copper with the deviation documented.
- All component bodies, connectors, cable lands, test pads, and reinforcement remain top-side only.
- BAT_A and BAT_B remain independent from their external star split through their local bridges; no combined-current PCB net or segment is allowed.
- Exactly 36 SFS06R025GF MOSFETs: three per switch, 18 per ESC, with one tunable gate resistor per MOSFET and no daisy-chained gates.
- One DRV8300DRGER and one PY32F030K28U6TR per ESC; do not invent a DRV8300 `nFAULT` pin.
- Default PWM remains 16 kHz; firmware retains 12/16/20/24 kHz evaluation options.
- Default limits remain 100 A target, 120 A soft limit, 130 A aggressive limit, and a locked 150 A experimental ceiling.
- JLCPCB/LCSC is the primary build path; Mouser is the verified secondary source.
- Automation proves internal consistency only. The project remains `UNVALIDATED` and non-fabrication-ready until ERC, DRC, sourcing, and staged physical gates are complete.

---

### Task 1: Publish and continuously synchronize the engineering baseline

**Files:**
- Modify: Git remote `iamdarshg/EDF-ESC`, branch `main`
- Verify: `.github/workflows/ci.yml`, `README.md`, `docs/cad-status.md`

**Interfaces:**
- Consumes: local audited commits and GitHub public repository created by the user.
- Produces: a public source-of-truth branch whose visible head is recorded after every reviewed milestone.

- [ ] Create one Git tree containing every `git ls-files` path, preserving mode `100644`/`100755`.
- [ ] Commit that tree on remote `main` with the existing seed commit as parent.
- [ ] Fetch the remote head and compare the uploaded file set and representative SHA/content for `hardware/edf-esc.kicad_pcb`, `edf_esc/cad.py`, and `scripts/check_release.py`.
- [ ] Keep `README.md` and `docs/cad-status.md` explicit that the current CAD is not safe to fabricate.
- [ ] After every later task passes review, publish its commit and re-verify the remote head.

Verification:

```sh
git ls-files | sort
git status --short
git diff --check
```

Commit message: `chore: publish EDF-ESC engineering baseline`

### Task 2: Freeze pin-accurate symbols and manufacturer land patterns

**Files:**
- Modify: `edf_esc/cad.py`
- Modify: `hardware/lib/edf-esc.kicad_sym`
- Modify: `hardware/lib/edf-esc.pretty/*.kicad_mod`
- Create: `tests/test_kicad_structure.py`
- Create: `docs/footprint-review.md`

**Interfaces:**
- Consumes: archived manufacturer drawings and the frozen MCU pin-mux table.
- Produces: `SYMBOL_PIN_MAPS`, `FOOTPRINT_SPECS`, deterministic symbol/footprint files, and an evidence row for every custom package.

- [ ] Add failing tests that assert DRV8300 RGE pins 1–25, PY32 QFN32 pins 1–33, INA190 DDF pins 1–8, and SFS06R025GF source/gate/drain pad mapping.
- [ ] Run the focused tests and confirm they fail because current symbols use anonymous `P1...Pn` names and provisional geometry.
- [ ] Implement named electrical pin maps and assign the exact custom footprint in every symbol's `Footprint` property.
- [ ] Replace provisional QFN/PDFN/TSOT/SOIC/SOT/TO-220 dimensions with values transcribed from manufacturer drawings; add pin-1, fab, silk, courtyard, paste, exposed-pad, and thermal-via details where required.
- [ ] Record datasheet page/revision, dimension, tolerance, and verification status in `docs/footprint-review.md`; mark unresolved geometry as a fabrication blocker.
- [ ] Regenerate twice and byte-compare the outputs.

Verification:

```sh
python -m pytest tests/test_kicad_structure.py -v
python -m edf_esc.cad
git diff --check
```

Commit message: `feat: verify EDF-ESC symbols and land patterns`

### Task 3: Build the complete connected dual-channel schematic

**Files:**
- Modify: `edf_esc/cad.py`
- Modify: `hardware/edf-esc.kicad_sch`
- Modify: `tests/test_kicad_structure.py`
- Create: `docs/erc-review.md`

**Interfaces:**
- Consumes: Task 2 symbols/footprints, BOM identities, and `hardware/pinmux.csv`.
- Produces: an annotated electrical netlist for power input, ESC A, ESC B, sensing/protection, auxiliary rails, and control/debug.

- [ ] Add failing structural tests for 36 FET symbols, 36 gate resistors, 12 group pulldowns, six bootstrap capacitors, six BEMF dividers/filters, two VBUS dividers, two INA190 channels, two external hardware-break paths, local DC-link capacitors, SWD, PWM throttle, and shared SPI with separate CS.
- [ ] Add failing assertions for independent `BAT_A±`/`BAT_B±`, Kelvin boundaries, and the absence of `BAT_COMBINED` and fabricated driver-fault nets.
- [ ] Generate real symbol instances, numbered pins, wires, junctions, labels, values, references, and assigned footprints; use hierarchical sheets or clearly separated functional sections.
- [ ] Connect each DRV8300 to matched star gate-resistor fan-outs, bootstrap networks, local GVDD filtering, its MCU PWM pins, and its local three-phase bridge.
- [ ] Connect current, VBUS, BEMF, NTC, comparator/BKIN, throttle, SPI, SWD, reset, and auxiliary supply circuits with explicit values from calculation inputs/BOM.
- [ ] Run ERC, resolve genuine faults, and document each intentional exclusion with its exact reference/pin and rationale.

Verification:

```sh
python -m pytest tests/test_kicad_structure.py -v
kicad-cli sch erc -o build/erc.rpt hardware/edf-esc.kicad_sch
rg '^(ERROR|WARNING)' build/erc.rpt
```

Acceptance: parser-valid schematic, zero unexplained ERC errors, exact component counts, and deterministic regeneration.

Commit message: `feat: add connected dual ESC schematic`

### Task 4: Re-place the board around real switching and sensing loops

**Files:**
- Modify: `edf_esc/cad.py`
- Modify: `hardware/edf-esc.kicad_pcb`
- Create: `tests/test_pcb_policy.py`
- Modify: `docs/layout.md`

**Interfaces:**
- Consumes: Task 3 netlist and Task 2 land patterns.
- Produces: locked placement, board stack-up, keepouts, net classes, and measurable routing constraints.

- [ ] Add failing tests for driver-to-gate-resistor distance, matched three-way fan-out length, bootstrap adjacency, local DC-link loop location, Kelvin separation, switching-node keepouts, board edge clearance, top-side-only placement, and reinforcement keepouts.
- [ ] Update the PCB from the schematic without deleting valid reference identities or channel-specific nets.
- [ ] Place each DRV8300 inside its six-switch bank; put each bootstrap capacitor at its driver pins and each gate resistor at its MOSFET gate branch.
- [ ] Place local bulk/ceramic DC-link capacitors directly across each channel's bridge supply loop and keep phase copper away from MCUs, ADC nets, SPI, throttle, SWD, and Kelvin pairs.
- [ ] Lock the accepted placement and record all measurable constraints in `docs/layout.md` and `hardware/net-classes.json`.

Verification:

```sh
python -m pytest tests/test_pcb_policy.py -v
kicad-cli pcb render -o build/board.png hardware/edf-esc.kicad_pcb
git diff --check
```

Commit message: `feat: place EDF-ESC around local power loops`

### Task 5: Route the four-layer PCB and CNC reinforcement system

**Files:**
- Modify: `edf_esc/cad.py`
- Modify: `hardware/edf-esc.kicad_pcb`
- Modify: `hardware/mechanical/reinforcement.csv`
- Modify: `hardware/mechanical/reinforcement.dxf`
- Modify: `tests/test_pcb_policy.py`
- Modify: `docs/layout.md`

**Interfaces:**
- Consumes: locked placement/net classes.
- Produces: fully routed copper, zones, via arrays, exposed reinforcement lands, and dimensioned CNC profiles.

- [ ] Route gate drives first as short, non-daisy-chained matched stars with clean source returns.
- [ ] Route Kelvin/current/BEMF/NTC/MCU/SPI/SWD signals with channel-local quiet reference and no switching copper beneath them.
- [ ] Route BAT+, BAT−, and U/V/W as channel-local polygon systems across appropriate layers with dense current-sharing/thermal vias and no combined-current neck.
- [ ] Add solder-mask openings and mechanical keepouts for 1–2 mm top copper reinforcement; revise DXF/CSV to match the final copper coordinates and mounting clearance.
- [ ] Fill zones, run DRC, fix every error, and document only demonstrably safe waivers.
- [ ] Render and inspect all copper layers, solder mask, courtyard, edge cuts, and reinforcement overlays.

Verification:

```sh
kicad-cli pcb drc --exit-code-violations -o build/drc.rpt hardware/edf-esc.kicad_pcb
kicad-cli pcb gerbers -o build/gerbers hardware/edf-esc.kicad_pcb
python -m pytest tests/test_pcb_policy.py tests/test_mechanical.py -v
```

Acceptance: zero unreviewed DRC violations, zero unconnected pads, exact 98 × 58 mm outline, top-only assembly, and CNC profiles aligned with final board copper.

Commit message: `feat: route four-layer EDF-ESC power board`

### Task 6: Complete and build the PY32F030 target firmware

**Files:**
- Create: `firmware/platform/py32f030/startup.c`
- Create: `firmware/platform/py32f030/platform.c`
- Create: `firmware/platform/py32f030/registers.h`
- Create: `firmware/CMakeLists.txt`
- Create: `firmware/toolchain-arm-none-eabi.cmake`
- Modify: `firmware/esc_a/config.h`, `firmware/esc_b/config.h`
- Modify: `docs/firmware.md`
- Create: `docs/flash-and-debug.md`

**Interfaces:**
- Consumes: tested `firmware/common` APIs and frozen pinmux.
- Produces: ESC A/B ELF, HEX, BIN and map files with identical logic and channel-specific configuration.

- [ ] Add a failing compile/link target for every `platform.h` function and static assertions for timer/ADC/SPI/SWD pin assignments.
- [ ] Implement reset, clock, safe GPIO startup, TIM1 complementary PWM/deadtime/BKIN, triggered ADC, comparator/external-break input, throttle capture, SPI slave/MISO release, watchdog, and fault ISR without blocking delays.
- [ ] Keep outputs disabled until initialization, valid arm sequence, and protection checks complete.
- [ ] Build both channel variants with warnings as errors; inspect maps against 64 KB flash and 8 KB SRAM.
- [ ] Run all host tests and record toolchain/version/hash in `docs/firmware.md`.

Verification:

```sh
cmake -S firmware -B build/firmware -DCMAKE_TOOLCHAIN_FILE=firmware/toolchain-arm-none-eabi.cmake
cmake --build build/firmware -- -j2
ctest --test-dir build/firmware --output-on-failure
make test-c
```

Commit message: `feat: add buildable PY32F030 ESC firmware`

### Task 7: Lock JLCPCB/LCSC and Mouser manufacturing data

**Files:**
- Modify: `bom/edf-esc.csv`, `bom/alternates.csv`, `bom/cost-summary.md`
- Create: `manufacturing/edf-esc-bom.csv`, `manufacturing/edf-esc-cpl.csv`
- Create: `docs/sourcing-review.md`
- Modify: `validation/ledger.csv`

**Interfaces:**
- Consumes: final references, footprints, rotation/origin data, and selected MPNs.
- Produces: JLCPCB-ready BOM/CPL plus source/date/stock/price evidence and Mouser fallbacks.

- [ ] Validate every primary LCSC code against exact MPN, package, lifecycle, stock, assembly class, and captured unit price/date.
- [ ] Validate at least one electrically/package-compatible Mouser alternative for each critical IC, MOSFET class, diode, inductor, capacitor bank, connector, and protection component.
- [ ] Generate BOM/CPL from the final board; assert exact reference-set equality, top-side-only placement, legal rotations, and no missing required MPN/LCSC fields.
- [ ] Separate hand-installed busbars, 8-AWG leads, and other non-PCBA items from JLC placement rows.
- [ ] Recompute prototype cost with priced and unpriced totals stated separately.

Verification:

```sh
python -m pytest tests/test_contracts.py tests/test_bom_cost.py -v
python scripts/check_release.py
```

Commit message: `build: lock JLCPCB and Mouser sourcing data`

### Task 8: Generate release outputs and perform the final fail-closed audit

**Files:**
- Modify: `scripts/release.sh`, `scripts/check_release.py`
- Populate: `manufacturing/gerbers/`, `manufacturing/drill/`
- Create: `manufacturing/SHA256SUMS`, fabrication/assembly drawings, schematic PDF, STEP export when supported
- Modify: `docs/bring-up.md`, `docs/calibration.md`, `docs/thermal-characterization.md`, `docs/cad-status.md`, `README.md`, `CHANGELOG.md`

**Interfaces:**
- Consumes: Tasks 3–7 outputs.
- Produces: reproducible manufacturing archive and an explicit staged-validation envelope.

- [ ] Run full Python/C/firmware/ERC/DRC checks from a clean build directory.
- [ ] Generate Gerbers, drills, BOM, CPL, schematic PDF, layer/fabrication drawings, and STEP; reject empty or stale outputs.
- [ ] Generate twice and compare SHA-256 manifests for deterministic source-derived files.
- [ ] Audit every original requirement against `docs/requirements-traceability.md` and fail on uncovered mandatory rows.
- [ ] Keep fabrication blocked until sourcing fields are verified and ERC/DRC are clean; keep full-power status blocked until staged physical evidence exists.
- [ ] Publish the reviewed source commit. Publish manufacturing artifacts only if their embedded validation status matches the repository.

Verification:

```sh
python -m pytest tests -v
make test-c
kicad-cli sch erc --exit-code-violations -o build/erc.rpt hardware/edf-esc.kicad_sch
kicad-cli pcb drc --exit-code-violations -o build/drc.rpt hardware/edf-esc.kicad_pcb
scripts/release.sh
python scripts/check_release.py
git diff --check
git status --short
```

Commit message: `release: add unvalidated EDF-ESC fabrication candidate`

## Execution policy

- Use Luna for focused implementation and mechanical review tasks by default.
- Use one implementation subagent at a time in the shared worktree; run independent read-only sourcing/layout audits in parallel when capacity permits.
- Every task follows red → green → refactor, then a separate spec/quality review before publication.
- Never suppress ERC/DRC errors merely to make the count reach zero.
- Never publish or label a fabrication release without the explicit fail-closed gates above.
