"""BOM cost reporting that never treats blank prices as zero-cost parts."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CostSummary:
    priced_subtotal_usd: float
    priced_rows: int
    unpriced_rows: int


def summarize(path: Path) -> CostSummary:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    priced = [row for row in rows if row["extended_price_usd"].strip()]
    subtotal = sum(float(row["extended_price_usd"]) for row in priced)
    return CostSummary(round(subtotal, 4), len(priced), len(rows) - len(priced))


def report(path: Path) -> str:
    summary = summarize(path)
    return (
        "# BOM cost status\n\n"
        f"Priced significant-component subtotal: **${summary.priced_subtotal_usd:.2f}** "
        f"across {summary.priced_rows} rows.\n\n"
        f"Unpriced rows: **{summary.unpriced_rows}**. These are not counted as zero; "
        "therefore no final assembled-board cost is claimed. Pricing uses consumed "
        "quantity rather than full reel/tube purchase cost and excludes PCB, assembly, "
        "shipping, tax, CNC copper, wire, and rework.\n"
    )


if __name__ == "__main__":
    root = Path(__file__).parents[1]
    (root / "bom/cost-summary.md").write_text(report(root / "bom/edf-esc.csv"))
