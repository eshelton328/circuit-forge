"""Audit every placed product component's local 3D dependencies; read-only PCB access."""
from design import *
import pcbnew as p,hashlib,json
for kind in ['main','controls','front']:
 d=ROOT/'boards'/('bedroom-alarm-'+kind);b=p.LoadBoard(str(d/(d.name+'.kicad_pcb')));rows=[]
 for f in b.GetFootprints():
  if f.GetReference().startswith(('H','TP')) or f.GetReference()=='J7' and kind=='main':continue
  models=[]
  for m in f.Models():
   path=d/m.m_Filename.replace('${KIPRJMOD}/','');assert path.is_file(),path
   models.append({'file':str(path.relative_to(d)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'offset':[m.m_Offset.x,m.m_Offset.y,m.m_Offset.z],'rotation':[m.m_Rotation.x,m.m_Rotation.y,m.m_Rotation.z]})
  assert models,f.GetReference()
  rows.append({'reference':f.GetReference(),'DNP':f.IsDNP(),'footprint':f.GetFPIDAsString(),'models':models,'ordered_part_geometry_qualified':False})
 (d/'review/3d-model-audit.json').write_text(json.dumps({'components':rows,'all_model_files_resolved':True,'scope':'Local package models only. All ordered variants, maximum heights and manufacturing tolerances still need checking.'},indent=2)+'\n')
 print(kind,len(rows),'component model references resolve')
