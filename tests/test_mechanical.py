import csv
from pathlib import Path

from edf_esc.mechanical import BARS, build_dxf


def test_reinforcement_quantities_cover_two_channels():
    quantities = {bar.name: bar.quantity for bar in BARS}
    assert quantities == {"BAT_RAIL": 4, "PHASE_RAIL": 6}
    assert all(bar.thickness_mm in (1.0, 2.0) for bar in BARS)
    assert all(bar.length_mm <= 98 and bar.width_mm <= 58 for bar in BARS)


def test_checked_in_dxf_and_csv_match_contract():
    root = Path(__file__).parents[1]
    assert (root / "hardware/mechanical/reinforcement.dxf").read_text() == build_dxf()
    with (root / "hardware/mechanical/reinforcement.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert sum(int(row["quantity"]) for row in rows) == 10
    assert {row["status"] for row in rows} == {"preliminary"}
