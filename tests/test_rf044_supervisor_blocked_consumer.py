"""RF-044 C2/C3: supervisor consumers receive a serializable blocked artifact."""

from __future__ import annotations

import copy
import json

from libs.contracts.agent_outputs import build_supervisor_output_artifact


def test_rf044_supervisor_blocked_order_normalizes_fake_inputs_without_state_mutation():
    state = {
        "run_id": "rf044-supervisor-blocked",
        "started_at": "2026-10-29T04:11:00+09:00",
        "runtime_phase": "preopen",
    }
    order = {
        "intent_id": "fake-intent-1",
        "action": " buy ",
        "symbol": "005930",
        "qty": "not-a-number",
        "order_type": "limit",
    }
    before = copy.deepcopy(state)

    artifact = build_supervisor_output_artifact(
        state,
        order=order,
        allowed=False,
        reason="fake approval denied",
        details=["not-a-dict"],
        strategy_policy_summary=["not-a-dict"],
    )

    assert state == before
    assert artifact["decision"] == artifact["verdict"] == "block"
    assert artifact["status"] == "blocked"
    assert artifact["command"] == artifact["action"] == "BUY"
    assert artifact["order_request_summary"]["qty"] == 0
    assert artifact["blocked_allowed_details"] == {}
    assert artifact["strategy_policy_summary"] == {}
    assert json.loads(json.dumps(artifact))["intent_id"] == "fake-intent-1"
