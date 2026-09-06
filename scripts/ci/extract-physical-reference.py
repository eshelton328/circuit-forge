#!/usr/bin/env python3
"""Restore the frozen comparison PCB without relying on pre-squash Git history."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def extract_reference(board: Path, output: Path) -> str:
    report = json.loads((board / "review/physical-validation/summary.json").read_text())
    expected = report["manifest"]["reference_pcb_sha256"]
    data = gzip.decompress((board / "analysis/reference/pre-compaction.kicad_pcb.gz").read_bytes())
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise ValueError(f"Comparison PCB hash mismatch: expected {expected}, got {actual}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    return actual


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    digest = extract_reference(args.board, args.output)
    print(f"Restored comparison PCB: {args.output} (SHA-256 {digest})")
