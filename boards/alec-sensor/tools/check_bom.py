#!/usr/bin/env python3
"""Check purchasing metadata against native sources and selected capacitor packages.

This checks known part-family size codes, not stock, land-pattern dimensions,
electrical derating, pin orientation or assembler approval.
"""
from pathlib import Path
import csv,json,sys,xml.etree.ElementTree as ET
D=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(D.parents[1]/'scripts/alarm'))
from design import parse,children,prop

def capacitor_package(mpn):
 for prefix,size in [('GRM15','0402_1005'),('GRM18','0603_1608'),('GRM21','0805_2012'),('GRM31','1206_3216'),('CL31','1206_3216')]:
  if mpn.startswith(prefix):return size
 raise AssertionError('Unreviewed capacitor package family: '+mpn)

def check(bom=D/'review/bom.csv',netlist=D/'review/netlist.xml',board=D/'alec-sensor.kicad_pcb'):
 with Path(bom).open(newline='') as f:rows=list(csv.DictReader(f))
 comps={c.get('ref'):c for c in ET.parse(netlist).findall('./components/comp')}
 fps={prop(f,'Reference'):f for f in children(parse(Path(board).read_text()),'footprint')}
 caps=0
 for r in rows:
  ref=r['Reference'];c=comps[ref];f=fps[ref]
  fields={a.get('name'):a.text for a in c.findall('fields/field')}
  assert r['MPN']==fields.get('MPN')==prop(f,'MPN'),ref+' MPN differs between BOM, schematic and PCB'
  assert r['Footprint']==c.findtext('footprint'),ref+' footprint differs between BOM and schematic'
  # Native footprint library identifier is the first argument of (footprint ...).
  assert r['Footprint']==f[1].strip('"'),ref+' footprint differs between BOM and PCB'
  if ref.startswith('C'):
   expected='Capacitor_SMD:C_'+capacitor_package(r['MPN'])+'Metric'
   assert r['Footprint']==expected,ref+' capacitor package does not match footprint'
   caps+=1
 return {'status':'pass','component_metadata_matches':len(rows),'capacitor_packages_checked':caps,'scope':__doc__.strip()}

if __name__=='__main__':
 result=check();(D/'review/bom-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
