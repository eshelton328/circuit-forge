"""Generate a dimensioned drawing, gallery and evidence-based geometry report."""
from pathlib import Path
import json,html,math,hashlib,csv
R=Path(__file__).resolve().parent
p=json.loads((R/'dimensions.json').read_text());v=json.loads((R/'verification.json').read_text())
assert not v['failed_checks']
if hashlib.sha256((R/'bedroom-cube-v4-1.blend').read_bytes()).hexdigest()!=v['tested_blend_sha256']:
 raise RuntimeError('Saved assembly changed: rerun verify_assembly.py before generating a passing report')
rows=[]
for c in v['checks']:
 evidence={k:q for k,q in c.items() if k not in ['name','passed']}
 rows.append('| '+c['name']+' | PASS | '+html.escape(json.dumps(evidence,ensure_ascii=False)).replace('|','&#124;')+' |')
report=f'''# v4.1 test report

2026-09-06. **{len(v['checks'])}/{len(v['checks'])} nominal geometry checks passed. Physical qualification: NOT PERFORMED. Manufacturing release: NO.**

The tested artifact is the saved `bedroom-cube-v4-1.blend`, reopened independently by `verify_assembly.py` under Blender 5.2.1 LTS. The native main PCB was not changed; SHA-256: `{p['pcb_sha256']}`. This is the v4.1 EastRising 1.3-inch display update to the preserved v4 enclosure. There is no new PCB-layout simulation or SPICE result in this revision.

## Display change and preserved layout

See [DISPLAY-UPDATE.md](DISPLAY-UPDATE.md) for the drawing datums, old/new comparison, electrical pin mapping and remaining checks. The four-pin EastRising ER-OLEDM013-1W-I2C module is modeled from manufacturer drawing page 6 and pin table page 8. It is not the seven-pin SPI/I2C version or the bare production OLED panel.

- OLED PCB: 35.4 × 33.5 × 1.2 mm. Mounting: 30.4 × 28.5 mm centres, Ø3 holes.
- Active area: 29.42 × 14.70 mm, offset 2.05 mm toward the header from PCB centre. Glass front Z=7.0; PCB rear Z=9.8, implementing the 2.8 mm nominal stack in the drawing.
- Display moved +1.5 mm in Y. Only the proposed front UI board and its cable start moved −0.5 mm in Y; the exterior button/lens stayed fixed. Bottom window is now 31.8 × 17.1 mm.
- Nominal OLED-PCB gaps: 1.25 mm to the front UI PCB, 1.25 mm to the withdrawal corridor, 2.445 mm to the holder. The two 1.25 mm gaps leave 0.25 mm after a 1 mm screening reserve. This is tight packaging, not a complete production tolerance stack.
- The unverified female mating socket is allocated 11 × 3.5 × 7 mm, with cable bend space above it. A 3 mm rear-component allowance is checked separately. Exact shipped back-side components and mating hardware still require samples.
- The final verifier compares evaluated mesh coordinates and topology in this saved model against the original v4 file. The preserved exterior, main PCB, batteries, speaker pod and control PCB match.
- No board copper, buck-boost placement, SPICE decks or firmware changed. The SH1106 driver, full-white current/startup, bus behavior and off-state leakage must be checked when integrating the module.

## Results and interpretation

- Body: 105 mm cube; modeled complete external envelope: **{' × '.join(str(x) for x in v['overall_physical_size_mm'])} mm**, including feet and front-button/icon protrusion.
- Actual PCB assembly: 65.50 × 62.25 × 11.54 mm from the source GLB. Native PCB thickness is 1.6 mm; the GLB substrate alone is 1.51 mm. Component models remain subject to exact-part checks.
- Four grilles: 418 openings each, **1,672 total**. Hole centres, solid webs, non-manifold edges and Euler characteristic were checked on evaluated meshes. The expected Euler value per grille is 2 − 2×418 = −834.
- The RF volume has no foreign modeled surface inside it. Triangle/box tests distinguish the hollow shell from its enclosing bounding box. This does not measure antenna efficiency or radio range.
- The battery withdrawal corridor is clear after the cover and retention bridge are released. Own holder contacts, cells, retention parts and flexible battery leads are excluded. Spring compression, removal force, finger grip and drop retention are not evaluated.
- The direct path has no rigid reflector/duct obstruction. The cloth is an intended acoustic material, excluded from the rigid obstruction test; its acoustic impedance and insertion loss have not been simulated or measured.
- Maximum diaphragm travel leaves 2.8 mm to the grille and 2.45 mm to the allocated cloth. A 1 mm rigid tolerance budget leaves 1.8/1.45 mm respectively; fabric movement and real driver variation still need allowance verification.
- The rear chamber contains {p['chamber_gross_air_box_litres']:.4f} L gross rectangular space before displacement. Net volume and acoustic response are not qualified.

These checks are a scoped interference and topology audit, not a complete tolerance stack, stress analysis, production CAD audit, acoustic model or assembly-process qualification. A rendered sealed pod is not a leak test. The short switch wells and captive hardware still require detail design. Amber geometry is intentionally provisional.

## Reproduce

From this directory:

```sh
CUBE_SKIP_RENDER=1 blender --background --python-exit-code 1 --python build_blender.py
blender --background --python-exit-code 1 --python verify_assembly.py
python3 build_report.py
```

Omit `CUBE_SKIP_RENDER=1` to regenerate the six rendered views. See [README.md](README.md) for Blender installation/path options and SVG-to-PNG rendering. Blender's `--python-exit-code 1` makes a raised verification failure visible to the shell. `verification.json` contains the full machine-readable measurements. Native PCB ERC/DRC and electrical regressions are not repeated here because no native board or circuit was modified; they are mandatory when implementing the proposed PCB revision.

## Detailed completed checks

| Check | Result | Evidence |
|---|---|---|
'''+ '\n'.join(rows)+'''

## Physical testing — every row below is NOT RUN

The following numbers are proposed engineering screening criteria, not published certification limits or guaranteed wake-up thresholds. Record the chosen alarm file, volume, firmware, battery chemistry/state, ambient temperature, microphone calibration, position and exact enclosure/cloth revision with every result.

| Test | Method and saved evidence | Decision criterion / unresolved target | Status |
|---|---|---|---|
| Basic part fit | Calipers and real parts; verify OLED drawing datums, back-side components, mated connector envelope, speaker terminals, holder with max-size cells; update the CAD | All prescribed clearances survive actual dimensions and tolerances; no pressed wires or cell interference | NOT RUN |
| New display electrical integration | Run SH1106 edge/checkerboard patterns and settings screen; 100 switched-power cycles; test full-white current, I2C rise time and powered-off leakage using the actual J4 harness | Correct orientation and complete 128×64 image on every start; rail/pin limits respected, no back-power or off-state lighting; module datasheet lists 45 mA maximum at 3.3 V full-white | NOT RUN |
| Service controls | Fit direct switches and panel; 100 presses each, 20 settings sessions, 20 battery replacements | No sticking, missed/double events, accidental power operation or cells falling out while setting the alarm; intact wells/bridge | NOT RUN |
| Grille/cloth insertion loss | Same sealed pod, speaker and fixed electrical drive; compare bare baffle, grille only, grille + cloth; three repeated sweeps each | Provisional screen: within 2 dB average level in 500 Hz–4 kHz; investigate every repeatable new >3 dB response feature, buzz or audible loss of clarity | NOT RUN |
| Small chamber response | Compare v4.1 to a larger sealed test volume with measured net volumes; same driver and drive; save response/decay and listening notes | Choose the smallest volume meeting the agreed sound quality. Do not retain 105 mm solely for appearance if the response is objectionable | NOT RUN |
| Old versus new arrangement | Same speaker/amplifier/file and measured drive; compare v3 reflector prototype if available against v4.1 | Prefer the arrangement with cleaner response and adequate pillow-position level at less battery power; no superiority claimed before measurement | NOT RUN |
| Direction and bedside placement | Record at 1 m on axis, ±45°, 90°, 180°, then the actual pillow position; repeat near wall and beside normal nightstand objects | Front-facing placement meets a user-approved awake listening level with adjustment margin. Side/rear loss is reported, not passed as omnidirectional | NOT RUN |
| Distortion and rattles | Low-level sweep first, then controlled stepped level using the real alarm signal; inspect harmonics and audible buzz; repeat at the pillow | No buzz, panel rattle or abrupt compression; provisional <5% THD in 500 Hz–4 kHz at the agreed level, subject to microphone noise/distortion floor | NOT RUN |
| Pod leakage | Inspect gasket compression, blind bosses, joints and potted wire exit; compare low-level response before/after temporary seam sealing | No repeatable response/buzz change from sealing a supposedly closed seam; any leak is fixed before acoustic comparison | NOT RUN |
| Continuous load and cooling | Real assembled unit, initial 0.5–1 W-class audio trial only after checking electrical drive, fresh and depleted AA sets of each chemistry; log battery current, minimum loaded voltage, rails and component/cell/holder temperatures | Meet selected component/cell limits with design margin; no resets, audio collapse or continuing temperature rise. Intended maximum alarm duration and ambient envelope still need definition | NOT RUN |
| Overnight energy reserve | Measure sleep, radio checks, display use and a sustained alarm; integrate current for both chemistries | Define and demonstrate a battery warning threshold that leaves the required alarm reserve; no battery-life figure inferred from nominal AA capacity | NOT RUN |
| Radio and dwell behavior | Closed enclosure in actual bedroom; sensor in shower location, doors closed, normal obstacles; log sequences, gaps and dwell events | No false completion, no ACK-timeout silence, no counting absent/unknown presence toward X; interruption/recovery behavior matches state contract | NOT RUN |
| Switching ringing / parasitics | Differential probing with short connections at regulator and amplifier supply nodes; measure overshoot/undershoot at startup, radio bursts and alarm transients | Compare to exact datasheet limits with margin; preserve captures and probe setup. No oscilloscope data has been supplied | NOT RUN |
| EMI screening | Compare supply/near-field spectra during sleep, ESP-NOW and alarm operation; vary wire routing and closed shell; repeat radio checks | Explain and address repeatable coupling/noise regressions; this is screening, not radiated/conducted-emissions certification | NOT RUN |

## Free software workflow for the acoustic comparison

Use the free single-channel features of [REW](https://www.roomeqwizard.com/) for response, spectrum and distortion analysis. No paid REW upgrade is needed. Follow its [measurement setup](https://www.roomeqwizard.com/help/help_en-GB/html/makingmeasurements.html): keep drive level, microphone position and gain fixed, avoid clipping and apply calibration where available. Save the native measurement files and export traces. A calibrated borrowed microphone or meter can establish SPL; an uncalibrated microphone is useful for controlled relative comparisons but does not establish absolute pillow SPL. Disable automatic gain control/noise suppression when possible and verify repeatability.

For the assembled ESP32 alarm, the test stimulus must actually pass through its DAC/I²S/amplifier path. Add a firmware test mode that plays a known sweep/WAV at a reproducible level, or use REW's appropriate offline/import workflow with timing accounted for. Do not simply measure a different computer-driven amplifier and call it the board's result. Actual alarm recordings and RTA comparisons can precede this firmware work.

Start at low drive, especially below the small driver's resonance. Measure the same physical setup three times; if repeatability exceeds about 1 dB over the comparison band, fix placement/gain/noise before interpreting a 2 dB difference. The user should judge the awake listening level before any scheduled wake-up trial; a louder measurement alone does not demonstrate reliable waking.

Optional impedance measurements can help identify enclosure resonance, but require a correctly built/calibrated jig and a speaker disconnected from the alarm amplifier. Follow [REW's impedance instructions](https://www.roomeqwizard.com/help/help_en-GB/html/impedancemeasurement.html). **Do not attach a grounded sound-card input or oscilloscope ground clip to either BTL speaker output.** Neither output is ground; use an appropriate differential measurement arrangement for the powered amplifier.

Python and CSV files suffice for battery/temperature logging and plotting. Free software cannot replace the microphone, probes, temperature sensors or radio test hardware needed to collect evidence. No software-only thermal or EMI qualification is claimed.

## Remaining release blockers

'''+ '\n'.join('- '+x for x in v['unresolved'])+'\n'
(R/'TEST-REPORT.md').write_text(report)
# Blank physical measurement register; no synthetic measured data.
fields=['test_id','test_name','status','enclosure_revision','speaker_serial','firmware_commit','alarm_file_sha256','battery_chemistry','battery_loaded_V','drive_setting','mic_calibration','position','ambient_C','measurement_file','observations','pass_fail']
if not (R/'physical-test-log.csv').exists():
 with (R/'physical-test-log.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
  for i,name in enumerate(['Basic part fit','New display electrical integration','Service controls','Grille and cloth loss','Small chamber response','Old versus new arrangement','Direction and bedside placement','Distortion and rattles','Pod leakage','Continuous load and cooling','Overnight energy reserve','Radio and dwell','Switching ringing and parasitics','EMI screening'],1):w.writerow(dict(test_id=f'PHY-{i:02}',test_name=name,status='NOT_RUN',enclosure_revision='v4.1'))
# Dimensioned two-view sheet.
a=[]
def add(s):a.append(s)
def t(x,y,s,size=18,color='#263a3e',anchor='start',bold=False):add(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" text-anchor="{anchor}" font-weight="{700 if bold else 400}">{html.escape(s)}</text>')
def rect(x,y,w,h,fill,stroke='#526b72',dash=''):add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" '+(f'stroke-dasharray="{dash}"' if dash else '')+'/>')
def line(x,y,X,Y,col='#526b72'):add(f'<path d="M{x},{y} L{X},{Y}" stroke="{col}" fill="none"/>')
def circ(x,y,r,fill='white'):add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="#526b72"/>')
def dim(x,y,X,Y,label):
 add(f'<path d="M{x},{y} L{X},{Y}" stroke="#526b72" marker-start="url(#arr)" marker-end="url(#arr)"/>');t((x+X)/2,y-9,label,17,anchor='middle')
add('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1100" viewBox="0 0 1600 1100"><defs><marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M10 1L1 5L10 9" fill="none" stroke="#526b72"/></marker></defs><rect width="1600" height="1100" fill="#f4f6f5"/><g font-family="Arial, sans-serif">')
t(60,65,'BEDROOM ALARM / V4.1',34,bold=True);t(60,103,'Direct radiator • Protected setup panel • 105 mm body • All dimensions in mm',20)
rect(60,126,1480,48,'#fff0d4','#d6a65d');t(82,157,'PACKAGING PROTOTYPE — geometry checked; amber dimensions and physical performance remain unqualified.',19,'#835111')
t(100,224,'SIDE SECTION / front at left',23,bold=True);t(860,224,'BOTTOM SERVICE / front at top',23,bold=True)
k=4.0;ox=332;oy=716
X=lambda y:ox+k*y;Z=lambda z:oy-k*z
D=lambda y0,z0,y1,z1,fill,stroke='#526b72',dash='':rect(X(y0),Z(z1),k*(y1-y0),k*(z1-z0),fill,stroke,dash)
D(-52.5,0,52.5,105,'#e2e8e7');D(-50.1,2.4,50.1,102.6,'white')
D(-44.5,46.8,8.7,102,'#b9ccd0');D(-42.1,49.2,6.3,99.6,'white')
D(-45,48.75,-43.5,101.25,'#2c3b40');D(-45,52.1,-27.5,97.9,'#66777d');D(-27.5,52.5,-11.5,97.5,'#a5afb3')
D(-48.5,52,-45,98,'none','#bb811a','5 3');D(-51.15,22,-50.95,98,'#263a3e');D(-52.5,22,-51.3,98,'#738489')
D(-28,42.4,28,44,'#398261');D(-28,33.865,34.25,45.405,'none','#398261','5 3')
D(-13,23,39,25,'#b8c8c8');D(-10.305,5.61,36.305,23,'#c4d1d8')
D(-46.25,6.8,-12.75,19.3,'#f6d192','#ac7719');D(12.75,26.405,49.25,57.405,'none','#d47d1b','6 4')
D(-49,4,49,6,'none','#526b72');D(-52.25,0,52.25,2.4,'#596b70')
# Outward sound arrow is explanatory, not a simulated field.
add(f'<path d="M{X(-48)} {Z(75)} L{X(-66)} {Z(75)}" stroke="#207d7f" stroke-width="3" marker-end="url(#arr)"/>');t(64,Z(75)+32,'SOUND',15,'#207d7f')
dim(X(-52.5),Z(105)-20,X(52.5),Z(105)-20,'105')
for z,label,y in [(101,'Pod roof: 102',318),(75,'Driver axis: Z=75',395),(46.8,'Pod floor: 46.8',486),(44,'PCB datum: 44',526),(24,'Carrier: 23–25',602),(23,'Holder top: 23',646),(1.2,'Cover: 0–2.4',707)]:
 line(X(44),Z(z),590,y-5);t(599,y,label,16)
t(100,751,'Orange: 15 mm antenna reserve, shown in projection.',16,'#a46c17')
t(100,777,'Actual parts separated in X may overlap in this view.',16,'#647478')
px,py=1120,502
PX=lambda x:px+4*x;PY=lambda y:py+4*y
B=lambda x0,y0,x1,y1,fill,stroke='#526b72',dash='':rect(PX(x0),PY(y0),4*(x1-x0),4*(y1-y0),fill,stroke,dash)
B(-52.5,-52.5,52.5,52.5,'#e2e8e7');B(-49,-49,49,49,'#eef2ef')
B(-28.575,-10.305,28.575,36.305,'#b8cbd3')
for y in [-2.125,13,28.125]:B(-25.25,y-7.25,25.25,y+7.25,'#e1e8e8')
B(-4,-14,4,40,'#506268');B(-15,-11,-9,37,'#e7bf80')
B(-35.7,-46.25,-.3,-12.75,'#f6d192','#ac7719');B(-33.9,-40.1,-2.1,-23,'#283a40')
for x in [-33.2,-2.8]:
 for y in [-43.75,-15.25]:circ(PX(x),PY(y),6)
B(-23.5,-46,-12.5,-42.5,'#dba750')
t(PX(-18),PY(-30),'1.3 OLED',17,'white',anchor='middle')
B(13,-47,40,-13,'none','#be861d','4 3')
for y,label in [(-43,'+'),(-31,'SET'),(-19,'−')]:circ(PX(20),PY(y),20,'#b5c0bf');t(PX(28),PY(y)+5,label,13,anchor='middle')
B(33.25,-36.5,38.75,-21.5,'#596b70')
for x in [-45,45]:
 for y in [-43,43]:circ(PX(x),PY(y),6.8)
dim(PX(-52.5),PY(-52.5)-20,PX(52.5),PY(-52.5)-20,'105')
t(px,PY(-55),'FRONT',15,anchor='middle');t(px,PY(45),'3 × AA / cell bridge and pull ribbon',17,anchor='middle')
t(870,751,'Holder body: 57.15 × 46.61 × 17.39 CAD height.',16)
t(870,777,'OLED: 35.4 × 33.5; mating socket remains provisional.',16)
line(60,818,1540,818,'#c1cecd')
t(70,857,'CLEARANCE AND ACOUSTIC RECORD',22,bold=True)
record=[('Speaker / fixing','Ø52.5 body; 68 lug span; 60 hole centres; Ø4.2 holes; Ø46 cutout'),('Maximum moving envelope','2.80 to grille; 2.45 to allocated cloth; fabric movement unqualified'),('Rear chamber','0.1981 L GROSS before driver, bosses, wires and damping; net volume unverified'),('Four grille fields','418 openings per face, 1,672 total; Ø3.2 nominal; 4 pitch; 1.2 thick'),('Electrical scope','Actual main PCB unchanged; new control/front UI boards are allocations, not routed designs')]
for i,(label,value) in enumerate(record):t(74,898+i*34,label,16,bold=True);t(352,898+i*34,value,16)
add('</g></svg>');(R/'dimensioned-layout.svg').write_text(''.join(a))
# Self-contained local HTML gallery; no external fonts/scripts.
images=[('exterior-front-right.png','Exterior — one button and one normally dark lens'),('exterior-rear-left.png','Matching perforations on the other two faces'),('acoustic-cutaway.png','Direct driver and rear pod — roof and one wall hidden for inspection'),('bottom-service.png','Protected bottom setup face — outer cover removed'),('internals.png','Actual PCB and component arrangement'),('clearances.png','Clearance allocations — orange RF volume'),('dimensioned-layout.png','Dimensioned arrangement and limits')]
body=''.join(f'<figure><a href="{f}"><img src="{f}" alt="{html.escape(cap)}" loading="lazy"></a><figcaption>{html.escape(cap)}</figcaption></figure>' for f,cap in images)
(R/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bedroom alarm v4.1</title><style>body{margin:0;background:#eef1ef;color:#263a3e;font:17px/1.5 system-ui}main{max-width:1180px;margin:auto;padding:32px}h1{font-size:40px;margin-bottom:8px}nav{display:flex;flex-wrap:wrap;gap:18px;margin:24px 0}a{color:#146d70}.notice{background:#ffedcf;padding:18px;border-radius:8px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}figure{margin:0;background:white;border-radius:12px;overflow:hidden}img{display:block;width:100%}figcaption{padding:14px}figure:last-child{grid-column:1/-1}@media(max-width:700px){.grid{grid-template-columns:1fr}h1{font-size:30px}}</style><main><h1>Bedroom alarm / v4.1</h1><p>105 mm body · Direct front speaker · Four perforated walls · Protected bottom setup</p><p class="notice">{CHECK_COUNT} nominal geometry checks passed. Physical acoustic, battery, thermal and radio tests are pending. Amber parts and new PCB interfaces remain provisional.</p><nav><a href="bedroom-cube-v4-1.blend">Assembled Blender</a><a href="bedroom-cube-v4-1-acoustic-cutaway.blend">Acoustic cutaway</a><a href="bedroom-cube-v4-1-service.blend">Bottom service</a><a href="DISPLAY-UPDATE.md">Display update</a><a href="DESIGN-REVIEW.md">Design review</a><a href="TEST-REPORT.md">Test report</a><a href="PCB-INTERFACE.md">PCB revision brief</a></nav><div class="grid">'''+body+'</div></main></html>')
page=R/'index.html';page.write_text(page.read_text().replace('{CHECK_COUNT}',str(len(v['checks']))))
manifest=dict(date='2026-09-06',source_pcb_sha256=p['pcb_sha256'],files={})
for folder in [R/'sources']:
 for f in folder.iterdir():
  if f.is_file():manifest['files'][str(f.relative_to(R))]=hashlib.sha256(f.read_bytes()).hexdigest()
manifest['upstream_manifest']='sources/source-manifest.json'
manifest['files']['reference/bedroom-cube-v4.blend']=hashlib.sha256((R/'reference/bedroom-cube-v4.blend').read_bytes()).hexdigest()
(R/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Reports, drawing, gallery and physical-test register written.')
