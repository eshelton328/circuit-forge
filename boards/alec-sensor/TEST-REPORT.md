# ALEC Sensor S1.1 — design and test report

**Result:** a real, fully routed four-layer sensor PCB and a dimensioned circular enclosure assembly now exist. Local ERC, DRC, schematic parity, saved-copper connectivity and JLCPCB advanced four-layer rule checks pass. These results support preparing a small engineering PCB order alongside the clock. Supplier fabrication/assembly preflight remains required; customer shower qualification is a later stage. See the [prototype order plan](PROTOTYPE-ORDER.md).

S1.1 corrects rear service access: POWER/RESET/BOOT are on B.Cu beside a rear-opening battery holder, which is retained independently of the cover. The electrical topology and values remain at S1. A subsequent ordering audit corrected C29 from a 0603 manufacturer part number to GRM155R71C104KA88D for its existing 0402 footprint. No placement, routing or electrical value changed in that correction; [metadata-only evidence](review/ordering-metadata-change.json) binds the unchanged geometry to the retained render/simulation evidence.

The previous S0 material was a schematic study with no PCB. S1 promotes the electrical project to `boards/alec-sensor`, adds a populated board model, and integrates its actual geometry with the AA holder and radar. The main alarm boards are unchanged.

## What changed

- Retained ESP32-S3-WROOM-1-N16, RV-3028-C7, both TPS63070 cells, reverse-polarity protection, native USB and switched battery measurement.
- Added the LD2410C five-pin interface, TMUX1511 signal isolation, local bypassing and explicit GPIO/power sequencing.
- Selected SW1 C&K **1101M2S3CQE2**, rated 6 A at 28 VDC, for a physical battery disconnect. F1 **046701.5NRHF**, 1.5 A fast fuse, is near the battery connector. The unused switch throw is NC; pin 2 is common.
- Selected Samtec **SSW-105-01-F-S** socket; a custom footprint uses the manufacturer's body dimensions and 2.54 mm pitch. A nonmetallic radar retention clip is allocated; the socket itself is not a positive lock.
- Placed POWER, RESET and BOOT on the rear of the board, clear of the battery holder. The battery/pair button and RGB indicator retain their front-panel linkage positions. The holder now opens toward the rear cover, on an internal carrier; routine cell/control service leaves the board and wiring installed.
- Assigned explicit ordering candidates to all **88 electrical components**, including previously unspecified passive parts. This is a prototype BOM, with DC-bias and availability checks still open.
- Built a **116 mm diameter × 54 mm** circular enclosure fit model. Three AA cells sit behind the flat PCB; radar faces the PC front. The earlier 100 × 40 mm concept did not include the full connector/air-gap/service stack.

## Executed checks

| Check | Local result | What it establishes |
|---|---|---|
| Fresh KiCad ERC | **0 errors, 0 warnings** | Schematic electrical rule consistency |
| DRC with zone refill and saved board | **0 violations** | Checked board clearances, holes, silk and routing rules |
| Schematic parity | **0 issues** | Native schematic and PCB agree |
| Unconnected items | **0** | No outstanding ratsnest connections |
| Filled-copper check | **277 pad nodes across 60 nets, all connected** | Copper actually touches each multi-node electrical terminal |
| JLCPCB four-layer advanced profile | **Pass** | Checked profile limits; not a fabricator quote/stackup approval |
| Independent interface assertions | **47 pass** | USB/RTC/UART GPIOs, correct TX/RX crossing, power isolation, fuse and switch topology |
| Ordering metadata and capacitor sizes | **88 components agree; 27 capacitor packages match** | BOM/schematic/PCB MPN consistency and selected package-family size codes; supplier stock, pin mapping and assembly review remain open |
| Rear service contract | **8 pass** | Native control faces/positions, exterior interfaces and rear-opening holder; includes negative wrong-face/holder-orientation tests |
| Layout intent | **Pass** | Short capacitor connections, ground reference, switch-node geometry, battery trace widths |
| Passive input SPICE | **27 cases executed** | Bounded contact-closure/inrush RLC behavior under stated assumptions |
| Battery source calculation | **72 cases evaluated** | Supply-voltage margins versus illustrative loads/pack resistance |
| Lumped thermal calculation | **12 cases evaluated** | Sensitivity to assumed cooling; not PCB or junction temperature |
| Parametric CAD | **Valid solids; 19 selected solid/approach intersection checks pass** | Explicit nominal fit checks, not an exhaustive tolerance/collision certification |
| Python regression suite | **127 passed, 1 skipped**; [log](review/python-tests.txt) | Includes negative UART-swap, isolation-bypass and fuse-bypass, front-facing service-button, inward-opening holder and stale BOM substitution controls |

The local suite ran under Python 3.9; the single integration skip requires Docker. Deprecation warnings were from the installed plotting dependencies. CI runs the repository suite under Python 3.12.

Reports are in [review](review/). [source-hashes.json](review/source-hashes.json) binds the delivered evidence to native source files. CI regenerates sensor connectivity/layout/power evidence and separately rebuilds the mechanical CAD. Existing CI for other boards is not evidence that this sensor is qualified.

## Buckboost layout review

**The converter cells were not compacted or rotated.** U1/U2, L1/L2, C1–C16 and R3–R10 retain their original positions and footprints. The saved switch-node track geometry matches the reviewed source. C3/C5/C11/C13 remain about **1.81 mm** from their respective VIN/VOUT power-pad centers, with **direct 0.4 mm F.Cu connections**. Each has a short return to a ground via; each converter retains two nearby PGND plane connections. In1.Cu contains no signal tracks.

The MCU-side enable connection changes because GPIO18 is now radar RX. GPIO16 controls the radar regulator; its local converter enable escape is retained, with R19 holding it off during reset. The RTC uses GPIO8/9 and interrupt GPIO1, independent of UART17/18.

The new series battery path uses at least **0.75 mm** tracks. Its three net-length sums are approximately **9.63, 55.09 and 54.27 mm**. Assuming 35 µm copper at 20°C, their summed trace resistance is **78.1 mΩ**, before vias, contacts, heating and tolerance. The rear-facing mechanical switch costs routing length; this is an explicit prototype tradeoff. Measure the drop at the actual operating current.

These geometric checks prevent known layout regressions. They do not establish parasitic inductance, switch-node overshoot, radiated EMI, converter stability or RF performance. New routing, a radar load and a sealed enclosure invalidate any claim that the old board's physical results automatically transfer.

## Power, batteries and sleep

Supported chemistry is three series **AA alkaline or 1.5 V primary lithium** cells. No Li-ion/14500 cells, charger or USB-to-battery path is present. USB-C supplies data and VBUS detection only; batteries and SW1 ON are needed for flashing.

The source sweep assumes pack open-circuit voltages 3.0/3.6/4.5/5.4 V; whole-pack resistance 0.15/0.6/1.5 Ω; efficiency 75/85%; and three load cases: 80 mA MCU + 79 mA radar, 80 mA MCU + 200 mA radar reserve, and 500 mA MCU + 200 mA radar simultaneous peak envelope. It adds computed PCB resistance, 38.5 mΩ nominal fuse resistance, 10 mΩ switch, 150 mΩ Q1 and 20 mΩ extra via/harness allowance. These are **assumptions**, not chemistry/SOC measurements.

**26 of 72 combinations lack the assumed 3 V cold-start margin or a stable source operating point.** TPS63070 may run below its cold-start requirement; a board that keeps running on depleted cells may fail to restart. Firmware must qualify battery voltage under load, prevent brownout/restart loops and declare low-battery status before this region. Do not treat “3 AA” as a regulated 4.5 V source. See [power-screening/summary.json](review/power-screening/summary.json).

At the example active load, input power is about **0.775 W**. With 9 Wh usable pack energy, the arithmetic yields approximately **11.6 hours continuous**, or **22 days at 30 minutes active per day** with 0.2 mA assumed whole-board sleep current. Energy, temperature, age, chemistry, voltage cutoff and wake/sync time will change this substantially. The battery model is not a discharge curve.

**Recommended starting firmware mode: scheduled alarm window, with continuous mode available for testing.** Synchronize time and the alarm schedule while the radio is awake. Wake from the RTC before the alarm window; enable 5 V, wait for PG, enable signal isolation and qualify fresh UART frames. Shut down I/O before the radar rail. ESP-NOW cannot remotely wake an ESP32 in deep sleep. Radar OUT only provides a wake hint while the radar and signal path remain powered. Hard OFF/battery removal loses RTC time because there is no backup cell.

The existing local ultrasonic breadboard sketch waits for an ESP-NOW START message with its radio awake. It cannot be used unchanged for a sleeping LD2410C product. Firmware migration and sleep-current measurement are still required; no application firmware is claimed complete in this PR.

## SPICE and fuse review

The 27 new ngspice cases model connection of a 5.4 V pack to the board's nominal 60 µF input bank, with 25/50/100% effective capacitance, 10/100/1000 nH assumed harness inductance and 0.15/0.6/1.5 Ω pack resistance. They include the new PCB trace resistance and the stated series allowances.

The simulated passive cases peak at **5.414 V** and **11.70 A** across the sweep; maximum input I²t is about **2.50%** of the fuse's nominal 0.0766 A²s melting figure. The short modeled pulse is **not** proof of fuse or switch endurance. Converter startup, load current, contact bounce, initial cell conditions and real parasitics are omitted. The 6 A switch's steady DC rating does not establish its capacitive-inrush lifetime.

F1 is secondary board protection, not a precise current limiter. The 1.5 A marking is not a continuous operating budget at elevated temperature: apply the manufacturer's 25% continuous derating and temperature rerating. A short on the holder wiring **upstream of F1 is not protected by this PCB fuse**. Inspect/secure/insulate those leads and evaluate pack-side protection before releasing the enclosure.

No encrypted/commercial converter model or paid solver is used. These SPICE runs do **not** simulate TPS63070 switch-node ringing, common-mode EMI, radio emissions or closed-loop stability.

## Thermal screen

The lumped calculation uses the front and side external area, excludes the obstructed rear face, and assumes effective convection coefficients of 3/5/8 W/(m²·K). It treats internal electrical power as heat and ignores internal temperature gradients, wall conduction and radiation.

At **40°C ambient**, the example 0.775 W case gives an estimated lumped surface temperature of **45.1°C at h=5** or **48.5°C at h=3**. The deliberately sustained 3.53 W stress envelope gives **63.4°C** or **78.9°C**, respectively. This sustained peak case is not an approved operating mode; it demonstrates why firmware load duration and cooling cannot be assumed away.

These are neither local PCB temperatures nor semiconductor junction temperatures. Measure U1/U2, Q1, cells, radar and case in the assembled housing. Verify each selected part's limits, especially the mechanical switch's 65°C operating maximum, and assess touch temperature and cell behavior independently.

## Mechanical/RF checks

The assembly imports actual PCB GLB, MPD holder geometry and Hi-Link radar STEP-derived GLB. The holder body is **57.15 × 46.61 × 17.39 mm**. Radar body is **22 × 16 mm**; its existing header/socket stack puts the front copper plane at Z=38 mm. The PC inner face is Z=50.4 mm.

Nominal clearances are **1.29 mm** at the battery holder's farthest corner through the rear opening, **3.61 mm** to PCB underside and **1.61 mm** to PCB screw heads. The lower-right PCB support uses a short post/rib below the radar. Nineteen explicit CAD intersection checks cover the prior cup/button/radar/holder pairs, the new carrier against cup/cover/holder, and each service control’s rear approach against cup/holder/carrier. The AA holder opens rearward. The fixed carrier uses three M2 mounts, a 1 mm plate, 1 mm stiffening ribs and four nominal edge hooks; the cover carries no battery wiring. Nominal carrier rib-to-PCB clearance is 1.61 mm, and plate-to-PCB-screw-head clearance is 0.61 mm. Physical finger access, clip retention/release, cell extraction and the tolerance stack must still be checked. This is not an exhaustive all-component/tolerance check.

The 3.6 mm PC wall and 12.4 mm air gap are initial values derived from the Hi-Link radome guide, **not tested tuning**. Use unfilled, nonconductive material and qualify the actual resin, pigment, finish and wet surface. The circular shoulder helps drainage, but shape alone cannot make a product waterproof. Six rear screws sit outside the main O-ring; the button uses a clamped silicone membrane and guided plunger. Gasket dimensions are nominal; material, gland tolerances, inserts and torque require samples. There is no ingress rating yet.

The front optical area remains solid PC. The radar-retention clip, battery-carrier clip tolerances/creep, mated battery plug/harness, suction/adhesive adapters and exact insert/hardware variants remain mechanical allocations. Internal undercuts mean a manufacturing review is required before CNC or molding. The complete enclosure is not represented as ready-to-order tooling.

## Required prototype tests / acceptance record

Record actual cells, holder/contact resistance, firmware revision, LD2410C firmware/configuration, ambient, mounting angle and instruments for every run. Save waveforms and raw logs; do not replace missing measurements with a checked box.

| Test | Procedure and decision |
|---|---|
| First power / assembly | Inspect socket pin1 and switch common against drawings; check polarity and resistance with current-limited bench supply. Confirm both rails/PG before adding radar. Verify fuse continuity and all package orientations. |
| Startup/depleted cells | Start and restart at 5.4/4.5/3.6/3.0 V with representative source resistance. Capture protected battery, 3.3 V, 5 V, EN and PG. Establish a firmware cutoff above repeatable startup/brownout failure, with margin. |
| Inrush/fault | Measure hot-plug, bounce, converter startup and worst load pulses; integrate actual current² over time. Review fuse derating/interrupt rating, switch inrush wear and safe fault clearing. Evaluate upstream holder-wire faults separately in a protected fixture. |
| Load step/ringing | Step actual radar and ESP-NOW loads. Probe converter switch nodes and VIN/VOUT with short ground springs/coax at ≥100 MHz bandwidth; check overshoot against component absolute maxima and rails against operating limits. Repeat at voltage/temperature extremes and PFM/forced-PWM modes. |
| Signal backfeed | Radar OFF, I/O OFF: measure radar supply and TX/RX/OUT leakage. Test MCU reset, power sequencing, brownout, USB insertion and sleep holds. No unintended powering or invalid presence transition is acceptable. |
| Sleep / RTC / radio | Measure complete pack current, not only ESP32 current. Verify RTC alarm/button wake, UART restart, schedule resync, lost peer and power cycle. Confirm radar Bluetooth state after resets/rapid power cycles. |
| Conducted/radiated noise | Compare rails/spectrum and near-field probes with radar off/on, ESP-NOW bursts, LED PWM and both converter modes. Free sigrok/PulseView, Python and instrument FFT tools can record/analyze data; probes/scopes may need to be borrowed. Formal EMC compliance remains separate. |
| Enclosed thermal | Log U1/U2, Q1, cells, radar and case until stable at the agreed ambient/duty limits; include warm, still-air mounting and a continuous stress run. Investigate hot spots and derate before exceeding any selected part's limits. |
| Dry/wet RF | Compare bare radar versus enclosure, dry/condensed/wet/soap film, several gaps/material coupons, tile/glass surroundings and intended mounting height/angle. Log detection gates and false positives, not only a green LED. |
| Water-only false stop | Run empty-shower spray/steam, moving curtains, fan and nearby people behind glass. The alarm must not stop from water/held OUT alone. Require fresh qualified UART evidence throughout the chosen dwell time; define acceptable false-stop rate before release. |
| Sealing/condensation | Validate membrane force/travel/fatigue, O-ring compression, torque and repeated battery access; test jets/immersion for the chosen target plus hot/cold condensation and soap exposure. IP66/IP67 are separate proposed tests, not a current rating. |
| Rear service | With the holder/cells installed, remove only the rear cover and operate POWER/RESET/BOOT; replace all three cells without moving the PCB or pulling the harness. Check finger room, polarity markings, carrier hooks, screw access and re-sealing over repeated cycles. USB cable service remains a separate carrier/PCB-removal operation. |
| Mount retention | Test rigid screw cradle and selected suction/adhesive adapters on representative wet tile/glass, sustained load and repeated thermal cycles. Check slippage/angle changes, drainage and clean removal. |

**Release gates remain open:** actual battery endurance and load limits; effective capacitor values and assembled load-step response; fuse/switch transient behavior; fabricator stackup/USB impedance/thermal-via process; RF/wet false-positive behavior; temperature measurements; enclosure tolerances and ingress/mount qualification. Passing CI does not close these gates.

## Primary references

- [Hi-Link LD2410C product/downloads](https://www.hlktech.com/en/Goods-239.html) and the manufacturer V1.09 manual/radome guide linked in [SOURCES.md](SOURCES.md).
- [TI TPS63070 datasheet](https://www.ti.com/lit/ds/symlink/tps63070.pdf), [TMUX1511 datasheet](https://www.ti.com/lit/ds/symlink/tmux1511.pdf).
- [C&K/Littelfuse 1000 series](https://www.littelfuse.com/assetdocs/littelfuse-c-k-slide-1000-series-datasheet?assetguid=68a2b41e-19a4-4cf4-821b-aca78a430f00), [Littelfuse 467 fuse](https://www.littelfuse.com/assetdocs/fuse-467-datasheet?assetguid=4a59f034-1cca-460e-a5ba-e1e66247c76d).
- [Samtec SSW drawing](https://suddendocs.samtec.com/prints/ssw-1xx-xx-xxx-x-xx-xxx-xx-mkt.pdf), [MPD BH3AAW drawing](https://www.batteryholders.com/uploads/parts/BH3AAW/datasheets/BH3AAW-datasheet.pdf).
- [Espressif S3 sleep modes](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/sleep_modes.html), [module positioning](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html#general-principles-of-pcb-layout-for-modules-positioning-a-module-on-a-base-board).
