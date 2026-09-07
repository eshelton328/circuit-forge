#!/usr/bin/env python3
"""Move service controls on an existing S1 board; reroute and check afterward.
The schematic and converter/USB copper stay unchanged. Intended as a one-time S1.1 migration;
create_pcb.py also reads the same service-control coordinates for a fresh build.
"""
from pathlib import Path
import hashlib,json
import pcbnew as p
D=Path(__file__).resolve().parents[1];path=D/'alec-sensor.kicad_pcb'
cfg=json.loads((D.parents[1]/'enclosures/alec-sensor/interface.json').read_text())
before=hashlib.sha256(path.read_bytes()).hexdigest();b=p.LoadBoard(str(path));fps={f.GetReference():f for f in b.GetFootprints()};held=[];nets=set();moved=[]
for ref,c in cfg['service_controls'].items():
 f=fps[ref];dest=p.VECTOR2I(*(p.FromMM(v) for v in c['kicad_xy']))
 if f.GetPosition()==dest and f.GetLayer()==p.B_Cu:continue
 nets.update(pd.GetNetname() for pd in f.Pads() if pd.GetNetCode() and pd.GetNetname()!='GND')
 if f.GetLayer()!=p.B_Cu:f.Flip(f.GetPosition(),False)
 f.SetPosition(dest);moved.append(ref)
removed=0
for t in list(b.GetTracks()):
 if t.GetNetname() in nets:b.Remove(t);held.append(t);removed+=1
b.BuildConnectivity();p.SaveBoard(str(path),b)
(D/'review/rear-service-migration.json').write_text(json.dumps({'revision':'S1.1','source_pcb_sha256':before,'moved_controls':moved,'removed_track_items':removed,'nets_to_reroute':sorted(nets),'note':'No schematic change. Converter cells and USB paths retained; final DRC, connectivity and layout guards required.'},indent=2)+'\n')
print('Moved',moved,'and removed',removed,'items on',sorted(nets))
