"""Remove explicitly obsolete stubs/legends, stitch connector return, save filled copper."""
from design import *
import pcbnew as p,json
V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
removed=[]
for kind in ['main','controls','front']:
 d=ROOT/'boards'/('alec-'+kind);path=d/(d.name+'.kicad_pcb');b=p.LoadBoard(str(path))
 if kind=='main':
  for g in list(b.GetDrawings()):
   if isinstance(g,p.PCB_TEXT) and (g.GetText() in ['VOL-','MODE','VOL+','BATTERY'] or 'DEV' in g.GetText().upper()):b.Remove(g);removed.append(g)
  # Retired slide-switch branch on EN. Keep the surviving R32/U1 branch.
  for t in list(b.GetTracks()):
   if t.GetNetname()=='/EN_3V3' and (round(p.ToMM(t.GetStart().x),2),round(p.ToMM(t.GetStart().y),2))in [(104.45,105.75),(105.75,105.75)]:b.Remove(t);removed.append(t)
  for x,text in [(110,'J5 SETUP'),(145,'J6 FRONT'),(126,'J7 UART')]:
   g=p.PCB_TEXT(b);g.SetText(text);g.SetPosition(V(x,122));g.SetLayer(p.B_SilkS);g.SetMirrored(True);g.SetTextSize(V(1,1));g.SetTextThickness(p.FromMM(.15));b.Add(g)
 if kind=='controls':
  f=next(f for f in b.GetFootprints() if f.GetReference()=='SW4');m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/3dmodels/EG1218_drawing_envelope.step';f.Add3DModel(m)
 # Discard copper islands having no electrical anchor.
 for z in b.Zones():
  if not z.GetIsRuleArea():z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
 print(kind,'saved')
