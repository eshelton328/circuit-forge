# v4.1 — 1.3-inch display update

2026-09-06. **Small bottom-panel revision; accepted v4 exterior and acoustic arrangement preserved.**

The selected prototype part is [EastRising ER-OLEDM013-1W-I2C](https://www.buydisplay.com/i2c-white-1-3-inch-oled-display-module-128x64-arduino-raspberry-pi): white 1.3-inch, 128×64, SH1106, four-pin I2C. The [manufacturer datasheet](https://www.buydisplay.com/download/manual/ER-OLEDM013-1_Datasheet.pdf) is saved in [sources](sources/ER-OLEDM013-1_Datasheet.pdf); page 6 is the I2C-only mechanical drawing, page 8 the pin table, page 9 the supply/current table. Page 7 and the supplier's seven-pin SPI/I2C CAD must not be substituted silently. Dimensions below are millimetres.

| Feature | v4 / DFR0486 | v4.1 / EastRising |
|---|---|---|
| Body | 105 × 105 × 105 | Same |
| Four grilles, front button and one lens | Accepted v4 | Same mesh positions and shapes |
| Main PCB, AA holder/cells, speaker/pod | Accepted v4 arrangement | Same mesh positions and shapes |
| Display PCB outline | 41.2 × 26.2 | 35.4 × 33.5 |
| Mounting centres | 35 × 20 | 30.4 × 28.5, Ø3 holes |
| Active image | 21.744 × 10.864 | 29.42 × 14.70 |
| Protected panel aperture | 24 × 13 | 31.8 × 17.1 |
| Display PCB centre XY | (−18, −31) | (−18, −29.5) |
| Display active centre XY | Previously provisional | (−18, −31.55), 2.05 toward header |
| Front UI board centre XY | (0, −47.8) | (0, −48.3), 0.5 closer to front wall |
| Main-board display connector | Four-pin 2.54 J4 | Same; new display-end cable geometry |
| Firmware controller | SSD1306 | SH1106 integration required |

The image is approximately **35% wider/taller and 83% larger in area**, at the same pixel count. The illustrative screen in the service render scales the same text accordingly; it is not running firmware.

## Mechanical implementation

The module faces down under the screwed bottom cover. Its four-pin header points inward (+Z), at the front edge (−Y). The PCB is at Z=8.6..9.8. The glass face is at Z=7.0, giving 1.0 mm separation from the back of the protected panel at Z=6.0. The drawing's 2.8±0.15 glass-front-to-PCB-back dimension, 1.2±0.15 PCB thickness and 1.45±0.1 glass thickness are represented nominally. Mount through the PCB holes; do not clamp the glass.

The active area sits 2.05 mm toward the header from the centre of the PCB. The new window follows that offset. Normal-view rays through the aperture clear the active-area corners with an additional 0.3 mm offset allowance. The module is recessed, so extreme-angle readability and actual tolerances still need a sample check.

Four short M2.5 support/screw allocations replace the old 35×20 pattern. Header spacer height is 2.5; exposed pins are 6.0±0.2 above it, at 2.54 pitch. The female socket is an explicitly unverified 11×3.5×7 allowance. The allocated cable rises and bends along the left-side corridor to J4. Back-side components are reserved up to 3 mm above the PCB; that height is a design allowance, not a manufacturer guarantee of every shipped component.

Nominal PCB-edge clearance is **1.25 mm to the front UI board**, **1.25 mm to the cell withdrawal corridor**, and **2.445 mm to the holder**. The first two leave only 0.25 mm after a 1 mm screening reserve. The front UI board has 1.0 mm nominal clearance to the inside front wall. These compact gaps need ordered-part and process tolerances before release; they are acceptable for continuing the packaging study, not a manufacturing sign-off.

No speaker-pod volume was traded for the display. No main PCB component, regulator, capacitor loop, antenna datum or battery position moved. The final saved-scene check compares the unchanged objects against the actual original v4 Blender file, including evaluated world-space geometry and topology.

## Electrical and BOM consequences

J4's pin nets are 1 GND, 2 switched OLED_3V3, 3 OLED_SCL, 4 OLED_SDA, matching the module's function order. A four-wire harness remains appropriate. Exact connector orientation and continuity must be verified before power is applied. The native main-board design is unchanged. The bottom-control/front-UI PCB work already required by v4 remains outstanding; this display does not create a new buck-boost placement requirement.

Use the SH1106 driver and test the actual I2C address, rotation, column mapping, power cycling, pull-ups and off-state leakage. At 3.3 V the supplier lists 40 mA typical / 45 mA maximum with all pixels lit, so retain display power gating and recheck startup/full-white load. See [PCB-INTERFACE.md](PCB-INTERFACE.md) for the exact mapping and integration checklist. No firmware, PCB layout, SPICE deck or electrical qualification was changed or claimed in this packaging revision.

The complete four-pin module is used for the next prototype. The cheaper bare ER-OLED013-3W remains a separate future production cost-reduction candidate: it would require its own footprint, support circuit, connection and mechanical review. This model does not silently assume that future integration is already done.

## Deliverables and limits

Open [the bottom service view](bottom-service.png), [assembled model](alec-cube-v4-1.blend), [service model](alec-cube-v4-1-service.blend), [gallery](index.html), or [test report](TEST-REPORT.md). The original accepted v4 scene is preserved in [reference/](reference/README.md). This complete v4.1 deliverable is tracked under `enclosures/alec/`.

Mechanical geometry checks are recorded in verification.json and bound to the saved model by SHA-256. Purchased-part fit, exact mating hardware, manufacturing tolerances, acoustics, RF, battery load/cooling, EMI and parasitics remain physical validation work. The new display electrical test has been added to the unrun test register; measured data has not been fabricated.
