"""Real PCB + vendor geometry + parametric enclosure assembly. Run with Blender."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
D=Path(__file__).resolve().parents[1];R=D.parents[1];cfg=json.loads((D/'interface.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.unit_settings.system='METRIC';S.unit_settings.scale_length=.001
S.render.engine='CYCLES';S.cycles.samples=32;S.render.resolution_x=1500;S.render.resolution_y=1200;S.render.resolution_percentage=100
S.world.color=(.22,.22,.22)
exec((R/'enclosures/alec/geometry_helpers.py').read_text(),globals())
def col(name):c=bpy.data.collections.new(name);S.collection.children.link(c);return c
mechanics=col('01 Parametric enclosure');boards=col('02 Actual routed PCB');components=col('03 Vendor component geometry');details=col('04 Assembly hardware and harness');guides=col('05 RF and service guides');studio=col('06 Studio')
parts={}
for part in json.loads((D/'cad-parts.json').read_text()):
 n=part['name']
 if n in ['battery_holder_envelope','radar_pcb_envelope']:continue
 bpy.ops.wm.stl_import(filepath=str(D/'cad'/(n+'.stl')))
 o=bpy.context.object;link(o,n,mechanics,mat(n,part['color']),part['evidence']);parts[n]=o
 # Keep planar faces flat and smooth only the curved side tessellation.
 for poly in o.data.polygons:poly.use_smooth=abs(poly.normal.z)<.98
root,pcbmeshes=import_mm(R/'boards/alec-sensor/docs/assembly.glb',boards,'native_KiCad_S1')
cx,cy=cfg['pcb_center_kicad'];pcb_back=cfg['pcb_front_z']-cfg['pcb_thickness']
root.location=(-cx,cy,pcb_back)
for o in pcbmeshes:o['fit_group']='pcb';o['native_ref']=o.name
# BH3AAW vendor frame: long X, vertical Y, across-cell Z. Remove only long straight cable tails.
hr,holder=import_mm(R/'enclosures/alec/sources/BH3AAW.glb',components,'MPD_BH3AAW_vendor')
for o in holder:
 bm=bmesh.new();bm.from_mesh(o.data)
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(-36.575,0,0),plane_no=(1,0,0),clear_inner=True,clear_outer=False)
 bm.to_mesh(o.data);bm.free();o['cable_note']='Vendor straight 150 mm leads cropped to 8 mm stubs; bent harness is a separate allocation.'
h=cfg['battery_holder'];hx,hy=h['center_xy']
hr.rotation_euler.x=math.pi/2;hr.location=(hx,hy+1.595,h['bottom_z'])
# Manufacturer radar GLB uses millimetres in a metre-declared container. Explicit conversion.
rr,radar=import_mm(D/'sources/HLK-LD2410C.glb',components,'HiLink_LD2410C_vendor')
rr.scale=(.001,.001,.001)
# Exact vendor pin row: first x=157.506; y=42.7. Radar front copper plane z=0.
rd=cfg['radar'];rx,ry=rd['pin1_xy'];rz=rd['face_z']
rr.location=(rx-157.506,ry-42.7,rz)
for o in radar:o['fit_group']='radar';o['source']='HLK STEP converted without geometry simplification'
# AA maximum envelope 14.5 x 50.5 mm; labels are illustrative, no cell brand implied.
cells=[]
for i,y in enumerate([hy-15.55,hy,hy+15.55],1):
 o=cyl(f'AA{i} max-size cell',(hx,y,h['bottom_z']+9.4),7.25,50.5,components,silver,'X',status='IEC/Energizer AA maximum envelope; polarity follows holder markings');cells.append(o)
 for x in [-24.8,24.8]:cyl(f'AA{i} sleeve end',(hx+x,y,h['bottom_z']+9.4),7.27,.8,components,black,'X')
# Hold the radar with a nonmetallic removable clip; socket alone is not positive retention.
clip=box('Radar retention bridge',(18,-5,40.7),(27,2,1.2),details,black,bevel=.2,status='nylon retaining-clip allocation; snaps and strain relief unqualified')
# Narrow contacts are confined to header edge; do not cover radar patch antennas.
for x in [6.2,30.2]:box('Radar clip leg',(x,-5,45.55),(1.4,2,9.7),details,black,status='retaining clip support allocation')
# Service harness follows the trimmed holder exit and lands on the native battery header.
for i,material in enumerate([red,cableblack]):
 tube('Battery harness '+str(i),[(-35.5,5+i*2,10),(-38,5+i*2,21),(-30,-7+i*2,34),(-13+i*2,-10,33)],.6,details,material,status='trimmed 24AWG harness allocation, validate strain relief and actual PH crimp housing')
# Surface finish marks the clear unpainted LED area; front wall remains solid PC in CAD.
lx,ly=cfg['led_xy'];bx,by=cfg['button_xy'];front_z=cfg['shell_depth']
o=cyl('LED optical finish',(lx,ly,front_z+.02),1.2,.03,details,ledmat,status='visualization of unpainted PC window, not a through-hole')
o.data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=1
text3d('ALEC wordmark','alec',(0,12,front_z+.04),5,details,white)
text3d('Pair button mark','•',(bx,by,front_z+.03),3,details,white)
# RF guides are saved hidden; they are engineering allocations, not simulated radiation patterns.
wirebox('ESP antenna 15 mm guide',(-23,17,9),(25,53,42),guides,orange)
wirebox('Radar front gap',(7.029,-20.535,38),(29.029,-4.535,50.4),guides,orange)
for o in guides.objects:o.hide_render=True;o.hide_set(True)
# Studio/cameras.
box('Studio plane',(0,0,-10),(2000,2000,1),studio,mat('Backdrop',(.11,.14,.16)),status='render only')
def camera(name,loc,target,scale):
 data=bpy.data.cameras.new(name);data.type='ORTHO';data.ortho_scale=scale;data.clip_end=5000
 o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def area(name,loc,power,size):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
 o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,20))-o.location).to_track_quat('-Z','Y').to_euler()
area('Key',(0,-100,220),350000,140);area('Fill',(-160,40,160),220000,150);area('Rim',(80,110,180),300000,90);area('Service underside',(-80,80,-160),220000,140)
frontcam=camera('Exterior',(140,-150,200),(0,0,23),162)
internalcam=camera('Internal',(120,-150,190),(0,0,21),168)
rearcam=camera('Rear service',(80,110,-170),(0,0,18),164)
S.camera=frontcam;S['status']=cfg['status'];bpy.context.view_layer.update()
report={'pcb_sha256':hashlib.sha256((R/'boards/alec-sensor/alec-sensor.kicad_pcb').read_bytes()).hexdigest(),'pcb_bounds_mm':bounds(pcbmeshes),'holder_trimmed_bounds_mm':bounds(holder),'radar_bounds_mm':bounds(radar),'dimensions_mm':[cfg['shell_diameter'],cfg['shell_diameter'],cfg['shell_depth']],'scope':'Vendor/PCB nominal geometry and CAD allocations. Refer to cad-checks.json; no waterproof or RF performance claim.'}
(D/'assembly-sources.json').write_text(json.dumps(report,indent=2)+'\n')
bpy.data.texts.new('READ ME - PROTOTYPE').write(json.dumps(report,indent=2)+'\n'+cfg['status'])
bpy.ops.wm.save_as_mainfile(filepath=str(D/'alec-sensor-s1.blend'))
S.render.filepath=str(D/'exterior.png');bpy.ops.render.render(write_still=True)
# Uncovered assembly view retains the actual board and component positions.
for n in ['front_cup','button_membrane','button_retainer','button_plunger','light_pipe']:
 parts[n].hide_render=True
for o in details.objects:
 if o.name.startswith(('LED optical','ALEC wordmark','Pair button')):o.hide_render=True
S.camera=internalcam;S.render.filepath=str(D/'internals.png');bpy.ops.render.render(write_still=True)
# Reverse view: battery carrier removed, internal switch and true PCB underside visible.
for o in mechanics.objects:o.hide_render=True
for o in components.objects:o.hide_render=True
for o in details.objects:o.hide_render=True
for o in studio.objects:
 if o.name=='Studio plane':o.hide_render=True
S.camera=rearcam;S.render.filepath=str(D/'pcb-service.png');bpy.ops.render.render(write_still=True)
print(json.dumps(report,indent=2))
