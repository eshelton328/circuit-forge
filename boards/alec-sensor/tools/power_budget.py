#!/usr/bin/env python3
"""Sensitivity estimate, not a battery discharge simulation or measured runtime."""
from pathlib import Path
import json
D=Path(__file__).resolve().parents[1]

def estimate(active_hours_per_day, energy_wh=9.0, efficiency=.85, mcu_active_ma=80.0, sleep_pack_ma=.2, pack_v=4.5):
 if not 0<=active_hours_per_day<=24 or not 0<efficiency<=1 or energy_wh<=0:
  raise ValueError('Invalid energy, efficiency or duty cycle')
 radar_w=5*.079
 awake_pack_w=(radar_w+3.3*mcu_active_ma/1000)/efficiency
 day_wh=awake_pack_w*active_hours_per_day+pack_v*sleep_pack_ma/1000*(24-active_hours_per_day)
 return {'active_hours_per_day':active_hours_per_day,'day_wh':day_wh,'days':energy_wh/day_wh}
if __name__=='__main__':
 out={'status':'illustrative_unmeasured','assumptions':{'usable_pack_wh':[6,9,12],'conversion_efficiency':.85,'radar_5v_ma':79,'mcu_3v3_active_ma':80,'whole_board_sleep_pack_ma':.2,'sleep_pack_voltage':4.5,'schedule_sync_time':'must be included in active time; not modeled separately','temperature_and_cell_impedance':'not modeled'},'radar_alone_continuous_hours':{str(e):e/(5*.079/.85) for e in [6,9,12]},'scenarios':[{'pack_wh':e,**estimate(h,e)} for e in [6,9,12] for h in [.25,.5,1,24]]}
 (D/'review/power-budget.json').write_text(json.dumps(out,indent=2)+'\n')
 print('Generated unmeasured runtime sensitivity estimates')
