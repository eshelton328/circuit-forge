"""Fail closed when the parts register cannot support a final enclosure fit claim.

This is a documentation/readiness guard, not a collision solver or physical test.
"""
import hashlib, json
from pathlib import Path

R=Path(__file__).resolve().parent
REPO=R.parents[2]
register=json.loads((R/'parts-register.json').read_text())
pcb=json.loads((R/'pcb-evidence.json').read_text())
required={'speaker','display','battery_holder','aa_cells','main_pcb','front_board','service_board',
 'front_button','setup_buttons','service_switch','rgb_indicator','display_window',
 'battery_connection','speaker_connection','display_connection','front_connection','service_connection',
 'usb_service','pcb_mounts','cover_fasteners','speaker_fasteners','acoustic_seals',
 'speaker_chamber','battery_retention','feet','enclosure'}
required.add('acoustic_cloth')
errors=[]
items=register['mechanical_items']
ids=[i['id'] for i in items]
if set(ids)!=required or len(ids)!=len(required):
    errors.append('Mechanical inventory coverage mismatch or duplicate ID')
actual_hash=hashlib.sha256((REPO/pcb['source_pcb']).read_bytes()).hexdigest()
if actual_hash!=pcb['source_pcb_sha256']:
    errors.append('PCB changed: refresh model, mounting geometry and inventory')
unresolved=[{'id':i['id'],'status':i['status']} for i in items
            if not i.get('ready_for_final_enclosure_fit')]
unchecked=[c['reference'] for c in pcb['pcb_components']
           if c['populated'] and not c.get('exact_ordered_part_geometry_verified')]
report={'scope':'Part identification and geometry evidence, not physical qualification',
        'inventory_errors':errors,'unresolved_mechanical_items':unresolved,
        'populated_references_needing_ordered_part_geometry_check':unchecked,
        'ready_for_final_enclosure_fit':not(errors or unresolved or unchecked)}
(R/'fit-readiness.json').write_text(json.dumps(report,indent=2)+'\n')
print('Final enclosure fit readiness:', 'READY' if report['ready_for_final_enclosure_fit'] else 'NOT READY')
print('Inventory errors:',len(errors),'Unresolved mechanical items:',len(unresolved),
      'PCB references without exact ordered-part sign-off:',len(unchecked))
raise SystemExit(0 if report['ready_for_final_enclosure_fit'] else 2)
