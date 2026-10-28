"""RF-044 C2/C3: executor artifact generation does not mutate fake inputs."""

from __future__ import annotations

import copy
import json

from libs.contracts.agent_outputs import build_executor_output_artifact


def test_rf044_executor_artifact_preserves_order_and_execution_inputs():
    state = {"run_id": "rf044-immutable-input", "runtime_phase": "preopen"}
    order = {"intent_id": "fake-1", "action": " buy ", "symbol": "005930", "qty": "2", "meta": {"source": "fake"}}
    execution = {
        "allowed": True,
        "execution_ok": True,
        "status": "accepted",
        "action": " sell ",
        "symbol": "000660",
        "qty": "3",
        "payload": {"response_payload": {"return_msg": "fake accepted"}},
        "quote_snapshot": {"best_bid": "100", "best_ask": "101"},
    }
    before_order, before_execution, before_state = copy.deepcopy(order), copy.deepcopy(execution), copy.deepcopy(state)

    artifact = build_executor_output_artifact(state, execution=execution, order=order)

    if state != before_state or order != before_order or execution != before_execution:
        raise AssertionError("artifact builder mutated a caller input")
    if artifact["action"] != "SELL" or artifact["order_request_summary"]["action"] != "BUY":
        raise AssertionError(artifact)
    if artifact["status"] != "accepted" or artifact["execution_ok"] is not True:
        raise AssertionError(artifact)
    if json.loads(json.dumps(artifact))["broker_result"]["broker_message"] != "fake accepted":
        raise AssertionError(artifact)
