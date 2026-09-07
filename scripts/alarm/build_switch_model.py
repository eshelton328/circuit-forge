"""Drawing-based EG1218 envelope; not a manufacturer STEP model. Requires CadQuery."""
from pathlib import Path
import cadquery as cq
root=Path(__file__).resolve().parents[2]
d=root/'boards/bedroom-alarm-controls/3dmodels';d.mkdir(exist_ok=True)
a=cq.Assembly(name='EG1218_drawing_envelope')
a.add(cq.Workplane('XY').box(11.6,4,5.4,centered=(True,True,False)),name='body',color=cq.Color(.7,.7,.72))
a.add(cq.Workplane('XY').box(2,2,2,centered=(True,True,False)).translate((-1,0,5.4)),name='actuator_ON',color=cq.Color(.08,.08,.08))
for i,x in enumerate([-2.5,0,2.5],1):
 a.add(cq.Workplane('XY').box(.6,.5,4.7,centered=(True,True,False)).translate((x,0,-4.7)),name=f'pin{i}',color=cq.Color(.7,.7,.72))
a.save(str(d/'EG1218_drawing_envelope.step'))
