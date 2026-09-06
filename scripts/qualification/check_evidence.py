#!/usr/bin/env python3
"""Reject stale proposal evidence; this is never physical release approval."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT/'boards/esp32s3-devkit-5v'


def check():
    report = json.loads((BOARD/'review/physical-validation/operating-envelope-results.json').read_text())
    manifest = report['manifest']
    expected = {
        'pcb_sha256': BOARD/'esp32s3-devkit-5v.kicad_pcb',
        'config_sha256': BOARD/'analysis/operating-envelope.json',
        'legacy_config_sha256': BOARD/'analysis/assumptions.json',
    }
    for key, path in expected.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != manifest[key]:
            raise ValueError(f'Stale operating envelope: {path.relative_to(ROOT)}')
    for name, value in manifest['source_hashes'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != value:
            raise ValueError(f'Stale numerical source: {name}')
    for name, value in report.get('supporting_source_hashes', {}).items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != value:
            raise ValueError(f'Stale supporting source: {name}')
    if manifest['physical_release_approved'] is not False:
        raise ValueError('A scenario calculator cannot grant physical approval')
    battery = json.loads((BOARD/'review/physical-validation/aa-battery-results.json').read_text())
    for name, value in battery['input_hashes'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != value:
            raise ValueError(f'Stale three-AA source evidence: {name}')
    if battery['physical_release_approved'] is not False:
        raise ValueError('A static battery model cannot grant physical approval')
    print('Operating proposal evidence matches PCB, configuration and numerical sources.')
    print('Requirements and physical measurements remain pending; no release approval.')


if __name__ == '__main__':
    check()
