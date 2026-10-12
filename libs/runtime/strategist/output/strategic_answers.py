"""Strategist strategic-answers assembly (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _build_strategic_answers_r3_impl(
    *,
    commander_context,
    market_regime,
    market_sentiment,
    key_events,
    themes,
    avoid_themes,
    playbook,
    scanner_bias,
    scanner_priority,
    trade_aggressiveness,
    risk_tone,
    monitor_guidance,
    report_focus,
    recent_strategy_feedback,
    strategy_memory,
    read_model_facts,
    reports_root,
    facade,
):
    open_position_refresh_context = (
        dict(commander_context.get("open_position_refresh_context") or {})
        if isinstance(commander_context.get("open_position_refresh_context"), dict)
        else {}
    )
    strategist_refresh_context = (
        dict(commander_context.get("strategist_refresh_context") or {})
        if isinstance(commander_context.get("strategist_refresh_context"), dict)
        else {}
    )
    refresh_context = (
        dict(open_position_refresh_context)
        if open_position_refresh_context
        else dict(strategist_refresh_context)
    )
    commander_horizon_policy = (
        dict(commander_context.get("commander_horizon_policy") or {})
        if isinstance(commander_context.get("commander_horizon_policy"), dict)
        else {}
    )
    selected_symbol = str(refresh_context.get("selected_symbol") or "")
    selected_symbol_was_rank1_raw = refresh_context.get("selected_symbol_was_rank1")
    selected_symbol_was_rank1 = (
        bool(selected_symbol_was_rank1_raw)
        if selected_symbol_was_rank1_raw is not None
        else int(refresh_context.get("selected_rank") or 0) == 1
    )
    return {
        "q1_market_mode": market_regime,
        "q2_global_macro_events": list(key_events),
        "q3_leading_themes": list(themes),
        "q4_theme_strength_check": "use_scanner_score_breakdown_and_theme_boost",
        "q5_preferred_playbook": playbook,
        "q6_scanner_priority_stocks": list(scanner_priority),
        "q7_avoid_conditions": list(avoid_themes),
        "q8_trade_aggressiveness": trade_aggressiveness,
        "q9_risk_tone": risk_tone,
        "q10_scanner_ranking_priority": list(scanner_priority),
        "q11_monitor_exit_guidance": monitor_guidance,
        "q12_reporter_focus": list(report_focus),
        "q13_recent_strategy_feedback": {
            "feedback_window_size": int(recent_strategy_feedback.get("feedback_window_size") or 0),
            "top_recent_strengths": list(recent_strategy_feedback.get("top_recent_strengths") or [])[:3],
            "top_recent_weaknesses": list(recent_strategy_feedback.get("top_recent_weaknesses") or [])[:3],
            "recent_reporter_summary": list(recent_strategy_feedback.get("recent_reporter_summary") or [])[:2],
        },
        "q14_strategy_memory_advisory": {
            "status": str(strategy_memory.get("status") or ""),
            "best_playbooks": list(strategy_memory.get("best_playbooks") or [])[:3],
            "worst_playbooks": list(strategy_memory.get("worst_playbooks") or [])[:3],
            "recent_failures": list(strategy_memory.get("recent_failures") or [])[:3],
            "recent_success_patterns": list(strategy_memory.get("recent_success_patterns") or [])[:3],
            "recent_playbook_performance": dict(strategy_memory.get("playbook_performance_snapshot") or {}),
            "reporter_analysis_digest": dict(strategy_memory.get("reporter_analysis_digest") or {}),
        },
        "q15_commander_refresh_context": {
            "requested": bool(commander_context.get("strategist_refresh_requested")),
            "reason": str(commander_context.get("strategist_refresh_reason") or ""),
            "refresh_scope": str(refresh_context.get("refresh_scope") or ""),
            "selected_symbol": selected_symbol,
            "hold_repeat_count_max": int(refresh_context.get("hold_repeat_count_max") or 0),
            "selected_hold_repeat_count": int(refresh_context.get("selected_hold_repeat_count") or 0),
            "monitor_reason": str(refresh_context.get("monitor_reason") or ""),
            "active_exit_axis": str(refresh_context.get("active_exit_axis") or ""),
            "refresh_summary": str(refresh_context.get("refresh_summary") or ""),
            "selected_rank": int(refresh_context.get("selected_rank") or 0),
            "selected_score": facade._round_optional(refresh_context.get("selected_score"), 4),
            "scanner_primary_candidate": dict(refresh_context.get("scanner_primary_candidate") or {}),
            "actual_selected_candidate": dict(
                refresh_context.get("actual_selected_candidate")
                or refresh_context.get("scanner_primary_candidate")
                or {}
            ),
            "scanner_rank1_candidate": dict(refresh_context.get("scanner_rank1_candidate") or {}),
            "scanner_runner_ups": [
                dict(row)
                for row in list(refresh_context.get("scanner_runner_ups") or [])[:4]
                if isinstance(row, dict)
            ],
            "scanner_top_candidates": [
                dict(row)
                for row in list(refresh_context.get("scanner_top_candidates") or [])[:5]
                if isinstance(row, dict)
            ],
            "selected_symbol_was_rank1": bool(selected_symbol_was_rank1),
            "stage2_context_quality": str(refresh_context.get("stage2_context_quality") or ""),
            "stage2_context_quality_reasons": [
                str(reason or "")
                for reason in list(refresh_context.get("stage2_context_quality_reasons") or [])[:6]
                if str(reason or "").strip()
            ],
            "entry_state": dict(refresh_context.get("entry_state") or {}),
            "carry_state": str(refresh_context.get("carry_state") or commander_context.get("carry_state") or ""),
            "carry_risk_bias": str(
                refresh_context.get("carry_risk_bias") or commander_context.get("carry_risk_bias") or ""
            ),
            "carry_risk_reason": str(
                refresh_context.get("carry_risk_reason") or commander_context.get("carry_risk_reason") or ""
            ),
            "session_open_recovery_assessment": dict(
                refresh_context.get("session_open_recovery_assessment")
                or commander_context.get("session_open_recovery_assessment")
                or {}
            ),
            "prior_monitor_entry_policy_summary": dict(
                refresh_context.get("prior_monitor_entry_policy_summary")
                or strategist_refresh_context.get("prior_monitor_entry_policy_summary")
                or {}
            )
            if isinstance(
                refresh_context.get("prior_monitor_entry_policy_summary")
                or strategist_refresh_context.get("prior_monitor_entry_policy_summary"),
                dict,
            )
            else {},
            "current_monitor_entry_policy_summary": dict(
                refresh_context.get("current_monitor_entry_policy_summary")
                or strategist_refresh_context.get("current_monitor_entry_policy_summary")
                or {}
            )
            if isinstance(
                refresh_context.get("current_monitor_entry_policy_summary")
                or strategist_refresh_context.get("current_monitor_entry_policy_summary"),
                dict,
            )
            else {},
            "selected_symbol_memory": facade._build_symbol_refresh_memory_excerpt(
                selected_symbol,
                read_model_facts,
                reports_root,
            ),
            "commander_horizon_policy": dict(commander_horizon_policy),
            "horizon_context": {
                "owner": str(commander_horizon_policy.get("owner") or "commander") if commander_horizon_policy else "",
                "strategy_horizon": str(commander_horizon_policy.get("strategy_horizon") or ""),
                "source_strategy_horizon": str(commander_horizon_policy.get("source_strategy_horizon") or ""),
                "observability_only": bool(commander_horizon_policy.get("observability_only", True))
                if commander_horizon_policy
                else True,
                "do_not_force_hold": bool(commander_horizon_policy.get("do_not_force_hold", True))
                if commander_horizon_policy
                else True,
            },
        },
        "scanner_bias": scanner_bias,
    }
