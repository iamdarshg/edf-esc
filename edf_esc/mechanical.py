"""Deterministic preliminary CNC copper reinforcement profiles."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Bar:
    name: str
    length_mm: float
    width_mm: float
    thickness_mm: float
    quantity: int


BARS = (
    Bar("BAT_RAIL", 32.0, 4.0, 1.0, 4),
    Bar("PHASE_RAIL", 30.0, 4.0, 1.0, 6),
)


def build_dxf() -> str:
    lines = ["0", "SECTION", "2", "ENTITIES"]
    x = 0.0
    for bar in BARS:
        for index in range(bar.quantity):
            y = index * (bar.width_mm + 3.0)
            points = ((x, y), (x + bar.length_mm, y),
                      (x + bar.length_mm, y + bar.width_mm), (x, y + bar.width_mm))
            for start, end in zip(points, points[1:] + points[:1]):
                lines.extend([
                    "0", "LINE", "8", bar.name,
                    "10", f"{start[0]:.3f}", "20", f"{start[1]:.3f}", "30", "0.000",
                    "11", f"{end[0]:.3f}", "21", f"{end[1]:.3f}", "31", "0.000",
                ])
        x += bar.length_mm + 10.0
    lines.extend(["0", "ENDSEC", "0", "EOF"])
    return "\n".join(lines) + "\n"


def write_mechanical(root: Path) -> None:
    target = root / "hardware/mechanical/reinforcement.dxf"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_dxf())


if __name__ == "__main__":
    write_mechanical(Path(__file__).parents[1])
