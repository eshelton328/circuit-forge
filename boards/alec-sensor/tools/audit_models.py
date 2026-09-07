#!/usr/bin/env python3
"""Verify project-local model coverage; this does not certify package tolerances."""
from pathlib import Path
import hashlib,json
import pcbnew as p
D=Path(__file__).resolve().parents[1]
b=p.LoadBoard(str(D/'alec-sensor.kicad_pcb'));rows=[]
for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
 ref=f.GetReference()
 if ref.startswith(('TP','H')):continue
 models=[]
 for m in f.Models():
  assert m.m_Filename.startswith('${KIPRJMOD}/3dmodels/'),(ref,m.m_Filename)
  path=Path(m.m_Filename.replace('${KIPRJMOD}',str(D)))
  assert path.is_file(),(ref,path)
  models.append({'path':str(path.relative_to(D)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'offset_mm':[m.m_Offset.x,m.m_Offset.y,m.m_Offset.z],'rotation_deg':[m.m_Rotation.x,m.m_Rotation.y,m.m_Rotation.z],'scale':[m.m_Scale.x,m.m_Scale.y,m.m_Scale.z]})
 assert models,(ref,'missing 3D model')
 rows.append({'reference':ref,'side':b.GetLayerName(f.GetLayer()),'position_mm':[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)],'footprint':f.GetFPIDAsString(),'models':models})
result={'status':'pass','electrical_footprints':len(rows),'unique_model_files':len({m['path'] for r in rows for m in r['models']}),'components':rows,'scope':'Resolvable local file coverage and transforms; generic passives and simplified models are not exact MPN/tolerance validation.'}
(D/'review/3d-model-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(f"Models: {len(rows)} electrical footprints, {result['unique_model_files']} unique files, all resolve")
