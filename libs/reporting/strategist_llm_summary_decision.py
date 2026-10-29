"""Strategist LLM summary output-quality audit and stage decision projections (moved verbatim).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def strategist_output_quality_audit(
    *,
    payload: Dict[str, Any],
    canonical: Dict[str, Any],
    stage_decision: Dict[str, Any],
    strategy_detail: Dict[str, Any],
    market_rail: Dict[str, Any],
    news_quality: Dict[str, Any],
    facade: Any,
) -> Dict[str, Any]:
    candidate_watch = facade._as_dict(strategy_detail.get("candidate_watch_policy"))
    memory_usage = facade._memory_usage_from_canonical(canonical)
    is_stage_specific = bool(stage_decision.get("is_stage_specific"))
    decision = facade._text(stage_decision.get("decision") or payload.get("decision"), "")
    confidence = stage_decision.get("confidence")
    if confidence in (None, ""):
        confidence = payload.get("confidence")
    issues: List[str] = []
    if not decision:
        issues.append("decision_missing")
    if confidence in (None, ""):
        issues.append("confidence_missing")
    if is_stage_specific:
        if not facade._as_dict(stage_decision.get("monitor_instruction")) and not facade._as_dict(stage_decision.get("entry_policy_delta")):
            issues.append("stage_control_fields_missing")
    else:
        if not facade._text(strategy_detail.get("final_playbook"), ""):
            issues.append("final_playbook_missing")
        if not facade._text(strategy_detail.get("tactical_strategy"), ""):
            issues.append("tactical_strategy_missing")
        if not candidate_watch:
            issues.append("candidate_watch_policy_missing")
    if facade._text(market_rail.get("market_regime_rail"), "") in {"", "macro_packet_unavailable"}:
        issues.append("market_regime_rail_missing")
    if news_quality.get("status") != "ok":
        issues.append("news_quality_not_ok")
    if not bool(memory_usage.get("available")):
        issues.append("memory_trace_missing_or_disabled")
    elif not facade._as_list(memory_usage.get("active_layers")):
        issues.append("memory_active_layers_empty")
    if not issues:
        status = "ok"
    elif len(issues) <= 2:
        status = "watch"
    else:
        status = "needs_review"
    return {
        "schema_version": "strategist_output_quality_audit.v1",
        "status": status,
        "issues": issues,
        "decision": decision,
        "confidence": confidence,
        "final_playbook": facade._text(strategy_detail.get("final_playbook"), ""),
        "tactical_strategy": facade._text(strategy_detail.get("tactical_strategy"), ""),
        "market_regime": facade._text(market_rail.get("market_regime"), ""),
        "market_regime_rail": facade._text(market_rail.get("market_regime_rail"), ""),
        "candidate_watch_policy_present": bool(candidate_watch),
        "memory_available": bool(memory_usage.get("available")),
        "memory_active_layers": facade._as_list(memory_usage.get("active_layers")),
        "news_quality_status": facade._text(news_quality.get("status"), ""),
    }


def stage_decision_from_payload(
    payload: Dict[str, Any],
    raw: Dict[str, Any],
    meta: Dict[str, Any] | None = None,
    *,
    facade: Any,
) -> Dict[str, Any]:
    stage_meta = facade._stage_meta(payload, raw, meta)
    call_kind = facade._text(stage_meta.get("call_kind"), "")
    stage_name = facade._text(stage_meta.get("stage_name") or payload.get("stage_name"), "")
    try:
        stage_index = int(stage_meta.get("stage_index") or payload.get("stage_index") or 0)
    except (TypeError, ValueError):
        stage_index = 0
    is_market_frame = stage_index in (0, 1) and call_kind in {"", "market_strategy_frame", "theme_selection", "strategic_frame"}
    if is_market_frame:
        return {"is_stage_specific": False}

    selected_symbol_review = facade._as_dict(payload.get("selected_symbol_tactical_review"))
    candidate_watch = facade._as_dict(payload.get("candidate_watch_policy"))
    refresh_trace = facade._as_dict(payload.get("strategy_refresh_trace"))
    decision = facade._first_text(
        "",
        selected_symbol_review.get("selected_symbol_decision"),
        payload.get("hold_review_decision"),
        payload.get("carry_review_decision"),
        payload.get("tactical_refresh_decision"),
        payload.get("selected_symbol_decision"),
        payload.get("decision"),
    )
    monitor_adjustment = facade._first_dict(payload.get("monitor_adjustment"), selected_symbol_review.get("monitor_adjustment"))
    priority_exit_triggers = facade._as_list(payload.get("priority_exit_triggers"))
    runner_up_order = facade._as_list(payload.get("runner_up_order")) or facade._as_list(selected_symbol_review.get("runner_up_order"))
    commander_actionability = facade._first_dict(
        payload.get("commander_actionability"),
        selected_symbol_review.get("commander_actionability"),
    )
    if not commander_actionability:
        actionability_text = facade._first_text("", payload.get("commander_actionability"), selected_symbol_review.get("commander_actionability"))
        commander_actionability = {"value": actionability_text} if actionability_text else {}
    return {
        "is_stage_specific": True,
        "stage_index": stage_index,
        "stage_name": stage_name,
        "call_kind": call_kind,
        "stage_component": facade._text(stage_meta.get("stage_component"), ""),
        "decision": decision,
        "target_symbol": facade._first_text("", selected_symbol_review.get("target_symbol"), payload.get("target_symbol")),
        "target_rank": selected_symbol_review.get("target_rank") or payload.get("target_rank"),
        "runner_up_order": runner_up_order,
        "monitor_instruction": facade._first_dict(payload.get("monitor_instruction"), selected_symbol_review.get("monitor_instruction")),
        "entry_policy_delta": facade._first_dict(payload.get("entry_policy_delta"), selected_symbol_review.get("entry_policy_delta")),
        "commander_actionability": commander_actionability,
        "confidence": selected_symbol_review.get("confidence") if selected_symbol_review.get("confidence") is not None else payload.get("confidence"),
        "exit_pressure": facade._text(payload.get("exit_pressure"), ""),
        "thesis_status": facade._text(payload.get("thesis_status"), ""),
        "next_check_minutes": payload.get("next_check_minutes"),
        "priority_exit_triggers": priority_exit_triggers,
        "monitor_adjustment": monitor_adjustment,
        "reason": facade._first_text("", payload.get("reason"), selected_symbol_review.get("reason"), candidate_watch.get("reason"), refresh_trace.get("summary")),
        "raw_payload_keys": sorted(str(key) for key in payload.keys()),
    }
