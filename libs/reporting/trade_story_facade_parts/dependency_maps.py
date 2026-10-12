"""Story façade dependency maps: call-time name->callable dictionaries handed to the Story assembly/human/evidence Owners.

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _story_assembly_deps_r3_impl(*, facade):
    return {
        "EXECUTION_OUTCOME_NOT_CAPTURED": facade.EXECUTION_OUTCOME_NOT_CAPTURED,
        "LIFECYCLE_CONCLUSION_NOT_CAPTURED": facade.LIFECYCLE_CONCLUSION_NOT_CAPTURED,
        "REPORTER_LINKAGE_NOT_CAPTURED": facade.REPORTER_LINKAGE_NOT_CAPTURED,
        "_attach_news_scanner_contribution": facade._attach_news_scanner_contribution,
        "_build_monitor_blocker_trace": facade._build_monitor_blocker_trace,
        "_build_monitor_stop_policy_trace": facade._build_monitor_stop_policy_trace,
        "_build_scanner_selection_trace": facade._build_scanner_selection_trace,
        "_build_strategist_evidence_trace": facade._build_strategist_evidence_trace,
        "_commander_reasoning_flag": facade._commander_reasoning_flag,
        "_commander_reasoning_source_priority": facade._commander_reasoning_source_priority,
        "_compact_canonical_monitor": facade._compact_canonical_monitor,
        "_derive_evidence_provenance": facade._derive_evidence_provenance,
        "_has_substantive_exit_evidence": facade._has_substantive_exit_evidence,
        "_hydrate_canonical_agent_artifacts": facade._hydrate_canonical_agent_artifacts,
        "_is_empty_placeholder": facade._is_empty_placeholder,
        "_list_text": facade._list_text,
        "_raw_strategist_evidence": facade._raw_strategist_evidence,
        "_resolve_commander_source_ref": facade._resolve_commander_source_ref,
        "_resolve_selection_monitor_artifact": facade._resolve_selection_monitor_artifact,
        "_safe_ref_map": facade._safe_ref_map,
        "_set_or_replace_placeholder": facade._set_or_replace_placeholder,
        "_strategist_trace_source": facade._strategist_trace_source,
        "build_execution_outcome_fallback_from_lifecycle": facade.build_execution_outcome_fallback_from_lifecycle,
        "build_news_symbol_linkage_view": facade.build_news_symbol_linkage_view,
        "build_operator_conclusion_human": facade.build_operator_conclusion_human,
        "build_reasoning_provenance": facade.build_reasoning_provenance,
        "build_reasoning_trace_from_summaries": facade.build_reasoning_trace_from_summaries,
        "build_report_section_provenance_seeds": facade.build_report_section_provenance_seeds,
        "build_report_section_seeds": facade.build_report_section_seeds,
        "build_section_provenance": facade.build_section_provenance,
        "build_strategist_feedback_input_view": facade.build_strategist_feedback_input_view,
        "compute_evidence_completeness": facade.compute_evidence_completeness,
        "enrich_filters_from_evidence": facade.enrich_filters_from_evidence,
        "enrich_scanner_reason_from_evidence": facade.enrich_scanner_reason_from_evidence,
        "execution_outcome_summary_is_placeholder": facade.execution_outcome_summary_is_placeholder,
        "lifecycle_conclusion_summary_is_placeholder": facade.lifecycle_conclusion_summary_is_placeholder,
        "normalize_reasoning_provenance_aliases": facade.normalize_reasoning_provenance_aliases,
        "normalize_reasoning_trace_aliases": facade.normalize_reasoning_trace_aliases,
        "normalize_reporter_status_human": facade.normalize_reporter_status_human,
        "normalize_trade_report_section": facade.normalize_trade_report_section,
        "reanchor_scanner_selection_for_monitor_fallback": facade.reanchor_scanner_selection_for_monitor_fallback,
        "resolve_shared_trade_facts": facade.resolve_shared_trade_facts,
    }


def _human_payload_deps_r3_impl(*, facade):
    return {
        "build_strategist_evidence_trace": facade._build_strategist_evidence_trace,
        "korea_indices_bullet": facade._korea_indices_bullet,
        "list_text": facade._list_text,
        "format_pct": facade.format_pct,
        "safe_float": facade.safe_float,
        "safe_int": facade.safe_int,
        "build_news_scanner_contribution_trace": facade._build_news_scanner_contribution_trace,
        "build_scanner_selection_trace": facade._build_scanner_selection_trace,
        "scanner_chart_fit_payload": facade._scanner_chart_fit_payload,
        "scanner_macro_chart_fit_payload": facade._scanner_macro_chart_fit_payload,
        "clip": facade.clip,
        "confidence_label": facade.confidence_label,
        "normalized_feature_coverage": facade.normalized_feature_coverage,
        "build_monitor_blocker_trace": facade._build_monitor_blocker_trace,
        "build_monitor_stop_policy_trace": facade._build_monitor_stop_policy_trace,
        "merge_missing_values": facade._merge_missing_values,
        "format_exit_label": facade.format_exit_label,
        "format_ratio_pct": facade.format_ratio_pct,
    }


def _evidence_enrichment_deps_r3_impl(*, facade):
    return {
        "normalized_feature_coverage_from_scanner_evidence": facade._normalized_feature_coverage_from_scanner_evidence,
        "scanner_candidate_row_from_evidence": facade._scanner_candidate_row_from_evidence,
        "scanner_chart_fit_from_scanner_evidence": facade._scanner_chart_fit_from_scanner_evidence,
        "scanner_macro_chart_fit_from_scanner_evidence": facade._scanner_macro_chart_fit_from_scanner_evidence,
        "selection_basis_from_scores": facade._selection_basis_from_scores,
        "top_numeric_drivers": facade._top_numeric_drivers,
    }
