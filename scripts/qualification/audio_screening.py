#!/usr/bin/env python3
"""Continuous-alarm proposals: source budget, PCB heat and acoustic arithmetic."""
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
from power_budget import budget

ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT/'boards/esp32s3-devkit-5v'


def acoustic_estimate(sensitivity_db, watts, metres):
    """Ideal far-field scaling only; not a measured alarm SPL or dBA rating."""
    if not all(math.isfinite(x) for x in (sensitivity_db, watts, metres)) or watts <= 0 or metres <= 0:
        raise ValueError('Finite values, positive power and positive distance required')
    return sensitivity_db + 10*math.log10(watts) - 20*math.log10(metres)


def sine_drive(watts, ohms, gain_db=12., dac_dbv=2.1):
    """Requested pre-clipping sine level into nominal resistance, not a limiter."""
    if not all(math.isfinite(x) for x in (watts, ohms, gain_db, dac_dbv)) or watts <= 0 or ohms <= 0:
        raise ValueError('Finite values, positive power and positive impedance required')
    vrms = math.sqrt(watts*ohms)
    dbfs = 20*math.log10(vrms)-gain_db-dac_dbv
    return {'audio_w': watts, 'ohms': ohms, 'vrms': vrms,
            'vpeak_sine': math.sqrt(2)*vrms, 'requested_sine_dbfs': dbfs,
            'digital_peak_fraction_of_full_scale': 10**(dbfs/20)}


def run(geometry, out):
    sys.path.insert(0, str(ROOT/'scripts/physics'))
    from thermal import solve_thermal
    import numpy as np
    config_paths = [BOARD/'analysis/audio-load-proposals.json',
                    BOARD/'analysis/operating-envelope.json',
                    BOARD/'analysis/aa-battery-scenarios.json',
                    BOARD/'analysis/operating-requirements.json']
    cfg, base, bat, _ = [json.loads(p.read_text()) for p in config_paths]
    data = json.loads(geometry.read_text())
    pcb = BOARD/'esp32s3-devkit-5v.kicad_pcb'
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if data['pcb_sha256'] != digest(pcb):
        raise ValueError('Stale PCB geometry')
    files = [*config_paths, pcb, Path(__file__), Path(__file__).with_name('power_budget.py'),
             ROOT/'scripts/physics/thermal.py', ROOT/'scripts/physics/copper.py']
    manifest = {'input_hashes': {str(p.relative_to(ROOT)): digest(p) for p in files},
                'geometry_sha256': digest(geometry), 'physical_release_approved': False}
    rows = []
    sweep = cfg['battery_sweep']
    for b, current, audio, eta in itertools.product(bat['cases'], sweep['rail_3v3_a'], sweep['audio_w'], sweep['incremental_amp_efficiency']):
        assumptions = {**base['assumptions'], 'eta_audio': eta,
                       'external_series_ohm': 3*b['cell_ohm']+bat['holder_and_wire_ohm']}
        case = {'name': b['name'], 'source_v': b['source_v'], 'rail_3v3_a': current,
                'audio_w': audio, 'offboard_3v3_w': 0}
        rows.append(budget(case, assumptions))
    thermal = []
    out.mkdir(parents=True, exist_ok=True)
    for case in cfg['thermal_cases']:
        assumptions = {**base['assumptions'], 'eta_audio': cfg['thermal']['incremental_amp_efficiency'],
                       'external_series_ohm': cfg['thermal']['external_series_ohm']}
        result = budget(case, assumptions)
        if result['supply'] is None:
            raise ValueError('Selected thermal case has no supply solution')
        for h in cfg['thermal']['h_each_face_w_m2k']:
            t, grid, xy = solve_thermal(data, cfg['thermal']['pitch_mm'], h, result['sources'])
            if t['energy_relative_error'] > 1e-6:
                raise ValueError('Thermal energy conservation failed')
            t['local_air_c'] = cfg['thermal']['local_air_c']
            t['peak_pcb_c'] = t['peak_pcb_rise_c']+t['local_air_c']
            thermal.append({'case': result, 'thermal': t})
            np.savez_compressed(out/f'{case["name"]}-h{h}.npz', rise_c=grid, x=xy[0], y=xy[1])
            print(case['name'], 'h=', h, 'peak PCB C=', round(t['peak_pcb_c'], 2), flush=True)
    sensitivity = cfg['recommended_starting_point']['candidate_sensitivity_db_1w_1m']
    compact_rows = [{'inputs': r['inputs'], 'amp_eta': r['assumptions']['eta_audio'],
                     'supply': r['supply'], 'pcb_heat_w': r.get('board_heat_w'),
                     'q1_w': r.get('sources', {}).get('Q1', {}).get('watts'),
                     'status': r['status']} for r in rows]
    result = {'manifest': manifest, 'battery_cases': compact_rows, 'thermal_cases': thermal,
              'sine_settings': [sine_drive(p, 8) for p in (.5, 1., 1.4)],
              'ideal_acoustic_scaling': [{'watts': p, 'metres': d, 'db_spl_estimate': acoustic_estimate(sensitivity, p, d)} for p, d in itertools.product((.5, 1., 1.4), (1, 3, 5))],
              'scope': 'Continuous-load scenarios, not measured acoustic output, safe operating limits, runtime or junction temperature. Lithium assumes primary 1.5 V AA pending confirmation.'}
    (out/'audio-results.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    with (out/'audio-battery-results.csv').open('w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(['battery_case','rail_3v3_a','audio_w','amp_eta','battery_a','protected_v','pcb_heat_w','status'])
        for r in rows:
            s = r['supply']
            writer.writerow([r['inputs']['name'],r['inputs']['rail_3v3_a'],r['inputs']['audio_w'],r['assumptions']['eta_audio'],s['current_a'] if s else '',s['protected_v'] if s else '',r.get('board_heat_w',''),r['status']])
    print(len(rows), 'source cases; six thermal cases; no physical qualification.', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--geometry', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    run(a.geometry, a.output)
