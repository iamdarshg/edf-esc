# Manufacturing release directory

**No manufacturing release exists yet. Do not order the current CAD.**

`scripts/release.sh` is fail-closed: it first runs the source audit and stops on
placeholder footprints, unresolved sourcing, recorded CAD blockers, missing
validation documents, or policy violations. Only after those conditions are
cleared may it write Gerbers, Excellon drill, front-side CPL, BOM, schematic PDF,
and a SHA-256 manifest here.

The intended fabrication baseline is 98 × 58 mm, four layers, 1.6 mm FR-4, 2 oz
outer / 1 oz inner copper minimum subject to final impedance and thermal review,
ENIG, filled/tented thermal vias where called out, and top-side assembly only.
High-current testing additionally requires the approved CNC copper reinforcement
set and external star-split 8-AWG battery leads.
