"""V4.2 PCB integration prototype. Preserve v4.1 as a separately verified reference.
Run with Blender. Imports actual native-board exports, not placeholder board boxes.
"""
import bpy,math,json,hashlib,os
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parent;E=R.parent;REPO=E.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(E/'bedroom-cube-v4-1.blend'));S=bpy.context.scene
exec((E/'geometry_helpers.py').read_text(),globals())
def col(name):
 c=bpy.data.collections.new(name);S.collection.children.link(c);return c
boards=col('16 PRODUCT PCBs v4.2');parts=col('17 Product interface mechanics');cables=col('18 Product UI harness allocations');guides=col('19 Product service fixture guide')
# Replace the old electrical reference and all unrouted UI component allocations.
remove=[]
for o in list(S.objects):
 if any(c.name.startswith('04 ACTUAL') for c in o.users_collection):remove.append(o);continue
 if o.name.startswith(('NEW control PCB','NEW front UI board','B3F-1060 body','B3F-1060 direct actuator','Tactile lead','EG1218 switch','EG1218 direct actuator','EG1218 PCB lead','NEW low-speed connector zone','NEW controls harness','NEW front UI harness')):remove.append(o)
for o in remove:bpy.data.objects.remove(o,do_unlink=True)
# The old amber controls cable name is retained nowhere; check exact prefix below.
for o in list(S.objects):
 if o.get('evidence_status')=='unrouted_electrical_interface':bpy.data.objects.remove(o,do_unlink=True)
roots={};meshes={}
for kind in ['main','controls','front']:
 root,obs=import_mm(R/'sources'/f'{kind}.glb',boards,'native_'+kind)
 if kind=='main':root.rotation_euler.y=math.pi;root.location=(132,98,44)
 elif kind=='controls':root.rotation_euler.y=math.pi;root.location=(40,-13,14.4)
 else:root.rotation_euler.x=math.pi/2;root.location=(-12,-47.5,17)
 for o in obs:o['fit_group']='product_'+kind;o['native_reference']=o.name;o.name=kind+'::'+o.name
 roots[kind]=root;meshes[kind]=obs
bpy.context.view_layer.update()
# Add exact connector/body maximum allocations from JST GH drawing. Actual headers are in GLBs.
# Mated top-entry assembly 7.3 mm above its PCB mounting surface; wire-bend allowance is separate.
def mating(name,lo,hi):
 o=box(name,[(a+b)/2 for a,b in zip(lo,hi)],[b-a for a,b in zip(lo,hi)],parts,amber,group='mated_envelope',status='JST_GH_drawing_maximum_allocation_not_exact_housing_mesh');return o
# Native BM headers have body center y=-0.375, mirrored by KiCad on B.Cu.
mating('Main J5 mated GH7', [16,-26,35.1],[28,-21.7,42.4])
mating('Main J6 mated GH6',[-18.375,-26,35.1],[-7.625,-21.7,42.4])
mating('Controls J1 mated GH7',[25,-39.95,14.4],[37,-35.65,21.7])
mating('Front J1 mated GH6',[.625,-47.5,11],[11.375,-40.2,15.3])
# Cable envelopes use 200 mm maximum wire lengths with strain relief; route south of antenna.
tube('GH7 setup cable',[(31,-38,22),(35,-35,27),(28,-29,32),(22,-23.85,35.1)],1.5,cables,wireblue,group='product_cable',status='7xAWG28_bundle_allocation_length_limit_200mm')
tube('GH6 front cable',[(6,-40.2,13.2),(8,-37,20),(-4,-35,28),(-10,-30,32),(-13,-23.85,35.1)],1.4,cables,wireblue,group='product_cable',status='6xAWG28_bundle_allocation_length_limit_200mm')
# Two M2 mounts. The left screw is above the OLED rear envelope; right is below GH header.
for x,z in [(-10.3,15.3),(10.3,8.5)]:
 cyl('Front PCB boss',(x,-49.6,z),2.1,1,parts,light,'Y',group='front_mount',status='M2_boss_thread_or_insert_and_wall_attachment_unqualified')
 cyl('Front PCB screw shank',(x,-48.8,z),1,4.2,parts,silver,'Y',group='front_mount',status='M2_4mm_hardware_allocation')
 cyl('Front PCB screw head',(x,-46.7,z),1.9,1.6,parts,silver,'Y',group='front_mount',status='M2_head_envelope_unselected_variant')
# Nominal cap-to-switch linkage: B3U top is 1.6 mm above front PCB face.
# Flange assembles from inside before PCB; axial free play .05 mm; no final tolerance approval.
cyl('Check cap central stem',(-6,-51.275,12),.5,1.05,parts,black,'Y',group='front_actuator',status='nominal_0.05mm_switch_gap_tolerance_unqualified')
flange=cyl('Check cap rear retaining flange',(-6,-49.85,12),4.5,.5,parts,black,'Y',group='front_actuator',status='retained_by_inner_wall_M2_board_removed_for_assembly')
boolean(flange,cyl('Flange clears switch body',(-6,-49.85,12),2.5,2,parts,None,'Y'))
boolean(flange,cyl('Flange relief around upper left boss',(-10.3,-49.85,15.3),2.3,2,parts,None,'Y'))
for x in [-9.2,-2.8]:box('Cap retention leg',(x,-50.95,12),(.65,1.7,1),parts,black,group='front_actuator',status='cap_flange_integral_leg_prototype')
# Small light-pipe envelope bridges the selected RGB package and existing lens.
cyl('RGB light-pipe allocation',(6,-51.75,12),.9,.9,parts,ledmat,'Y',group='light_pipe',status='optical_material_diffusion_and_exact_gap_unqualified')
# Probe path stays between OLED and controls, forward of the main support rail.
panel=next(o for o in S.objects if o.name=='Protected setup face | electronics behind')
boolean(panel,box('UART access cut',(6,-25,5),(10,12,5),parts,None))
probe=box('J7 2x3 spring-probe corridor',(6,-25,22.2),(8,10,40.4),guides,amber,group='service_corridor',status='custom_3v3_UART_fixture_allocation_not_off_the_shelf_programmer')
probe.hide_render=True;probe.hide_set(True)
# Show the three actual boards and preserve the approved shell/acoustic geometry.
S['design_status']='v4.2 integrated PCB prototype; ERC/DRC pass; mechanical tolerances and physical qualification pending'
S['source_pcb_sha256']=hashlib.sha256((REPO/'boards/bedroom-alarm-main/bedroom-alarm-main.kicad_pcb').read_bytes()).hexdigest()
source={k:{'pcb':'boards/bedroom-alarm-'+k+'/bedroom-alarm-'+k+'.kicad_pcb','pcb_sha256':hashlib.sha256((REPO/'boards'/('bedroom-alarm-'+k)/('bedroom-alarm-'+k+'.kicad_pcb')).read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256((R/'sources'/f'{k}.glb').read_bytes()).hexdigest(),'bounds_mm':bounds(meshes[k])} for k in meshes}
(R/'assembly-sources.json').write_text(json.dumps(source,indent=2)+'\n')
bpy.data.texts.new('V4.2 PCB INTEGRATION').write(S['design_status']+'\nRead README.md and TEST-REPORT.md alongside this model.\nAmber connector/fixture/cable shapes are conservative allocations, not purchased mating-part CAD.\n')
# Hide old guides; all physical objects remain in saved complete assembly.
for o in S.objects:
 if any(c.name.startswith(('14 ','19 ')) for c in o.users_collection):o.hide_render=True;o.hide_set(True)
S.camera=bpy.data.objects['CAM Exterior'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'bedroom-cube-v4-2.blend'))
# Internal review render with shell and cover hidden, saved as a separate view.
for o in S.objects:
 if any(c.name.startswith(('01 ','02 ','03 ','12 ','13 ')) for c in o.users_collection):o.hide_render=True;o.hide_set(True)
S.camera=bpy.data.objects['CAM Internal side'];S.render.resolution_x=1600;S.render.resolution_y=1200;S.cycles.samples=24
S.render.filepath=str(R/'internals.png');bpy.ops.wm.save_as_mainfile(filepath=str(R/'bedroom-cube-v4-2-internals.blend'))
if os.environ.get('CUBE_SKIP_RENDER')!='1':bpy.ops.render.render(write_still=True)
print(json.dumps(source,indent=2))
