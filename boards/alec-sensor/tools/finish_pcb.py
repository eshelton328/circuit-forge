"""Final silkscreen/model cleanup; electrical errors must be fixed, never excluded."""
from pathlib import Path
import pcbnew as p
D=Path(__file__).resolve().parents[1];fn=D/(D.name+'.kicad_pcb');b=p.LoadBoard(str(fn));held=[]
seen=set()
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  key=(t.GetNetname(),t.GetPosition().x,t.GetPosition().y,t.GetDrill(),t.GetWidth(p.F_Cu))
  if key in seen:b.Remove(t);held.append(t)
  seen.add(key)
for g in b.GetDrawings():
 if isinstance(g,p.PCB_TEXT):
  s=g.GetText();pos={'BAT / PAIR':(114,125),'BOOT':(152,125),'PRESENCE':(130,114.3),'3 AA ONLY - NO CHARGE':(130,114),'ON':(157.7,94.5),'OFF':(148.3,94.5)}.get(s)
  if pos:g.SetPosition(p.VECTOR2I(p.FromMM(pos[0]),p.FromMM(pos[1])))
  if s=='3 AA ONLY - NO CHARGE':g.SetLayer(p.B_SilkS);g.SetMirrored(True)
source=p.LoadBoard(str(D.parent/'esp32s3-devkit-5v/esp32s3-devkit-5v.kicad_pcb'));old={f.GetReference():f for f in source.GetFootprints()}
for f in b.GetFootprints():
 if f.GetReference()=='SW7':
  f.Models().clear()
  for m in old['SW7'].Models():f.Add3DModel(m)
b.BuildConnectivity();p.SaveBoard(str(fn),b)
