# CAD status

The checked-in CAD is a deterministic **placement and power-topology review
prototype**, not a fabrication release. It is deliberately marked
`UNVALIDATED` on the silkscreen and schematic.

## Verified automatically

- KiCad 7.0.11 parses the board and schematic and exports Gerber/PDF files.
- Outline is 98 mm x 58 mm with four copper layers.
- Every footprint is on the front side.
- There are exactly 36 `SFS06R025GF` positions and 36 individual 4.7 ohm gate
  resistors.
- Channel A and B have independent battery, phase, Kelvin, BEMF, and break nets.
- Source files regenerate byte-for-byte from `python -m edf_esc.cad`.

## Open fabrication blockers

- The centre section now uses package-structured QFN-24, QFN-32-EP, TSOT-23-8,
  SOIC-8, TO-220-5, and SOT-23 pads, but their courtyard, paste, thermal-via,
  assembly, and manufacturer land-pattern dimensions still require final review.
- The schematic is a functional-block review sheet, not the final connected
  electrical schematic.
- The latest local KiCad DRC after assigning the control-device pins reports 895
  violations and 157 unconnected pads. This is expected to rise as real nets
  replace stand-ins; it is not a regression to hide by suppressing checks.
- Copper-zone geometry, gate fan-out, creepage, silkscreen, thermal vias, and
  busbar interfaces need final routing review.
- ERC/DRC must reach reviewed zero-error status before manufacturing files are
  allowed into a release archive.

Do not order this revision. Generated plots are parser smoke-test artifacts only.
