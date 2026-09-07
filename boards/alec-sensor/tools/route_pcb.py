#!/usr/bin/env python3
"""Route remaining prototype connections with a conservative three-layer grid.
Critical switching and USB traces are supplied by create_pcb.py. In1.Cu is
reserved entirely for GND. KiCad DRC is mandatory after this geometric pass.
Requires numpy and ALARM_GRID_LIBRARY pointing to the compiled grid_search.cpp library.
"""
import pcbnew as p
import numpy as np
from pathlib import Path
import ctypes as ct
import math, json, time, os
import sys
D=Path(__file__).resolve().parents[1];pcb=D/(D.name+'.kicad_pcb');b=p.LoadBoard(str(pcb))
edge=b.GetBoardEdgesBoundingBox()
step=.05;ox,oy=round(p.ToMM(edge.GetX()),1),round(p.ToMM(edge.GetY()),1)
ex,ey=round(p.ToMM(edge.GetRight()),1),round(p.ToMM(edge.GetBottom()),1)
nx,ny=int(round((ex-ox)/step))+1,int(round((ey-oy)/step))+1
layers=[p.F_Cu,p.In2_Cu,p.B_Cu] if b.GetCopperLayerCount()==4 else [p.F_Cu,p.B_Cu];NL=len(layers);area=nx*ny
lib=ct.CDLL(os.environ.get('ALARM_GRID_LIBRARY','/tmp/esp32_grid_search.dylib'));fn=lib.find_path
P8=ct.POINTER(ct.c_uint8);PI=ct.POINTER(ct.c_int)
fn.argtypes=[ct.c_int,ct.c_int,ct.c_int,P8,P8,ct.c_int,ct.c_int,PI,ct.c_int,ct.c_int];fn.restype=ct.c_int
out=np.zeros(200000,dtype=np.int32)
def mm(pt):return p.ToMM(pt.x),p.ToMM(pt.y)
def vec(q):return p.VECTOR2I(p.FromMM(q[0]),p.FromMM(q[1]))
def grid(q):return int(round((q[0]-ox)/step)),int(round((q[1]-oy)/step))
def real(x,y):return round(ox+x*step,5),round(oy+y*step,5)
def nid(q,l=0):x,y=grid(q);return l*area+y*nx+x
def dec(i):return i%nx,(i%area)//nx,i//area
def addtrace(net,points,width=.2,layer=p.F_Cu):
 for a,c in zip(points,points[1:]):
  if a==c:continue
  t=p.PCB_TRACK(b);t.SetStart(vec(a));t.SetEnd(vec(c));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNetCode(net);b.Add(t)
def addvia(net,pt,size=.6,drill=.3):
 for old in b.GetTracks():
  if isinstance(old,p.PCB_VIA) and old.GetNetCode()==net and old.GetPosition()==vec(pt):return
 v=p.PCB_VIA(b);v.SetPosition(vec(pt));v.SetWidth(p.FromMM(size));v.SetDrill(p.FromMM(drill));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(net);b.Add(v)
# Conservative bounding rectangles for pads; track/via circles use exact distance.
padobs=[];pads=[]
for f in b.GetFootprints():
 for pd in f.Pads():
  box=pd.GetBoundingBox();rect=[p.ToMM(box.GetX()),p.ToMM(box.GetY()),p.ToMM(box.GetRight()),p.ToMM(box.GetBottom())]
  ls=[j for j,l in enumerate(layers) if pd.IsOnLayer(l)]
  hole=p.ToMM(max(pd.GetDrillSize().x,pd.GetDrillSize().y))
  if ls:padobs.append((pd.GetNetCode(),rect,ls,hole,pd))
  if pd.GetNumber() and pd.GetNetCode() and not pd.GetNetname().startswith('unconnected-'):pads.append(pd)
def paintrect(a,rect,r=0):
 x1,y1=grid((rect[0]-r,rect[1]-r));x2,y2=grid((rect[2]+r,rect[3]+r));x1=max(0,x1);y1=max(0,y1);x2=min(nx-1,x2);y2=min(ny-1,y2)
 if x2>=x1 and y2>=y1:a[y1:y2+1,x1:x2+1]=1

def paintseg(a,start,end,r):
 x1,y1=grid((min(start[0],end[0])-r,min(start[1],end[1])-r));x2,y2=grid((max(start[0],end[0])+r,max(start[1],end[1])+r));x1=max(0,x1);y1=max(0,y1);x2=min(nx-1,x2);y2=min(ny-1,y2)
 if x2<x1 or y2<y1:return
 xx=ox+np.arange(x1,x2+1)*step; yy=oy+np.arange(y1,y2+1)*step;X=xx[None,:]-start[0];Y=yy[:,None]-start[1];dx=end[0]-start[0];dy=end[1]-start[1];den=dx*dx+dy*dy
 t=np.clip((X*dx+Y*dy)/den,0,1) if den else 0
 mask=(X-dx*t)**2+(Y-dy*t)**2<=r*r
 a[y1:y2+1,x1:x2+1]|=mask.astype(np.uint8)

def obstacles(net,width,vd=.55):
 blocked=np.zeros((NL,ny,nx),np.uint8);vb=np.zeros((ny,nx),np.uint8);clr=.155 if NL==3 else .225
 for a in [*blocked,vb]:
  margin=.525+(vd if a is vb else width)/2
  paintrect(a,[ox,oy,ex,oy+margin]);paintrect(a,[ox,ey-margin,ex,ey]);paintrect(a,[ox,oy,ox+margin,ey]);paintrect(a,[ex-margin,oy,ex,ey])
 # All module antenna keepout is outside board, but preserve it if origin changes.
 for pn,rect,ls,hole,pd in padobs:
  if pn!=net:
   for l in ls:paintrect(blocked[l],rect,clr+width/2)
  # No new via-in-pad (thermal vias already exist in the critical layout).
  paintrect(vb,rect,clr+vd/2)
  if hole:
   # Hole clearance applies on internal layers even if copper not present.
   cp=mm(pd.GetPosition());r=hole/2+.27+width/2
   for l in range(NL):
    if pn!=net:paintseg(blocked[l],cp,cp,r)
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   pt=mm(t.GetPosition());rr=p.ToMM(t.GetWidth(p.F_Cu))/2
   if t.GetNetCode()!=net:
    for a in blocked:paintseg(a,pt,pt,rr+clr+width/2)
   paintseg(vb,pt,pt,rr+vd/2+.21)
  else:
   if t.GetNetCode()==net:continue
   if t.GetLayer() not in layers:continue
   l=layers.index(t.GetLayer());a,c=mm(t.GetStart()),mm(t.GetEnd());rr=p.ToMM(t.GetWidth())/2
   paintseg(blocked[l],a,c,rr+clr+width/2);paintseg(vb,a,c,rr+clr+vd/2)
 vo=1-vb
 # Existing same-net plated vias are legal layer transitions, not obstacles.
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA) and t.GetNetCode()==net:
   x,y=grid(mm(t.GetPosition()))
   if 0<=x<nx and 0<=y<ny and not any(blocked[l,y,x] for l in range(NL)):vo[y,x]=1
 return blocked,vo

def pathfind(a,c,blocked,vo,l1=0,l2=0):
 start=nid(a,l1);goal=nid(c,l2)
 if not(0<=start<NL*area and 0<=goal<NL*area):return None
 # Same-net copper was excluded, so blocked terminals indicate insufficient clearance.
 if blocked.reshape(-1)[start] or blocked.reshape(-1)[goal]:return None
 n=fn(nx,ny,NL,blocked.ctypes.data_as(P8),vo.ctypes.data_as(P8),start,goal,out.ctypes.data_as(PI),len(out),8000000)
 return [dec(int(i)) for i in out[:n]] if n>0 else None

def emit(net,path,a,c,width,vd=.6,drill=.3):
 # Compress collinear steps. Keep a point at each layer transition.
 pts=[]
 for i,q in enumerate(path):
  if i==0 or i==len(path)-1:pts.append(q);continue
  before=tuple(q[j]-path[i-1][j] for j in range(3));after=tuple(path[i+1][j]-q[j] for j in range(3))
  if before!=after:pts.append(q)
 addtrace(net,[a,real(*pts[0][:2])],width,layers[pts[0][2]])
 for q,r in zip(pts,pts[1:]):
  pa,pc=real(*q[:2]),real(*r[:2])
  if q[2]!=r[2]:
   exists=any(isinstance(t,p.PCB_VIA) and t.GetNetCode()==net and grid(mm(t.GetPosition()))==q[:2] for t in b.GetTracks())
   if not exists:addvia(net,pa,vd,drill)
  else:addtrace(net,[pa,pc],width,layers[q[2]])
 addtrace(net,[real(*pts[-1][:2]),c],width,layers[pts[-1][2]])

# Every local decoupler gets its own short path to a GND via before signals.
gnd=b.GetNetcodeFromNetname('GND' if b.GetCopperLayerCount()==4 else '/GND');ground_fail=[]
for pd in pads:
 ref=pd.GetParentFootprint().GetReference()
 if pd.GetNetCode()!=gnd or pd.GetAttribute()!=p.PAD_ATTRIB_SMD:continue
 if b.GetCopperLayerCount()==4 and ref not in ['U10','C35','C36','C37','R54','R55','R56','SW2','SW3','SW7','C25','D2']:continue
 if ref in ['U1','U2','U3']:continue
 first_layer=0 if pd.IsOnLayer(p.F_Cu) else NL-1
 if any(isinstance(t,p.PCB_VIA) and t.GetNetCode()==gnd and math.dist(mm(t.GetPosition()),mm(pd.GetPosition()))<1.0 for t in b.GetTracks()):continue
 a=mm(pd.GetPosition());blocked,vo=obstacles(gnd,.2)
 ax,ay=grid(a);candidates=[]
 for dy in range(-26,27):
  for dx in range(-26,27):
   x,y=ax+dx,ay+dy
   if 0<=x<nx and 0<=y<ny and .5/step<=math.hypot(dx,dy)<=1.3/step and vo[y,x] and not blocked[first_layer,y,x]:candidates.append((dx*dx+dy*dy,x,y))
 for _,x,y in sorted(candidates)[:24]:
  dest=real(x,y);path=pathfind(a,dest,blocked,vo,first_layer,first_layer)
  if path:
   emit(gnd,path,a,dest,.2);addvia(gnd,dest);break
 else:ground_fail.append(ref+'.'+pd.GetNumber())
print('Local GND vias complete; deferred to plane:',ground_fail,flush=True)
# Initial copper groups allow manual power/USB routes to stay intact.
# Restore the reviewed inside-module escape via; route from its B.Cu landing.
if not any(isinstance(t,p.PCB_VIA) and math.dist(mm(t.GetPosition()),(141.2,82.7))<.01 for t in b.GetTracks()):addvia(b.GetNetcodeFromNetname('/GPIO38'),(141.2,82.7),.55,.25)
# Short SCL fanouts preserve fine-pitch escapes before routing the new rear-service bay.
# Work from the via landings; the grid's rectangular pad obstacles are conservative at the IC pins.
if 'service_controls' in json.loads((D.parents[1]/'enclosures/alec-sensor/interface.json').read_text()):
 scl=b.GetNetcodeFromNetname('/GPIO9')
 for points in [[(128.555,89),(128.6,88.955),(128.6,88.45),(129.1,87.95),(129.2,87.95),(130.95,86.2),(131.35,86.2)],[(153.35,78.45),(153.05,78.75),(152.6,78.75),(152.6,79.95),(153.2,80.55),(153.2,81.55)]]:
  for a,c in zip(points,points[1:]):
   if not any(not isinstance(t,p.PCB_VIA) and t.GetNetCode()==scl and t.GetLayer()==p.F_Cu and {tuple(mm(t.GetStart())),tuple(mm(t.GetEnd()))}=={a,c} for t in b.GetTracks()):addtrace(scl,[a,c],.15)
 for xy in [(131.35,86.2),(153.2,81.55)]:addvia(scl,xy,.55,.25)
b.BuildConnectivity();cn=b.GetConnectivity()
by_net={}
for pd in pads:
 if pd.GetNetCode()!=gnd or NL==2:by_net.setdefault(pd.GetNetCode(),[]).append(pd)
def groups_for(pp):
 remaining={pd.m_Uuid.AsString():pd for pd in pp};groups=[]
 while remaining:
  key,pd=next(iter(remaining.items()));todo=[pd];seen=set();group=[]
  while todo:
   item=todo.pop();key=item.m_Uuid.AsString()
   if key in seen:continue
   seen.add(key)
   if key in remaining:group.append(remaining.pop(key))
   for connected in cn.GetConnectedItems(item):
    if isinstance(connected,p.ZONE):continue
    if connected.GetNetCode()==pd.GetNetCode() and connected.m_Uuid.AsString() not in seen:todo.append(connected)
  groups.append(group)
 return groups
ng={n:groups_for(pp) for n,pp in by_net.items()}
# Connectivity through a filled zone does not create an explicit track at a PTH pad.
# On passive daughterboards, provide a trace network as well as the ground pours.
if NL==2 and gnd in by_net:
 ground_tracks=[t for t in b.GetTracks() if t.GetNetCode()==gnd]
 if any(not any(pd.HitTest(t.GetStart()) or pd.HitTest(t.GetEnd()) for t in ground_tracks) for pd in by_net[gnd]):
  ng[gnd]=[[pd] for pd in by_net[gnd]]

power={'/VBAT','/VBAT_FUSED','/VBAT_SW','/PFET','/3v3','/5v'}
def order(n):
 name=b.FindNet(n).GetNetname()
 return (0 if name in power else 1 if name.startswith('/LED_') else 2 if name.startswith('/BTN_') else 4,-sum(len(g) for g in ng[n]))
failed=[];done=0
for net in sorted(ng,key=order):
 groups=ng[net];name=b.FindNet(net).GetNetname()
 if len(groups)<2:continue
 width= .75 if name in ['/VBAT','/VBAT_FUSED','/VBAT_SW'] else .5 if name=='/5v' else .2 if name=='/3v3' else .15;vd=.55 if NL==3 else .6;drill=.25 if NL==3 else .3
 groups.sort(key=len,reverse=True);tree=groups.pop(0);blocked,vo=obstacles(net,width,vd)
 while groups:
  choices=[]
  for gi,group in enumerate(groups):
   for aa in tree:
    if aa.GetParentFootprint().GetReference() in ['U1','U2'] and name in power:continue
    for cc in group:
     if cc.GetParentFootprint().GetReference() in ['U1','U2'] and name in power and len(group)>1:continue
     a,c=mm(aa.GetPosition()),mm(cc.GetPosition())
     if NL==3 and name=='/SW_ON':
      if aa.GetParentFootprint().GetReference()=='R31':a=(104.45,102.75)
      if cc.GetParentFootprint().GetReference()=='R31':c=(104.45,102.75)
     la=0 if aa.IsOnLayer(p.F_Cu) else NL-1;lc=0 if cc.IsOnLayer(p.F_Cu) else NL-1
     if name=='/GPIO38':
      if aa.GetParentFootprint().GetReference()=='U3':a=(141.2,82.7);la=NL-1
      if cc.GetParentFootprint().GetReference()=='U3':c=(141.2,82.7);lc=NL-1
     if name=='/GPIO9':
      landings={'U3':(131.35,86.2),'U5':(153.2,81.55)}
      if aa.GetParentFootprint().GetReference() in landings:a=landings[aa.GetParentFootprint().GetReference()];la=NL-1
      if cc.GetParentFootprint().GetReference() in landings:c=landings[cc.GetParentFootprint().GetReference()];lc=NL-1
     dist=(a[0]-c[0])**2+(a[1]-c[1])**2
     choices.append((dist,gi,a,c,la,lc))
  found=False
  for _,gi,a,c,la,lc in sorted(choices)[:30]:
   path=pathfind(a,c,blocked,vo,la,lc)
   if path:
    emit(net,path,a,c,width,vd,drill);tree.extend(groups.pop(gi));done+=1;found=True;break
  if not found:
   failed.append({'net':name,'groups':[[x.GetParentFootprint().GetReference()+'.'+x.GetNumber() for x in g] for g in groups]});break
  # Same-net additions do not change track clearance, but new holes block more vias.
  blocked,vo=obstacles(net,width,vd)
 p.SaveBoard(str(pcb),b)
 print(name,'remaining',len(groups),'routes',done,flush=True)
b.BuildConnectivity();p.SaveBoard(str(pcb),b)
report={'routed_connections':done,'ground_deferred':ground_fail,'unrouted_groups':failed,'tracks_and_vias':len(b.GetTracks())}
(D/'review/routing-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if failed:raise SystemExit("Routing incomplete; inspect routing-report.json before proceeding")
