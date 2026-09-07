# ALEC — v4.1 design review

2026-09-06. **A revised packaging prototype, not a manufacturing release.** Bedside unit; the shower sensor is a separate product. This revision retains the accepted v4 product/acoustic design and substitutes the EastRising 1.3-inch I2C OLED. See [DISPLAY-UPDATE.md](DISPLAY-UPDATE.md) for the small mechanical changes. The broader product decisions below were made in v4 and are preserved.

Open [the gallery](index.html), [assembled Blender model](alec-cube-v4-1.blend), [acoustic cutaway](alec-cube-v4-1-acoustic-cutaway.blend), [bottom service model](alec-cube-v4-1-service.blend), or [dimensioned drawing](dimensioned-layout.svg). See the [test report](TEST-REPORT.md) for what was actually checked.

## Decisions

| Critique | v4.1 response | Remaining limitation |
|---|---|---|
| The reflector and long sound paths were speculative | Front-facing FRS 5 X, immediately behind the front grille; separate closed rear pod; no reflector, tuned port or side duct | Frequency response, loudness and cloth/grille loss require a physical comparison |
| Long control extensions were driving the enclosure | Three direct Omron B3F-1060 actuators and a direct E-Switch EG1218 on a small bottom PCB | New PCB is an allocation; switch wells, board mounts and harness need detail design |
| The bottom looked like exposed electronics | Protected setup face with display window, labeled controls and separate battery opening | Drawing-based display window updated; connector, tolerances and finger access require samples |
| Cells could fall out during setup | Downward-facing holder with a screw-retained bridge and pull ribbon | Retention force, bridge stiffness and captive hardware remain unqualified |
| The exterior resembled an industrial mini-PC | Rounded continuous shell, fewer visible joints, matching grille fields, cloth hiding internals, one small battery-check button and one dark lens | Cloth and nonconductive enclosure materials not selected |
| 110 mm cube lacked justification | 105 × 105 × 105 mm body: 13.0% less body volume than v3; 15.8% larger than the original 100 mm aspiration | No additional shrinking until the acoustic and measured-part checks pass |
| Readiness was unclear | Explicit battery/readiness interactions and fault-state contract | Proposed behavior; not implemented firmware |

## Acoustic architecture

Place the **button/front face toward the sleeping position**. The driver radiates through that face. All four side walls are physically perforated, as requested, but this design does **not** promise equal sound from all four sides. The side/rear grilles are part of the enclosure appearance and ventilation; the speaker's rear wave stays inside its own pod. If equal four-direction output becomes a requirement, it needs a separately tested acoustic design.

Visaton's installation guidance calls for separation of front and rear radiation, adequate grille opening area, a short grille-to-driver distance without excursion contact, and a well-sealed enclosure. Those principles motivate the direct radiator and closed pod. They do not establish the performance of this particular enclosure. [Manufacturer installation guide, pages 1–5](https://www.visaton.de/sites/default/files/downloads/Visaton_Basics-of-speaker-installation_2025-05_V1_1.pdf).

The clear rectangular rear space is **81.2 × 48.4 × 50.4 mm = 0.1981 L before driver, bosses, wiring, sealant or damping displacement**. This is gross space, not usable acoustic volume. The simplified solid driver geometry occupies roughly 0.05 L of this region; that is only a packaging estimate. Net volume must be measured or recalculated from complete driver geometry. This remains a small enclosure; v4.1 does not establish improved bass or fidelity. Compare a larger sealed test box if the response sounds thin or resonant before accepting 105 mm.

Each grille has 418 genuine openings on a 4 mm pitch, nominal Ø3.2, thickness 1.2. Ideal circular opening area is 50.3%; the 16-sided modeled holes yield about 48.8%. The allocated cloth adds unknown acoustic resistance. It must be nonconductive, held taut and kept out of the diaphragm envelope. The nearest rigid grille is **2.8 mm** from the conservative maximum forward cone envelope; the allocated cloth is **2.45 mm** away. These are nominal geometric gaps, not allowances for measured fabric sag, assembly error or driver variation.

The rear pod has blind fixing bosses and a proposed sealed two-wire feedthrough. It has no intentional bass-reflex opening. The cutaway intentionally hides one wall and the roof; the assembled file includes them. Leakage, screw seating and wall vibration still need physical tests.

## Parts and dimensional evidence

| Part | Geometry used | Confidence boundary |
|---|---|---|
| [Visaton FRS 5 X, 8 Ω](https://www.visaton.de/en/products/drivers/fullrange-systems/frs-5-x-8-ohm) | Ø52.5 body, 68 lug span, 60 mounting centres, Ø4.2 holes, 33.5 rear projection, 1.5 flange allowance, Ø45 magnet, Ø46 cutout | [Drawing](https://www.visaton.de/sites/default/files/dd_product/frs5x_tz.gif). Basket shape, axial magnet split and terminal position simplified |
| [MPD BH3AAW](https://www.batteryholders.com/part.php?original=AA&override=AA&pn=BH3AAW) | Manufacturer STEP body: 57.15 × 46.61; full CAD height 17.39 | Long straight lead overhang trimmed and rerouted separately; contact compression, actual cells and harness still need testing |
| [EastRising ER-OLEDM013-1W-I2C](https://www.buydisplay.com/i2c-white-1-3-inch-oled-display-module-128x64-arduino-raspberry-pi) | 35.4 × 33.5 × 1.2 PCB; 30.4 × 28.5 mounting centres; 29.42 × 14.70 active area; 2.8 mm glass-front-to-PCB-back stack | [Local manufacturer datasheet](sources/ER-OLEDM013-1_Datasheet.pdf), pp. 6/8/9. Four-pin I2C variant. Exact back-side components, mated socket, cable and production tolerance stack remain unverified |
| [Omron B3F-1060](https://components.omron.com/sites/default/files/datasheet_pdf/A070-E1.pdf) | 6 × 6 body, 7.0 mm overall actuator height, 0.25 mm nominal pretravel | Stock direct actuator; simplified leads. Aperture Ø10 and short finger well need hand testing. No separate actuator-extension rod |
| [E-Switch EG1218](https://www.e-switch.com/product/eg-series-subminiature-slide-switch/?part-number=EG1218) | [Manufacturer drawing](https://configured-product-images.s3.amazonaws.com/2D/specs/EG1218.pdf): 11.6 × 4 body, 5.4 body height, 2 mm actuator, 4.7 terminal projection | Used for a low-current enable signal. Its 200 mA contact rating is not a basis for switching the alarm's battery load |
| Existing main PCB | Actual KiCad GLB; 64 × 56 × 1.6 native board, actual asymmetric holes and component placements | Generic package models are not ordered-part maximum envelopes |
| Shell, cloth, feet, screws, inserts, ribbon, seal and lenses | Explicit custom geometry or tagged allocation | Exact purchased variants, tolerances, durability and manufacturing process remain open |

Manufacturer documents, the original holder STEP and source GLBs are committed in [sources/](sources/README.md). Sources and their provenance are hashed in `sources/source-manifest.json` and `source-manifest.json`. The original accepted v4 Blender scene is retained in [reference/](reference/README.md) for the geometry comparison.

## PCB and assembly consequences

The main board stays **flat, component-side down**, with its local mounting datum at Z=44 mm. Keeping this orientation leaves the speaker pod above it and keeps the current vertical connector mating envelopes below it. The new bottom control board removes the need to reach the main-board switches with long rods. The main PCB is preserved as a real fit reference; this model does not secretly relocate individual components.

**The already-planned product PCB revision is still required**, chiefly for the external control connections and service layout. Read [PCB-INTERFACE.md](PCB-INTERFACE.md). There is no new routed main PCB, electrically functional daughterboard or updated SPICE model in this enclosure revision. The two existing buck-boost layouts and corrected local capacitor connections have not been changed.

The current USB connector cannot accept a normal straight cable while the shell is assembled. Development service is specified by removal of the internal chassis. The narrow connector corridor is deliberately not called a pass. A detailed chassis release mechanism, service loop and final USB arrangement are still required before printing a complete functional assembly. Ordinary battery replacement and settings access do not require USB.

The 15 mm conservative antenna study volume is free of the modeled foreign parts. This is a geometric reserve around the antenna-end model, not a field simulation. Use a nonconductive shell, fabric and finish; validate ESP-NOW with the loaded holder, speaker magnet, closed cover and real shower location. [Espressif module placement guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html).

## Daily use and fault behavior — proposed contract

The outer screw-fastened cover hides setup and power controls. Its four screws have a retainer allocation; exact captive hardware and grooves remain to be designed. Removing it exposes the setup panel, not the main board. The cell bridge remains in place while changing settings; release it only for battery replacement. Mark cell polarity clearly after confirming the actual holder wiring.

The lens stays dark in the normal night state. A short check-button press reports battery reserve using a brief documented pulse count; a two-second hold requests readiness. Readiness can show green only when the schedule is armed, time is valid, the sensor check succeeds and the measured battery reserve is adequate. A failed check gives amber/red and a specific explanation on the bottom OLED. Battery thresholds must come from the chosen chemistry and loaded-voltage testing, not an invented percentage-to-voltage mapping.

While the alarm is sounding, the exterior button cannot snooze, disarm or erase settings. Only a valid shower-sensor session with the required continuous dwell completes the alarm. Packet loss must not count as presence; missing ACKs must not silence it. If the radio fails, preserve the sounding state and show a fault; deliberate service override remains under the screwed cover. Do not present READY based on the current breadboard sketch until these behaviors are implemented and tested. The earlier sketch's first-presence and ACK-timeout stop paths need correction in that firmware work.

## What I would build next

First compare the **same speaker in the direct sealed pod with and without grille/cloth**, plus the older reflector arrangement if a prototype exists. Keep the same amplifier, level, recording chain and positions. Include a larger sealed test volume if the small pod shows a resonance or poor clarity. Choose the enclosure based on those measurements and listening checks, then freeze the real component heights and route the control/main-board revision. This design pass supplies the assembly and a reproducible test plan; it does not substitute for those measurements.
