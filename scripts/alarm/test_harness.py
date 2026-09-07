"""Free ngspice screening of remote button RLC and hardware-enable states.
This is a lumped sensitivity study, not measured parasitic extraction or EMC qualification.
"""
from design import *
import subprocess,re,itertools,hashlib
D=MAIN/'sim';D.mkdir(exist_ok=True)
results=[]
# C22-C25 nominal 100 nF; parasitics below are bounded assumptions to measure on prototypes.
for series,L,C,wire_r in [(r,l,c,w) for r in [0,95,105] for l,c,w in itertools.product([.1e-6,1e-6],[80e-9,120e-9],[.1,1.0])]:
 key=f'button-r{series}-l{L:g}-c{C:g}-w{wire_r:g}'
 deck=f'''Remote button sensitivity: series={series} ohm, L={L}, C={C}, Rwire={wire_r}
VDD supply 0 3.3
Rpull supply gpio 10000
Cdeb gpio 0 {C}
Rseries gpio cable {max(series,.001)}
Lwire cable remote {L}
Rwire remote contact {wire_r}
Vcontact control 0 PULSE(0 3.3 1m 1n 1n 1m 5m)
Sbutton contact 0 control 0 BUTTON
.model BUTTON SW(Ron=0.05 Roff=1e12 Vt=1.65 Vh=0)
.tran 50n 4m
.meas tran gpio_min MIN v(gpio) FROM=0.99m TO=2m
.meas tran gpio_max MAX v(gpio) FROM=0.99m TO=4m
.meas tran press_current MAX i(Lwire) FROM=1m TO=1.1m
.meas tran held FIND v(gpio) AT=1.9m
.meas tran released FIND v(gpio) AT=3.9m
.end
'''
 tag=f'c{len(results)+1:02}'
 for measure in ['gpio_min','gpio_max','press_current','held','released']:deck=deck.replace('.meas tran '+measure+' ','.meas tran '+measure+'_'+tag+' ')
 path=D/(key+'.cir');path.write_text(deck)
 run=subprocess.run(['ngspice','-b',str(path)],capture_output=True,text=True)
 assert run.returncode==0,run.stdout+run.stderr
 measures={k:float(v) for k,v in re.findall(r'^(gpio_min|gpio_max|press_current|held|released)(?:_c\d+)?\s*=\s*([-+\d.eE]+)',run.stdout,re.M)}
 assert len(measures)==5,run.stdout
 passed=measures['gpio_min']>=-.1 and measures['gpio_max']<=3.4 and measures['press_current']<=.05 and measures['held']<.825 and measures['released']>2.475
 results.append(dict(series_ohm=series,loop_inductance_H=L,debounce_F=C,wire_resistance_ohm=wire_r,measures=measures,screening_limits_met=passed,deck=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
# Actual switch wiring: common EN, ON through R31=10k, OFF directly GND; R32=100k on main.
en=[]
for vbat in [2.7,3.0,4.5,5.4]:
 for state in ['on','off','unplugged']:
  switch='Rthrow sw_on enable .1' if state=='on' else 'Rthrow enable 0 .1' if state=='off' else '* Unplugged: no throw connected'
  deck=f'''Hardware enable {state}, protected battery {vbat} V
Vbat pfet 0 {vbat}
R31 pfet sw_on 10k
R32 enable 0 100k
{switch}
.control
op
print v(enable) i(Vbat)
.endc
.end
'''
  path=D/f'enable-{state}-{vbat:g}.cir';path.write_text(deck)
  run=subprocess.run(['ngspice','-b',str(path)],capture_output=True,text=True)
  match=re.search(r'v\(enable\)\s*=\s*([-+\d.eE]+)',run.stdout);assert match,run.stdout
  voltage=float(match[1]);expected=vbat*100000/(110000.1) if state=='on' else 0
  assert abs(voltage-expected)<1e-4
  en.append(dict(protected_battery_V=vbat,state=state,enable_V=voltage))
report=dict(scope='Lumped RLC sensitivity and DC enable topology only; not extracted parasitics, switch life, GPIO ESD-clamp current, EMC, thermal or physical qualification.',assumptions={'cable_length_limit_mm':200,'loop_inductance_H':[.1e-6,1e-6],'wire_and_contacts_ohm':[.1,1.0],'button_on_resistance_ohm':.05,'capacitor_F':[80e-9,120e-9],'GPIO_threshold_assumptions_V':{'low_max':.825,'high_min':2.475},'switching_edges':'Ideal switch with 1 ns drive edges; no contact bounce or GPIO clamps'},tool=subprocess.run(['ngspice','--version'],capture_output=True,text=True).stdout,button_cases=results,enable_cases=en,passed=all(r['screening_limits_met'] for r in results if r['series_ohm']>0))
(MAIN/'review/harness-simulation.json').write_text(json.dumps(report,indent=2)+'\n')
for r in [0,95,105]:
 cases=[c for c in results if c['series_ohm']==r];print(r,'min GPIO',min(c['measures']['gpio_min'] for c in cases),'peak current',max(c['measures']['press_current'] for c in cases),'pass',sum(c['screening_limits_met'] for c in cases),'/',len(cases))
assert report['passed']
print('12 enable states passed; OFF/unplugged are standby, not battery disconnect.')
