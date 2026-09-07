#!/usr/bin/env python3
"""Free-tool S1 battery/thermal sensitivity and passive input-inrush SPICE screening.
No transistor converter model, EMI field solver or qualified thermal model is implied.
"""
from pathlib import Path
import json,math,itertools,subprocess,shutil,re,csv
D=Path(__file__).resolve().parents[1];out=D/'review/power-screening';out.mkdir(exist_ok=True)
layout=json.loads((D/'review/layout-validation.json').read_text())
trace_r=sum(a['track_resistance_35um_copper_20C_ohm'] for a in layout['battery_series_copper'].values())
# Contact, via and temperature allowances are separate from the computed trace sum.
fixed_r=trace_r+.02+.0385+.01+.15
rows=[]
for v,rpack,(name,i3,i5),eta in itertools.product([3.,3.6,4.5,5.4],[.15,.6,1.5],[('active_example',.08,.079),('radar_supply_reserve',.08,.2),('simultaneous_peak_envelope',.5,.2)],[.75,.85]):
 power=(3.3*i3+5*i5)/eta;rs=rpack+fixed_r;disc=v*v-4*rs*power
 node=(v+math.sqrt(disc))/2 if disc>=0 else None
 current=power/node if node else None
 rows.append({'pack_open_circuit_v':v,'pack_resistance_ohm':rpack,'load':name,'efficiency':eta,'converter_input_v':node,'battery_a':current,'cold_start_3v_margin_v':node-3 if node else None,'running_2v_margin_v':node-2 if node else None,'q1_w':current*current*.15 if current else None,'status':'source_power_collapse' if not node else 'below_cold_start' if node<3 else 'conditional_voltage_margin'})
# Every watt consumed inside ultimately becomes heat; exclude the blocked rear face from area.
interface=json.loads((D.parents[1]/'enclosures/alec-sensor/interface.json').read_text())
diameter=interface['shell_diameter']/1000;depth=interface['shell_depth']/1000
area=math.pi*diameter**2/4+math.pi*diameter*depth
thermal=[]
for ambient,h,(name,power) in itertools.product([25,40],[3,5,8],[('active_example',(.08*3.3+.079*5)/.85),('continuous_peak_stress',(.5*3.3+.2*5)/.75)]):
 thermal.append({'ambient_c':ambient,'h_w_m2k':h,'load':name,'internal_w':power,'lumped_surface_c':ambient+power/(h*area)})
# Passive contact closure into the actual nominal 60uF input bank, swept for bias and harness L.
# The regulators are deliberately absent. This bounds one contributor to inrush; it cannot predict switching-node ringing.
ng=shutil.which('ngspice');assert ng,'Install free ngspice to run the screening'
spice=[]
for index,(fraction,lwire,rpack) in enumerate(itertools.product([.25,.5,1.0],[10e-9,100e-9,1e-6],[.15,.6,1.5])):
 cap=60e-6*fraction;rs=rpack+fixed_r
 deck=f'''S1 passive battery closure; no converter switching model
Vpack source 0 PWL(0 0 0.5u 5.4)
Vsense source a 0
Rseries a b {rs:.9g}
Lharness b vin {lwire:.9g}
Resr vin cap 0.01
Cin cap 0 {cap:.9g}
Rleak vin 0 100Meg
.tran 5n 400u 0 100n
.meas tran vin_peak MAX v(vin)
.meas tran i_peak MAX i(Vsense)
.meas tran input_i2t INTEG par('i(Vsense)*i(Vsense)') FROM=0 TO=400u
.end
'''
 path=out/f'inrush-{index:02}.cir';path.write_text(deck);log=out/f'inrush-{index:02}.log'
 result=subprocess.run([ng,'-b','-o',str(log),str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
 assert result.returncode==0,(path,result.stderr)
 data='\n'.join(line.rstrip() for line in log.read_text().splitlines()).rstrip()+'\n';log.write_text(data);measures={k:float(v) for k,v in re.findall(r'^(vin_peak|i_peak|input_i2t)\s*=\s*([-+\deE.]+)',data,re.M)}
 assert len(measures)==3 and all(math.isfinite(v) for v in measures.values()),path
 spice.append({'effective_input_cap_uF':cap*1e6,'harness_l_nH':lwire*1e9,'pack_resistance_ohm':rpack,**measures,'fraction_of_fuse_nominal_melting_i2t':measures['input_i2t']/.0766})
result={'status':'screening_complete_not_qualification','pcb_trace_r_35um_20c_ohm':trace_r,'additional_assumed_series_r_ohm':fixed_r-trace_r,'assumptions':{'pack_resistance':'Illustrative whole-pack values, not chemistry/SOC characterization','q1_r_ohm':.15,'fuse_cold_r_ohm':.0385,'switch_r_ohm':.01,'via_and_harness_extra_r_ohm':.02,'fuse_nominal_melting_i2t_a2s':.0766,'input_nominal_uF':60,'thermal_exposed_area_m2':area,'thermal_limit':'Lumped surface estimate ignores hot spots, wall conduction, radiation and internal thermal resistance; it is not junction temperature','spice_limit':'Passive pack-connection RLC only. Contact bounce, converter startup/switching, aging and cell dynamics absent.'},'battery_cases':rows,'thermal_cases':thermal,'passive_spice_cases':spice,'ngspice_version':subprocess.check_output([ng,'--version'],text=True).splitlines()[1:4]}
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'battery_cases':len(rows),'thermal_cases':len(thermal),'spice_cases':len(spice),'no_cold_start_margin':sum(a['status']!='conditional_voltage_margin' for a in rows),'passive_max_peak_v':max(a['vin_peak'] for a in spice),'passive_max_peak_a':max(a['i_peak'] for a in spice),'max_passive_i2t_fuse_fraction':max(a['fraction_of_fuse_nominal_melting_i2t'] for a in spice)},indent=2))
