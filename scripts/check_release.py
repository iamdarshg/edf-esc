#!/usr/bin/env python3
"""Audit repository completeness and refuse unsafe manufacturing releases."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

MANDATORY = (
    "hardware/edf-esc.kicad_pro",
    "hardware/edf-esc.kicad_sch",
    "hardware/edf-esc.kicad_pcb",
    "bom/edf-esc.csv",
    "hardware/pinmux.csv",
    "calculations/report.md",
    "docs/bring-up.md",
    "docs/calibration.md",
    "docs/thermal-characterization.md",
    "validation/ledger.csv",
)


def audit(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in MANDATORY:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    board_path = root / "hardware/edf-esc.kicad_pcb"
    if board_path.is_file():
        board = board_path.read_text()
        if "PLACEHOLDER_" in board:
            errors.append("PCB contains placeholder footprints")
        if "UNVALIDATED" in board:
            errors.append("PCB is explicitly marked UNVALIDATED")
        if board.count('(footprint "EDF_ESC:PDFN56"') != 36:
            errors.append("PCB does not contain exactly 36 MOSFET footprints")
        if '(gr_rect (start 0 0) (end 98 58)' not in board:
            errors.append("PCB outline is not the frozen 98 x 58 mm rectangle")
        tail = board.split("(footprint", 1)[-1]
        if re.search(r'\(layer "B\.(?:Cu|SilkS|Fab|Mask)"\)', tail):
            errors.append("PCB contains a bottom-side footprint item")

    bom_path = root / "bom/edf-esc.csv"
    if bom_path.is_file():
        with bom_path.open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        unresolved = sum("validation_required" in row.get("status", "") for row in rows)
        if unresolved:
            errors.append(f"BOM has {unresolved} validation-required sourcing rows")

    status_path = root / "docs/cad-status.md"
    if status_path.is_file() and "Open fabrication blockers" in status_path.read_text():
        errors.append("CAD status explicitly records open fabrication blockers")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--allow-prototype", action="store_true")
    args = parser.parse_args()
    errors = audit(args.root.resolve())
    if errors:
        print("RELEASE BLOCKED")
        for error in errors:
            print(f"- {error}")
        return 0 if args.allow_prototype else 1
    print("release source audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
