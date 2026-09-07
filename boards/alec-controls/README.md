# ALEC controls PCB

27 × 34 mm bottom settings board with three Omron B3F-1060 switches and an E-Switch EG1218 enable switch. Two copper layers, 1.6 mm thickness. J1 faces inward on B.Cu. These are actual routed boards fitted to the [v4.2 enclosure](../../enclosures/alec/pcb-revision/README.md), with physical tolerance/assembly verification still pending.

![Component side](review/pcb-top.png)

[Connector side](review/pcb-bottom.png) · [Schematic PDF](review/schematic.pdf) · [Native schematic](alec-controls.kicad_sch) · [Native PCB](alec-controls.kicad_pcb) · [BOM](review/bom.csv)

See the [harness contract](../alec-main/HARNESS.md) and [test report](../alec-main/review/TEST-REPORT.md). Pullups, debounce capacitors, 100 Ω button series resistors and RGB resistors live on the main board. Do not connect this board directly to an unprotected ESP32 input in place of the defined main-board interface.

<!-- board-images-start -->
## Board Images

_Auto-generated on merge to main._

### Schematic

![Schematic](docs/schematic.svg)

[Download schematic PDF](docs/schematic.pdf)

### PCB 3D Views

| Top | Bottom |
| :---: | :---: |
| ![Top](docs/pcb-top.png) | ![Bottom](docs/pcb-bottom.png) |

[Download populated 3D model (GLB)](docs/assembly.glb) — open in Blender or a glTF viewer.

<!-- board-images-end -->
