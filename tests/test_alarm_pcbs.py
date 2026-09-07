"""Prevent enclosure-board evidence drift and guard the actual panel/interface contract."""
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'boards/alec-main'
ASSEMBLY=ROOT/'enclosures/alec/pcb-revision'
sys.path.insert(0,str(ROOT/'scripts/alarm'))
from design import parse,children,child,prop,val

def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def test_review_evidence_matches_source_files():
    manifest=read(MAIN/'review/qa-manifest.json')
    assert manifest['manufacturing_release'] is False
    assert not any(name.endswith(('.kicad_prl','.lck')) for name in manifest['files'])
    for name,digest in manifest['files'].items():assert sha(ROOT/name)==digest,name
    for name,digest in manifest['evidence'].items():assert sha(ROOT/name)==digest,name

def test_all_native_boards_have_clean_recorded_erc_drc_and_fab_results():
    for kind in ['main','controls','front']:
        d=ROOT/'boards'/('alec-'+kind)/'review'
        assert not any(s['violations'] for s in read(d/'erc.json')['sheets'])
        for file in ['drc.json','fab-drc.json']:
            r=read(d/file)
            assert not(r['violations']+r['unconnected_items']+r.get('schematic_parity',[]))
        assert read(d/'3d-model-audit.json')['all_model_files_resolved']

def test_panel_plus_minus_follow_real_switch_references_and_positions():
    d=ROOT/'boards/alec-controls'
    board=parse((d/(d.name+'.kicad_pcb')).read_text())
    fps={prop(f,'Reference'):f for f in children(board,'footprint')}
    sch=ET.parse(d/'review/netlist.xml').getroot()
    comps={c.attrib['ref']:c for c in sch.find('components')}
    for ref,label,xy in [('SW3','VOL+',(16.75,27.75)),('SW2','MODE',(16.75,15.75)),('SW1','VOL-',(16.75,3.75))]:
        assert comps[ref].findtext('value')==label
        assert tuple(map(float,child(fps[ref],'at')[1:3]))==xy
    main=ET.parse(MAIN/'review/netlist.xml').getroot()
    pins={(p.attrib['ref'],p.attrib['pin']):net.attrib['name'] for net in main.find('nets') for p in net}
    for ref,external,gpio in [('R50','BTN_VOL_MINUS',4),('R51','BTN_MODE',5),('R52','BTN_VOL_PLUS',6),('R53','BTN_BAT',10)]:
        assert pins[ref,'1']=='/'+external
        assert pins[ref,'2']=='/GPIO'+str(gpio)
    assert pins['J7','3']==pins['U3','37']
    assert pins['J7','4']==pins['U3','36']
    assert pins['J5','7']==pins['R32','1']==pins['U1','14']

def test_harness_negative_controls_fail_and_all_damped_corners_pass():
    r=read(MAIN/'review/harness-simulation.json')
    negative=[c for c in r['button_cases'] if c['series_ohm']==0]
    damped=[c for c in r['button_cases'] if c['series_ohm']>0]
    assert len(negative)==8 and all(not c['screening_limits_met'] for c in negative)
    assert len(damped)==16 and all(c['screening_limits_met'] for c in damped)
    for case in r['button_cases']:
        assert sha(MAIN/'sim'/case['deck'])==case['sha256']
    assert all(c['enable_V']==0 for c in r['enable_cases'] if c['state'] in ['off','unplugged'])
    m=read(MAIN/'review/spice-report.metrics.json')
    assert m['pass'] and len(m['measures'])==105 and all(v['passed'] for v in m['measures'])

def test_geometry_and_physics_are_bound_to_current_sources_without_release_claim():
    g=read(ASSEMBLY/'verification.json')
    assert g['tested_blend_sha256']==sha(ASSEMBLY/'alec-cube-v4-2.blend')
    assert g['status']=='NOMINAL_GEOMETRY_PASS' and all(c['passed'] for c in g['checks'])
    assert not g['physical_qualification_performed'] and not g['manufacturing_release']
    for kind,row in read(ASSEMBLY/'assembly-sources.json').items():
        assert row['pcb_sha256']==sha(ROOT/row['pcb'])
        assert row['glb_sha256']==sha(ASSEMBLY/'sources'/f'{kind}.glb')
    p=read(MAIN/'review/physical-screening/summary.json')
    assert p['manifest']['pcb_sha256']==sha(MAIN/(MAIN.name+'.kicad_pcb'))
    assert p['manifest']['physical_release_approved'] is False
    assert p['gates']['not_demonstrated']
