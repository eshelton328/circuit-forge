"""Create the product schematics from the reviewed bench-board circuit, deterministically."""
from design import *
import shutil,xml.etree.ElementTree as E,yaml
MAIN.mkdir(exist_ok=True)
for file in ['esp32s3-devkit-5v.kicad_pro','power-monitor.kicad_sch','sym-lib-table','fp-lib-table']:
 text=(BASE/file).read_text().replace('esp32s3-devkit-5v','bedroom-alarm-main')
 (MAIN/file.replace('esp32s3-devkit-5v','bedroom-alarm-main')).write_text(text)
for directory in ['footprints','3dmodels','models']:
 if (BASE/directory).exists():shutil.copytree(BASE/directory,MAIN/directory,dirs_exist_ok=True,ignore=shutil.ignore_patterns('model-map.json','README.md') if directory=='3dmodels' else None)
(MAIN/'review').mkdir(exist_ok=True)
shutil.copy(BASE/'review/Review.kicad_sym',MAIN/'review/Review.kicad_sym')
r=parse((BASE/'esp32s3-devkit-5v.kicad_sch').read_text().replace('esp32s3-devkit-5v','bedroom-alarm-main'))
child(r,'paper')[1]=q('A2')
for t in children(r,'text'):
 t[1]=q(val(t[1]).replace('SW1 selects EN_3V3: ON = PFET via R31; OFF = GND.\nBattery current bypasses SW1; this is standby, not battery isolation.', 'Setup-board SW4 via J5: ON = PFET via R31; OFF = GND.\nOnly enable current crosses the cable; OFF is standby, not isolation.').replace('D2: common anode at 3V3; RGB GPIO LOW = ON.', 'Front-board D1 via J6: common anode at 3V3; LOW = ON.'))
r.append(node('(title_block (title "Bedroom alarm main PCB") (date "2026-09-06") (rev "v4.2 prototype"))'))
netlist=E.parse(BASE/'review/netlist.xml').getroot()
netmap={(n.attrib['ref'],n.attrib['pin']):net.attrib['name'].lstrip('/') for net in netlist.find('nets') for n in net}
renames={'Net-(D2-RK)':'LED_R_K','Net-(D2-GK)':'LED_G_K','Net-(D2-BK)':'LED_B_K'}
defs={val(d[1]):d for d in children(child(r,'lib_symbols'),'symbol')}
for s in list(children(r,'symbol')):
 ref=prop(s,'Reference')
 if ref not in REMOVE:continue
 x,y,angle=map(float,child(s,'at')[1:]);assert angle==0
 for pn,(dx,dy) in pins(defs[val(child(s,'lib_id')[1])]).items():
  if (ref,pn) in netmap:
   net=netmap[ref,pn];r.append(label(renames.get(net,net),x+dx,y-dy))
  else:
   r[:]=[a for a in r if not(isinstance(a,list) and a[0]=='no_connect' and list(map(float,child(a,'at')[1:3]))==[round(x+dx,4),round(y-dy,4)])]
 r.remove(s)
# UART pins are direct module RXD0/TXD0, formerly explicitly NC.
s=next(s for s in children(r,'symbol') if prop(s,'Reference')=='U3')
x,y=map(float,child(s,'at')[1:3])
for pn,name in [('36','UART_RX'),('37','UART_TX')]:
 dx,dy=pins(defs[val(child(s,'lib_id')[1])])[pn];xx,yy=round(x+dx,4),round(y-dy,4)
 r[:]=[a for a in r if not(isinstance(a,list) and a[0]=='no_connect' and list(map(float,child(a,'at')[1:3]))==[xx,yy])]
 r.extend([wire(xx,yy,xx+5.08,yy,'UART/'+pn),label(name,xx+5.08,yy)])
# EN and IO0 use existing net names (verify the exported netlist).
for pn,name in [('3','EN'),('27','GPIO0')]:
 dx,dy=pins(defs[val(child(s,'lib_id')[1])])[pn]
 r.append(label(name,round(x+dx,4),round(y-dy,4)))
for ref,netnames,y,fp,mpn in [('J5',BOTTOM,60,gh(7),gh_mpn(7)),('J6',FRONT,115,gh(6),gh_mpn(6)),('J7',SERVICE,170,'Alarm:Programming_2x03_P2.0mm','UNPOPULATED_TEST_PADS')]:
 add_symbol(r,symbol_def('Connector_Generic',f'Conn_01x{len(netnames):02}'),ref,mpn,fp,460,y,{str(i):n for i,n in enumerate(netnames,1)},MAIN.name,'https://www.jst-mfg.com/product/pdf/eng/eGH.pdf' if ref!='J7' else '',mpn)
for i,(gpio,external) in enumerate([('GPIO4','BTN_VOL_MINUS'),('GPIO5','BTN_MODE'),('GPIO6','BTN_VOL_PLUS'),('GPIO10','BTN_BAT')],50):
 add_symbol(r,symbol_def('Device','R'),'R'+str(i),'100Ω','Resistor_SMD:R_0402_1005Metric',525,50+20*(i-50),{'1':external,'2':gpio},MAIN.name,'https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/pyu-rc-group_51_rohs_l.pdf','RC0402FR-07100RL')
for y,text in [(30,'ENCLOSURE INTERFACES — keyed GH cables, pin 1 to pin 1'),(85,'J5: VOL− / MODE / VOL+ and hardware enable; unplugged = standby'),(140,'J6: BAT button + common-anode RGB; R28–R30 remain on main board'),(192,'J7: service fixture only. 3v3 is TARGET REFERENCE, not a power input.'),(205,'UART: TX goes to programmer RX; RX to programmer TX. Use 3.3 V logic.'),(220,'OFF is standby: protected battery still feeds regulator VIN. No hard disconnect.')]:
 r.append(node(f'(text {q(text)} (at 435 {y} 0) (effects (font (size 1.5 1.5)) (justify left bottom)) (uuid {uid(text)}))'))
(MAIN/(MAIN.name+'.kicad_sch')).write_text(dump(r)+'\n')
check=yaml.safe_load((BASE/'checks.yml').read_text())
for ref in REMOVE:check['required_components'].pop(ref,None)
for ref in ['J5','J6','J7','R50','R51','R52','R53']:check['required_components'][ref]={}
(MAIN/'checks.yml').write_text(yaml.safe_dump(check,sort_keys=False,allow_unicode=True))
(MAIN/'board.yml').write_text('name: bedroom-alarm-main\ndescription: Enclosure main board with remote controls and UART service pads\nlayers: 4\ncopper_weight: 1oz\nthickness: 1.6mm\nfab_targets:\n  - jlcpcb-4layer-advanced\n')
# Daughterboards contain passive switches/LED only. All pullups, debounce and LED resistors remain on main.
for kind in ['controls','front']:
 name='bedroom-alarm-'+kind;d=ROOT/'boards'/name;d.mkdir(exist_ok=True);(d/'review').mkdir(exist_ok=True)
 r=node(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {uid(name)}) (paper "A4") (lib_symbols))')
 r.append(node(f'(title_block (title {q(name)}) (date "2026-09-06") (rev "v4.2 prototype"))'))
 names=BOTTOM if kind=='controls' else FRONT;n=len(names)
 add_symbol(r,symbol_def('Connector_Generic',f'Conn_01x{n:02}'),'J1',gh_mpn(n),gh(n),50,65,dict(zip(map(str,range(1,n+1)),names)),name,'https://www.jst-mfg.com/product/pdf/eng/eGH.pdf')
 if kind=='controls':
  for ref,net,y,value in [('SW1','BTN_VOL_MINUS',50,'VOL-'),('SW2','BTN_MODE',90,'MODE'),('SW3','BTN_VOL_PLUS',130,'VOL+')]:
   add_symbol(r,symbol_def('Switch','SW_Push'),ref,value,'Button_Switch_THT:SW_TH_Tactile_Omron_B3F-106x',120,y,{'1':'GND','2':net},name,'https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3f.pdf','B3F-1060')
  add_symbol(r,symbol_def('Switch','SW_SPDT'),'SW4','EG1218','Alarm:EG1218',205,65,{'1':'SW_ON','2':'EN_3V3','3':'GND'},name,'https://configured-product-images.s3.amazonaws.com/2D/specs/EG1218.pdf')
 else:
  add_symbol(r,symbol_def('Switch','SW_Push'),'SW1','BATTERY','Button_Switch_SMD:SW_SPST_B3U-1000P',125,50,{'1':'GND','2':'BTN_BAT'},name,'https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3u.pdf','B3U-1000P')
  add_symbol(r,defs['Review:WE_150141M173100'],'D1','150141M173100','LED_SMD:LED_RGB_Wuerth-PLCC4_3.2x2.8mm_150141M173100',125,95,{'1':'3v3','2':'LED_B_K','3':'LED_R_K','4':'LED_G_K'},name,'https://www.we-online.com/components/products/datasheet/150141M173100.pdf')
 r.append(node(f'(text {q("1:1 GH harness to main J5" if kind=="controls" else "1:1 GH harness to main J6; LED series resistors on main") } (at 40 170 0) (effects (font (size 1.5 1.5)) (justify left bottom)) (uuid {uid(name+"note")}))'))
 (d/(name+'.kicad_sch')).write_text(dump(r)+'\n')
 (d/(name+'.kicad_pro')).write_text('{}\n')
 (d/'board.yml').write_text(f'name: {name}\ndescription: Passive {kind} daughterboard for bedroom alarm\nlayers: 2\ncopper_weight: 1oz\nthickness: 1.6mm\nfab_targets:\n  - jlcpcb-2layer-standard\n')
 (d/'checks.yml').write_text(yaml.safe_dump({'required_components':{prop(s,'Reference'):{} for s in children(r,'symbol')},'required_nets':sorted(set(names)),'bom_rules':{'require_footprint':True,'no_duplicate_refs':True}},sort_keys=False))
 (d/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Alarm") (type "KiCad") (uri "${KIPRJMOD}/../../libs/footprints/Alarm.pretty") (options "") (descr "Alarm interface parts")))\n')
 print(name)
f=MAIN/'fp-lib-table';a=parse(f.read_text());a.append(node('(lib (name "Alarm") (type "KiCad") (uri "${KIPRJMOD}/../../libs/footprints/Alarm.pretty") (options "") (descr "Alarm interface parts"))'));f.write_text(dump(a)+'\n')
print('service pin order',SERVICE)
