# ALEC Sensor S0 verification and qualification plan

Date: 2026-09-07. Scope: the new native schematic, interface contract, initial power estimates and enclosure brief. **No sensor PCB has been routed or built. No shower, RF, thermal, ringing or ingress test has passed yet.**

## Completed checks

| Check | Result | What it establishes |
|---|---|---|
| KiCad 10.0.1 ERC, all three sheets | 0 errors / 0 warnings, no ERC exclusions | Schematic electrical-rule consistency |
| Fresh exported XML netlist | 87 components | Reviewable electrical connectivity |
| Independent sensor interface assertions | 45 passed | UART direction, GPIO assignments, USB/RTC separation, reset pull-downs, rail isolation and RGB polarity |
| Deliberate fault injection | UART swap and bypassed isolation both rejected | Checks detect two realistic assembly/design mistakes |
| Python tests for this study | 4 passed | Interface checks and energy-budget units exercised |
| Full repository Python suite | 121 passed, 1 skipped | Existing Python regression checks also pass locally; not a PCB or physical test |
| Retained circuit comparison | 50 multi-node net groups preserved | Retained baseline circuitry matches after excluding the deliberate hard-switch and UART/enable changes; checked locally |
| Schematic PDF/SVG export | Three pages generated and visually inspected | Readable native artifacts; no physical-layout evidence |
| Manufacturer radar CAD | STEP opened; bounding box 22.000 × 16.000 × 11.500 mm | Correct C variant/header envelope, not mounted assembly fit |
| Runtime sensitivity calculation | Generated for 6/9/12 Wh and four duty cycles | Illustrative energy arithmetic; no measured lifetime |
| Enclosure outline comparison | Circular and rounded-square views generated at the same scale and visually inspected | Concept comparison only; the holder diagonal and face areas are calculated, with no complete assembly fit or new physical qualification |

Machine outputs: [ERC](review/erc.json), [interface checks](review/interface-checks.json), [netlist](review/netlist.xml), [power budget](review/power-budget.json), [source hashes](review/source-hashes.json). The separate schematic-study CI workflow exports fresh inputs before checking; a committed XML file is not treated as proof that later schematic edits passed.

The preserved topology comparison excluded SW1, the battery-switch boundary J1.1/Q1.3, and U3.11 (GPIO18, deliberately reassigned). All other retained nodes of each original net with at least two retained nodes had to share a net in S0. It is not a simulation or proof of analog behavior.

## Open release items

- Exact hard power switch with verified DC continuous/inrush rating, battery short-circuit/current protection, footprint and service geometry. The schematic's switch is explicitly a placeholder. Select these before a PCB order.
- Retained, correctly oriented LD2410C socket/harness. Generic connector numbering does not prove mating orientation. Exact capacitor MPNs/DC-bias derating for added parts also remain open.
- Actual LD2410C firmware, MyLD2410 version, frame period and startup/absence hold behavior.
- All-day versus scheduled operation, awake window, X-second dwell, battery replacement target and behavior when the sensor fails to wake or synchronize.
- Real PCB with both antenna keepouts, ground returns, converter capacitor loops, test points and mechanical mounting datums. No Gerbers or board 3D model are provided for S0.
- Enclosure material grade/color, radome thickness/gap, gasket, vent, button membrane, light-pipe seal and mounts. The concept drawing has no validated 3D stack.

## First experiment — before custom PCB or enclosure tooling

Use the user's breadboard LD2410C and a **dry, battery-powered, temporarily sealed test fixture** outside direct spray. Keep the electronics protected; never expose a breadboard or USB-connected bench setup to shower water. Put removable plastic coupons in front of the radar so their outer surfaces can be tested wet while the electronics remain dry. This can answer whether this radar is suitable for the task before spending money on custom parts.

Log time, firmware version, configuration, supply voltage, raw/engineering gate data, reported distance/state, OUT, ground-truth occupancy, wet/dry condition and mounting geometry. Use MyLD2410, Python/CSV and a free plotting tool. Mark the person entering/leaving independently; the radar's own output is not ground truth.

Provisional screening criteria below are **proposed engineering gates**, not a standard or established product performance. Record results, repeat with different people and then set the product's final acceptance limits.

| Test | Method | Provisional decision gate |
|---|---|---|
| Person in intended shower zone | At least 20 complete approach / X-second dwell / departure trials per condition, varied height and motion; dry front, droplets, water film and representative soap residue | At least 19/20 valid completions, no completion before X; report worst arrival/departure latency and missed-frame intervals |
| Water-only rejection | Person leaves field, shower runs; include curtain movement and dripping front; at least 30 minutes per condition | Zero false completed dwells; extend to repeated full shower cycles before relying on it |
| Outside-zone rejection | Person beyond door/glass, near adjacent wall and behind sensor; vary range-gate settings | Zero completed dwells from excluded locations in the logged trials |
| Pause / leave mid-dwell | Leave at several points within X; characterize minimum resolvable absence, including no-person hold | Dwell resets for the declared interruption duration; if hold masks required departures, redesign the detection rule |
| Enclosure sensitivity | Same fixture and settings, open reference vs actual plastic grade/thickness; gaps 4/6.2/12.4/18.6 mm | Select the combination that preserves acceptance above; do not select solely by apparent range |
| Mount motion | Repeat with final cradle, suction/adhesive options and realistic vibration | No false completed dwell from housing movement; no slips or detachment |
| Radio through bathroom | Intended bedside position, doors shut, person between units, shower operating, relevant Wi-Fi channels | Log delivery and application ACK latency; completion retries succeed within agreed limit; loss never creates success |

Zero false events in a short test does not establish a zero false-alarm probability. A failed water-only rejection test is a reason to revisit the sensor or add independent evidence, not to hide the failure with a longer timeout.

## Electrical bench tests after schematic/BOM completion

Use a current-limited dry bench supply and actual alkaline/1.5 V primary-lithium packs. Nominal pack sweep: 3.0, 3.6, 4.5 and 5.4 V. Add controlled source resistance based on measurements of depleted cells and contacts. The inherited TPS63070 circuit requires about 3.0 V for reliable cold start; investigate below that for fault behavior rather than promise usable operation. Test both rail loads simultaneously.

- Record 5 V startup/ripple at J3 with a ground spring and documented oscilloscope bandwidth. Supply more than 200 mA capacity at the radar; use **≤50 mV peak-to-peak ripple** as an initial supplier-guided target, and separately record startup overshoot and transients. Measure the actual radar load rather than treating 79 mA as its peak.
- Step the 3.3 V load through realistic ESP32 radio bursts while radar operates. Confirm neither rail causes reset, UART corruption or false presence. Use real firmware plus a programmable load where available; component absolute maxima and guaranteed operating limits define electrical pass/fail.
- Measure pack current in hard OFF, scheduled sleep, powered-radar wake and active ESPNOW operation. Measure LED and monitoring-circuit contributions. Whole-board 0.2 mA sleep is only the runtime model's assumption, not a passed limit.
- Sweep startup, shutdown and brownout ordering. Drive UART high/low and exercise pulls while 5 V is OFF. Measure residual radar VCC and signal currents; verify no partial boot or persistent back-power. Include reset/crash while GPIO holds were active. U10 default-OFF pull-downs do not replace this measurement.
- Verify BOOT/RESET recovery from deep sleep, native USB flashing, no VBUS-to-battery charging path and no battery-to-USB backfeed with supply combinations. Current-limited fixtures first.
- Calibrate switched ADC battery measurement under load and after recovery. Thresholds are chemistry-dependent; voltage alone is not a precise state-of-charge estimate.
- Verify RTC alarm/button wake, interrupt clearing, timer fallback, time loss after battery removal, schedule acknowledgment, pairing persistence and replay/stale-session rejection.

## PCB, thermal, EMI and water qualification

When a layout exists, run ERC, schematic parity, routed connectivity, board/fab DRC and a specific review of the two converter loops and both antennas. Generate new simulations from the sensor circuit and layout. Use ngspice for load/rail/sequence hypotheses, FastHenry for conductor inductance where its assumptions fit, and openEMS for controlled RF studies with measured material inputs. None of these establishes shower presence accuracy or regulatory compliance by itself.

In the final sealed housing, log radar, ESP32, converters, battery contacts and ambient temperatures during sustained active sensing and rapid radio retries. Test the hottest intended bathroom ambient, depleted-cell load and warm/cold cycles. Compare measured temperatures against each selected component's guaranteed operating range and material limits. No numeric temperature rise is predicted without geometry, losses and boundary conditions.

Build a seal-only mechanical prototype before risking electronics. Test gasket compression, cover reassembly, button cycling, light-pipe seam, vent bond and mount retention, then test the fully assembled device to the chosen IP66/IP67 procedures. Add repeated warm humid exposure, cooling/condensation and representative cleaner/soap exposure. Inspect inside for moisture and corrosion, then rerun RF and electrical checks. A passed dry bench test or component IP rating does not establish the whole product's rating.

All proposed software tools are free. Physical fixtures, instruments, custom parts and any formal qualification service can still cost money.
