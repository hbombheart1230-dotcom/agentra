"""AI report façade dependency maps: call-time name->callable dictionaries handed to the AI section/context builders.

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _section_builder_deps_r3_impl(*, facade):
    return {
        "clip": facade._clip,
        "extract_korea_indices_snapshot": facade._extract_korea_indices_snapshot,
        "extract_us_indices_snapshot": facade._extract_us_indices_snapshot,
        "format_korea_indices_sentence": facade._format_korea_indices_sentence,
        "format_pct_points": facade._format_pct_points,
        "market_token_label": facade._market_token_label,
        "num_opt": facade._num_opt,
        "theme_text": facade._theme_text,
        "dedupe_list": facade._dedupe_list,
        "join_headlines": facade._join_headlines,
        "listify": facade._listify,
        "select_symbol_headline": facade._select_symbol_headline,
        "risk_mode_label": facade._risk_mode_label,
        "scanner_bias_text": facade._scanner_bias_text,
        "scanner_source_text": facade._scanner_source_text,
        "strategy_constraint_text": facade._strategy_constraint_text,
        "theme_linkage_label": facade._theme_linkage_label,
        "build_runner_up_comparison": facade._build_runner_up_comparison,
        "build_scanner_driver_summary": facade._build_scanner_driver_summary,
        "fmt_num": facade._fmt_num,
        "scanner_basis_text": facade._scanner_basis_text,
        "scanner_chart_feature_coverage": facade._scanner_chart_feature_coverage,
        "scanner_chart_feature_label": facade._scanner_chart_feature_label,
        "scanner_monitor_fallback_context": facade._scanner_monitor_fallback_context,
        "scanner_ranked_candidates": facade._scanner_ranked_candidates,
        "scanner_selected_row": facade._scanner_selected_row,
        "build_scanner_choice_bullets": facade._build_scanner_choice_bullets,
        "build_scanner_choice_summary": facade._build_scanner_choice_summary,
        "build_scanner_choice_bullets": facade._build_scanner_choice_bullets,
        "build_scanner_choice_summary": facade._build_scanner_choice_summary,
        "entry_gate_score_relation": facade._entry_gate_score_relation,
        "entry_path_label": facade._entry_path_label,
        "entry_reason_label": facade._entry_reason_label,
        "operator_action_label": facade._operator_action_label,
        "as_dict": facade._as_dict,
        "compact_entry_gate_snapshot": facade._compact_entry_gate_snapshot,
        "entry_gate_signature": facade._entry_gate_signature,
        "entry_snapshot_as_post_entry_observation": facade._entry_snapshot_as_post_entry_observation,
        "looks_like_post_entry_monitor_snapshot": facade._looks_like_post_entry_monitor_snapshot,
        "select_entry_decision_detail": facade._select_entry_decision_detail,
        "entry_gate_bits": facade._entry_gate_bits,
        "korean_predicate": facade._korean_predicate,
        "decision_chain_label": facade._decision_chain_label,
        "fmt_pct": facade._fmt_pct,
        "fmt_price": facade._fmt_price,
        "is_low_information_bullet": facade._is_low_information_bullet,
        "operator_axis_label": facade._operator_axis_label,
        "build_reporter_evaluation_from_feedback": facade._build_reporter_evaluation_from_feedback,
        "humanize_duration_text": facade._humanize_duration_text,
        "korean_euro_ro": facade._korean_euro_ro,
        "operatorize_report_text": facade._operatorize_report_text,
        "execution_mode_label": facade._execution_mode_label,
        "exit_reason_label": facade._exit_reason_label,
        "normalize_reporter_text": facade.normalize_reporter_text,
        "build_execution_truth_bullets": facade.build_execution_truth_bullets,
    }


def _context_builder_deps_r3_impl(*, facade):
    return {
        "as_dict": facade._as_dict,
        "clip": facade._clip,
        "compact_candidate_watch_proposal": facade._compact_candidate_watch_proposal,
        "compact_commander_entry_control": facade._compact_commander_entry_control,
        "compact_entry_candidate_cascade": facade._compact_entry_candidate_cascade,
        "enrich_candidate_watch_proposal_from_entry_control": facade._enrich_candidate_watch_proposal_from_entry_control,
        "entry_execution_visibility_summary": facade._entry_execution_visibility_summary,
        "extract_strategy_detail_from_source": facade._extract_strategy_detail_from_source,
        "first_dict_from": facade._first_dict_from,
        "compact_memory_application_trace": facade._compact_memory_application_trace,
        "compact_memory_layer_decisions": facade._compact_memory_layer_decisions,
        "compact_scalar_dict": facade._compact_scalar_dict,
        "compact_strategy_detail_context": facade._compact_strategy_detail_context,
        "compact_strategy_refresh_trace": facade._compact_strategy_refresh_trace,
        "extract_strategist_report_context": facade._extract_strategist_report_context,
        "listify": facade._listify,
    }
