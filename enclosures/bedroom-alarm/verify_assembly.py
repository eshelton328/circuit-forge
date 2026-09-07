"""Independent saved-scene geometry checks; no physical qualification claims."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;REPO=R.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'bedroom-cube-v4-1.blend'))
S=bpy.context.scene;P=json.loads((R/'dimensions.json').read_text());deps=bpy.context.evaluated_depsgraph_get()
checks=[];failures=[]
def check(name,ok,**kw):
 checks.append(dict(name=name,passed=bool(ok),**kw))
 if not ok:failures.append(name)
def bounds(obs):
 pts=[o.matrix_world@Vector(p) for o in obs for p in o.bound_box]
 return [[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]
def gap(a,b):return max(max(a[0][i]-b[1][i],b[0][i]-a[1][i]) for i in range(3))
def triangle_box(vs,lo,hi):
 # Separating-axis triangle/AABB test, including triangle-plane and edge axes.
 c=(Vector(lo)+Vector(hi))/2;half=(Vector(hi)-Vector(lo))/2;v=[p-c for p in vs]
 e=[v[1]-v[0],v[2]-v[1],v[0]-v[2]];basis=[Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))]
 for ax in basis+[e[0].cross(e[1])]+[edge.cross(b) for edge in e for b in basis]:
  if ax.length_squared<1e-16:continue
  projection=[p.dot(ax) for p in v];radius=sum(half[i]*abs(ax[i]) for i in range(3))
  if min(projection)>radius+1e-5 or max(projection)<-radius-1e-5:return False
 return True
def mesh_hits_box(o,bb):
 if gap(bounds([o]),bb)>=-.0001:return False
 e=o.evaluated_get(deps);me=e.to_mesh();me.calc_loop_triangles();mat=o.matrix_world
 verts=[mat@v.co for v in me.vertices]
 hit=any(triangle_box([verts[i] for i in t.vertices],*bb) for t in me.loop_triangles)
 e.to_mesh_clear();return hit

def ray(o,origin,direction,distance):
 inv=o.matrix_world.inverted();return o.evaluated_get(deps).ray_cast(inv@Vector(origin),inv.to_3x3()@Vector(direction),distance=distance)[0]
physical=[o for o in S.objects if o.type in ['MESH','CURVE'] and not o.hide_render and not any(c.name.startswith(('14 ','15 ')) for c in o.users_collection)]
pcbcol=next(c for c in bpy.data.collections if c.name.startswith('04 ACTUAL'));pcb=[o for o in pcbcol.objects if o.type=='MESH'];body=next(o for o in pcb if '_PCB.' in o.data.name)
bb=bounds([body]);check('Actual 64 x 56 mm PCB scale',abs(bb[1][0]-bb[0][0]-64)<.05 and abs(bb[1][1]-bb[0][1]-56)<.05,bounds_mm=bb)
check('Main PCB hash unchanged',hashlib.sha256((REPO/'boards/esp32s3-devkit-5v/esp32s3-devkit-5v.kicad_pcb').read_bytes()).hexdigest()==P['pcb_sha256'],sha256=P['pcb_sha256'])
check('Actual main PCB flat and component-side down',bounds([bpy.data.objects['U3']])[1][2]<bb[0][2]+.02)
source=json.loads((R/'parts/pcb-evidence.json').read_text())
for h in source['mounting_holes']:
 x,y=132-h['xy_mm'][0],98-h['xy_mm'][1];o=next(o for o in S.objects if o.name.startswith(h['reference']+' support'))
 check(h['reference']+' real mounting-hole alignment',not ray(body,(x,y,47),(0,0,-1),8) and abs(o.location.x-x)<.001 and abs(o.location.y-y)<.001,xy_mm=[x,y])
wallresults=[]
for name in ['Front','Right','Rear','Left']:
 o=bpy.data.objects[name+' | 418 perforations'];e=o.evaluated_get(deps);hits=misses=0
 # These are local coordinates, so each rotation gets the same exact field audit.
 for i in range(22):
  for j in range(19):
   x=-44+(i+.5)*4;z=22+(j+.5)*4
   hits+=e.ray_cast(Vector((x,-54,z)),Vector((0,1,0)),distance=4)[0]
   misses+=not e.ray_cast(Vector((x+1.8,-54,z)),Vector((0,1,0)),distance=4)[0]
 me=e.to_mesh();bm=bmesh.new();bm.from_mesh(me);nm=sum(not q.is_manifold for q in bm.edges);eu=len(bm.verts)-len(bm.edges)+len(bm.faces);bm.free();e.to_mesh_clear()
 result=dict(wall=name,holes=418,blocked_holes=hits,missing_webs=misses,nonmanifold_edges=nm,euler=eu)
 wallresults.append(result);check(name+' perforations and closed webs',hits==misses==nm==0 and eu==2-2*418,**result)
groups={}
for o in physical:
 if o.get('fit_group'):groups.setdefault(o['fit_group'],[]).append(o)
gbs={k:bounds(obs) for k,obs in groups.items()}
for a,b in [('actual_pcb','holder'),('actual_pcb','battery_carrier'),('actual_pcb','display'),('actual_pcb','rear_chamber'),('holder','display'),('holder','new_control_pcb'),('loaded_cells','bottom_cover'),('battery_harness','battery_carrier'),('display_harness','battery_carrier'),('new_control_pcb','display')]:
 d=gap(gbs[a],gbs[b])
 if a.endswith('_harness'):
  hits=[o.name for o in groups[a] if mesh_hits_box(o,gbs[b])]
  check(a+' clear of '+b,not hits,method='triangle/box against solid carrier',obstacles=hits)
 else:check(a+' separated from '+b,d>0,gap_mm=round(d,4))
rf=[[v-15 for v in P['antenna_body_bounds_mm'][0]],[v+15 for v in P['antenna_body_bounds_mm'][1]]]
rf_bad=[o.name for o in physical if o not in pcb and mesh_hits_box(o,rf)]
check('15 mm RF envelope free of foreign modeled geometry',not rf_bad,obstacles=rf_bad,box_mm=rf,note='Triangle/box test resolves hollow-shell false positives. RF performance still requires measurements.')
# Withdrawal is tested after removing the outer cover and retention bridge/ribbon.
withdraw=[[-30,-11.5,-30],[29.5,37.5,23]]
exclude_prefix=('Holder #2','Cell retention','Retention bridge','Cell pull','Battery lead')
obstacles=[]
for o in physical:
 if any(c.name.startswith(('06 ','07 ','13 ')) for c in o.users_collection) or o.name.startswith(exclude_prefix):continue
 if mesh_hits_box(o,withdraw):obstacles.append(o.name)
check('Bottom cell withdrawal has no foreign rigid obstruction',not obstacles,obstacles=obstacles,note='Cover and retention bridge released. Does not test spring force, grip or own holder contacts.')
# Speaker direction from its actual transform, not a label.
root=bpy.data.objects['Speaker FRONT axis -Y'];axis=root.matrix_world.to_3x3()@Vector((0,0,1))
check('Speaker axis points directly toward front grille',axis.dot(Vector((0,-1,0)))>.9999,axis=list(axis))
cone_front=P['speaker_mount_y_mm']-P['speaker_flange_mm']-P['speaker_excursion_mm'];grille_inner=-52.5+1.2;d=cone_front-grille_inner
check('Maximum forward diaphragm envelope clears grille',d>=2,gap_mm=round(d,3),remaining_after_1mm_rigid_budget_mm=round(d-1,3))
rear=P['speaker_mount_y_mm']+P['speaker_rear_projection_mm'];back=6.3
check('Driver rear envelope clears rear chamber wall',back-rear>=2,gap_mm=round(back-rear,3))
check('Maximum diaphragm envelope clears allocated acoustic cloth',cone_front-(-50.95)>=2,gap_mm=round(cone_front+50.95,3),note='Cloth deflection and material not qualified')
# Baffle aperture and direct-ray checks at front grille hole centres within driver.
baffle=bpy.data.objects['Front baffle'];front=bpy.data.objects['Front | 418 perforations'];paths=0;blocked=[]
for i in range(22):
 for j in range(19):
  x=-44+(i+.5)*4;z=22+(j+.5)*4
  if x*x+(z-75)**2<20**2:
   paths+=1
   # Outward from maximum forward diaphragm. Front grille must pass hole rays.
   for o in physical:
    if o in pcb or o.get('fit_group') in ['speaker','acoustic_scrim'] or o.parent==root:continue
    if ray(o,(x,cone_front-.05,z),(0,-1,0),4):blocked.append(o.name)
check('Direct sound path has no rigid reflector or duct obstruction; cloth loss untested',paths>50 and not blocked,open_rays=paths,obstacles=sorted(set(blocked)))
# All five closed pod faces physically stop rays; front must have its aperture.
wall_tests=[('Chamber back',(0,0,75),(0,1,0)),('Chamber floor',(0,-20,55),(0,0,-1)),('Chamber roof',(0,-20,95),(0,0,1)),('Chamber side',(35,-20,75),(1,0,0)),('Chamber side',(-35,-20,75),(-1,0,0))]
closed=[]
for name,origin,direction in wall_tests:
 obs=[o for o in physical if o.name.startswith(name)];closed.append(any(ray(o,origin,direction,15) for o in obs))
check('Rear pod five walls are closed at test rays',all(closed),wall_hits=closed,scope='Nominal wall continuity, not a seal-pressure or leakage test')
check('Driver baffle has open 46 mm central aperture',not ray(baffle,(0,-50,75),(0,1,0),10) and ray(baffle,(25,-50,75),(0,1,0),10))
check('Long control extensions removed',not any('plunger' in o.name.lower() or 'reach shaft' in o.name.lower() for o in physical),switch_board_to_actuator_mm=7.0,external_actuator_extension_mm=0)
# Protected panel aperture ray tests for the direct actuators.
panel=bpy.data.objects['Protected setup face | electronics behind']
check('Three direct controls accessible through panel',all(not ray(panel,(20,y,0),(0,0,1),7) for y in [-43,-31,-19]),aperture_diameter_mm=10)
# No falsely dimensioned display claim and no invisible functional fake PCB.
check('Unqualified display mating hardware and UI interfaces remain explicit',P['display_nominal_stack_drawing_checked'] and not P['display_height_verified'] and not P['display_connector_verified'] and bpy.data.objects['NEW control PCB | 27 x 34 unrouted'].get('evidence_status')=='unrouted_board_allocation')
# Critical custom-component clearances use actual mesh triangles if AABBs overlap.
internal_bad=[]
for o in groups['actual_pcb']+groups['battery_harness']+groups['display_harness']+groups['speaker_harness']:
 for c in groups['rear_chamber']:
  # Pod feedthrough and internal speaker lead are intended penetrations.
  if o.name.startswith('Speaker internal'):continue
  if mesh_hits_box(o,bounds([c])):internal_bad.append([o.name,c.name])
check('PCB and external connector/harness allocations clear sealed pod',not internal_bad,aabb_candidates=internal_bad)
# v4.1-specific checks derive actual geometry from the saved scene.
db=bpy.data.objects['ER-OLEDM013-1W-I2C PCB | 35.4 x 33.5 x 1.2']
dbb=bounds([db]);sizes=[dbb[1][i]-dbb[0][i] for i in range(3)]
check('I2C-only module outline and PCB thickness match drawing p6',all(abs(a-b)<.002 for a,b in zip(sizes,[35.4,33.5,1.2])),measured_mm=sizes)
for x in [-33.2,-2.8]:
 for y in [-43.75,-15.25]:
  check('OLED mounting hole at %.2f, %.2f'%(x,y),not ray(db,(x,y,12),(0,0,-1),4) and ray(db,(x+1.7,y,12),(0,0,-1),4),hole_diameter_mm=3.0)
glass=bpy.data.objects['ER OLED glass | 34.5 x 23 x 1.45'];gb=bounds([glass])
check('Glass front and PCB back implement drawing 2.8 mm stack',abs(gb[0][2]-7)<.002 and abs(dbb[1][2]-gb[0][2]-2.8)<.002,glass_front_z_mm=gb[0][2],pcb_back_z_mm=dbb[1][2])
active=bpy.data.objects['ER OLED active area 128 x 64'];ab=bounds([active])
check('Active area is 29.42 x 14.7 with 2.05 mm offset toward header',abs(ab[1][0]-ab[0][0]-29.42)<.002 and abs(ab[1][1]-ab[0][1]-14.7)<.002 and abs(active.location.y-db.location.y+2.05)<.002,active_bounds_mm=ab)
# AA edge/corner rays through panel, with 0.3 mm offset allowance and angular viewing margin.
blocked=[]
for x in [ab[0][0]-.3,ab[1][0]+.3]:
 for y in [ab[0][1]-.3,ab[1][1]+.3]:
  if ray(panel,(x,y,0),(0,0,1),6.1):blocked.append([x,y])
check('Enlarged window exposes active area including 0.3 mm offset allowance',not blocked,blocked_corner_rays=blocked,window_mm=[31.8,17.1],nominal_edge_margin_mm=[1.19,1.2],note='Normal viewing tested; recessed glass limits extreme viewing angles. No lens selected.')
# Budget is a screening reserve, not a completed worst-case production tolerance stack.
rear_allow=[[-35.7,-46.25,9.8],[-.3,-12.75,12.8]]
display_checks={
 'display PCB to front UI PCB':(dbb,bounds([bpy.data.objects['NEW front UI board allocation']])),
 'display PCB to holder':(dbb,gbs['holder']),
 'display PCB to battery withdrawal corridor':(dbb,withdraw),
 'rear component allowance to front UI PCB':(rear_allow,bounds([bpy.data.objects['NEW front UI board allocation']])),
 'rear component allowance to holder':(rear_allow,gbs['holder']),
 'display socket to front UI PCB':(gbs['display_connector'],bounds([bpy.data.objects['NEW front UI board allocation']])),
 'display module to main PCB':(gbs['display'],gbs['actual_pcb'])}
for name,(a,b) in display_checks.items():
 d=gap(a,b);check(name+' retains 1 mm screening reserve',d>=.999,gap_mm=round(d,4),remaining_after_1mm_reserve_mm=round(d-1,4))
check('Display glass is recessed clear of protected panel',gb[0][2]-6>=.99,gap_mm=round(gb[0][2]-6,3),note='Separate from lateral 1 mm reserve; actual glass/PCB tolerances and mount height still require fit check')
# Each display mount must clear neighboring board, holder and cell-service path.
mount_bad=[]
for o in groups['display_mounts']:
 for name,ob in [('front UI',bounds([bpy.data.objects['NEW front UI board allocation']])),('holder',gbs['holder']),('cell corridor',withdraw)]:
  if gap(bounds([o]),ob)<.5-.001:mount_bad.append([o.name,name,gap(bounds([o]),ob)])
check('OLED mounts have at least 0.5 mm nominal neighbor clearance',not mount_bad,obstacles=mount_bad,note='Final screw head and pilot details unselected; this is not a full tolerance approval')
pins=[bpy.data.objects['OLED header pin %d | %s'%(n,name)] for n,name in enumerate(['GND','VCC','SCL','SDA'],1)]
check('Four header pins use drawing p8 signal order and 2.54 mm pitch',all(abs(pins[i+1].location.x-pins[i].location.x-2.54)<.002 for i in range(3)) and all(abs(o.location.y+44.25)<.002 for o in pins),pins_1_to_4=['GND','VCC','SCL','SDA'],note='Modeled signal mapping; no continuity or power test has been performed')
# The cable is tested against neighboring solid envelopes; intended display socket mating excluded.
cable=bpy.data.objects['OLED cable allocation'];cable_bad=[]
obstacles_for_cable=[bpy.data.objects['NEW front UI board allocation'],db,glass]+groups['battery_carrier']+groups['holder']+groups['pcb_supports']+groups['display_mounts']
for o in obstacles_for_cable:
 if mesh_hits_box(cable,bounds([o])):cable_bad.append(o.name)
check('Rerouted OLED cable avoids module, mounts, holder, carrier and front UI',not cable_bad,obstacles=cable_bad,note='Allocated 2 mm cable diameter; exact connector, bend radius and strain relief remain to select')

check('Blender assembly is self-contained',not bpy.data.libraries and all(i.packed_file or i.source in ['GENERATED','VIEWER'] for i in bpy.data.images),linked_libraries=[l.filepath for l in bpy.data.libraries])
overall=bounds(physical)
result=dict(tested_blend_sha256=hashlib.sha256((R/'bedroom-cube-v4-1.blend').read_bytes()).hexdigest(),status='NOMINAL_GEOMETRY_CHECKS_PASS' if not failures else 'GEOMETRY_FAILURES',physical_qualification_performed=False,manufacturing_release=False,
 failed_checks=failures,checks=checks,wall_results=wallresults,overall_physical_bounds_mm=overall,
 overall_physical_size_mm=[round(overall[1][i]-overall[0][i],3) for i in range(3)],measured_group_bounds_mm=gbs,
 acoustic_gross_chamber_litres=P['chamber_gross_air_box_litres'],net_acoustic_volume_verified=False,
 unresolved=['EastRising shipped I2C-only revision, back-side component maxima, exact mating socket and cable bend; SH1106 firmware and switched-power bench tests','Switch, holder and PCB dimensional tolerances; loaded AA contact compression',
 'Control/front UI board schematics, connectors and routed PCB revision','USB access by chassis removal; detailed detachable chassis fasteners and harness service loop',
 'Captive screw hardware, retention bridge, gasket and sealed feedthrough production details',
 'Speaker basket displacement and terminals; measured net acoustic volume',
 'Grille strength, vibration, acoustic loss and four-direction response','Actual battery-load, radio, thermal, EMI and parasitic measurements'])
# Compare unchanged geometry to the actual saved v4 scene, not copied parameters.
def snapshot():
 dg=bpy.context.evaluated_depsgraph_get();out={}
 selected_prefix=('01 ','02 ','04 ','06 ','07 ','10 ','11 ','13 ','17 ')
 for o in bpy.context.scene.objects:
  if o.type not in ['MESH','CURVE']:continue
  chosen=any(c.name.startswith(selected_prefix) for c in o.users_collection) or o.get('fit_group') in ['battery_carrier','pcb_supports','pod_mount'] or o.name in ['Exterior check button','ONE RGB lens normally off','NEW control PCB | 27 x 34 unrouted']
  if not chosen:continue
  e=o.evaluated_get(dg);me=e.to_mesh()
  vertices=[[round(q,4) for q in o.matrix_world@v.co] for v in me.vertices]
  polygons=[list(p.vertices) for p in me.polygons]
  out[o.name]=hashlib.sha256(json.dumps([vertices,polygons]).encode()).hexdigest();e.to_mesh_clear()
 return out
updated=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(R/'reference/bedroom-cube-v4.blend'))
baseline=snapshot();changes=sorted(k for k in set(baseline)|set(updated) if baseline.get(k)!=updated.get(k))
check('V4 exterior, main PCB, speaker pod, batteries and control PCB geometry preserved',not changes,compared_objects=len(baseline),changed_objects=changes,method='SHA-256 of evaluated world-space vertices rounded to 0.0001 mm and face indices from both saved scenes')
result['status']='NOMINAL_GEOMETRY_CHECKS_PASS' if not failures else 'GEOMETRY_FAILURES'
result['preserved_v4_objects']=len(baseline)
(R/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'failed_checks':failures,'checks':len(checks),'RF_obstacles':rf_bad,'withdraw_obstacles':obstacles,'pod_candidates':internal_bad},indent=2))
if failures:raise RuntimeError('Geometry checks failed')
