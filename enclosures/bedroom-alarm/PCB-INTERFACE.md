# PCB interface and placement contract — v4.1 proposal

This is a mechanical/electrical interface brief, **not a completed schematic or routed PCB**. The actual native board is unchanged; its hash is in `dimensions.json` and checked by `verify_assembly.py`.

## Preserve

- Flat main board and actual mounting pattern: KiCad H1=(104,74), H2=(160,74), H3=(104,113), H4=(160,115). Assembly XY: (28,24), (-28,24), (28,-15), (-28,-17).
- Antenna-end keepout in assembly coordinates: X=-25..23, Y=12.75..49.25, Z=26.405..57.405. Recompute if board position, module or antenna changes.
- Local TPS63070 capacitor connections and current loops. Do not move the regulators or lengthen those loops to accommodate controls.
- 3 AA battery protection, 5 V amplifier supply, switched display supply, existing audio topology and ESP-NOW function, subject to the existing outstanding electrical qualification.

## New bottom control board

Allocation: **27 × 34 × 1.6 mm**, centred at assembly (26.5,-30,13.6); switch-side mounting surface Z=12.8. Three B3F-1060 switches at (20,-43), (20,-31), (20,-19). EG1218 enable switch centre (36,-29). Four proposed Ø2.2 mounting holes are at (15.5,-37), (15.5,-25), (38,-43), (38,-16); check copper clearances and exact M2 hardware before routing. These coordinates are enclosure coordinates, not a KiCad placement file.

Bring the existing VOL+/MODE/VOL- functions to a keyed low-speed connector with ground. Map each signal from the schematic/netlist, including debounce and ESD considerations; do not select new ESP32 GPIOs casually. Existing main-board buttons may remain for development but no longer define the mechanical controls. Final connector MPN, pin count and pin order are unresolved and must be added to the schematic before any harness is built.

The EG1218 controls a low-current hardware enable/standby function. It must not carry speaker/amplifier battery current. Resolve the relationship with SW1 so the two cannot produce ambiguous states. A true battery-disconnect requirement would need a separately rated switch or power-path solution; “OFF” in this proposal is standby, with quiescent drain to measure and document.

## Front check board

Allocation: 24 × 10 × 1.6 mm, vertical behind the front lower band; centre (0,-48.3,12), moved 0.5 mm toward the front from v4 without moving the exterior cap/lens. Bring battery-check input and the one RGB indicator's required signals from the main board via a keyed connector. Specify drive/current limiting and LED behavior from the real circuit. No invented copper or connector pins are shown in the model. The amber harnesses end at a **proposed connector zone**, not at functioning connector pads on the existing board.

## Display and existing harnesses

Current J4 is a four-position 2.54 mm header. The selected **EastRising ER-OLEDM013-1W-I2C** uses a four-position 2.54 mm header. The native KiCad board pad nets and EastRising datasheet p8 agree on the functional order:

| J4 pin / net | Display pin / signal |
|---|---|
| 1 / GND | 1 / GND |
| 2 / OLED_3V3, switched | 2 / VCC |
| 3 / OLED_SCL | 3 / SCL |
| 4 / OLED_SDA | 4 / SDA |

Matching pitch/order does not establish cable plug orientation, wire order or keyed mating. Select the exact female-to-female harness, verify continuity with power removed, and check the shipped board labels. Do not use the seven-pin ER-OLEDM013-1W-SPI-I2C or the bare ER-OLED013-3W as a drop-in substitute. No connector footprint or buck-boost relocation is required solely for this display selection, subject to the current/rail checks below.

The module operates from 3.0–5.0 V, 3.3 V typical; use the existing switched 3.3 V rail, not a new 5 V signal interface. Datasheet p9 lists 40 mA typical/45 mA maximum for all pixels lit at 3.3 V, and up to 1 mA sleep current. Preserve actual power gating while the display is unused; software sleep alone is not a sufficient battery-life assumption.

This module needs the **SH1106** controller driver; the prior SSD1306 constructor is not validated for it. Firmware is not edited in this mechanical revision. Select the appropriate U8g2 SH1106 128×64 hardware-I2C constructor during integration; verify the actual address and rotation, initialize after every power cycle, then exercise a one-pixel perimeter/checkerboard to reveal column offsets/clipping. A matching 128×64 resolution does not mean an unchanged SSD1306 initializer works.

Retain display power/bus sequencing: power, settle, connect I2C; disconnect I2C before removing power. R37/R38 on the actual board are 4.7 kΩ pull-ups to OLED_3V3. Inspect the module's own pull-ups, calculate the effective value, measure rise times and check off-state leakage/back-power. Bench-test 100 switched-power cycles, full-white current, start transients and correct image orientation. These tests are pending, not passed by the geometry checks.

J1 is the battery PH pair; J3 is the differential/BTL speaker pair. Neither speaker lead is ground. Route speaker conductors together, away from antenna and low-level signals, with a sealed pod feedthrough and strain relief. All connector mating envelopes in this model are allocations pending exact parts.

## Release gates for the board revision

Resolve exact component envelopes, mechanical access and connector orientation before routing. Run ERC/DRC and the relevant existing electrical regressions after schematic/layout changes. Re-export the actual revised board into this assembly and rerun geometry checks. Then measure continuous-alarm battery sag, rail behavior, switching transients, radio performance and temperature in the closed enclosure. The v4.1 geometry check is not evidence that these electrical tests have passed.
