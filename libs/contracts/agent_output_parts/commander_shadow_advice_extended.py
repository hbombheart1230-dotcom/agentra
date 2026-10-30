from __future__ import annotations
from typing import Any, Dict


def llm_call_advice(
    *,
    strategist_action_recommendation: str,
    observations: Dict[str, Any],
    state: Dict[str, Any],
    facade,
) -> str:
    strategist_llm = facade._dict(state.get("strategist_llm"))
    llm_status = str(observations.get("last_llm_status") or strategist_llm.get("status") or "").strip().lower()
    if strategist_action_recommendation == "SKIP" and observations.get("market_changed") is False:
        return "SKIP"
    if strategist_action_recommendation == "SKIP" and observations.get("repeated_same_context") is True:
        return "SKIP"
    if bool(strategist_llm.get("blocked")) or llm_status in {"error", "fallback"}:
        return "RETRY_MINIMAL"
    if llm_status in {"partial", "salvaged", "repaired"}:
        return "RETRY_COMPACT"
    if strategist_action_recommendation == "SKIP":
        return "SKIP"
    return "ALLOW"



def suggested_action(
    *,
    strategist_action_recommendation: str,
    llm_call_advice: str,
    no_trade_reason_code: str,
    facade,
) -> str:
    if strategist_action_recommendation == "SKIP" and no_trade_reason_code == "POSITION_ALREADY_OPEN":
        return "monitor_only_observe"
    if strategist_action_recommendation == "SKIP" and no_trade_reason_code in {"NO_MARKET_CHANGE", "REPEATED_SAME_CONTEXT"}:
        return "skip_strategist_reuse_context"
    if llm_call_advice == "RETRY_COMPACT":
        return "compact_strategist_retry"
    if llm_call_advice == "RETRY_MINIMAL":
        return "minimal_strategist_retry"
    return "allow_current_flow"



def next_action_recommendation(
    *,
    strategist_action_recommendation: str,
    llm_call_advice: str,
    no_trade_reason_code: str,
    actual_runtime: Dict[str, Any],
    facade,
) -> str:
    if no_trade_reason_code == "POSITION_ALREADY_OPEN":
        return "HOLD_OBSERVE"
    if strategist_action_recommendation in {"RETRY_COMPACT", "RETRY_MINIMAL", "USE_FALLBACK"} or llm_call_advice in {
        "RETRY_COMPACT",
        "RETRY_MINIMAL",
    }:
        return "RETRY_COMPACT_NEXT"
    if no_trade_reason_code in {"WAIT_FOR_CONFIRMATION", "LOW_SIGNAL_QUALITY", "LOW_CONFIDENCE", "DATA_INSUFFICIENT"}:
        return "WAIT_NEXT_BAR"
    monitor_decision = facade._clip(actual_runtime.get("monitor_decision"), max_len=24).upper()
    if monitor_decision in {"BUY", "SELL", "HOLD"}:
        return "HOLD_OBSERVE"
    return "NO_ACTION"
