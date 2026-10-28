"""RF-044 C2: contract builders preserve an in-memory state boundary."""

from __future__ import annotations

import copy
import json

from libs.contracts.agent_outputs import (
    build_monitor_output_artifact,
    build_scanner_output_artifact,
)


def test_rf044_scanner_and_monitor_outputs_are_json_serializable_without_mutating_state():
    """Two external consumers can serialize a minimal state without shared mutation."""
    state = {
        "run_id": "rf044-state",
        "started_at": "2026-10-28T12:00:00+00:00",
        "runtime_phase": "preopen",
        "runtime_status": "ready",
        "path": "rf044_state_serialization",
        "selected": {"symbol": "005930", "score": 0.7},
    }
    before = copy.deepcopy(state)

    scanner = build_scanner_output_artifact(state)
    monitor = build_monitor_output_artifact(state)

    assert state == before
    assert (scanner["agent"], monitor["agent"]) == ("scanner", "monitor")
    assert json.loads(json.dumps(scanner))["run_id"] == "rf044-state"
    assert json.loads(json.dumps(monitor))["run_id"] == "rf044-state"
