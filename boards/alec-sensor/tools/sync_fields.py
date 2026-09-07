"""Update ordering metadata only; never replace routed footprints or copper."""
from pathlib import Path
import xml.etree.ElementTree as E
import pcbnew as p
D=Path(__file__).resolve().parents[1];fn=D/(D.name+'.kicad_pcb');b=p.LoadBoard(str(fn));cs={c.get('ref'):c for c in E.parse(D/'review/netlist.xml').findall('./components/comp')}
for f in b.GetFootprints():
 c=cs.get(f.GetReference())
 if c is None:continue
 for a in c.findall('fields/field'):
  if a.get('name')!='Footprint':f.SetField(a.get('name'),a.text or '')
 for field in f.GetFields():field.SetVisible(False)
p.SaveBoard(str(fn),b)
