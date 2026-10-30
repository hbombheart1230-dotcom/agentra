from graphs.nodes.strategist_node import _resolve_strategist_llm_call_kind
from libs.runtime.strategist.llm.stage_call_kind import resolve_strategist_llm_call_kind


def test_closeout_precedes_hold_and_wrapper_parity():
    payload = {"commander_refresh_context": {"requested": True, "refresh_scope": "open_position_closeout"}}
    assert _resolve_strategist_llm_call_kind(payload) == resolve_strategist_llm_call_kind(payload) == "end_of_day_carry_review"


def test_hold_selected_and_explicit_invalid_payloads():
    assert resolve_strategist_llm_call_kind({"commander_refresh_context": {"requested": True, "carry_state": "held"}}) == "stale_intraday_hold_review"
    assert resolve_strategist_llm_call_kind({"commander_refresh_context": {"requested": True}}) == "selected_symbol_tactical_refresh"
    assert resolve_strategist_llm_call_kind({"resolved_call_kind": "market_strategy_frame"}) == "market_strategy_frame"
    assert resolve_strategist_llm_call_kind(None) == "market_strategy_frame"
