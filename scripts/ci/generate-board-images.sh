#!/usr/bin/env bash
# Generate documentation images for a single board using kicad-cli.
#
# Outputs (written to boards/<name>/docs/):
#   schematic.svg          — full schematic (multi-page → one SVG per page)
#   schematic.pdf          — downloadable multi-page schematic
#   assembly.glb           — downloadable populated 3D board model
#   pcb-top.png            — PCB top side with silkscreen (high-quality 3D render)
#   pcb-bottom.png         — PCB bottom side with silkscreen (high-quality 3D render)
#
# Usage:  bash scripts/ci/generate-board-images.sh boards/<name>
# Expects kicad-cli on PATH (run inside the KiCad Docker image in CI).
#
# 3D models: set KICAD10_3DMODEL_DIR (and optionally KICAD9_3DMODEL_DIR) to the
# downloaded package3D cache. Repo-local STEP files can use ${KIPRJMOD}/../../libs/...
# so they resolve in Docker with -w /workspace.

set -euo pipefail

BOARD_DIR="${1:?Usage: $0 <board-directory>}"
BOARD_NAME=$(basename "$BOARD_DIR")
SCH_FILE="$BOARD_DIR/$BOARD_NAME.kicad_sch"
PCB_FILE="$BOARD_DIR/$BOARD_NAME.kicad_pcb"
DOCS_DIR="$BOARD_DIR/docs"

mkdir -p "$DOCS_DIR"

# ── Schematic SVG ─────────────────────────────────────────────────────
if [ -f "$SCH_FILE" ]; then
  echo "Exporting schematic SVG..."
  SCH_TMP=$(mktemp -d)
  trap 'rm -rf "$SCH_TMP"' EXIT
  kicad-cli sch export svg \
    --output "$SCH_TMP" \
    --exclude-drawing-sheet \
    "$SCH_FILE"

  # A child such as board-Power.svg sorts before board.svg. Select the root
  # explicitly so schematic.svg always shows the main sheet.
  ROOT_SVG="$SCH_TMP/$BOARD_NAME.svg"
  if [ ! -s "$ROOT_SVG" ]; then
    echo "Expected root schematic export missing: $ROOT_SVG" >&2
    exit 1
  fi
  cp "$ROOT_SVG" "$DOCS_DIR/schematic.svg"
  # Retired sheets must not remain embedded after the hierarchy shrinks.
  rm -f "$DOCS_DIR"/schematic-page*.svg
  page=1
  for svg in "$SCH_TMP"/*.svg; do
    [ -f "$svg" ] || continue
    [ "$svg" = "$ROOT_SVG" ] && continue
    cp "$svg" "$DOCS_DIR/schematic-page${page}.svg"
    page=$((page + 1))
  done
  rm -rf "$SCH_TMP"
  echo "  → schematic.svg ($page page(s))"
  kicad-cli sch export pdf --output "$DOCS_DIR/schematic.pdf" "$SCH_FILE"
else
  echo "No schematic found at $SCH_FILE — skipping."
fi

# ── PCB top/bottom renders ───────────────────────────────────────────
# Leave room for components that overhang the board outline (e.g. an antenna).
if [ -f "$PCB_FILE" ]; then
  echo "Exporting populated 3D model..."
  kicad-cli pcb export glb \
    --force --no-dnp --subst-models --include-pads --include-silkscreen \
    --output "$DOCS_DIR/assembly.glb" "$PCB_FILE"

  echo "Rendering PCB top..."
  kicad-cli pcb render \
    --output "$DOCS_DIR/pcb-top.png" \
    --side top \
    --background transparent \
    --width 1600 --height 1200 \
    --zoom 0.85 \
    --quality high \
    "$PCB_FILE"
  echo "  → pcb-top.png"

  echo "Rendering PCB bottom..."
  kicad-cli pcb render \
    --output "$DOCS_DIR/pcb-bottom.png" \
    --side bottom \
    --background transparent \
    --width 1600 --height 1200 \
    --zoom 0.85 \
    --quality high \
    "$PCB_FILE"
  echo "  → pcb-bottom.png"
else
  echo "No PCB found at $PCB_FILE — skipping."
fi

echo "Done: $DOCS_DIR"
ls -lh "$DOCS_DIR"
