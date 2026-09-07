"""Render inspection views from the verified complete assembly without rewriting it."""
import bpy,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'alec-cube-v4-2.blend'));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100
for o in s.objects:
 if any(c.name.startswith(('01 ','02 ','03 ','12 ','13 ')) for c in o.users_collection):o.hide_render=True;o.hide_set(True)
# Remove the setup panel only in the interior inspection view to expose daughterboards.
for o in s.objects:
 if o.name=='Studio ground' or o.type=='FONT' or o.get('fit_group') in ['service_panel','acoustic_scrim'] or o.name.startswith(('Short protected button well','Finger well')):o.hide_render=True;o.hide_set(True)
camera=bpy.data.objects['CAM Internal side'];camera.location=(155,-225,-100);camera.rotation_euler=(Vector((0,-6,33))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=140;s.camera=camera
s.render.filepath=str(R/'internals.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'alec-cube-v4-2-internals.blend'))
bpy.ops.wm.open_mainfile(filepath=str(R/'alec-cube-v4-2.blend'));s=bpy.context.scene
s.render.resolution_x=1600;s.render.resolution_y=1200;s.cycles.samples=24
for o in s.objects:
 if any(c.name.startswith('13 ') for c in o.users_collection) or o.name=='Studio ground':o.hide_render=True;o.hide_set(True)
s.camera=bpy.data.objects['CAM Protected bottom'];s.render.filepath=str(R/'bottom-service.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'alec-cube-v4-2-service.blend'))
