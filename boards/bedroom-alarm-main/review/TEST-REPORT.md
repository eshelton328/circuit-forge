# V4.2 PCB and enclosure test report

**Prototype review passed the listed software checks. Physical qualification and manufacturing release have not been performed.** Tests refer to the actual saved boards and v4.2 Blender assembly, with source hashes in [qa-manifest.json](qa-manifest.json). No battery endurance, wake-up reliability, acoustic quality, ESP-NOW range, emissions compliance or junction-temperature pass is claimed.

## Electrical and layout checks

| Board | ERC violations | DRC/parity/unconnected violations | Fabrication rules |
|---|---:|---:|---|
| main | 0 | 0 | jlcpcb-4layer-advanced: pass |
| controls | 0 | 0 | jlcpcb-2layer-standard: pass |
| front | 0 | 0 | jlcpcb-2layer-standard: pass |

The full local repository suite reports **115 passed, 1 skipped**.

All three also pass the repository's filled-copper connectivity guard. The bottom board uses explicit ground traces as well as its filled planes. Board intent validation passes on all three projects.

- 487 circuit/interface checks: retained circuit peers and component values/footprints, full cable pin maps, hardware-enable throws, LED polarity/current limiting, display order and UART connections.
- 145 layout checks: retained placements, 1,094 inherited power/return/USB/BTL track or via geometries, In1 ground-plane use, local bypass connections, mounts and inward-facing daughterboard connectors. The local capacitor pad-to-pad separation remains approximately 1.81 mm.
- 105 SPICE measurements passed. This includes the inherited 25 behavioral power/load checks and 80 measurements across sixteen damped remote-button corners. The TPS63070 model is the repository approximation, not a validated TI switching model.
- 52 saved-assembly checks passed, including actual board sizes/orientations, switch-to-panel alignment, OLED rear/socket clearance, RF keepout, mated connector/cable envelopes, cap clearance at rest, and the programming-fixture corridor. The unchanged exterior/acoustic/battery objects are fingerprinted against v4.1.

## Remote button sensitivity — why R50–R53 were added

The model sweeps 0.1–1 µH cable-loop inductance, 0.1–1 Ω wire/contact resistance, and 80–120 nF debounce capacitance. These are **assumed screening bounds for ≤200 mm cables**, not extracted or measured harness parasitics. The ideal switch and unclamped GPIO node expose the circuit's tendency to ring; there is no transistor-level ESP32 clamp or ESD model.

All eight undamped negative controls violate the screening limits. The worst unconstrained model requests −3.076 V at the GPIO and 3.203 A peak switch current; those are not predictions of an actual clamped ESP32 waveform. With a nominal 100 Ω series resistor, tested conservatively at 95 and 105 Ω, all sixteen corners pass: minimum GPIO ≥0.031 V, peak switch current ≤34.67 mA, valid held LOW and released HIGH. The selected resistor is 1%; the sweep is wider. Twelve separate DC cases confirm the enable switch truth table, including unplugged = standby.

These results justify damping and a prototype oscilloscope test. They do not replace bounce testing, ESD qualification, contact-life validation or measured cable parasitics. See [raw harness results](harness-simulation.json) and [SPICE report](spice-report.md).

## Fresh copper/thermal screening

FastHenry and ngspice were rerun on freshly exported product-board copper. The comparison is the **merged 64 × 56 mm bench board**. Both use the same coarse local-window extraction. The original key in the raw solver JSON refers to that bench board in this report.

| Local bypass loop | Product R at 1 MHz, mΩ | Product L at 1 MHz, nH | Bench L at 1 MHz, nH |
|---|---:|---:|---:|
| U1 / C3 | 4.355 | 0.923 | 0.923 |
| U1 / C5 | 4.040 | 0.885 | 0.885 |
| U2 / C11 | 4.512 | 0.942 | 0.942 |
| U2 / C13 | 4.250 | 0.904 | 0.904 |

These are approximate PCB-only local loops. Package/inductor/capacitor internals, remote conductors and full mutual coupling are omitted. Coarse-mesh values are not precise signoff parasitics. The existing passive-PDN, bounded ringing, differential-mode transfer and mathematical controls ran; no actual TPS63070 switching spectrum or radiated/common-mode EMI result is available. [Summary and assumptions](physical-screening/summary.json), [raw inputs/matrices/transcripts](physical-screening/raw-data.zip).

The four-sheet PCB thermal model predicts **33.61°C peak PCB rise**, versus 33.40°C for the bench board at 0.5 mm thermal grid spacing. At 1 mm it predicts 33.11°C, versus 32.93°C. The ~0.21°C difference is not a demonstrated physical deterioration; it is smaller than the unvalidated model uncertainty.

The inherited nominal fixture uses 0.5 A on 3.3 V, 0.6 A on 5 V, 85% converter efficiency, 0.7 W ESP32 heat, 0.3 W amplifier heat and an assumed 10 W/m²K surface heat-transfer coefficient. At 25°C ambient this implies about 58.6°C peak PCB temperature; at 50°C, about 83.6°C. **Neither enclosure cooling nor package junction temperature is modeled.** Energy conservation passes, but this thermal result does not qualify continuous playback from three AA cells. The current run uses the suite's `ci` profile; fine-mesh and weak-cooling/full-profile results were not newly rerun.

## Mechanical and physical work before manufacture

The main PCB remains 64 × 56 mm. The bottom board is 27 × 34 mm and the front board is 24 × 10 mm. Actual native-board exports replace both old amber PCB placeholders. The upper button is VOL+; the lower is VOL−. The front left mounting screw is above the OLED rear-component envelope, and the cap flange has clearance around its boss. The actual PCB's component mounting plane is accounted for in each Blender transform.

The front switch linkage has only about 0.055 mm nominal free clearance. Verify the B3U pretravel range, printed-part tolerances, cap return force and positive overtravel stop on a physical sample; CAD does not guarantee operation. Verify actual M2 heads/threads, light-pipe diffusion and the GH plugs/cable bends. The custom spring-probe fixture still needs registration/retention details. No claim of a completely qualified production mechanism is made.

Before ordering a production batch: assemble a fit sample with the actual holder/display/speaker/headers; measure button and slide-switch operation through the panel; test cable continuity and all RGB channels; verify UART boot and 100 switched-display cycles; measure continuous alarm battery sag, 3.3/5 V rails, switch-node ringing, sleep/standby current, closed-enclosure temperatures and ESP-NOW range; measure bedroom SPL/distortion and run real wake-up trials. Continue the existing [physical test log](../../../enclosures/bedroom-alarm/physical-test-log.csv). Its unrun rows remain unrun.

## Sources and reproduction

[Reproduction guide](../../../scripts/alarm/README.md), [integrated assembly](../../../enclosures/bedroom-alarm/pcb-revision/README.md). Component/interface choices follow [JST GH](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf), [Omron B3U](https://components.omron.com/eu-en/products/switches/B3U), [E-Switch EG1218](https://configured-product-images.s3.amazonaws.com/2D/specs/EG1218.pdf), [TI TPS63070 layout guidance](https://www.ti.com/lit/ds/symlink/tps63070.pdf) and [Espressif antenna guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html). The existing display/holder/speaker drawings remain in the v4.1 enclosure source package.
