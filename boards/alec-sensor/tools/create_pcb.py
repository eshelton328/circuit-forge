#!/usr/bin/env python3
"""Build S1 from reviewed copper. Run with KiCad Python; route low-speed additions next.
No switching-cell footprint or local copper is moved. See migration.json for net edits.
"""
from pathlib import Path
import sys, shutil, json, xml.etree.ElementTree as E
import wx
app=wx.App(False)
import pcbnew as p
ROOT=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/alarm'))
from design import BASE,LIB
V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def layers(*ll):
 s=p.LSET()
 for l in ll:s.AddLayer(l)
 return s
FP=D/'footprints/Sensor.pretty';FP.mkdir(parents=True,exist_ok=True)
shutil.copytree(BASE/'footprints/Board.pretty',D/'footprints/Board.pretty',dirs_exist_ok=True)
(D/'3dmodels').mkdir(exist_ok=True)
for model in (BASE/'3dmodels').iterdir():
 if model.suffix.lower() in ['.step','.wrl'] or model.name.startswith('LICENSE-'):shutil.copy2(model,D/'3dmodels'/model.name)
def rect(f,l,x1,y1,x2,y2):
 for a,c in [((x1,y1),(x2,y1)),((x2,y1),(x2,y2)),((x2,y2),(x1,y2)),((x1,y2),(x1,y1))]:
  g=p.PCB_SHAPE(f);g.SetShape(p.SHAPE_T_SEGMENT);g.SetStart(V(*a));g.SetEnd(V(*c));g.SetLayer(l);g.SetWidth(p.FromMM(.05 if l==p.F_CrtYd else .15));f.Add(g)
for name in ['SW_CK_1101M2S3CQE2','Samtec_SSW-105-01-F-S']:
 f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID('Sensor',name));f.SetReference('REF**');f.SetValue(name);f.SetAttributes(p.FP_THROUGH_HOLE)
 if name.startswith('SW_'):
  pos=[(-4.7,0),(0,0),(4.7,0)];size=2.65;drill=1.85;bounds=(-6.35,-3.3,6.35,3.3)
 else:
  pos=[(i*2.54,0) for i in range(5)];size=1.7;drill=1.0;bounds=(-1.525,-1.205,11.685,1.205)
 for i,(x,y) in enumerate(pos,1):
  pad=p.PAD(f);pad.SetNumber(str(i));pad.SetPosition(V(x,y));pad.SetShape(p.PAD_SHAPE_RECT if i==1 else p.PAD_SHAPE_CIRCLE);pad.SetAttribute(p.PAD_ATTRIB_PTH);pad.SetSize(V(size,size));pad.SetDrillSize(V(drill,drill));pad.SetLayerSet(p.PAD.PTHMask());f.Add(pad)
 rect(f,p.F_Fab,*bounds);rect(f,p.F_CrtYd,bounds[0]-.5,bounds[1]-.5,bounds[2]+.5,bounds[3]+.5)
 rect(f,p.F_SilkS,bounds[0]-.1,bounds[1]-.2,bounds[2]+.1,bounds[3]+.2)
 model=p.FP_3DMODEL();model.m_Filename='${KIPRJMOD}/3dmodels/'+name+'.step';f.Add3DModel(model)
 p.PCB_IO_KICAD_SEXPR().FootprintSave(str(FP),f)
xml=E.parse(D/'review/netlist.xml').getroot();comps={c.get('ref'):c for c in xml.find('components')};pn={}
for n in xml.find('nets'):
 for a in n:pn[a.get('ref'),a.get('pin')]=n.get('name')
b=p.LoadBoard(str(BASE/(BASE.name+'.kicad_pcb')));oldfps={f.GetReference():f for f in b.GetFootprints()}
oldpn={(ref,a.GetNumber()):a.GetNetname() for ref,f in oldfps.items() for a in f.Pads()}
replace={'SW1','J3','SW7'} # SW7 schematic B3U footprint differs from base PCB TS1187
moved={'D2','R28','R29','R30','SW3','R27','C25'}
removed=[];discarded=[]
for ref,f in oldfps.items():
 if ref in replace or (ref not in comps and not ref.startswith(('H','TP'))):b.Remove(f);discarded.append(f);removed.append(ref)
# Schematic same-net mapping must be unambiguous before any retained track is relabelled.
mapsets={}
for key,new in pn.items():
 if key in oldpn and key[0] not in replace:mapsets.setdefault(oldpn[key],set()).add(new)
renames={old:next(iter(nn)) for old,nn in mapsets.items() if len(nn)==1}
reroute={'/VBAT','/GPIO18','/SW_ON','/GPIO4','/GPIO10','/GPIO11','/GPIO17','/LED_R_K','/LED_G_K','/LED_B_K','/GPIO38','/GPIO39','/GPIO40','/GPIO0','/GPIO8','/GPIO9'}
reroute.update(old for (ref,pin),old in oldpn.items() if ref in moved|replace and old not in ['GND','/3v3','/5v','/PFET'])
# Keep power nets and critical USB/local regulator traces, remove conductors for retired signals.
override_tracks={}
netnames={n.get('name') for n in xml.find('nets')};removed_tracks=0
for t in list(b.GetTracks()):
 old=t.GetNetname();new=renames.get(old,old)
 if old in ['/EN_3V3','/SW_ON']:
  override_tracks[t.m_Uuid.AsString()]='/EN_3V3';continue
 if old=='/GPIO18' and min(p.ToMM(t.GetStart().y),p.ToMM(t.GetEnd().y))>=90:
  override_tracks[t.m_Uuid.AsString()]='/RADAR_EN';continue
 if old=='/GPIO38' and max(p.ToMM(t.GetStart().y),p.ToMM(t.GetEnd().y))<85:continue
 retired_area=(min(p.ToMM(t.GetStart().x),p.ToMM(t.GetEnd().x))>150 and min(p.ToMM(t.GetStart().y),p.ToMM(t.GetEnd().y))>92) or (min(p.ToMM(t.GetStart().x),p.ToMM(t.GetEnd().x))>142 and min(p.ToMM(t.GetStart().y),p.ToMM(t.GetEnd().y))>106)
 if old in reroute or new not in netnames or new.startswith('unconnected-') or len(mapsets.get(old,set()))>1 or retired_area:
  b.Remove(t);discarded.append(t);removed_tracks+=1
# Discard local supply stubs at moved/removed components in the southern former UI region.
for t in list(b.GetTracks()):
 if min(p.ToMM(t.GetStart().y),p.ToMM(t.GetEnd().y))>=111 and t.GetNetname() in ['GND','/3v3']:
  b.Remove(t);discarded.append(t);removed_tracks+=1
nets={}
for name in netnames:
 ni=next((v for v in b.GetNetsByNetcode().values() if v.GetNetname()==name),None)
 if ni is None:ni=p.NETINFO_ITEM(b,name);b.Add(ni)
 nets[name]=ni
for t in b.GetTracks():
 name=override_tracks.get(t.m_Uuid.AsString(),renames.get(t.GetNetname(),t.GetNetname()))
 if name in nets:t.SetNet(nets[name])
for f in b.GetFootprints():
 for pad in f.Pads():
  key=f.GetReference(),pad.GetNumber()
  if key in pn:pad.SetNet(nets[pn[key]])
  elif f.GetReference()=='TP8':pad.SetNet(nets['/RADAR_EN']);f.SetValue('RADAR_EN')
 f.SetSheetfile(D.name+'.kicad_sch')
positions={'SW1':(153,89.5,0),'SW3':(152,120,0),'SW7':(114,121,0),'D2':(130,121,0),'R28':(128,117,90),'R29':(130,117,90),'R30':(132,117,90),'R27':(114,117,0),'C25':(116,117,0),'F1':(110,112,0),'U10':(155,96.5,0),'J3':(145,108,0),'C35':(155,111.5,0),'C36':(159.5,108,90),'C37':(161,93.5,90),'R54':(152,92.3,0),'R55':(160.8,96,90),'R56':(160.8,98,90)}
for ref,c in comps.items():
 f=next((a for a in b.GetFootprints() if a.GetReference()==ref),None)
 if f is None:
  lib,name=c.findtext('footprint').split(':');folder=FP if lib=='Sensor' else D/'footprints/Board.pretty' if lib=='Board' else ROOT/'libs/footprints/TPS63070.pretty' if lib=='TPS63070' else LIB/'footprints'/f'{lib}.pretty'
  f=p.FootprintLoad(str(folder),name);assert f,ref;f.SetFPID(p.LIB_ID(lib,name));f.SetReference(ref);b.Add(f)
  updated=list(f.Models());f.Models().clear()
  for m in updated:
   src=Path(m.m_Filename.replace('${KICAD10_3DMODEL_DIR}',str(LIB/'3dmodels')).replace('${KICAD9_3DMODEL_DIR}',str(LIB/'3dmodels')))
   if src.is_file():shutil.copy2(src,D/'3dmodels'/src.name);m.m_Filename='${KIPRJMOD}/3dmodels/'+src.name
   f.Add3DModel(m)
 f.SetValue(c.findtext('value'))
 for a in c.findall('fields/field'):
  if a.get('name')!='Footprint':f.SetField(a.get('name'),a.text or '')
 path=p.KIID_PATH()
 for u in (c.find('sheetpath').get('tstamps')+c.findtext('tstamps')).strip('/').split('/'):path.push_back(p.KIID(u))
 f.SetPath(path)
 for pd in f.Pads():
  if (ref,pd.GetNumber()) in pn:pd.SetNet(nets[pn[ref,pd.GetNumber()]])
 if ref in positions:
  x,y,rot=positions[ref];f.SetPosition(V(x,y));f.SetOrientationDegrees(rot)
 if ref=='SW1':f.Flip(f.GetPosition(),False)
 for field in f.GetFields():field.SetVisible(False)
# Retired labels are not allowed to misidentify the sensor interface.
for g in list(b.GetDrawings()):
 if isinstance(g,p.PCB_TEXT):b.Remove(g);discarded.append(g)
def text(s,x,y,layer=p.F_SilkS,size=1):
 t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(V(x,y));t.SetTextSize(V(size,size));t.SetTextThickness(p.FromMM(.15));t.SetLayer(layer);t.SetMirrored(layer==p.B_SilkS);b.Add(t)
text('ALEC SENSOR S1',131,124,size=1.2)
text('BAT / PAIR',114,124);text('PRESENCE',130,118.8);text('BOOT',152,124)
text('TX RX OUT GND 5V',150,105);text('LD2410C',150,103.4)
text('3 AA ONLY - NO CHARGE',129,109.3)
text('ON',157.7,93.5,p.B_SilkS);text('OFF',148.3,93.5,p.B_SilkS)
b.BuildConnectivity();p.SaveBoard(str(D/(D.name+'.kicad_pcb')),b)
(D/'review/migration.json').write_text(json.dumps({'source_board':str(BASE.relative_to(ROOT)),'source_revision':'0bce752','removed_components':sorted(removed),'moved_low_speed_parts':positions,'removed_track_items':removed_tracks,'rerouted_original_nets':sorted(reroute),'net_renames':{k:v for k,v in renames.items() if k!=v},'power_cells':'U1/U2/L1/L2/C1-C16/R3-R10 preserved at original locations. Run check_layout.py after final routing.'},indent=2)+'\n')
print('Created PCB with',len(b.GetFootprints()),'footprints and',len(b.GetTracks()),'retained copper items')
