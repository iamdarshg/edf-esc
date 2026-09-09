#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

.venv/bin/python scripts/check_release.py
make test
mkdir -p manufacturing/gerbers manufacturing/drill
kicad-cli pcb export gerbers -o manufacturing/gerbers/ hardware/edf-esc.kicad_pcb
kicad-cli pcb export drill -o manufacturing/drill/edf-esc.drl hardware/edf-esc.kicad_pcb
kicad-cli pcb export pos --format csv --units mm --side front \
  -o manufacturing/edf-esc-cpl.csv hardware/edf-esc.kicad_pcb
kicad-cli sch export pdf -o manufacturing/edf-esc-schematic.pdf hardware/edf-esc.kicad_sch
cp bom/edf-esc.csv manufacturing/edf-esc-bom.csv
find manufacturing -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > manufacturing/SHA256SUMS
