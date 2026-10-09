from __future__ import annotations

from typing import Any, Dict, List, Mapping

from libs.reporting.trade_report_common import clip_text as clip, utc_now_iso
from libs.reporting.trade_reporter_status_text import normalize_reporter_status_human


def build_lifecycle_bundle(
    *,
    day: str,
    trade_id: str,
    run_id: str,
    symbol: str,
    lifecycle: Dict[str, Any],
    strategist_summary: Dict[str, Any],
    scanner_summary: Dict[str, Any],
    monitor_summary: Dict[str, Any],
    commander_summary: Dict[str, Any],
    story_input: Dict[str, Any],
    diagnostics: Dict[str, Any],
    canonical_refs: Dict[str, Any],
    llm_refs: Dict[str, Any],
    artifact_links: Dict[str, Any],
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    _commander_reasoning_flag = deps["_commander_reasoning_flag"]
    _commander_reasoning_source_priority = deps["_commander_reasoning_source_priority"]
    _resolve_commander_source_ref = deps["_resolve_commander_source_ref"]
    _safe_ref_map = deps["_safe_ref_map"]
    build_reasoning_provenance = deps["build_reasoning_provenance"]
    build_reasoning_trace_from_summaries = deps["build_reasoning_trace_from_summaries"]
    compute_evidence_completeness = deps["compute_evidence_completeness"]
    normalize_reasoning_provenance_aliases = deps["normalize_reasoning_provenance_aliases"]
    normalize_reasoning_trace_aliases = deps["normalize_reasoning_trace_aliases"]
    resolve_shared_trade_facts = deps["resolve_shared_trade_facts"]
    lifecycle_obj = dict(lifecycle or {})
    entry_obj = dict(lifecycle_obj.get("entry") or {})
    holding_obj = dict(lifecycle_obj.get("holding") or {})
    exit_obj = dict(lifecycle_obj.get("exit") or {})
    summary_obj = dict(lifecycle_obj.get("summary") or {})
    hold_events = [
        dict(row)
        for row in list(holding_obj.get("holding_events") or [])
        if isinstance(row, dict)
    ]
    if not hold_events and isinstance(holding_obj.get("posture_history"), list):
        hold_events = [
            dict(row)
            for row in list(holding_obj.get("posture_history") or [])
            if isinstance(row, dict)
        ]
    completeness = compute_evidence_completeness(story_input)
    shared_facts = resolve_shared_trade_facts(story_input)
    exit_reason = (
        str(summary_obj.get("exit_reason_human") or "")
        or str((exit_obj.get("monitor_context") or {}).get("exit_reason") or "")
        or str(exit_obj.get("reason_human") or "")
    )
    entry_reason = (
        str(summary_obj.get("entry_reason_human") or "")
        or str(entry_obj.get("reason_human") or "")
        or str((story_input.get("entry_reason_human") or {}).get("summary") or "")
    )
    monitor_snapshot = dict(story_input.get("monitor_reason_human") or {})
    same_day_reporter_linkage = dict(story_input.get("same_day_reporter_linkage") or lifecycle_obj.get("same_day_reporter_linkage") or {})
    execution_details = dict(story_input.get("execution_details") or lifecycle_obj.get("execution_details") or {})
    entry_execution_details = dict(
        story_input.get("entry_execution_details")
        or (entry_obj.get("execution_details") if isinstance(entry_obj.get("execution_details"), dict) else {})
        or {}
    )
    exit_execution_details = dict(
        story_input.get("exit_execution_details")
        or (exit_obj.get("execution_details") if isinstance(exit_obj.get("execution_details"), dict) else {})
        or {}
    )
    failure_classification = dict(story_input.get("failure_classification") or lifecycle_obj.get("failure_classification") or {})
    derived_reasoning_trace = build_reasoning_trace_from_summaries(
        commander_summary=dict(commander_summary or {}),
        strategist_summary=dict(strategist_summary or {}),
        scanner_summary=dict(scanner_summary or {}),
        monitor_summary=dict(monitor_summary or {}),
        market_context_human=dict(story_input.get("market_context_human") or {}),
        scanner_reason_human=dict(story_input.get("scanner_reason_human") or {}),
        monitor_reason_human=dict(story_input.get("monitor_reason_human") or {}),
        operator_conclusion_human=dict(story_input.get("operator_conclusion_human") or {}),
    )
    reasoning_trace = normalize_reasoning_trace_aliases(story_input, fallback=derived_reasoning_trace)
    section_provenance = dict(story_input.get("section_provenance") or {})
    evidence_provenance = dict(story_input.get("evidence_provenance") or {})
    refs = _safe_ref_map({**dict(canonical_refs or {}), **dict(artifact_links or {})})
    commander_source_priority = _commander_reasoning_source_priority(story_input, dict(commander_summary or {}))
    derived_reasoning_provenance = build_reasoning_provenance(
        commander_context_source="canonical" if refs.get("canonical_commander_json") or refs.get("canonical_commander") else str(evidence_provenance.get("commander") or ""),
        strategist_plan_source=str(
            (section_provenance.get("market_context_human") or {}).get("source")
            or evidence_provenance.get("strategist")
            or ("canonical" if refs.get("canonical_strategist_json") or refs.get("canonical_strategist") else "")
        ),
        scanner_reason_source=str(
            (section_provenance.get("scanner_reason_human") or {}).get("source")
            or evidence_provenance.get("scanner")
            or ("canonical" if refs.get("canonical_scanner_json") or refs.get("canonical_scanner") else "")
        ),
        monitor_reason_source=str(
            (section_provenance.get("monitor_reason_human") or {}).get("source")
            or evidence_provenance.get("monitor")
            or ("canonical" if refs.get("canonical_monitor_json") or refs.get("canonical_monitor") else "")
        ),
        commander_source_ref=_resolve_commander_source_ref(refs, section_provenance),
        strategist_source_ref=str(
            refs.get("canonical_strategist_json")
            or refs.get("canonical_strategist")
            or (section_provenance.get("market_context_human") or {}).get("artifact_path")
            or ""
        ),
        scanner_source_ref=str(
            refs.get("canonical_scanner_json")
            or refs.get("canonical_scanner")
            or (section_provenance.get("scanner_reason_human") or {}).get("artifact_path")
            or ""
        ),
        monitor_source_ref=str(
            refs.get("canonical_monitor_json")
            or refs.get("canonical_monitor")
            or (section_provenance.get("monitor_reason_human") or {}).get("artifact_path")
            or ""
        ),
        shadow_used=_commander_reasoning_flag(story_input, dict(commander_summary or {}), "shadow_used"),
        strategist_fallback_used=(
            _commander_reasoning_flag(story_input, dict(commander_summary or {}), "strategist_fallback_used")
            or bool((strategist_summary or {}).get("strategist_fallback_used"))
        ),
        source_priority=commander_source_priority,
    )
    reasoning_provenance = normalize_reasoning_provenance_aliases(
        story_input,
        fallback=derived_reasoning_provenance,
    )
    top_level_entry = dict(entry_obj)
    if not top_level_entry:
        top_level_entry = {"available": False}
    top_level_entry.setdefault("available", bool(entry_obj))
    if entry_reason:
        top_level_entry.setdefault("summary", str(entry_reason))
    if symbol:
        top_level_entry.setdefault("symbol", str(symbol))

    top_level_exit = dict(exit_obj)
    if not top_level_exit:
        top_level_exit = {"available": False}
    top_level_exit.setdefault("available", bool(exit_obj))
    if exit_reason:
        top_level_exit.setdefault("summary", str(exit_reason))
    if symbol:
        top_level_exit.setdefault("symbol", str(symbol))
    return {
        "schema_version": "lifecycle_bundle.v1",
        "day": str(day or ""),
        "trade_id": str(trade_id or ""),
        "symbol": str(symbol or ""),
        "run_id": str(run_id or ""),
        "entry": top_level_entry,
        "exit": top_level_exit,
        "shared_facts": dict(shared_facts or {}),
        "news_symbol_linkage": dict(story_input.get("news_symbol_linkage") or {}),
        "strategist_feedback_input": dict(story_input.get("strategist_feedback_input") or {}),
        "lifecycle": {
            "entry": entry_obj,
            "hold": hold_events,
            "exit": exit_obj,
        },
        "strategist_summary": dict(strategist_summary or {}),
        "scanner_summary": dict(scanner_summary or {}),
        "monitor_summary": dict(monitor_summary or {}),
        "commander_summary": dict(commander_summary or {}),
        "reasoning_trace": reasoning_trace,
        "reasoning_provenance": reasoning_provenance,
        "trade_outcome": {
            "pnl": monitor_snapshot.get("pnl"),
            "return_pct": monitor_snapshot.get("current_drawdown"),
            "holding_time": str(summary_obj.get("holding_duration") or ""),
            "exit_reason": str(exit_reason or ""),
        },
        "hold_duration": str(
            summary_obj.get("holding_duration")
            or holding_obj.get("hold_duration")
            or story_input.get("hold_duration")
            or ""
        ),
        "hold_duration_sec": (
            holding_obj.get("hold_duration_sec")
            if holding_obj.get("hold_duration_sec") is not None
            else story_input.get("hold_duration_sec")
        ),
        "holding_phase_summary": str(
            holding_obj.get("holding_phase_summary")
            or story_input.get("holding_phase_summary")
            or ""
        ),
        "hold_events_count": (
            holding_obj.get("hold_events_count")
            if holding_obj.get("hold_events_count") is not None
            else story_input.get("hold_events_count")
            if story_input.get("hold_events_count") is not None
            else len(hold_events)
        ),
        "monitor_context_snapshots": [
            dict(row)
            for row in list(
                holding_obj.get("monitor_context_snapshots")
                or story_input.get("monitor_context_snapshots")
                or []
            )
            if isinstance(row, dict)
        ][:20],
        "hold_signal_transitions": [
            dict(row)
            for row in list(
                holding_obj.get("hold_signal_transitions")
                or story_input.get("hold_signal_transitions")
                or []
            )
            if isinstance(row, dict)
        ][:20],
        "pre_exit_context_summary": dict(
            holding_obj.get("pre_exit_context_summary")
            or story_input.get("pre_exit_context_summary")
            or {}
        ),
        "same_day_reporter_linkage": same_day_reporter_linkage,
        "execution_details": execution_details,
        "entry_execution_details": entry_execution_details,
        "exit_execution_details": exit_execution_details,
        "failure_classification": failure_classification,
        "evidence_summary": {
            "completeness_score": float(completeness.get("completeness_score") or 0.0),
            "missing_sections": [str(x or "") for x in list(completeness.get("missing_sections") or []) if str(x or "").strip()],
        },
        "llm_summary": {
            "strategist_llm_status": str(diagnostics.get("strategist_llm_status") or "skipped"),
            "brief_llm_status": str(diagnostics.get("llm_brief_status") or "skipped"),
            "ai_report_status": str(diagnostics.get("ai_trade_report_status") or "skipped"),
        },
        "refs": {
            "canonical_refs": _safe_ref_map(canonical_refs),
            "llm_refs": _safe_ref_map(llm_refs),
            "artifact_links": _safe_ref_map(artifact_links),
        },
        "missing": {
            "entry_missing": not bool(entry_obj),
            "hold_missing": not bool(hold_events),
            "exit_missing": not bool(exit_obj),
        },
    }



