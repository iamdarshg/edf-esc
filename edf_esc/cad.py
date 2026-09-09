"""Deterministic KiCad source generation for the review prototype.

The generated PCB is intentionally source-controlled: regeneration is tested byte
for byte so manufacturing plots can always be traced to reviewed Python inputs.
"""

from __future__ import annotations

import re
from pathlib import Path

BOARD_VERSION = 20221018
SCHEMATIC_VERSION = 20230121


def _qfn_fet(ref: str, x: float, y: float, gate: str, source: str, drain: str,
             nets: dict[str, int]) -> str:
    pads = []
    for number, px, py, net in (
        (1, -2.35, -1.90, source), (2, 0, -1.90, source), (3, 2.35, -1.90, source),
        (4, -2.35, 1.90, gate), (5, -0.78, 1.90, drain), (6, 0, 1.90, drain),
        (7, 0.78, 1.90, drain), (8, 2.35, 1.90, drain),
    ):
        pads.append(
            f'    (pad "{number}" smd roundrect (at {px:.2f} {py:.2f}) '
            f'(size 1.25 1.5) (layers "F.Cu" "F.Paste" "F.Mask") '
            f'(roundrect_rratio 0.2) (net {nets[net]} "{net}"))'
        )
    return "\n".join([
        f'  (footprint "EDF_ESC:PDFN56" (layer "F.Cu") (at {x:.2f} {y:.2f})',
        f'    (fp_text reference "{ref}" (at 0 -3.3 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
        '    (fp_text value "SFS06R025GF" (at 0 3.3 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
        '    (attr smd)',
        '    (fp_rect (start -3 -2.6) (end 3 2.6) (stroke (width 0.2) (type default)) (fill none) (layer "F.SilkS"))',
        *pads,
        '  )',
    ])


def _resistor(ref: str, x: float, y: float, left: str, right: str,
              nets: dict[str, int]) -> str:
    return f'''  (footprint "EDF_ESC:R_0603" (layer "F.Cu") (at {x:.2f} {y:.2f})
    (fp_text reference "{ref}" (at 0 -1.25 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))
    (fp_text value "4R7" (at 0 1.25 0) (layer "F.Fab") (effects (font (size 0.7 0.7) (thickness 0.1))))
    (attr smd)
    (pad "1" smd roundrect (at -0.85 0) (size 0.9 0.95) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2) (net {nets[left]} "{left}"))
    (pad "2" smd roundrect (at 0.85 0) (size 0.9 0.95) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2) (net {nets[right]} "{right}"))
  )'''


def _testpad(ref: str, x: float, y: float, net: str, nets: dict[str, int]) -> str:
    return f'''  (footprint "EDF_ESC:TESTPAD_2MM" (layer "F.Cu") (at {x:.2f} {y:.2f})
    (fp_text reference "{ref}" (at 0 -1.8 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))
    (fp_text value "{net}" (at 0 1.8 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))
    (attr exclude_from_pos_files)
    (pad "1" thru_hole circle (at 0 0) (size 2.5 2.5) (drill 1.0) (layers "*.Cu" "*.Mask") (net {nets[net]} "{net}"))
  )'''


def _device(ref: str, value: str, package: str, x: float, y: float,
            pad_nets: list[str | None], nets: dict[str, int]) -> str:
    count = len(pad_nets)
    pads: list[str] = []
    if package.startswith("QFN"):
        perimeter = count - 1
        per_side = perimeter // 4
        positions: list[tuple[float, float, float]] = []
        for i in range(per_side):
            offset = -((per_side - 1) * 0.5) * 0.5 + i * 0.5
            positions.append((-2.35 if perimeter == 32 else -1.85, -offset, 90))
        for i in range(per_side):
            offset = -((per_side - 1) * 0.5) * 0.5 + i * 0.5
            positions.append((offset, -2.35 if perimeter == 32 else -1.85, 0))
        for i in range(per_side):
            offset = -((per_side - 1) * 0.5) * 0.5 + i * 0.5
            positions.append((2.35 if perimeter == 32 else 1.85, offset, 90))
        for i in range(per_side):
            offset = -((per_side - 1) * 0.5) * 0.5 + i * 0.5
            positions.append((-offset, 2.35 if perimeter == 32 else 1.85, 0))
        positions.append((0, 0, 0))
        for number, ((px, py, angle), net) in enumerate(zip(positions, pad_nets), 1):
            size = "2.8 2.8" if number == count and perimeter == 32 else ("2.5 2.5" if number == count else "0.9 0.28")
            shape = "rect" if number == count else "roundrect"
            rr = " (roundrect_rratio 0.2)" if shape == "roundrect" else ""
            net_clause = f' (net {nets[net]} "{net}")' if net else ""
            pads.append(f'    (pad "{number}" smd {shape} (at {px:.2f} {py:.2f} {angle}) (size {size}) (layers "F.Cu" "F.Paste" "F.Mask"){rr}{net_clause})')
        body = 5.0 if perimeter == 32 else 4.0
    elif package == "SOIC8" or package == "TSOT23-8":
        pitch = 1.27 if package == "SOIC8" else 0.65
        row_x = 2.6 if package == "SOIC8" else 1.5
        positions = [(-row_x, (i - 1.5) * pitch, 0) for i in range(4)] + [(row_x, (1.5 - i) * pitch, 0) for i in range(4)]
        for number, ((px, py, angle), net) in enumerate(zip(positions, pad_nets), 1):
            net_clause = f' (net {nets[net]} "{net}")' if net else ""
            pads.append(f'    (pad "{number}" smd roundrect (at {px:.2f} {py:.2f} {angle}) (size 1.4 0.55) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2){net_clause})')
        body = 4.0 if package == "SOIC8" else 3.0
    elif package == "SOT23-3":
        positions = [(-0.95, 1.0, 0), (0.95, 1.0, 0), (0, -1.0, 0)]
        for number, ((px, py, angle), net) in enumerate(zip(positions, pad_nets), 1):
            net_clause = f' (net {nets[net]} "{net}")' if net else ""
            pads.append(f'    (pad "{number}" smd roundrect (at {px:.2f} {py:.2f} {angle}) (size 1.0 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2){net_clause})')
        body = 3.0
    elif package == "TO220-5":
        positions = [((i - 2) * 1.7, 0, 0) for i in range(5)]
        for number, ((px, py, angle), net) in enumerate(zip(positions, pad_nets), 1):
            net_clause = f' (net {nets[net]} "{net}")' if net else ""
            pads.append(f'    (pad "{number}" thru_hole circle (at {px:.2f} {py:.2f} {angle}) (size 1.6 1.6) (drill 0.9) (layers "*.Cu" "*.Mask"){net_clause})')
        body = 10.0
    else:
        raise ValueError(package)
    return "\n".join([
        f'  (footprint "EDF_ESC:{package}" (layer "F.Cu") (at {x:.2f} {y:.2f})',
        f'    (fp_text reference "{ref}" (at 0 -3.5 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        f'    (fp_text value "{value}" (at 0 3.5 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '    (attr smd)',
        f'    (fp_rect (start {-body/2:.2f} {-body/2:.2f}) (end {body/2:.2f} {body/2:.2f}) (stroke (width 0.15) (type default)) (fill none) (layer "F.Fab"))',
        *pads,
        '  )',
    ])


def build_board() -> str:
    fixed_nets = [
        "GND", "BAT_A+", "BAT_A-", "MOTOR_A_U", "MOTOR_A_V", "MOTOR_A_W",
        "BAT_B+", "BAT_B-", "MOTOR_B_U", "MOTOR_B_V", "MOTOR_B_W",
        "12V_GATE", "5V_BEC", "+3V3", "KELVIN_A+", "KELVIN_A-",
        "KELVIN_B+", "KELVIN_B-", "TIM1_BKIN_A", "TIM1_BKIN_B",
    ]
    gate_groups = [f"G_{ch}_{phase}{side}" for ch in "AB" for phase in "UVW" for side in "HL"]
    gate_pads = [f"{group}_{n}" for group in gate_groups for n in range(1, 4)]
    bemf = [f"BEMF_{ch}_{phase}" for ch in "AB" for phase in "UVW"]
    controls = [f"PWM_{ch}_{phase}{side}" for ch in "AB" for phase in "UVW" for side in "HL"]
    bootstrap = [f"BST_{ch}_{phase}" for ch in "AB" for phase in "UVW"]
    sensed = [f"CURRENT_{ch}" for ch in "AB"] + [f"VBUS_ADC_{ch}" for ch in "AB"] + [f"NTC_{ch}" for ch in "AB"]
    interfaces = ["SPI_SCK", "SPI_MOSI", "SPI_MISO", "CS_A", "CS_B", "THROTTLE_A", "THROTTLE_B", "SWDIO_A", "SWCLK_A", "SWDIO_B", "SWCLK_B", "NRST_A", "NRST_B", "GATE_SUPPLY_FAULT_A", "GATE_SUPPLY_FAULT_B", "BEC_SW", "BEC_FB", "12V_SW", "12V_FB"]
    names = fixed_nets + gate_groups + gate_pads + bemf + controls + bootstrap + sensed + interfaces
    nets = {name: i + 1 for i, name in enumerate(names)}
    out = [
        f'(kicad_pcb (version {BOARD_VERSION}) (generator pcbnew)',
        '  (general (thickness 1.6))',
        '  (paper "A4")',
        '  (layers',
        '    (0 "F.Cu" signal)',
        '    (2 "In1.Cu" power)',
        '    (4 "In2.Cu" power)',
        '    (31 "B.Cu" signal)',
        '    (36 "B.SilkS" user "b.silkscreen")',
        '    (37 "F.SilkS" user "f.silkscreen")',
        '    (44 "Edge.Cuts" user)',
        '  )',
        '  (setup (pad_to_mask_clearance 0))',
        *[f'  (net {number} "{name}")' for name, number in nets.items()],
        '  (gr_rect (start 0 0) (end 98 58) (stroke (width 0.1) (type default)) (fill none) (layer "Edge.Cuts"))',
        '  (gr_text "EDF-ESC REV A  UNVALIDATED" (at 49 3) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))',
        '  (gr_text "DANGER: DUAL 6S HIGH CURRENT" (at 49 55) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.18))))',
    ]

    groups = [("U", "H"), ("U", "L"), ("V", "H"), ("V", "L"), ("W", "H"), ("W", "L")]
    for ch, x0 in (("A", 7.0), ("B", 66.0)):
        batp, batm = f"BAT_{ch}+", f"BAT_{ch}-"
        for group_index, (phase, side) in enumerate(groups):
            row, column = divmod(group_index, 2)
            source = f"MOTOR_{ch}_{phase}" if side == "H" else batm
            drain = batp if side == "H" else f"MOTOR_{ch}_{phase}"
            group_gate = f"G_{ch}_{phase}{side}"
            for parallel in range(3):
                ordinal = group_index * 3 + parallel + 1
                x = x0 + column * 15.5 + parallel * 4.8
                y = 14.0 + row * 15.0
                fet_gate = f"{group_gate}_{parallel + 1}"
                out.append(_qfn_fet(f"Q{ch}{ordinal}", x, y, fet_gate, source, drain, nets))
                out.append(_resistor(f"RG{ch}{ordinal}", x, y - 5.0, group_gate, fet_gate, nets))
                out.append(f'  (segment (start {x + 0.85:.2f} {y - 5:.2f}) (end {x - 2.35:.2f} {y + 1.90:.2f}) (width 0.35) (layer "F.Cu") (net {nets[fet_gate]}))')
                if parallel:
                    out.append(f'  (segment (start {x - 5.65:.2f} {y - 5:.2f}) (end {x - 0.85:.2f} {y - 5:.2f}) (width 0.4) (layer "F.Cu") (net {nets[group_gate]}))')
                power_net = drain if side == "H" else source
                power_pad_y = y + 1.90 if side == "H" else y - 1.90
                out.append(f'  (via (at {x:.2f} {power_pad_y:.2f}) (size 1.2) (drill 0.6) (layers "F.Cu" "B.Cu") (net {nets[power_net]}))')

        edge_x = 3.0 if ch == "A" else 95.0
        for phase, y in zip("UVW", (14.0, 29.0, 44.0)):
            out.append(_testpad(f"J{ch}{phase}", edge_x, y, f"MOTOR_{ch}_{phase}", nets))
            zone_x1, zone_x2 = ((1.5, 34.5) if ch == "A" else (63.5, 96.5))
            phase_net = f"MOTOR_{ch}_{phase}"
            out.append(f'''  (zone (net {nets[phase_net]}) (net_name "{phase_net}") (layer "F.Cu") (hatch edge 0.5)
    (connect_pads (clearance 0.4)) (min_thickness 0.25) (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.8))
    (polygon (pts (xy {zone_x1} {y - 2.6}) (xy {zone_x2} {y - 2.6}) (xy {zone_x2} {y + 2.6}) (xy {zone_x1} {y + 2.6})))
  )''')
        out.append(_testpad(f"JBAT{ch}P", edge_x, 6.5, batp, nets))
        out.append(_testpad(f"JBAT{ch}N", edge_x, 51.5, batm, nets))
        kelvin_x = 24.0 if ch == "A" else 74.0
        out.append(_testpad(f"TPK{ch}P", kelvin_x, 5.0, f"KELVIN_{ch}+", nets))
        out.append(_testpad(f"TPK{ch}N", kelvin_x + 4.0, 5.0, f"KELVIN_{ch}-", nets))

    # The centre is deliberately kept low-current and clear of phase copper.
    for ch, x in (("A", 38.0), ("B", 60.0)):
        driver_pins = [
            f"PWM_{ch}_UL", f"PWM_{ch}_VL", f"PWM_{ch}_WL", "12V_GATE", "GND", "GND", None, None,
            f"G_{ch}_WL", f"G_{ch}_VL", f"G_{ch}_UL", f"MOTOR_{ch}_W", f"G_{ch}_WH", f"BST_{ch}_W",
            f"MOTOR_{ch}_V", f"G_{ch}_VH", f"BST_{ch}_V", f"MOTOR_{ch}_U", f"G_{ch}_UH", f"BST_{ch}_U",
            None, f"PWM_{ch}_UH", f"PWM_{ch}_VH", f"PWM_{ch}_WH", "GND",
        ]
        out.append(_device(f"UG{ch}", "DRV8300DRGER", "QFN24", x, 15.0, driver_pins, nets))
        mcu_pins = [
            "+3V3", "SPI_SCK", "SPI_MISO", f"NRST_{ch}", None, f"CURRENT_{ch}", f"VBUS_ADC_{ch}", f"BEMF_{ch}_U",
            f"BEMF_{ch}_V", f"BEMF_{ch}_W", f"NTC_{ch}", f"TIM1_BKIN_{ch}", f"PWM_{ch}_UL", f"PWM_{ch}_VL",
            f"PWM_{ch}_WL", "GND", None, f"PWM_{ch}_UH", f"PWM_{ch}_VH", f"PWM_{ch}_WH", None, None,
            f"SWDIO_{ch}", f"SWCLK_{ch}", None, None, f"THROTTLE_{ch}", f"GATE_SUPPLY_FAULT_{ch}", None, "SPI_MOSI", "GND", f"CS_{ch}", "GND",
        ]
        out.append(_device(f"UC{ch}", "PY32F030K28U6TR", "QFN32", 40.0 if ch == "A" else 58.0, 28.0, mcu_pins, nets))
        ina_pins = ["+3V3", "+3V3", "GND", "GND", f"CURRENT_{ch}", None, f"KELVIN_{ch}+", f"KELVIN_{ch}-"]
        out.append(_device(f"UCS{ch}", "INA190A3IDDFR", "TSOT23-8", 40.0 if ch == "A" else 58.0, 38.0, ina_pins, nets))
    out.append(_device("U12V", "XL1509-ADJ", "SOIC8", 42.0, 48.0,
                       ["12V_SW", "12V_SW", "12V_FB", "GND", None, "BAT_A+", "BAT_A+", None], nets))
    out.append(_device("UBEC", "XL4016E1", "TO220-5", 49.0, 48.0,
                       ["GND", "BEC_FB", "BEC_SW", "BAT_A+", None], nets))
    out.append(_device("U3V3", "XC6206P332MR", "SOT23-3", 56.0, 48.0,
                       ["GND", "+3V3", "5V_BEC"], nets))

    # Four mounting holes, all populated from the top side.
    for index, (x, y) in enumerate(((3, 3), (95, 3), (3, 55), (95, 55)), 1):
        out.append(f'''  (footprint "EDF_ESC:M3_NPTH" (layer "F.Cu") (at {x} {y})
    (fp_text reference "H{index}" (at 0 -3 0) (layer "F.SilkS") hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text value "M3" (at 0 3 0) (layer "F.Fab") hide (effects (font (size 1 1) (thickness 0.15))))
    (attr exclude_from_pos_files exclude_from_bom)
    (pad "" np_thru_hole circle (at 0 0) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))
  )''')

    # Named high-current zones make branch separation inspectable in KiCad.
    for ch, x1, x2 in (("A", 1.5, 39.0), ("B", 59.0, 96.5)):
        for layer, net in (("In1.Cu", f"BAT_{ch}-"), ("In2.Cu", f"BAT_{ch}+")):
            out.append(f'''  (zone (net {nets[net]}) (net_name "{net}") (layer "{layer}") (hatch edge 0.5)
    (connect_pads (clearance 0.5)) (min_thickness 0.25) (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.8))
    (polygon (pts (xy {x1} 5) (xy {x2} 5) (xy {x2} 53) (xy {x1} 53)))
  )''')
    out.append(')')
    return "\n".join(out) + "\n"


def build_schematic() -> str:
    blocks = [
        "POWER INPUT A: BAT_A+ -> KELVIN_A+ / KELVIN_A- -> INA190A3IDDFR",
        "ESC A: DRV8300DRGER + 18x PARALLEL MOSFET + PY32F030K28U6TR",
        "BEMF_A_U BEMF_A_V BEMF_A_W TIM1_BKIN_A",
        "POWER INPUT B: BAT_B+ -> KELVIN_B+ / KELVIN_B- -> INA190A3IDDFR",
        "ESC B: DRV8300DRGER + 18x PARALLEL MOSFET + PY32F030K28U6TR",
        "BEMF_B_U BEMF_B_V BEMF_B_W TIM1_BKIN_B",
        "AUXILIARY: XL1509-ADJ 12V GATE; XL4016E1 5V/8A TARGET; XC6206P332MR 3V3",
        "UNVALIDATED REVIEW SCHEMATIC — see docs/requirements-traceability.md",
    ]
    fet_manifest = " ".join(["SFS06R025GF" for _ in range(36)])
    blocks.append(f"FET MANIFEST: {fet_manifest}")
    lines = [
        f'(kicad_sch (version {SCHEMATIC_VERSION}) (generator eeschema)',
        '  (uuid 3e5b24b0-462c-4f73-9fb1-36e521559001)',
        '  (paper "A4")',
        '  (lib_symbols)',
    ]
    y = 25
    for index, block in enumerate(blocks, 1):
        escaped = block.replace('"', "'")
        lines.extend([
            f'  (text "{escaped}" (at 20 {y} 0)',
            '    (effects (font (size 1.27 1.27)) (justify left bottom))',
            f'    (uuid 3e5b24b0-462c-4f73-9fb1-{index:012d})',
            '  )',
        ])
        y += 12
    lines.extend([
        '  (sheet_instances',
        '    (path "/" (page "1"))',
        '  )',
        ')',
    ])
    return "\n".join(lines) + "\n"


def build_footprints() -> dict[str, str]:
    definitions: dict[str, str] = {}
    for package, value, count in (
        ("QFN24", "DRV8300DRGER", 25),
        ("QFN32", "PY32F030K28U6TR", 33),
        ("TSOT23-8", "INA190A3IDDFR", 8),
        ("SOIC8", "XL1509-ADJ", 8),
        ("TO220-5", "XL4016E1", 5),
        ("SOT23-3", "XC6206P332MR", 3),
    ):
        definitions[f"{package}.kicad_mod"] = _device("REF**", value, package, 0, 0, [None] * count, {})
    fet = _qfn_fet("REF**", 0, 0, "G", "S", "D", {"G": 1, "S": 2, "D": 3})
    definitions["PDFN56.kicad_mod"] = re.sub(r' \(net \d+ "[GSD]"\)', "", fet)
    resistor = _resistor("REF**", 0, 0, "1", "2", {"1": 1, "2": 2})
    definitions["R_0603.kicad_mod"] = re.sub(r' \(net \d+ "[12]"\)', "", resistor)
    return {name: content + ("\n" if not content.endswith("\n") else "") for name, content in definitions.items()}


def build_symbol_library() -> str:
    devices = (
        ("SFS06R025GF", "Q", 8), ("DRV8300DRGER", "U", 24),
        ("PY32F030K28U6TR", "U", 32), ("INA190A3IDDFR", "U", 8),
        ("XL1509-ADJ", "U", 8), ("XL4016E1", "U", 5),
        ("XC6206P332MR", "U", 3),
    )
    lines = ['(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor)']
    for name, prefix, count in devices:
        height = max(5.08, count * 0.635)
        lines.extend([
            f'  (symbol "{name}" (pin_names (offset 0.5)) (in_bom yes) (on_board yes)',
            f'    (property "Reference" "{prefix}" (at 0 {height / 2 + 2:.3f} 0) (effects (font (size 1.27 1.27))))',
            f'    (property "Value" "{name}" (at 0 {-height / 2 - 2:.3f} 0) (effects (font (size 1.27 1.27))))',
            '    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
            '    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
            f'    (symbol "{name}_0_1"',
            f'      (rectangle (start -5.08 {height/2:.3f}) (end 5.08 {-height/2:.3f}) (stroke (width 0.254) (type default)) (fill (type background)))',
            '    )',
            f'    (symbol "{name}_1_1"',
        ])
        for pin in range(1, count + 1):
            left = pin <= (count + 1) // 2
            row = pin - 1 if left else pin - ((count + 1) // 2) - 1
            px, angle = (-7.62, 0) if left else (7.62, 180)
            py = height / 2 - 0.635 - row * 1.27
            lines.extend([
                f'      (pin passive line (at {px:.2f} {py:.3f} {angle}) (length 2.54)',
                f'        (name "P{pin}" (effects (font (size 0.8 0.8))))',
                f'        (number "{pin}" (effects (font (size 0.8 0.8))))',
                '      )',
            ])
        lines.extend(['    )', '  )'])
    lines.append(')')
    return "\n".join(lines) + "\n"


def write_cad(root: Path) -> None:
    hardware = root / "hardware"
    hardware.mkdir(parents=True, exist_ok=True)
    (hardware / "edf-esc.kicad_pcb").write_text(build_board())
    (hardware / "edf-esc.kicad_sch").write_text(build_schematic())
    library = hardware / "lib"
    footprints = library / "edf-esc.pretty"
    footprints.mkdir(parents=True, exist_ok=True)
    for name, content in build_footprints().items():
        (footprints / name).write_text(content)
    (library / "edf-esc.kicad_sym").write_text(build_symbol_library())


if __name__ == "__main__":
    write_cad(Path(__file__).parents[1])
