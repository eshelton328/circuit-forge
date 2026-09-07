#!/usr/bin/env python3
"""Independent schematic interface assertions; export a fresh XML netlist first."""
from pathlib import Path
import json, xml.etree.ElementTree as ET
D=Path(__file__).resolve().parents[1]

def check(path=D/'review/netlist.xml'):
 r=ET.parse(path).getroot()
 nets=[{(n.get('ref'),n.get('pin')) for n in net.findall('node')} for net in r.findall('./nets/net')]
 comps={c.get('ref'):c.findtext('value') for c in r.findall('./components/comp')}
 done=[]
 def same(title,*members):
  pairs={tuple(m.split('.')) for m in members}
  assert any(pairs<=n for n in nets),title
  done.append(title)
 def apart(title,a,b):
  assert not any(tuple(a.split('.')) in n and tuple(b.split('.')) in n for n in nets),title
  done.append(title)
 same('Native USB D- stays GPIO19','U3.13','R34.1')
 same('Native USB D+ stays GPIO20','U3.14','R35.1')
 same('RTC SDA stays GPIO8','U3.12','U5.4','R17.1')
 same('RTC SCL stays GPIO9','U3.17','U5.3','R16.1')
 same('RTC interrupt uses RTC GPIO1','U3.39','U5.2','R18.1')
 same('RTC remains on the always-on MCU rail','U3.2','U5.7','U1.8','U10.14')
 same('U2 enable moves from IO18 to IO16 with reset pull-down','U3.9','U2.14','R19.1')
 same('Radar enable pull-down ends at ground','R19.2','J1.2')
 same('ESP UART TX17 connects switch S1','U3.10','U10.2')
 same('Switch D1 feeds radar RX, module pin2','U10.3','J3.2')
 same('Radar TX, module pin1, feeds switch D2','J3.1','U10.6')
 same('Switch S2 feeds ESP UART RX18','U10.5','U3.11','R56.1')
 same('Radar OUT is module pin3','J3.3','U10.8')
 same('Switch S3 feeds RTC-capable GPIO4','U10.9','U3.4','R55.1')
 same('GPIO11 controls all three used channels','U3.19','U10.1','U10.4','U10.10','R54.1')
 same('Signal isolation defaults off, receive inputs default low','R54.2','R55.2','R56.2','J1.2')
 same('Unused fourth channel grounded and disabled','U10.11','U10.12','U10.13','J1.2')
 same('Radar connector receives regulated 5V with local bypass','J3.5','U2.8','C35.1','C36.1')
 same('Radar pin4 is ground','J3.4','J1.2')
 same('Exterior button on GPIO10','U3.18','SW7.2','C25.1','R27.2')
 same('Battery ADC GPIO2 retained','U3.38','R48.2','R49.1','C34.1')
 same('Switched battery measurement GPIO12 retained','U3.20','R46.1')
 same('Hard power switch raw battery input','J1.1','SW1.1')
 same('Hard switch output feeds reverse-protection FET drain','SW1.2','Q1.3')
 same('3V3 enable is biased from protected battery via R31','R31.1','Q1.2')
 same('3V3 enable division','R31.2','R32.1','U1.14')
 same('3V3 enable pull-down','R32.2','J1.2')
 same('RGB common anode on 3V3','D2.1','U1.8')
 for gpio,pad,res,ledpad in [(38,31,28,3),(39,32,29,4),(40,33,30,2)]:
  same(f'GPIO{gpio} RGB series resistor','U3.'+str(pad),f'R{res}.2')
  same(f'GPIO{gpio} RGB correct cathode',f'R{res}.1',f'D2.{ledpad}')
 same('RTC no-backup connection','U5.6','R33.1')
 same('RTC backup 10k to ground','R33.2','J1.2')
 for title,a,b in [('Raw battery isolated by switch','J1.1','Q1.3'),('USB cannot charge AA cells','J2.A4','J1.1'),('USB cannot bypass hard switch','J2.A4','Q1.2'),('Radar 5V separate from MCU 3V3','J3.5','U3.2'),('TX not directly tied to unpowered radar','U3.10','J3.2'),('RX not directly tied to radar','U3.11','J3.1'),('OUT not directly tied to MCU','U3.4','J3.3'),('RX pin no longer enables converter','U3.11','U2.14')]:apart(title,a,b)
 assert comps['U1']==comps['U2']=='TPS63070RNMR'
 assert comps['U5']=='RV-3028-C7' and comps['U10']=='TMUX1511PWR'
 assert not {'U6','U7','U8','D1','R11','SW4','SW5','SW6'} & comps.keys()
 done.append('Audio, OLED, spare user switches and always-on power LED removed')
 return done
if __name__=='__main__':
 done=check()
 result={'status':'pass','assertions':len(done),'checks':done,'scope':'Fresh exported schematic connectivity only; no analog, RF, enclosure or PCB qualification.'}
 (D/'review/interface-checks.json').write_text(json.dumps(result,indent=2)+'\n')
 print(f'{len(done)} interface checks passed')
