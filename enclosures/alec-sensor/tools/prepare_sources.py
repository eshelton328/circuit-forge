"""Convert manufacturer radar STEP geometry to a lightweight GLB using CadQuery.
Pass the downloaded HLK-LD2410C.step; no paid CAD exporter required.
"""
import sys,json,hashlib
from pathlib import Path
import cadquery as cq
D=Path(__file__).resolve().parents[1];source=Path(sys.argv[1]);shape=cq.importers.importStep(str(source));a=cq.Assembly()
for i,o in enumerate(shape.solids().vals()):
 b=o.BoundingBox();color=(.025,.24,.34) if i==0 else (.1,.12,.14) if b.zlen>1 and b.xlen>2 and b.ylen>2 else (.6,.53,.28)
 a.add(o,name=f'HLK_solid_{i:03}',color=cq.Color(*color))
a.save(str(D/'sources/HLK-LD2410C.glb'))
(D/'sources/provenance.json').write_text(json.dumps({'radar':{'url':'https://r0.hlktech.com/download/HLK-LD2410C-24G/1/HLK-LD2410C-3D图.zip','step_filename':source.name,'step_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256((D/'sources/HLK-LD2410C.glb').read_bytes()).hexdigest(),'materials':'Illustrative replacement colors; geometry from vendor STEP'},'holder':{'source':'../../alec/sources/BH3AAW.glb','drawing':'https://www.batteryholders.com/uploads/parts/BH3AAW/datasheets/BH3AAW-datasheet.pdf','model':'https://www.memoryprotectiondevices.com/3D/download.php?pn=BH3AAW&id=1295'}},indent=2)+'\n')
