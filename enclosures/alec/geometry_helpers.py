def mat(name,color,metal=0,rough=.5):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1);m.use_nodes=True
 n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1)
 n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough;return m
charcoal=mat('Charcoal nonconductive polymer',(.065,.072,.076),rough=.65)
black=mat('Black nylon / rubber / cone',(.01,.014,.02),rough=.6)
silver=mat('Nickel and steel',(.54,.58,.62),.7,.3)
green=mat('Circuit board',(.025,.28,.15))
blue=mat('Drawing-based part',(.075,.26,.40))
amber=mat('UNVERIFIED dimensions or proposed mechanism',(.93,.40,.075))
light=mat('Matte chamber polymer',(.16,.19,.20))
white=mat('Printed markings',(.84,.89,.91))
red=mat('Positive conductor',(.65,.035,.025)); cableblack=mat('Ground conductor',(.02,.025,.032))
wireblue=mat('I2C cable',(.10,.30,.57)); orange=mat('15 mm RF clearance',(.98,.48,.02))
ledmat=mat('One exterior RGB lens in green state',(.08,.10,.09))
ledmat.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(.01,.45,.04,1)
ledmat.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=0
floor_mat=mat('Studio background',(.18,.21,.25),rough=.85)

def link(o,name,c,m=None,status='custom_geometry',group=None):
 o.name=name
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o)
 if m and o.type in ['MESH','CURVE','FONT']:o.data.materials.append(m)
 o['evidence_status']=status
 if group:o['fit_group']=group
 return o
def box(name,loc,size,c,m,bevel=0,**kw):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=link(bpy.context.object,name,c,m,**kw)
 o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  b=o.modifiers.new('Edge radius','BEVEL');b.width=bevel;b.segments=3
  o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o
def cyl(name,loc,r,depth,c,m,axis='Z',vertices=64,**kw):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc)
 o=link(bpy.context.object,name,c,m,**kw)
 if axis=='X':o.rotation_euler.y=math.pi/2
 if axis=='Y':o.rotation_euler.x=math.pi/2
 return o
def boolean(o,cut):
 mod=o.modifiers.new('Actual opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(cut,do_unlink=True)
def tube(name,points,r,c,m,**kw):
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=16
 sp=curve.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for b,p in zip(sp.bezier_points,points):b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 curve.bevel_depth=r;curve.bevel_resolution=3
 o=bpy.data.objects.new(name,curve);c.objects.link(o);curve.materials.append(m)
 o['evidence_status']=kw.get('status','allocated_harness');o['fit_group']=kw.get('group','harness')
 return o
def rod(name,a,b,r,c,m):
 a,b=Vector(a),Vector(b);o=cyl(name,(a+b)/2,r,(b-a).length,c,m)
 o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def wirebox(name,lo,hi,c,m):
 vs=[Vector((x,y,z)) for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]]
 for i,a in enumerate(vs):
  for b in vs[i+1:]:
   if sum(abs(a[k]-b[k])>.001 for k in range(3))==1:rod(name,a,b,.17,c,m)
def text3d(name,body,loc,size,c,m,rot=(0,0,0)):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.extrude=.015
 o=bpy.data.objects.new(name,cu);c.objects.link(o);cu.materials.append(m);o.location=loc;o.rotation_euler=rot;return o
def import_mm(path,c,label):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));S.view_layers.update()
 imported=set(bpy.data.objects)-before;meshes=[o for o in imported if o.type=='MESH']
 for o in meshes:
  # Blender's glTF importer already honours this scene's 0.001 m unit scale.
  world=o.matrix_world.copy()
  o.data=o.data.copy();o.data.transform(world);o.parent=None;o.matrix_world=Matrix.Identity(4)
  link(o,o.name,c,status=label)
 for o in imported:
  if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
 root=bpy.data.objects.new(label,None);c.objects.link(root)
 for o in meshes:o.parent=root
 return root,meshes
def bounds(obs):
 pts=[o.matrix_world@Vector(p) for o in obs for p in o.bound_box]
 return [[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]
