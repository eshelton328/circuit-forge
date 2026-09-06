#!/usr/bin/env python3
"""Three-AA source sensitivity; no battery lifetime or startup certification."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from power_budget import budget

ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT/'boards/esp32s3-devkit-5v'


def run(out):
    paths = [BOARD/'analysis/operating-envelope.json', BOARD/'analysis/aa-battery-scenarios.json',
             BOARD/'analysis/operating-requirements.json', Path(__file__), Path(__file__).with_name('power_budget.py')]
    base, batteries = [json.loads(p.read_text()) for p in paths[:2]]
    rows = []
    for battery in batteries['cases']:
        a = {**base['assumptions'], 'external_series_ohm': 3*battery['cell_ohm']+batteries['holder_and_wire_ohm']}
        for case in base['cases'][:3]:
            r = budget({**case, 'source_v': battery['source_v']}, a)
            r['battery_case'] = battery
            rows.append(r)
    out.mkdir(parents=True, exist_ok=True)
    result = {'input_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
              'physical_release_approved': False, 'scope': batteries['scope'], 'cases': rows}
    (out/'aa-battery-results.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    with (out/'aa-battery-results.csv').open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['battery_case','load_case','source_v','series_ohm_including_q1','battery_a','protected_v','q1_w','external_series_heat_w','loaded_v_at_least_3','below_2a','status'])
        for r in rows:
            s = r['supply']
            writer.writerow([r['battery_case']['name'],r['inputs']['name'],r['inputs']['source_v'],r['assumptions']['external_series_ohm']+r['assumptions']['q1_ohm'],
                             s['current_a'] if s else '',s['protected_v'] if s else '',r.get('sources',{}).get('Q1',{}).get('watts',''),
                             r.get('external_series_heat_w',''),r.get('protected_at_least_3v',''),r.get('connector_below_2a',''),r['status']])
    print(f'{len(rows)} three-AA source cases computed; no physical approval.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
