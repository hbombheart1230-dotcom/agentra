"""Read-only operator brief input assembly and projections.

Dependencies resolve through the caller facade at use time to preserve monkeypatch
seams. LLM coordination and persistence remain in data_access_core.
"""
from __future__ import annotations

from typing import Any, Dict, List
from apps.operator_ui import data_access_brief_evidence_projection_p15 as _evidence


def brief_input_candidate_hints_market_headlines(monitor, scanner_trace, selected, canonical_trade, strategist_artifact, raw_input, strategist_summary, trade_story_input, *, facade):
    monitor_summary = monitor.get("summary") if isinstance(monitor.get("summary"), dict) else {}
    monitor_trace = monitor.get("decision_trace") if isinstance(monitor.get("decision_trace"), dict) else {}
    monitor_artifact = monitor.get("artifact") if isinstance(monitor.get("artifact"), dict) else {}
    monitor_policy_ref = monitor_trace.get("policy_ref") if isinstance(monitor_trace.get("policy_ref"), dict) else {}
    monitor_timing_assessment = monitor_trace.get("timing_assessment") if isinstance(monitor_trace.get("timing_assessment"), dict) else {}
    monitor_thresholds_used = monitor_trace.get("thresholds_guards_used") if isinstance(monitor_trace.get("thresholds_guards_used"), dict) else {}
    monitor_entry_metrics = monitor_summary.get("entry_metrics") if isinstance(monitor_summary.get("entry_metrics"), dict) else {}
    monitor_entry_thresholds = monitor_summary.get("entry_thresholds") if isinstance(monitor_summary.get("entry_thresholds"), dict) else {}
    selected_symbol = str(
        scanner_trace.get("selected_symbol")
        or selected.get("symbol")
        or canonical_trade.get("symbol")
        or ""
    ).strip()
    news_ranked = (
        strategist_artifact.get("news_evidence_ranked")
        if isinstance(strategist_artifact.get("news_evidence_ranked"), dict)
        else {}
    )
    market_headlines = (
        facade._brief_collect_top_headlines(news_ranked.get("market_news_ranked") or [], limit=3)
        or [str((x or {}).get("title") or "") for x in list(raw_input.get("collected_market_news") or []) if isinstance(x, dict)][:3]
        or list(canonical_trade.get("strategist_market_headlines") or canonical_trade.get("market_news_titles") or [])[:3]
    )
    symbol_headlines = (
        facade._brief_collect_top_headlines(news_ranked.get("candidate_news_ranked") or [], limit=3, symbol=selected_symbol)
        or [str((x or {}).get("title") or "") for x in list(raw_input.get("collected_candidate_news") or []) if isinstance(x, dict)][:3]
        or list(canonical_trade.get("strategist_symbol_headlines") or canonical_trade.get("candidate_news_titles") or [])[:3]
    )
    candidate_hints = list(
        strategist_artifact.get("candidate_symbols_hint")
        or strategist_summary.get("candidate_hints")
        or canonical_trade.get("strategist_candidate_hints")
        or []
    )[:8]
    scanner_selection_trace = (
        trade_story_input.get("scanner_selection_trace")
        if isinstance(trade_story_input.get("scanner_selection_trace"), dict)
        else canonical_trade.get("scanner_selection_trace")
        if isinstance(canonical_trade.get("scanner_selection_trace"), dict)
        else {}
    )
    return (candidate_hints, market_headlines, monitor_artifact, monitor_entry_metrics, monitor_entry_thresholds, monitor_policy_ref, monitor_summary, monitor_thresholds_used, monitor_timing_assessment, monitor_trace, scanner_selection_trace, selected_symbol, symbol_headlines)


def brief_input_scanner_selection_trace(scanner_artifact, selected_symbol, score_breakdown, scanner_trace, selected, canonical_trade, *, facade):
    if True:
        score_breakdown_by_symbol = (
            scanner_artifact.get("score_breakdown_by_symbol")
            if isinstance(scanner_artifact.get("score_breakdown_by_symbol"), dict)
            else {}
        )
        scanner_selection_trace = {
            "ranked_candidates": list(canonical_trade.get("top_candidates") or [])[:5],
            "selected_symbol": selected_symbol,
            "selected_rank": scanner_trace.get("selected_rank") or selected.get("rank"),
            "selection_reason": canonical_trade.get("selection_basis")
            or canonical_trade.get("selection_summary")
            or scanner_trace.get("selection_reason_with_bias")
            or selected.get("why"),
            "selected_symbol_score_drivers": facade._brief_top_numeric_drivers(
                score_breakdown_by_symbol.get(selected_symbol)
                if isinstance(score_breakdown_by_symbol.get(selected_symbol), dict)
                else score_breakdown,
                limit=4,
            ),
        }
    return (scanner_selection_trace,)


def brief_input_canonical_monitor_snapshot_stop_policy_t(monitor_artifact, monitor_summary, monitor_trace, canonical_trade, *, facade):
    merged_monitor_stop_source: facade.Dict[str, facade.Any] = {}
    if isinstance(monitor_artifact, dict):
        merged_monitor_stop_source.update(monitor_artifact)
    if isinstance(monitor_summary, dict):
        merged_monitor_stop_source.update(monitor_summary)
    if isinstance(monitor_trace, dict):
        merged_monitor_stop_source.update(monitor_trace)
    monitor_stop_policy_trace = facade._brief_build_stop_policy_trace(merged_monitor_stop_source)
    canonical_monitor_stop_policy_trace = (
        canonical_trade.get("monitor_stop_policy_trace")
        if isinstance(canonical_trade.get("monitor_stop_policy_trace"), dict)
        else {}
    )
    canonical_monitor_snapshot_stop_policy_trace = (
        (canonical_trade.get("monitor_snapshot") or {}).get("monitor_stop_policy_trace")
        if isinstance((canonical_trade.get("monitor_snapshot") or {}).get("monitor_stop_policy_trace"), dict)
        else {}
    )
    return (canonical_monitor_snapshot_stop_policy_trace, canonical_monitor_stop_policy_trace, monitor_stop_policy_trace)


def brief_input_commander_applied_policy_monitor_applied(commander_artifact, commander_decision, monitor_trace, monitor_policy_ref, *, facade):
    commander_applied_policy = (
        commander_artifact.get("applied_policy")
        if isinstance(commander_artifact.get("applied_policy"), dict)
        else (
            commander_decision.get("applied_policy")
            if isinstance(commander_decision.get("applied_policy"), dict)
            else {}
        )
    )
    monitor_applied_policy = (
        monitor_trace.get("applied_policy")
        if isinstance(monitor_trace.get("applied_policy"), dict)
        else (
            monitor_policy_ref.get("applied_policy")
            if isinstance(monitor_policy_ref.get("applied_policy"), dict)
            else {}
        )
    )
    monitor_received_policy = (
        monitor_trace.get("received_policy")
        if isinstance(monitor_trace.get("received_policy"), dict)
        else (
            monitor_policy_ref.get("received_policy")
            if isinstance(monitor_policy_ref.get("received_policy"), dict)
            else {}
        )
    )
    monitor_effective_policy = (
        monitor_trace.get("effective_policy")
        if isinstance(monitor_trace.get("effective_policy"), dict)
        else (
            monitor_policy_ref.get("effective_policy")
            if isinstance(monitor_policy_ref.get("effective_policy"), dict)
            else monitor_applied_policy
        )
    )
    return (commander_applied_policy, monitor_applied_policy, monitor_effective_policy, monitor_received_policy)


def build_operator_brief_input(detail: Dict[str, Any], *, facade) -> Dict[str, Any]:
    strategist = detail.get("strategist") if isinstance(detail.get("strategist"), dict) else {}
    scanner = detail.get("scanner") if isinstance(detail.get("scanner"), dict) else {}
    monitor = detail.get("monitor") if isinstance(detail.get("monitor"), dict) else {}
    commander = detail.get("commander") if isinstance(detail.get("commander"), dict) else {}
    commander_artifact = commander.get("artifact") if isinstance(commander.get("artifact"), dict) else {}
    commander_decision = commander_artifact.get("commander_decision") if isinstance(commander_artifact.get("commander_decision"), dict) else {}
    reporter = detail.get("reporter") if isinstance(detail.get("reporter"), dict) else {}
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    trade_report_data = trade_report.get("report_data") if isinstance(trade_report.get("report_data"), dict) else {}
    trade_story_input = trade_report_data.get("trade_story_input") if isinstance(trade_report_data.get("trade_story_input"), dict) else {}
    canonical_trade = facade._build_canonical_trade_brief_input(trade_report)
    prefer_runtime_reporter = facade._prefer_runtime_reporter_state(reporter)
    strategist_summary = strategist.get("summary") if isinstance(strategist.get("summary"), dict) else {}
    strategist_artifact = strategist.get("artifact") if isinstance(strategist.get("artifact"), dict) else {}
    strategist_evidence = strategist.get("evidence") if isinstance(strategist.get("evidence"), dict) else {}
    raw_input = strategist_evidence.get("raw_input") if isinstance(strategist_evidence.get("raw_input"), dict) else {}
    scanner_trace = scanner.get("decision_trace") if isinstance(scanner.get("decision_trace"), dict) else {}
    scanner_artifact = scanner.get("artifact") if isinstance(scanner.get("artifact"), dict) else {}
    selected = scanner_trace.get("selected_candidate") if isinstance(scanner_trace.get("selected_candidate"), dict) else {}
    score_breakdown = selected.get("score_breakdown") if isinstance(selected.get("score_breakdown"), dict) else {}
    component_snapshot = selected.get("component_snapshot") if isinstance(selected.get("component_snapshot"), dict) else {}
    feature_snapshot = selected.get("feature_snapshot") if isinstance(selected.get("feature_snapshot"), dict) else {}
    feature_coverage = facade._normalized_feature_coverage(
        scanner.get("feature_coverage") if isinstance(scanner.get("feature_coverage"), dict) else {},
        feature_snapshot,
    )
    chart_status, chart_note = facade._chart_filter_status_and_note(feature_coverage)
    canonical_filter_bullets, canonical_filters_summary, canonical_selection_bullets = _evidence.chart_evidence(
        canonical_trade, feature_coverage, chart_status, chart_note, facade=facade,
    )
    candidate_hints, market_headlines, monitor_artifact, monitor_entry_metrics, monitor_entry_thresholds, monitor_policy_ref, monitor_summary, monitor_thresholds_used, monitor_timing_assessment, monitor_trace, scanner_selection_trace, selected_symbol, symbol_headlines = facade.brief_input_candidate_hints_market_headlines(monitor=monitor, scanner_trace=scanner_trace, selected=selected, canonical_trade=canonical_trade, strategist_artifact=strategist_artifact, raw_input=raw_input, strategist_summary=strategist_summary, trade_story_input=trade_story_input, facade=facade)
    if not scanner_selection_trace:
        scanner_selection_trace = facade.brief_input_scanner_selection_trace(scanner_artifact=scanner_artifact, selected_symbol=selected_symbol, score_breakdown=score_breakdown, scanner_trace=scanner_trace, selected=selected, canonical_trade=canonical_trade, facade=facade)[0]
    canonical_monitor_snapshot_stop_policy_trace, canonical_monitor_stop_policy_trace, monitor_stop_policy_trace = facade.brief_input_canonical_monitor_snapshot_stop_policy_t(monitor_artifact=monitor_artifact, monitor_summary=monitor_summary, monitor_trace=monitor_trace, canonical_trade=canonical_trade, facade=facade)
    monitor_stop_policy_trace = _evidence.merge_stop_evidence(
        monitor_stop_policy_trace, canonical_monitor_stop_policy_trace, canonical_monitor_snapshot_stop_policy_trace,
    )
    commander_applied_policy, monitor_applied_policy, monitor_effective_policy, monitor_received_policy = facade.brief_input_commander_applied_policy_monitor_applied(commander_artifact=commander_artifact, commander_decision=commander_decision, monitor_trace=monitor_trace, monitor_policy_ref=monitor_policy_ref, facade=facade)
    return {
        "run_id": detail.get("run_id"),
        "commander": facade.build_brief_input_commander(commander=commander, commander_applied_policy=commander_applied_policy, commander_artifact=commander_artifact, commander_decision=commander_decision),
        "strategist": facade.build_brief_input_strategist(candidate_hints=candidate_hints, canonical_trade=canonical_trade, market_headlines=market_headlines, raw_input=raw_input, strategist_artifact=strategist_artifact, strategist_summary=strategist_summary, symbol_headlines=symbol_headlines, trade_story_input=trade_story_input, facade=facade),
        "scanner": facade.build_brief_input_scanner(canonical_filter_bullets=canonical_filter_bullets, canonical_filters_summary=canonical_filters_summary, canonical_selection_bullets=canonical_selection_bullets, canonical_trade=canonical_trade, component_snapshot=component_snapshot, feature_coverage=feature_coverage, feature_snapshot=feature_snapshot, scanner=scanner, scanner_selection_trace=scanner_selection_trace, scanner_trace=scanner_trace, score_breakdown=score_breakdown, selected=selected),
        "monitor": facade.build_brief_input_monitor(canonical_trade=canonical_trade, monitor_applied_policy=monitor_applied_policy, monitor_effective_policy=monitor_effective_policy, monitor_entry_metrics=monitor_entry_metrics, monitor_entry_thresholds=monitor_entry_thresholds, monitor_policy_ref=monitor_policy_ref, monitor_received_policy=monitor_received_policy, monitor_stop_policy_trace=monitor_stop_policy_trace, monitor_summary=monitor_summary, monitor_thresholds_used=monitor_thresholds_used, monitor_timing_assessment=monitor_timing_assessment, monitor_trace=monitor_trace, facade=facade),
        "supervisor": {
            **((((detail.get("supervisor") or {}).get("verdict") or {}) if isinstance(detail.get("supervisor"), dict) else {})),
            "canonical_summary": canonical_trade.get("guard_summary"),
        },
        "executor": {
            **((((detail.get("executor") or {}).get("execution") or {}) if isinstance(detail.get("executor"), dict) else {})),
            "canonical_summary": canonical_trade.get("execution_summary"),
            "canonical_bullets": list(canonical_trade.get("execution_bullets") or [])[:6],
        },
        "reporter": {
            "ai_summary": reporter.get("ai_summary") if prefer_runtime_reporter else (canonical_trade.get("reporter_summary") or reporter.get("ai_summary")),
            "ai_run_grade": reporter.get("ai_run_grade") if prefer_runtime_reporter else (canonical_trade.get("reporter_grade") or reporter.get("ai_run_grade")),
            "found": reporter.get("found"),
            "status": canonical_trade.get("reporter_status"),
            "reason": reporter.get("reason"),
        },
        "trade_report": facade.build_brief_input_trade_report(trade_report=trade_report),
        "shared_facts": dict(canonical_trade.get("shared_facts") or {}),
        "canonical_trade": canonical_trade,
    }
