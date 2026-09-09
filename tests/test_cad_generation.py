from pathlib import Path
import re

from edf_esc.cad import build_board, build_footprints, build_schematic, build_symbol_library


def test_board_is_four_layer_98_by_58_and_top_side_only():
    board = build_board()
    assert '(2 "In1.Cu" power)' in board
    assert '(4 "In2.Cu" power)' in board
    assert '(31 "B.Cu" signal)' in board
    assert '(gr_rect (start 0 0) (end 98 58)' in board
    assert '(layer "B.Cu")' not in board.split("(footprint", 1)[-1]


def test_board_contains_exact_parallel_power_stage_and_independent_inputs():
    board = build_board()
    assert len(re.findall(r'fp_text reference "Q[AB]\d+"', board)) == 36
    assert len(re.findall(r'fp_text reference "RG[AB]\d+"', board)) == 36
    for net in ("BAT_A+", "BAT_A-", "MOTOR_A_U", "MOTOR_A_V", "MOTOR_A_W",
                "BAT_B+", "BAT_B-", "MOTOR_B_U", "MOTOR_B_V", "MOTOR_B_W"):
        assert f'"{net}"' in board
    assert "BAT_COMBINED" not in board


def test_schematic_names_all_mandatory_functional_blocks():
    schematic = build_schematic()
    for token in (
        "DRV8300DRGER", "PY32F030K28U6TR", "INA190A3IDDFR", "XL4016E1",
        "XL1509-ADJ", "XC6206P332MR", "KELVIN_A+", "KELVIN_A-",
        "KELVIN_B+", "KELVIN_B-", "BEMF_A_U", "BEMF_A_V", "BEMF_A_W",
        "BEMF_B_U", "BEMF_B_V", "BEMF_B_W", "TIM1_BKIN_A", "TIM1_BKIN_B",
    ):
        assert token in schematic
    assert schematic.count("SFS06R025GF") == 36


def test_control_devices_have_full_package_pad_counts():
    board = build_board()
    driver = board.split('fp_text reference "UGA"', 1)[1].split("(footprint", 1)[0]
    mcu = board.split('fp_text reference "UCA"', 1)[1].split("(footprint", 1)[0]
    current_amp = board.split('fp_text reference "UCSA"', 1)[1].split("(footprint", 1)[0]
    assert driver.count("(pad ") == 25
    assert mcu.count("(pad ") == 33
    assert current_amp.count("(pad ") == 8
    assert "PLACEHOLDER_" not in board


def test_checked_in_cad_matches_generator():
    root = Path(__file__).parents[1]
    assert (root / "hardware/edf-esc.kicad_pcb").read_text() == build_board()
    assert (root / "hardware/edf-esc.kicad_sch").read_text() == build_schematic()
    for name, content in build_footprints().items():
        assert (root / "hardware/lib/edf-esc.pretty" / name).read_text() == content
    assert (root / "hardware/lib/edf-esc.kicad_sym").read_text() == build_symbol_library()
