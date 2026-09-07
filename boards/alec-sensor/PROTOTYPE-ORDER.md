# ALEC paired PCB prototype order

The immediate objective is to build and test the clock and sensor PCBs together. On 2026-09-07 the user reported a working breadboard and successful sensing through a plastic food container. This is useful feasibility evidence; exact material, thickness, firmware, load and test conditions were not recorded here. Testing of the custom PCB and final shower enclosure remains separate.

Enclosure development is paused at the current fit concept while the electronics are prepared for a small prototype order. Customer waterproofing, final appearance and long-term endurance do not need to be completed before ordering engineering test boards.

## Board set

| Product | Board | Layers | Role |
|---|---|---:|---|
| Clock | `alec-main` | 4 | ESP32, RTC, power and audio |
| Clock | `alec-controls` | 2 | Settings buttons and enable switch |
| Clock | `alec-front` | 2 | External button and RGB LED |
| Sensor | `alec-sensor` | 4 | ESP32, RTC, power, radar socket and controls |

Plan matching quantities for complete clock/sensor test sets. These are four PCB designs; generate and review separate fabrication/assembly packages. A combined purchasing/shipping plan does not imply one shared Gerber ZIP or panel. Final quantities and assembly services depend on the quote.

## Before submitting the PCB orders

- Freeze exact commits for all four designs and export matching Gerbers, drills, BOMs and placement files. Inspect the rendered fabrication output, board outline and both assembly sides.
- Confirm the fabricator's actual four-layer stackup, USB impedance assumptions and via process against the boards. The sensor's stored JLCPCB advanced-rule pass is a geometric check, not a stackup or assembly approval.
- Resolve ordering MPNs to available assembler parts and inspect rotations/pin 1. The sensor BOM currently contains prototype MPN candidates; the repository's JLCPCB exporter expects `LCSC#` fields, which are not a completed sourcing map. Exporting a CSV alone does not finish PCBA preparation.
- Confirm which through-hole connectors/switches and rear-side components will be assembled by the supplier versus locally. Include the radar socket, service buttons and power switch in the assembly review.
- Include the separate LD2410C, battery holders, mating battery plugs, clock harnesses, display and speaker needed to run complete systems. Use the [clock harness contract](../alec-main/HARNESS.md). These are not all represented in a bare-PCB or SMT assembly quote.

The C29 purchasing correction uses Murata GRM155R71C104KA88D (100 nF, 16 V, X7R, 0402) on the existing 0402 footprint. It replaces an erroneous 0603 MPN; electrical value, footprint and routing stay unchanged. [Manufacturer package specification](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM155R71C104KA88-01A.pdf). The BOM check compares 88 component MPNs with the schematic/PCB and checks all 27 selected capacitor package codes. Availability and full package/pin review remain open.

## What the first boards should establish

Start with accessible, dry bench assemblies: inspect soldering and polarity; bring up the power rails using a current-limited source; verify USB flashing, RTC, radar UART, signal isolation, controls and battery measurement. Then integrate the actual clock/sensor firmware and prove ESP-NOW communication, wake sequencing and complete alarm/dwell operation.

Measure active/sleep current, battery sag, converter startup/ringing and component temperatures on the real boards. Record cells, firmware and radar configuration. Use the results to choose the sensing schedule and guide the next enclosure iteration. Enclosure-material and wet tests follow with a protected test assembly; no current customer shower rating is claimed.

No order, quote submission or payment has been made. The files currently document a prototype-order plan and design checks, not an approved supplier assembly package.
