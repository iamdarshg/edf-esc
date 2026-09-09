from pathlib import Path

import pytest

from edf_esc.contracts import validate_bom, validate_pinmux


ROOT = Path(__file__).parents[1]


def test_core_bom_has_exact_required_quantities_and_columns():
    result = validate_bom(ROOT / "bom/edf-esc.csv")
    assert result.quantities["SFS06R025GF"] == 36
    assert result.quantities["DRV8300DRGER"] == 2
    assert result.quantities["PY32F030K28U6TR"] == 2
    assert result.quantities["INA190A3IDDFR"] == 2
    assert not result.errors


def test_pinmux_is_unique_and_covers_simultaneous_functions():
    result = validate_pinmux(ROOT / "hardware/pinmux.csv")
    required = {
        "PWM_U_H", "PWM_U_L", "PWM_V_H", "PWM_V_L", "PWM_W_H", "PWM_W_L",
        "BEMF_U", "BEMF_V", "BEMF_W", "CURRENT", "VBUS", "NTC_POWER",
        "THROTTLE_PWM", "SPI_SCLK", "SPI_MOSI", "SPI_MISO", "SPI_CS",
        "BREAK", "GATE_SUPPLY_FAULT", "SWDIO", "SWCLK", "NRST",
    }
    assert required <= result.functions
    assert not result.duplicate_pins
    assert not result.errors


def test_pinmux_validator_rejects_duplicate_physical_pin(tmp_path):
    path = tmp_path / "pinmux.csv"
    path.write_text(
        "function,pin,peripheral,af,mode,evidence\n"
        "PWM_U_H,PA8,TIM1_CH1,AF2,output,datasheet\n"
        "PWM_V_H,PA8,TIM1_CH2,AF2,output,datasheet\n",
        encoding="utf-8",
    )
    assert validate_pinmux(path).duplicate_pins == {"PA8"}


def test_bom_validator_rejects_price_without_capture_date(tmp_path):
    path = tmp_path / "bom.csv"
    path.write_text(
        "reference,quantity,manufacturer,mpn,distributor,distributor_part_number,unit_price_usd,extended_price_usd,price_captured,alternate_part,reason_selected,status\n"
        "Q1,1,Vendor,Part,LCSC,C1,1.0,1.0,,,reason,verified\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="price_captured"):
        validate_bom(path)

