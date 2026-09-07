"""Refresh native exports and the orderable-parts inventory. Requires KiCad CLI."""
from design import *
import subprocess,concurrent.futures,csv,xml.etree.ElementTree as ET,shutil,os
CLI=os.environ.get('KICAD_CLI',shutil.which('kicad-cli') or '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
def export(kind):
 d=ROOT/'boards'/('alec-'+kind);sch=d/(d.name+'.kicad_sch');pcb=d/(d.name+'.kicad_pcb');review=d/'review'
 jobs=[['sch','export','netlist','--format','kicadxml','-o',str(review/'netlist.xml'),str(sch)],['sch','export','pdf','-o',str(review/'schematic.pdf'),str(sch)],['pcb','export','glb','--force','--no-dnp','--subst-models','--include-pads','--include-silkscreen','-o',str(ROOT/'enclosures/alec/pcb-revision/sources'/f'{kind}.glb'),str(pcb)]]
 jobs += [['pcb','render','--width','1600','--height','1000','--side',side,'--background','opaque','-o',str(review/f'pcb-{side}.png'),str(pcb)] for side in ['top','bottom']]
 for args in jobs:
  run=subprocess.run([CLI]+args,capture_output=True,text=True);assert run.returncode==0,run.stdout+run.stderr
 r=ET.parse(review/'netlist.xml').getroot();rows=[]
 for c in r.find('components'):
  fields={f.attrib['name']:f.text for f in c.findall('fields/field')};ref=c.attrib['ref']
  if ref=='J7' and kind=='main':continue
  rows.append({'Reference':ref,'Value':c.findtext('value'),'MPN':fields.get('MPN',''),'Footprint':c.findtext('footprint'),'Datasheet':c.findtext('datasheet'),'Assembly': 'NO PART: fabricated probe pads' if ref=='J7' and kind=='main' else 'DNP' if ref=='R11' and kind=='main' else 'Populate; verify ordering code'})
 with (review/'bom.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(sorted(rows,key=lambda r:r['Reference']))
 print(kind,'exports complete',flush=True)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(3) as pool:list(pool.map(export,['main','controls','front']))
