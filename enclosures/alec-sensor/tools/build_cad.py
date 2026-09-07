#!/usr/bin/env python3
"""Parametric millimetre CAD using free CadQuery. Nominal prototype, not tooling release."""
from pathlib import Path
import math,json,hashlib
import cadquery as cq
D=Path(__file__).resolve().parents[1];R=D.parents[1];cfg=json.loads((D/'interface.json').read_text());out=D/'cad';out.mkdir(exist_ok=True)
parts=[]
def box(x,y,z,dx,dy,dz):return cq.Workplane('XY').box(dx,dy,dz).translate((x,y,z))
def cyl(x,y,z,r,h):return cq.Workplane('XY').circle(r).extrude(h).translate((x,y,z))
def add(name,s,color,status='custom nominal geometry'):
 assert s.val().isValid(),name
 cq.exporters.export(s,str(out/(name+'.step')))
 cq.exporters.export(s,str(out/(name+'.stl')),tolerance=.06,angularTolerance=.15)
 parts.append((name,s,color,status))
rad=cfg['shell_diameter']/2;depth=cfg['shell_depth'];front=depth-cfg['radome_wall'];cover=cfg['rear_cover'];opening=cfg['rear_seal']['opening_radius']
# One-piece PC cup: rear flange below z=6, full cavity above it, uninterrupted radar face.
shell=cyl(0,0,cover,rad,depth-cover)
try:shell=shell.edges('>Z').fillet(2)
except Exception:pass
shell=shell.cut(cyl(0,0,cover-.01,opening,6-cover+.02)).cut(cyl(0,0,6,rad-cfg['side_wall'],front-6))
# Groove is in the stationary cup. Hard cover-to-flange contact sets 25% nominal O-ring squeeze.
groove=cyl(0,0,cover-.01,52.4,1.51).cut(cyl(0,0,cover-.02,49.6,1.53));shell=shell.cut(groove)
rear=cyl(0,0,0,rad,cover)
for i in range(6):
 angle=math.radians(i*60);x,y=55*math.cos(angle),55*math.sin(angle)
 # Blind M2 insert pilot cavities OUTSIDE the main seal. Exact insert tolerances pending.
 shell=shell.cut(cyl(x,y,cover,1.6,3.2))
 rear=rear.cut(cyl(x,y,-.01,1.1,cover+.02)).cut(cyl(x,y,-.01,2,1))
 add(f'rear_screw_{i+1}',cyl(x,y,.2,1.9,.8).union(cyl(x,y,1,1,4)),(.62,.64,.67),'M2x4 counterbored hardware envelope; final insert/torque pending')
# PCB screws enter from rear; posts stop on component-side mounting annuli.
for i,(kx,ky) in enumerate(cfg['pcb_mounts_kicad'],1):
 cx,cy=cfg['pcb_center_kicad'];x,y=kx-cx,cy-ky
 # The lower-right post stops below the radar; a side rib carries it.
 boss=cyl(x,y,26,3.45,5 if i==4 else front-26).cut(cyl(x,y,25.9,1.25,8))
 if i==4:
  rib=box(43,y,30,30,3,2).intersect(cyl(0,0,29,rad,2))
  boss=boss.union(rib)
 shell=shell.union(boss)
 add(f'pcb_screw_{i}',cyl(x,y,22.4,2.75,2).union(cyl(x,y,24.4,1.5,6)),(.62,.64,.67),'M3x6 hardware envelope; boss engagement/tolerance pending')
# Front button: flexible membrane separates the dry mechanism from water.
bx,by=cfg['button_xy'];shell=shell.cut(cyl(bx,by,front-.01,6,4))
# Inner counterbore captures a silicone flange under an independent retainer.
shell=shell.cut(cyl(bx,by,front-.01,9,.91))
membrane=cyl(bx,by,front,9,.9).union(cyl(bx,by,front+.9,6,2.7))
add('button_membrane',membrane,(.09,.11,.12),'custom silicone: 1.2 mm free flange / 0.9 mm installed (25% nominal squeeze); tolerances, force and fatigue unqualified')
# 0.15 mm gap to selected TS-1187A actuator; a guided plastic rod stops on the membrane.
rod_bottom=cfg['button_top_z']+cfg['button_nominal_free_gap'];rod_top=front
plunger=cyl(bx,by,rod_bottom,.8,rod_top-rod_bottom).union(cyl(bx,by,front-1,4,1))
add('button_plunger',plunger,(.17,.21,.24),'nylon plunger: force, alignment and travel require tolerance test')
retainer=cyl(bx,by,front-1.2,10.5,1.2).cut(cyl(bx,by,front-1.3,5,1.4))
for dy_button in [-12.5,12.5]:
 # Two M2 clamps above/below the membrane; the outer relief stays outside its 9 mm flange.
 shell=shell.union(cyl(bx,by+dy_button,front-2.4,2.8,3.3).cut(cyl(bx,by+dy_button,front-2.5,1,3.4)))
 tab=cyl(bx,by+dy_button,front-3.6,2.8,1.2).union(box(bx,by+dy_button/2,front-3,4,abs(dy_button),1.2))
 tab=tab.cut(cyl(bx,by+dy_button,front-3.7,1.1,1.4))
 retainer=retainer.union(tab).union(cyl(bx,by+dy_button/2,front-3.6,1.5,3.6))
 retainer=retainer.cut(cyl(bx,by+dy_button,front-2.4,2.9,2.5))
retainer=retainer.cut(cyl(bx,by,front-3.7,5,3.8))
# Clear the nearby PCB boss and the separate plunger-guide support post.
retainer=retainer.cut(cyl(-28,-11,front-3.7,3.6,3.8)).cut(cyl(bx+12,by,front-3.7,2.2,3.8))
add('button_retainer',retainer,(.19,.22,.24))
guide=cyl(bx,by,30,2.4,front-31).cut(cyl(bx,by,29.9,1.1,front-30.8))
support=guide.union(box(bx+6,by,front-3,12,2,2)).union(cyl(bx+12,by,front-4,2,4))
support=support.cut(cyl(bx,by,29.9,1.1,front-29.8))
shell=shell.union(support)
# Optical window is the same unbroken PC face. The light pipe needs no wet-side hole.
lx,ly=cfg['led_xy'];add('light_pipe',cyl(lx,ly,28.2,1.4,front-28.2),(.6,.95,.7),'clear PC optical allocation; diffusion/brightness pending')
# Rear cover holds the holder. Locators are outside the exact body envelope.
h=cfg['battery_holder'];hx,hy=h['center_xy'];dx,dy,dz=h['size']
for sign in [-1,1]:
 rear=rear.union(box(hx+sign*(dx/2+1),hy,3.1,1.5,dy+2,1.4))
 rear=rear.union(box(hx,hy+sign*(dy/2+1),3.1,dx+2,1.5,1.4))
# Support bars establish holder height. A removable nonpenetrating retainer remains a mechanical allocation.
for x in [-20,20]:rear=rear.union(box(x,hy,2.9,4,dy+4,1))
# External rails support a removable mounting cradle. All screw slots remain outside the sealed volume.
for x in [-32,32]:rear=rear.union(box(x,0,-1.5,4,35,3))
cradle=box(0,0,-5.5,76,52,4).cut(box(0,0,-5.5,52,28,5))
for x in [-32,32]:
 cradle=cradle.union(box(x,0,-2.5,7,38,3)).cut(box(x,0,-1.5,4.5,35.5,3.2))
for y in [-20,20]:cradle=cradle.cut(cyl(0,y,-8,2.2,6)).cut(cyl(0,y+3,-8,4.1,6))
add('mounting_cradle',cradle,(.12,.15,.16),'screw slots / adhesive plate / suction adaptor interface; retention and tilt testing pending')
add('front_cup',shell,(.24,.29,.29));add('rear_cover',rear,(.2,.25,.25))
# O-ring shown as compressed elliptical cross section, 2 mm free cord -> 1.5 mm installed height.
# Installed O-ring is an annular bounding envelope, not the unloaded circular cord.
# Use a bounded annular envelope if a kernel interprets the workplane revolve differently.
oring=cyl(0,0,cover,52.25,1.5).cut(cyl(0,0,cover-.01,49.75,1.52))
add('rear_oring_installed_envelope',oring,(.025,.03,.035),'100x2 mm EPDM candidate, 25% nominal squeeze; cross section drawn as bounding envelope')
# Vendor body geometry is retained separately; STEP frame here places its exact body envelope.
add('battery_holder_envelope',box(hx,hy,h['bottom_z']+dz/2,dx,dy,dz),(.1,.14,.19),'BH3AAW exact drawing envelope; vendor STEP rendered in Blender instead')
rd=cfg['radar'];rx,ry=rd['pin1_xy'];x1,y1,x2,y2=rd['body_xy_relative_pin1'];z=rd['face_z'];th=rd['pcb_thickness']
radar=box(rx+(x1+x2)/2,ry+(y1+y2)/2,z-th/2,x2-x1,y2-y1,th)
add('radar_pcb_envelope',radar,(.02,.23,.34),'HLK drawing/CAD exact outline, component/header envelope added in Blender')
assembly=cq.Assembly()
for name,s,col,status in parts:assembly.add(s,name=name,color=cq.Color(*col))
assembly.save(str(D/'alec-sensor-s1-mechanical.step'))
# Useful checks are explicitly narrow: body fit, stack gaps, and seal nominal compression.
max_radius=max(math.hypot(hx+sx*dx/2,hy+sy*dy/2) for sx in [-1,1] for sy in [-1,1])
clearance_pairs=[('front_cup','button_retainer'),('front_cup','button_membrane'),('front_cup','button_plunger'),('front_cup','radar_pcb_envelope'),('front_cup','battery_holder_envelope'),('button_retainer','button_plunger'),('button_retainer','light_pipe')]
shapes={n:s for n,s,_,_ in parts}
intersections={a+' / '+b:shapes[a].intersect(shapes[b]).val().Volume() for a,b in clearance_pairs}
assert all(v<1e-5 for v in intersections.values()),intersections
checks={'checked_intersections_mm3':intersections,'holder_radial_clearance_at_rear_opening_mm':opening-max_radius,'holder_to_pcb_underside_mm':cfg['pcb_front_z']-cfg['pcb_thickness']-(h['bottom_z']+dz),'holder_to_pcb_screw_head_mm':22.4-(h['bottom_z']+dz),'radar_face_to_front_inner_mm':front-z,'rear_seal_nominal_squeeze_percent':25,'body_volume_valid':shell.val().isValid(),'body_depth_mm':depth,'body_diameter_mm':rad*2,'radar_face_stack_mm':cfg['pcb_front_z']+rd['socket_height']+rd['male_header_spacer']+th,'scope':'Nominal envelopes, not all-component interference or sealing/thermal/RF qualification.'}
assert checks['holder_radial_clearance_at_rear_opening_mm']>1
assert checks['holder_to_pcb_screw_head_mm']>1
assert abs(checks['radar_face_to_front_inner_mm']-12.4)<.01
assert abs(checks['radar_face_stack_mm']-z)<.01
(D/'cad-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
(D/'cad-parts.json').write_text(json.dumps([{'name':n,'color':c,'evidence':s} for n,_,c,s in parts],indent=2)+'\n')
print(json.dumps(checks,indent=2))
