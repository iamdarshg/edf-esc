# Controlled engineering sources

Only manufacturer documents can close an electrical or pin-mux gate. Distributor pages support stock, price, and ordering identity but not design limits.

| Component | Controlled source | Facts used | Status |
|---|---|---|---|
| TI DRV8300 | https://www.ti.com/lit/ds/symlink/drv8300.pdf, Rev. D (March 2022), SHA-256 `bb467652a531335d23ea67644db1db26ce53f149e3f889f8158a1c3ddac3e4db` | 5-20 V GVDD, 750 mA source, 1.5 A sink, QFN variable deadtime, integrated bootstrap diode on D variant, pinout/layout | verified from manufacturer PDF |
| TI INA190 | https://www.ti.com/lit/ds/symlink/ina190.pdf, Rev. D, SHA-256 `6ed9c2cc41d6c5ba4f36ce33d9d829b2f0c51e376583e94e2c63be4d950b39af` | common-mode range, gain option, supply/ADC interface, layout | verified from manufacturer PDF |
| PUYA PY32F030 | LCSC manufacturer PDF mirror, Datasheet Rev1.3, SHA-256 `38262b8a2c8320567f7f80594d4e9558cd0721edacbe360e37839284c0d04a4f` | exact QFN-32 K2 pins, alternate functions and ADC channels | pin map verified; comparator internal routing still requires reference-manual evidence |
| Oriental Semiconductor SFS06R025GF | Manufacturer PDF V1.0, SHA-256 `6a947af2537023168338109af4bddd3e03c0364027fd04a3ce05bfe177fd5f03` | 60 V, 2.5 mOhm maximum at 10 V, 81 nC Qg, 16 nC Qgd, PDFN 5x6 pinout | verified from manufacturer PDF; thermal assumptions remain a physical validation gate |
| XLSEMI XL4016E1 | Manufacturer datasheet, 8 A/180 kHz/40 V family | reference circuit, feedback, inductor, diode, capacitors, thermal limits | secondary mirror located; manufacturer PDF must be archived |
| XLSEMI/UMW XL1509 | Manufacturer datasheet for exact ordered variant | 12 V buck reference circuit and magnetics | validation gate before schematic release |
| XC6206P332MR | Torex manufacturer datasheet | pinout, 3.3 V regulation, capacitor stability, current/thermal limits | validation gate before schematic release |

## Distributor capture

LCSC product pages were captured on 2026-09-09 for ordering identity, prototype
price, and stock only: C49005839 (259), C3655801 (11,428), C3018718 (18,245),
C1852076 (8,100), C55881 (26,710), and C2681227 (13,060). Distributor values do
not override the electrical limits above. Prices in `bom/edf-esc.csv` use the
lowest applicable quantity tier for one board, including LCSC minimum-order
tiers where relevant.
