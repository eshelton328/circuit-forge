"""Shared, explicit enclosure-board interface and lossless KiCad S-expression helpers."""
from pathlib import Path
import re,json,uuid,os
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'boards/esp32s3-devkit-5v'
MAIN=ROOT/'boards/bedroom-alarm-main'
LIB=Path(os.environ.get('KICAD_SHARE','/Applications/KiCad/KiCad.app/Contents/SharedSupport' if Path('/Applications/KiCad/KiCad.app').exists() else '/usr/share/kicad'))
REMOVE={'SW1','SW4','SW5','SW6','SW7','D2'}
BOTTOM=['GND','BTN_VOL_MINUS','BTN_MODE','BTN_VOL_PLUS','GND','SW_ON','EN_3V3']
FRONT=['GND','3v3','BTN_BAT','LED_R_K','LED_G_K','LED_B_K']
SERVICE=['GND','3v3','UART_TX','UART_RX','EN','GPIO0']
def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'the-forge/bedroom-alarm/'+key))
def q(s):return json.dumps(str(s),ensure_ascii=False)
def val(s):return json.loads(s) if s.startswith('"') else s
def parse(s):
 stack=[[]]
 for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s):
  if t=='(':stack.append([])
  elif t==')':a=stack.pop();stack[-1].append(a)
  else:stack[-1].append(t)
 assert len(stack)==1
 return stack[0][0]
def dump(a,depth=0):
 if not isinstance(a,list):return a
 if any(isinstance(x,list) for x in a):return '('+'\n'.join(('\t'*(depth+1) if i else '')+dump(x,depth+1) for i,x in enumerate(a))+')'
 return '('+' '.join(a)+')'
def children(a,tag):return [x for x in a if isinstance(x,list) and x[0]==tag]
def child(a,tag):return next(x for x in a if isinstance(x,list) and x[0]==tag)
def prop(a,key):return next(val(x[2]) for x in children(a,'property') if val(x[1])==key)
def node(s):return parse(s)
def label(name,x,y):return node(f'(label {q(name)} (at {x:.4f} {y:.4f} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {uid(f"label/{name}/{x}/{y}")}))')
def wire(x,y,xx,yy,key):return node(f'(wire (pts (xy {x} {y}) (xy {xx} {yy})) (stroke (width 0) (type default)) (uuid {uid(key)}))')
def symbol_def(lib,name):
 r=parse((LIB/'symbols'/f'{lib}.kicad_sym').read_text())
 a=next(s for s in children(r,'symbol') if val(s[1])==name)
 a[1]=q(lib+':'+name);return a

def pins(definition):
 return {val(child(p,'number')[1]):tuple(map(float,child(p,'at')[1:3])) for sub in children(definition,'symbol') for p in children(sub,'pin')}
def add_symbol(root,definition,ref,value,footprint,x,y,pin_nets,project,datasheet='',mpn=''):
 x=round(round(x/1.27)*1.27,4);y=round(round(y/1.27)*1.27,4)
 name=val(definition[1]);defs=child(root,'lib_symbols')
 if not any(val(s[1])==name for s in children(defs,'symbol')):defs.append(definition)
 rootid=val(child(root,'uuid')[1]);key=project+'/'+ref
 s=node(f'''(symbol (lib_id {q(name)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)
 (uuid {uid(key)})
 (property "Reference" {q(ref)} (at {x} {y-6} 0) (effects (font (size 1.27 1.27))))
 (property "Value" {q(value)} (at {x} {y-3.5} 0) (effects (font (size 1.27 1.27))))
 (property "Footprint" {q(footprint)} (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (property "Datasheet" {q(datasheet)} (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (property "MPN" {q(mpn or value)} (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (instances (project {q(project)} (path {q('/'+rootid)} (reference {q(ref)}) (unit 1)))))''')
 if name.startswith('Connector_Generic:'):
  top=y-max(py for px,py in pins(definition).values())
  for field in children(s,'property'):
   if val(field[1]) in ['Reference','Value']:child(field,'at')[1:3]=[str(x),str(round(top-(6 if val(field[1])=='Reference' else 3.5),4))]
 if name=='Device:R':
  for field in children(s,'property'):
   if val(field[1]) in ['Reference','Value']:child(field,'at')[1:3]=[str(x-5.08),str(y-1.27 if val(field[1])=='Reference' else y+1.27)]
 if ref.startswith('J'):s.append(node('(exclude_from_sim yes)'))
 if ref=='J7' and project=='bedroom-alarm-main':
  child(s,'in_bom')[1]='no';s.append(node('(in_pos_files no)'))
 for pn,(px,py) in pins(definition).items():
  s.append(node(f'(pin {q(pn)} (uuid {uid(key+"/"+pn)}))'))
  if pn in pin_nets:
   xx,yy=round(x+px,4),round(y-py,4);end=xx-(25.4 if name.startswith('Connector_Generic:') else 5.08) if px<0 else xx+5.08
   root.extend([wire(xx,yy,end,yy,key+'/wire/'+pn),label(pin_nets[pn],end,yy)])
 root.append(s)
 return s

def gh(n):return f'Connector_JST:JST_GH_BM{n:02}B-GHS-TBT_1x{n:02}-1MP_P1.25mm_Vertical'
def gh_mpn(n):return f'BM{n:02}B-GHS-TBT'
