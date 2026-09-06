"""Steady-state proposal calculator; never certifies startup, cooling or ratings."""
import math


def supply_point(power_w, source_v, series_ohm):
    """High-voltage root of P = I*(Voc - I*R), including source sag.

    No solution at/above the maximum-power nose is accepted as an operating
    point. Dynamic stability, inrush and battery chemistry are not modeled.
    """
    if not all(math.isfinite(v) for v in (power_w, source_v, series_ohm)):
        raise ValueError('Supply inputs must be finite')
    if power_w < 0 or source_v <= 0 or series_ohm < 0:
        raise ValueError('Invalid supply inputs')
    discriminant = source_v**2 - 4*series_ohm*power_w
    if discriminant <= 0:
        return None
    # Rationalized expression avoids cancellation for small R or P.
    current = 2*power_w/(source_v + math.sqrt(discriminant))
    return {'current_a': current, 'protected_v': source_v-current*series_ohm}


def budget(case, assumptions):
    a = assumptions
    for key in ('eta_3v3', 'eta_5v', 'eta_audio'):
        if not math.isfinite(a[key]) or not 0 < a[key] <= 1:
            raise ValueError(f'Invalid {key}')
    for key in ('q1_ohm', 'external_series_ohm', 'amp_idle_w'):
        if not math.isfinite(a[key]) or a[key] < 0:
            raise ValueError(f'Invalid {key}')
    for key in ('rail_3v3_a', 'audio_w', 'offboard_3v3_w'):
        if not math.isfinite(case[key]) or case[key] < 0:
            raise ValueError(f'Invalid {key}')
    if not 0 <= a['converter_ic_loss_fraction'] <= 1:
        raise ValueError('Invalid converter loss partition')
    rail3 = 3.3*case['rail_3v3_a']
    if case['offboard_3v3_w'] > rail3:
        raise ValueError('Off-board power exceeds delivered 3.3 V power')
    # eta_audio applies to the incremental audio power only. Idle overhead is
    # explicit, avoiding undefined zero-output efficiency and double counting.
    rail5 = case['audio_w']/a['eta_audio'] + a['amp_idle_w']
    pin = rail3/a['eta_3v3'] + rail5/a['eta_5v']
    supply = supply_point(pin, case['source_v'], a['q1_ohm']+a['external_series_ohm'])
    result = {'inputs': case, 'assumptions': a, 'rail_3v3_w': rail3,
              'rail_5v_w': rail5, 'rail_5v_a': rail5/5,
              'converter_input_w': pin, 'supply': supply,
              'physical_release_approved': False}
    if supply is None:
        result['status'] = 'no steady-state supply solution'
        return result
    current = supply['current_a']
    fraction = a['converter_ic_loss_fraction']
    sources = {}
    for i, loss in enumerate((rail3*(1/a['eta_3v3']-1),
                              rail5*(1/a['eta_5v']-1)), 1):
        sources[f'U{i}'] = {'watts': loss*fraction}
        sources[f'L{i}'] = {'watts': loss*(1-fraction)}
    # U3 is a declared location proxy for all retained 3.3 V dissipation.
    # Do not interpret its modeled temperature as the ESP die temperature.
    sources['U3'] = {'watts': rail3-case['offboard_3v3_w']}
    sources['U6'] = {'watts': rail5-case['audio_w']}
    sources['Q1'] = {'watts': current**2*a['q1_ohm']}
    heat = sum(s['watts'] for s in sources.values())
    external_loss = current**2*a['external_series_ohm']
    supply_power = case['source_v']*current
    balance = supply_power-(heat+external_loss+case['audio_w']+case['offboard_3v3_w'])
    result.update(sources=sources, board_heat_w=heat, external_series_heat_w=external_loss,
                  source_power_w=supply_power, energy_balance_error_w=balance,
                  status='hypothetical steady-state solution',
                  connector_below_2a=current < 2,
                  connector_below_proposed_1p6a=current <= 1.6,
                  protected_at_least_3v=supply['protected_v'] >= 3,
                  minimum_source_v_for_3v_loaded=3+pin/3*(a['external_series_ohm']+a['q1_ohm']))
    return result
