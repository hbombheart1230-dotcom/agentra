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



def reason_summary(
    *,
    no_trade_reason_code: str,
    observations: Dict[str, Any],
    actual_runtime: Dict[str, Any],
    facade,
) -> str:
    llm_status = facade._clip(observations.get("last_llm_status"), max_len=40) or "unknown"
    monitor_decision = facade._clip(actual_runtime.get("monitor_decision"), max_len=24) or "WAIT"
    executor_action = facade._clip(actual_runtime.get("executor_action"), max_len=24) or "NONE"
    mapping = {
        "NONE": f"Observed runtime ended with monitor={monitor_decision} and executor={executor_action} without a stronger commander block signal.",
        "POSITION_ALREADY_OPEN": "Open position state already existed, so monitor-only observation was more appropriate than a fresh strategist cycle.",
        "RISK_BLOCKED": "Risk or portfolio guard signals were stronger than any need to refresh strategist context in this cycle.",
        "EXECUTION_BLOCKED": "Execution or approval constraints were the main reason to stand down, independent of strategist quality.",
        "DATA_INSUFFICIENT": "Available minute, feature, or symbol data was too thin to justify a fresh strategist-driven trade attempt.",
        "NO_MARKET_CHANGE": "The cycle looked materially similar to the prior context, so a new strategist run likely added little value.",
        "LLM_UNSTABLE": f"Recent strategist LLM status was {llm_status}, so a compact or minimal retry would have been safer than a full refresh.",
        "LOW_CONFIDENCE": "Signal confidence was weak enough that waiting for stronger confirmation looked safer than acting now.",
        "LOW_SIGNAL_QUALITY": "Monitor signal quality was too weak to justify a trade, even if strategist context was available.",
        "REPEATED_SAME_CONTEXT": "The cycle repeated nearly the same strategist context, suggesting reuse or skip would have been reasonable.",
        "WAIT_FOR_CONFIRMATION": "Monitor gates were not fully aligned yet, so waiting for another bar or clearer confirmation looked appropriate.",
    }
    return mapping.get(no_trade_reason_code, "Shadow commander observed the cycle, but the evidence was limited and should be treated as advisory only.")
