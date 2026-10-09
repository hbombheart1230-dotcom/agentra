from __future__ import annotations

from typing import Any, Dict, List, Mapping

from libs.reporting.trade_report_common import clip_text as clip, utc_now_iso
from libs.reporting.trade_reporter_status_text import normalize_reporter_status_human



from .trade_story_assembly_parts.timeline import (
    build_timeline,
    collect_story_warnings,
    compact_canonical_monitor,
)

from .trade_story_assembly_parts.lifecycle_normalization import (
    normalize_trade_lifecycle_for_story_input,
)

from .trade_story_assembly_parts.lifecycle_bundle import (
    build_lifecycle_bundle,
)

from .trade_story_assembly_parts.lifecycle_human import build_lifecycle_human_fallback

from .trade_story_assembly_parts.reasoning_provenance import build_story_reasoning_provenance

from .trade_story_assembly_parts.direct_story import build_direct_story_input

from .trade_story_assembly_parts.lifecycle_evidence import enrich_lifecycle_story_evidence

from .trade_story_assembly_parts.report_seeds import (
    build_report_section_seeds,
)

def build_trade_story_input(
    bundle_out: Dict[str, Any],
    *,
    trade_lifecycle: Dict[str, Any] | None = None,
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    EXECUTION_OUTCOME_NOT_CAPTURED = deps["EXECUTION_OUTCOME_NOT_CAPTURED"]
    LIFECYCLE_CONCLUSION_NOT_CAPTURED = deps["LIFECYCLE_CONCLUSION_NOT_CAPTURED"]
    REPORTER_LINKAGE_NOT_CAPTURED = deps["REPORTER_LINKAGE_NOT_CAPTURED"]
    _attach_news_scanner_contribution = deps["_attach_news_scanner_contribution"]
    _build_monitor_blocker_trace = deps["_build_monitor_blocker_trace"]
    _build_monitor_stop_policy_trace = deps["_build_monitor_stop_policy_trace"]
    _build_scanner_selection_trace = deps["_build_scanner_selection_trace"]
    _build_strategist_evidence_trace = deps["_build_strategist_evidence_trace"]
    _commander_reasoning_flag = deps["_commander_reasoning_flag"]
    _commander_reasoning_source_priority = deps["_commander_reasoning_source_priority"]
    _compact_canonical_monitor = deps["_compact_canonical_monitor"]
    _derive_evidence_provenance = deps["_derive_evidence_provenance"]
    _has_substantive_exit_evidence = deps["_has_substantive_exit_evidence"]
    _hydrate_canonical_agent_artifacts = deps["_hydrate_canonical_agent_artifacts"]
    _is_empty_placeholder = deps["_is_empty_placeholder"]
    _raw_strategist_evidence = deps["_raw_strategist_evidence"]
    _resolve_commander_source_ref = deps["_resolve_commander_source_ref"]
    _resolve_selection_monitor_artifact = deps["_resolve_selection_monitor_artifact"]
    _set_or_replace_placeholder = deps["_set_or_replace_placeholder"]
    _strategist_trace_source = deps["_strategist_trace_source"]
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
        (
            market_context_human, scanner_reason_human, monitor_reason_human,
            guard_reason_human, execution_outcome_human, reporter_status_human,
            operator_conclusion_human,
        ) = build_lifecycle_human_fallback(
            bundle_out, entry=entry, holding=holding, exit_ctx=exit_ctx,
            summary=summary, reporter=reporter, status=status,
            entry_action=entry_action, exit_action=exit_action,
            lifecycle_action=lifecycle_action, symbol=symbol,
            market_context_human=market_context_human,
            scanner_reason_human=scanner_reason_human,
            filters_human=filters_human, deps=deps,
        )
        (
            canonical_strategist, canonical_scanner, canonical_monitor,
            strategy_horizon_feedback, exit_vs_strategy_intent, post_exit_shadow,
            selection_monitor, scanner_selection_trace, raw_strategist_evidence,
            strategist_evidence_trace, news_symbol_linkage,
            monitor_stop_policy_trace, monitor_blocker_trace, scanner_reason_human,
        ) = enrich_lifecycle_story_evidence(
            bundle_out, lifecycle=lifecycle, exit_ctx=exit_ctx,
            canonical_agent_artifacts=canonical_agent_artifacts,
            symbol=symbol, market_context_human=market_context_human,
            scanner_reason_human=scanner_reason_human,
            monitor_reason_human=monitor_reason_human, deps=deps,
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
        reasoning_provenance = build_story_reasoning_provenance(
            bundle_out,
            bundle_reasoning_provenance=bundle_reasoning_provenance,
            canonical_agent_artifacts=canonical_agent_artifacts,
            evidence_provenance=evidence_provenance,
            section_provenance=section_provenance, deps=deps,
        )
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

    return build_direct_story_input(
        bundle_out, story_contract=story_contract,
        section_provenance=section_provenance,
        canonical_agent_artifacts=canonical_agent_artifacts,
        evidence_provenance=evidence_provenance,
        bundle_reasoning_trace=bundle_reasoning_trace,
        bundle_reasoning_provenance=bundle_reasoning_provenance,
        lifecycle=lifecycle, deps=deps,
    )

