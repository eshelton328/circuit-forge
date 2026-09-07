"""v4.1 bedside alarm: direct radiator + protected bottom UI. Millimetres.
Actual main PCB is a fit reference, not an electrically revised PCB.
Run: Blender --background --python-exit-code 1 --python build_blender.py
"""
import bpy,bmesh,math,json,hashlib,os
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parent;REPO=R.parents[1]
P=dict(version="4.1",outer_mm=105,corner_radius_mm=7.5,wall_mm=2.4,
 grille_thickness_mm=1.2,grille_cols=22,grille_rows=19,grille_diameter_mm=3.2,
 grille_field_mm=[88,76],grille_z_range_mm=[22,98],
 pcb_transform_origin_mm=[132,98,44],pcb_flip_axis='Y',
 holder_center_xy_mm=[0,13],holder_top_mm=23,
 display_part='EastRising ER-OLEDM013-1W-I2C',display_controller='SH1106',
 display_center_xy_mm=[-18,-29.5],display_pcb_xy_mm=[35.4,33.5],display_pcb_thickness_mm=1.2,
 display_mount_centres_xy_mm=[30.4,28.5],display_hole_diameter_mm=3.0,
 display_glass_xy_mm=[34.5,23.0],display_glass_thickness_mm=1.45,
 display_active_xy_mm=[29.42,14.70],display_active_center_xy_mm=[-18,-31.55],
 display_visual_xy_mm=[31.42,16.70],display_window_xy_mm=[31.8,17.1],
 display_glass_front_z_mm=7.0,display_pcb_front_z_mm=8.6,display_pcb_back_z_mm=9.8,
 display_header_y_mm=-44.25,display_header_pin_x_mm=[-21.81,-19.27,-16.73,-14.19],
 display_header_pitch_mm=2.54,display_header_body_height_mm=2.5,display_header_pin_height_mm=6.0,
 display_allocated_z_mm=[6.8,19.3],display_height_verified=False,
 display_nominal_stack_drawing_checked=True,display_rear_component_allowance_mm=3.0,
 display_mating_socket_xyz_mm=[11,3.5,7],display_connector_verified=False,
 display_movement_vs_v4_mm=[0,1.5,0],front_ui_board_movement_vs_v4_mm=[0,-.5,0],
 speaker_mount_y_mm=-45.0,speaker_center_z_mm=75,speaker_rear_projection_mm=33.5,
 speaker_lug_span_mm=68,speaker_mount_centres_mm=60,speaker_holes_mm=4.2,speaker_body_diameter_mm=52.5,
 speaker_magnet_diameter_mm=45,speaker_cutout_mm=46,speaker_flange_mm=1.5,speaker_excursion_mm=2,
 chamber_outer_bounds_mm=[[-43,-44.5,46.8],[43,8.7,102]],
 chamber_inner_bounds_mm=[[-40.6,-42.1,49.2],[40.6,6.3,99.6]],
 antenna_body_bounds_mm=[[-10,27.75,41.405],[8,34.25,42.405]],antenna_clearance_mm=15,
 rigid_tolerance_budget_mm=1.0,setup_switch='Omron B3F-1060',setup_switch_height_mm=7.0,setup_switch_pretravel_mm=.25,
 setup_switch_board_surface_z_mm=12.8,setup_face_z_mm=4,
 power_switch='E-Switch EG1218 (enable signal only; not battery-load isolation)',
 status='v4.1 packaging prototype; actual main PCB retained as reference; UI board and electrical interfaces require revision; physical qualification not performed')
P['pcb_sha256']=hashlib.sha256((REPO/'boards/esp32s3-devkit-5v/esp32s3-devkit-5v.kicad_pcb').read_bytes()).hexdigest()
source=json.loads((R/'parts/pcb-evidence.json').read_text())
if source['source_pcb_sha256']!=P['pcb_sha256']:
 raise RuntimeError('PCB changed: refresh parts evidence and source GLB before rebuilding enclosure')
P['chamber_gross_air_box_litres']=math.prod(P['chamber_inner_bounds_mm'][1][i]-P['chamber_inner_bounds_mm'][0][i] for i in range(3))/1e6
P['body_volume_reduction_vs_v3_percent']=100*(1-(105/110)**3)
(R/'dimensions.json').write_text(json.dumps(P,indent=2)+'\n')
bpy.ops.wm.read_factory_settings(use_empty=True);S=bpy.context.scene
bpy.context.preferences.filepaths.save_version=0
S.unit_settings.system='METRIC';S.unit_settings.scale_length=.001;S.unit_settings.length_unit='MILLIMETERS'
S['design_status']=P['status'];S['source_pcb_sha256']=P['pcb_sha256']
def col(name):
 c=bpy.data.collections.new(name);S.collection.children.link(c);return c
shell=col('01 Continuous rounded shell | production construction TBD')
walls={n:col('02 '+n+' | 418 real perforations') for n in ['Front','Right','Rear','Left']}
lid=col('03 Integral top | no reflector')
pcbcol=col('04 ACTUAL main PCB | flat components DOWN | electrical reference')
mounts=col('05 Carrier and supports | hardware variants provisional')
holdercol=col('06 MPD BH3AAW | manufacturer CAD')
cellscol=col('07 AA cells | maximum envelopes')
displaycol=col('08 EastRising 1.3 I2C | drawing-based | mated harness AMBER')
controls=col('09 Direct controls | NEW PCB allocation, unrouted')
speakercol=col('10 FRS 5 X | FRONT-facing direct radiator')
cup=col('11 Sealed rear chamber | physical seal untested')
wires=col('12 Harness allocations | electrical endpoints unresolved tagged')
cover=col('13 Bottom cover | retained screw concept')
guides=col('14 Clearance guides | not physical')
studio=col('15 Studio')
panelcol=col('16 Protected bottom setup panel')
scrimcol=col('17 Acoustic cloth allocation | material and insertion loss UNTESTED')
exec((R/'geometry_helpers.py').read_text())

def finish(o,r=.5):
 b=o.modifiers.new('Soft edge','BEVEL');b.width=r;b.segments=4;o.modifiers.new('Normals','WEIGHTED_NORMAL');return o

def rounded_xy(name,size,height,z,r,c,m,group=None):
 # Rounded rectangle extruded in Z; millimetre-exact silhouette.
 vs=[];faces=[];n=16
 for zz in [z-height/2,z+height/2]:
  for cx,cy,start in [(size[0]/2-r,-size[1]/2+r,-90),(size[0]/2-r,size[1]/2-r,0),(-size[0]/2+r,size[1]/2-r,90),(-size[0]/2+r,-size[1]/2+r,180)]:
   for i in range(n+1):
    a=math.radians(start+90*i/n);vs.append((cx+r*math.cos(a),cy+r*math.sin(a),zz))
 N=len(vs)//2;faces=[tuple(reversed(range(N))),tuple(range(N,2*N))]
 for i in range(N):j=(i+1)%N;faces.append((i,j,N+j,N+i))
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(name,me);c.objects.link(o);me.materials.append(m)
 o['evidence_status']='custom_geometry';o['fit_group']=group or 'shell';return o

pcbroot,pcbmeshes=import_mm(R/'sources/current-pcb.glb',pcbcol,'actual_KiCad_export_generic_package_limits_apply')
pcbroot.rotation_euler.y=math.pi;pcbroot.location=P['pcb_transform_origin_mm']
for o in pcbmeshes:o['fit_group']='actual_pcb'

hroot,hmeshes=import_mm(R/'sources/BH3AAW.glb',holdercol,'manufacturer_STEP_body_trimmed_only_at_long_wire_overhang')
for o in hmeshes:
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(-31,0,0),plane_no=(1,0,0),clear_inner=True)
 bm.to_mesh(o.data);bm.free();o['fit_group']='holder'
hroot.rotation_euler.x=-math.pi/2;hroot.location=(0,13-1.595,23)
for i,y in enumerate([-2.125,13,28.125],1):
 cyl('AA %d maximum 14.5 x 50.5'%i,(0,y,12.8),7.25,50.5,cellscol,silver,'X',group='loaded_cells',status='maximum_cell_envelope_contacts_unverified')
 text3d('Cell label %d'%i,'AA  1.5 V',(0,y+1,5.45),3,cellscol,black,(math.pi,0,0))
carrier=box('Battery carrier',(0,13,24),(64,52,2),mounts,light,group='battery_carrier')
for y in [13-19.745,13+19.745]:
 cyl('Holder #2-56 screw head allocation',(0,y,21.85),2.15,.8,mounts,silver,status='hardware_variant_unverified')
 cyl('Holder #2-56 screw shaft allocation',(0,y,23.7),1.092,3,mounts,silver,status='hardware_variant_unverified')
# Carrier legs outside the cell corridor; support the PCB above the carrier.
for x in [-38,38]:
 box('Carrier side rail',(x,13,24),(4,62,2),mounts,light,group='carrier_mount')
 box('Carrier cross arm',(x/2,38,24),(abs(x),3,2),mounts,light,group='carrier_mount')
source=json.loads((R/'parts/pcb-evidence.json').read_text())
pcbholes=[]
for h in source['mounting_holes']:
 x,y=132-h['xy_mm'][0],98-h['xy_mm'][1];pcbholes.append([x,y])
 cyl(h['reference']+' support | OD4 nylon allocation',(x,y,33.7),2,17.4,mounts,light,group='pcb_supports',status='hardware_variant_unverified')
 cyl(h['reference']+' screw head allocation',(x,y,44.7),2,1.2,mounts,silver,status='hardware_variant_unverified')
# Rear supports land on carrier, front supports on separate cross bar.
box('Front PCB support rail',(0,-16,24),(64,6,2),mounts,light,group='pcb_support_rail')
for x in [-38,38]:
 box('Front support rail side link',(x/2,-16,24),(abs(x),3,2),mounts,light)

# A flat protected setup face. Only glass, actuators and cells are exposed.
panel=rounded_xy('Protected setup face | electronics behind', [98,98],2,5,5,panelcol,light,'service_panel')
boolean(panel,box('Battery access opening',(0,13,5),(64,52,8),panelcol,None))
boolean(panel,box('Display active viewing opening',(-18,-31.55,5),(31.8,17.1,8),panelcol,None))
# Manufacturer drawing p6: I2C-only FOUR-pin variant. Header towards front (-Y).
# Display faces down. Glass front Z7; rear PCB face Z9.8 (2.8 drawing stack).
db=box('ER-OLEDM013-1W-I2C PCB | 35.4 x 33.5 x 1.2',(-18,-29.5,9.2),(35.4,33.5,1.2),displaycol,green,group='display',status='manufacturer_p6_nominal_drawing')
for x in [-33.2,-2.8]:
 for y in [-43.75,-15.25]:
  boolean(db,cyl('OLED hole diameter 3',(x,y,9.2),1.5,5,displaycol,None))
  st=cyl('OLED standoff | M2.5 allocation',(x,y,7.3),2.25,2.6,mounts,light,group='display_mounts',status='custom_mount_hardware_unselected')
  boolean(st,cyl('OLED support pilot',(x,y,7.3),1.05,5,mounts,None))
  cyl('OLED M2.5 screw shaft allocation',(x,y,8.1),1.25,5,mounts,silver,group='display_mounts',status='M2.5_hardware_unselected')
  cyl('OLED screw head allocation',(x,y,10.6),2.25,1.6,mounts,silver,group='display_mounts',status='M2.5_hardware_unselected')
box('ER OLED glass | 34.5 x 23 x 1.45',(-18,-29.5,7.725),(34.5,23,1.45),displaycol,black,group='display',status='manufacturer_p6_nominal_drawing')
box('ER OLED visual area | offset 2.05 toward header',(-18,-31.55,6.995),(31.42,16.7,.01),displaycol,black,group='display',status='manufacturer_p6_nominal_drawing')
box('ER OLED active area 128 x 64',(-18,-31.55,6.98),(29.42,14.7,.02),displaycol,black,group='display',status='manufacturer_p6_nominal_drawing')
text3d('OLED example screen','07:00\nREADY',(-18,-29.93,6.955),3.585,displaycol,white,(math.pi,0,0))
box('ER OLED header spacer | four positions',(-18,-44.25,11.05),(10.16,2.5,2.5),displaycol,black,group='display',status='manufacturer_height_pitch_inferred_housing_outline')
for n,x in enumerate(P['display_header_pin_x_mm'],1):
 box('OLED header pin %d | %s'%(n,['GND','VCC','SCL','SDA'][n-1]),(x,-44.25,15.3),(.64,.64,6),displaycol,silver,group='display',status='manufacturer_p6_pin_dimensions_p8_signals')
 cyl('OLED solder tail %d'%n,(x,-44.25,7.7),.65,1.8,displaycol,silver,group='display',status='1.8_drawing_projection_solder_profile_simplified')
socket=box('OLED 2.54 female socket | mating allocation',(-18,-44.25,15.8),(11,3.5,7),displaycol,amber,.15,group='display_connector',status='mating_MPN_and_envelope_unverified')
for x in P['display_header_pin_x_mm']:
 boolean(socket,box('OLED socket contact cavity',(x,-44.25,15.3),(.85,.85,6.1),displaycol,None))
# Small board close to the panel; three direct switches, no custom plungers.
cb=box('NEW control PCB | 27 x 34 unrouted',(26.5,-30,13.6),(27,34,1.6),controls,amber,group='new_control_pcb',status='unrouted_board_allocation')
for x,y in [(15.5,-37),(15.5,-25),(38,-43),(38,-16)]:
 boolean(cb,cyl('Control PCB M2 hole',(x,y,13.6),1.1,5,controls,None))
 cyl('Control PCB support allocation',(x,y,9.4),2.25,6.8,mounts,black,status='M2_hardware_variant_unselected')
 cyl('Control PCB screw head',(x,y,15.3),1.9,1.8,mounts,silver,status='M2_hardware_variant_unselected')
for y,label in [(-43,'+'),(-31,'SET'),(-19,'-')]:
 boolean(panel,cyl('Setup switch aperture',(20,y,5),5,8,panelcol,None))
 box('B3F-1060 body '+label,(20,y,11.1),(6,6,3.4),controls,black,group='direct_controls',status='manufacturer_dimension_envelope_simplified')
 cyl('B3F-1060 direct actuator '+label,(20,y,7.6),1.75,3.6,controls,white,group='direct_controls',status='manufacturer_7mm_height_0.25mm_nominal_travel')
 well=cyl('Short protected button well '+label,(20,y,7.7),5,3.4,controls,black,group='direct_controls',status='custom_finger_well_clearance_unqualified')
 boolean(well,cyl('Finger well bore',(20,y,7.7),3.5,6,controls,None))
 # Four lead allocations, kept behind panel; 6.5 x 4.5 pin grid.
 for dx in [-3.25,3.25]:
  for dy in [-2.25,2.25]:cyl('Tactile lead',(20+dx,y+dy,14.4),.3,3.2,controls,silver,status='lead_profile_simplified')
 text3d('Setup label '+label,label,(29,y+1,3.95),2.8,panelcol,white,(math.pi,0,0))
# Direct top-actuated power enable switch: envelope to be confirmed from drawing.
boolean(panel,box('Enable switch access',(36,-29,5),(5.5,15,8),panelcol,None))
box('EG1218 switch envelope',(36,-29,10.1),(4,11.6,5.4),controls,silver,group='direct_controls',status='drawing_based_envelope')
box('EG1218 direct actuator',(36,-30,6.4),(2,2,2),controls,black,.2,group='direct_controls',status='2mm_actuator_simple_profile')
for yy in [-31.5,-29,-26.5]:
 box('EG1218 PCB lead',(36,yy,15.15),(.5,.6,4.7),controls,silver,status='drawing_terminal_envelope')
text3d('Power label','ON',(36,-39,3.95),2.3,panelcol,white,(math.pi,0,0))
text3d('Standby label','OFF',(36,-20,3.95),2.3,panelcol,white,(math.pi,0,0))
text3d('Setup title','SETUP',(-18,-45.5,3.95),2.2,panelcol,white,(math.pi,0,0))
text3d('Battery caption','3 x AA  |  1.5 V',(-5,44.5,3.95),2.3,panelcol,white,(math.pi,0,0))
# A screw-fastened cell retention bridge and a pull ribbon; materials / force TBD.
ret=box('Cell retention bridge | remove captive screw to service',(0,13,4.5),(8,54,1.0),panelcol,black,.3,group='cell_retention',status='retention_material_force_and_captive_detail_unverified')
for y in [-13,39]:
 cyl('Retention bridge screw head',(0,y,3.65),2.3,.7,panelcol,silver,status='captive_fastener_unselected')
# Pull ribbon is a flexible service aid, not a rigid withdrawal obstruction.
box('Cell pull ribbon | flexible 6 mm allocation',(-12,13,5.3),(6,48,.3),panelcol,amber,status='ribbon_material_and_route_unverified')

# Compact front check UI behind the solid lower band. One lens, normally dark.
box('NEW front UI board allocation',(0,-48.3,12),(24,1.6,10),controls,amber,group='front_ui',status='unrouted_front_UI_board')
cyl('Exterior check button',(-6,-52.45,12),3.7,1.3,controls,black,'Y',group='front_ui',status='cap_stroke_and_switch_interface_unverified')
cyl('ONE RGB lens normally off',(6,-52.45,12),1.2,.5,controls,ledmat,'Y',group='front_ui',status='lens_MPN_unselected')
# Simple battery icon beside button, on the same small interface group.
icon=box('Battery icon outline',(-6,-53.12,12),(3.6,.035,1.9),controls,white,.1)
boolean(icon,box('Icon inside',(-6,-53.12,12),(3,.2,1.3),controls,None))
box('Battery icon terminal',(-4.05,-53.12,12),(.3,.035,.65),controls,white)

# Build speaker in local Z; rotate so acoustic axis points toward -Y.
# Datums and diameters match manufacturer drawing; basket is simplified.
sp_root=bpy.data.objects.new('Speaker FRONT axis -Y',None);speakercol.objects.link(sp_root)
flange=cyl('FRS 5 X flange diameter 52.5',(0,0,.75),26.25,1.5,speakercol,black,group='speaker',status='drawing_based_envelope')
boolean(flange,cyl('Flange diaphragm aperture',(0,0,.75),22.7,5,speakercol,None))
for x in [-30,30]:
 lug=box('FRS 5 X lug 68 overall',(x,0,.75),(8,10,1.5),speakercol,black,group='speaker',status='mount_centres_and_span_known_lug_profile_simplified')
 boolean(lug,cyl('4.2 speaker fixing hole',(x,0,.75),2.1,5,speakercol,None))
 cyl('Speaker screw allocation',(x,0,3),2.75,3,speakercol,silver,status='hardware_unselected')
 cyl('Speaker screw shaft',(x,0,-2),1.5,9,speakercol,silver,status='hardware_unselected')
cyl('FRS 5 X magnet | rear datum known',(0,0,-25.5),22.5,16,speakercol,silver,group='speaker',status='diameter_and_rear_datum_known_axial_split_unverified')
bpy.ops.mesh.primitive_cone_add(vertices=96,radius1=22.5,radius2=22.9,depth=17.5,location=(0,0,-8.75))
link(bpy.context.object,'FRS 5 X basket profile simplified',speakercol,black,group='speaker',status='basket_profile_unverified')
bpy.ops.mesh.primitive_cone_add(vertices=96,radius1=10,radius2=22.6,depth=3.5,location=(0,0,-1))
link(bpy.context.object,'Diaphragm visualization',speakercol,black,status='decorative_not_moving_clearance')
cyl('Dust cap',(0,0,1),7,.7,speakercol,black,status='decorative')
box('Speaker terminal allocation',(24,-12,-8),(6,8,5),speakercol,amber,group='speaker_terminal',status='terminal_location_unverified')
for o in list(speakercol.objects):
 if o!=sp_root:o.parent=sp_root
sp_root.rotation_euler.x=math.pi/2;sp_root.location=(0,-45.7,75)

# Rear shell is a simple sealed rectangular pod, independent of four grilles.
baffle=box('Front baffle',(0,-44,74.4),(86,2.4,55.2),cup,light,group='rear_chamber')
boolean(baffle,cyl('46 mm acoustic cutout',(0,-44,75),23,7,cup,None,'Y'))
for x in [-30,30]:boolean(baffle,cyl('Speaker screw through baffle',(x,-44,75),1.6,7,cup,None,'Y'))
box('Chamber back',(0,6.8,74.4),(86,2.4,55.2),cup,light,group='rear_chamber')
for x in [-41.8,41.8]:box('Chamber side',(x,-18.6,74.4),(2.4,48.4,55.2),cup,light,group='rear_chamber')
box('Chamber floor',(0,-18.6,48),(81.2,48.4,2.4),cup,light,group='rear_chamber')
box('Chamber roof',(0,-18.6,100.8),(81.2,48.4,2.4),cup,light,group='rear_chamber')
gasket=cyl('Driver gasket | 0.5 compressed allocation',(0,-45.45,75),26,.5,cup,black,'Y',status='gasket_material_unselected')
boolean(gasket,cyl('Gasket centre',(0,-45.45,75),23,4,cup,None,'Y'))
for x in [-30,30]:
 boss=cyl('Blind speaker fixing boss',(x,-40.3,75),4.5,5,cup,light,'Y',status='blind_insert_detail_unselected')
 boolean(boss,cyl('Blind fixing pilot',(x,-42.85,75),1.6,8.3,cup,None,'Y'))
# Closed feedthrough represented by a seal body; no free acoustic port.
box('Sealed two-wire feedthrough allocation',(41.8,-25,60),(3,6,6),cup,amber,.3,status='seal_process_and_wire_bond_unverified')
# Pod is installed on removable carrier outside antenna volume.
for x in [-46,46]:
 box('Pod mounting rail',(x,-20,46),(4,62,3),mounts,light,.4,group='pod_mount')
 for y in [-39,0]:
  box('Pod mounting ear',(x*.95,y,47),(8,7,2),mounts,light,.3,group='pod_mount')
# Outer supports stay out of bottom battery opening and RF antenna zone.
for x in [-45,45]:
 for y in [-43,43]:
  boolean(panel,cyl('Setup panel corner clearance',(x,y,5),1.7,6,panelcol,None))
  cyl('Chassis corner post',(x,y,26),2.6,40,mounts,charcoal,group='chassis_post')
# Battery carrier attaches to corner structure.
for x in [-40,40]:
 box('Carrier corner link',(x,40,24),(10,5,2),mounts,light,group='carrier_mount')

# Connector mating envelopes on the actual downward PCB; explicitly allocated.
box('J1 PH mating plug allocation',(13,-12,35),(8,6,7),wires,white,.3,group='battery_harness',status='mated_geometry_unverified')
box('J3 PH mating plug allocation',(-29,-8.5,35),(6,8,7),wires,white,.3,group='speaker_harness',status='mated_geometry_unverified')
box('J4 2.54 female socket allocation',(-29,8,33.5),(3.5,11,7),wires,black,.3,group='display_harness',status='mated_geometry_unverified')
for d,m in [(-.6,red),(.6,cableblack)]:
 tube('Battery lead allocation',[(-31,0+d,15),(-34,-7+d,22),(-33,-12+d,29),(13,-15+d,29),(13,-12+d,31.5)],.5,wires,m,group='battery_harness')
for d,m in [(-.6,red),(.6,cableblack)]:
 tube('Speaker lead allocation',[(-29,-8.5+d,31.5),(-36,-20+d,31),(-36,-36+d,35),(46,-36+d,35),(47,-25+d,60),(44,-25+d,60)],.5,wires,m,group='speaker_harness')
 tube('Sealed feedthrough wire',[(44,-25+d,60),(40,-25+d,60)],.5,wires,m,group='sealed_feedthrough_wire',status='intentional_sealed_wall_penetration')
 tube('Speaker internal lead allocation',[(40,-25+d,60),(32,-30+d,65),(25,-36+d,63)],.5,wires,m,group='speaker_harness')
tube('OLED cable allocation',[(-29,8,30),(-38,2,29),(-40,-29,27),(-30,-44.25,24),(-18,-44.25,23),(-18,-44.25,19.3)],1,wires,wireblue,group='display_harness')
# These end at proposed connector zones, NOT on imaginary pins of the demo PCB.
tube('NEW control harness to proposed connector zone',[(36,-14,12),(40,-12,23),(36,-22,29)],1, wires,wireblue,status='unrouted_electrical_interface',group='new_harness')
tube('NEW front UI harness to proposed connector zone',[(8,-48.3,15),(22,-41,22),(36,-22,29)],.9,wires,wireblue,status='unrouted_electrical_interface',group='new_harness')
wirebox('NEW low-speed connector zone | revise PCB',[29,-27,27],[40,-17,34],guides,amber)
wirebox('USB cable insertion | lift chassis for development service',[32,4,36],[62,16,46],guides,amber)

# Shift the pod 0.7 mm inward to reserve movement clearance to the cloth.
sp_root.location.y += .7
for o in cup.objects:o.location.y += .7
for o in wires.objects:
 if o.type=='CURVE' and o.name.startswith(('Speaker internal','Sealed feedthrough')):
  for sp in o.data.splines:
   for b in sp.bezier_points:b.co.y += .7
 if o.type=='CURVE' and o.name.startswith('Speaker lead'):
  o.data.splines[0].bezier_points[-1].co.y += .7
# One continuous visual skin with rounded corners; fields use exact tile corners.
outer=rounded_xy('Rounded shell frame',[105,105],102.3,53.85,7.5,shell,charcoal)
inner=rounded_xy('Shell hollow cutter',[100.2,100.2],107,53,5.1,shell,charcoal)
boolean(outer,inner)
for wi,name in enumerate(['Front','Right','Rear','Left']):
 a=wi*math.pi/2
 cut=box('Grille frame opening',(0,-51.5,60),(88,8,76),shell,None)
 cut.location=Matrix.Rotation(a,4,'Z')@cut.location;cut.rotation_euler.z=a;boolean(outer,cut)
boolean(outer,cyl('Check cap aperture',(-6,-52,12),4,8,shell,None,'Y'))
boolean(outer,cyl('Single lens aperture',(6,-52,12),1.4,8,shell,None,'Y'))
# Perforated fields are separate meshes for review, same material, flush seams.
for wi,name in enumerate(['Front','Right','Rear','Left']):
 verts=[];faces=[];nx,ny=22,19;dx=dz=4
 for ix in range(nx):
  for iz in range(ny):
   x=-44+(ix+.5)*dx;z=22+(iz+.5)*dz;base=len(verts)
   for ring in [0,1]:
    for k in range(16):
     side,t=k//4,(k%4)/4
     ux,uz=[(2,-2+t*4),(2-t*4,2),(-2,2-t*4),(-2+t*4,-2)][side]
     if ring:rr=math.hypot(ux,uz);ux,uz=1.6*ux/rr,1.6*uz/rr
     verts.append((x+ux,-52.5,z+uz))
   for k in range(16):j=(k+1)%16;faces.append((base+k,base+j,base+16+j,base+16+k))
 me=bpy.data.meshes.new(name+' grille');me.from_pydata(verts,[],faces);me.update()
 o=bpy.data.objects.new(name+' | 418 perforations',me);walls[name].objects.link(o);me.materials.append(charcoal);o.rotation_euler.z=wi*math.pi/2
 w=o.modifiers.new('Weld shared edges','WELD');w.merge_threshold=.0001
 so=o.modifiers.new('Thin grille inward','SOLIDIFY');so.thickness=1.2;so.offset=-1
 o['fit_group']='shell';o['perforation_count']=418
# Top blends into frame with no additional decorative seam.
top=rounded_xy('Integral solid top',[105,105],2.4,103.8,7.5,lid,charcoal,'lid')
u=outer.modifiers.new('Integral roof union','BOOLEAN');u.operation='UNION';u.object=top
bpy.context.view_layer.objects.active=outer;bpy.ops.object.modifier_apply(modifier=u.name);bpy.data.objects.remove(top,do_unlink=True)
finish(outer,.25)
for wi,name in enumerate(['Front','Right','Rear','Left']):
 cloth=box(name+' acoustic cloth allocation',(0,-51.05,60),(88,.2,76),scrimcol,black,group='acoustic_scrim',status='nonconductive_cloth_MPN_and_acoustic_impedance_unselected')
 cloth.location=Matrix.Rotation(wi*math.pi/2,4,'Z')@cloth.location;cloth.rotation_euler.z=wi*math.pi/2
base=rounded_xy('Screw-fastened bottom cover',[104.5,104.5],2.4,1.2,7.25,cover,charcoal,'bottom_cover')
for x in [-45,45]:
 for y in [-43,43]:
  boolean(base,cyl('Cover screw hole',(x,y,1),1.7,7,cover,None))
  cyl('Captive screw head concept',(x,y,-.6),2.7,1.2,cover,silver,status='captive_screw_and_retainer_unselected')
  cyl('Captive screw shaft concept',(x,y,3),1.5,7,cover,silver,status='captive_screw_and_retainer_unselected')
  ring=cyl('Captive retainer washer allocation',(x,y,3),2.5,.4,cover,black,status='retention_groove_and_fastener_unselected')
  boolean(ring,cyl('Retainer bore',(x,y,3),1.3,2,cover,None))
for x in [-40,40]:
 for y in [-40,40]:cyl('Non-slip foot allocation',(x,y,-1.5),5,3,cover,black,status='foot_material_and_MPN_unselected')
lo,hi=P['antenna_body_bounds_mm'];rflo=[v-15 for v in lo];rfhi=[v+15 for v in hi]
wirebox('15 mm antenna envelope',rflo,rfhi,guides,orange)
wirebox('Cell withdrawal after bridge released',[-31,-12,-30],[30,37,23],guides,blue)
wirebox('OLED rear components | unverified 3 mm allowance',[-35.7,-46.25,9.8],[-.3,-12.75,12.8],guides,amber)
wirebox('OLED complete module and socket envelope',[-35.7,-46.25,6.8],[-.3,-12.75,19.3],guides,amber)
wirebox('Maximum diaphragm motion',[-23,-48.5,52],[23,-43.0,98],guides,amber)

# Studio and separate useful saved views.
def camera(name,loc,target,scale):
 bpy.ops.object.camera_add(location=loc);o=link(bpy.context.object,name,studio);o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale;o.data.clip_end=5000;return o
frontcam=camera('CAM Exterior',(180,-245,155),(0,0,50),173)
rearcam=camera('CAM Rear',(-180,245,155),(0,0,50),173)
cutcam=camera('CAM Internal side',(-180,-240,150),(0,0,53),180)
sectioncam=camera('CAM Acoustic side',(220,-100,120),(0,0,62),173)
bottomcam=camera('CAM Protected bottom',(0,-65,-230),(0,0,30),150)
for name,loc,power,size in [('Key',(20,-130,230),1000000,160),('Fill',(-140,-15,100),700000,140),('Rim',(110,140,175),850000,120),('Bottom',(10,-70,-140),450000,130)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=link(bpy.context.object,name,studio);o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,50))-o.location).to_track_quat('-Z','Y').to_euler()
ground=box('Studio ground',(0,0,-4),(2000,2000,1),studio,floor_mat)
S.render.filepath='//preview.png'
S.world=bpy.data.worlds.new('Studio world');S.world.color=(.18,.18,.18)
S.render.engine='CYCLES';S.cycles.samples=32;S.cycles.use_denoising=True
S.render.resolution_x=S.render.resolution_y=1500;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.view_settings.view_transform='AgX'
def visible(c,state):
 for o in c.objects:o.hide_render=not state;o.hide_set(not state)
def render(name,cam):
 S.camera=cam;S.render.filepath='//'+name;bpy.ops.render.render(write_still=True)
def save(name,cam):
 S.camera=cam
 for a in bpy.context.screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.clip_end=5000;a.spaces.active.shading.type='MATERIAL'
 bpy.ops.wm.save_as_mainfile(filepath=str(R/name))
def do_render(name,cam):
 if os.environ.get('CUBE_SKIP_RENDER')!='1':render(name,cam)
visible(guides,False);bpy.context.view_layer.update()
evidence=dict(pcb_bounds_mm=bounds(pcbmeshes),holder_trimmed_bounds_mm=bounds(hmeshes),pcb_mesh_count=len(pcbmeshes),pcb_hole_centres_mm=pcbholes,rf_guide_bounds_mm=[rflo,rfhi],scene_units_m=.001,source_pcb_sha256=P['pcb_sha256'])
(R/'assembly-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
bpy.data.texts.new('START HERE - v4.1').write(P['status']+'\n\nRead DISPLAY-UPDATE.md, DESIGN-REVIEW.md and TEST-REPORT.md.\n105 mm body, 3 AA, actual flat main PCB, direct front speaker.\nFour grilles are perforated; sound is directed primarily through FRONT.\nNo reflector or long button extensions. Amber = provisional or unrouted.\nBottom setup board and front UI board require electrical design.\nFirmware, acoustic performance, RF, thermal, EMC and purchased part fit remain unqualified.\n')
save('bedroom-cube-v4-1.blend',frontcam);do_render('exterior-front-right.png',frontcam);do_render('exterior-rear-left.png',rearcam)
# Remove outer shell for an honest assembly view; speaker pod remains closed.
visible(shell,False);visible(lid,False);visible(scrimcol,False)
for c in walls.values():visible(c,False)
save('bedroom-cube-v4-1-internals.blend',cutcam);do_render('internals.png',cutcam)
# Separate cutaway opens just the chamber side and roof, showing sealed topology.
for o in cup.objects:
 if o.name.startswith('Chamber roof') or (o.name.startswith('Chamber side') and o.location.x>0):o.hide_render=True;o.hide_set(True)
save('bedroom-cube-v4-1-acoustic-cutaway.blend',sectioncam);do_render('acoustic-cutaway.png',sectioncam)
visible(guides,True);save('bedroom-cube-v4-1-clearances.blend',sectioncam);do_render('clearances.png',sectioncam);visible(guides,False)
# Bottom view is assembled, only removable outer cover absent.
visible(shell,True);visible(lid,True);visible(cup,True);visible(scrimcol,True)
for c in walls.values():visible(c,True)
visible(cover,False);ground.hide_render=True;ground.hide_set(True)
save('bedroom-cube-v4-1-service.blend',bottomcam);do_render('bottom-service.png',bottomcam)
print('V4.1 built',json.dumps(evidence))
