from libs.contracts.agent_outputs import _commander_shadow_no_trade_reason_code
from libs.contracts.agent_output_parts.commander_shadow_advice import no_trade_reason_code
import libs.contracts.agent_outputs as facade


def _reason(state, observations=None, runtime=None, path=""):
    observations = observations or {}
    runtime = runtime or {}
    return _commander_shadow_no_trade_reason_code(state, observations=observations, actual_runtime=runtime, path=path)


def test_shadow_advice_priorities_and_owner_wrapper_parity():
    assert _reason({}, runtime={"monitor_decision": "BUY"}) == "NONE"
    assert _reason({"monitor": {"open_position_count": 1, "buy_blocked_open_position": True}}) == "POSITION_ALREADY_OPEN"
    assert _reason({"portfolio_preflight": {"blocked": True}}) == "RISK_BLOCKED"
    assert _reason({"execution": {"allowed": False, "reason": "blocked"}}) == "EXECUTION_BLOCKED"
    state = {"selected": {"symbol": "005930", "confidence": 0.5499}}
    assert _reason(state) == "LOW_CONFIDENCE"
    assert no_trade_reason_code(state, observations={}, actual_runtime={}, path="", facade=facade) == _reason(state)
