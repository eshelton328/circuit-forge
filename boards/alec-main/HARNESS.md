# Harness and programming contract

Both remote cables use [JST GH](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf) headers with positive latches, GHR housings and SSHL-002T-P0.2 crimp contacts. Use AWG28 stranded insulated conductors within the manufacturer's contact/insulation ranges, a maximum 200 mm wire length, strain relief, and pin-1-to-pin-1 continuity at both ends. A keyed connector does not validate a cable's crimp order. Measure continuity and shorts before applying batteries.

## Bottom controls: main J5 ↔ controls J1

Headers: BM07B-GHS-TBT; cable housings: two GHR-07V-S.

| Pin | Signal | Destination/function |
|---|---|---|
| 1 | GND | Button returns and OFF throw |
| 2 | BTN_VOL_MINUS | R50 100 Ω → GPIO4; lower panel button SW1 |
| 3 | BTN_MODE | R51 100 Ω → GPIO5; middle SW2 |
| 4 | BTN_VOL_PLUS | R52 100 Ω → GPIO6; upper SW3 |
| 5 | GND | Additional return conductor |
| 6 | SW_ON | Protected battery through R31 10 kΩ; EG1218 pin 1 |
| 7 | EN_3V3 | EG1218 common pin 2; U1 enable and R32 100 kΩ pulldown |

EG1218 pin 3 is GND. Sliding toward the panel's ON label connects common to pin 1. The switch carries enable current, not amplifier current. OFF and an unplugged cable hold EN low; protected battery still reaches the regulator VIN pins. Measure standby drain with the real batteries. Firmware should allow at least 10 ms debounce; the RC circuit alone does not reject every possible contact bounce.

## Front: main J6 ↔ front J1

Headers: BM06B-GHS-TBT; cable housings: two GHR-06V-S.

| Pin | Signal | Destination/function |
|---|---|---|
| 1 | GND | B3U switch return |
| 2 | 3v3 | Wuerth 150141M173100 common anode, LED pin 1 |
| 3 | BTN_BAT | R53 100 Ω → GPIO10; exterior battery-check button |
| 4 | LED_R_K | LED pin 3 through main R28 330 Ω |
| 5 | LED_G_K | LED pin 4 through main R29 150 Ω |
| 6 | LED_B_K | LED pin 2 through main R30 150 Ω |

RGB channels remain active LOW on GPIO38/39/40. No LED resistors are omitted: they remain on the main board. The remote switch is [Omron B3U-1000P](https://components.omron.com/eu-en/products/switches/B3U); its 1.6 mm operating height matters to the cap linkage, rather than the 1.2 mm body headline dimension. Switch force, pretravel and printed cap travel require a physical tolerance check.

## UART service pads J7

Two columns, 2 mm pitch, Ø1 mm pads; no paste or populated connector. Coordinates below are in the enclosure's assembly coordinate system, not a bottom-view photograph.

| Pin | Signal | Assembly X,Y (mm) |
|---|---|---|
| 1 | GND | 7, −23 |
| 2 | Target 3v3 reference | 5, −23 |
| 3 | ESP32 TXD0 / GPIO43 | 7, −25 |
| 4 | ESP32 RXD0 / GPIO44 | 5, −25 |
| 5 | ESP32 EN / reset | 7, −27 |
| 6 | GPIO0 / boot | 5, −27 |

Use a battery-powered target and 3.3 V UART logic. Cross TX/RX at the programming adapter; connect grounds. The 3v3 pad is for voltage sensing, **not external target power**. A fixture may pull GPIO0 and EN low to enter the bootloader; it must release them and must not force 5 V onto any pad. There is no on-board USB-to-UART bridge or automatic RTS/DTR circuit. The allocated probe corridor is 8 × 10 mm through a 10 × 12 mm panel opening. Fixture alignment and retention remain to be designed and verified.

## Existing interfaces

J4/display pin order remains GND, switched OLED_3V3, OLED_SCL, OLED_SDA. Use the selected four-pin EastRising ER-OLEDM013-1W-I2C with an SH1106 driver and the established power/bus-isolation sequencing. The seven-pin or bare-glass variants are not substitutes. J1 remains the battery PH pair. J3 remains the BTL speaker pair: neither conductor is ground. Preserve paired speaker wiring and the sealed acoustic feedthrough.
