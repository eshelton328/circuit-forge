"""Keep the committed enclosure review usable without a local output directory.

These checks validate evidence and packaging. Blender's geometric checks are
run separately; no physical qualification is inferred from pytest.
"""
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ENCLOSURE = ROOT / "enclosures/bedroom-alarm"


def read_json(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_sources_and_native_pcb_match_committed_evidence():
    manifest = read_json(ENCLOSURE / "source-manifest.json")
    for relative, expected in manifest["files"].items():
        assert sha(ENCLOSURE / relative) == expected, relative
    upstream = read_json(ENCLOSURE / manifest["upstream_manifest"])
    for relative, evidence in upstream["files"].items():
        assert sha(ENCLOSURE / "sources" / relative) == evidence["sha256"], relative
    pcb = read_json(ENCLOSURE / "parts/pcb-evidence.json")
    dimensions = read_json(ENCLOSURE / "dimensions.json")
    assert sha(ROOT / pcb["source_pcb"]) == pcb["source_pcb_sha256"]
    assert pcb["source_pcb_sha256"] == dimensions["pcb_sha256"] == manifest["source_pcb_sha256"] == upstream["native_pcb_sha256"]


def test_geometry_report_is_bound_to_saved_assembly():
    report = read_json(ENCLOSURE / "verification.json")
    assert report["tested_blend_sha256"] == sha(ENCLOSURE / "bedroom-cube-v4-1.blend")
    assert report["status"] == "NOMINAL_GEOMETRY_CHECKS_PASS"
    assert report["checks"] and all(check["passed"] for check in report["checks"])
    assert report["failed_checks"] == []
    assert report["physical_qualification_performed"] is False
    assert report["manufacturing_release"] is False


def test_documentation_and_gallery_have_no_missing_local_files():
    documents = sorted(ENCLOSURE.rglob("*.md")) + [ENCLOSURE / "index.html"]
    for document in documents:
        text = document.read_text()
        targets = re.findall(r'\]\(([^)]+)\)', text) if document.suffix == ".md" else re.findall(r'(?:href|src)="([^"]+)"', text)
        for target in targets:
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            assert not parsed.path.startswith("/"), (document.name, target)
            local = (document.parent / unquote(parsed.path)).resolve()
            assert local.is_relative_to(ROOT), (document.name, target)
            assert local.exists(), (document.name, target)
        assert "/Users/" not in text
        assert "output/bedroom-cube" not in text


def test_readiness_guard_matches_current_register():
    process = subprocess.run([sys.executable, str(ENCLOSURE / "parts/check_fit_readiness.py")],
                             cwd=ROOT, capture_output=True, text=True)
    assert process.returncode == 2, process.stdout + process.stderr
    report = read_json(ENCLOSURE / "parts/fit-readiness.json")
    assert report["inventory_errors"] == []
    register = read_json(ENCLOSURE / "parts/parts-register.json")
    unresolved = {item["id"] for item in register["mechanical_items"] if not item["ready_for_final_enclosure_fit"]}
    assert {item["id"] for item in report["unresolved_mechanical_items"]} == unresolved
    with (ENCLOSURE / "parts/mechanical-parts.csv").open() as stream:
        assert {item["id"] for item in csv.DictReader(stream)} == {item["id"] for item in register["mechanical_items"]}


def test_report_regeneration_preserves_measurements_and_rejects_stale_scene(tmp_path):
    # Only committed project files are copied: no Git history, /Users path or output/ tree.
    copied = tmp_path / "enclosure"
    shutil.copytree(ENCLOSURE, copied)
    log = copied / "physical-test-log.csv"
    recorded = log.read_bytes() + b"sample-record-preservation-check\n"
    log.write_bytes(recorded)
    command = [sys.executable, str(copied / "build_report.py")]
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert log.read_bytes() == recorded
    model = copied / "bedroom-cube-v4-1.blend"
    model.write_bytes(model.read_bytes() + b"changed scene")
    previous_report = (copied / "TEST-REPORT.md").read_bytes()
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode != 0
    assert "Saved assembly changed" in result.stderr
    assert (copied / "TEST-REPORT.md").read_bytes() == previous_report
    assert log.read_bytes() == recorded
