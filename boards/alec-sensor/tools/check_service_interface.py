#!/usr/bin/env python3
"""Native-file regression guard for rear service access; no KiCad runtime needed."""
from pathlib import Path
import json,sys
D=Path(__file__).resolve().parents[1];ROOT=D.parents[1]
sys.path.insert(0,str(ROOT/'scripts/alarm'))
from design import parse,children,child,prop,val

def check(board=D/'alec-sensor.kicad_pcb',interface=ROOT/'enclosures/alec-sensor/interface.json'):
 cfg=json.loads(Path(interface).read_text());tree=parse(Path(board).read_text())
 fps={prop(f,'Reference'):f for f in children(tree,'footprint')};done=[]
 for ref in ['SW1','SW2','SW3']:
  f=fps[ref]
  assert val(child(f,'layer')[1])=='B.Cu',f'{ref} must face the rear battery compartment'
  assert list(map(float,child(f,'at')[1:3]))==cfg['service_controls'][ref]['kicad_xy'],f'{ref} is outside its service-control allocation'
  done.append(ref+' rear-facing and located in service bay')
 for ref in ['J3','SW7','D2']:
  assert val(child(fps[ref],'layer')[1])=='F.Cu',f'{ref} must face the exterior panel'
  done.append(ref+' faces outward')
 assert cfg['battery_holder']['opening'].startswith('rear (-Z)'),'Battery holder must open toward the rear cover'
 done.append('Battery holder opens toward rear cover')
 assert cfg['service_access']['requires_pcb_removal_for_cells_or_controls'] is False,'Routine service must leave the PCB installed'
 done.append('Routine cell/control service leaves PCB installed')
 return done

if __name__=='__main__':
 done=check();(D/'review/service-interface-checks.json').write_text(json.dumps({'status':'pass','assertions':len(done),'checks':done,'scope':'Native PCB face/position and service intent. CAD separately checks approach volumes; physical hand access and tolerances need samples.'},indent=2)+'\n')
 print(f'{len(done)} rear-service interface checks passed')
