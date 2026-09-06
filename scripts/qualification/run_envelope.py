#!/usr/bin/env python3
"""Evaluate declared operating proposals using the existing PCB thermal solver."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts/physics'))
from thermal import solve_thermal
from power_budget import budget
import numpy as np


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(geometry, pcb, config, out):
    data = json.loads(geometry.read_text())
    cfg = json.loads(config.read_text())
    if data['pcb_sha256'] != digest(pcb):
        raise ValueError('Geometry is stale: PCB changed')
    out.mkdir(parents=True, exist_ok=True)
    sources = [*Path(__file__).parent.glob('*.py'),
               ROOT/'scripts/physics/thermal.py', ROOT/'scripts/physics/copper.py']
    manifest = {'pcb_sha256': digest(pcb), 'geometry_sha256': digest(geometry),
                'config_sha256': digest(config),
                'source_hashes': {str(p.relative_to(ROOT)): digest(p) for p in sources},
                'physical_release_approved': False}
    rows = []
    for case in cfg['cases']:
        result = budget(case, cfg['assumptions'])
        result['thermal'] = []
        if result['supply'] is not None:
            for h in cfg['thermal']['h_each_face_w_m2k']:
                r, grid, xy = solve_thermal(data, cfg['thermal']['pitch_mm'], h, result['sources'])
                r['peak_pcb_c'] = r['peak_pcb_rise_c']+cfg['thermal']['local_air_c']
                r['local_air_c'] = cfg['thermal']['local_air_c']
                r['below_proposed_pcb_investigation_threshold'] = r['peak_pcb_c'] < cfg['thermal']['proposed_pcb_investigation_threshold_c']
                result['thermal'].append(r)
                np.savez_compressed(out/f'{case["name"]}-h{h}.npz', rise_c=grid, x=xy[0], y=xy[1])
                print(case['name'], h, round(r['peak_pcb_c'], 2), flush=True)
        rows.append(result)
    # Isolate the missed Q1 source in the ORIGINAL loss budget. Use the same
    # seven package landing nodes in both cases so only heat input changes.
    legacy = json.loads((ROOT/'boards/esp32s3-devkit-5v/analysis/assumptions.json').read_text())
    from run_screening import heat_sources
    from power_budget import supply_point
    old_sources = heat_sources(legacy, .85)
    supply = supply_point(4.65/.85, 3.6, .33)
    q1_loss = supply['current_a']**2*.13
    correction = []
    for q in (0., q1_loss):
        s = {**old_sources, 'Q1': {'watts': q}}
        r, _, _ = solve_thermal(data, .5, 10, s)
        correction.append({'q1_w': q, 'result': r})
    manifest['legacy_config_sha256'] = digest(ROOT/'boards/esp32s3-devkit-5v/analysis/assumptions.json')
    # Mesh check for the moderate case, on the same seven-source model.
    moderate = next(r for r in rows if r['inputs']['name'] == 'moderate')
    coarse = next(r for r in moderate['thermal'] if r['h_w_m2k_each_face'] == 10)
    fine, _, _ = solve_thermal(data, .25, 10, moderate['sources'])
    change = abs(coarse['peak_pcb_rise_c']-fine['peak_pcb_rise_c'])/fine['peak_pcb_rise_c']
    output = {'manifest': manifest, 'cases': rows, 'legacy_q1_sensitivity': correction,
              'mesh_check_moderate_h10': {'fine': fine, 'relative_peak_change': change, 'passed_5pct': change < .05},
              'unresolved': list(cfg['confirmed_requirements']),
              'scope': 'Steady-state scenarios only. Numerical thresholds do not approve product operating ratings.'}
    (out/'results.json').write_text(json.dumps(output, indent=2, allow_nan=False)+'\n')
    with (out/'results.csv').open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['case', 'source_v', 'rail_3v3_a', 'audio_w', 'battery_a', 'protected_v', 'Q1_w', 'pcb_heat_w', 'h_each_face', 'local_air_c', 'peak_pcb_c'])
        for r in rows:
            for t in r['thermal']:
                writer.writerow([r['inputs'][k] for k in ('name', 'source_v', 'rail_3v3_a', 'audio_w')]+[r['supply']['current_a'], r['supply']['protected_v'], r['sources']['Q1']['watts'], r['board_heat_w'], t['h_w_m2k_each_face'], t['local_air_c'], t['peak_pcb_c']])
    return output


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('geometry', 'pcb', 'config', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    run(a.geometry, a.pcb, a.config, a.output)
