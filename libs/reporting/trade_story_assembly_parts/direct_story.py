from __future__ import annotations

from typing import Any, Dict, Mapping

from .reasoning_provenance import build_story_reasoning_provenance


def build_direct_story_input(
    bundle_out: Dict[str, Any], *, story_contract: Dict[str, Any],
    section_provenance: Dict[str, Any], canonical_agent_artifacts: Dict[str, Any],
    evidence_provenance: Dict[str, Any], bundle_reasoning_trace: Dict[str, Any],
    bundle_reasoning_provenance: Dict[str, Any], lifecycle: Dict[str, Any],
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    """Assemble the direct-artifact v1 story when no trade lifecycle is provided."""
    _attach_news_scanner_contribution = deps["_attach_news_scanner_contribution"]
    _build_monitor_blocker_trace = deps["_build_monitor_blocker_trace"]
    _build_monitor_stop_policy_trace = deps["_build_monitor_stop_policy_trace"]
    _build_scanner_selection_trace = deps["_build_scanner_selection_trace"]
    _build_strategist_evidence_trace = deps["_build_strategist_evidence_trace"]
    _compact_canonical_monitor = deps["_compact_canonical_monitor"]
    _has_substantive_exit_evidence = deps["_has_substantive_exit_evidence"]
    _raw_strategist_evidence = deps["_raw_strategist_evidence"]
    _resolve_selection_monitor_artifact = deps["_resolve_selection_monitor_artifact"]
    _set_or_replace_placeholder = deps["_set_or_replace_placeholder"]
    _strategist_trace_source = deps["_strategist_trace_source"]
    build_news_symbol_linkage_view = deps["build_news_symbol_linkage_view"]
    build_reasoning_trace_from_summaries = deps["build_reasoning_trace_from_summaries"]
    build_report_section_provenance_seeds = deps["build_report_section_provenance_seeds"]
    build_report_section_seeds = deps["build_report_section_seeds"]
    build_strategist_feedback_input_view = deps["build_strategist_feedback_input_view"]
    enrich_filters_from_evidence = deps["enrich_filters_from_evidence"]
    enrich_scanner_reason_from_evidence = deps["enrich_scanner_reason_from_evidence"]
    normalize_reasoning_trace_aliases = deps["normalize_reasoning_trace_aliases"]
    normalize_reporter_status_human = deps["normalize_reporter_status_human"]
    reanchor_scanner_selection_for_monitor_fallback = deps["reanchor_scanner_selection_for_monitor_fallback"]
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
    reasoning_provenance = build_story_reasoning_provenance(
        bundle_out,
        bundle_reasoning_provenance=bundle_reasoning_provenance,
        canonical_agent_artifacts=canonical_agent_artifacts,
        evidence_provenance=evidence_provenance,
        section_provenance=section_provenance, deps=deps,
    )
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
