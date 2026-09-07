# ALEC Sensor — S0 schematic study

The battery-powered shower companion for the ALEC bedside alarm. It observes a configured presence zone and reports a timed dwell to the alarm over ESP-NOW. This is an initial electrical design and enclosure brief, **not a routed PCB, waterproof product or manufacturing release**.

- [Three-sheet schematic PDF](docs/schematic.pdf)
- [Editable KiCad schematic](alec-sensor.kicad_sch) and [project](alec-sensor.kicad_pro)
- [Enclosure direction](ENCLOSURE.md) and [concept drawing](docs/enclosure-concept.svg)
- [Power and firmware behavior](OPERATION.md)
- [Verification report and physical test plan](TEST-REPORT.md)
- [Source register](SOURCES.md)

![Sensor circuitry](docs/alec-sensor.svg)

![Switched radar interface](docs/alec-sensor-Radar%20interface.svg)

## What is included

| Function | S0 implementation |
|---|---|
| Processor | ESP32-S3-WROOM-1-N16, matching the ALEC family |
| Power | Two TPS63070 converters: 3.31 V MCU/RTC and 4.985 V switched radar supply |
| Presence | Internal LD2410C connection; 5 V power, 3.3 V UART and OUT |
| Sleep isolation | TMUX1511PWR opens UART TX, UART RX and OUT; external pull-down defaults it OFF |
| Clock | RV-3028-C7, same as ALEC; interrupt wired for deep-sleep wake |
| User interface | One common-anode RGB LED; one battery/pair button |
| Flashing | Native USB-C data path, ESD protection, BOOT and RESET |
| Batteries | Three series AA primary cells, reverse-polarity protection and switched measurement |
| Power switch | Hard battery disconnect; exact switch, current protection and package remain to be selected |

The USB connection retains ALEC's **data-only power arrangement**. Batteries and the power switch must supply the board while flashing. There is no charger or path from USB VBUS into the AA pack. USB, BOOT/RESET and the power switch belong inside the dry service compartment.

The draft removes the audio amplifier, display circuit, three unused user switches and always-on power LED. It reuses the reviewed converter topology and monitoring circuit, but no old PCB layout or physical test result qualifies a future sensor board.

## Pin contract

GPIO numbers below are ESP32 signal numbers, not physical module pad numbers.

| Function | GPIO | Notes |
|---|---:|---|
| USB D− / D+ | 19 / 20 | Native flashing interface |
| Radar UART TX / RX | 17 / 18 | ESP TX → radar RX; radar TX → ESP RX, through U10 |
| Radar OUT | 4 | RTC-capable wake input through U10; not sufficient evidence to stop the alarm |
| Radar 5 V enable | 16 | Moved away from the original board's GPIO18 assignment; reset default OFF |
| Radar signal isolation enable | 11 | HIGH closes three signal switches; reset default OFF |
| Radar / MCU rail power-good | 13 / 15 | Pulled up to MCU 3.3 V |
| RTC SDA / SCL | 8 / 9 | Independent I²C bus |
| RTC interrupt | 1 | Active LOW, external pull-up |
| Battery / pair button | 10 | Active LOW, external pull-up and debounce capacitor |
| RGB R / G / B | 38 / 39 / 40 | Active LOW, current-limiting resistors retained |
| Battery ADC / measurement enable | 2 / 12 | Switched divider, calibrate under load |
| USB present | 7 | Isolated transistor sensing from existing power-monitor sheet |

**There is no inherent conflict between the RTC, radar UART and USB.** The S0 change that matters is moving the radar converter enable off GPIO18 before assigning that pin as UART RX.

## Stage and reproducibility

This lives under `designs/` because existing `boards/` automation requires an actual PCB, schematic parity, copper connectivity and fabrication checks. An independent workflow exports a fresh netlist, runs ERC and checks the sensor interface. It does not bypass or relax any existing board checks. Promote this to `boards/alec-sensor` when a real layout exists.

Using free tools, from the repository root:

```sh
python3 designs/alec-sensor/tools/create_schematic.py
kicad-cli sch erc --exit-code-violations --format json -o designs/alec-sensor/review/erc.json designs/alec-sensor/alec-sensor.kicad_sch
kicad-cli sch export netlist --format kicadxml -o designs/alec-sensor/review/netlist.xml designs/alec-sensor/alec-sensor.kicad_sch
python3 designs/alec-sensor/tools/check_design.py
python3 designs/alec-sensor/tools/power_budget.py
python3 -m pytest tests/test_alec_sensor_study.py
kicad-cli sch export pdf -o designs/alec-sensor/docs/schematic.pdf designs/alec-sensor/alec-sensor.kicad_sch
kicad-cli sch export svg -o designs/alec-sensor/docs/ designs/alec-sensor/alec-sensor.kicad_sch
```

The generator derives selected blocks from `esp32s3-devkit-5v`; editing that source can change a regeneration. Review regenerated netlists and assets. The committed native schematic is the checked design. Several new mechanical and capacitor MPNs intentionally remain `TBD`; this package cannot produce an order-ready BOM.
