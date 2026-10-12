"""Markdown-clean façade dependency maps: call-time name->callable/constant dictionaries handed to the existing Markdown section Owners.

Bodies moved from the Markdown-clean public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _markdown_diagnostics_deps_r3_impl(*, facade):
    return {
        "action_label": facade._action_label,
        "as_dict": facade._as_dict,
        "authoritative_final_operator_summary": facade._authoritative_final_operator_summary,
        "first_present_impl": facade._first_present_impl,
        "listify": facade._listify,
        "looks_like_symbol_name_impl": facade._looks_like_symbol_name_impl,
        "metadata_value": facade._metadata_value,
        "normalize_evaluation_hold_duration": facade._normalize_evaluation_hold_duration,
        "resolve_trade_symbol_metadata": facade._resolve_trade_symbol_metadata,
        "strip_trailing_blanks": facade._strip_trailing_blanks,
        "summary_decimal": facade._summary_decimal,
        "summary_eval_sentence": facade._summary_eval_sentence,
        "summary_fact_text": facade._summary_fact_text,
        "summary_money": facade._summary_money,
        "summary_problem_label": facade._summary_problem_label,
        "summary_root_cause_label": facade._summary_root_cause_label,
        "translate_text": facade._translate_text,
    }


def _summary_render_deps_r3_impl(*, facade):
    return {
        "RECOVERED_PARTIAL_ENTRY_NOTE": facade._RECOVERED_PARTIAL_ENTRY_NOTE,
        "RECOVERED_PARTIAL_EXIT_NOTE": facade._RECOVERED_PARTIAL_EXIT_NOTE,
        "action_label": facade._action_label,
        "applied_label": facade._applied_label,
        "as_dict": facade._as_dict,
        "authoritative_final_operator_summary": facade._authoritative_final_operator_summary,
        "authoritative_holding_duration_label": facade._authoritative_holding_duration_label,
        "build_post_exit_shadow_summary_lines": facade._build_post_exit_shadow_summary_lines,
        "build_strategy_horizon_lines": facade._build_strategy_horizon_lines,
        "build_summary_exit_trigger_lines": facade._build_summary_exit_trigger_lines,
        "build_trade_cost_analysis": facade._build_trade_cost_analysis,
        "carryover_context": facade._carryover_context,
        "clip": facade._clip,
        "dedupe": facade._dedupe,
        "enrich_exit_signal_snapshot_from_monitor": facade._enrich_exit_signal_snapshot_from_monitor,
        "ensure_sentence": facade._ensure_sentence,
        "entry_confidence_for_operator_summary": facade._entry_confidence_for_operator_summary,
        "entry_reason_line": facade._entry_reason_line,
        "entry_signal_metric_summary_lines": facade._entry_signal_metric_summary_lines,
        "entry_watch_summary_lines": facade._entry_watch_summary_lines,
        "execution_mode_label": facade._execution_mode_label,
        "extract_exit_signal_snapshot": facade._extract_exit_signal_snapshot,
        "fmt_pct": facade._fmt_pct,
        "get_truth_surface": facade._get_truth_surface,
        "is_not_captured": facade._is_not_captured,
        "is_post_entry_gate_text": facade._is_post_entry_gate_text,
        "is_recovered_partial_exit_report": facade._is_recovered_partial_exit_report,
        "korea_index_lines": facade._korea_index_lines,
        "listify": facade._listify,
        "memory_layers_text": facade._memory_layers_text,
        "metadata_value": facade._metadata_value,
        "normalize_entry_confidence_for_operator_summary": facade._normalize_entry_confidence_for_operator_summary,
        "normalize_exit_trigger_label": facade._normalize_exit_trigger_label,
        "num_opt": facade._num_opt,
        "operator_pnl_pct": facade._operator_pnl_pct,
        "playbook_label": facade._playbook_label,
        "pnl_basis_label": facade._pnl_basis_label,
        "render_controlled_lane_report_lines": facade._render_controlled_lane_report_lines,
        "render_quant_tactic_report_lines_impl": facade._render_quant_tactic_report_lines_impl,
        "resolve_entry_signal_snapshot": facade._resolve_entry_signal_snapshot,
        "resolve_market_context": facade._resolve_market_context,
        "resolve_trade_symbol_metadata": facade._resolve_trade_symbol_metadata,
        "risk_mode_label": facade._risk_mode_label,
        "same_day_current_result": facade._same_day_current_result,
        "same_day_summary_from_texts": facade._same_day_summary_from_texts,
        "sample_news_titles": facade._sample_news_titles,
        "sample_news_titles_for_symbol": facade._sample_news_titles_for_symbol,
        "selection_fallback_context": facade._selection_fallback_context,
        "status_label": facade._status_label,
        "story_type_label": facade._story_type_label,
        "strip_trailing_blanks": facade._strip_trailing_blanks,
        "theme_label": facade._theme_label,
        "trade_cost_analysis_lines": facade._trade_cost_analysis_lines,
        "translate_text": facade._translate_text,
        "translated_metadata": facade._translated_metadata,
    }


def _summary_input_deps_r3_impl(*, facade):
    return {
        "RECOVERED_PARTIAL_ENTRY_NOTE": facade._RECOVERED_PARTIAL_ENTRY_NOTE,
        "RECOVERED_PARTIAL_EXIT_NOTE": facade._RECOVERED_PARTIAL_EXIT_NOTE,
        "action_label": facade._action_label,
        "as_dict": facade._as_dict,
        "authoritative_final_operator_summary": facade._authoritative_final_operator_summary,
        "authoritative_hold_duration_seconds": facade._authoritative_hold_duration_seconds,
        "authoritative_holding_duration_label": facade._authoritative_holding_duration_label,
        "build_trade_cost_analysis": facade._build_trade_cost_analysis,
        "carryover_context": facade._carryover_context,
        "clip": facade._clip,
        "compact_post_exit_shadow": facade._compact_post_exit_shadow,
        "enrich_exit_signal_snapshot_from_monitor": facade._enrich_exit_signal_snapshot_from_monitor,
        "entry_confidence_for_operator_summary": facade._entry_confidence_for_operator_summary,
        "entry_reason_line": facade._entry_reason_line,
        "entry_watch_execution_lines": facade._entry_watch_execution_lines,
        "execution_mode_label": facade._execution_mode_label,
        "extract_exit_signal_snapshot": facade._extract_exit_signal_snapshot,
        "fmt_pct": facade._fmt_pct,
        "get_truth_surface": facade._get_truth_surface,
        "is_not_captured": facade._is_not_captured,
        "is_recovered_partial_exit_report": facade._is_recovered_partial_exit_report,
        "listify": facade._listify,
        "metadata_value": facade._metadata_value,
        "normalize_exit_trigger_label": facade._normalize_exit_trigger_label,
        "num_opt": facade._num_opt,
        "operator_pnl_pct": facade._operator_pnl_pct,
        "playbook_label": facade._playbook_label,
        "post_exit_shadow_surface": facade._post_exit_shadow_surface,
        "quant_tactic_surface_impl": facade._quant_tactic_surface_impl,
        "resolve_entry_execution_visibility": facade._resolve_entry_execution_visibility,
        "resolve_entry_signal_snapshot": facade._resolve_entry_signal_snapshot,
        "resolve_market_context": facade._resolve_market_context,
        "resolve_trade_symbol_metadata": facade._resolve_trade_symbol_metadata,
        "risk_mode_label": facade._risk_mode_label,
        "same_day_current_result": facade._same_day_current_result,
        "same_day_summary_from_texts": facade._same_day_summary_from_texts,
        "sample_news_titles": facade._sample_news_titles,
        "sample_news_titles_for_symbol": facade._sample_news_titles_for_symbol,
        "selection_fallback_context": facade._selection_fallback_context,
        "status_label": facade._status_label,
        "story_type_label": facade._story_type_label,
        "strategy_horizon_report_surface": facade._strategy_horizon_report_surface,
        "theme_label": facade._theme_label,
        "translate_text": facade._translate_text,
        "translated_metadata": facade._translated_metadata,
        "truth_source_label": facade._truth_source_label,
    }


def _strategy_memory_deps_r3_impl(*, facade):
    return {
        "action_label": facade._action_label,
        "as_dict": facade._as_dict,
        "badge": facade._badge,
        "carry_risk_label": facade._carry_risk_label,
        "carry_state_label": facade._carry_state_label,
        "dedupe": facade._dedupe,
        "duration_label_seconds": facade._duration_label_seconds,
        "failure_label": facade._failure_label,
        "first_report_path": facade._first_report_path,
        "fmt_pct": facade._fmt_pct,
        "format_kst_date": facade._format_kst_date,
        "format_kst_datetime": facade._format_kst_datetime,
        "humanize_reporter_source_label": facade._humanize_reporter_source_label,
        "listify": facade._listify,
        "memory_layers_text": facade._memory_layers_text,
        "memory_packet_state_line": facade._memory_packet_state_line,
        "memory_status_label": facade._memory_status_label,
        "metadata_value": facade._metadata_value,
        "monitor_delta_interpretation": facade._monitor_delta_interpretation,
        "monitor_phase_line": facade._monitor_phase_line,
        "num_opt": facade._num_opt,
        "parse_report_datetime": facade._parse_report_datetime,
        "playbook_label": facade._playbook_label,
        "policy_phase_line": facade._policy_phase_line,
        "policy_source_label": facade._policy_source_label,
        "reason_summary_line": facade._reason_summary_line,
        "resolve_prompt_proven_surface": facade._resolve_prompt_proven_surface,
        "same_policy_snapshot": facade._same_policy_snapshot,
        "scanner_phase_line": facade._scanner_phase_line,
        "to_kst": facade._to_kst,
    }


def _markdown_entry_visibility_deps_r3_impl(*, facade):
    return {
        "as_dict": facade._as_dict,
        "first_dict": facade._first_dict,
        "metadata_value": facade._metadata_value,
        "resolve_entry_monitor_artifact": facade._resolve_entry_monitor_artifact,
    }


def _markdown_signal_deps_r3_impl(*, facade):
    return {
        "as_dict": facade._as_dict,
        "candidate_cascade_matches_trade": facade._candidate_cascade_matches_trade,
        "candidate_watch_reason_label": facade._candidate_watch_reason_label,
        "dedupe": facade._dedupe,
        "display_candidate_symbol": facade._display_candidate_symbol,
        "first_present_value": facade._first_present_value,
        "fmt_multiple": facade._fmt_multiple,
        "fmt_pct": facade._fmt_pct,
        "fmt_signed_pct": facade._fmt_signed_pct,
        "listify": facade._listify,
        "metadata_value": facade._metadata_value,
        "normalize_exit_trigger_label": facade._normalize_exit_trigger_label,
        "num_opt": facade._num_opt,
        "resolve_entry_execution_visibility": facade._resolve_entry_execution_visibility,
        "summary_money": facade._summary_money,
        "truth_source_label": facade._truth_source_label,
        "watch_scope_label": facade._watch_scope_label,
    }


def _markdown_translation_deps_r3_impl(*, facade):
    return {
        "action_label": facade._action_label,
        "axis_label": facade._axis_label,
        "clip": facade._clip,
        "metadata_value": facade._metadata_value,
        "translate_reason_phrase": facade._translate_reason_phrase,
    }


def _markdown_truth_surface_deps_r3_impl(*, facade):
    return {
        "as_dict": facade._as_dict,
        "authority_label": facade._authority_label,
        "badge": facade._badge,
        "fmt_pct": facade._fmt_pct,
        "fmt_price": facade._fmt_price,
        "get_truth_surface": facade._get_truth_surface,
        "metadata_value": facade._metadata_value,
        "num_opt": facade._num_opt,
        "trade_cost_analysis_lines": facade._trade_cost_analysis_lines,
        "truth_source_label": facade._truth_source_label,
    }


def _markdown_strategy_deps_r3_impl(*, facade):
    return {
        "append_strategy_output_line": facade._append_strategy_output_line,
        "as_dict": facade._as_dict,
        "clip": facade._clip,
        "dedupe": facade._dedupe,
        "entry_watch_execution_lines": facade._entry_watch_execution_lines,
        "is_not_captured": facade._is_not_captured,
        "korea_index_lines": facade._korea_index_lines,
        "listify": facade._listify,
        "looks_corrupted": facade._looks_corrupted,
        "market_context_structured_lines": facade._market_context_structured_lines,
        "market_context_summary_from_raw": facade._market_context_summary_from_raw,
        "memory_layers_text": facade._memory_layers_text,
        "metadata_value": facade._metadata_value,
        "mismatched_symbol_news_bullet": facade._mismatched_symbol_news_bullet,
        "news_linkage_strength_label": facade._news_linkage_strength_label,
        "noun_predicate_was": facade._noun_predicate_was,
        "num_opt": facade._num_opt,
        "playbook_label": facade._playbook_label,
        "policy_token_label": facade._policy_token_label,
        "rank_scope_text": facade._rank_scope_text,
        "resolve_market_context": facade._resolve_market_context,
        "resolve_strategist_output_surface": facade._resolve_strategist_output_surface,
        "risk_mode_label": facade._risk_mode_label,
        "sample_news_titles": facade._sample_news_titles,
        "sample_news_titles_for_symbol": facade._sample_news_titles_for_symbol,
        "section_summary": facade._section_summary,
        "strategy_output_layer_bits": facade._strategy_output_layer_bits,
        "strategy_output_list_text": facade._strategy_output_list_text,
        "strategy_output_text": facade._strategy_output_text,
        "theme_label": facade._theme_label,
        "translate_text": facade._translate_text,
    }
