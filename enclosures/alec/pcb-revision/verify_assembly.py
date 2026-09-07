"""Independent tests against the saved v4.2 assembly, including mating and probe access."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;E=R.parent;REPO=E.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'alec-cube-v4-2.blend'));S=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
checks=[]
def check(name,passed,**details):checks.append(dict(name=name,passed=bool(passed),**details))
def bounds(obs):
 pts=[o.matrix_world@Vector(p) for o in obs for p in o.bound_box]
 return [[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]
def gap(a,b):return max(max(a[0][i]-b[1][i],b[0][i]-a[1][i]) for i in range(3))
def triangle_box(vs,lo,hi):
 c=(Vector(lo)+Vector(hi))/2;half=(Vector(hi)-Vector(lo))/2;v=[p-c for p in vs]
 e=[v[1]-v[0],v[2]-v[1],v[0]-v[2]];basis=[Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))]
 for ax in basis+[e[0].cross(e[1])]+[edge.cross(b) for edge in e for b in basis]:
  if ax.length_squared<1e-16:continue
  projection=[p.dot(ax) for p in v];radius=sum(half[i]*abs(ax[i]) for i in range(3))
  if min(projection)>radius+1e-5 or max(projection)<-radius-1e-5:return False
 return True
def mesh_hits_box(o,bb):
 if gap(bounds([o]),bb)>=-.0001:return False
 e=o.evaluated_get(deps);me=e.to_mesh();me.calc_loop_triangles();verts=[o.matrix_world@v.co for v in me.vertices]
 hit=any(triangle_box([verts[i] for i in t.vertices],*bb) for t in me.loop_triangles)
 e.to_mesh_clear();return hit

def physical(o):return o.type in ['MESH','CURVE'] and not any(c.name.startswith(('14 ','15 ','19 ')) for c in o.users_collection)
def group(k):return [o for o in S.objects if o.get('fit_group')==k]
source=json.loads((R/'assembly-sources.json').read_text())
for kind in ['main','controls','front']:
 row=source[kind];check(kind+' native PCB and export hashes',hashlib.sha256((REPO/row['pcb']).read_bytes()).hexdigest()==row['pcb_sha256'] and hashlib.sha256((R/'sources'/f'{kind}.glb').read_bytes()).hexdigest()==row['glb_sha256'])
 body=next(o for o in group('product_'+kind) if '_PCB' in o.data.name)
 bb=bounds([body]);size=[round(bb[1][i]-bb[0][i],3) for i in range(3)]
 wanted={'main':[64,56,1.51],'controls':[27,34,1.51],'front':[24,1.51,10]}[kind]
 check(kind+' PCB size and orientation',all(abs(a-b)<.05 for a,b in zip(size,wanted)),size_mm=size,bounds_mm=bb)
for a,b in [('product_main','holder'),('product_main','battery_carrier'),('product_main','display'),('product_main','rear_chamber'),('product_main','product_controls'),('product_main','product_front'),('product_controls','display'),('product_controls','holder')]:
 distance=gap(bounds(group(a)),bounds(group(b)));check(a+' / '+b+' clear',distance>0,minimum_axis_gap_mm=distance)
oled_boxes=[[[-35.7,-46.25,6.8],[-.3,-12.75,12.8]],[[-23.5,-46,12.3],[-12.5,-42.5,19.3]]]
for what,objects in [('Front PCB and parts',group('product_front')),('Front screws',group('front_mount')),('GH mating envelopes',group('mated_envelope')),('UI cables',group('product_cable'))]:
 hits=[o.name for o in objects if any(mesh_hits_box(o,bb) for bb in oled_boxes)];check(what+' clear OLED board, rear allowance and socket',not hits,intersections=hits)
# Cable/plug envelopes must clear holder, carrier, acoustic chamber, controls and each other where not mated.
for o in group('mated_envelope')+group('product_cable'):
 for g in ['holder','battery_carrier','pcb_support_rail','rear_chamber']:
  hits=[p.name for p in group(g) if mesh_hits_box(o,bounds([p]))]
  check(o.name+' clear '+g,not hits,intersections=hits)
rf=[[-25,12.75,26.405],[23,49.25,57.405]]
objects=group('product_controls')+group('product_front')+group('mated_envelope')+group('product_cable')+group('front_mount')
hits=[o.name for o in objects if mesh_hits_box(o,rf)];check('All new UI parts and harnesses outside antenna keepout',not hits,intersections=hits)
probe=[[2,-30,2],[10,-20,42.39]]
# The setup face has an actual opening. Main board is intended termination; guides omitted.
objects=[o for o in S.objects if physical(o) and o.get('fit_group') not in ['product_main','bottom_cover'] and not any(c.name.startswith('13 ') for c in o.users_collection)]
hits=[o.name for o in objects if mesh_hits_box(o,probe)];check('Unobstructed spring-probe body corridor behind removed cover',not hits,intersections=hits,envelope_mm=probe)
# Mounting pattern and switch actuator centers are tested against actual exported component meshes.
for name,xy in [('SW1',(20,-19)),('SW2',(20,-31)),('SW3',(20,-43))]:
 obs=[o for o in group('product_controls') if o.get('native_reference')==name];bb=bounds(obs)
 check(name+' control actuator position and exposed height',abs((bb[0][0]+bb[1][0])/2-xy[0])<.1 and abs((bb[0][1]+bb[1][1])/2-xy[1])<.1 and abs(bb[0][2]-5.8)<.12,bounds_mm=bb)
# Exported B3U's plunger face, not its body headline dimension, defines the stem gap.
switch=bounds([o for o in group('product_front') if o.get('native_reference')=='SW1']);stem=bounds([bpy.data.objects['Check cap central stem']])
button_gap=switch[0][1]-stem[1][1]
check('Front button stem nominal rest clearance',0<=button_gap<=.15,gap_mm=button_gap,qualification='Nominal only. Supplier pretravel tolerance, print tolerances and force/stroke test remain required.')
from mathutils.bvhtree import BVHTree
def bvh(o):
 e=o.evaluated_get(deps);me=e.to_mesh();verts=[o.matrix_world@v.co for v in me.vertices];faces=[tuple(p.vertices) for p in me.polygons];tree=BVHTree.FromPolygons(verts,faces);e.to_mesh_clear();return tree
collisions=[]
for a in group('front_actuator'):
 for b in group('front_mount')+group('product_front'):
  if gap(bounds([a]),bounds([b])) < -.001 and bvh(a).overlap(bvh(b)):collisions.append([a.name,b.name])
check('Printed cap clears front PCB, parts and mount hardware at rest',not collisions,intersections=collisions)
check('All four grille fields retained',all(bpy.data.objects[n+' | 418 perforations']['perforation_count']==418 for n in ['Front','Right','Rear','Left']))
check('Assembly is self-contained',not bpy.data.libraries and not [i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file])
# Verify unchanged exterior/acoustics/batteries using evaluated mesh fingerprints in both saved scenes.
def snapshot():
 result={};dg=bpy.context.evaluated_depsgraph_get()
 for o in bpy.context.scene.objects:
  selected=any(c.name.startswith(('01 ','02 ','03 ','05 ','06 ','07 ','08 ','12 ','13 ')) for c in o.users_collection) or o.name in ['Exterior check button','ONE RGB lens normally off']
  if not selected or o.type not in ['MESH','CURVE'] or o.name.startswith('NEW '):continue
  e=o.evaluated_get(dg);me=e.to_mesh();vs=[tuple(round(v,4) for v in o.matrix_world@p.co) for p in me.vertices];fs=[tuple(p.vertices) for p in me.polygons];e.to_mesh_clear()
  result[o.name]=hashlib.sha256(repr((vs,fs)).encode()).hexdigest()
 return result
updated=snapshot();bpy.ops.wm.open_mainfile(filepath=str(E/'alec-cube-v4-1.blend'));baseline=snapshot();changes=[n for n in set(updated)|set(baseline) if updated.get(n)!=baseline.get(n)]
check('v4.1 shell, speaker, batteries and visible controls preserved',not changes,changed_objects=changes,compared_objects=len(baseline))
report=dict(status='NOMINAL_GEOMETRY_PASS' if all(c['passed'] for c in checks) else 'GEOMETRY_FAILURE',checks=checks,failed_checks=[c['name'] for c in checks if not c['passed']],tested_blend_sha256=hashlib.sha256((R/'alec-cube-v4-2.blend').read_bytes()).hexdigest(),manufacturing_release=False,physical_qualification_performed=False)
(R/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2));assert not report['failed_checks'],report['failed_checks']
