from __future__ import annotations

from typing import Any, Dict, List, Mapping

from libs.reporting.trade_report_common import clip_text as clip, utc_now_iso
from libs.reporting.trade_reporter_status_text import normalize_reporter_status_human


def build_timeline(
    *,
    commander: Dict[str, Any],
    market_context_human: Dict[str, Any],
    scanner_reason_human: Dict[str, Any],
    monitor_reason_human: Dict[str, Any],
    guard_reason_human: Dict[str, Any],
    execution_outcome_human: Dict[str, Any],
    reporter_status_human: Dict[str, Any],
    execution: Dict[str, Any],
) -> List[Dict[str, Any]]:
    route_ts = str(commander.get("route_ts") or "")
    execution_ts = str(execution.get("ts") or "")
    return [
        {"step": "strategist_frame", "status": "ok", "ts": route_ts, "summary": market_context_human.get("summary") or ""},
        {"step": "scanner_ranking", "status": "ok", "ts": route_ts, "summary": scanner_reason_human.get("summary") or ""},
        {"step": "monitor_signal", "status": "ok", "ts": execution_ts, "summary": monitor_reason_human.get("summary") or ""},
        {"step": "supervisor_approval", "status": "ok", "ts": execution_ts, "summary": guard_reason_human.get("summary") or ""},
        {"step": "broker_result", "status": "ok", "ts": execution_ts, "summary": execution_outcome_human.get("summary") or ""},
        {"step": "reporter_output", "status": "ok", "ts": utc_now_iso(), "summary": reporter_status_human.get("summary") or ""},
    ]


def collect_story_warnings(
    *,
    story_contract: Dict[str, Any],
    market_context_human: Dict[str, Any],
    filters_human: Dict[str, Any],
    reporter_status_human: Dict[str, Any],
    execution_outcome_human: Dict[str, Any],
) -> List[str]:
    warnings = [str(x or "") for x in list(story_contract.get("warnings") or []) if str(x or "").strip()]
    if market_context_human.get("defensive_mode"):
        warnings.append("Macro or volatility context was defensive for this run.")
    if reporter_status_human.get("status") == "pending":
        warnings.append("Reporter evaluation is pending because same-day run linkage was not available yet.")
    elif reporter_status_human.get("status") == "missing":
        warnings.append("Reporter evaluation is missing because the same-day analysis file was not generated yet.")
    for row in list(filters_human.get("checks") or []):
        if not isinstance(row, dict):
            continue
        status = str(row.get("status") or "").upper()
        if status in {"FAIL", "PARTIAL", "NOT_AVAILABLE"}:
            warnings.append(f"{row.get('name')}: {status} ({row.get('detail') or ''})")
    if execution_outcome_human.get("outcome") == "failed":
        warnings.append("Execution did not complete successfully and needs operator review.")
    deduped: List[str] = []
    for item in warnings:
        text = clip(item, max_len=260)
        if text and text not in deduped:
            deduped.append(text)
    return deduped[:10]


def normalize_trade_lifecycle_for_story_input(
    bundle_out: Dict[str, Any],
    *,
    trade_lifecycle: Dict[str, Any] | None = None,
    existing_story_input: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    lifecycle_src = (
        trade_lifecycle
        if isinstance(trade_lifecycle, dict)
        else bundle_out.get("lifecycle")
        if isinstance(bundle_out.get("lifecycle"), dict)
        else {}
    )
    if not lifecycle_src:
        return {}

    out = dict(lifecycle_src)
    entry_ctx = (
        lifecycle_src.get("entry")
        if isinstance(lifecycle_src.get("entry"), dict)
        else bundle_out.get("entry")
        if isinstance(bundle_out.get("entry"), dict)
        else {}
    )
    holding_ctx = (
        lifecycle_src.get("holding")
        if isinstance(lifecycle_src.get("holding"), dict)
        else lifecycle_src.get("hold")
        if isinstance(lifecycle_src.get("hold"), dict)
        else bundle_out.get("holding")
        if isinstance(bundle_out.get("holding"), dict)
        else bundle_out.get("hold")
        if isinstance(bundle_out.get("hold"), dict)
        else {}
    )
    exit_ctx = (
        lifecycle_src.get("exit")
        if isinstance(lifecycle_src.get("exit"), dict)
        else bundle_out.get("exit")
        if isinstance(bundle_out.get("exit"), dict)
        else {}
    )
    summary_ctx = (
        lifecycle_src.get("summary")
        if isinstance(lifecycle_src.get("summary"), dict)
        else bundle_out.get("trade_outcome")
        if isinstance(bundle_out.get("trade_outcome"), dict)
        else bundle_out.get("summary")
        if isinstance(bundle_out.get("summary"), dict)
        else {}
    )
    reporter_ctx = (
        lifecycle_src.get("reporter")
        if isinstance(lifecycle_src.get("reporter"), dict)
        else {}
    )
    if not reporter_ctx:
        reporter_status_human = normalize_reporter_status_human(
            bundle_out.get("reporter_status_human")
            if isinstance(bundle_out.get("reporter_status_human"), dict)
            else {}
        )
        if reporter_status_human:
            reporter_ctx = {
                "status_human": str(reporter_status_human.get("status") or ""),
                "summary": str(reporter_status_human.get("summary") or ""),
                "grade": str(reporter_status_human.get("grade") or ""),
                "improvement_points": list(reporter_status_human.get("bullets") or []),
            }

    out["entry"] = dict(entry_ctx)
    out["holding"] = dict(holding_ctx)
    out["exit"] = dict(exit_ctx)
    out["summary"] = dict(summary_ctx)
    out["reporter"] = dict(reporter_ctx)
    out["trade_id"] = str(
        out.get("trade_id")
        or bundle_out.get("trade_id")
        or (existing_story_input or {}).get("trade_id")
        or ""
    ).strip()
    out["symbol"] = str(
        out.get("symbol")
        or bundle_out.get("symbol")
        or (entry_ctx.get("symbol") if isinstance(entry_ctx, dict) else "")
        or (exit_ctx.get("symbol") if isinstance(exit_ctx, dict) else "")
        or (existing_story_input or {}).get("symbol")
        or ""
    ).strip()
    out["status"] = str(
        out.get("status")
        or bundle_out.get("trade_lifecycle_status")
        or (existing_story_input or {}).get("status")
        or ""
    ).strip()
    if not out.get("execution_details") and isinstance(bundle_out.get("execution_details"), dict):
        out["execution_details"] = dict(bundle_out.get("execution_details") or {})
    if (
        not out.get("same_day_reporter_linkage")
        and isinstance(bundle_out.get("same_day_reporter_linkage"), dict)
    ):
        out["same_day_reporter_linkage"] = dict(bundle_out.get("same_day_reporter_linkage") or {})
    if (
        not out.get("failure_classification")
        and isinstance(bundle_out.get("failure_classification"), dict)
    ):
        out["failure_classification"] = dict(bundle_out.get("failure_classification") or {})
    return out


def compact_canonical_monitor(canonical_monitor: Dict[str, Any] | None) -> Dict[str, Any]:
    monitor = canonical_monitor if isinstance(canonical_monitor, dict) else {}
    compact = {
        "decision_action": monitor.get("decision_action"),
        "exit_reason": monitor.get("exit_reason"),
        "current_price": monitor.get("current_price"),
        "avg_price": monitor.get("avg_price"),
        "account_pnl_ratio": monitor.get("account_pnl_ratio"),
        "effective_pnl_ratio": monitor.get("effective_pnl_ratio"),
        "price_source": monitor.get("price_source"),
    }
    if any(value not in (None, "", [], {}) for value in compact.values()):
        return compact
    return {}

# P1.5.2 R2-C: lifecycle/report-section/main story assembly owners.


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
    _commander_reasoning_flag = deps["commander_reasoning_flag"]
    _commander_reasoning_source_priority = deps["commander_reasoning_source_priority"]
    _resolve_commander_source_ref = deps["resolve_commander_source_ref"]
    _safe_ref_map = deps["safe_ref_map"]
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



def build_report_section_seeds(
    *,
    market_context_human: Dict[str, Any],
    scanner_reason_human: Dict[str, Any],
    filters_human: Dict[str, Any],
    monitor_reason_human: Dict[str, Any] | None = None,
    execution_outcome_human: Dict[str, Any] | None = None,
    guard_reason_human: Dict[str, Any] | None = None,
    reporter_status_human: Dict[str, Any] | None = None,
    operator_conclusion_human: Dict[str, Any] | None = None,
    deps: Mapping[str, Any],
) -> Dict[str, Dict[str, Any]]:
    _list_text = deps["list_text"]
    normalize_trade_report_section = deps["normalize_trade_report_section"]
    report_like = {
        "market_context_at_entry": dict(market_context_human or {}),
        "why_this_symbol_was_chosen": dict(scanner_reason_human or {}),
        "scanner_filters": dict(filters_human or {}),
        "holding_monitoring_story": dict(monitor_reason_human or {}),
        "exit_decision": dict(execution_outcome_human or {}),
        "execution_quality": dict(execution_outcome_human or {}),
        "guard_approval_result": dict(guard_reason_human or {}),
        "reporter_evaluation": dict(reporter_status_human or {}),
        "final_operator_conclusion": dict(operator_conclusion_human or {}),
    }
    return {
        "market_context_at_entry": normalize_trade_report_section(
            report_like,
            "market_context_at_entry",
            str((market_context_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "strategist_summary": normalize_trade_report_section(
            report_like,
            "strategist_summary",
            str((market_context_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "why_this_symbol_was_chosen": normalize_trade_report_section(
            report_like,
            "why_this_symbol_was_chosen",
            str((scanner_reason_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "entry_decision": normalize_trade_report_section(
            report_like,
            "entry_decision",
            str((scanner_reason_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "holding_monitoring_story": normalize_trade_report_section(
            report_like,
            "holding_monitoring_story",
            str((monitor_reason_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "exit_decision": normalize_trade_report_section(
            report_like,
            "exit_decision",
            str((execution_outcome_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "scanner_filters": normalize_trade_report_section(
            report_like,
            "scanner_filters",
            str((filters_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "execution_quality": normalize_trade_report_section(
            report_like,
            "execution_quality",
            str((execution_outcome_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "guard_approval_result": normalize_trade_report_section(
            report_like,
            "guard_approval_result",
            str((guard_reason_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "reporter_evaluation": normalize_trade_report_section(
            report_like,
            "reporter_evaluation",
            str((reporter_status_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "final_operator_conclusion": normalize_trade_report_section(
            report_like,
            "final_operator_conclusion",
            str((operator_conclusion_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
    }



def build_trade_story_input(
    bundle_out: Dict[str, Any],
    *,
    trade_lifecycle: Dict[str, Any] | None = None,
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    _attach_news_scanner_contribution = deps["attach_news_scanner_contribution"]
    _build_monitor_blocker_trace = deps["build_monitor_blocker_trace"]
    _build_monitor_stop_policy_trace = deps["build_monitor_stop_policy_trace"]
    _build_scanner_selection_trace = deps["build_scanner_selection_trace"]
    _build_strategist_evidence_trace = deps["build_strategist_evidence_trace"]
    _commander_reasoning_flag = deps["commander_reasoning_flag"]
    _commander_reasoning_source_priority = deps["commander_reasoning_source_priority"]
    _compact_canonical_monitor = deps["compact_canonical_monitor"]
    _derive_evidence_provenance = deps["derive_evidence_provenance"]
    _has_substantive_exit_evidence = deps["has_substantive_exit_evidence"]
    _hydrate_canonical_agent_artifacts = deps["hydrate_canonical_agent_artifacts"]
    _is_empty_placeholder = deps["is_empty_placeholder"]
    _raw_strategist_evidence = deps["raw_strategist_evidence"]
    _resolve_commander_source_ref = deps["resolve_commander_source_ref"]
    _resolve_selection_monitor_artifact = deps["resolve_selection_monitor_artifact"]
    _set_or_replace_placeholder = deps["set_or_replace_placeholder"]
    _strategist_trace_source = deps["strategist_trace_source"]
    build_execution_outcome_fallback_from_lifecycle = deps["build_execution_outcome_fallback_from_lifecycle"]
    build_news_symbol_linkage_view = deps["build_news_symbol_linkage_view"]
    build_operator_conclusion_human = deps["build_operator_conclusion_human"]
    build_reasoning_provenance = deps["build_reasoning_provenance"]
    build_reasoning_trace_from_summaries = deps["build_reasoning_trace_from_summaries"]
    build_report_section_provenance_seeds = deps["build_report_section_provenance_seeds"]
    build_report_section_seeds = deps["build_report_section_seeds"]
    build_section_provenance = deps["build_section_provenance"]
    build_strategist_feedback_input_view = deps["build_strategist_feedback_input_view"]
    enrich_filters_from_evidence = deps["enrich_filters_from_evidence"]
    enrich_scanner_reason_from_evidence = deps["enrich_scanner_reason_from_evidence"]
    execution_outcome_summary_is_placeholder = deps["execution_outcome_summary_is_placeholder"]
    lifecycle_conclusion_summary_is_placeholder = deps["lifecycle_conclusion_summary_is_placeholder"]
    normalize_reasoning_provenance_aliases = deps["normalize_reasoning_provenance_aliases"]
    normalize_reasoning_trace_aliases = deps["normalize_reasoning_trace_aliases"]
    normalize_reporter_status_human = deps["normalize_reporter_status_human"]
    reanchor_scanner_selection_for_monitor_fallback = deps["reanchor_scanner_selection_for_monitor_fallback"]
    EXECUTION_OUTCOME_NOT_CAPTURED = deps["EXECUTION_OUTCOME_NOT_CAPTURED"]
    LIFECYCLE_CONCLUSION_NOT_CAPTURED = deps["LIFECYCLE_CONCLUSION_NOT_CAPTURED"]
    REPORTER_LINKAGE_NOT_CAPTURED = deps["REPORTER_LINKAGE_NOT_CAPTURED"]
    story_contract = bundle_out.get("story_contract") if isinstance(bundle_out.get("story_contract"), dict) else {}
    section_provenance = build_section_provenance(bundle_out)
    canonical_agent_artifacts = _hydrate_canonical_agent_artifacts(
        bundle_out,
        dict(bundle_out.get("canonical_agent_artifacts") or {}),
    )
    evidence_provenance = _derive_evidence_provenance(bundle_out)
    # Reporting layers prefer the canonical reasoning snapshot when it is already
    # mirrored into bundle inputs; otherwise they derive a compatible mirror.
    bundle_reasoning_trace = bundle_out.get("reasoning_trace") if isinstance(bundle_out.get("reasoning_trace"), dict) else {}
    bundle_reasoning_provenance = (
        bundle_out.get("reasoning_provenance") if isinstance(bundle_out.get("reasoning_provenance"), dict) else {}
    )
    lifecycle = (
        trade_lifecycle
        if isinstance(trade_lifecycle, dict)
        else bundle_out.get("trade_lifecycle")
        if isinstance(bundle_out.get("trade_lifecycle"), dict)
        else {}
    )
    if lifecycle:
        entry = lifecycle.get("entry") if isinstance(lifecycle.get("entry"), dict) else {}
        holding = lifecycle.get("holding") if isinstance(lifecycle.get("holding"), dict) else {}
        exit_ctx = lifecycle.get("exit") if isinstance(lifecycle.get("exit"), dict) else {}
        summary = lifecycle.get("summary") if isinstance(lifecycle.get("summary"), dict) else {}
        reporter = lifecycle.get("reporter") if isinstance(lifecycle.get("reporter"), dict) else {}
        symbol = str(
            lifecycle.get("symbol")
            or bundle_out.get("symbol")
            or (bundle_out.get("execution") or {}).get("symbol")
            or ""
        )
        authoritative_status = str(bundle_out.get("trade_lifecycle_status") or lifecycle.get("status") or "open").strip() or "open"
        status = authoritative_status
        entry_action = str(entry.get("action") or (bundle_out.get("execution") or {}).get("action") or "BUY")
        exit_action = str(exit_ctx.get("action") or "")
        exit_evidence = _has_substantive_exit_evidence(exit_ctx)
        if status.lower() == "open" and not exit_evidence:
            lifecycle_action = "HOLD" if entry_action else "WAIT"
        else:
            lifecycle_action = exit_action or entry_action or "WAIT"
        market_context_human = dict(bundle_out.get("market_context_human") or {})
        scanner_reason_human = dict(bundle_out.get("scanner_reason_human") or {})
        scanner_evidence = dict(bundle_out.get("scanner_evidence") or (bundle_out.get("evidence") or {}).get("scanner") or {})
        scanner_reason_human = enrich_scanner_reason_from_evidence(scanner_reason_human, scanner_evidence)
        filters_human = dict(bundle_out.get("filters_human") or {})
        filters_human = enrich_filters_from_evidence(
            filters_human,
            scanner_evidence,
            selected_symbol=str(scanner_reason_human.get("selected_symbol") or (entry.get("scanner_context") or {}).get("selected_symbol") or symbol),
            monitor_evidence=dict(bundle_out.get("monitor_evidence") or (bundle_out.get("evidence") or {}).get("monitor") or {}),
            entry_execution_details=dict((entry.get("execution_details") if isinstance(entry.get("execution_details"), dict) else {}) or bundle_out.get("entry_execution_details") or {}),
            exit_execution_details=dict((exit_ctx.get("execution_details") if isinstance(exit_ctx.get("execution_details"), dict) else {}) or bundle_out.get("exit_execution_details") or {}),
        )
        monitor_reason_human = dict(bundle_out.get("monitor_reason_human") or {})
        guard_reason_human = dict(bundle_out.get("guard_reason_human") or {})
        execution_outcome_human = dict(bundle_out.get("execution_outcome_human") or {})
        reporter_status_human = normalize_reporter_status_human(dict(bundle_out.get("reporter_status_human") or {}))
        operator_conclusion_human = dict(bundle_out.get("operator_conclusion_human") or {})
        if not market_context_human:
            market_context_human = {
                "summary": str((entry.get("strategist_context") or {}).get("market_context_summary") or "Market context was not captured."),
                "bullets": [
                    f"Playbook: {str((entry.get('strategist_context') or {}).get('playbook') or 'not_captured')}",
                    "Lifecycle-level entry context was used.",
                ],
            }
        if not scanner_reason_human:
            scanner_reason_human = {
                "summary": str(entry.get("reason_human") or "Scanner selection rationale was not captured."),
                "bullets": [str(entry.get("reason_human") or "no scanner rationale captured")],
            }
        if not monitor_reason_human:
            monitor_reason_human = {
                "summary": (
                    f"Holding updates captured from {len(list(holding.get('run_ids') or []))} monitor runs."
                    if list(holding.get("run_ids") or [])
                    else "Holding monitor updates were not captured."
                ),
                "bullets": [str(x or "") for x in list(holding.get("monitor_updates") or [])[:8]],
            }
        synthesized_execution_outcome = build_execution_outcome_fallback_from_lifecycle(
            entry,
            exit_ctx,
            status=status,
            entry_action=entry_action,
            exit_action=exit_action,
            symbol=symbol,
        )
        if not execution_outcome_human or execution_outcome_summary_is_placeholder(execution_outcome_human.get("summary")):
            execution_outcome_human = dict(synthesized_execution_outcome)
        elif not execution_outcome_human.get("bullets"):
            execution_outcome_human["bullets"] = list(synthesized_execution_outcome.get("bullets") or [])
        if not str(execution_outcome_human.get("summary") or "").strip():
            execution_outcome_human = dict(synthesized_execution_outcome)
        if not str(execution_outcome_human.get("summary") or "").strip():
            execution_outcome_human = {
                "summary": str(summary.get("lifecycle_summary_human") or EXECUTION_OUTCOME_NOT_CAPTURED),
                "bullets": [
                    f"Lifecycle status: {status}",
                    f"Entry action: {entry_action or 'not_captured'}",
                    f"Exit action: {exit_action or 'not_captured'}",
                ],
            }
        if not reporter_status_human:
            reporter_status_human = {
                "status": str(reporter.get("status_human") or "missing"),
                "summary": str(reporter.get("summary") or REPORTER_LINKAGE_NOT_CAPTURED),
                "grade": str(reporter.get("grade") or "N/A"),
                "bullets": [str(x or "") for x in list(reporter.get("improvement_points") or [])[:6]],
            }
        reporter_status_human = normalize_reporter_status_human(reporter_status_human)
        synthesized_operator_conclusion = build_operator_conclusion_human(
            execution={
                "action": lifecycle_action,
                "status": status,
                "symbol": symbol,
            },
            scanner_reason_human=scanner_reason_human,
            filters_human=filters_human,
            monitor_reason_human=monitor_reason_human,
            execution_outcome_human=execution_outcome_human,
            reporter_status_human=reporter_status_human,
        )
        if (
            not operator_conclusion_human
            or lifecycle_conclusion_summary_is_placeholder(operator_conclusion_human.get("summary"))
        ):
            operator_conclusion_human = dict(synthesized_operator_conclusion)
        else:
            if not str(operator_conclusion_human.get("current_action") or "").strip():
                operator_conclusion_human["current_action"] = str(
                    synthesized_operator_conclusion.get("current_action") or ("HOLD" if status == "open" else lifecycle_action)
                )
            if not list(operator_conclusion_human.get("watch_next") or []):
                operator_conclusion_human["watch_next"] = list(synthesized_operator_conclusion.get("watch_next") or [])
            if not list(operator_conclusion_human.get("thesis_invalidation") or []):
                operator_conclusion_human["thesis_invalidation"] = list(
                    synthesized_operator_conclusion.get("thesis_invalidation") or []
                )
        if not str(operator_conclusion_human.get("summary") or "").strip():
            operator_conclusion_human["summary"] = str(summary.get("operator_conclusion_human") or LIFECYCLE_CONCLUSION_NOT_CAPTURED)
        canonical_strategist = (
            canonical_agent_artifacts.get("strategist")
            if isinstance(canonical_agent_artifacts.get("strategist"), dict)
            else bundle_out.get("strategist")
            if isinstance(bundle_out.get("strategist"), dict)
            else {}
        )
        canonical_scanner = (
            canonical_agent_artifacts.get("scanner")
            if isinstance(canonical_agent_artifacts.get("scanner"), dict)
            else bundle_out.get("scanner")
            if isinstance(bundle_out.get("scanner"), dict)
            else {}
        )
        canonical_monitor = (
            canonical_agent_artifacts.get("monitor")
            if isinstance(canonical_agent_artifacts.get("monitor"), dict)
            else bundle_out.get("monitor")
            if isinstance(bundle_out.get("monitor"), dict)
            else {}
        )
        strategy_horizon_feedback = (
            dict(bundle_out.get("strategy_horizon_feedback") or {})
            if isinstance(bundle_out.get("strategy_horizon_feedback"), dict)
            else dict(canonical_strategist.get("strategy_horizon_feedback") or {})
            if isinstance(canonical_strategist.get("strategy_horizon_feedback"), dict)
            else {}
        )
        exit_vs_strategy_intent = (
            dict(bundle_out.get("exit_vs_strategy_intent") or {})
            if isinstance(bundle_out.get("exit_vs_strategy_intent"), dict)
            else dict(canonical_monitor.get("exit_vs_strategy_intent") or {})
            if isinstance(canonical_monitor.get("exit_vs_strategy_intent"), dict)
            else dict((exit_ctx.get("monitor_context") or {}).get("exit_vs_strategy_intent") or {})
            if isinstance(exit_ctx.get("monitor_context"), dict)
            and isinstance((exit_ctx.get("monitor_context") or {}).get("exit_vs_strategy_intent"), dict)
            else {}
        )
        post_exit_shadow = (
            dict(bundle_out.get("post_exit_shadow") or {})
            if isinstance(bundle_out.get("post_exit_shadow"), dict)
            else dict(lifecycle.get("post_exit_shadow") or {})
            if isinstance(lifecycle.get("post_exit_shadow"), dict)
            else dict(exit_ctx.get("post_exit_shadow") or {})
            if isinstance(exit_ctx.get("post_exit_shadow"), dict)
            else {}
        )
        selection_monitor = _resolve_selection_monitor_artifact(bundle_out, canonical_agent_artifacts)
        scanner_selection_trace = _build_scanner_selection_trace(scanner_reason_human, canonical_scanner)
        scanner_reason_human, scanner_selection_trace, selected_symbol = reanchor_scanner_selection_for_monitor_fallback(
            scanner_reason_human=scanner_reason_human,
            scanner_selection_trace=scanner_selection_trace,
            scanner_artifact=canonical_scanner,
            monitor_artifact=selection_monitor,
            trade_symbol=symbol or str((bundle_out.get("execution") or {}).get("symbol") or ""),
        )
        raw_strategist_evidence = _raw_strategist_evidence(bundle_out)
        strategist_evidence_trace = _build_strategist_evidence_trace(
            _strategist_trace_source(canonical_strategist, raw_strategist_evidence),
            selected_symbol=selected_symbol,
            fallback_market_titles=market_context_human.get("market_news_titles"),
            fallback_candidate_titles=market_context_human.get("candidate_news_titles"),
        )
        _attach_news_scanner_contribution(
            scanner_reason_human=scanner_reason_human,
            scanner_selection_trace=scanner_selection_trace,
            canonical_scanner=canonical_scanner,
            canonical_strategist=canonical_strategist,
            selected_symbol=selected_symbol,
        )
        ranked_symbols = [
            str(row.get("symbol") or "").strip()
            for row in list(scanner_selection_trace.get("ranked_candidates") or [])
            if isinstance(row, dict) and str(row.get("symbol") or "").strip()
        ]
        news_symbol_linkage = build_news_symbol_linkage_view(
            strategist_summary=canonical_strategist,
            strategist_raw_input=raw_strategist_evidence,
            strategist_parsed_output=dict((bundle_out.get("strategist_summary") or {}).get("llm_parsed_output") or {}),
            selected_symbol=selected_symbol,
            top_ranked_symbols=ranked_symbols or canonical_scanner.get("top_ranked_symbols") or [],
        )
        monitor_stop_thresholds = (
            ((canonical_monitor.get("thresholds_guards_used") or {}).get("thresholds"))
            if isinstance((canonical_monitor.get("thresholds_guards_used") or {}).get("thresholds"), dict)
            else canonical_monitor.get("thresholds")
            if isinstance(canonical_monitor.get("thresholds"), dict)
            else canonical_monitor.get("threshold_snapshot")
            if isinstance(canonical_monitor.get("threshold_snapshot"), dict)
            else {}
        )
        monitor_stop_policy_trace = _build_monitor_stop_policy_trace(
            canonical_monitor,
            monitor_stop_thresholds,
        )
        monitor_blocker_trace = _build_monitor_blocker_trace(monitor_reason_human)
        market_context_human.setdefault("candidate_hints", strategist_evidence_trace.get("candidate_hints") or [])
        market_context_human.setdefault("market_headlines", strategist_evidence_trace.get("market_headlines") or [])
        selected_symbol_headlines = list(strategist_evidence_trace.get("symbol_headlines") or [])
        market_context_human["symbol_headlines"] = selected_symbol_headlines
        market_context_human["symbol_news_titles"] = selected_symbol_headlines
        market_context_human["candidate_news_titles"] = selected_symbol_headlines
        market_context_human["strategist_evidence_trace"] = dict(strategist_evidence_trace)
        market_context_human["news_symbol_linkage"] = dict(news_symbol_linkage)
        _set_or_replace_placeholder(
            scanner_reason_human,
            "scanner_selection_trace",
            dict(scanner_selection_trace),
        )
        _set_or_replace_placeholder(
            scanner_reason_human,
            "ranked_candidates",
            list(scanner_selection_trace.get("ranked_candidates") or []),
        )
        scanner_reason_human.setdefault("selection_reason", scanner_selection_trace.get("selection_reason"))
        scanner_reason_human.setdefault(
            "selected_symbol_score_drivers",
            dict(scanner_selection_trace.get("selected_symbol_score_drivers") or {}),
        )
        _set_or_replace_placeholder(
            monitor_reason_human,
            "monitor_stop_policy_trace",
            dict(monitor_stop_policy_trace),
        )
        _set_or_replace_placeholder(
            monitor_reason_human,
            "monitor_blocker_trace",
            dict(monitor_blocker_trace),
        )
        report_section_seeds = build_report_section_seeds(
            market_context_human=market_context_human,
            scanner_reason_human=scanner_reason_human,
            filters_human=filters_human,
            monitor_reason_human=monitor_reason_human,
            execution_outcome_human=execution_outcome_human,
            guard_reason_human=guard_reason_human,
            reporter_status_human=reporter_status_human,
            operator_conclusion_human=operator_conclusion_human,
        )
        derived_reasoning_trace = build_reasoning_trace_from_summaries(
            commander_summary=dict(bundle_out.get("commander_summary") or {}),
            strategist_summary=dict(bundle_out.get("strategist_summary") or {}),
            scanner_summary=dict(bundle_out.get("scanner_summary") or {}),
            monitor_summary=dict(bundle_out.get("monitor_summary") or {}),
            report_section_seeds=report_section_seeds,
            market_context_human=market_context_human,
            scanner_reason_human=scanner_reason_human,
            monitor_reason_human=monitor_reason_human,
            operator_conclusion_human=operator_conclusion_human,
        )
        reasoning_trace = normalize_reasoning_trace_aliases(
            {
                "reasoning_trace": bundle_reasoning_trace,
                "latest_reasoning_trace": bundle_out.get("latest_reasoning_trace"),
            },
            fallback=derived_reasoning_trace,
        )
        commander_source_priority = _commander_reasoning_source_priority(bundle_out, dict(bundle_out.get("commander_summary") or {}))
        derived_reasoning_provenance = build_reasoning_provenance(
            commander_context_source="canonical" if canonical_agent_artifacts.get("canonical_commander_json") or canonical_agent_artifacts.get("canonical_commander") else str(evidence_provenance.get("commander") or ""),
            strategist_plan_source=str(
                (section_provenance.get("market_context_human") or {}).get("source")
                or evidence_provenance.get("strategist")
                or ("canonical" if canonical_agent_artifacts.get("canonical_strategist_json") or canonical_agent_artifacts.get("canonical_strategist") else "")
            ),
            scanner_reason_source=str(
                (section_provenance.get("scanner_reason_human") or {}).get("source")
                or evidence_provenance.get("scanner")
                or ("canonical" if canonical_agent_artifacts.get("canonical_scanner_json") or canonical_agent_artifacts.get("canonical_scanner") else "")
            ),
            monitor_reason_source=str(
                (section_provenance.get("monitor_reason_human") or {}).get("source")
                or evidence_provenance.get("monitor")
                or ("canonical" if canonical_agent_artifacts.get("canonical_monitor_json") or canonical_agent_artifacts.get("canonical_monitor") else "")
            ),
            commander_source_ref=_resolve_commander_source_ref(canonical_agent_artifacts, section_provenance),
            strategist_source_ref=str(
                canonical_agent_artifacts.get("canonical_strategist_json")
                or canonical_agent_artifacts.get("canonical_strategist")
                or (section_provenance.get("market_context_human") or {}).get("artifact_path")
                or ""
            ),
            scanner_source_ref=str(
                canonical_agent_artifacts.get("canonical_scanner_json")
                or canonical_agent_artifacts.get("canonical_scanner")
                or (section_provenance.get("scanner_reason_human") or {}).get("artifact_path")
                or ""
            ),
            monitor_source_ref=str(
                canonical_agent_artifacts.get("canonical_monitor_json")
                or canonical_agent_artifacts.get("canonical_monitor")
                or (section_provenance.get("monitor_reason_human") or {}).get("artifact_path")
                or ""
            ),
            shadow_used=_commander_reasoning_flag(bundle_out, dict(bundle_out.get("commander_summary") or {}), "shadow_used"),
            strategist_fallback_used=(
                _commander_reasoning_flag(bundle_out, dict(bundle_out.get("commander_summary") or {}), "strategist_fallback_used")
                or bool((bundle_out.get("strategist_summary") or {}).get("strategist_fallback_used"))
            ),
            source_priority=commander_source_priority,
        )
        reasoning_provenance = normalize_reasoning_provenance_aliases(
            {
                "reasoning_provenance": bundle_reasoning_provenance,
                "latest_reasoning_trace_provenance": bundle_out.get("latest_reasoning_trace_provenance"),
            },
            fallback=derived_reasoning_provenance,
        )
        if isinstance(bundle_out.get("commander"), dict) or isinstance(bundle_out.get("latest_reasoning_trace_provenance"), dict):
            reasoning_provenance["shadow_used"] = _commander_reasoning_flag(
                bundle_out,
                dict(bundle_out.get("commander_summary") or {}),
                "shadow_used",
            )
            reasoning_provenance["strategist_fallback_used"] = (
                _commander_reasoning_flag(
                    bundle_out,
                    dict(bundle_out.get("commander_summary") or {}),
                    "strategist_fallback_used",
                )
                or bool((bundle_out.get("strategist_summary") or {}).get("strategist_fallback_used"))
            )
            if commander_source_priority:
                reasoning_provenance["source_priority"] = list(commander_source_priority)
        section_provenance_out = dict(section_provenance)
        section_provenance_out["report_section_provenance_seeds"] = build_report_section_provenance_seeds(
            section_provenance_out,
        )
        story_artifacts = dict(bundle_out.get("artifacts") or {})
        if isinstance(lifecycle.get("artifacts"), dict):
            for key, value in dict(lifecycle.get("artifacts") or {}).items():
                if key not in story_artifacts or _is_empty_placeholder(story_artifacts.get(key)):
                    story_artifacts[key] = value
        entry_monitor_context = dict(entry.get("monitor_context") or {})
        if isinstance(selection_monitor, dict) and (
            selection_monitor.get("entry_triggered")
            or (isinstance(selection_monitor.get("monitor_focus_context"), dict)
                and selection_monitor.get("monitor_focus_context", {}).get("entry_triggered"))
        ):
            entry_monitor_context = dict(selection_monitor)
            if isinstance(entry.get("monitor_context"), dict) and entry.get("monitor_context"):
                entry_monitor_context.setdefault("entry_artifact_context", dict(entry.get("monitor_context") or {}))
        story_out = {
            "schema_version": "trade_story_input.v2",
            "day": str(bundle_out.get("day") or ""),
            "trade_id": str(lifecycle.get("trade_id") or bundle_out.get("trade_id") or bundle_out.get("story_id") or ""),
            "story_id": str(lifecycle.get("trade_id") or bundle_out.get("trade_id") or bundle_out.get("story_id") or ""),
            "run_id": str(bundle_out.get("run_id") or entry.get("run_id") or ""),
            "symbol": symbol,
            "action": lifecycle_action,
            "status": status,
            "story_type": str(story_contract.get("story_type") or lifecycle.get("story_type") or ""),
            "execution_mode_label": str(story_contract.get("execution_mode_label") or lifecycle.get("execution_mode_label") or ""),
            "entry_summary": {
                "run_id": str(entry.get("run_id") or ""),
                "ts": str(entry.get("ts") or ""),
                "action": entry_action,
                "reason_human": str(entry.get("reason_human") or ""),
                "strategist_context": dict(entry.get("strategist_context") or {}),
                "scanner_context": dict(entry.get("scanner_context") or {}),
                "monitor_context": entry_monitor_context,
                "guard_context": dict(entry.get("guard_context") or {}),
                "execution_context": dict(entry.get("execution_context") or {}),
            },
            "holding_summary": {
                "run_ids": [str(x or "") for x in list(holding.get("run_ids") or []) if str(x or "").strip()],
                "holding_events": [dict(x) for x in list(holding.get("holding_events") or []) if isinstance(x, dict)][:20],
                "posture_history": [dict(x) for x in list(holding.get("posture_history") or []) if isinstance(x, dict)][:20],
                "monitor_updates": [str(x or "") for x in list(holding.get("monitor_updates") or []) if str(x or "").strip()][:20],
                "hold_duration": str(holding.get("hold_duration") or bundle_out.get("hold_duration") or ""),
                "hold_duration_sec": holding.get("hold_duration_sec") if holding.get("hold_duration_sec") is not None else bundle_out.get("hold_duration_sec"),
                "holding_phase_summary": str(holding.get("holding_phase_summary") or bundle_out.get("holding_phase_summary") or ""),
                "hold_events_count": holding.get("hold_events_count") if holding.get("hold_events_count") is not None else bundle_out.get("hold_events_count"),
                "monitor_context_snapshots": [dict(x) for x in list(holding.get("monitor_context_snapshots") or bundle_out.get("monitor_context_snapshots") or []) if isinstance(x, dict)][:20],
                "hold_signal_transitions": [dict(x) for x in list(holding.get("hold_signal_transitions") or bundle_out.get("hold_signal_transitions") or []) if isinstance(x, dict)][:20],
                "pre_exit_context_summary": dict(holding.get("pre_exit_context_summary") or bundle_out.get("pre_exit_context_summary") or {}),
            },
            "exit_summary": {
                "run_id": str(exit_ctx.get("run_id") or ""),
                "ts": str(exit_ctx.get("ts") or ""),
                "action": exit_action,
                "reason_human": str(exit_ctx.get("reason_human") or ""),
                "monitor_context": dict(exit_ctx.get("monitor_context") or {}),
                "guard_context": dict(exit_ctx.get("guard_context") or {}),
                "execution_context": dict(exit_ctx.get("execution_context") or {}),
            },
            "lifecycle_summary": {
                "holding_duration": str(summary.get("holding_duration") or ""),
                "entry_reason_human": str(summary.get("entry_reason_human") or ""),
                "exit_reason_human": str(summary.get("exit_reason_human") or ""),
                "lifecycle_summary_human": str(summary.get("lifecycle_summary_human") or ""),
                "operator_conclusion_human": str(summary.get("operator_conclusion_human") or ""),
            },
            "market_context_human": market_context_human,
            "scanner_reason_human": scanner_reason_human,
            "canonical_monitor": _compact_canonical_monitor(canonical_monitor),
            "strategy_horizon_feedback": dict(strategy_horizon_feedback),
            "strategy_horizon": str(
                bundle_out.get("strategy_horizon")
                or canonical_strategist.get("strategy_horizon")
                or strategy_horizon_feedback.get("strategy_horizon")
                or ""
            ),
            "exit_vs_strategy_intent": dict(exit_vs_strategy_intent),
            "post_exit_shadow": dict(post_exit_shadow),
            "filters_human": filters_human,
            "monitor_reason_human": monitor_reason_human,
            "guard_reason_human": guard_reason_human,
            "execution_outcome_human": execution_outcome_human,
            "reporter_status_human": reporter_status_human,
            "same_day_reporter_linkage": dict(
                lifecycle.get("same_day_reporter_linkage")
                if isinstance(lifecycle.get("same_day_reporter_linkage"), dict)
                else bundle_out.get("same_day_reporter_linkage")
                if isinstance(bundle_out.get("same_day_reporter_linkage"), dict)
                else {}
            ),
            "operator_conclusion_human": operator_conclusion_human,
            "timeline": [dict(x) for x in list(lifecycle.get("timeline") or bundle_out.get("timeline") or []) if isinstance(x, dict)][:40],
            "warnings": [str(x or "") for x in list(bundle_out.get("warnings") or lifecycle.get("warnings") or []) if str(x or "").strip()][:20],
            "improvement_points": [str(x or "") for x in list(reporter.get("improvement_points") or []) if str(x or "").strip()][:12],
            "strategist_evidence": raw_strategist_evidence,
            "strategist_candidate_hints": list(strategist_evidence_trace.get("candidate_hints") or [])[:8],
            "strategist_market_headlines": list(strategist_evidence_trace.get("market_headlines") or [])[:3],
            "strategist_symbol_headlines": list(strategist_evidence_trace.get("symbol_headlines") or [])[:3],
            "strategist_evidence_trace": dict(strategist_evidence_trace),
            "news_symbol_linkage": dict(news_symbol_linkage),
            "scanner_evidence": scanner_evidence,
            "scanner_selection_trace": dict(scanner_selection_trace),
            "monitor_timeline": dict(bundle_out.get("monitor_timeline") or (bundle_out.get("evidence") or {}).get("monitor") or {}),
            "monitor_stop_policy_trace": dict(monitor_stop_policy_trace),
            "monitor_blocker_trace": dict(monitor_blocker_trace),
            "artifacts": story_artifacts,
            "canonical_agent_artifacts": canonical_agent_artifacts,
            "evidence_provenance": evidence_provenance,
            "section_provenance": section_provenance_out,
            "report_section_seeds": dict(report_section_seeds),
            "reasoning_trace": dict(reasoning_trace),
            "reasoning_provenance": dict(reasoning_provenance),
            "evidence_source": "canonical" if any(
                str(source or "").strip().lower() == "canonical"
                for source in evidence_provenance.values()
            ) else "direct_artifact",
            "ai_report_diagnostics": dict(bundle_out.get("ai_report_diagnostics") or {}),
            "execution_details": dict(bundle_out.get("execution_details") or lifecycle.get("execution_details") or {}),
            "entry_execution_details": dict((entry.get("execution_details") if isinstance(entry.get("execution_details"), dict) else {}) or bundle_out.get("entry_execution_details") or {}),
            "exit_execution_details": dict((exit_ctx.get("execution_details") if isinstance(exit_ctx.get("execution_details"), dict) else {}) or bundle_out.get("exit_execution_details") or {}),
            "failure_classification": dict(bundle_out.get("failure_classification") or lifecycle.get("failure_classification") or {}),
        }
        story_out["strategist_feedback_input"] = build_strategist_feedback_input_view(story_out)
        return story_out

    report_section_seeds = build_report_section_seeds(
        market_context_human=dict(bundle_out.get("market_context_human") or {}),
        scanner_reason_human=dict(bundle_out.get("scanner_reason_human") or {}),
        filters_human=dict(bundle_out.get("filters_human") or {}),
        monitor_reason_human=dict(bundle_out.get("monitor_reason_human") or {}),
        execution_outcome_human=dict(bundle_out.get("execution_outcome_human") or {}),
        guard_reason_human=dict(bundle_out.get("guard_reason_human") or {}),
        reporter_status_human=normalize_reporter_status_human(dict(bundle_out.get("reporter_status_human") or {})),
        operator_conclusion_human=dict(bundle_out.get("operator_conclusion_human") or {}),
    )
    derived_reasoning_trace = build_reasoning_trace_from_summaries(
        commander_summary=dict(bundle_out.get("commander_summary") or {}),
        strategist_summary=dict(bundle_out.get("strategist_summary") or {}),
        scanner_summary=dict(bundle_out.get("scanner_summary") or {}),
        monitor_summary=dict(bundle_out.get("monitor_summary") or {}),
        report_section_seeds=report_section_seeds,
        market_context_human=dict(bundle_out.get("market_context_human") or {}),
        scanner_reason_human=dict(bundle_out.get("scanner_reason_human") or {}),
        monitor_reason_human=dict(bundle_out.get("monitor_reason_human") or {}),
        operator_conclusion_human=dict(bundle_out.get("operator_conclusion_human") or {}),
    )
    reasoning_trace = normalize_reasoning_trace_aliases(
        {
            "reasoning_trace": bundle_reasoning_trace,
            "latest_reasoning_trace": bundle_out.get("latest_reasoning_trace"),
        },
        fallback=derived_reasoning_trace,
    )
    commander_source_priority = _commander_reasoning_source_priority(bundle_out, dict(bundle_out.get("commander_summary") or {}))
    derived_reasoning_provenance = build_reasoning_provenance(
        commander_context_source="canonical" if canonical_agent_artifacts.get("canonical_commander_json") or canonical_agent_artifacts.get("canonical_commander") else str(evidence_provenance.get("commander") or ""),
        strategist_plan_source=str(
            (section_provenance.get("market_context_human") or {}).get("source")
            or evidence_provenance.get("strategist")
            or ("canonical" if canonical_agent_artifacts.get("canonical_strategist_json") or canonical_agent_artifacts.get("canonical_strategist") else "")
        ),
        scanner_reason_source=str(
            (section_provenance.get("scanner_reason_human") or {}).get("source")
            or evidence_provenance.get("scanner")
            or ("canonical" if canonical_agent_artifacts.get("canonical_scanner_json") or canonical_agent_artifacts.get("canonical_scanner") else "")
        ),
        monitor_reason_source=str(
            (section_provenance.get("monitor_reason_human") or {}).get("source")
            or evidence_provenance.get("monitor")
            or ("canonical" if canonical_agent_artifacts.get("canonical_monitor_json") or canonical_agent_artifacts.get("canonical_monitor") else "")
        ),
        commander_source_ref=_resolve_commander_source_ref(canonical_agent_artifacts, section_provenance),
        strategist_source_ref=str(
            canonical_agent_artifacts.get("canonical_strategist_json")
            or canonical_agent_artifacts.get("canonical_strategist")
            or (section_provenance.get("market_context_human") or {}).get("artifact_path")
            or ""
        ),
        scanner_source_ref=str(
            canonical_agent_artifacts.get("canonical_scanner_json")
            or canonical_agent_artifacts.get("canonical_scanner")
            or (section_provenance.get("scanner_reason_human") or {}).get("artifact_path")
            or ""
        ),
        monitor_source_ref=str(
            canonical_agent_artifacts.get("canonical_monitor_json")
            or canonical_agent_artifacts.get("canonical_monitor")
            or (section_provenance.get("monitor_reason_human") or {}).get("artifact_path")
            or ""
        ),
        shadow_used=_commander_reasoning_flag(bundle_out, dict(bundle_out.get("commander_summary") or {}), "shadow_used"),
        strategist_fallback_used=(
            _commander_reasoning_flag(bundle_out, dict(bundle_out.get("commander_summary") or {}), "strategist_fallback_used")
            or bool((bundle_out.get("strategist_summary") or {}).get("strategist_fallback_used"))
        ),
        source_priority=commander_source_priority,
    )
    reasoning_provenance = normalize_reasoning_provenance_aliases(
        {
            "reasoning_provenance": bundle_reasoning_provenance,
            "latest_reasoning_trace_provenance": bundle_out.get("latest_reasoning_trace_provenance"),
        },
        fallback=derived_reasoning_provenance,
    )
    if isinstance(bundle_out.get("commander"), dict) or isinstance(bundle_out.get("latest_reasoning_trace_provenance"), dict):
        reasoning_provenance["shadow_used"] = _commander_reasoning_flag(
            bundle_out,
            dict(bundle_out.get("commander_summary") or {}),
            "shadow_used",
        )
        reasoning_provenance["strategist_fallback_used"] = (
            _commander_reasoning_flag(
                bundle_out,
                dict(bundle_out.get("commander_summary") or {}),
                "strategist_fallback_used",
            )
            or bool((bundle_out.get("strategist_summary") or {}).get("strategist_fallback_used"))
        )
        if commander_source_priority:
            reasoning_provenance["source_priority"] = list(commander_source_priority)
    market_context_human = dict(bundle_out.get("market_context_human") or {})
    scanner_reason_human = enrich_scanner_reason_from_evidence(
        dict(bundle_out.get("scanner_reason_human") or {}),
        dict(bundle_out.get("scanner_evidence") or (bundle_out.get("evidence") or {}).get("scanner") or {}),
    )
    filters_human = enrich_filters_from_evidence(
        dict(bundle_out.get("filters_human") or {}),
        dict(bundle_out.get("scanner_evidence") or (bundle_out.get("evidence") or {}).get("scanner") or {}),
        selected_symbol=str(((bundle_out.get("scanner_reason_human") or {}).get("selected_symbol")) or ((bundle_out.get("execution") or {}).get("symbol")) or ""),
        monitor_evidence=dict(bundle_out.get("monitor_evidence") or (bundle_out.get("evidence") or {}).get("monitor") or {}),
        entry_execution_details=dict(bundle_out.get("entry_execution_details") or {}),
        exit_execution_details=dict(bundle_out.get("exit_execution_details") or {}),
    )
    monitor_reason_human = dict(bundle_out.get("monitor_reason_human") or {})
    canonical_strategist = (
        canonical_agent_artifacts.get("strategist")
        if isinstance(canonical_agent_artifacts.get("strategist"), dict)
        else bundle_out.get("strategist")
        if isinstance(bundle_out.get("strategist"), dict)
        else {}
    )
    canonical_scanner = (
        canonical_agent_artifacts.get("scanner")
        if isinstance(canonical_agent_artifacts.get("scanner"), dict)
        else bundle_out.get("scanner")
        if isinstance(bundle_out.get("scanner"), dict)
        else {}
    )
    canonical_monitor = (
        canonical_agent_artifacts.get("monitor")
        if isinstance(canonical_agent_artifacts.get("monitor"), dict)
        else bundle_out.get("monitor")
        if isinstance(bundle_out.get("monitor"), dict)
        else {}
    )
    selection_monitor = _resolve_selection_monitor_artifact(bundle_out, canonical_agent_artifacts)
    scanner_selection_trace = _build_scanner_selection_trace(scanner_reason_human, canonical_scanner)
    scanner_reason_human, scanner_selection_trace, selected_symbol = reanchor_scanner_selection_for_monitor_fallback(
        scanner_reason_human=scanner_reason_human,
        scanner_selection_trace=scanner_selection_trace,
        scanner_artifact=canonical_scanner,
        monitor_artifact=selection_monitor,
        trade_symbol=str((bundle_out.get("execution") or {}).get("symbol") or bundle_out.get("symbol") or ""),
    )
    raw_strategist_evidence = _raw_strategist_evidence(bundle_out)
    strategist_evidence_trace = _build_strategist_evidence_trace(
        _strategist_trace_source(canonical_strategist, raw_strategist_evidence),
        selected_symbol=selected_symbol,
        fallback_market_titles=market_context_human.get("market_news_titles"),
        fallback_candidate_titles=market_context_human.get("candidate_news_titles"),
    )
    _attach_news_scanner_contribution(
        scanner_reason_human=scanner_reason_human,
        scanner_selection_trace=scanner_selection_trace,
        canonical_scanner=canonical_scanner,
        canonical_strategist=canonical_strategist,
        selected_symbol=selected_symbol,
    )
    ranked_symbols = [
        str(row.get("symbol") or "").strip()
        for row in list(scanner_selection_trace.get("ranked_candidates") or [])
        if isinstance(row, dict) and str(row.get("symbol") or "").strip()
    ]
    news_symbol_linkage = build_news_symbol_linkage_view(
        strategist_summary=canonical_strategist,
        strategist_raw_input=raw_strategist_evidence,
        strategist_parsed_output=dict((bundle_out.get("strategist_summary") or {}).get("llm_parsed_output") or {}),
        selected_symbol=selected_symbol,
        top_ranked_symbols=ranked_symbols or canonical_scanner.get("top_ranked_symbols") or [],
    )
    monitor_stop_thresholds = (
        ((canonical_monitor.get("thresholds_guards_used") or {}).get("thresholds"))
        if isinstance((canonical_monitor.get("thresholds_guards_used") or {}).get("thresholds"), dict)
        else canonical_monitor.get("thresholds")
        if isinstance(canonical_monitor.get("thresholds"), dict)
        else canonical_monitor.get("threshold_snapshot")
        if isinstance(canonical_monitor.get("threshold_snapshot"), dict)
        else {}
    )
    monitor_stop_policy_trace = _build_monitor_stop_policy_trace(
        canonical_monitor,
        monitor_stop_thresholds,
    )
    monitor_blocker_trace = _build_monitor_blocker_trace(monitor_reason_human)
    market_context_human.setdefault("candidate_hints", strategist_evidence_trace.get("candidate_hints") or [])
    market_context_human.setdefault("market_headlines", strategist_evidence_trace.get("market_headlines") or [])
    selected_symbol_headlines = list(strategist_evidence_trace.get("symbol_headlines") or [])
    market_context_human["symbol_headlines"] = selected_symbol_headlines
    market_context_human["symbol_news_titles"] = selected_symbol_headlines
    market_context_human["candidate_news_titles"] = selected_symbol_headlines
    market_context_human["strategist_evidence_trace"] = dict(strategist_evidence_trace)
    market_context_human["news_symbol_linkage"] = dict(news_symbol_linkage)
    _set_or_replace_placeholder(
        scanner_reason_human,
        "scanner_selection_trace",
        dict(scanner_selection_trace),
    )
    _set_or_replace_placeholder(
        scanner_reason_human,
        "ranked_candidates",
        list(scanner_selection_trace.get("ranked_candidates") or []),
    )
    scanner_reason_human.setdefault("selection_reason", scanner_selection_trace.get("selection_reason"))
    scanner_reason_human.setdefault(
        "selected_symbol_score_drivers",
        dict(scanner_selection_trace.get("selected_symbol_score_drivers") or {}),
    )
    _set_or_replace_placeholder(
        monitor_reason_human,
        "monitor_stop_policy_trace",
        dict(monitor_stop_policy_trace),
    )
    _set_or_replace_placeholder(
        monitor_reason_human,
        "monitor_blocker_trace",
        dict(monitor_blocker_trace),
    )
    section_provenance_out = dict(section_provenance)
    section_provenance_out["report_section_provenance_seeds"] = build_report_section_provenance_seeds(
        section_provenance_out,
    )
    story_out = {
        "schema_version": "trade_story_input.v1",
        "day": str(bundle_out.get("day") or ""),
        "trade_id": str(bundle_out.get("trade_id") or bundle_out.get("story_id") or ""),
        "story_id": str(bundle_out.get("story_id") or ""),
        "run_id": str(bundle_out.get("run_id") or ""),
        "symbol": str((bundle_out.get("execution") or {}).get("symbol") or ""),
        "action": (
            "HOLD"
            if str(bundle_out.get("trade_lifecycle_status") or "").strip().lower() == "open"
            and not _has_substantive_exit_evidence(
                lifecycle.get("exit") if isinstance(lifecycle.get("exit"), dict) else {}
            )
            else str((bundle_out.get("execution") or {}).get("action") or "")
        ),
        "status": str(bundle_out.get("trade_lifecycle_status") or lifecycle.get("status") or "closed"),
        "story_type": str(story_contract.get("story_type") or ""),
        "execution_mode_label": str(story_contract.get("execution_mode_label") or ""),
        "market_context_human": market_context_human,
        "scanner_reason_human": scanner_reason_human,
        "canonical_monitor": _compact_canonical_monitor(canonical_monitor),
        "filters_human": filters_human,
        "monitor_reason_human": monitor_reason_human,
        "guard_reason_human": dict(bundle_out.get("guard_reason_human") or {}),
        "execution_outcome_human": dict(bundle_out.get("execution_outcome_human") or {}),
        "reporter_status_human": normalize_reporter_status_human(dict(bundle_out.get("reporter_status_human") or {})),
        "operator_conclusion_human": dict(bundle_out.get("operator_conclusion_human") or {}),
        "timeline": list(bundle_out.get("timeline") or []),
        "warnings": list(bundle_out.get("warnings") or []),
        "strategist_evidence": raw_strategist_evidence,
        "strategist_candidate_hints": list(strategist_evidence_trace.get("candidate_hints") or [])[:8],
        "strategist_market_headlines": list(strategist_evidence_trace.get("market_headlines") or [])[:3],
        "strategist_symbol_headlines": list(strategist_evidence_trace.get("symbol_headlines") or [])[:3],
        "strategist_evidence_trace": dict(strategist_evidence_trace),
        "news_symbol_linkage": dict(news_symbol_linkage),
        "scanner_evidence": dict(bundle_out.get("scanner_evidence") or (bundle_out.get("evidence") or {}).get("scanner") or {}),
        "scanner_selection_trace": dict(scanner_selection_trace),
        "monitor_timeline": dict(bundle_out.get("monitor_timeline") or (bundle_out.get("evidence") or {}).get("monitor") or {}),
        "monitor_stop_policy_trace": dict(monitor_stop_policy_trace),
        "monitor_blocker_trace": dict(monitor_blocker_trace),
        "canonical_agent_artifacts": canonical_agent_artifacts,
        "evidence_provenance": evidence_provenance,
        "section_provenance": section_provenance_out,
        "report_section_seeds": dict(report_section_seeds),
        "reasoning_trace": dict(reasoning_trace),
        "reasoning_provenance": dict(reasoning_provenance),
        "evidence_source": "canonical" if any(
            str(source or "").strip().lower() == "canonical"
            for source in evidence_provenance.values()
        ) else "direct_artifact",
        "ai_report_diagnostics": dict(bundle_out.get("ai_report_diagnostics") or {}),
    }
    story_out["strategist_feedback_input"] = build_strategist_feedback_input_view(story_out)
    return story_out


