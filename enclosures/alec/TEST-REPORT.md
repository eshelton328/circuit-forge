# v4.1 test report

2026-09-06. **55/55 nominal geometry checks passed. Physical qualification: NOT PERFORMED. Manufacturing release: NO.**

The tested artifact is the saved `alec-cube-v4-1.blend`, reopened independently by `verify_assembly.py` under Blender 5.2.1 LTS. The native main PCB was not changed; SHA-256: `0e17f9ad0cf0508d8a53ed51c0b1e6af4423311598bbb03fe811c556e8b1e7d8`. This is the v4.1 EastRising 1.3-inch display update to the preserved v4 enclosure. There is no new PCB-layout simulation or SPICE result in this revision.

## Display change and preserved layout

See [DISPLAY-UPDATE.md](DISPLAY-UPDATE.md) for the drawing datums, old/new comparison, electrical pin mapping and remaining checks. The four-pin EastRising ER-OLEDM013-1W-I2C module is modeled from manufacturer drawing page 6 and pin table page 8. It is not the seven-pin SPI/I2C version or the bare production OLED panel.

- OLED PCB: 35.4 × 33.5 × 1.2 mm. Mounting: 30.4 × 28.5 mm centres, Ø3 holes.
- Active area: 29.42 × 14.70 mm, offset 2.05 mm toward the header from PCB centre. Glass front Z=7.0; PCB rear Z=9.8, implementing the 2.8 mm nominal stack in the drawing.
- Display moved +1.5 mm in Y. Only the proposed front UI board and its cable start moved −0.5 mm in Y; the exterior button/lens stayed fixed. Bottom window is now 31.8 × 17.1 mm.
- Nominal OLED-PCB gaps: 1.25 mm to the front UI PCB, 1.25 mm to the withdrawal corridor, 2.445 mm to the holder. The two 1.25 mm gaps leave 0.25 mm after a 1 mm screening reserve. This is tight packaging, not a complete production tolerance stack.
- The unverified female mating socket is allocated 11 × 3.5 × 7 mm, with cable bend space above it. A 3 mm rear-component allowance is checked separately. Exact shipped back-side components and mating hardware still require samples.
- The final verifier compares evaluated mesh coordinates and topology in this saved model against the original v4 file. The preserved exterior, main PCB, batteries, speaker pod and control PCB match.
- No board copper, buck-boost placement, SPICE decks or firmware changed. The SH1106 driver, full-white current/startup, bus behavior and off-state leakage must be checked when integrating the module.

## Results and interpretation

- Body: 105 mm cube; modeled complete external envelope: **105.0 × 105.638 × 108.0 mm**, including feet and front-button/icon protrusion.
- Actual PCB assembly: 65.50 × 62.25 × 11.54 mm from the source GLB. Native PCB thickness is 1.6 mm; the GLB substrate alone is 1.51 mm. Component models remain subject to exact-part checks.
- Four grilles: 418 openings each, **1,672 total**. Hole centres, solid webs, non-manifold edges and Euler characteristic were checked on evaluated meshes. The expected Euler value per grille is 2 − 2×418 = −834.
- The RF volume has no foreign modeled surface inside it. Triangle/box tests distinguish the hollow shell from its enclosing bounding box. This does not measure antenna efficiency or radio range.
- The battery withdrawal corridor is clear after the cover and retention bridge are released. Own holder contacts, cells, retention parts and flexible battery leads are excluded. Spring compression, removal force, finger grip and drop retention are not evaluated.
- The direct path has no rigid reflector/duct obstruction. The cloth is an intended acoustic material, excluded from the rigid obstruction test; its acoustic impedance and insertion loss have not been simulated or measured.
- Maximum diaphragm travel leaves 2.8 mm to the grille and 2.45 mm to the allocated cloth. A 1 mm rigid tolerance budget leaves 1.8/1.45 mm respectively; fabric movement and real driver variation still need allowance verification.
- The rear chamber contains 0.1981 L gross rectangular space before displacement. Net volume and acoustic response are not qualified.

These checks are a scoped interference and topology audit, not a complete tolerance stack, stress analysis, production CAD audit, acoustic model or assembly-process qualification. A rendered sealed pod is not a leak test. The short switch wells and captive hardware still require detail design. Amber geometry is intentionally provisional.

## Reproduce

From this directory:

```sh
CUBE_SKIP_RENDER=1 blender --background --python-exit-code 1 --python build_blender.py
blender --background --python-exit-code 1 --python verify_assembly.py
python3 build_report.py
```

Omit `CUBE_SKIP_RENDER=1` to regenerate the six rendered views. See [README.md](README.md) for Blender installation/path options and SVG-to-PNG rendering. Blender's `--python-exit-code 1` makes a raised verification failure visible to the shell. `verification.json` contains the full machine-readable measurements. Native PCB ERC/DRC and electrical regressions are not repeated here because no native board or circuit was modified; they are mandatory when implementing the proposed PCB revision.

## Detailed completed checks

| Check | Result | Evidence |
|---|---|---|
| Actual 64 x 56 mm PCB scale | PASS | {&quot;bounds_mm&quot;: [[-32.0, -27.99999237060547, 42.49000930786133], [32.00000762939453, 28.00000762939453, 44.00001525878906]]} |
| Main PCB hash unchanged | PASS | {&quot;sha256&quot;: &quot;0e17f9ad0cf0508d8a53ed51c0b1e6af4423311598bbb03fe811c556e8b1e7d8&quot;} |
| Actual main PCB flat and component-side down | PASS | {} |
| H1 real mounting-hole alignment | PASS | {&quot;xy_mm&quot;: [28.0, 24.0]} |
| H2 real mounting-hole alignment | PASS | {&quot;xy_mm&quot;: [-28.0, 24.0]} |
| H3 real mounting-hole alignment | PASS | {&quot;xy_mm&quot;: [28.0, -15.0]} |
| H4 real mounting-hole alignment | PASS | {&quot;xy_mm&quot;: [-28.0, -17.0]} |
| Front perforations and closed webs | PASS | {&quot;wall&quot;: &quot;Front&quot;, &quot;holes&quot;: 418, &quot;blocked_holes&quot;: 0, &quot;missing_webs&quot;: 0, &quot;nonmanifold_edges&quot;: 0, &quot;euler&quot;: -834} |
| Right perforations and closed webs | PASS | {&quot;wall&quot;: &quot;Right&quot;, &quot;holes&quot;: 418, &quot;blocked_holes&quot;: 0, &quot;missing_webs&quot;: 0, &quot;nonmanifold_edges&quot;: 0, &quot;euler&quot;: -834} |
| Rear perforations and closed webs | PASS | {&quot;wall&quot;: &quot;Rear&quot;, &quot;holes&quot;: 418, &quot;blocked_holes&quot;: 0, &quot;missing_webs&quot;: 0, &quot;nonmanifold_edges&quot;: 0, &quot;euler&quot;: -834} |
| Left perforations and closed webs | PASS | {&quot;wall&quot;: &quot;Left&quot;, &quot;holes&quot;: 418, &quot;blocked_holes&quot;: 0, &quot;missing_webs&quot;: 0, &quot;nonmanifold_edges&quot;: 0, &quot;euler&quot;: -834} |
| actual_pcb separated from holder | PASS | {&quot;gap_mm&quot;: 10.865} |
| actual_pcb separated from battery_carrier | PASS | {&quot;gap_mm&quot;: 8.865} |
| actual_pcb separated from display | PASS | {&quot;gap_mm&quot;: 15.565} |
| actual_pcb separated from rear_chamber | PASS | {&quot;gap_mm&quot;: 1.395} |
| holder separated from display | PASS | {&quot;gap_mm&quot;: 2.445} |
| holder separated from new_control_pcb | PASS | {&quot;gap_mm&quot;: 2.695} |
| loaded_cells separated from bottom_cover | PASS | {&quot;gap_mm&quot;: 3.15} |
| battery_harness clear of battery_carrier | PASS | {&quot;method&quot;: &quot;triangle/box against solid carrier&quot;, &quot;obstacles&quot;: []} |
| display_harness clear of battery_carrier | PASS | {&quot;method&quot;: &quot;triangle/box against solid carrier&quot;, &quot;obstacles&quot;: []} |
| new_control_pcb separated from display | PASS | {&quot;gap_mm&quot;: 13.3} |
| 15 mm RF envelope free of foreign modeled geometry | PASS | {&quot;obstacles&quot;: [], &quot;box_mm&quot;: [[-25, 12.75, 26.405], [23, 49.25, 57.405]], &quot;note&quot;: &quot;Triangle/box test resolves hollow-shell false positives. RF performance still requires measurements.&quot;} |
| Bottom cell withdrawal has no foreign rigid obstruction | PASS | {&quot;obstacles&quot;: [], &quot;note&quot;: &quot;Cover and retention bridge released. Does not test spring force, grip or own holder contacts.&quot;} |
| Speaker axis points directly toward front grille | PASS | {&quot;axis&quot;: [0.0, -1.0, -4.371138828673793e-08]} |
| Maximum forward diaphragm envelope clears grille | PASS | {&quot;gap_mm&quot;: 2.8, &quot;remaining_after_1mm_rigid_budget_mm&quot;: 1.8} |
| Driver rear envelope clears rear chamber wall | PASS | {&quot;gap_mm&quot;: 17.8} |
| Maximum diaphragm envelope clears allocated acoustic cloth | PASS | {&quot;gap_mm&quot;: 2.45, &quot;note&quot;: &quot;Cloth deflection and material not qualified&quot;} |
| Direct sound path has no rigid reflector or duct obstruction; cloth loss untested | PASS | {&quot;open_rays&quot;: 80, &quot;obstacles&quot;: []} |
| Rear pod five walls are closed at test rays | PASS | {&quot;wall_hits&quot;: [true, true, true, true, true], &quot;scope&quot;: &quot;Nominal wall continuity, not a seal-pressure or leakage test&quot;} |
| Driver baffle has open 46 mm central aperture | PASS | {} |
| Long control extensions removed | PASS | {&quot;switch_board_to_actuator_mm&quot;: 7.0, &quot;external_actuator_extension_mm&quot;: 0} |
| Three direct controls accessible through panel | PASS | {&quot;aperture_diameter_mm&quot;: 10} |
| Unqualified display mating hardware and UI interfaces remain explicit | PASS | {} |
| PCB and external connector/harness allocations clear sealed pod | PASS | {&quot;aabb_candidates&quot;: []} |
| I2C-only module outline and PCB thickness match drawing p6 | PASS | {&quot;measured_mm&quot;: [35.400001525878906, 33.5, 1.2000007629394531]} |
| OLED mounting hole at -33.20, -43.75 | PASS | {&quot;hole_diameter_mm&quot;: 3.0} |
| OLED mounting hole at -33.20, -15.25 | PASS | {&quot;hole_diameter_mm&quot;: 3.0} |
| OLED mounting hole at -2.80, -43.75 | PASS | {&quot;hole_diameter_mm&quot;: 3.0} |
| OLED mounting hole at -2.80, -15.25 | PASS | {&quot;hole_diameter_mm&quot;: 3.0} |
| Glass front and PCB back implement drawing 2.8 mm stack | PASS | {&quot;glass_front_z_mm&quot;: 7.0, &quot;pcb_back_z_mm&quot;: 9.800000190734863} |
| Active area is 29.42 x 14.7 with 2.05 mm offset toward header | PASS | {&quot;active_bounds_mm&quot;: [[-32.709999084472656, -38.89999771118164, 6.96999979019165], [-3.2899999618530273, -24.19999885559082, 6.990000247955322]]} |
| Enlarged window exposes active area including 0.3 mm offset allowance | PASS | {&quot;blocked_corner_rays&quot;: [], &quot;window_mm&quot;: [31.8, 17.1], &quot;nominal_edge_margin_mm&quot;: [1.19, 1.2], &quot;note&quot;: &quot;Normal viewing tested; recessed glass limits extreme viewing angles. No lens selected.&quot;} |
| display PCB to front UI PCB retains 1 mm screening reserve | PASS | {&quot;gap_mm&quot;: 1.25, &quot;remaining_after_1mm_reserve_mm&quot;: 0.25} |
| display PCB to holder retains 1 mm screening reserve | PASS | {&quot;gap_mm&quot;: 2.445, &quot;remaining_after_1mm_reserve_mm&quot;: 1.445} |
| display PCB to battery withdrawal corridor retains 1 mm screening reserve | PASS | {&quot;gap_mm&quot;: 1.25, &quot;remaining_after_1mm_reserve_mm&quot;: 0.25} |
| rear component allowance to front UI PCB retains 1 mm screening reserve | PASS | {&quot;gap_mm&quot;: 1.25, &quot;remaining_after_1mm_reserve_mm&quot;: 0.25} |
| rear component allowance to holder retains 1 mm screening reserve | PASS | {&quot;gap_mm&quot;: 2.445, &quot;remaining_after_1mm_reserve_mm&quot;: 1.445} |
| display socket to front UI PCB retains 1 mm screening reserve | PASS | {&quot;gap_mm&quot;: 1.5, &quot;remaining_after_1mm_reserve_mm&quot;: 0.5} |
| display module to main PCB retains 1 mm screening reserve | PASS | {&quot;gap_mm&quot;: 15.565, &quot;remaining_after_1mm_reserve_mm&quot;: 14.565} |
| Display glass is recessed clear of protected panel | PASS | {&quot;gap_mm&quot;: 1.0, &quot;note&quot;: &quot;Separate from lateral 1 mm reserve; actual glass/PCB tolerances and mount height still require fit check&quot;} |
| OLED mounts have at least 0.5 mm nominal neighbor clearance | PASS | {&quot;obstacles&quot;: [], &quot;note&quot;: &quot;Final screw head and pilot details unselected; this is not a full tolerance approval&quot;} |
| Four header pins use drawing p8 signal order and 2.54 mm pitch | PASS | {&quot;pins_1_to_4&quot;: [&quot;GND&quot;, &quot;VCC&quot;, &quot;SCL&quot;, &quot;SDA&quot;], &quot;note&quot;: &quot;Modeled signal mapping; no continuity or power test has been performed&quot;} |
| Rerouted OLED cable avoids module, mounts, holder, carrier and front UI | PASS | {&quot;obstacles&quot;: [], &quot;note&quot;: &quot;Allocated 2 mm cable diameter; exact connector, bend radius and strain relief remain to select&quot;} |
| Blender assembly is self-contained | PASS | {&quot;linked_libraries&quot;: []} |
| V4 exterior, main PCB, speaker pod, batteries and control PCB geometry preserved | PASS | {&quot;compared_objects&quot;: 223, &quot;changed_objects&quot;: [], &quot;method&quot;: &quot;SHA-256 of evaluated world-space vertices rounded to 0.0001 mm and face indices from both saved scenes&quot;} |

## Physical testing — every row below is NOT RUN

The following numbers are proposed engineering screening criteria, not published certification limits or guaranteed wake-up thresholds. Record the chosen alarm file, volume, firmware, battery chemistry/state, ambient temperature, microphone calibration, position and exact enclosure/cloth revision with every result.

| Test | Method and saved evidence | Decision criterion / unresolved target | Status |
|---|---|---|---|
| Basic part fit | Calipers and real parts; verify OLED drawing datums, back-side components, mated connector envelope, speaker terminals, holder with max-size cells; update the CAD | All prescribed clearances survive actual dimensions and tolerances; no pressed wires or cell interference | NOT RUN |
| New display electrical integration | Run SH1106 edge/checkerboard patterns and settings screen; 100 switched-power cycles; test full-white current, I2C rise time and powered-off leakage using the actual J4 harness | Correct orientation and complete 128×64 image on every start; rail/pin limits respected, no back-power or off-state lighting; module datasheet lists 45 mA maximum at 3.3 V full-white | NOT RUN |
| Service controls | Fit direct switches and panel; 100 presses each, 20 settings sessions, 20 battery replacements | No sticking, missed/double events, accidental power operation or cells falling out while setting the alarm; intact wells/bridge | NOT RUN |
| Grille/cloth insertion loss | Same sealed pod, speaker and fixed electrical drive; compare bare baffle, grille only, grille + cloth; three repeated sweeps each | Provisional screen: within 2 dB average level in 500 Hz–4 kHz; investigate every repeatable new >3 dB response feature, buzz or audible loss of clarity | NOT RUN |
| Small chamber response | Compare v4.1 to a larger sealed test volume with measured net volumes; same driver and drive; save response/decay and listening notes | Choose the smallest volume meeting the agreed sound quality. Do not retain 105 mm solely for appearance if the response is objectionable | NOT RUN |
| Old versus new arrangement | Same speaker/amplifier/file and measured drive; compare v3 reflector prototype if available against v4.1 | Prefer the arrangement with cleaner response and adequate pillow-position level at less battery power; no superiority claimed before measurement | NOT RUN |
| Direction and bedside placement | Record at 1 m on axis, ±45°, 90°, 180°, then the actual pillow position; repeat near wall and beside normal nightstand objects | Front-facing placement meets a user-approved awake listening level with adjustment margin. Side/rear loss is reported, not passed as omnidirectional | NOT RUN |
| Distortion and rattles | Low-level sweep first, then controlled stepped level using the real alarm signal; inspect harmonics and audible buzz; repeat at the pillow | No buzz, panel rattle or abrupt compression; provisional <5% THD in 500 Hz–4 kHz at the agreed level, subject to microphone noise/distortion floor | NOT RUN |
| Pod leakage | Inspect gasket compression, blind bosses, joints and potted wire exit; compare low-level response before/after temporary seam sealing | No repeatable response/buzz change from sealing a supposedly closed seam; any leak is fixed before acoustic comparison | NOT RUN |
| Continuous load and cooling | Real assembled unit, initial 0.5–1 W-class audio trial only after checking electrical drive, fresh and depleted AA sets of each chemistry; log battery current, minimum loaded voltage, rails and component/cell/holder temperatures | Meet selected component/cell limits with design margin; no resets, audio collapse or continuing temperature rise. Intended maximum alarm duration and ambient envelope still need definition | NOT RUN |
| Overnight energy reserve | Measure sleep, radio checks, display use and a sustained alarm; integrate current for both chemistries | Define and demonstrate a battery warning threshold that leaves the required alarm reserve; no battery-life figure inferred from nominal AA capacity | NOT RUN |
| Radio and dwell behavior | Closed enclosure in actual bedroom; sensor in shower location, doors closed, normal obstacles; log sequences, gaps and dwell events | No false completion, no ACK-timeout silence, no counting absent/unknown presence toward X; interruption/recovery behavior matches state contract | NOT RUN |
| Switching ringing / parasitics | Differential probing with short connections at regulator and amplifier supply nodes; measure overshoot/undershoot at startup, radio bursts and alarm transients | Compare to exact datasheet limits with margin; preserve captures and probe setup. No oscilloscope data has been supplied | NOT RUN |
| EMI screening | Compare supply/near-field spectra during sleep, ESP-NOW and alarm operation; vary wire routing and closed shell; repeat radio checks | Explain and address repeatable coupling/noise regressions; this is screening, not radiated/conducted-emissions certification | NOT RUN |

## Free software workflow for the acoustic comparison

Use the free single-channel features of [REW](https://www.roomeqwizard.com/) for response, spectrum and distortion analysis. No paid REW upgrade is needed. Follow its [measurement setup](https://www.roomeqwizard.com/help/help_en-GB/html/makingmeasurements.html): keep drive level, microphone position and gain fixed, avoid clipping and apply calibration where available. Save the native measurement files and export traces. A calibrated borrowed microphone or meter can establish SPL; an uncalibrated microphone is useful for controlled relative comparisons but does not establish absolute pillow SPL. Disable automatic gain control/noise suppression when possible and verify repeatability.

For the assembled ESP32 alarm, the test stimulus must actually pass through its DAC/I²S/amplifier path. Add a firmware test mode that plays a known sweep/WAV at a reproducible level, or use REW's appropriate offline/import workflow with timing accounted for. Do not simply measure a different computer-driven amplifier and call it the board's result. Actual alarm recordings and RTA comparisons can precede this firmware work.

Start at low drive, especially below the small driver's resonance. Measure the same physical setup three times; if repeatability exceeds about 1 dB over the comparison band, fix placement/gain/noise before interpreting a 2 dB difference. The user should judge the awake listening level before any scheduled wake-up trial; a louder measurement alone does not demonstrate reliable waking.

Optional impedance measurements can help identify enclosure resonance, but require a correctly built/calibrated jig and a speaker disconnected from the alarm amplifier. Follow [REW's impedance instructions](https://www.roomeqwizard.com/help/help_en-GB/html/impedancemeasurement.html). **Do not attach a grounded sound-card input or oscilloscope ground clip to either BTL speaker output.** Neither output is ground; use an appropriate differential measurement arrangement for the powered amplifier.

Python and CSV files suffice for battery/temperature logging and plotting. Free software cannot replace the microphone, probes, temperature sensors or radio test hardware needed to collect evidence. No software-only thermal or EMI qualification is claimed.

## Remaining release blockers

- EastRising shipped I2C-only revision, back-side component maxima, exact mating socket and cable bend; SH1106 firmware and switched-power bench tests
- Switch, holder and PCB dimensional tolerances; loaded AA contact compression
- Control/front UI board schematics, connectors and routed PCB revision
- USB access by chassis removal; detailed detachable chassis fasteners and harness service loop
- Captive screw hardware, retention bridge, gasket and sealed feedthrough production details
- Speaker basket displacement and terminals; measured net acoustic volume
- Grille strength, vibration, acoustic loss and four-direction response
- Actual battery-load, radio, thermal, EMI and parasitic measurements
