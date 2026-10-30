"""intraday_trade_reports projections (moved verbatim from intraday_trade_reports).

Module globals and helpers are resolved on ``facade`` (the intraday_trade_reports module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict


def _story_input_quality_score(story_input: Dict[str, Any], *, facade: Any) -> int:
    if not isinstance(story_input, dict) or not story_input:
        return 0

    def _execution_truth_score(details: Any) -> int:
        details_obj = details if isinstance(details, dict) else {}
        local_score = 0
        if str(details_obj.get("order_id") or "").strip():
            local_score += 1
        if details_obj.get("filled_qty") not in (None, ""):
            local_score += 1
        if details_obj.get("filled_price") not in (None, ""):
            local_score += 2
        if str(details_obj.get("broker_truth_source") or "").strip():
            local_score += 2
        if str(details_obj.get("broker_day_truth_source") or "").strip():
            local_score += 2
        if str(details_obj.get("broker_day_match_mode") or "").strip():
            local_score += 1
        if bool(details_obj.get("broker_day_authoritative")):
            local_score += 1
        if details_obj.get("broker_realized_pnl") not in (None, ""):
            local_score += 2
        if details_obj.get("broker_fee") not in (None, "") or details_obj.get("broker_tax") not in (None, ""):
            local_score += 1
        return local_score

    score = 0
    status_lower = str(story_input.get("status") or "").strip().lower()
    trade_symbol = str(story_input.get("symbol") or "").strip()
    if status_lower in {"open", "closed"}:
        score += 2
    if trade_symbol:
        score += 1
    if str(story_input.get("run_id") or "").strip():
        score += 1
    scanner_reason_human = (
        story_input.get("scanner_reason_human")
        if isinstance(story_input.get("scanner_reason_human"), dict)
        else {}
    )
    scanner_trace = (
        story_input.get("scanner_selection_trace")
        if isinstance(story_input.get("scanner_selection_trace"), dict)
        else {}
    )
    selected_symbol = str(
        story_input.get("selected_symbol")
        or scanner_reason_human.get("selected_symbol")
        or scanner_trace.get("selected_symbol")
        or ""
    ).strip()
    if selected_symbol:
        score += 2
    if status_lower == "closed" and trade_symbol and selected_symbol and trade_symbol != selected_symbol:
        score -= 2
    candidate_count = (
        story_input.get("candidate_count")
        if story_input.get("candidate_count") not in (None, "")
        else scanner_reason_human.get("candidate_count")
    )
    if isinstance(candidate_count, (int, float)) and float(candidate_count) > 0:
        score += 1
    if isinstance(scanner_trace.get("ranked_candidates"), list) and len(scanner_trace.get("ranked_candidates") or []) > 0:
        score += 1
    if isinstance(story_input.get("monitor_stop_policy_trace"), dict) and story_input.get("monitor_stop_policy_trace"):
        score += 1
    canonical_monitor = story_input.get("canonical_monitor") if isinstance(story_input.get("canonical_monitor"), dict) else {}
    if canonical_monitor:
        score += 1
    if canonical_monitor.get("current_price") not in (None, ""):
        score += 1
    if canonical_monitor.get("account_pnl_ratio") not in (None, "") or canonical_monitor.get("effective_pnl_ratio") not in (None, ""):
        score += 1
    if str(story_input.get("entry_summary") or "").strip():
        score += 1
    score += _execution_truth_score(story_input.get("execution_details"))
    score += _execution_truth_score(story_input.get("entry_execution_details"))
    score += _execution_truth_score(story_input.get("exit_execution_details"))
    return score


def _truth_surface_differs(existing_story_input: Dict[str, Any], rebuilt_story_input: Dict[str, Any], *, facade: Any) -> bool:
    for key in ("execution_details", "entry_execution_details", "exit_execution_details"):
        if facade._execution_truth_surface(existing_story_input.get(key)) != facade._execution_truth_surface(rebuilt_story_input.get(key)):
            return True
    return False
