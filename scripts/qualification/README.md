# Free operating-envelope and bench-validation tools

These tools supplement the archived physical screening in `scripts/physics`.
They record proposals and source sensitivities, never hardware qualification.
The user's three-AA requirement and pending inputs live in
`boards/esp32s3-devkit-5v/analysis/operating-requirements.json`.
The lithium sweep conditionally assumes 1.5 V primary Li/FeS2 cells.

Use the same Python virtual environment as the physical-screening suite.
`power_budget.py`, `battery_sweep.py` and `check_evidence.py` use the standard
library; the PCB thermal run also uses the free SciPy/Shapely stack.

```sh
python3 -m pytest tests/test_operating_envelope.py -v
python3 scripts/qualification/battery_sweep.py --output output/operating-envelope
python3 scripts/qualification/run_envelope.py \
  --geometry output/physical-screening/current.json \
  --pcb boards/esp32s3-devkit-5v/esp32s3-devkit-5v.kicad_pcb \
  --config boards/esp32s3-devkit-5v/analysis/operating-envelope.json \
  --output output/operating-envelope
python3 scripts/qualification/check_evidence.py
```

Export geometry using the KiCad command in the physical-screening runbook.
The supplement archive includes the actual geometry used. The thermal runner
verifies the PCB hash and writes all scenario fields, a fine moderate-load
mesh check, a controlled Q1 loss comparison and provenance. Its original
proposal snapshot predates the three-AA clarification and deliberately stays
separate from the chemistry-specific battery sweep.

To repeat the finer C3 extraction:

```sh
python3 scripts/physics/extract_loops.py output/physical-screening/current.json \
  output/mesh-c3-010 --fasthenry .cache/fasthenry/fasthenry-3.0wr/bin/fasthenry \
  --pitch 0.1 --nhinc 1 --cap C3
```

Use the pinned patched FastHenry build from `scripts/physics/install_fasthenry.sh`.
Keep failed or incomplete attempts in the evidence; they cannot count as passes.
Do not loosen the original mesh gate or infer all-loop convergence from C3 alone.

For hardware, follow `review/physical-validation/bench-plan.md` under the board.
`bench-measurements.csv` is intentionally headers only: no physical readings
have been taken. Keep waveform captures and instrument settings alongside it.
The proposed 1.6 A continuous design margin, 85 C PCB investigation threshold,
105 C TPS63070 junction estimate plus uncertainty target, and thermal settling
criterion are engineering proposals, not user-confirmed operating limits or
manufacturer guarantees. No purchased instrument or paid software was used for
the calculations; actual temperature and ringing claims require appropriate
measurement access.
