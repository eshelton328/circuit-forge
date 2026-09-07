# The Forge

Hardware design monorepo for KiCad PCB projects with automated CI/CD.

## Repository Structure

```
the-forge/
├── Makefile          # make check / erc / drc / fab-drc
├── boards/           # Individual board projects
├── designs/          # Schematic studies before PCB layout
├── enclosures/       # Product packaging, Blender models and fit evidence
├── fab-rules/        # DRC rule templates per fab house
├── kibot/            # KiBot output generation configs
├── libs/             # Shared libraries (symbols, footprints, 3D models)
├── scripts/          # Automation scripts
├── emi/              # openEMS + gerber2ems (FDTD / EMI-adjacent smoke; see emi/README.md)
└── .github/workflows # CI/CD pipelines
```

## Boards

<!-- board-catalog-start -->
| Board | Description | Layers |
|---|---|---:|
| [alec-controls](boards/alec-controls/README.md) | ALEC bottom controls with three settings buttons and hardware enable switch | 2 |
| [alec-front](boards/alec-front/README.md) | ALEC exterior battery-check button and RGB LED | 2 |
| [alec-main](boards/alec-main/README.md) | ALEC main board with ESP32-S3, dual TPS63070 rails, audio and remote controls | 4 |
| [esp32s3-devkit](boards/esp32s3-devkit/README.md) | ESP32-S3-WROOM-1 development board with TPS63070 buck-boost and USB-C | 4 |
| [esp32s3-devkit-5v](boards/esp32s3-devkit-5v/README.md) | ESP32-S3-WROOM-1 dev board with dual TPS63070 rails (3.3V + 5V), USB-C | 4 |
| [tps63070-breakout](boards/tps63070-breakout/README.md) | TPS63070 3.3V buck-boost breakout board | 2 |
<!-- board-catalog-end -->

Each board README includes schematic previews, a downloadable schematic PDF, top/bottom 3D renders and a populated GLB model. The board catalog and these assets are updated automatically after merges to `main`.

The **ALEC** alarm uses `alec-main`, `alec-controls` and `alec-front` together. The main board carries the ESP32-S3, dual power converters and audio circuit; the two smaller boards carry the protected settings controls and exterior battery-check button/RGB LED. These are engineering prototypes with physical qualification pending. See the [full PCB and enclosure test report](boards/alec-main/review/TEST-REPORT.md).

## Designs in development

| Design | Stage |
|---|---|
| [alec-sensor](designs/alec-sensor/) | Shower presence companion: initial three-sheet schematic, power/sleep contract and sealed-enclosure concept; PCB and physical qualification pending |

## Enclosures

| Enclosure | Board | Status |
|---|---|---|
| [ALEC v4.2](enclosures/alec/pcb-revision/) | alec-main, alec-controls, alec-front | Integrated PCB prototype: 105 mm cube, four perforated walls, 1.3-inch OLED and three AA cells; physical tests pending |
| [ALEC v4.1 reference](enclosures/alec/) | esp32s3-devkit-5v | Earlier packaging reference with the bench board |

The enclosure project includes editable Blender scenes, inline preview images, dimensional sources, a parts register and a reproducible test report. Open its README to download the models and review the current fit limits.

## CI/CD Pipeline

Every pull request automatically runs:
- **PR title** must follow [Conventional Commits](https://www.conventionalcommits.org/) (e.g. `feat:`, `fix:`, `chore:`, `ci:`)
- **`pytest`** on `tests/` (Python **3.12**; see [`.github/workflows/pytest.yml`](.github/workflows/pytest.yml) — Spice integration cases skip unless `ngspice`/Docker exist)
- **Open-source EMS (openEMS + gerber2ems)** — optional path-filtered workflow ([`.github/workflows/emi-checks.yml`](.github/workflows/emi-checks.yml)): builds pinned **openEMS** + **gerber2ems** and runs an upstream example slice ([`emi/README.md`](emi/README.md)); not every PR
- **ERC** (Electrical Rules Check) on schematics
- **DRC** (Design Rules Check) against multiple fab house rules (JLCPCB, PCBWay)

The KiCad workflow always runs, but it only **executes** ERC/DRC for boards that are in scope: changes under `boards/<name>/` check only those boards, while changes to `libs/`, `fab-rules/`, `kibot/`, `scripts/`, the root `Makefile`, or `.github/workflows/pr-checks.yml` trigger checks on all boards. Doc-only diffs (e.g. just `README.md`) skip the heavy KiCad jobs to save time. **`pytest`** (see **`pytest.yml`**) runs on every PR regardless, so Python regressions cannot slip through doc-only merges.

On release tags, the pipeline generates:
- Fab-ready Gerber/drill ZIPs per fab house
- BOM and component placement files
- Schematic PDFs and board renders

## Local Development

### Prerequisites

```bash
brew install --cask kicad    # KiCad 10 (includes kicad-cli)
pip install kibot kikit       # Automation tools
```

### Running checks locally

From the repository root, the **Makefile** is the usual entry point. **Each command checks one board** — the one named by `BOARD` (default: `esp32s3-devkit`). Nothing scans every board unless you ask for that explicitly.

```bash
make help           # list targets
make list-boards    # show board folder names you can pass as BOARD=...

# Default single board (esp32s3-devkit)
make check
make drc

# A different board — either form (folder and .kicad_* basename must match)
make drc BOARD=other-board
make drc other-board
make check other-board

# Optional: run make check for every board under boards/ (e.g. before a release)
make check-all
```

`kicad-cli` is picked up from your `PATH` if present; on macOS it falls back to
`/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`. Override with
`KICAD_CLI=/path/to/kicad-cli make check`.

### Python tests (pytest)

```bash
pip install -r requirements.txt
python3 -m pytest tests/
```

With **`ngspice`** and **Docker** available, `tests/test_spice_run_sim_integration.py` runs end-to-end Spice smoke; otherwise those cases are **skipped** (same as default CI for `pytest.yml`).

**SPICE / simulation (boards with `sim.yml`):** CI builds [`sim/docker/Dockerfile`](sim/docker/Dockerfile) — same KiCad digest as ERC/DRC plus pinned **ngspice** and the repo **`requirements.txt`** — and runs export + `run_sim.py` inside that image ([`sim/README.md`](sim/README.md)). Local parity: **`make sim-board-docker BOARD=tps63070-breakout`** or **`scripts/sim/run-spice-in-docker.sh --board …`**.

Raw commands (equivalent to the Makefile):

```bash
kicad-cli sch erc --exit-code-violations --format json -o boards/esp32s3-devkit/erc.json \
  boards/esp32s3-devkit/esp32s3-devkit.kicad_sch

kicad-cli pcb drc --exit-code-violations --refill-zones --schematic-parity --format json \
  -o boards/esp32s3-devkit/drc-default.json boards/esp32s3-devkit/esp32s3-devkit.kicad_pcb

./scripts/run-drc-all-fabs.sh boards/esp32s3-devkit
```

### Adding a new board

1. Create a new directory under `boards/`
2. Add a `board.yml` with layer count and fab targets
3. If using shared libraries, create project-local `fp-lib-table` / `sym-lib-table` pointing to `../../libs/`
4. Generate the initial schematic and model downloads with `bash scripts/ci/generate-board-images.sh boards/<name>` (`kicad-cli` must be on `PATH`), then run `python3 scripts/ci/update-board-readmes.py` to refresh the gallery and root catalog. Commit the generated `docs/` assets with the board.
5. Push a PR -- CI will automatically run checks; merge automation refreshes the galleries and catalog again.

## Fab House Rules

DRC rules for each fab house are stored in `fab-rules/` as `.kicad_dru` files. CI swaps these in and runs DRC to tell you which fabs your design is compatible with.

2-layer and 4-layer rules each come in two tiers where noted: **standard** (baseline process) vs **advanced** (tighter vias/clearances, typically higher cost). Each board declares which rule keys it runs in `board.yml`.

| Fab House | Rule File | Notes |
|-----------|-----------|-------|
| JLCPCB 2L Standard | `jlcpcb-2layer-standard.kicad_dru` | 0.3mm via drill, 0.15mm annular ring |
| JLCPCB 2L Advanced | `jlcpcb-2layer-advanced.kicad_dru` | 0.2mm via drill, 0.1mm annular ring |
| JLCPCB 4L Standard | `jlcpcb-4layer.kicad_dru` | |
| JLCPCB 4L Advanced | `jlcpcb-4layer-advanced.kicad_dru` | Tighter annular / hole clearance / pad-track clearance vs standard 4L |
| PCBWay 2L Standard | `pcbway-2layer-standard.kicad_dru` | 0.3mm via drill, 0.45mm via pad |
| PCBWay 2L Advanced | `pcbway-2layer-advanced.kicad_dru` | 0.2mm via drill, 0.35mm via pad |
| PCBWay 4L Standard | `pcbway-4layer.kicad_dru` | |
| PCBWay 4L Advanced | `pcbway-4layer-advanced.kicad_dru` | 0.2mm via drill, 0.35mm via pad vs standard 4L |
