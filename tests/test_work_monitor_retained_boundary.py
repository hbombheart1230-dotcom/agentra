"""Complete, reproducible exclusions protect every retained Monitor symbol."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("retained_boundary", ROOT / "scripts/refactor/work_monitor_retained_boundary.py")
boundary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(boundary)


def test_retained_exclusions_are_complete_and_match_actual_sources():
    recorded = json.loads((ROOT / "docs/refactor/work_projects/evidence/monitor/continuous/m9_retained_boundary.json").read_text())
    assert boundary.produce() == recorded
    assert recorded["symbol_count"] == 359
    assert len({(r["path"], r["symbol"]) for r in recorded["symbols"]}) == 359
    assert all(r["decision"] == "EXCLUDE_FROM_FURTHER_MOVES" and r["reason"] for r in recorded["symbols"])


def test_changed_retained_source_is_detected_without_executing_it(monkeypatch):
    original = boundary.ast.dump
    monkeypatch.setattr(boundary.ast, "dump", lambda *a, **k: original(*a, **k) + "changed")
    recorded = json.loads((ROOT / "docs/refactor/work_projects/evidence/monitor/continuous/m9_retained_boundary.json").read_text())
    assert boundary.produce() != recorded
