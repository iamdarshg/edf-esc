from pathlib import Path

from edf_esc.bom import report, summarize


def test_unpriced_parts_are_not_silently_zero_cost():
    root = Path(__file__).parents[1]
    summary = summarize(root / "bom/edf-esc.csv")
    assert summary.priced_subtotal_usd == 27.3884
    assert summary.priced_rows == 6
    assert summary.unpriced_rows > 0


def test_checked_in_cost_report_matches_generator():
    root = Path(__file__).parents[1]
    expected = report(root / "bom/edf-esc.csv")
    assert (root / "bom/cost-summary.md").read_text() == expected
