"""Migrate only low-speed UI copper; preserve the reviewed power/USB/audio layout.
Run with KiCad Python after create_schematics.py and netlist exports.
"""
from design import *
import pcbnew as p,xml.etree.ElementTree as E,shutil,json
V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def ls(*layers):
 s=p.LSET()
 for l in layers:s.AddLayer(l)
 return s
def mm(pt):return [p.ToMM(pt.x),p.ToMM(pt.y)]
FP=ROOT/'libs/footprints/Alarm.pretty';FP.mkdir(exist_ok=True)
def rectangle(fp,layer,x1,y1,x2,y2):
 for a,b in [((x1,y1),(x2,y1)),((x2,y1),(x2,y2)),((x2,y2),(x1,y2)),((x1,y2),(x1,y1))]:
  line=p.PCB_SHAPE(fp);line.SetShape(p.SHAPE_T_SEGMENT);line.SetStart(V(*a));line.SetEnd(V(*b));line.SetLayer(layer);line.SetWidth(p.FromMM(.05 if layer==p.F_CrtYd else .15));fp.Add(line)
def custom(name):
 fp=p.FOOTPRINT(None);fp.SetFPID(p.LIB_ID('Alarm',name));fp.SetReference('REF**');fp.SetValue(name)
 if name=='EG1218':
  fp.SetAttributes(p.FP_THROUGH_HOLE)
  for i,x in enumerate([-2.5,0,2.5],1):
   pad=p.PAD(fp);pad.SetNumber(str(i));pad.SetPosition(V(x,0));pad.SetShape(p.PAD_SHAPE_CIRCLE);pad.SetAttribute(p.PAD_ATTRIB_PTH);pad.SetSize(V(1.7,1.7));pad.SetDrillSize(V(.9,.9));pad.SetLayerSet(ls(p.F_Cu,p.B_Cu,p.F_Mask,p.B_Mask));fp.Add(pad)
  rectangle(fp,p.F_Fab,-5.8,-2,5.8,2);rectangle(fp,p.F_CrtYd,-6.05,-2.25,6.05,2.25)
 else:
  fp.SetAttributes(p.FP_SMD)
  for i,(x,y) in enumerate([(-1,-2),(1,-2),(-1,0),(1,0),(-1,2),(1,2)],1):
   pad=p.PAD(fp);pad.SetNumber(str(i));pad.SetPosition(V(x,y));pad.SetShape(p.PAD_SHAPE_CIRCLE);pad.SetAttribute(p.PAD_ATTRIB_SMD);pad.SetSize(V(1,1));pad.SetLayerSet(ls(p.F_Cu,p.F_Mask));fp.Add(pad)
  rectangle(fp,p.F_CrtYd,-2,-3,2,3);rectangle(fp,p.F_Fab,-2,-3,2,3)
 p.PCB_IO_KICAD_SEXPR().FootprintSave(str(FP),fp)
for name in ['EG1218','Programming_2x03_P2.0mm']:custom(name)

def loadfp(board,c,d,nets,padnets):
 ref=c.attrib['ref'];lib,name=c.findtext('footprint').split(':')
 folder=FP if lib=='Alarm' else LIB/'footprints'/f'{lib}.pretty'
 f=p.FootprintLoad(str(folder),name);assert f is not None,(lib,name)
 f.SetFPID(p.LIB_ID(lib,name));f.SetReference(ref);f.SetValue(c.findtext('value'));board.Add(f)
 for field in c.findall('fields/field'):
  if field.attrib['name']!='Footprint':f.SetField(field.attrib['name'],field.text or '')
 path=p.KIID_PATH()
 for u in (c.find('sheetpath').attrib['tstamps']+c.findtext('tstamps')).strip('/').split('/'):path.push_back(p.KIID(u))
 f.SetPath(path);f.SetSheetname('/');f.SetSheetfile(d.name+'.kicad_sch')
 for pad in f.Pads():
  if (ref,pad.GetNumber()) in padnets:pad.SetNet(nets[padnets[ref,pad.GetNumber()]])
 # Embed local STEP dependencies, preserving the library transforms.
 updated_models=list(f.Models())
 for model in updated_models:
  raw=model.m_Filename;resolved=Path(raw.replace('${KICAD10_3DMODEL_DIR}',str(LIB/'3dmodels')).replace('${KICAD9_3DMODEL_DIR}',str(LIB/'3dmodels')))
  if resolved.is_file():
   local=d/'3dmodels'/resolved.name;local.parent.mkdir(exist_ok=True);shutil.copy(resolved,local);model.m_Filename='${KIPRJMOD}/3dmodels/'+resolved.name
 f.Models().clear()
 for model in updated_models:f.Add3DModel(model)
 for field in f.GetFields():field.SetVisible(False)
 if ref=='J7':f.SetAttributes(p.FP_SMD|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
 for g in f.GraphicalItems():
  if isinstance(g,p.PCB_TEXT) and g.GetLayer()==p.F_SilkS and p.ToMM(g.GetTextSize().y)<1:g.SetLayer(p.F_Fab)
 return f

def setup(d,board=None):
 xml=E.parse(d/'review/netlist.xml').getroot();b=board or p.BOARD();existing={n.GetNetname():n for n in b.GetNetsByNetcode().values()};nets={};pn={}
 for net in xml.find('nets'):
  name=net.attrib['name'];ni=existing.get(name)
  if ni is None:ni=p.NETINFO_ITEM(b,name);b.Add(ni)
  nets[name]=ni
  for pd in net:pn[pd.attrib['ref'],pd.attrib['pin']]=name
 return b,xml,nets,pn
# The product starts from the reviewed board, never from an empty reroute.
b=p.LoadBoard(str(BASE/(BASE.name+'.kicad_pcb')))
removed=[]
oldfps={f.GetReference():f for f in b.GetFootprints()};oldnets={(ref,pd.GetNumber()):pd.GetNetname() for ref,f in oldfps.items() for pd in f.Pads()}
for ref in REMOVE:b.Remove(oldfps[ref]);removed.append(oldfps[ref])
b,xml,nets,pn=setup(MAIN,b)
# Derive renames from surviving physical pins; same-net copper must follow its net.
renames={}
for f in b.GetFootprints():
 for pad in f.Pads():
  key=f.GetReference(),pad.GetNumber()
  if key in pn:
   old=oldnets[key];new=pn[key]
   if old!=new:renames[old]=new
   pad.SetNet(nets[new])
 f.SetSheetfile(MAIN.name+'.kicad_sch')
for t in b.GetTracks():
 if t.GetNetname() in renames:t.SetNet(nets[renames[t.GetNetname()]])
# Remove obsolete UI conductors only. None of these is a switch node or a power path.
reroute={'/GPIO4','/GPIO5','/GPIO6','/GPIO10','/LED_R_K','/LED_G_K','/LED_B_K'}
for t in list(b.GetTracks()):
 if t.GetNetname() in reroute:b.Remove(t);removed.append(t)
# Retire ground/3v3 stubs at removed user parts and free southern connector footprints.
# Only south of y=118; all main regulator/capacitor copper is north of y=106.
for t in list(b.GetTracks()):
 if min(mm(t.GetStart())[1],mm(t.GetEnd())[1])>=118 and t.GetNetname() in ['GND','/3v3']:b.Remove(t);removed.append(t)
for c in xml.find('components'):
 if c.attrib['ref'] in ['J5','J6','J7','R50','R51','R52','R53']:
  f=loadfp(b,c,MAIN,nets,pn);pos={'J5':(110,122),'J6':(145,122),'J7':(126,123),'R50':(119,120),'R51':(119,122),'R52':(119,124),'R53':(137,121)}[c.attrib['ref']];f.SetPosition(V(*pos))
# Connector pin 5 return goes inward beneath its insulating housing.
net=b.GetNetcodeFromNetname('GND');v=p.PCB_VIA(b);v.SetPosition(V(111.25,123));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(net);b.Add(v)
t=p.PCB_TRACK(b);t.SetStart(V(111.25,123.95));t.SetEnd(V(111.25,123));t.SetWidth(p.FromMM(.2));t.SetLayer(p.F_Cu);t.SetNetCode(net);b.Add(t)
# Pre-route the central connector pin to a through via before adjacent fanout.
net=b.GetNetcodeFromNetname('/BTN_VOL_PLUS');v=p.PCB_VIA(b);v.SetPosition(V(110,122.8));v.SetWidth(p.FromMM(.55));v.SetDrill(p.FromMM(.25));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(net);b.Add(v)
t=p.PCB_TRACK(b);t.SetStart(V(110,123.95));t.SetEnd(V(110,122.8));t.SetWidth(p.FromMM(.15));t.SetLayer(p.F_Cu);t.SetNetCode(net);b.Add(t)
b.BuildConnectivity();p.SaveBoard(str(MAIN/(MAIN.name+'.kicad_pcb')),b)
(MAIN/'review/migration.json').write_text(json.dumps({'removed_main_parts':sorted(REMOVE),'renamed_nets':renames,'rerouted_ui_nets':sorted(reroute)},indent=2)+'\n')
# Daughterboard coordinates are pinned to v4.1 switch and mounting-hole locations.
for kind in ['controls','front']:
 d=ROOT/'boards'/('alec-'+kind);b,xml,nets,pn=setup(d);b.SetCopperLayerCount(2)
 dims=(27,34) if kind=='controls' else (24,10)
 for a,c in [((0,0),(dims[0],0)),((dims[0],0),dims),(dims,(0,dims[1])),((0,dims[1]),(0,0))]:
  e=p.PCB_SHAPE(b);e.SetShape(p.SHAPE_T_SEGMENT);e.SetStart(V(*a));e.SetEnd(V(*c));e.SetLayer(p.Edge_Cuts);e.SetWidth(p.FromMM(.05));b.Add(e)
 for c in xml.find('components'):
  ref=c.attrib['ref'];f=loadfp(b,c,d,nets,pn)
  if kind=='controls':
   loc={'J1':(9,24.5),'SW1':(16.75,3.75),'SW2':(16.75,15.75),'SW3':(16.75,27.75),'SW4':(4,16)}[ref]
   if ref=='SW4':f.SetOrientationDegrees(90)
  else:loc={'J1':(18,3.5),'SW1':(6,5),'D1':(18,5)}[ref]
  f.SetPosition(V(*loc))
  if ref=='J1':f.Flip(f.GetPosition(),False)
 holes=[(24.5,24),(24.5,12),(2,30),(2,3)] if kind=='controls' else [(1.7,1.7),(22.3,8.5)]
 for i,xy in enumerate(holes,1):
  f=p.FootprintLoad(str(LIB/'footprints/MountingHole.pretty'),'MountingHole_2.2mm_M2');f.SetReference('H'+str(i));f.SetAttributes(p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES|p.FP_BOARD_ONLY);f.SetPosition(V(*xy));b.Add(f)
  for field in f.GetFields():field.SetVisible(False)
 gnd=nets['/GND']
 for layer in [p.F_Cu,p.B_Cu]:
  z=p.ZONE(b);z.SetLayer(layer);z.SetNet(gnd);z.SetLocalClearance(p.FromMM(.2));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL);z.SetThermalReliefGap(p.FromMM(.25));z.SetThermalReliefSpokeWidth(p.FromMM(.3));z.SetMinThickness(p.FromMM(.2));outline=z.Outline();outline.NewOutline()
  for x,y in [(.3,.3),(dims[0]-.3,.3),(dims[0]-.3,dims[1]-.3),(.3,dims[1]-.3)]:outline.Append(p.FromMM(x),p.FromMM(y))
  b.Add(z)
 b.BuildConnectivity();p.SaveBoard(str(d/(d.name+'.kicad_pcb')),b)
 print(d.name,dims)
