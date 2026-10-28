"""RF-066 C2/C3: maintenance cleanup is confined to caller-owned temp roots."""

from __future__ import annotations

import json

from scripts.maintenance.clean_evaluation_test_contamination import clean_event_log


def test_rf066_clean_event_log_dry_run_then_quarantines_only_temp_rows(tmp_path):
    root = tmp_path / "root"
    events_path = root / "data" / "logs" / "events.jsonl"
    events_path.parent.mkdir(parents=True)
    valid = {"run_id": "prod_005930", "symbol": "005930"}
    synthetic = {"run_id": "pytest_fixture", "symbol": "BAD"}
    events_path.write_text(
        json.dumps(valid) + "\n" + json.dumps(synthetic) + "\n", encoding="utf-8"
    )
    quarantine = tmp_path / "quarantine"

    assert clean_event_log(root, quarantine, apply=False) == {"removed_events": 1}
    assert events_path.read_text(encoding="utf-8").count("\n") == 2

    assert clean_event_log(root, quarantine, apply=True) == {"removed_events": 1}
    assert events_path.read_text(encoding="utf-8") == json.dumps(valid) + "\n"
    rejected = quarantine / "data" / "logs" / "events.jsonl"
    assert rejected.read_text(encoding="utf-8") == json.dumps(synthetic) + "\n"
