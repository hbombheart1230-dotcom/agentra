"""Read-only operator brief section assembly and projections.

Dependencies resolve through the caller facade at use time to preserve monkeypatch
seams. These projections perform no LLM calls or persistence.
"""
from __future__ import annotations

from typing import Any, Dict, List
from apps.operator_ui import data_access_brief_market_sections as _market
from apps.operator_ui import data_access_brief_presentation_projection_p15 as _presentation


def build_current_snapshot_section(canonical_posture, decision_reason, execution_status_summary, final_action, focus_symbol, guard_status, live_monitor_reason, monitor_reason, next_expected_step, path_label, phase):
    return (
        {
            "summary": decision_reason,
            "phase": phase,
            "path": path_label,
            "final_action": final_action,
            "selected_symbol": focus_symbol,
            "current_focus": focus_symbol,
            "posture": canonical_posture or final_action or "-",
            "monitor_reason": monitor_reason or live_monitor_reason or "-",
            "guard_status": guard_status,
            "execution_status": execution_status_summary,
            "next_expected_step": next_expected_step or "-",
        }
    )

def build_strategist_evidence_section(candidate_hints, canonical_trade, global_score, market_headlines, news_targets, playbook, strategist_evidence_summary, strategist_summary, symbol_headlines, vix_level, *, facade):
    return (
        {
            "summary": strategist_evidence_summary,
            "market_regime": str(canonical_trade.get("market_regime") or strategist_summary.get("market_regime") or "-"),
            "playbook": playbook or "-",
            "global_sentiment": facade._format_float(global_score, 2) if global_score is not None else "-",
            "vix": facade._format_float(vix_level, 2) if vix_level is not None else "-",
            "candidate_hints": facade._clean_brief_list(candidate_hints, limit=6),
            "news_targets": facade._clean_brief_list(news_targets, limit=6),
            "market_headlines": facade._clean_str_list(market_headlines, limit=3, max_len=160),
            "symbol_headlines": facade._clean_str_list(symbol_headlines, limit=3, max_len=160),
        }
    )

def build_monitor_guard_snapshot_section(active_exit_axis, entry_guard_reason, entry_reason_code, execution_status_summary, guard_status, live_monitor_reason, monitor_guard_summary, monitor_reason, stop_policy_summary, supervisor_reason):
    return (
        {
            "summary": monitor_guard_summary,
            "monitor_reason": monitor_reason or live_monitor_reason or "-",
            "entry_reason": entry_reason_code or "-",
            "entry_guard_reason": entry_guard_reason or "-",
            "active_exit_axis": active_exit_axis or "-",
            "stop_policy_summary": stop_policy_summary[:4],
            "guard_status": guard_status,
            "guard_reason": supervisor_reason or "-",
            "execution_status": execution_status_summary,
        }
    )

def build_entry_timing_section(canonical_trade, entry_evaluated, entry_guard_reason, entry_metrics, entry_pattern, entry_reason_code, entry_signal_chain, entry_triggered, final_action):
    return (
        {
            "decision": "BUY" if entry_triggered or final_action == "BUY" else "WAIT",
            "evaluated": entry_evaluated,
            "triggered": entry_triggered,
            "reason_code": entry_reason_code,
            "reason_text": str(canonical_trade.get("entry_reason") or ""),
            "pattern": entry_pattern,
            "signal_chain": entry_signal_chain[:5],
            "metrics": dict(entry_metrics or {}),
            "guard_reason": entry_guard_reason,
        }
    )

def build_position_monitor_reasoning_section(active_exit_axis, avg_price_monitor, canonical_active_exit_axis, canonical_average_price, canonical_current_drawdown, canonical_current_price, canonical_effective_stop, canonical_effective_stop_reason, canonical_exit_triggers, canonical_feature_source, canonical_hold_reasons, canonical_holding_time, canonical_peak_drawdown, canonical_peak_price, canonical_posture, canonical_price_source, canonical_price_source_policy, canonical_stop_loss, canonical_take_profit, canonical_vwap_distance, canonical_watch_axes, current_drawdown_raw, current_price, effective_stop_reason, effective_stop_text, exit_triggers, final_action, hold_reasons, holding_time, monitor_summary, monitor_trace, peak_drawdown_raw, peak_price, stop_loss_text, take_profit_text, vwap_distance_raw, watch_axes, *, facade):
    return (
        {
            "posture": canonical_posture or final_action,
            "holding_time": canonical_holding_time or holding_time,
            "stop_loss": canonical_stop_loss or stop_loss_text,
            "effective_stop": canonical_effective_stop or effective_stop_text,
            "effective_stop_reason": (
                canonical_effective_stop_reason
                or (facade._friendly_exit_reason(effective_stop_reason or "stop_loss") if effective_stop_text != "-" else "-")
            ),
            "take_profit": canonical_take_profit or take_profit_text,
            "current_price": canonical_current_price or (facade._format_float(current_price, 2) if current_price not in (None, "") else "-"),
            "average_price": canonical_average_price or (facade._format_float(avg_price_monitor, 2) if avg_price_monitor not in (None, "") else "-"),
            "peak_price": canonical_peak_price or (facade._format_float(peak_price, 2) if peak_price not in (None, "") else "-"),
            "current_drawdown": canonical_current_drawdown or (facade._format_percent(current_drawdown_raw, 2) if current_drawdown_raw not in (None, "") else "-"),
            "peak_drawdown": canonical_peak_drawdown or (facade._format_percent(peak_drawdown_raw, 2) if peak_drawdown_raw not in (None, "") else "-"),
            "vwap_distance": canonical_vwap_distance or (facade._format_percent(vwap_distance_raw, 2) if vwap_distance_raw not in (None, "") else "-"),
            "price_source": canonical_price_source or str(monitor_trace.get("price_source") or monitor_summary.get("price_source") or "-"),
            "feature_source": canonical_feature_source or str(monitor_trace.get("feature_source") or monitor_summary.get("feature_source") or "-"),
            "price_source_policy": canonical_price_source_policy or str(monitor_trace.get("price_source_policy") or monitor_summary.get("price_source_policy") or ""),
            "active_exit_axis": (facade._friendly_exit_reason(canonical_active_exit_axis) if canonical_active_exit_axis else "") or active_exit_axis,
            "watch_axes": canonical_watch_axes or watch_axes,
            "hold_reasons": canonical_hold_reasons or hold_reasons[:4],
            "exit_triggers": canonical_exit_triggers or exit_triggers[:3],
        }
    )

def build_exit_plan_section(active_exit_axis, canonical_active_exit_axis, canonical_effective_stop, canonical_effective_stop_reason, canonical_exit_triggers, canonical_take_profit, canonical_trade, canonical_watch_axes, effective_stop_reason, effective_stop_text, exit_reason, exit_triggers, final_action, monitor_reason, take_profit_text, watch_axes, *, facade):
    return (
        {
            "current_action": final_action,
            "summary": str(canonical_trade.get("exit_reason") or exit_reason or monitor_reason or ""),
            "effective_stop": canonical_effective_stop or effective_stop_text,
            "effective_stop_reason": (
                canonical_effective_stop_reason
                or (facade._friendly_exit_reason(effective_stop_reason or "stop_loss") if effective_stop_text != "-" else "-")
            ),
            "take_profit": canonical_take_profit or take_profit_text,
            "active_exit_axis": (facade._friendly_exit_reason(canonical_active_exit_axis) if canonical_active_exit_axis else "") or active_exit_axis,
            "exit_triggers": canonical_exit_triggers or exit_triggers[:3],
            "watch_axes": canonical_watch_axes or watch_axes,
        }
    )

def build_ai_trade_report_section(report_available, report_lifecycle_status, report_lifecycle_summary, report_link, report_mode, report_model, report_next_step, report_reason, report_status, report_story_type, report_summary, report_trade_id, *, facade):
    return (
        {
            "status": report_status,
            "status_label": facade._report_status_label(report_status),
            "status_badge_class": facade._report_status_badge_class(report_status),
            "reason": report_reason or "AI report diagnostics were not captured.",
            "next_step": report_next_step or "Continue with Operator Brief while report diagnostics are resolved.",
            "model": report_model or "-",
            "available": report_available,
            "trade_id": report_trade_id,
            "lifecycle_status": report_lifecycle_status or "-",
            "lifecycle_summary": report_lifecycle_summary or "-",
            "story_type": report_story_type,
            "execution_mode_label": report_mode,
            "summary": report_summary or "No per-trade AI report is linked to this run yet.",
            "link": report_link,
        }
    )


def build_operator_brief_sections(detail: Dict[str, Any], *, facade) -> Dict[str, Any]:
    strategist = detail.get("strategist") if isinstance(detail.get("strategist"), dict) else {}
    scanner = detail.get("scanner") if isinstance(detail.get("scanner"), dict) else {}
    monitor = detail.get("monitor") if isinstance(detail.get("monitor"), dict) else {}
    supervisor = detail.get("supervisor") if isinstance(detail.get("supervisor"), dict) else {}
    executor = detail.get("executor") if isinstance(detail.get("executor"), dict) else {}
    reporter = detail.get("reporter") if isinstance(detail.get("reporter"), dict) else {}
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    trade_report_data = trade_report.get("report_data") if isinstance(trade_report.get("report_data"), dict) else {}
    trade_story_input = trade_report_data.get("trade_story_input") if isinstance(trade_report_data.get("trade_story_input"), dict) else {}
    canonical_trade = facade._build_canonical_trade_brief_input(trade_report)
    canonical_monitor_snapshot, execution, feature_coverage, feature_snapshot, live_exit_reason, live_monitor_reason, monitor_summary, monitor_trace, path_label, phase, quote_metrics, scanner_summary, scanner_trace, score_breakdown, selected_candidate, selected_symbol, source_scores, strategist_raw_input, strategist_summary, strategist_trace, supervisor_reason, thresholds, top_candidates, verdict = facade.operator_brief_canonical_facts(canonical_trade=canonical_trade, strategist=strategist, scanner=scanner, monitor=monitor, supervisor=supervisor, executor=executor, detail=detail, facade=facade)
    selected_rank = facade._safe_int(
        canonical_trade.get("selected_rank"),
        next((int(row.get("rank") or 0) for row in top_candidates if str(row.get("symbol") or "") == selected_symbol), 0),
    )
    confidence, execution_action, exit_reason, final_action, monitor_reason, report_lifecycle_status, selected_why, selection_reasons, shared_facts, universe_size = facade.brief_facts_confidence_execution_action(canonical_trade=canonical_trade, scanner_summary=scanner_summary, top_candidates=top_candidates, scanner_trace=scanner_trace, execution=execution, live_monitor_reason=live_monitor_reason, live_exit_reason=live_exit_reason, selected_candidate=selected_candidate, facade=facade)
    for reason in list(canonical_trade.get("why_selected") or [])[:4]:
        cleaned = facade._clean_brief_text(reason)
        if cleaned and cleaned not in selection_reasons:
            selection_reasons.append(cleaned)
    if selected_why and selected_why not in selection_reasons:
        selection_reasons.append(selected_why)
    for bullet in list(canonical_trade.get("selection_bullets") or [])[:4]:
        text = str(bullet or "").strip()
        if text.lower().startswith("chart / feature coverage:"):
            continue
        if text and text not in selection_reasons:
            selection_reasons.append(text)
    if feature_coverage.get("total"):
        selection_reasons.append(
            f"chart feature coverage {feature_coverage.get('present')}/{feature_coverage.get('total')} ({feature_coverage.get('quality') or '-'})"
        )
    if quote_metrics.get("quote_trading_value") is not None:
        selection_reasons.append("acceptable turnover and tradability")
    if strategist_summary.get("playbook"):
        selection_reasons.append(f"aligned with playbook {strategist_summary.get('playbook')}")

    comparison_reasons: List[str] = []
    canonical_runner_ups_lost = [dict(row) for row in list(canonical_trade.get("runner_ups_lost") or []) if isinstance(row, dict)]
    if canonical_runner_ups_lost:
        for row in canonical_runner_ups_lost[:3]:
            symbol = str(row.get("symbol") or "").strip()
            summary = facade._clean_brief_text(row.get("summary") or "; ".join(list(row.get("why_lost") or [])))
            if symbol and summary:
                comparison_reasons.append(f"{symbol} was weaker: {summary}")
    elif len(top_candidates) >= 2:
        for row in top_candidates[1:3]:
            reason = facade._clean_brief_text(row.get("reason"))
            if reason:
                comparison_reasons.append(f"{row.get('symbol')} was weaker: {reason}")
        if not comparison_reasons:
            comparison_reasons.append("other candidates had lower composite rank or weaker feature coverage")
    else:
        comparison_reasons.append("only one ranked candidate was persisted for this run")

    candidate_hints, defensive_mode, detected_themes, global_score, macro_moves, market_headlines, news_summary, news_targets, playbook, symbol_headlines, theme_match, vix_level = facade.brief_market_candidate_hints_defensive_mode(strategist_raw_input=strategist_raw_input, canonical_trade=canonical_trade, strategist_summary=strategist_summary, strategist=strategist, selected_symbol=selected_symbol, strategist_trace=strategist_trace, selected_candidate=selected_candidate, facade=facade)
    if not theme_match and selected_why and detected_themes:
        lowered = selected_why.lower()
        for theme in detected_themes:
            if str(theme).lower() in lowered:
                theme_match = theme
                break
    anomaly_note, anomaly_status, chart_note, chart_status, liquidity_note, liquidity_status, priority_alignment, ranking_basis, risk_note, risk_status, sector_note, sector_status, sentiment_gate_note, sentiment_gate_status, spread_note, spread_status, theme_priority, turnover_note, turnover_status = facade.brief_market_anomaly_note_anomaly_status(detected_themes=detected_themes, theme_match=theme_match, selected_symbol=selected_symbol, feature_snapshot=feature_snapshot, global_score=global_score, quote_metrics=quote_metrics, feature_coverage=feature_coverage, verdict=verdict, selected_candidate=selected_candidate, facade=facade)
    for key in list(score_breakdown.keys())[:6]:
        ranking_basis.append(facade._friendly_feature_name(key))
    if not ranking_basis:
        for key in list(source_scores.keys())[:6]:
            ranking_basis.append(str(key).replace("_", " "))
    if not ranking_basis:
        ranking_basis = ["trading value", "volume", "sector strength", "chart feature coverage"]

    component_scores: List[str] = []
    for key, value in list(score_breakdown.items())[:6]:
        component_scores.append(f"{facade._friendly_feature_name(str(key))}: {facade._format_float(value, 3)}")
    if not component_scores:
        for key, value in list(source_scores.items())[:6]:
            component_scores.append(f"{str(key).replace('_', ' ')}: {facade._format_float(value, 3)}")
    active_exit_axis, avg_price_monitor, canonical_current_price, canonical_holding_time, canonical_posture, chart_interpretation, current_drawdown_raw, current_price, effective_stop_reason, effective_stop_text, holding_time, missing_feature_names, peak_drawdown_raw, peak_price, positive_factors, present_feature_names, scanner_selection_trace, stop_loss, stop_loss_text, take_profit, take_profit_text, vwap_distance_raw, watch_axes, weak_factors = facade.brief_position_exit_axis_evidence(trade_story_input=trade_story_input, canonical_trade=canonical_trade, selected_why=selected_why, quote_metrics=quote_metrics, chart_status=chart_status, sector_status=sector_status, feature_coverage=feature_coverage, feature_snapshot=feature_snapshot, sentiment_gate_status=sentiment_gate_status, thresholds=thresholds, monitor_trace=monitor_trace, monitor_summary=monitor_summary, live_exit_reason=live_exit_reason, live_monitor_reason=live_monitor_reason, exit_reason=exit_reason, monitor_reason=monitor_reason, canonical_monitor_snapshot=canonical_monitor_snapshot, shared_facts=shared_facts, facade=facade)
    canonical_active_exit_axis, canonical_average_price, canonical_current_drawdown, canonical_effective_stop, canonical_effective_stop_reason, canonical_exit_triggers, canonical_feature_source, canonical_hold_reasons, canonical_peak_drawdown, canonical_peak_price, canonical_price_source, canonical_price_source_policy, canonical_stop_loss, canonical_take_profit, canonical_vwap_distance, canonical_watch_axes, entry_evaluated, entry_guard_reason, entry_metrics, entry_pattern, entry_reason_code, entry_signal_chain, entry_triggered, hold_reasons = facade.canonical_monitor_snapshot_view(canonical_monitor_snapshot=canonical_monitor_snapshot, monitor_summary=monitor_summary, monitor_trace=monitor_trace, facade=facade)
    if final_action == "HOLD":
        hold_reasons.append("no explicit exit trigger was hit yet")
        hold_reasons.append(f"monitor reason: {monitor_reason or '-'} / exit reason: {exit_reason or '-'}")
    elif final_action == "WAIT":
        hold_reasons.append("entry is waiting because no active position or execution signal is confirmed")
        hold_reasons.append(f"monitor reason: {monitor_reason or '-'}")
    elif final_action == "BUY":
        hold_reasons.append("scanner selection passed gating and execution was approved")
    elif final_action == "SELL":
        hold_reasons.append("monitor/supervisor flow reached sell execution condition")
    if chart_status in {"PASS", "PARTIAL"}:
        hold_reasons.append(f"chart coverage state: {feature_coverage.get('quality') or '-'}")

    exit_triggers = [
        "stop-loss breach",
        "take-profit hit",
        "monitor quality deterioration",
    ]
    if stop_loss_text != "-" or take_profit_text != "-":
        exit_triggers = [
            f"stop-loss trigger ({stop_loss_text})" if stop_loss_text != "-" else "stop-loss trigger",
            f"take-profit trigger ({take_profit_text})" if take_profit_text != "-" else "take-profit trigger",
            "risk gate failure or abnormal volatility expansion",
        ]

    prefer_runtime_reporter = facade._prefer_runtime_reporter_state(reporter)
    decision_reason, execution_quality, focus_symbol, key_finding, monitor_consistency, report_available, report_lifecycle_status, report_lifecycle_summary, report_link, report_mode, report_model, report_next_step, report_reason, report_status, report_story_type, report_summary, report_trade_id, reporter_reason, reporter_status, run_grade, strategy_alignment, thesis_invalidation, trade_quality, watch_next = facade.brief_decision_report_linkage(prefer_runtime_reporter=prefer_runtime_reporter, reporter=reporter, canonical_trade=canonical_trade, execution_action=execution_action, monitor_reason=monitor_reason, exit_reason=exit_reason, final_action=final_action, selected_rank=selected_rank, universe_size=universe_size, feature_coverage=feature_coverage, selected_symbol=selected_symbol, take_profit_text=take_profit_text, stop_loss_text=stop_loss_text, vix_level=vix_level, detected_themes=detected_themes, trade_report=trade_report, scanner_summary=scanner_summary, facade=facade)
    execution_status_label, next_expected_step, selection_reason_text, stop_policy_summary, strategist_evidence_summary, supervisor_allowed = facade.brief_monitor_execution_status_label_next_expected_ste(verdict=verdict, execution=execution, canonical_trade=canonical_trade, thresholds=thresholds, stop_loss=stop_loss, stop_loss_text=stop_loss_text, canonical_monitor_snapshot=canonical_monitor_snapshot, effective_stop_text=effective_stop_text, take_profit=take_profit, take_profit_text=take_profit_text, canonical_effective_stop_reason=canonical_effective_stop_reason, effective_stop_reason=effective_stop_reason, watch_next=watch_next, final_action=final_action, selected_symbol=selected_symbol, active_exit_axis=active_exit_axis, playbook=playbook, global_score=global_score, vix_level=vix_level, strategist_summary=strategist_summary, selection_reasons=selection_reasons, selected_why=selected_why, facade=facade)
    score_driver_preview = list(component_scores[:4]) or [
        f"{key}={value}"
        for key, value in list((scanner_selection_trace.get("selected_symbol_score_drivers") or {}).items())[:4]
    ]
    top_monitor_blocker = (
        entry_guard_reason
        or monitor_reason
        or live_monitor_reason
        or live_exit_reason
        or "No explicit blocker or trigger was persisted."
    )
    monitor_guard_summary = top_monitor_blocker if final_action == "WAIT" else (live_exit_reason or monitor_reason or top_monitor_blocker)
    guard_status = "approved" if supervisor_allowed else "blocked"
    execution_status_summary = execution_status_label or str(canonical_trade.get("execution_summary") or "not captured")
    operator_takeaway_items = watch_next[:3] or weak_factors[:3] or thesis_invalidation[:3]

    macro_summary, filters_and_gates = _market.build_market_readout(
        macro_moves, canonical_trade, chart_status, chart_note, liquidity_status, liquidity_note, turnover_status, turnover_note, sector_status, sector_note, sentiment_gate_status, sentiment_gate_note, risk_status, risk_note, anomaly_status, anomaly_note, spread_status, spread_note, facade=facade,
    )

    hold_reason_rows = list(canonical_trade.get("monitor_bullets") or [])
    if hold_reason_rows:
        hold_reasons = hold_reason_rows[:4]

    return {
        "executive_decision": _presentation.executive_decision(confidence, decision_reason, final_action, selected_rank, selected_symbol, universe_size),
        "current_snapshot": facade.build_current_snapshot_section(canonical_posture=canonical_posture, decision_reason=decision_reason, execution_status_summary=execution_status_summary, final_action=final_action, focus_symbol=focus_symbol, guard_status=guard_status, live_monitor_reason=live_monitor_reason, monitor_reason=monitor_reason, next_expected_step=next_expected_step, path_label=path_label, phase=phase),
        "strategist_evidence": facade.build_strategist_evidence_section(candidate_hints=candidate_hints, canonical_trade=canonical_trade, global_score=global_score, market_headlines=market_headlines, news_targets=news_targets, playbook=playbook, strategist_evidence_summary=strategist_evidence_summary, strategist_summary=strategist_summary, symbol_headlines=symbol_headlines, vix_level=vix_level, facade=facade),
        "scanner_focus": _presentation.scanner_focus(canonical_trade, focus_symbol, score_driver_preview, selected_rank, selection_reason_text, top_candidates, universe_size),
        "monitor_guard_snapshot": facade.build_monitor_guard_snapshot_section(active_exit_axis=active_exit_axis, entry_guard_reason=entry_guard_reason, entry_reason_code=entry_reason_code, execution_status_summary=execution_status_summary, guard_status=guard_status, live_monitor_reason=live_monitor_reason, monitor_guard_summary=monitor_guard_summary, monitor_reason=monitor_reason, stop_policy_summary=stop_policy_summary, supervisor_reason=supervisor_reason),
        "next_step": _presentation.next_step(next_expected_step, operator_takeaway_items, watch_next),
        "why_symbol_chosen": _presentation.why_symbol_chosen(canonical_trade, comparison_reasons, selected_rank, selected_symbol, selection_reasons, top_candidates, universe_size),
        "entry_timing": facade.build_entry_timing_section(canonical_trade=canonical_trade, entry_evaluated=entry_evaluated, entry_guard_reason=entry_guard_reason, entry_metrics=entry_metrics, entry_pattern=entry_pattern, entry_reason_code=entry_reason_code, entry_signal_chain=entry_signal_chain, entry_triggered=entry_triggered, final_action=final_action),
        "market_context": _presentation.market_context(canonical_trade, defensive_mode, global_score, macro_summary, news_summary, news_targets, strategist_summary, strategist_trace, vix_level, facade=facade),
        "theme_detection": _presentation.theme_detection(detected_themes, priority_alignment, theme_match, theme_priority),
        "filters_and_gates": filters_and_gates,
        "scanner_ranking_explanation": _presentation.scanner_ranking_explanation(canonical_trade, component_scores, positive_factors, ranking_basis, scanner_trace, weak_factors),
        "chart_feature_coverage": _presentation.chart_feature_coverage(chart_interpretation, feature_coverage, missing_feature_names, present_feature_names, facade=facade),
        "position_monitor_reasoning": facade.build_position_monitor_reasoning_section(active_exit_axis=active_exit_axis, avg_price_monitor=avg_price_monitor, canonical_active_exit_axis=canonical_active_exit_axis, canonical_average_price=canonical_average_price, canonical_current_drawdown=canonical_current_drawdown, canonical_current_price=canonical_current_price, canonical_effective_stop=canonical_effective_stop, canonical_effective_stop_reason=canonical_effective_stop_reason, canonical_exit_triggers=canonical_exit_triggers, canonical_feature_source=canonical_feature_source, canonical_hold_reasons=canonical_hold_reasons, canonical_holding_time=canonical_holding_time, canonical_peak_drawdown=canonical_peak_drawdown, canonical_peak_price=canonical_peak_price, canonical_posture=canonical_posture, canonical_price_source=canonical_price_source, canonical_price_source_policy=canonical_price_source_policy, canonical_stop_loss=canonical_stop_loss, canonical_take_profit=canonical_take_profit, canonical_vwap_distance=canonical_vwap_distance, canonical_watch_axes=canonical_watch_axes, current_drawdown_raw=current_drawdown_raw, current_price=current_price, effective_stop_reason=effective_stop_reason, effective_stop_text=effective_stop_text, exit_triggers=exit_triggers, final_action=final_action, hold_reasons=hold_reasons, holding_time=holding_time, monitor_summary=monitor_summary, monitor_trace=monitor_trace, peak_drawdown_raw=peak_drawdown_raw, peak_price=peak_price, stop_loss_text=stop_loss_text, take_profit_text=take_profit_text, vwap_distance_raw=vwap_distance_raw, watch_axes=watch_axes, facade=facade),
        "exit_plan": facade.build_exit_plan_section(active_exit_axis=active_exit_axis, canonical_active_exit_axis=canonical_active_exit_axis, canonical_effective_stop=canonical_effective_stop, canonical_effective_stop_reason=canonical_effective_stop_reason, canonical_exit_triggers=canonical_exit_triggers, canonical_take_profit=canonical_take_profit, canonical_trade=canonical_trade, canonical_watch_axes=canonical_watch_axes, effective_stop_reason=effective_stop_reason, effective_stop_text=effective_stop_text, exit_reason=exit_reason, exit_triggers=exit_triggers, final_action=final_action, monitor_reason=monitor_reason, take_profit_text=take_profit_text, watch_axes=watch_axes, facade=facade),
        "reporter_evaluation": _presentation.reporter_evaluation(execution_quality, key_finding, monitor_consistency, reporter_reason, reporter_status, run_grade, strategy_alignment, trade_quality),
        "ai_trade_report": facade.build_ai_trade_report_section(report_available=report_available, report_lifecycle_status=report_lifecycle_status, report_lifecycle_summary=report_lifecycle_summary, report_link=report_link, report_mode=report_mode, report_model=report_model, report_next_step=report_next_step, report_reason=report_reason, report_status=report_status, report_story_type=report_story_type, report_summary=report_summary, report_trade_id=report_trade_id, facade=facade),
        "operator_conclusion": _presentation.operator_conclusion(final_action, thesis_invalidation, watch_next),
        "risk_alerts": _presentation.risk_alerts(defensive_mode, thesis_invalidation, weak_factors),
    }
