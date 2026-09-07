"""Verify preserved high-current geometry and the new enclosure mounting contract."""
from design import *
import pcbnew as p,math,json,hashlib
b=p.LoadBoard(str(MAIN/(MAIN.name+'.kicad_pcb')));base=p.LoadBoard(str(BASE/(BASE.name+'.kicad_pcb')))
fps={f.GetReference():f for f in b.GetFootprints()};old={f.GetReference():f for f in base.GetFootprints()}
def xy(v):return tuple(round(p.ToMM(k),6) for k in [v.x,v.y])
checks=[]
def check(name,ok,**details):
 assert ok,(name,details)
 checks.append(dict(name=name,passed=True,**details))
for ref in set(old)-REMOVE:
 check(ref+' retained placement',xy(old[ref].GetPosition())==xy(fps[ref].GetPosition()) and old[ref].GetOrientationDegrees()==fps[ref].GetOrientationDegrees())
critical={'GND','/PFET','/3v3','/5v','/speaker +','/speaker -','/D+','/D-'}
for ref in ['U1','U2']:
 for pd in old[ref].Pads():
  if pd.GetNumber() in ['9','11','1','3','4']:critical.add(pd.GetNetname())
def geometry(t):
 via=isinstance(t,p.PCB_VIA)
 return (t.GetNetname(),xy(t.GetStart()),xy(t.GetEnd()),round(p.ToMM(t.GetWidth(p.F_Cu) if via else t.GetWidth()),6),t.GetLayer(),p.ToMM(t.GetDrill()) if via else 0)
expected=[geometry(t) for t in base.GetTracks() if t.GetNetname() in critical and min(xy(t.GetStart())[1],xy(t.GetEnd())[1])<118]
actual={geometry(t) for t in b.GetTracks()}
check('Reviewed power, local return, USB and BTL copper retained',all(t in actual for t in expected),checked_tracks_and_vias=len(expected))
check('In1 remains an unrouted filled ground plane',not any(not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.In1_Cu for t in b.GetTracks()) and any(z.GetNetname()=='GND' and z.IsOnLayer(p.In1_Cu) and z.GetFilledPolysList(p.In1_Cu).OutlineCount() for z in b.Zones()))
for ref,cap,pin in [('U1','C3','12'),('U1','C5','7'),('U2','C11','12'),('U2','C13','7')]:
 a=next(pd for pd in fps[ref].Pads() if pd.GetNumber()==pin);c=next(pd for pd in fps[cap].Pads() if pd.GetNumber()=='1')
 distance=math.dist(xy(a.GetPosition()),xy(c.GetPosition()));check(cap+' short local connection retained',distance<=2,IC_pad_to_cap_pad_mm=distance)
for kind,holes in [('controls',[(24.5,24),(24.5,12),(2,30),(2,3)]),('front',[(1.7,1.7),(22.3,8.5)])]:
 board=p.LoadBoard(str(ROOT/'boards'/('alec-'+kind)/('alec-'+kind+'.kicad_pcb')))
 f={f.GetReference():f for f in board.GetFootprints()}
 for i,pt in enumerate(holes,1):check(kind+' mount H'+str(i),xy(f['H'+str(i)].GetPosition())==pt)
 check(kind+' connector faces inward',f['J1'].GetLayer()==p.B_Cu)
 for pad in f['J1'].Pads():
  if pad.GetNumber().isdigit():check(kind+' connector pin '+pad.GetNumber()+' on B.Cu',pad.IsOnLayer(p.B_Cu) and not pad.IsOnLayer(p.F_Cu))
report=dict(passed=True,pcb_sha256=hashlib.sha256((MAIN/(MAIN.name+'.kicad_pcb')).read_bytes()).hexdigest(),checks=checks,scope='Preserved reviewed layout geometry; changed filled copper and remote wiring still require physical screening and prototype qualification.')
(MAIN/'review/layout-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(len(checks),'layout guards passed')
