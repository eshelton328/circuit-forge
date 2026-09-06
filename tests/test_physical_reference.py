"""The comparison PCB must survive squash merges and reject damaged inputs."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "boards/esp32s3-devkit-5v"


@pytest.fixture
def isolated_reference(tmp_path):
    """Copy only the needed files: no Git metadata, refs or installed git command."""
    board = tmp_path / "board"
    for name in ("analysis/reference/pre-compaction.kicad_pcb.gz",
                 "review/physical-validation/summary.json"):
        dest = board / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(BOARD / name, dest)
    script = tmp_path / "extract.py"
    shutil.copyfile(ROOT / "scripts/ci/extract-physical-reference.py", script)
    output = tmp_path / "output/original.kicad_pcb"
    env = {**os.environ, "PATH": str(tmp_path / "no-executables")}

    def run():
        return subprocess.run(
            [sys.executable, str(script), "--board", str(board), "--output", str(output)],
            cwd=tmp_path, env=env, text=True, capture_output=True,
        )

    return board, output, run


def test_comparison_is_recoverable_without_git_history(isolated_reference):
    board, output, run = isolated_reference
    result = run()
    assert result.returncode == 0, result.stderr
    expected = json.loads((board / "review/physical-validation/summary.json").read_text())["manifest"]["reference_pcb_sha256"]
    assert hashlib.sha256(output.read_bytes()).hexdigest() == expected
    assert output.read_bytes().lstrip().startswith(b"(kicad_pcb")


def test_changed_reference_does_not_overwrite_existing_output(isolated_reference):
    board, output, run = isolated_reference
    archive = board / "analysis/reference/pre-compaction.kicad_pcb.gz"
    data = gzip.decompress(archive.read_bytes())
    archive.write_bytes(gzip.compress(data + b"\n", mtime=0))
    output.parent.mkdir()
    output.write_bytes(b"preserve previous output")
    result = run()
    assert result.returncode != 0
    assert "Comparison PCB hash mismatch" in result.stderr
    assert output.read_bytes() == b"preserve previous output"


def test_corrupt_archive_does_not_create_output(isolated_reference):
    board, output, run = isolated_reference
    (board / "analysis/reference/pre-compaction.kicad_pcb.gz").write_bytes(b"invalid gzip")
    result = run()
    assert result.returncode != 0
    assert not output.exists()
