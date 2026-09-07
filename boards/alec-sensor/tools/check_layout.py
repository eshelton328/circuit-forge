#!/usr/bin/env python3
"""Check layout intent beyond DRC. Run with KiCad Python after saved zone fill."""
from pathlib import Path
import argparse
import json
import math
import pcbnew as p

D = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--board', type=Path, default=D / 'alec-sensor.kicad_pcb')
parser.add_argument('--report', type=Path, default=D / 'review/layout-validation.json')
args = parser.parse_args()
b = p.LoadBoard(str(args.board))
fps = {f.GetReference(): f for f in b.GetFootprints()}
tracks = [t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA)]
vias = [t for t in b.GetTracks() if isinstance(t, p.PCB_VIA)]
assert not any(t.GetLayer() == p.In1_Cu for t in tracks), 'In1.Cu must remain an unrouted ground reference'
assert any(z.GetNetname() == 'GND' and z.IsOnLayer(p.In1_Cu) and z.GetFilledPolysList(p.In1_Cu).OutlineCount() for z in b.Zones()), 'Save the filled ground plane first'
converter_caps = {}
for ref, caps in [('U1', ['C3', 'C5']), ('U2', ['C11', 'C13'])]:
    x, y = p.ToMM(fps[ref].GetPosition().x), p.ToMM(fps[ref].GetPosition().y)
    ground = [v for v in vias if v.GetNetname() == 'GND' and abs(p.ToMM(v.GetPosition().x)-x)<.1 and y-5.2 <= p.ToMM(v.GetPosition().y) <= y-3.7]
    assert len(ground) >= 2, (ref, 'PGND needs both nearby plane connections')
    # Proximity alone cannot certify loop inductance. These bounds prevent the
    # previous regression where rotating ceramics doubled their supply paths.
    for cap, pin in zip(caps, ['12', '7']):
        power = next(pd for pd in fps[ref].Pads() if pd.GetNumber() == pin)
        positive = next(pd for pd in fps[cap].Pads() if pd.GetNumber() == '1')
        negative = next(pd for pd in fps[cap].Pads() if pd.GetNumber() == '2')
        distance = lambda a, c: math.hypot(p.ToMM(a.x-c.x), p.ToMM(a.y-c.y))
        separation = distance(power.GetPosition(), positive.GetPosition())
        assert separation <= 2.0, (ref, cap, 'local supply ceramic too far from power pin', separation)
        def intersects_pad(t, pd):
            a, c, q = t.GetStart(), t.GetEnd(), pd.GetPosition()
            dx, dy = c.x-a.x, c.y-a.y
            ratio = max(0, min(1, ((q.x-a.x)*dx+(q.y-a.y)*dy)/(dx*dx+dy*dy))) if dx or dy else 0
            return pd.HitTest(p.VECTOR2I(round(a.x+ratio*dx), round(a.y+ratio*dy)))
        direct = [t for t in tracks if t.GetNetname() == positive.GetNetname()
                  and t.GetLayer() == p.F_Cu and p.ToMM(t.GetWidth()) >= .4-1e-6
                  and intersects_pad(t, power) and intersects_pad(t, positive)]
        assert direct, (ref, cap, 'requires a direct top-side supply connection at least 0.4 mm wide')
        nearest_ground_via = min(distance(negative.GetPosition(), v.GetPosition())
                                 for v in vias if v.GetNetname() == 'GND')
        assert nearest_ground_via <= 1.2, (ref, cap, 'missing local capacitor return via')
        converter_caps[cap] = {'ic': ref, 'power_pad_separation_mm': round(separation, 4),
                               'direct_supply_track_min_width_mm': .4,
                               'ground_pad_to_via_mm': round(nearest_ground_via, 4)}
    for pin in ['9', '11']:
        net = next(pd.GetNetname() for pd in fps[ref].Pads() if pd.GetNumber() == pin)
        assert not any(v.GetNetname() == net for v in vias), (ref, net)
        assert all(t.GetLayer() == p.F_Cu for t in tracks if t.GetNetname() == net), (ref, net)
# Exact footprint and switching-node geometry comparison against the reviewed source.
source=p.LoadBoard(str(D.parent/'esp32s3-devkit-5v/esp32s3-devkit-5v.kicad_pcb'))
old={f.GetReference():f for f in source.GetFootprints()}
unchanged=['U1','U2','L1','L2']+[f'C{i}' for i in range(1,17)]+[f'R{i}' for i in range(3,11)]
for ref in unchanged:
 assert fps[ref].GetPosition()==old[ref].GetPosition() and fps[ref].GetOrientationDegrees()==old[ref].GetOrientationDegrees(),ref
 assert fps[ref].GetFPIDAsString()==old[ref].GetFPIDAsString(),ref
for ref in ['U1','U2']:
 for pin in ['9','11']:
  net=next(pd.GetNetname() for pd in fps[ref].Pads() if pd.GetNumber()==pin)
  def signature(board):
   return sorted((t.GetLayer(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth()) for t in board.GetTracks() if t.GetNetname()==net)
  assert signature(b)==signature(source),(ref,net,'switch node copper changed')
# Wider series-battery path, and uninterrupted In1 reference are checked on saved copper.
series={}
for n in ['/VBAT','/VBAT_FUSED','/VBAT_SW']:
 ts=[t for t in tracks if t.GetNetname()==n]
 assert ts and all(p.ToMM(t.GetWidth())>=.75-1e-6 for t in ts),n
 length=sum(p.ToMM(t.GetLength()) for t in ts)
 resistance=sum(1.724e-8*(p.ToMM(t.GetLength())*.001)/(p.ToMM(t.GetWidth())*.001*35e-6) for t in ts)
 series[n]={'sum_track_length_mm':round(length,3),'minimum_width_mm':.75,'track_resistance_35um_copper_20C_ohm':resistance}
# Independently compare native PCB locations with the enclosure interface.
interface=json.loads((D.parents[1]/'enclosures/alec-sensor/interface.json').read_text())
cx,cy=interface['pcb_center_kicad']
def front_xy(point):return [round(p.ToMM(point.x)-cx,4),round(cy-p.ToMM(point.y),4)]
assert front_xy(fps['SW7'].GetPosition())==interface['button_xy'],'button/plunger mismatch'
assert front_xy(fps['D2'].GetPosition())==interface['led_xy'],'LED/light pipe mismatch'
pin1=next(pd for pd in fps['J3'].Pads() if pd.GetNumber()=='1')
assert front_xy(pin1.GetPosition())==interface['radar']['pin1_xy'],'radar socket/CAD mismatch'
# Rear service is a physical assembly contract: controls must face the battery opening.
for ref,c in interface['service_controls'].items():
 f=fps[ref]
 assert f.GetLayer()==p.B_Cu,(ref,'service control must face rear/batteries')
 assert [round(p.ToMM(f.GetPosition().x),4),round(p.ToMM(f.GetPosition().y),4)]==c['kicad_xy'],(ref,'service bay position mismatch')
for ref in ['J3','SW7','D2']:
 assert fps[ref].GetLayer()==p.F_Cu,(ref,'radar/exterior interface must face outward')
assert interface['battery_holder']['opening'].startswith('rear (-Z)'),'battery holder must open toward rear panel'
mounts=sorted([round(p.ToMM(fps[f'H{i}'].GetPosition().x),4),round(p.ToMM(fps[f'H{i}'].GetPosition().y),4)] for i in range(1,5))
assert mounts==sorted(interface['pcb_mounts_kicad']),'PCB mount/CAD mismatch'
assert abs(p.ToMM(b.GetDesignSettings().GetBoardThickness())-interface['pcb_thickness'])<1e-6,'PCB thickness/CAD mismatch'
report={'passed':True,'outline_mm':[64,56],'layers':b.GetCopperLayerCount(),'in1_signal_tracks':0,'enclosure_interface_matches':True,'rear_service_controls':[c['name'] for c in interface['service_controls'].values()],'electrical_footprints':len([r for r in fps if not r.startswith(('TP','H'))]),'track_segments':len(tracks),'vias':len(vias),'converter_capacitors':converter_caps,'unchanged_converter_footprints':unchanged,'switch_node_copper_matches_reviewed_source':True,'battery_series_copper':series,'scope':'Saved copper geometry guards. Resistance sums assume 35 um copper and omit vias/contacts/temperature; no parasitic inductance, RF or thermal qualification.'}
args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
