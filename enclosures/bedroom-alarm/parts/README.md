# Current parts and fit evidence

This is the v4.1 register for the bedside alarm. The selected display is EastRising ER-OLEDM013-1W-I2C; the holder is MPD BH3AAW and the speaker candidate is Visaton FRS 5 X, 8 ohm. See [display changes](../DISPLAY-UPDATE.md) and the [full design review](../DESIGN-REVIEW.md).

- [parts-register.json](parts-register.json) is the curated source for 27 mechanical items, dimensional evidence and remaining work. Edit this source when part selections or verified measurements change.
- [mechanical-parts.csv](mechanical-parts.csv) is its convenient tabular export; regenerate with `python3 update_register.py`.
- [pcb-evidence.json](pcb-evidence.json) records the actual native PCB, four mounting holes, model provenance and all electrical references. Its `source_pcb` and component model paths are relative to the repository root.
- [pcb-components.csv](pcb-components.csv) contains 112 electrical references: 111 populated and R11 unpopulated.
- [fit-readiness.json](fit-readiness.json) deliberately remains **NOT READY**: 27 mechanical items and 111 populated references lack final purchased-part geometry sign-off.

Run `python3 check_fit_readiness.py` to check inventory coverage and current PCB hash; an unresolved register returns exit code 2. This does not mean a geometry test failed, and setting a readiness field to true requires supporting dimensional/physical evidence.

To refresh the native PCB inventory, run `collect_pcb.py` with KiCad's `pcbnew` Python environment. The reader checks existing component model provenance hashes; it does not silently accept changed models. Refresh `sources/current-pcb.glb` and rerun the Blender build/verifier separately after an actual board revision.

All enclosure dimensions are millimetres. A drawing-based envelope, rendered part or nominal gap is not final part qualification. Continue the [physical test register](../physical-test-log.csv) when samples and measurements are available.
