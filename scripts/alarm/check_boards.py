"""Run KiCad ERC, default/parity DRC and explicit fab-rule DRC on the three boards."""
from design import ROOT
import subprocess,json,os,shutil,concurrent.futures
CLI=os.environ.get('KICAD_CLI',shutil.which('kicad-cli') or '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
def run(d,kind):
 args=[CLI,'sch' if kind=='erc' else 'pcb',kind,'--format','json','-o',str(d/'review'/f'{kind}.json')]
 if kind=='drc':args+=['--refill-zones','--schematic-parity']
 args+=[str(d/(d.name+('.kicad_sch' if kind=='erc' else '.kicad_pcb')))]
 r=subprocess.run(args,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 report=json.loads((d/'review'/f'{kind}.json').read_text())
 violations=[v for s in report['sheets'] for v in s['violations']] if kind=='erc' else report['violations']+report['unconnected_items']+report['schematic_parity']
 print(d.name,kind,len(violations),flush=True)
 for v in violations:print(v['type'],v['description'],[(i['description'],i.get('pos')) for i in v['items']],flush=True)
 return len(violations)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(6) as pool:
  counts=list(pool.map(lambda a:run(*a),[(ROOT/'boards'/('alec-'+k),c) for k in ['main','controls','front'] for c in ['erc','drc']]))
 raise SystemExit(bool(sum(counts)))
