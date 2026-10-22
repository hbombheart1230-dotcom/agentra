"""Read-only operator brief input assembly and projections.

Dependencies resolve through the caller facade at use time to preserve monkeypatch
seams. LLM coordination and persistence remain in data_access_core.
"""
from __future__ import annotations

from typing import Any, Dict, List


from apps.operator_ui.data_access_brief_source_truth_p15 import (
    brief_input_candidate_hints_market_headlines as brief_input_candidate_hints_market_headlines,
    brief_input_scanner_selection_trace as brief_input_scanner_selection_trace,
    brief_input_canonical_monitor_snapshot_stop_policy_t as brief_input_canonical_monitor_snapshot_stop_policy_t,
    brief_input_commander_applied_policy_monitor_applied as brief_input_commander_applied_policy_monitor_applied,
)


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
    canonical_filter_bullets = list(canonical_trade.get("filter_bullets") or [])[:8]
    canonical_selection_bullets = list(canonical_trade.get("selection_bullets") or [])[:6]
    if facade._safe_int(feature_coverage.get("total"), 0) > 0:
        updated_bullets: List[str] = []
        replaced_chart_bullet = False
        for bullet in canonical_filter_bullets:
            text = str(bullet or "").strip()
            if text.lower().startswith("chart completeness filter:"):
                updated_bullets.append(f"chart completeness filter: {chart_status} - {chart_note}")
                replaced_chart_bullet = True
            else:
                updated_bullets.append(text)
        if not replaced_chart_bullet:
            updated_bullets.append(f"chart completeness filter: {chart_status} - {chart_note}")
        canonical_filter_bullets = updated_bullets[:8]
        canonical_filters_summary = (
            f"Scanner and guard checks used normalized chart coverage with {feature_coverage.get('present')}/{feature_coverage.get('total')} captured features."
        )
        updated_selection_bullets: List[str] = []
        replaced_selection_chart_bullet = False
        for bullet in canonical_selection_bullets:
            text = str(bullet or "").strip()
            if text.lower().startswith("chart / feature coverage:"):
                updated_selection_bullets.append(
                    f"Chart / feature coverage: {feature_coverage.get('present')}/{feature_coverage.get('total')}"
                )
                replaced_selection_chart_bullet = True
            else:
                updated_selection_bullets.append(text)
        if not replaced_selection_chart_bullet:
            updated_selection_bullets.append(
                f"Chart / feature coverage: {feature_coverage.get('present')}/{feature_coverage.get('total')}"
            )
        canonical_selection_bullets = updated_selection_bullets[:6]
    else:
        canonical_filters_summary = canonical_trade.get("filters_summary")
    candidate_hints, market_headlines, monitor_artifact, monitor_entry_metrics, monitor_entry_thresholds, monitor_policy_ref, monitor_summary, monitor_thresholds_used, monitor_timing_assessment, monitor_trace, scanner_selection_trace, selected_symbol, symbol_headlines = facade.brief_input_candidate_hints_market_headlines(monitor=monitor, scanner_trace=scanner_trace, selected=selected, canonical_trade=canonical_trade, strategist_artifact=strategist_artifact, raw_input=raw_input, strategist_summary=strategist_summary, trade_story_input=trade_story_input, facade=facade)
    if not scanner_selection_trace:
        scanner_selection_trace = facade.brief_input_scanner_selection_trace(scanner_artifact=scanner_artifact, selected_symbol=selected_symbol, score_breakdown=score_breakdown, scanner_trace=scanner_trace, selected=selected, canonical_trade=canonical_trade, facade=facade)[0]
    canonical_monitor_snapshot_stop_policy_trace, canonical_monitor_stop_policy_trace, monitor_stop_policy_trace = facade.brief_input_canonical_monitor_snapshot_stop_policy_t(monitor_artifact=monitor_artifact, monitor_summary=monitor_summary, monitor_trace=monitor_trace, canonical_trade=canonical_trade, facade=facade)
    if not any(value not in (None, "", []) for value in monitor_stop_policy_trace.values()):
        monitor_stop_policy_trace = dict(canonical_monitor_stop_policy_trace or {})
    elif canonical_monitor_stop_policy_trace:
        for key, value in canonical_monitor_stop_policy_trace.items():
            if monitor_stop_policy_trace.get(key) in (None, "", []):
                monitor_stop_policy_trace[key] = value
    if canonical_monitor_snapshot_stop_policy_trace:
        for key, value in canonical_monitor_snapshot_stop_policy_trace.items():
            if monitor_stop_policy_trace.get(key) in (None, "", []):
                monitor_stop_policy_trace[key] = value
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
