"""Export the curated current parts register without replacing its evidence."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
register = json.loads((ROOT / "parts-register.json").read_text())
pcb = json.loads((ROOT / "pcb-evidence.json").read_text())
fields = ["id", "part", "identification", "source", "status", "remaining_checks"]
with (ROOT / "mechanical-parts.csv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for item in register["mechanical_items"]:
        writer.writerow({key: "; ".join(item[key]) if key == "remaining_checks" else item[key]
                         for key in fields})
summary = {
    "mechanical_items": len(register["mechanical_items"]),
    "pcb_footprints": len(pcb["pcb_components"]),
    "populated_pcb_components": sum(c["populated"] for c in pcb["pcb_components"]),
    "unpopulated_refs": [c["reference"] for c in pcb["pcb_components"] if not c["populated"]],
    "model_classes_populated": dict(Counter(c["model_classification"] for c in pcb["pcb_components"] if c["populated"])),
    "all_parts_dimensionally_verified": register["all_parts_dimensionally_verified"],
    "pending_user_input": register["pending_user_input"],
}
(ROOT / "audit-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(f"Exported {len(register['mechanical_items'])} mechanical items.")
