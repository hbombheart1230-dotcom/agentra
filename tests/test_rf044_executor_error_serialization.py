"""RF-044 C2/C3: executor-result DTO keeps a failed broker response in-memory."""

from __future__ import annotations

import copy
import json

from libs.contracts.agent_outputs import build_executor_output_artifact


def test_rf044_executor_error_payload_is_serializable_without_execution_or_state_mutation():
    state = {
        "run_id": "rf044-executor-error",
        "started_at": "2026-10-29T00:10:00+09:00",
        "runtime_phase": "preopen",
    }
    execution = {
        "allowed": False,
        "execution_ok": False,
        "action": "buy",
        "symbol": "005930",
        "qty": "2",
        "reason": "approval_denied",
        "exception_type": "PermissionError",
        "broker_outcome": "NOT_SENT",
        "submission_phase": "approval",
        "reconciliation_required": False,
        "payload": {"response_payload": {"return_msg": "blocked by fake approval"}},
    }
    before = copy.deepcopy(state)

    artifact = build_executor_output_artifact(state, execution=execution, order={"order_type": "limit"})

    assert state == before
    assert artifact["status"] == "blocked by fake approval"
    assert artifact["broker_outcome"] == "NOT_SENT"
    assert artifact["broker_result"]["broker_message"] == "blocked by fake approval"
    assert json.loads(json.dumps(artifact))["exception_type"] == "PermissionError"
