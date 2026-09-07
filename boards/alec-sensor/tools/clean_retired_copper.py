#!/usr/bin/env python3
"""Remove only reported dangling tracks/vias; never suppress an electrical error.
The --initial migration pass may also remove obsolete conductors colliding with new
parts. It aborts if a collision touches the reviewed local switching-cell region.
Final DRC and connectivity must pass after rerouting.
"""
from pathlib import Path
import json,sys,subprocess
import pcbnew as p
D=Path(__file__).resolve().parents[1];pcb=D/(D.name+'.kicad_pcb')
cli='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli' if Path('/Applications/KiCad').exists() else 'kicad-cli'
removed=[];keep=[]
for iteration in range(80):
 subprocess.run([cli,'pcb','drc','--refill-zones','--save-board','--format','json','-o',str(D/'review/drc.json'),str(pcb)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
 r=json.loads((D/'review/drc.json').read_text());b=p.LoadBoard(str(pcb));tracks={t.m_Uuid.AsString():t for t in b.GetTracks()};uu=set()
 for a in r['violations']:
  if a['type'] in ['track_dangling','via_dangling']:uu.add(a['items'][0]['uuid'])
  elif '--initial' in sys.argv and a['type'] in ['clearance','shorting_items','hole_clearance','hole_to_hole']:
   for item in a['items']:
    t=tracks.get(item['uuid'])
    if t:
     assert not all(100<=p.ToMM(pt.x)<=150 and 94<=p.ToMM(pt.y)<=106 for pt in [t.GetStart(),t.GetEnd()]),'Move part instead of cutting local converter copper'
     uu.add(item['uuid'])
 if not uu:break
 for u in uu:
  t=tracks.get(u)
  if t:b.Remove(t);keep.append(t);removed.append(u)
 b.BuildConnectivity();p.SaveBoard(str(pcb),b)
print('Removed',len(removed),'retired/dangling items in',iteration+1,'passes')
(D/'review/copper-cleanup.json').write_text(json.dumps({'removed_count':len(removed),'iterations':iteration+1,'initial_migration':'--initial' in sys.argv},indent=2)+'\n')
