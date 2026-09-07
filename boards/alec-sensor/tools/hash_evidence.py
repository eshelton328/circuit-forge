#!/usr/bin/env python3
"""Bind delivered source and evidence bytes; rerun only after final validation."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parents[1];R=D.parents[1]
paths=[]
for base in [D,R/'enclosures/alec-sensor']:
 for p in base.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.pyc','.kicad_prl','.blend1']:continue
  if p.name.startswith('~') or p.name=='source-hashes.json':continue
  if p.parent==D and p.name.startswith('drc-fab-'):continue
  if p.suffix in ['.kicad_sch','.kicad_pcb','.kicad_pro','.kicad_mod','.kicad_sym','.py','.json','.md','.csv','.txt','.cir','.log','.pdf','.png','.glb','.blend','.step','.stl','.svg','.yml'] or p.name.endswith('-lib-table'):
   paths.append(p)
paths.extend(R/p for p in ['scripts/alarm/design.py','scripts/ci/check_copper_connectivity.py','boards/esp32s3-devkit-5v/esp32s3-devkit-5v.kicad_pcb','boards/esp32s3-devkit-5v/esp32s3-devkit-5v.kicad_sch','boards/esp32s3-devkit-5v/power-monitor.kicad_sch','enclosures/alec/geometry_helpers.py','enclosures/alec/sources/BH3AAW.glb','tests/test_alec_sensor.py','.github/workflows/alec-sensor-study.yml'])
result={'revision':'S1','scope':'SHA-256 of delivered sources, models, documentation and local evidence; not a physical qualification or CI attestation. The manifest excludes itself.','files':{str(p.relative_to(R)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(paths)}}
(D/'review/source-hashes.json').write_text(json.dumps(result,indent=2)+'\n')
print(f'Hashed {len(paths)} source/evidence files')
