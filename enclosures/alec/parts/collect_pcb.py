"""Read-only extraction of the actual KiCad PCB and model provenance."""
import csv, hashlib, json
from pathlib import Path
import pcbnew

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
D=REPO/'boards/esp32s3-devkit-5v'
pcb=D/'esp32s3-devkit-5v.kicad_pcb'
b=pcbnew.LoadBoard(str(pcb))
inventory={r['Reference']:r for r in csv.DictReader((D/'review/component-inventory.csv').open())}
models=json.loads((D/'3dmodels/model-map.json').read_text())
def mm(v): return round(pcbnew.ToMM(v),6)
outline=b.GetBoardEdgesBoundingBox()
edge_points=[]
for shape in b.GetDrawings():
    if shape.GetLayer()!=pcbnew.Edge_Cuts: continue
    assert int(shape.GetShape())==0, 'Non-segment edge requires an exact curve-extrema extraction'
    edge_points.extend([[mm(shape.GetStart().x),mm(shape.GetStart().y)],
                        [mm(shape.GetEnd().x),mm(shape.GetEnd().y)]])
edge_min=[min(p[i] for p in edge_points) for i in range(2)]
edge_max=[max(p[i] for p in edge_points) for i in range(2)]
records=[]; holes=[]; points=[]
for f in b.GetFootprints():
    ref=f.GetReference()
    if ref.startswith('H'):
        for p in f.Pads():
            holes.append({'reference':ref,'xy_mm':[mm(p.GetPosition().x),mm(p.GetPosition().y)],
                          'drill_xy_mm':[mm(p.GetDrillSize().x),mm(p.GetDrillSize().y)]})
        continue
    if ref.startswith('TP'):
        points.append({'reference':ref,'xy_mm':[mm(f.GetPosition().x),mm(f.GetPosition().y)]})
        continue
    row=inventory[ref]; model=models[f.GetFPIDAsString()]
    model_path=D/model['path'].replace('${KIPRJMOD}/','')
    digest=hashlib.sha256(model_path.read_bytes()).hexdigest()
    assert digest==model['sha256'], 'Model changed since provenance audit: '+ref
    records.append({
        'reference':ref,'value':row['Value'],'mpn_field':row['MPN field'] or None,
        'footprint':f.GetFPIDAsString(),'datasheet':row['Datasheet'] or None,
        'populated':not f.IsDNP(),'xy_mm':[mm(f.GetPosition().x),mm(f.GetPosition().y)],
        'rotation_deg':f.GetOrientationDegrees(),'board_layer':b.GetLayerName(f.GetLayer()),
        'model_path':str(model_path.relative_to(REPO)),'model_sha256':digest,
        'model_classification':model['classification'],
        'model_matches_recorded_hash':True,
        'exact_ordered_part_geometry_verified':False,
        'model_transform':{k:model[k] for k in ['offset','rotation','scale']},
        'remaining_check':('Exclude from populated enclosure assembly' if f.IsDNP() else
            'Confirm selected manufacturer/order variant and maximum package height; compare model to drawing')
    })
assert len(records)==len(inventory)
data={
    'source_pcb':str(pcb.relative_to(REPO)), 'source_pcb_sha256':hashlib.sha256(pcb.read_bytes()).hexdigest(),
    'outline_centerline_bbox_xy_mm':[*edge_min,*[edge_max[i]-edge_min[i] for i in range(2)]],
    'outline_graphic_bbox_including_stroke_mm':[mm(outline.GetX()),mm(outline.GetY()),mm(outline.GetWidth()),mm(outline.GetHeight())],
    'board_thickness_mm':mm(b.GetDesignSettings().GetBoardThickness()),
    'mounting_holes':sorted(holes,key=lambda x:x['reference']),
    'test_points':sorted(points,key=lambda x:x['reference']),
    'pcb_components':sorted(records,key=lambda x:x['reference']),
    'complete_assembly_model_extent_mm':[65.5,62.25,11.54],
    'extent_basis':'Existing STEP audit and successful GLB re-import; generic component heights are not exact ordered-part qualification'
}
(ROOT/'pcb-evidence.json').write_text(json.dumps(data,indent=2)+'\n')
fields=['reference','value','mpn_field','populated','footprint','datasheet','model_path','model_classification',
        'model_matches_recorded_hash','exact_ordered_part_geometry_verified','remaining_check']
with (ROOT/'pcb-components.csv').open('w',newline='') as out:
    w=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(data['pcb_components'])
print(json.dumps({k:v for k,v in data.items() if k not in ['pcb_components','test_points']},indent=2))
print('Electrical footprint count:',len(records),'Populated:',sum(r['populated'] for r in records))
