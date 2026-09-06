"""Independent scaling/units controls; no speaker performance is asserted."""
from pathlib import Path
import sys
import math
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/qualification'))
from audio_screening import acoustic_estimate, sine_drive


def test_reference_power_and_distance_preserve_sensitivity():
    assert acoustic_estimate(86, 1, 1) == 86


def test_doubling_distance_requires_four_times_power_for_same_level():
    assert acoustic_estimate(86, 4, 2) == pytest.approx(acoustic_estimate(86, 1, 1))


def test_tenfold_distance_costs_twenty_db():
    assert acoustic_estimate(86, 1, 10) == pytest.approx(66)


def test_nominal_sine_power_from_known_rms_voltage():
    d = sine_drive(1, 8)
    assert d['vrms'] == pytest.approx(math.sqrt(8))
    assert d['vpeak_sine'] == pytest.approx(4)
    assert d['requested_sine_dbfs'] == pytest.approx(-5.0691001301)
    assert sine_drive(.5, 8)['requested_sine_dbfs'] == pytest.approx(d['requested_sine_dbfs']-10*math.log10(2))


@pytest.mark.parametrize('power,distance',[(0,1),(1,0),(float('nan'),1)])
def test_unphysical_acoustic_inputs_rejected(power,distance):
    with pytest.raises(ValueError):
        acoustic_estimate(86,power,distance)
