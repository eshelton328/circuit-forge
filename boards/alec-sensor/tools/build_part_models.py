"""Drawing-based STEP envelopes for custom footprints. Requires free CadQuery.
Mechanical bodies/pin locations are explicit; these are not EM-solver models.
"""
from pathlib import Path
import cadquery as cq
D=Path(__file__).resolve().parents[1]/'3dmodels';D.mkdir(exist_ok=True)
def box(x,y,z,dx,dy,dz):return cq.Workplane('XY').box(dx,dy,dz).translate((x,y,z))
def save(name,parts):
 a=cq.Assembly()
 for label,shape,color in parts:a.add(shape,name=label,color=cq.Color(*color))
 a.save(str(D/(name+'.step')))
black=(.06,.065,.07);silver=(.7,.71,.73);gold=(.75,.57,.2)
save('SW_CK_1101M2S3CQE2',[('case',box(0,0,3.175,12.7,6.6,6.35),silver),('actuator',box(-1.205,0,8.89,3.86,3.86,5.08),black)]+[(f'pin{i}',box(x,0,-3.175,.76,1.27,6.35),silver) for i,x in enumerate([-4.7,0,4.7],1)])
body=box(5.08,0,4.255,13.21,2.41,8.51)
for i in range(5):body=body.cut(box(i*2.54,0,5.51,.75,.75,6))
save('Samtec_SSW-105-01-F-S',[('housing',body,black)]+[(f'tail{i}',box(i*2.54,0,-1.32,.41,.79,2.64),gold) for i in range(5)])
print('Built drawing-based switch and socket models')
