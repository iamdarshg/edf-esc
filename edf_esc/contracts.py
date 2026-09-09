"""Machine-checkable BOM and MCU pin-mux contracts."""

from collections import Counter
from dataclasses import dataclass
import csv
from pathlib import Path


BOM_COLUMNS = {
    "reference", "quantity", "manufacturer", "mpn", "distributor",
    "distributor_part_number", "unit_price_usd", "extended_price_usd",
    "price_captured", "alternate_part", "reason_selected", "status",
}


@dataclass(frozen=True)
class BomValidation:
    quantities: Counter
    errors: tuple[str, ...]


@dataclass(frozen=True)
class PinmuxValidation:
    functions: set[str]
    duplicate_pins: set[str]
    errors: tuple[str, ...]


def validate_bom(path: Path) -> BomValidation:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = BOM_COLUMNS - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"missing BOM columns: {sorted(missing)}")
        quantities: Counter = Counter()
        errors: list[str] = []
        for line, row in enumerate(reader, start=2):
            quantity = int(row["quantity"])
            if quantity <= 0:
                errors.append(f"line {line}: quantity must be positive")
            quantities[row["mpn"]] += quantity
            if row["unit_price_usd"] and not row["price_captured"]:
                raise ValueError(f"line {line}: price_captured required with price")
            if row["unit_price_usd"]:
                expected = quantity * float(row["unit_price_usd"])
                if abs(expected - float(row["extended_price_usd"])) > 0.005:
                    errors.append(f"line {line}: extended price mismatch")
            if not row["reason_selected"]:
                errors.append(f"line {line}: selection reason is empty")
    return BomValidation(quantities=quantities, errors=tuple(errors))


def validate_pinmux(path: Path) -> PinmuxValidation:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    pins = [row["pin"] for row in rows]
    counts = Counter(pins)
    duplicates = {pin for pin, count in counts.items() if count > 1}
    errors = []
    for line, row in enumerate(rows, start=2):
        for key in ("function", "pin", "peripheral", "mode", "evidence"):
            if not row.get(key):
                errors.append(f"line {line}: {key} is empty")
    return PinmuxValidation(
        functions={row["function"] for row in rows},
        duplicate_pins=duplicates,
        errors=tuple(errors),
    )

