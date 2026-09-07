# Rebuild and verify ALEC Sensor S1

Run from the repository root. Free tools: KiCad 10.0.x with its `pcbnew` Python, ngspice, a C++ compiler and NumPy; CadQuery 2.8.0 and Blender 5.2.1 LTS for the enclosure. The committed native PCB is the reviewed routed result. Generators overwrite their output: use a clean branch and inspect the diff before accepting regeneration.

On macOS, use the bundled KiCad Python and CLI:

```sh
export PATH="/Applications/KiCad/KiCad.app/Contents/MacOS:$PATH"
KICAD_PYTHON=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
```

On Linux, install KiCad 10 plus `python3-pcbnew`, or use the pinned KiCad Docker image in the sensor workflow; set `KICAD_PYTHON=python3`. The creation scripts use the existing repository `scripts/alarm/design.py` KiCad library discovery and require wxPython. Use a desktop session or `xvfb-run` for `create_pcb.py` on headless Linux.

## Verify the delivered sources

```sh
kicad-cli sch export netlist --format kicadxml -o boards/alec-sensor/review/netlist.xml boards/alec-sensor/alec-sensor.kicad_sch
kicad-cli sch erc --exit-code-violations --format json -o boards/alec-sensor/review/erc.json boards/alec-sensor/alec-sensor.kicad_sch
kicad-cli pcb drc --exit-code-violations --refill-zones --save-board --schematic-parity --format json -o boards/alec-sensor/review/drc.json boards/alec-sensor/alec-sensor.kicad_pcb
"$KICAD_PYTHON" scripts/ci/check_copper_connectivity.py boards/alec-sensor
python3 boards/alec-sensor/tools/check_design.py
python3 boards/alec-sensor/tools/check_service_interface.py
"$KICAD_PYTHON" boards/alec-sensor/tools/check_layout.py
"$KICAD_PYTHON" boards/alec-sensor/tools/audit_models.py
bash scripts/run-drc-all-fabs.sh boards/alec-sensor
python3 boards/alec-sensor/tools/power_budget.py
python3 boards/alec-sensor/tools/power_screening.py
python3 -m pytest tests/
bash scripts/ci/generate-board-images.sh boards/alec-sensor
python3 scripts/ci/update-board-readmes.py
```

The input SPICE cases are passive contact-closure RLC screens. They deliberately do not claim converter-loop stability, switch-node ringing, EMI or thermal qualification. Raw decks, logs and assumptions are in `review/power-screening/`; results and physical acceptance work are in [TEST-REPORT.md](../TEST-REPORT.md).

## Regenerate schematic and routing

`create_schematic.py` derives the reusable sections from `esp32s3-devkit-5v`, applies the independent sensor pin contract and explicit candidate parts from `parts.py`. Export its netlist before creating the PCB. Regeneration intentionally depends on that source board; review changes there before updating this sensor.

```sh
python3 boards/alec-sensor/tools/create_schematic.py
kicad-cli sch export netlist --format kicadxml -o boards/alec-sensor/review/netlist.xml boards/alec-sensor/alec-sensor.kicad_sch
"$KICAD_PYTHON" boards/alec-sensor/tools/create_pcb.py
"$KICAD_PYTHON" boards/alec-sensor/tools/clean_retired_copper.py --initial
c++ -O3 -shared -fPIC boards/esp32s3-devkit-5v/tools/grid_search.cpp -o /tmp/alec-grid-search.so
export ALARM_GRID_LIBRARY=/tmp/alec-grid-search.so
"$KICAD_PYTHON" boards/alec-sensor/tools/route_pcb.py
"$KICAD_PYTHON" boards/alec-sensor/tools/finish_pcb.py
"$KICAD_PYTHON" boards/alec-sensor/tools/clean_retired_copper.py
```

Then repeat every verification above. Routing is a geometric construction step, not an electrical signoff. `clean_retired_copper.py --initial` only belongs to the initial migration before routing; it refuses to cut a collision inside the reviewed switching-cell region. Do not use it to conceal a final routing error. `apply_rear_service.py` migrates an existing S1 layout to the rear-control positions from `interface.json`; follow it with the initial cleanup, routing, final cleanup and all verification above. `sync_fields.py` updates BOM metadata on an existing board without rerouting.

## Mechanical models and evidence

In a CadQuery 2.8.0 environment, `build_part_models.py` generates the drawing-based switch and socket STEP envelopes. The other model sources are in [3dmodels/README.md](../3dmodels/README.md).

```sh
python boards/alec-sensor/tools/build_part_models.py
python enclosures/alec-sensor/tools/build_cad.py
blender -b --python enclosures/alec-sensor/tools/build_blender.py
```

Regenerate the board GLB before Blender. The enclosure imports actual populated PCB geometry and the vendor-derived holder/radar meshes. `interface.json` controls the nominal stack; `check_layout.py` also verifies its PCB mount, radar, LED, external button and rear service-control coordinates. `build_cad.py` tests 19 explicit solid/approach intersections, not all package/tolerance combinations. The STEP is the geometry authority; rendered colors and harness/retention allocations are illustrative.

After validating and rendering a release candidate, run `python3 boards/alec-sensor/tools/hash_evidence.py` to bind the native sources and reports. The manifest excludes itself to avoid a hash cycle. Re-running tools may change export timestamps and identifiers; compare electrical/geometry results, not just byte identity.
