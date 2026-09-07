#!/usr/bin/env python3
"""Generate the S1 sensor schematic from reviewed ALEC circuit blocks.
PCB construction and validation are separate tools.
"""
from pathlib import Path
import copy, json, shutil, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts/alarm'))
from design import BASE, parse, dump, child, children, val, q, prop, node, uid, label, wire, pins, symbol_def, add_symbol
DEST=Path(__file__).resolve().parents[1]
NAME='alec-sensor'
from parts import apply
def select_parts(r):apply(r,(children,child,val,prop,q,node))

def note(root,text,x,y,size=1.27):
 root.append(node(f'(text {q(text)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left bottom)) (uuid {uid(NAME+text)}))'))

def keep_point(x,y):
 if 108<x<140 and 30<y<52:return False # old enable-only switch
 if 223<x<233 and 25<y<47:return False # always-on power LED
 return ((x<225 and y<235) or (x>=225 and y<112) or
         (238<=x<=314 and 112<=y<=154) or
         (195<=x<=237 and 215<=y<=237) or
         (205<=x<=267 and 242<=y<=284))

r=parse((BASE/'esp32s3-devkit-5v.kicad_sch').read_text().replace('esp32s3-devkit-5v',NAME))
original_defs={val(s[1]):copy.deepcopy(s) for s in children(child(r,'lib_symbols'),'symbol')}
kept=[]
for a in r:
 if not isinstance(a,list):kept.append(a);continue
 if a[0] in ['text','title_block']:continue
 if a[0] in ['symbol','label','junction','no_connect','wire']:
  pts=children(child(a,'pts'),'xy') if a[0]=='wire' else [child(a,'at')]
  if not all(keep_point(*map(float,p[1:3])) for p in pts):continue
 kept.append(a)
r=kept
r.extend([wire(220.98,27.94,237.49,27.94,NAME+'3v3-bus-left'),wire(237.49,27.94,246.38,27.94,NAME+'3v3-bus-right')])
r.append(node(f'(title_block (title "ALEC Sensor — prototype S1") (date "2026-09-07") (rev "S1"))'))
# Route each MCU function deliberately. Unused audio/display/button GPIOs become NC.
mcu=next(s for s in children(r,'symbol') if prop(s,'Reference')=='U3')
mx,my=map(float,child(mcu,'at')[1:3]);mpins=pins(original_defs[val(child(mcu,'lib_id')[1])])
unused=['5','6','22','23','24','25','34'] # GPIO5,6,14,21,47,48,41
for pn in unused:
 dx,dy=mpins[pn];point=(round(mx+dx,4),round(my-dy,4))
 ends={point}
 for a in children(r,'wire'):
  ps=[tuple(round(float(v),4) for v in p[1:3]) for p in children(child(a,'pts'),'xy')]
  if point in ps:ends.update(ps);r.remove(a)
 for a in list(children(r,'label'))+list(children(r,'no_connect')):
  if tuple(round(float(v),4) for v in child(a,'at')[1:3]) in ends:r.remove(a)
 r.append(node(f'(no_connect (at {point[0]} {point[1]}) (uuid {uid(NAME+"nc"+pn)}))'))
for a in children(r,'label'):
 name=val(a[1]);x,y=map(float,child(a,'at')[1:3])
 if name=='VBAT' and x>70:a[1]=q('VBAT_SW')
 if name=='SW_ON':a[1]=q('EN_3V3')
 if name=='GPIO18':a[1]=q('RADAR_EN' if x<200 else 'RADAR_RX')
 if name=='GPIO4':a[1]=q('PRESENCE_WAKE')
 if name=='GPIO11':a[1]=q('RADAR_IO_EN')
for pn,name in [('9','RADAR_EN'),('10','RADAR_TX')]: # physical module pads for IO16 / IO17
 dx,dy=mpins[pn];x,y=round(mx+dx,4),round(my-dy,4)
 for a in list(children(r,'no_connect')):
  if tuple(map(float,child(a,'at')[1:3]))==(x,y):r.remove(a)
 end=x-5.08 if dx<0 else x+5.08
 r.extend([wire(x,y,end,y,NAME+pn),label(name,end,y)])
ls=child(r,'lib_symbols');ls[:]=[a for a in ls if not (isinstance(a,list) and a[0]=='symbol' and val(a[1])=='Switch:SW_SPDT')]
swdef=symbol_def('Switch','SW_SPDT')
sw=add_symbol(r,swdef,'SW1','1101M2S3CQE2','Sensor:SW_CK_1101M2S3CQE2',121.92,40.64,{'1':'VBAT_SW','2':'VBAT_FUSED'},NAME,'https://www.littelfuse.com/assetdocs/littelfuse-c-k-slide-1000-series-datasheet?assetguid=68a2b41e-19a4-4cf4-821b-aca78a430f00')
# KiCad generic SPDT has pin 2 common. Pin 3 is the open/OFF throw.
px,py=pins(swdef)['3'];r.append(node(f'(no_connect (at {121.92+px} {40.64-py}) (uuid {uid(NAME+"sw1-off")}))'))
add_symbol(r,symbol_def('Device','Fuse'),'F1','1.5A FAST','Fuse:Fuse_0603_1608Metric',62.23,55.88,{'1':'VBAT','2':'VBAT_FUSED'},NAME,'https://www.littelfuse.com/assetdocs/fuse-467-datasheet?assetguid=4a59f034-1cca-460e-a5ba-e1e66247c76d','046701.5NRHF')
# Keep ordering text clear of the actual switch/fuse wiring.
for part in children(r,'symbol'):
 ref=prop(part,'Reference')
 if ref in ['F1','SW1']:
  for field in children(part,'property'):
   key=val(field[1])
   if key in ['Reference','Value']:
    xy=(54.61,53.34 if key=='Reference' else 57.15) if ref=='F1' else (121.92,30.48 if key=='Reference' else 33.02)
    child(field,'at')[1:3]=[str(v) for v in xy]
# Place left-facing switch label away from the contact graphic.
for a in children(r,'label'):
 if val(a[1])=='VBAT_FUSED' and 100<float(child(a,'at')[1])<121:
  child(child(a,'effects'),'justify')[1]='right'
# Resolve dense inherited reference labels without changing connectivity.
for part in children(r,'symbol'):
 ref=prop(part,'Reference')
 if ref in ['U5','C20']:
  for field in children(part,'property'):
   key=val(field[1])
   if key in ['Reference','Value']:
    xy=(283.21,160.02 if key=='Reference' else 162.56) if ref=='U5' else (383.54,62.23 if key=='Reference' else 64.77)
    child(field,'at')[1:3]=[str(v) for v in xy]
# Retain one external button; package boot/seal is a mechanical release gate.
for s in children(r,'symbol'):
 if prop(s,'Reference')=='SW7':
  for p in children(s,'property'):
   if val(p[1])=='Value':p[2]=q('BATTERY / PAIR')
# New radar sheet. Existing power-monitor sheet stays intact.
rootid=val(child(r,'uuid')[1]);sid=uid(NAME+'/radar-sheet')
nets=['3v3','5v','GND','RADAR_TX','RADAR_RX','PRESENCE_WAKE','RADAR_IO_EN']
sheet=node(f'''(sheet (at 345.44 124.46) (size 53.34 45.72) (stroke (width 0) (type default)) (fill (color 0 0 0 0))
(uuid {sid}) (property "Sheetname" "Radar interface" (at 345.44 122.428 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
(property "Sheetfile" "radar.kicad_sch" (at 345.44 172.212 0) (effects (font (size 1.27 1.27)) (justify left top)))
(instances (project "{NAME}" (path "/{rootid}" (page "3")))))''')
for i,n in enumerate(nets):
 x,y=345.44,round(129.54+5.08*i,4)
 sheet.append(node(f'(pin {q(n)} bidirectional (at {x} {y} 180) (effects (font (size 1.27 1.27)) (justify left)) (uuid {uid(NAME+"sheet"+n)}))'))
 r.extend([wire(x,y,x-7.62,y,NAME+'radar/'+n),label(n,x-7.62,y)])
r.append(sheet)
note(r,'ALEC SENSOR S1 — prototype; bench and ingress tests required.\n3 AA primary cells; no charging. USB-C is data-only: batteries + SW1 ON required.\nSW1: hard battery disconnect, 6 A / 28 VDC. F1: 1.5 A fast fuse; validate inrush and fault clearing.\nRTC time survives ESP deep sleep, but is lost on SW1 OFF or battery removal. Resync before arming.',22.86,23,1.27)
note(r,'3.31 V always on with SW1 closed. 4.985 V radar rail: GPIO16 high = ON.\nR19 holds radar OFF during reset; PS/SYNC high permits power-save operation.\nReserve >=200 mA at the radar connector; measure startup at depleted-cell voltage.',22.86,248,1.27)
note(r,'GPIO17 TX -> radar RX; GPIO18 RX <- radar TX. UART: 256000 8N1.\nGPIO4 = presence wake. GPIO11 = I/O switch enable, default OFF.\nPower up: I/O OFF -> rail ON -> PG valid -> I/O ON -> fresh valid frames.\nPower down: I/O OFF -> UART stop -> rail OFF. OUT cannot wake if radar is off.',22.86,271,1.27)
note(r,'RV-3028: I2C GPIO8 SDA / GPIO9 SCL; interrupt GPIO1 (active LOW).\nShort press GPIO10: battery; long press: physical pairing.\nRGB common anode; GPIO38/39/40 LOW lights R/G/B.\nNo always-on power LED. Use low-duty PWM for presence indication.',270,205,1.27)
note(r,'Prototype hardware. See TEST-REPORT.md for checks and remaining\nbench, radome, condensation and water-ingress release gates.',270,248,1.27)
# Remove cached definitions which no longer have instances.
used={val(child(s,'lib_id')[1]) for s in children(r,'symbol')}
ls=child(r,'lib_symbols');ls[:]=[ls[0]]+[s for s in children(ls,'symbol') if val(s[1]) in used]
for a in children(r,'label'):
 if val(a[1]) in ['PRESENCE_WAKE','RADAR_IO_EN','RADAR_EN'] and 225<float(child(a,'at')[1])<280:
  child(child(a,'effects'),'justify')[1]='right'
 if float(child(a,'at')[1])==round(345.44-7.62,4):
  child(child(a,'effects'),'justify')[1]='right'
select_parts(r)
(DEST/(NAME+'.kicad_sch')).write_text(dump(r)+'\n')
monitor=parse((BASE/'power-monitor.kicad_sch').read_text().replace('esp32s3-devkit-5v',NAME))
monitor[:]=[a for a in monitor if not (isinstance(a,list) and a[0]=='title_block')]
monitor.append(node('(title_block (title "ALEC Sensor — power monitoring") (date "2026-09-07") (rev "S1"))'))
select_parts(monitor)
(DEST/'power-monitor.kicad_sch').write_text(dump(monitor)+'\n')
# Custom part uses the PW/TSSOP-14 pin table, never the QFN table.
pin_specs=[('1','SEL1','input',-15.24,-10.16,0),('2','S1','passive',-15.24,10.16,0),('3','D1','passive',15.24,10.16,180),
 ('4','SEL2','input',-15.24,-15.24,0),('5','S2','passive',-15.24,5.08,0),('6','D2','passive',15.24,5.08,180),
 ('7','GND','power_in',0,-25.4,90),('8','D3','passive',15.24,0,180),('9','S3','passive',-15.24,0,0),
 ('10','SEL3','input',-15.24,-20.32,0),('11','D4','passive',15.24,-5.08,180),('12','S4','passive',-15.24,-5.08,0),
 ('13','SEL4','input',15.24,-15.24,180),('14','VDD','power_in',0,20.32,270)]
definition=node('''(symbol "Sensor:TMUX1511PWR" (pin_names (offset 0.508)) (in_bom yes) (on_board yes)
(property "Reference" "U" (at 0 22.86 0) (effects (font (size 1.27 1.27))))
(property "Value" "TMUX1511PWR" (at 0 25.4 0) (effects (font (size 1.27 1.27))))
(symbol "TMUX1511PWR_0_1" (rectangle (start -12.7 17.78) (end 12.7 -22.86) (stroke (width 0.254) (type default)) (fill (type background))))
(symbol "TMUX1511PWR_1_1"))''')
for pn,n,t,x,y,angle in pin_specs:
 children(definition,'symbol')[1].append(node(f'(pin {t} line (at {x} {y} {angle}) (length 2.54) (name {q(n)} (effects (font (size 1.016 1.016)))) (number {q(pn)} (effects (font (size 1.016 1.016)))))'))
childroot=uid(NAME+'/radar')
r=node(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {childroot}) (paper "A4") (lib_symbols))')
r.append(node('(title_block (title "ALEC Sensor — switched radar interface") (date "2026-09-07") (rev "S1"))'))
pn={'1':'RADAR_IO_EN','2':'RADAR_TX','3':'LD_RX','4':'RADAR_IO_EN','5':'RADAR_RX','6':'LD_TX','7':'GND','8':'LD_OUT','9':'PRESENCE_WAKE','10':'RADAR_IO_EN','11':'GND','12':'GND','13':'GND','14':'3v3'}
s=add_symbol(r,definition,'U10','TMUX1511PWR','Package_SO:TSSOP-14_4.4x5mm_P0.65mm',100.33,81.28,pn,NAME,'https://www.ti.com/lit/ds/symlink/tmux1511.pdf')
for p in children(s,'property'):
 if val(p[1]) in ['Value','Reference']: child(p,'at')[1:3]=['100.33',str(55.88 if val(p[1])=='Reference' else 58.42)]
add_symbol(r,symbol_def('Connector_Generic','Conn_01x05'),'J3','LD2410C — INTERNAL','Sensor:Samtec_SSW-105-01-F-S',215.9,76.2,{'1':'LD_TX','2':'LD_RX','3':'LD_OUT','4':'GND','5':'5v'},NAME,'https://www.hlktech.com/en/Goods-239.html','SSW-105-01-F-S')
for ref,value,x,y,ns in [('R54','100k',43.18,111.76,{'1':'RADAR_IO_EN','2':'GND'}),('R55','100k',43.18,139.7,{'1':'PRESENCE_WAKE','2':'GND'}),('R56','100k',93.98,139.7,{'1':'RADAR_RX','2':'GND'})]:
 add_symbol(r,symbol_def('Device','R'),ref,value,'Resistor_SMD:R_0402_1005Metric',x,y,ns,NAME,mpn='RC0402FR-07100KL')
for ref,value,x,y,rail in [('C35','10uF',215.9,114.3,'5v'),('C36','0.1uF',248.92,114.3,'5v'),('C37','0.1uF',149.86,139.7,'3v3')]:
 add_symbol(r,symbol_def('Device','C'),ref,value,'Capacitor_SMD:C_0603_1608Metric',x,y,{'1':rail,'2':'GND'},NAME,mpn='GRM188R61A106KAALD' if ref=='C35' else 'GRM188R71C104KA01D')
# Bypass-capacitor labels sit beside the plates, clear of their supply wires.
for part in children(r,'symbol'):
 if prop(part,'Reference') in ['C35','C36','C37']:
  x,y=map(float,child(part,'at')[1:3])
  for field in children(part,'property'):
   key=val(field[1])
   if key in ['Reference','Value']:child(field,'at')[1:3]=[str(x-6.35),str(y-1.27 if key=='Reference' else y+1.27)]
# All child symbols are in the actual hierarchical instance path.
for s in children(r,'symbol'):
 path=child(child(child(s,'instances'),'project'),'path');path[1]=q('/'+rootid+'/'+sid)
for i,n in enumerate(nets):
 x,y=40.64,round(27.94+i*5.08,4)
 r.extend([node(f'(hierarchical_label {q(n)} (shape bidirectional) (at {x} {y} 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid {uid(NAME+"port"+n)}))'),wire(x,y,x+12.7,y,NAME+'portwire'+n),label(n,x+12.7,y)])
note(r,'LD2410C: regulated 5 V; logic is 3.3 V. J3 numbering follows the module drawing.\nThis is NOT the pin order of a generic JST cable. Verify assembled socket orientation.\nU10 opens all three signal paths when GPIO11 is low; no pull-ups on the unpowered radar side.',22.86,20.32)
note(r,'ON: rail PG valid before closing U10; ignore startup frames until qualified.\nOFF: open U10 before disabling 5 V. Check reset, brownout and sleep-hold behavior on the bench.\nPowered-radar wake mode: retain 5 V and U10 ON, use OUT only as a wake hint, then verify UART.\nU10 is signal isolation, not a voltage translator. The fourth channel is grounded and disabled.',22.86,165.1)
for a in children(r,'label'):
 if abs(float(child(a,'at')[1])-80.01)<0.001:
  child(child(a,'effects'),'justify')[1]='right'
select_parts(r)
(DEST/'radar.kicad_sch').write_text(dump(r)+'\n')
lib=copy.deepcopy(definition);lib[1]=q('TMUX1511PWR')
(DEST/'review/Sensor.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")\n'+dump(lib)+')\n')
shutil.copy2(BASE/'review/Review.kicad_sym',DEST/'review/Review.kicad_sym')
(DEST/'sym-lib-table').write_text((BASE/'sym-lib-table').read_text().rstrip()[:-1]+'(lib (name "Sensor") (type "KiCad") (uri "${KIPRJMOD}/review/Sensor.kicad_sym") (options "") (descr "TMUX1511 PW pin table")))\n')
(DEST/'fp-lib-table').write_text((BASE/'fp-lib-table').read_text().rstrip()[:-1]+'(lib (name "Sensor") (type "KiCad") (uri "${KIPRJMOD}/footprints/Sensor.pretty") (options "") (descr "Drawing-controlled sensor parts")))\n')
pro=json.loads((BASE/'esp32s3-devkit-5v.kicad_pro').read_text())
pro.setdefault('meta',{})['filename']=NAME+'.kicad_pro'
pro.setdefault('erc',{})['erc_exclusions']=[]
(DEST/(NAME+'.kicad_pro')).write_text(json.dumps(pro,indent=2)+'\n')
print('Generated S1 prototype schematic:',DEST)
