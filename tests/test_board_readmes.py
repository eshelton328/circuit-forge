"""Regression coverage for the merge-time board gallery integration."""
import importlib.util
import os
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "update_board_readmes", ROOT / "scripts/ci/update-board-readmes.py"
)
readmes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readmes)


def test_missing_gallery_is_added_without_losing_handwritten_content(tmp_path):
    original = "# Custom board\n\nKeep the design notes and model links.\n"
    readme = tmp_path / "README.md"
    readme.write_text(original)
    docs = tmp_path / "docs"
    docs.mkdir()
    for name in ("schematic.svg", "schematic-page1.svg", "pcb-top.png", "pcb-bottom.png"):
        (docs / name).touch()

    assert readmes.update_readme(tmp_path)
    text = readme.read_text()
    assert text.startswith(original)
    for name in ("schematic.svg", "schematic-page1.svg", "pcb-top.png", "pcb-bottom.png"):
        assert f"(docs/{name})" in text
    assert "### PCB 3D Views" in text
    assert not readmes.update_readme(tmp_path)
    assert readme.read_text() == text


def test_existing_gallery_is_replaced_in_place(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/pcb-top.png").touch()
    readme = tmp_path / "README.md"
    readme.write_text(f"# Intro\n\n{readmes.IMG_START}\nstale\n{readmes.IMG_END}\n\nKeep this footer.\n")
    assert readmes.update_readme(tmp_path)
    text = readme.read_text()
    assert text.startswith("# Intro\n\n")
    assert text.endswith("\n\nKeep this footer.\n")
    assert "stale" not in text
    assert text.count(readmes.IMG_START) == 1
    assert "(docs/pcb-top.png)" in text
    assert "(docs/pcb-bottom.png)" not in text


@pytest.mark.parametrize("markers", [
    readmes.IMG_START,
    readmes.IMG_END,
    readmes.IMG_END + readmes.IMG_START,
    readmes.IMG_START + readmes.IMG_START + readmes.IMG_END,
])
def test_broken_markers_fail_without_overwriting_readme(tmp_path, markers):
    (tmp_path / "docs").mkdir()
    readme = tmp_path / "README.md"
    readme.write_text(markers)
    with pytest.raises(ValueError, match="Invalid README section markers"):
        readmes.update_readme(tmp_path)
    assert readme.read_text() == markers


def _export_with_fake_cli(tmp_path, *, omit_root=False):
    """Exercise the shell orchestration; this stub does not test KiCad rendering."""
    board = tmp_path / "board"
    board.mkdir()
    (board / "board.kicad_sch").touch()
    docs = board / "docs"
    docs.mkdir()
    (docs / "schematic.svg").write_text("previous root")
    (docs / "schematic-page9.svg").write_text("retired child")
    bindir = tmp_path / "bin"
    bindir.mkdir()
    cli = bindir / "kicad-cli"
    cli.write_text('''#!/usr/bin/env bash
set -eu
test "$1 $2 $3" = "sch export svg"
out="$5"
test "$4" = "--output"
if [ "${OMIT_ROOT:-0}" = 0 ]; then
  printf 'root sheet' > "$out/board.svg"
fi
printf 'child sheet' > "$out/board-Power.svg"
''')
    cli.chmod(0o755)
    result = subprocess.run(
        ["bash", str(ROOT / "scripts/ci/generate-board-images.sh"), str(board)],
        env={**os.environ, "PATH": str(bindir) + os.pathsep + os.environ["PATH"],
             "OMIT_ROOT": str(int(omit_root))},
        text=True, capture_output=True,
    )
    return result, docs


def test_schematic_export_puts_root_first_and_removes_retired_sheets(tmp_path):
    result, docs = _export_with_fake_cli(tmp_path)
    assert result.returncode == 0, result.stderr
    assert (docs / "schematic.svg").read_text() == "root sheet"
    assert (docs / "schematic-page1.svg").read_text() == "child sheet"
    assert not (docs / "schematic-page9.svg").exists()


def test_missing_root_export_fails_and_preserves_previous_images(tmp_path):
    result, docs = _export_with_fake_cli(tmp_path, omit_root=True)
    assert result.returncode != 0
    assert "Expected root schematic export missing" in result.stderr
    assert (docs / "schematic.svg").read_text() == "previous root"
    assert (docs / "schematic-page9.svg").read_text() == "retired child"
