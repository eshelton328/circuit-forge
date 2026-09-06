"""Independent energy and source-collapse checks, requiring no paid tools."""
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/qualification'))
from power_budget import budget, supply_point


def proposal():
    return json.loads((ROOT/'boards/esp32s3-devkit-5v/analysis/operating-envelope.json').read_text())


def test_supply_matches_known_resistor_operating_point():
    # I=1 A, Voc=4 V, R=0.5 ohm -> Vload=3.5 V, Pload=3.5 W.
    assert supply_point(3.5, 4, .5) == {'current_a': 1., 'protected_v': 3.5}


def test_supply_zero_resistance_and_zero_load():
    assert supply_point(6, 3, 0) == {'current_a': 2., 'protected_v': 3.}
    assert supply_point(0, 3, .2) == {'current_a': 0., 'protected_v': 3.}


def test_supply_collapse_cannot_return_a_passing_point():
    assert supply_point(9, 3, 1) is None
    assert supply_point(2.25, 3, 1) is None  # maximum-power nose is not accepted


def test_total_power_conserved_including_speaker_and_q1():
    cfg = proposal()
    for case in cfg['cases']:
        r = budget(case, cfg['assumptions'])
        assert abs(r['energy_balance_error_w']) < 1e-12
        assert r['sources']['Q1']['watts'] > 0
        assert r['physical_release_approved'] is False


def test_offboard_power_reduces_board_heat_without_changing_input():
    cfg = proposal(); case = cfg['cases'][1]
    a = budget(case, cfg['assumptions'])
    b = budget({**case, 'offboard_3v3_w': .3}, cfg['assumptions'])
    assert a['supply'] == b['supply']
    assert a['board_heat_w']-b['board_heat_w'] == pytest.approx(.3)


def test_audio_output_is_not_all_counted_as_pcb_heat():
    cfg = proposal(); case = cfg['cases'][1]
    a = budget(case, {**cfg['assumptions'], 'eta_audio': 1., 'amp_idle_w': 0.})
    assert a['sources']['U6']['watts'] == 0


def test_battery_sag_increases_current_and_q1_heating():
    cfg = proposal(); case = cfg['cases'][1]
    a = budget(case, {**cfg['assumptions'], 'external_series_ohm': 0.})
    b = budget(case, cfg['assumptions'])
    assert b['supply']['current_a'] > a['supply']['current_a']
    assert b['sources']['Q1']['watts'] > a['sources']['Q1']['watts']


@pytest.mark.parametrize('change', [{'eta_audio': 0}, {'eta_5v': 1.1}, {'q1_ohm': -1}, {'q1_ohm': float('nan')}])
def test_invalid_assumptions_rejected(change):
    cfg = proposal()
    with pytest.raises(ValueError):
        budget(cfg['cases'][0], {**cfg['assumptions'], **change})


def test_offboard_power_cannot_exceed_the_rail_budget():
    cfg = proposal()
    with pytest.raises(ValueError, match='Off-board power'):
        budget({**cfg['cases'][0], 'offboard_3v3_w': 100}, cfg['assumptions'])
