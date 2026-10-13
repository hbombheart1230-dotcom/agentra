"""Deterministic fallback summary and status projection.

Second Pass (P1.5) intra-function extraction from `libs/reporting/trade_report_ai_deterministic.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def fb_summary_effective_scanner_selection_trace_exit_s(story_input, _listify, _as_dict, entry_summary, scanner_reason, shared_selection_trace, *, facade):
    holding_summary = story_input.get("holding_summary") if isinstance(story_input.get("holding_summary"), dict) else {}
    exit_summary = story_input.get("exit_summary") if isinstance(story_input.get("exit_summary"), dict) else {}
    lifecycle_summary = story_input.get("lifecycle_summary") if isinstance(story_input.get("lifecycle_summary"), dict) else {}
    warnings = _listify(story_input.get("warnings"), max_items=10, max_len=260)
    improvement_points = _listify(story_input.get("improvement_points"), max_items=10, max_len=260)
    scanner_selection_trace = _as_dict(story_input.get("scanner_selection_trace"))
    entry_scanner_context = (
        entry_summary.get("scanner_context")
        if isinstance(entry_summary.get("scanner_context"), dict)
        else {}
    )
    news_scanner_contribution = _as_dict(
        scanner_reason.get("news_scanner_contribution")
        or scanner_selection_trace.get("news_scanner_contribution")
        or entry_scanner_context.get("news_scanner_contribution")
    )
    effective_scanner_selection_trace = _as_dict(scanner_selection_trace) or _as_dict(shared_selection_trace)
    return (effective_scanner_selection_trace, exit_summary, holding_summary, improvement_points, lifecycle_summary, news_scanner_contribution, scanner_selection_trace, warnings)


def fb_summary_confidence_executive_reason(_clip, shared_seed, story_input, operator_conclusion, lifecycle_summary, _lifecycle_summary_conflicts_with_status, execution_outcome, scanner_reason, _build_scanner_choice_summary, market_context, _is_low_information_bullet, has_runtime_scanner_reason, scanner_selection_trace, why_symbol_seed, _build_market_context_summary, has_runtime_market_context, market_context_seed, _build_strategist_summary_section, *, facade):
    symbol = _clip(shared_seed.get("symbol"), max_len=32) or _clip(story_input.get("symbol"), max_len=32) or "unknown"
    trade_id = _clip(shared_seed.get("trade_id"), max_len=120) or _clip(story_input.get("trade_id") or story_input.get("story_id"), max_len=120)
    status_text = _clip(shared_seed.get("lifecycle_status"), max_len=32) or _clip(story_input.get("status"), max_len=32) or "closed"
    operator_summary_text = _clip(operator_conclusion.get("summary"), max_len=600)
    lifecycle_summary_text = _clip(lifecycle_summary.get("lifecycle_summary_human"), max_len=600)
    if _lifecycle_summary_conflicts_with_status(lifecycle_summary_text, status_text):
        lifecycle_summary_text = ""
    execution_outcome_text = _clip(execution_outcome.get("summary"), max_len=600)
    scanner_summary_text = _clip(scanner_reason.get("summary"), max_len=600)
    if status_text.strip().lower() == "closed" and lifecycle_summary_text:
        executive_reason = lifecycle_summary_text
    else:
        executive_reason = (
            operator_summary_text
            or lifecycle_summary_text
            or execution_outcome_text
            or scanner_summary_text
            or "The decision path was recorded, but the operator-facing summary is limited."
        )
    confidence = _clip(scanner_reason.get("confidence_label"), max_len=24) or _clip(scanner_reason.get("confidence"), max_len=24)
    scanner_choice_summary = _build_scanner_choice_summary(scanner_reason, market_context)
    if (
        (not has_runtime_scanner_reason and not scanner_selection_trace)
        or not scanner_choice_summary
        or _is_low_information_bullet(scanner_choice_summary)
    ) and str(why_symbol_seed.get("summary") or "").strip():
        scanner_choice_summary = _clip(why_symbol_seed.get("summary"), max_len=600)
    if str(shared_seed.get("scanner_evidence_status") or "").strip() == "unavailable":
        scanner_choice_summary = "Scanner evidence unavailable for this trade. Selection rationale is reported conservatively."
    market_context_summary = _build_market_context_summary(market_context, scanner_reason=scanner_reason)
    if (
        not has_runtime_market_context
        or not market_context_summary
        or _is_low_information_bullet(market_context_summary)
    ) and str(market_context_seed.get("summary") or "").strip():
        market_context_summary = _clip(market_context_seed.get("summary"), max_len=600)
    if str(shared_seed.get("strategist_evidence_status") or "").strip() == "unavailable" and (
        not market_context_summary or _is_low_information_bullet(market_context_summary)
    ):
        market_context_summary = "Strategist evidence unavailable for this trade. Market context is shown as limited."
    strategist_summary = _build_strategist_summary_section(market_context, scanner_reason)
    strategist_summary_summary = _clip(strategist_summary.get("summary"), max_len=600)
    return (confidence, executive_reason, lifecycle_summary_text, market_context_summary, scanner_choice_summary, status_text, strategist_summary, strategist_summary_summary, symbol, trade_id)
