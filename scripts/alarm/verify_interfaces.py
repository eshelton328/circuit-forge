"""Verify exported circuit equivalence and complete end-to-end cable pin maps."""
from design import *
import xml.etree.ElementTree as E,hashlib,json

def extract(d):
 r=E.parse(d/'review/netlist.xml').getroot()
 comp={c.attrib['ref']:c for c in r.find('components')}
 nets={n.attrib['name']:{(p.attrib['ref'],p.attrib['pin']) for p in n} for n in r.find('nets')}
 pins={p:name for name,ps in nets.items() for p in ps}
 return comp,nets,pins
old,on,op=extract(BASE);new,nn,np=extract(MAIN);common=set(old)-REMOVE
checks=[]
def check(name,ok):
 assert ok,name
 checks.append({'name':name,'passed':True})
check('Exactly the six relocated main-board user parts were removed',set(new)==common|{'J5','J6','J7','R50','R51','R52','R53'})
for ref in common:
 check(ref+' value and footprint preserved',all(old[ref].findtext(k)==new[ref].findtext(k) for k in ['value','footprint']))
for pin in op:
 if pin[0] not in common:continue
 check('Existing circuit peers '+'.'.join(pin),{p for p in on[op[pin]] if p[0] in common}=={p for p in nn[np[pin]] if p[0] in common})
for connector,names in [('J5',BOTTOM),('J6',FRONT),('J7',SERVICE)]:
 for i,n in enumerate(names,1):check(f'{connector}.{i} = {n}',np[connector,str(i)].lstrip('/')==n)
# Cable, resistor, MCU, pullup, capacitor, switch form a single reviewed signal chain.
paths=[]
for i,(gpio,btn,switch,board,conn,pin,pull,cap) in enumerate([
 ('4','BTN_VOL_MINUS','SW1','controls','J5','2','R24','C22'),('5','BTN_MODE','SW2','controls','J5','3','R25','C23'),('6','BTN_VOL_PLUS','SW3','controls','J5','4','R26','C24'),('10','BTN_BAT','SW1','front','J6','3','R27','C25')],50):
 ref='R'+str(i);_,dn,dp=extract(ROOT/'boards'/('bedroom-alarm-'+board))
 check(ref+' 100 ohm cable damping',new[ref].findtext('value')=='100Ω' and np[ref,'1'].lstrip('/')==btn and np[ref,'2']=='/GPIO'+gpio)
 check(switch+' '+board+' return to connector',dp[switch,'1']==dp['J1','1'] and dp[switch,'2']==dp['J1',pin])
 check('Main pullup/debounce '+gpio,np[pull,'2']==np[cap,'1']==np[ref,'2'])
 paths.append(dict(function=btn,main_connector=conn,pin=int(pin),series_resistor=ref,value_ohm=100,GPIO=int(gpio),remote_board=board,remote_switch=switch))
_,dn,dp=extract(ROOT/'boards/bedroom-alarm-controls')
check('Hardware enable common goes to EN, ON throw via R31, OFF to ground',dp['SW4','2']==dp['J1','7'] and dp['SW4','1']==dp['J1','6'] and dp['SW4','3']==dp['J1','1'] and np['J5','6']==np['R31','2'] and np['J5','7']==np['R32','1']==np['U1','14'])
_,dn,dp=extract(ROOT/'boards/bedroom-alarm-front')
for pin,led in [('2','1'),('4','3'),('5','4'),('6','2')]:check('Front LED pin '+led,dp['J1',pin]==dp['D1',led])
for cp,res in [('4','R28'),('5','R29'),('6','R30')]:check('Main RGB current limit '+cp,np['J6',cp]==np[res,'1'])
for cp,mp in [('3','37'),('4','36'),('5','3'),('6','27')]:check('UART service module pin '+mp,np['J7',cp]==np['U3',mp])
check('Display pin order and switched power preserved',[np['J4',str(i)] for i in range(1,5)]==['GND','/OLED_3V3','/OLED_SCL','/OLED_SDA'])
report=dict(passed=True,checks=checks,button_paths=paths,harnesses={'bottom':dict(main='J5',remote='controls.J1',pin_order=BOTTOM,housings='GHR-07V-S',contacts='SSHL-002T-P0.2'), 'front':dict(main='J6',remote='front.J1',pin_order=FRONT,housings='GHR-06V-S',contacts='SSHL-002T-P0.2')},service=dict(connector='J7',pin_order=SERVICE,power='Battery-powered target; 3v3 is voltage reference only, never external supply'),netlist_sha256={d.name:hashlib.sha256((d/'review/netlist.xml').read_bytes()).hexdigest() for d in [BASE,MAIN,ROOT/'boards/bedroom-alarm-controls',ROOT/'boards/bedroom-alarm-front']})
(MAIN/'review/interface-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(len(checks),'circuit/interface checks passed')
