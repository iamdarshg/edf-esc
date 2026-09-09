# EDF-ESC Dual 6S Sensorless Controller Design

## Status and safety boundary

EDF-ESC is a public, open engineering prototype for two independently controlled 6S sensorless BLDC/EDF motors. It is not a certified product and is not rated for 150 A continuous operation. Initial firmware restricts current and duty cycle; 150 A is an experimental hard ceiling unlocked only after staged electrical and thermal characterization. Fabrication files remain marked `UNVALIDATED` until the validation ledger records oscilloscope, current-calibration, thermal, and powered-motor results.

## Physical architecture

The board is a 98 mm x 58 mm, four-layer, 1.6 mm FR4 PCB. All components, connectors, test pads, and reinforcement metal are on the top side. ESC A occupies the left power zone and ESC B the right power zone. A central low-current zone contains the shared 12 V gate supply, 5 V BEC, 3.3 V logic rail, and control connector. Each channel has its own battery pads, calibrated shunt geometry, local DC-link capacitors, bridge, phase pads, gate driver, MCU, analog sensing, and return path. The battery is star-split externally; no PCB segment carries both channels' motor current.

Each of the six half-bridge switches per channel contains three SFS06R025GF MOSFETs in parallel. Every MOSFET has its own tunable gate resistor fed by a matched star fan-out from one DRV8300D output. Gate-source pulldowns are per switching group. Optional RC snubbers are fitted across all phase-switching nodes.

## Power path and reinforcement

High-current paths use broad outer-layer polygons, deliberate inner-layer reinforcement, dense via arrays, and short local loops. Top-side solder-mask openings accept CNC-cut 1-2 mm copper bars or braid on BAT+, BAT-, and phase paths. The repository includes dimensioned DXF reinforcement profiles. Eight-AWG cable lands are top-side slotted pads with strain-relief holes. The copper bars are part of the prototype's current path and are not optional at high current.

The layer intent is:

- L1: components, gate fan-outs, local DC-link loops, exposed high-current copper, analog islands.
- L2: channel-local power returns and quiet signal references; split so neither motor return crosses the other channel.
- L3: channel-local battery/phase reinforcement and auxiliary-power distribution.
- L4: additional return/power reinforcement and low-risk signal routing.

No switching node is allowed beneath an MCU, current amplifier, SPI trace, PWM input, or Kelvin pair.

## Sensing and protection

Each BAT+ branch includes a nominal 0.10 milliohm defined copper shunt with true Kelvin boundaries, four-wire calibration pads, and a nearby 10 kohm NTC. An INA190A3 produces the current ADC signal. The PCB also carries an unpopulated metal-shunt fallback footprint. Firmware converts offset-corrected ADC counts through a stored calibration coefficient and optionally compensates copper temperature using 0.0039/K before calibrated corrections.

Each phase has a protected high-impedance BEMF divider, RC filter, ADC series resistor, and clamp chosen so the MCU pin remains inside its injected-current and voltage limits during 6S switching transients. Each channel separately measures VBUS, current, shunt temperature, and power-stage temperature. Floating-phase zero crossing is compared in software with measured VBUS/2.

The hardware break path uses the PY32 comparator-to-TIM1-BREAK route only if the reference manual proves simultaneous pin and internal-route availability. Otherwise, a fast external comparator drives TIM1 BREAK. This independent path is in addition to sampled software current limiting. DRV8300 faults, watchdog, UVLO/OVLO, startup timeout, stall, lost commutation, desynchronization, throttle loss, SPI timeout, and overtemperature all force a coast-safe state.

## Supplies

One XL1509-derived 12 V rail supplies both DRV8300D devices through separate local filters and at least 10 uF local ceramic capacitance per driver. Worst-case average gate-drive demand is calculated from 36 MOSFETs, gate charge, and PWM frequency.

One XL4016E1 non-synchronous buck provides a target 5.0 V/8 A BEC through top-side heavy-wire pads. The design follows the manufacturer's reference topology and documents inductor ripple, saturation current, diode stress, capacitor ripple, and estimated losses. Eight amperes is a characterization target, not a guaranteed continuous rating. An XC6206-class LDO generates 3.3 V for both MCUs and analog circuitry.

## Control and firmware

Each PY32F030K28U6TR uses TIM1 complementary PWM with hardware deadtime. A checked pin-mux table must demonstrate simultaneous six PWM outputs, three BEMF ADC inputs, current ADC, VBUS ADC, at least one NTC ADC, PWM throttle input, SPI slave with independent CS and tri-stated MISO, fault/break, and SWD. If the exact QFN-32 package cannot satisfy this concurrently after all documented remaps, the BOM may move to the cheapest stocked compatible MCU, with the rejected mapping and cost delta recorded.

Both MCUs run the same bare-metal C source with a channel configuration constant. The nonblocking state machine is `DISARMED -> ALIGN -> OPEN_LOOP_RAMP -> CLOSED_LOOP -> FAULT`. Closed-loop six-step commutation blanks switching noise, detects the correct floating-phase crossing around VBUS/2, schedules nominal 30-electrical-degree commutation delay, and applies configurable advance. Default PWM is 16 kHz; supported evaluation settings are 12, 16, 20, and 24 kHz. The default motor is four-pole, while pole count is configurable.

PWM throttle accepts a configurable range centered on 1000-2000 us at 50-400 Hz and becomes invalid after 100 ms. The shared SPI bus uses separate chip selects. Frames contain sync, command, payload length, payload, and CRC-8. Commands cover throttle, arm/disarm, emergency stop, PWM frequency, current limits, ramp rate, optional direction configuration, telemetry, faults, and firmware version. An inactive slave releases MISO.

Default protection starts conservative: a 100 A software target, soft limiting from 120 A, aggressive limiting at 130 A, and an inaccessible 150 A ceiling until characterization data enables it. Temperature warning/derating starts at 80-90 C and shutdown at 100-110 C, all configurable and explicitly described as PCB/NTC rather than junction temperatures.

## Repository deliverables

- `hardware/edf-esc.kicad_sch`, `hardware/edf-esc.kicad_pcb`, project settings, custom symbols, and custom footprints.
- `hardware/mechanical/` with board drawing, STEP export when the CLI supports it, and CNC reinforcement DXF files.
- `firmware/common/`, `firmware/platform/py32f030/`, and channel configurations with reproducible builds.
- `host/` reference SPI encoder/decoder and calibration utilities.
- `tests/` host-executable tests for commutation tables, state transitions, CRC/framing, protection limits, calculations, BOM integrity, pin-mux completeness, and manufacturing-file presence.
- `bom/` with JLCPCB/LCSC-first and Mouser-secondary sourcing, prices captured with dates, alternatives, and selection reasons.
- `calculations/` with machine-readable inputs and generated reports for gates, switching/conduction loss, shunt geometry, BEC, DC-link, and copper loss.
- `manufacturing/` with Gerbers, drill files, BOM/CPL, fabrication notes, assembly drawings, and SHA-256 manifests.

## Verification gates

Automated gates are KiCad ERC with reviewed exclusions, KiCad DRC, board dimension and top-side-only checks, BOM-reference consistency, firmware compilation, host tests, formatting/static analysis, Gerber/drill generation, and clean regeneration from scripts. Passing automation means the files are internally consistent; it does not validate high-current performance.

Physical gates progress through: unpowered inspection; gate-only testing; current-limited low-voltage switching; 3S low-power motor operation; 6S restricted-current operation; then full characterization. Each stage records supply limits, load, waveforms, deadtime, ringing, temperatures, current-calibration error, observed faults, operator, date, and artifact hashes. Full-power use requires validated bus transient margin, equal gate behavior among parallel FETs, stable BEMF handoff, shunt calibration, acceptable MOSFET/PCB/BEC temperatures, and a documented safe operating envelope.

## Engineering assumptions

JLCPCB is the fabrication and primary top-side PCBA target. LCSC is the first sourcing choice and Mouser is the verified secondary source. The board uses separate BAT_A and BAT_B leads from an external star point, 8-AWG cable at full-power experiments, forced airflow from the EDF installation, and soldered top copper reinforcement for any test above the low-current bring-up envelope. Exact component ratings, footprints, availability, and pin functions come from archived manufacturer datasheets, never distributor headlines alone.
