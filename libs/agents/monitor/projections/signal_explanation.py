"""Intraday entry-signal reason/explanation views (read-only).

Second Pass (P1.5) intra-function extraction from `libs/runtime/intraday_monitor_signals.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def signal_explain_effect_free_block_3479(entry_condition_path, grouped_logic_trace, scoring_settings, score_breakdown, policy_aware_gating, chart_structure_decision_hint, chart_human_context, human_chart_entry_setup, human_chart_detail_context, human_chart_buy_guard, entry_quality_score, entry_quality_tier, entry_quality_path, entry_hard_gate_passed, entry_hard_gate_blockers, entry_quality_vs_gate_summary, breakout_score, etf_deviation_entry_score, *, facade):
    grouped_logic_trace["triggered_path"] = entry_condition_path
    grouped_logic_trace["scoring_mode"] = str(scoring_settings.get("scoring_mode") or "disabled")
    grouped_logic_trace["score_passed"] = bool(sum(facade._to_float(v) for v in score_breakdown.values()) >= float(scoring_settings.get("entry_threshold") or 3.0))
    grouped_logic_trace["signal_evidence_ready"] = True
    grouped_logic_trace["policy_aware_gating_available"] = bool(policy_aware_gating.get("available"))
    grouped_logic_trace["policy_aware_gating_applied"] = bool(policy_aware_gating.get("applied"))
    grouped_logic_trace["policy_aware_gating_hints"] = list(policy_aware_gating.get("applied_hints") or [])
    grouped_logic_trace["policy_aware_gating_blocked_by_required"] = list(policy_aware_gating.get("blocked_by_required") or [])
    grouped_logic_trace["entry_tuning_flags"] = list(policy_aware_gating.get("entry_tuning_flags") or [])
    grouped_logic_trace["reclaim_readiness_tuned"] = bool(policy_aware_gating.get("reclaim_readiness_tuned"))
    grouped_logic_trace["reclaim_tuning_version"] = str(policy_aware_gating.get("reclaim_tuning_version") or "")
    grouped_logic_trace["reclaim_tuning_scope"] = str(policy_aware_gating.get("reclaim_tuning_scope") or "")
    grouped_logic_trace["chart_structure_decision_hint_available"] = bool(chart_structure_decision_hint.get("available"))
    grouped_logic_trace["chart_structure_decision_hint_applied"] = bool(chart_structure_decision_hint.get("applied"))
    grouped_logic_trace["chart_structure_decision_hint_mode"] = str(chart_structure_decision_hint.get("mode") or "none")
    grouped_logic_trace["chart_structure_decision_hint_blocking_features"] = list(chart_structure_decision_hint.get("blocking_features") or [])
    grouped_logic_trace["human_chart_entry_score"] = chart_human_context.get("entry_chart_score")
    grouped_logic_trace["human_chart_exit_risk_score"] = chart_human_context.get("exit_risk_score")
    grouped_logic_trace["human_chart_entry_setup_available"] = bool(human_chart_entry_setup.get("available"))
    grouped_logic_trace["human_chart_entry_setup_applied"] = bool(human_chart_entry_setup.get("applied"))
    grouped_logic_trace["human_chart_setup_quality"] = str(human_chart_entry_setup.get("setup_quality") or "none")
    grouped_logic_trace["human_chart_setup_label"] = str(human_chart_entry_setup.get("setup_label") or "")
    grouped_logic_trace["human_chart_setup_score"] = human_chart_entry_setup.get("setup_score")
    grouped_logic_trace["human_candle_quality_score"] = human_chart_detail_context.get("candle_quality_score")
    grouped_logic_trace["human_vwap_reference_quality_score"] = human_chart_detail_context.get("vwap_reference_quality_score")
    grouped_logic_trace["human_reward_room_score"] = human_chart_detail_context.get("reward_room_score")
    grouped_logic_trace["human_multi_window_structure_score"] = human_chart_detail_context.get("multi_window_structure_score")
    grouped_logic_trace["human_chart_detail_observed"] = dict(human_chart_detail_context.get("observed") or {})
    grouped_logic_trace["human_chart_entry_setup_matched_features"] = list(
        human_chart_entry_setup.get("matched_features") or []
    )
    grouped_logic_trace["human_chart_entry_setup_blocking_features"] = list(
        human_chart_entry_setup.get("blocking_features") or []
    )
    grouped_logic_trace["human_chart_buy_guard_available"] = bool(human_chart_buy_guard.get("available"))
    grouped_logic_trace["human_chart_buy_guard_applied"] = bool(human_chart_buy_guard.get("applied"))
    grouped_logic_trace["human_chart_buy_guard_blocking_features"] = list(
        human_chart_buy_guard.get("blocking_features") or []
    )
    grouped_logic_trace["late_entry_risk"] = str(chart_human_context.get("late_entry_risk") or "")
    grouped_logic_trace["chart_structure_scoring_consumed"] = bool(chart_human_context.get("available"))
    grouped_logic_trace["entry_quality_score"] = entry_quality_score
    grouped_logic_trace["entry_quality_tier"] = entry_quality_tier
    grouped_logic_trace["entry_quality_path"] = entry_quality_path
    grouped_logic_trace["entry_quality_observability_only"] = True
    grouped_logic_trace["entry_hard_gate_passed"] = bool(entry_hard_gate_passed)
    grouped_logic_trace["entry_hard_gate_blockers"] = list(entry_hard_gate_blockers)
    grouped_logic_trace["entry_quality_vs_gate_summary"] = entry_quality_vs_gate_summary
    grouped_logic_trace["breakout_proximity_score"] = breakout_score
    grouped_logic_trace["etf_deviation_entry_score"] = round(float(etf_deviation_entry_score), 4)
    return None
