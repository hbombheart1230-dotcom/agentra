from __future__ import annotations

from typing import Any, Callable, Dict, List

from libs.reporting.trade_execution_outcome_text import execution_outcome_summary_is_placeholder
from libs.reporting.trade_report_common import (
    compact_named_rows,
    compact_scalar_dict,
    listify,
    report_clip,
)


def as_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}

def compact_section_seed_for_llm(value: Any) -> Dict[str, Any]:
    row = value if isinstance(value, dict) else {}
    out = {
        "summary": report_clip(row.get("summary"), max_len=220),
        "bullets": listify(row.get("bullets"), max_items=2, max_len=140),
        "status": report_clip(row.get("status"), max_len=24),
        "grade": report_clip(row.get("grade"), max_len=16),
        "current_action": report_clip(row.get("current_action"), max_len=24),
        "watch_next": listify(row.get("watch_next"), max_items=2, max_len=120),
        "thesis_invalidation": listify(row.get("thesis_invalidation"), max_items=2, max_len=120),
    }
    return {key: val for key, val in out.items() if val not in ("", None, [], {})}


def sparse_story_input_for_llm(
    story_input: Dict[str, Any],
    *,
    compact_story_input_for_llm: Callable[[Dict[str, Any]], Dict[str, Any]],
    reporter_summary_is_placeholder: Callable[[Any], bool],
    compact_timeline_rows: Callable[..., List[Dict[str, Any]]],
) -> Dict[str, Any]:
    compact = compact_story_input_for_llm(story_input)
    commander = compact.get("commander") if isinstance(compact.get("commander"), dict) else {}
    entry = compact.get("entry_summary") if isinstance(compact.get("entry_summary"), dict) else {}
    exit_summary = compact.get("exit_summary") if isinstance(compact.get("exit_summary"), dict) else {}
    market = compact.get("market_context_human") if isinstance(compact.get("market_context_human"), dict) else {}
    scanner = compact.get("scanner_reason_human") if isinstance(compact.get("scanner_reason_human"), dict) else {}
    monitor = compact.get("monitor_reason_human") if isinstance(compact.get("monitor_reason_human"), dict) else {}
    filters_human = compact.get("filters_human") if isinstance(compact.get("filters_human"), dict) else {}
    guard = compact.get("guard_reason_human") if isinstance(compact.get("guard_reason_human"), dict) else {}
    execution = compact.get("execution_outcome_human") if isinstance(compact.get("execution_outcome_human"), dict) else {}
    reporter = compact.get("reporter_status_human") if isinstance(compact.get("reporter_status_human"), dict) else {}
    conclusion = compact.get("operator_conclusion_human") if isinstance(compact.get("operator_conclusion_human"), dict) else {}
    entry_visibility = compact.get("entry_execution_visibility") if isinstance(compact.get("entry_execution_visibility"), dict) else {}
    report_section_seeds = compact.get("report_section_seeds") if isinstance(compact.get("report_section_seeds"), dict) else {}
    execution_seed = as_dict(report_section_seeds.get("execution_quality"))
    if execution.get("summary") and execution_outcome_summary_is_placeholder(execution_seed.get("summary")):
        execution_seed = dict(execution_seed)
        execution_seed["summary"] = execution.get("summary")
        if execution.get("bullets"):
            execution_seed["bullets"] = listify(execution.get("bullets"), max_items=4, max_len=180)
        if execution.get("status"):
            execution_seed["status"] = execution.get("status")
    guard_seed = as_dict(report_section_seeds.get("guard_approval_result"))
    reporter_seed = as_dict(report_section_seeds.get("reporter_evaluation"))
    if reporter_summary_is_placeholder(reporter.get("summary")) and report_clip(reporter_seed.get("summary"), max_len=220):
        reporter = dict(reporter)
        reporter["summary"] = report_clip(reporter_seed.get("summary"), max_len=220)
        if reporter_seed.get("bullets"):
            reporter["bullets"] = listify(reporter_seed.get("bullets"), max_items=4, max_len=180)
        if reporter_seed.get("status"):
            reporter["status"] = report_clip(reporter_seed.get("status"), max_len=24)
        if reporter_seed.get("grade"):
            reporter["grade"] = report_clip(reporter_seed.get("grade"), max_len=16)
    conclusion_seed = as_dict(report_section_seeds.get("final_operator_conclusion"))
    holding = compact.get("holding_summary") if isinstance(compact.get("holding_summary"), dict) else {}
    lifecycle = compact.get("lifecycle_summary") if isinstance(compact.get("lifecycle_summary"), dict) else {}
    diagnostics = compact.get("ai_report_diagnostics") if isinstance(compact.get("ai_report_diagnostics"), dict) else {}
    return {
        "trade_id": compact.get("trade_id"),
        "story_id": compact.get("story_id"),
        "run_id": compact.get("run_id"),
        "symbol": compact.get("symbol"),
        "action": compact.get("action"),
        "status": compact.get("status"),
        "story_type": compact.get("story_type"),
        "execution_mode_label": compact.get("execution_mode_label"),
        "strategist_output": as_dict(compact.get("strategist_output")),
        "strategist_refresh_trace": as_dict(compact.get("strategist_refresh_trace")),
        "lifecycle_summary": {
            "holding_duration": lifecycle.get("holding_duration"),
            "entry_reason_human": lifecycle.get("entry_reason_human"),
            "exit_reason_human": lifecycle.get("exit_reason_human"),
            "lifecycle_summary_human": lifecycle.get("lifecycle_summary_human"),
        },
        "market_context": {
            "regime": market.get("regime"),
            "market_sentiment": market.get("market_sentiment"),
            "playbook": market.get("playbook"),
            "themes": listify(market.get("themes"), max_items=3, max_len=60),
            "theme_strength_packet": compact_scalar_dict(
                market.get("theme_strength_packet"),
                max_items=8,
                max_len=120,
            ),
            "theme_source": market.get("theme_source"),
            "theme_source_status": market.get("theme_source_status"),
            "theme_source_reason": market.get("theme_source_reason"),
            "theme_strength_top_themes": listify(market.get("theme_strength_top_themes"), max_items=6, max_len=60),
            "risk_mode": market.get("risk_mode"),
            "selected_playbook": market.get("selected_playbook"),
            "preferred_themes": listify(market.get("preferred_themes"), max_items=4, max_len=60),
            "avoid_themes": listify(market.get("avoid_themes"), max_items=4, max_len=60),
            "scanner_bias_summary": {
                "enabled": (market.get("scanner_bias_summary") or {}).get("enabled"),
                "active_biases": listify((market.get("scanner_bias_summary") or {}).get("active_biases"), max_items=6, max_len=80),
                "bias_strength": report_clip((market.get("scanner_bias_summary") or {}).get("bias_strength"), max_len=24),
                "bias_source": report_clip((market.get("scanner_bias_summary") or {}).get("bias_source"), max_len=80),
                "summary": report_clip((market.get("scanner_bias_summary") or {}).get("summary"), max_len=220),
            },
            "global_sentiment_score": market.get("global_sentiment_score"),
            "vix_level": market.get("vix_level"),
            "stress_flags": listify(market.get("stress_flags"), max_items=3, max_len=60),
            "candidate_hints": listify(market.get("candidate_hints"), max_items=6, max_len=24),
            "market_headlines": listify(market.get("market_headlines"), max_items=3, max_len=160),
            "symbol_headlines": listify(market.get("symbol_headlines"), max_items=3, max_len=160),
            "global_sentiment_signal": compact_scalar_dict(
                market.get("global_sentiment_signal"), max_items=8, max_len=120
            ),
            "fear_index": compact_scalar_dict(market.get("fear_index"), max_items=8, max_len=120),
            "key_events": listify(market.get("key_events_hint"), max_items=4, max_len=160),
            "news_input_summary": market.get("news_input_summary"),
        },
        "commander": {
            "command_intent": commander.get("command_intent"),
            "strategist_invocation": commander.get("strategist_invocation"),
            "llm_policy": commander.get("llm_policy"),
            "selected_route": commander.get("selected_route"),
            "route_reason_text": commander.get("route_reason_text"),
            "strategist_cache_used": commander.get("strategist_cache_used"),
            "strategist_called": commander.get("strategist_called"),
            "cooldown_applied": commander.get("cooldown_applied"),
            "applied_policy": compact_scalar_dict(commander.get("applied_policy"), max_items=12, max_len=120),
            "policy_source": commander.get("policy_source"),
            "policy_validation_status": commander.get("policy_validation_status"),
            "policy_fallback_used": commander.get("policy_fallback_used"),
            "policy_fallback_reason": commander.get("policy_fallback_reason"),
            "policy_partial_normalized": commander.get("policy_partial_normalized"),
            "policy_default_filled_fields": listify(commander.get("policy_default_filled_fields"), max_items=12, max_len=80),
            "policy_validation_missing_fields": listify(commander.get("policy_validation_missing_fields"), max_items=12, max_len=80),
            "policy_validation_invalid_fields": listify(commander.get("policy_validation_invalid_fields"), max_items=12, max_len=80),
            "override_reason": commander.get("override_reason"),
            "applied_policy_source_chain": listify(
                commander.get("applied_policy_source_chain"), max_items=6, max_len=80
            ),
            "entry_control": as_dict(commander.get("entry_control"))
            or as_dict(entry_visibility.get("commander_entry_control")),
        },
        "entry": {
            "ts": entry.get("ts"),
            "action": entry.get("action"),
            "reason_human": entry.get("reason_human"),
        },
        "scanner": {
            "selected_symbol": scanner.get("selected_symbol"),
            "selected_rank": scanner.get("selected_rank"),
            "universe_size": scanner.get("universe_size"),
            "ranking_basis": scanner.get("ranking_basis"),
            "playbook": scanner.get("playbook"),
            "policy_source": scanner.get("policy_source"),
            "applied_policy_present": scanner.get("applied_policy_present"),
            "monitor_entry_policy_summary": compact_scalar_dict(
                scanner.get("monitor_entry_policy_summary"), max_items=8, max_len=120
            ),
            "confidence": scanner.get("confidence"),
            "confidence_label": scanner.get("confidence_label"),
            "top_reasons": listify(scanner.get("top_reasons"), max_items=3, max_len=140),
            "why_selected": listify(scanner.get("why_selected"), max_items=4, max_len=140),
            "selection_basis": scanner.get("selection_basis"),
            "selection_reason_with_bias": scanner.get("selection_reason_with_bias"),
            "tie_break_rule": scanner.get("tie_break_rule"),
            "runner_ups": listify(scanner.get("runner_ups"), max_items=2, max_len=140),
            "runner_ups_lost": [
                {
                    "symbol": report_clip((row or {}).get("symbol"), max_len=24),
                    "summary": report_clip((row or {}).get("summary"), max_len=180),
                }
                for row in list(scanner.get("runner_ups_lost") or [])[:3]
                if isinstance(row, dict)
            ],
            "scanner_bias_applied": scanner.get("scanner_bias_applied"),
            "scanner_bias_summary": compact_scalar_dict(scanner.get("scanner_bias_summary"), max_items=8, max_len=120),
            "candidate_bias_adjustments": [
                {
                    "symbol": report_clip((row or {}).get("symbol"), max_len=24),
                    "bias_adjustment": (row or {}).get("bias_adjustment"),
                    "bias_adjustments": listify(
                        [
                            (
                                str((item or {}).get("reason") or "")
                                if isinstance(item, dict)
                                else str(item or "")
                            )
                            for item in list((row or {}).get("bias_adjustments") or [])
                            if str((item or {}).get("reason") if isinstance(item, dict) else item or "").strip()
                        ],
                        max_items=4,
                        max_len=120,
                    ),
                }
                for row in list(scanner.get("candidate_bias_adjustments") or [])[:5]
                if isinstance(row, dict)
            ],
            "selection_trace": {
                "ranked_candidates": compact_named_rows(
                    (scanner.get("selection_trace") or {}).get("ranked_candidates"),
                    max_items=5,
                ),
                "selected_symbol": report_clip((scanner.get("selection_trace") or {}).get("selected_symbol"), max_len=24),
                "selected_rank": (scanner.get("selection_trace") or {}).get("selected_rank"),
                "selection_reason": report_clip((scanner.get("selection_trace") or {}).get("selection_reason"), max_len=280),
                "selected_symbol_score_drivers": compact_scalar_dict(
                    (scanner.get("selection_trace") or {}).get("selected_symbol_score_drivers"),
                    max_items=6,
                    max_len=120,
                ),
            },
            "summary": scanner.get("summary"),
        },
        "filters": {
            "summary": filters_human.get("summary"),
            "bullets": listify(filters_human.get("bullets"), max_items=4, max_len=180),
        },
        "holding": {
            "run_count": holding.get("run_count"),
            "holding_event_count": holding.get("holding_event_count"),
            "recent_monitor_updates": listify(holding.get("recent_monitor_updates"), max_items=4, max_len=140),
        },
        "monitor": {
            "posture": monitor.get("posture"),
            "trigger_type": monitor.get("trigger_type"),
            "summary": monitor.get("summary"),
            "entry_check_summary": monitor.get("entry_check_summary"),
            "entry_blockers": listify(monitor.get("entry_blockers"), max_items=6, max_len=120),
            "threshold_shortfalls": listify(monitor.get("threshold_shortfalls"), max_items=4, max_len=160),
            "policy_ref": compact_scalar_dict(monitor.get("policy_ref"), max_items=8, max_len=120),
            "timing_assessment": compact_scalar_dict(monitor.get("timing_assessment"), max_items=8, max_len=120),
            "thresholds_guards_used": compact_scalar_dict(monitor.get("thresholds_guards_used"), max_items=8, max_len=120),
            "entry_metrics": compact_scalar_dict(monitor.get("entry_metrics"), max_items=10, max_len=120),
            "entry_thresholds": compact_scalar_dict(monitor.get("entry_thresholds"), max_items=8, max_len=120),
            "received_policy": compact_scalar_dict(monitor.get("received_policy"), max_items=12, max_len=120),
            "received_policy_source": monitor.get("received_policy_source"),
            "effective_policy": compact_scalar_dict(monitor.get("effective_policy"), max_items=12, max_len=120),
            "effective_policy_source": monitor.get("effective_policy_source"),
            "effective_policy_source_chain": listify(
                monitor.get("effective_policy_source_chain"), max_items=6, max_len=80
            ),
            "policy_adjustments": compact_scalar_dict(monitor.get("policy_adjustments"), max_items=8, max_len=120),
            "policy_adjustment_summary": monitor.get("policy_adjustment_summary"),
            "policy_adjustment_reasoning": monitor.get("policy_adjustment_reasoning"),
            "effective_policy_deltas": [
                (
                    report_clip(
                        f"{(row or {}).get('field')}: {(row or {}).get('from')} -> {(row or {}).get('to')}",
                        max_len=120,
                    )
                    if isinstance(row, dict)
                    else report_clip(row, max_len=120)
                )
                for row in list(monitor.get("effective_policy_deltas") or [])[:8]
                if (
                    isinstance(row, dict)
                    or str(row or "").strip()
                )
            ],
            "applied_policy": compact_scalar_dict(monitor.get("applied_policy"), max_items=12, max_len=120),
            "policy_source": monitor.get("policy_source"),
            "policy_validation_status": monitor.get("policy_validation_status"),
            "policy_fallback_used": monitor.get("policy_fallback_used"),
            "policy_fallback_reason": monitor.get("policy_fallback_reason"),
            "policy_partial_normalized": monitor.get("policy_partial_normalized"),
            "policy_default_filled_fields": listify(monitor.get("policy_default_filled_fields"), max_items=12, max_len=80),
            "policy_validation_missing_fields": listify(monitor.get("policy_validation_missing_fields"), max_items=12, max_len=80),
            "policy_validation_invalid_fields": listify(monitor.get("policy_validation_invalid_fields"), max_items=12, max_len=80),
            "override_reason": monitor.get("override_reason"),
            "applied_policy_source_chain": listify(
                monitor.get("applied_policy_source_chain"), max_items=6, max_len=80
            ),
            "position_age_seconds": monitor.get("position_age_seconds"),
            "hard_stop_pct": monitor.get("hard_stop_pct"),
            "adaptive_stop_loss_pct": monitor.get("adaptive_stop_loss_pct"),
            "stop_loss_pct": monitor.get("stop_loss_pct"),
            "effective_stop_loss_pct": monitor.get("effective_stop_loss_pct"),
            "trailing_stop_pct": monitor.get("trailing_stop_pct"),
            "take_profit_pct": monitor.get("take_profit_pct"),
            "monitor_stop_policy_trace": compact_scalar_dict(
                monitor.get("monitor_stop_policy_trace"), max_items=8, max_len=120
            ),
            "current_price": monitor.get("current_price"),
            "average_price": monitor.get("average_price"),
            "peak_price": monitor.get("peak_price"),
            "current_drawdown": monitor.get("current_drawdown"),
            "peak_drawdown": monitor.get("peak_drawdown"),
            "active_exit_axis": monitor.get("active_exit_axis"),
            "watch_axes": listify(monitor.get("watch_axes"), max_items=4, max_len=80),
            "price_source": monitor.get("price_source"),
            "entry_candidate_cascade": as_dict(monitor.get("entry_candidate_cascade"))
            or as_dict(entry_visibility.get("monitor_entry_candidate_cascade")),
        },
        "exit": {
            "ts": exit_summary.get("ts"),
            "action": exit_summary.get("action"),
            "reason_human": exit_summary.get("reason_human"),
        },
        "guard": {
            "summary": guard.get("summary") or guard_seed.get("summary"),
            "status": guard.get("status") or guard_seed.get("status"),
            "bullets": listify(guard.get("bullets"), max_items=4, max_len=180) or listify(guard_seed.get("bullets"), max_items=4, max_len=180),
        },
        "execution": {
            "summary": execution.get("summary") or execution_seed.get("summary"),
            "status": execution.get("status") or execution_seed.get("status"),
            "bullets": listify(execution.get("bullets"), max_items=4, max_len=180) or listify(execution_seed.get("bullets"), max_items=4, max_len=180),
        },
        "reporter": {
            "summary": reporter.get("summary") or reporter_seed.get("summary"),
            "status": reporter.get("status") or reporter_seed.get("status"),
            "grade": reporter.get("grade") or reporter_seed.get("grade"),
            "bullets": listify(reporter.get("bullets"), max_items=3, max_len=160) or listify(reporter_seed.get("bullets"), max_items=3, max_len=160),
        },
        "operator_conclusion": {
            "summary": conclusion.get("summary") or conclusion_seed.get("summary"),
            "current_action": conclusion.get("current_action") or conclusion_seed.get("current_action"),
            "watch_next": listify(conclusion.get("watch_next"), max_items=3, max_len=140) or listify(conclusion_seed.get("watch_next"), max_items=3, max_len=140),
            "thesis_invalidation": listify(conclusion.get("thesis_invalidation"), max_items=3, max_len=140) or listify(conclusion_seed.get("thesis_invalidation"), max_items=3, max_len=140),
        },
        "report_section_seeds": {
            "market_context_at_entry": compact_section_seed_for_llm(report_section_seeds.get("market_context_at_entry")),
            "strategist_summary": compact_section_seed_for_llm(report_section_seeds.get("strategist_summary")),
            "why_this_symbol_was_chosen": compact_section_seed_for_llm(report_section_seeds.get("why_this_symbol_was_chosen")),
            "entry_decision": compact_section_seed_for_llm(report_section_seeds.get("entry_decision")),
            "holding_monitoring_story": compact_section_seed_for_llm(report_section_seeds.get("holding_monitoring_story")),
            "exit_decision": compact_section_seed_for_llm(report_section_seeds.get("exit_decision")),
            "scanner_filters": compact_section_seed_for_llm(report_section_seeds.get("scanner_filters")),
            "execution_quality": compact_section_seed_for_llm(execution_seed),
            "guard_approval_result": compact_section_seed_for_llm(guard_seed),
            "reporter_evaluation": compact_section_seed_for_llm(reporter_seed),
            "final_operator_conclusion": compact_section_seed_for_llm(conclusion_seed),
        },
        "timeline": compact_timeline_rows(story_input.get("timeline"), head=1, tail=5),
        "improvement_points": listify(compact.get("improvement_points"), max_items=4, max_len=140),
        "strategist_evidence": as_dict(compact.get("strategist_evidence")),
        "entry_execution_visibility": entry_visibility,
        "ai_report_diagnostics": {
            "report_status": diagnostics.get("report_status"),
            "report_reason_code": diagnostics.get("report_reason_code"),
            "report_reason_human": diagnostics.get("report_reason_human"),
        },
    }

def compact_story_input_for_llm(
    story_input: Dict[str, Any],
    *,
    deps: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the compact LLM story payload behind the reporting façade."""

    _build_shared_summary_seed = deps["build_shared_summary_seed"]
    _extract_policy_ref_context = deps["extract_policy_ref_context"]
    _extract_scanner_bias_summary = deps["extract_scanner_bias_summary"]
    _as_dict = deps["as_dict"]
    _clip = deps["clip"]
    _listify = deps["listify"]
    _compact_scalar_dict = deps["compact_scalar_dict"]
    _reporter_summary_is_placeholder = deps["reporter_summary_is_placeholder"]
    _compact_strategist_report_context = deps["compact_strategist_report_context"]
    _build_report_strategist_refresh_trace = deps["build_report_strategist_refresh_trace"]
    _compact_entry_or_exit_summary = deps["compact_entry_or_exit_summary"]
    _compact_holding_summary = deps["compact_holding_summary"]
    _compact_named_rows = deps["compact_named_rows"]
    _compact_monitor_snapshot = deps["compact_monitor_snapshot"]
    _compact_entry_candidate_cascade = deps["compact_entry_candidate_cascade"]
    _compact_timeline_rows = deps["compact_timeline_rows"]
    _evidence_digest = deps["evidence_digest"]
    execution_outcome_summary_is_placeholder = deps["execution_outcome_summary_is_placeholder"]

    market_context = story_input.get("market_context_human") if isinstance(story_input.get("market_context_human"), dict) else {}
    scanner_reason = story_input.get("scanner_reason_human") if isinstance(story_input.get("scanner_reason_human"), dict) else {}
    filters_human = story_input.get("filters_human") if isinstance(story_input.get("filters_human"), dict) else {}
    monitor_reason = story_input.get("monitor_reason_human") if isinstance(story_input.get("monitor_reason_human"), dict) else {}
    guard_reason = story_input.get("guard_reason_human") if isinstance(story_input.get("guard_reason_human"), dict) else {}
    execution_outcome = story_input.get("execution_outcome_human") if isinstance(story_input.get("execution_outcome_human"), dict) else {}
    reporter_status = story_input.get("reporter_status_human") if isinstance(story_input.get("reporter_status_human"), dict) else {}
    operator_conclusion = story_input.get("operator_conclusion_human") if isinstance(story_input.get("operator_conclusion_human"), dict) else {}
    lifecycle_summary = story_input.get("lifecycle_summary") if isinstance(story_input.get("lifecycle_summary"), dict) else {}
    diagnostics = story_input.get("ai_report_diagnostics") if isinstance(story_input.get("ai_report_diagnostics"), dict) else {}
    shared_seed = _build_shared_summary_seed(story_input)
    commander_route = shared_seed.get("commander_route") if isinstance(shared_seed.get("commander_route"), dict) else {}
    strategist_evidence = shared_seed.get("strategist_evidence") if isinstance(shared_seed.get("strategist_evidence"), dict) else {}
    strategist_context = shared_seed.get("strategist_context") if isinstance(shared_seed.get("strategist_context"), dict) else {}
    entry_execution_visibility = (
        shared_seed.get("entry_execution_visibility")
        if isinstance(shared_seed.get("entry_execution_visibility"), dict)
        else {}
    )
    scanner_reasoning = shared_seed.get("scanner_reasoning") if isinstance(shared_seed.get("scanner_reasoning"), dict) else {}
    monitor_reasoning = shared_seed.get("monitor_reasoning") if isinstance(shared_seed.get("monitor_reasoning"), dict) else {}
    policy_ref_context = _extract_policy_ref_context(story_input, monitor_reason)
    scanner_bias_summary = _extract_scanner_bias_summary(story_input, scanner_reason)
    report_section_seeds = shared_seed.get("report_section_seeds") if isinstance(shared_seed.get("report_section_seeds"), dict) else {}
    market_context_seed = _as_dict(report_section_seeds.get("market_context_at_entry"))
    strategist_summary_seed = _as_dict(report_section_seeds.get("strategist_summary"))
    why_symbol_seed = _as_dict(report_section_seeds.get("why_this_symbol_was_chosen"))
    holding_story_seed = _as_dict(report_section_seeds.get("holding_monitoring_story"))
    scanner_filters_seed = _as_dict(report_section_seeds.get("scanner_filters"))
    execution_quality_seed = _as_dict(report_section_seeds.get("execution_quality"))
    if _clip(execution_outcome.get("summary"), max_len=280) and execution_outcome_summary_is_placeholder(execution_quality_seed.get("summary")):
        execution_quality_seed = dict(execution_quality_seed)
        execution_quality_seed["summary"] = _clip(execution_outcome.get("summary"), max_len=280)
        if execution_outcome.get("bullets"):
            execution_quality_seed["bullets"] = _listify(execution_outcome.get("bullets"), max_items=6, max_len=220)
        if execution_outcome.get("status"):
            execution_quality_seed["status"] = _clip(execution_outcome.get("status"), max_len=48)
    market_context_summary = _clip(market_context.get("summary"), max_len=320) or _clip(market_context_seed.get("summary"), max_len=320)
    market_context_bullets = _listify(market_context.get("bullets"), max_items=6, max_len=220) or _listify(market_context_seed.get("bullets"), max_items=6, max_len=220)
    if not market_context_summary:
        market_context_summary = _clip(strategist_summary_seed.get("summary"), max_len=320)
    scanner_summary = _clip(scanner_reason.get("summary"), max_len=320) or _clip(why_symbol_seed.get("summary"), max_len=320)
    scanner_bullets = _listify(scanner_reason.get("bullets"), max_items=6, max_len=220) or _listify(why_symbol_seed.get("bullets"), max_items=6, max_len=220)
    filters_summary = _clip(filters_human.get("summary"), max_len=280) or _clip(scanner_filters_seed.get("summary"), max_len=280)
    filters_bullets = _listify(filters_human.get("bullets"), max_items=6, max_len=220) or _listify(scanner_filters_seed.get("bullets"), max_items=6, max_len=220)
    monitor_summary = _clip(monitor_reason.get("summary"), max_len=280) or _clip(holding_story_seed.get("summary"), max_len=280)
    monitor_bullets = _listify(monitor_reason.get("bullets"), max_items=6, max_len=220) or _listify(holding_story_seed.get("bullets"), max_items=6, max_len=220)
    guard_summary = _clip(guard_reason.get("summary"), max_len=280) or _clip((_as_dict(report_section_seeds.get("guard_approval_result"))).get("summary"), max_len=280)
    guard_bullets = _listify(guard_reason.get("bullets"), max_items=6, max_len=220) or _listify((_as_dict(report_section_seeds.get("guard_approval_result"))).get("bullets"), max_items=6, max_len=220)
    execution_summary = _clip(execution_outcome.get("summary"), max_len=280) or _clip(execution_quality_seed.get("summary"), max_len=280)
    execution_bullets = _listify(execution_outcome.get("bullets"), max_items=6, max_len=220) or _listify(execution_quality_seed.get("bullets"), max_items=6, max_len=220)
    reporter_seed = _as_dict(report_section_seeds.get("reporter_evaluation"))
    if _reporter_summary_is_placeholder(reporter_status.get("summary")) and _clip(reporter_seed.get("summary"), max_len=280):
        reporter_status = dict(reporter_status)
        reporter_status["summary"] = _clip(reporter_seed.get("summary"), max_len=280)
        if reporter_seed.get("bullets"):
            reporter_status["bullets"] = _listify(reporter_seed.get("bullets"), max_items=5, max_len=180)
        if reporter_seed.get("status"):
            reporter_status["status"] = _clip(reporter_seed.get("status"), max_len=32)
        if reporter_seed.get("grade"):
            reporter_status["grade"] = _clip(reporter_seed.get("grade"), max_len=24)
    reporter_summary = _clip(reporter_status.get("summary"), max_len=280) or _clip(reporter_seed.get("summary"), max_len=280)
    reporter_bullets = _listify(reporter_status.get("bullets"), max_items=5, max_len=180) or _listify(reporter_seed.get("bullets"), max_items=5, max_len=180)
    conclusion_current_action = _clip(operator_conclusion.get("current_action"), max_len=24) or _clip((_as_dict(report_section_seeds.get("final_operator_conclusion"))).get("current_action"), max_len=24)
    conclusion_watch_next = _listify(operator_conclusion.get("watch_next"), max_items=5, max_len=180) or _listify((_as_dict(report_section_seeds.get("final_operator_conclusion"))).get("watch_next"), max_items=5, max_len=180)
    conclusion_thesis_invalidation = _listify(operator_conclusion.get("thesis_invalidation"), max_items=5, max_len=180) or _listify((_as_dict(report_section_seeds.get("final_operator_conclusion"))).get("thesis_invalidation"), max_items=5, max_len=180)
    conclusion_summary = _clip(operator_conclusion.get("summary"), max_len=280) or _clip((_as_dict(report_section_seeds.get("final_operator_conclusion"))).get("summary"), max_len=280)
    return {
        "trade_id": story_input.get("trade_id") or story_input.get("story_id"),
        "story_id": story_input.get("story_id"),
        "run_id": story_input.get("run_id"),
        "symbol": story_input.get("symbol"),
        "action": story_input.get("action"),
        "status": story_input.get("status"),
        "story_type": story_input.get("story_type"),
        "execution_mode_label": story_input.get("execution_mode_label"),
        "strategist_output": _compact_strategist_report_context(story_input),
        "strategist_refresh_trace": _build_report_strategist_refresh_trace(story_input),
        "entry_summary": _compact_entry_or_exit_summary(story_input.get("entry_summary")),
        "holding_summary": _compact_holding_summary(story_input.get("holding_summary")),
        "exit_summary": _compact_entry_or_exit_summary(story_input.get("exit_summary")),
        "lifecycle_summary": {
            "holding_duration": _clip(lifecycle_summary.get("holding_duration"), max_len=40),
            "entry_reason_human": _clip(lifecycle_summary.get("entry_reason_human"), max_len=240),
            "exit_reason_human": _clip(lifecycle_summary.get("exit_reason_human"), max_len=240),
            "lifecycle_summary_human": _clip(lifecycle_summary.get("lifecycle_summary_human"), max_len=320),
        },
        "market_context_human": {
            "regime": _clip(market_context.get("regime"), max_len=24),
            "market_sentiment": _clip(market_context.get("market_sentiment"), max_len=24),
            "playbook": _clip(market_context.get("playbook"), max_len=32),
            "themes": _listify(market_context.get("themes"), max_items=4, max_len=80),
            "theme_strength_packet": _compact_scalar_dict(
                market_context.get("theme_strength_packet") or strategist_context.get("theme_strength_packet"),
                max_items=8,
                max_len=120,
            ),
            "theme_source": _clip(market_context.get("theme_source") or strategist_context.get("theme_source"), max_len=80),
            "theme_source_status": _clip(
                market_context.get("theme_source_status") or strategist_context.get("theme_source_status"),
                max_len=80,
            ),
            "theme_source_reason": _clip(
                market_context.get("theme_source_reason") or strategist_context.get("theme_source_reason"),
                max_len=160,
            ),
            "theme_strength_top_themes": _listify(
                market_context.get("theme_strength_top_themes") or strategist_context.get("theme_strength_top_themes"),
                max_items=6,
                max_len=80,
            ),
            "risk_tone": _clip(market_context.get("risk_tone") or strategist_context.get("risk_tone"), max_len=40),
            "risk_mode": _clip(policy_ref_context.get("risk_mode"), max_len=32),
            "selected_playbook": _clip(policy_ref_context.get("selected_playbook"), max_len=32),
            "preferred_themes": _listify(policy_ref_context.get("preferred_themes"), max_items=4, max_len=80),
            "avoid_themes": _listify(policy_ref_context.get("avoid_themes"), max_items=4, max_len=80),
            "scanner_bias_summary": scanner_bias_summary,
            "global_sentiment_score": market_context.get("global_sentiment_score"),
            "vix_level": market_context.get("vix_level"),
            "candidate_hints": _listify(
                market_context.get("candidate_hints") or strategist_evidence.get("candidate_hints"),
                max_items=8,
                max_len=24,
            ),
            "market_headlines": _listify(
                market_context.get("market_headlines") or strategist_evidence.get("market_headlines"),
                max_items=3,
                max_len=180,
            ),
            "symbol_headlines": _listify(
                market_context.get("symbol_headlines") or strategist_evidence.get("symbol_headlines"),
                max_items=3,
                max_len=180,
            ),
            "global_sentiment_signal": _compact_scalar_dict(
                market_context.get("global_sentiment_signal") or strategist_evidence.get("global_sentiment_signal"),
                max_items=8,
                max_len=120,
            ),
            "korea_indices": _as_dict(market_context.get("korea_indices") or strategist_evidence.get("korea_indices")),
            "fear_index": _compact_scalar_dict(
                market_context.get("fear_index") or strategist_evidence.get("fear_index"),
                max_items=8,
                max_len=120,
            ),
            "headline_count": market_context.get("headline_count"),
            "news_query_count": market_context.get("news_query_count"),
            "market_signal_total": market_context.get("market_signal_total"),
            "candidate_signal_total": market_context.get("candidate_signal_total"),
            "news_query_targets": _listify(market_context.get("news_query_targets"), max_items=6, max_len=80),
            "key_events_hint": _listify(
                market_context.get("key_events_hint") or strategist_evidence.get("key_events"),
                max_items=4,
                max_len=180,
            ),
            "market_news_titles": _listify(market_context.get("market_news_titles"), max_items=3, max_len=140),
            "candidate_news_titles": _listify(market_context.get("candidate_news_titles"), max_items=3, max_len=140),
            "stress_flags": _listify(market_context.get("stress_flags"), max_items=4, max_len=80),
            "news_input_summary": _clip(market_context.get("news_input_summary"), max_len=220),
            "summary": market_context_summary,
            "bullets": market_context_bullets,
        },
        "commander": {
            "command_intent": _clip(commander_route.get("command_intent"), max_len=40),
            "strategist_invocation": _clip(commander_route.get("strategist_invocation"), max_len=40),
            "llm_policy": _clip(commander_route.get("llm_policy"), max_len=40),
            "selected_route": _clip(commander_route.get("selected_route"), max_len=60),
            "route_reason_text": _clip(commander_route.get("reason"), max_len=220),
            "strategist_cache_used": commander_route.get("strategist_cache_used"),
            "strategist_called": commander_route.get("strategist_called"),
            "cooldown_applied": commander_route.get("cooldown_applied"),
            "applied_policy": _compact_scalar_dict(commander_route.get("applied_policy"), max_items=12, max_len=120),
            "policy_source": _clip(commander_route.get("policy_source"), max_len=80),
            "policy_validation_status": _clip(commander_route.get("policy_validation_status"), max_len=80),
            "policy_fallback_used": commander_route.get("policy_fallback_used"),
            "policy_fallback_reason": _clip(commander_route.get("policy_fallback_reason"), max_len=220),
            "policy_partial_normalized": commander_route.get("policy_partial_normalized"),
            "policy_default_filled_fields": _listify(commander_route.get("policy_default_filled_fields"), max_items=12, max_len=80),
            "policy_validation_missing_fields": _listify(commander_route.get("policy_validation_missing_fields"), max_items=12, max_len=80),
            "policy_validation_invalid_fields": _listify(commander_route.get("policy_validation_invalid_fields"), max_items=12, max_len=80),
            "override_reason": _clip(commander_route.get("override_reason"), max_len=160),
            "applied_policy_source_chain": _listify(
                commander_route.get("applied_policy_source_chain"), max_items=6, max_len=80
            ),
            "entry_control": _as_dict(commander_route.get("entry_control"))
            or _as_dict(entry_execution_visibility.get("commander_entry_control")),
        },
        "scanner_reason_human": {
            "selected_symbol": _clip(scanner_reason.get("selected_symbol"), max_len=24),
            "selected_rank": scanner_reason.get("selected_rank"),
            "universe_size": scanner_reason.get("universe_size"),
            "ranking_basis": _clip(scanner_reason.get("ranking_basis"), max_len=180),
            "playbook": _clip(scanner_reason.get("playbook") or scanner_reasoning.get("playbook"), max_len=80),
            "policy_source": _clip(scanner_reason.get("policy_source") or scanner_reasoning.get("policy_source"), max_len=80),
            "applied_policy_present": (
                scanner_reason.get("applied_policy_present")
                if scanner_reason.get("applied_policy_present") is not None
                else scanner_reasoning.get("applied_policy_present")
            ),
            "monitor_entry_policy_summary": _compact_scalar_dict(
                scanner_reason.get("monitor_entry_policy_summary")
                or scanner_reasoning.get("monitor_entry_policy_summary"),
                max_items=8,
                max_len=120,
            ),
            "selected_score": scanner_reason.get("selected_score"),
            "selected_sources": _listify(scanner_reason.get("selected_sources"), max_items=5, max_len=80),
            "source_scores": scanner_reason.get("source_scores") if isinstance(scanner_reason.get("source_scores"), dict) else {},
            "score_breakdown": scanner_reason.get("score_breakdown") if isinstance(scanner_reason.get("score_breakdown"), dict) else {},
            "why_selected": _listify(scanner_reason.get("why_selected"), max_items=4, max_len=160),
            "selection_basis": _clip(scanner_reason.get("selection_basis"), max_len=240),
            "selection_reason_with_bias": _clip(
                scanner_reason.get("selection_reason_with_bias") or scanner_reasoning.get("selection_reason_with_bias"),
                max_len=320,
            ),
            "tie_break_rule": _clip(scanner_reason.get("tie_break_rule"), max_len=180),
            "top_candidates": _compact_named_rows(scanner_reason.get("top_candidates"), max_items=3),
            "confidence": scanner_reason.get("confidence"),
            "confidence_label": _clip(scanner_reason.get("confidence_label"), max_len=32),
            "top_reasons": _listify(scanner_reason.get("top_reasons"), max_items=5, max_len=180),
            "runner_ups": _compact_named_rows(scanner_reason.get("runner_ups"), max_items=3),
            "runner_ups_lost": [
                {
                    "symbol": _clip((row or {}).get("symbol"), max_len=24),
                    "summary": _clip((row or {}).get("summary"), max_len=180),
                }
                for row in list(scanner_reason.get("runner_ups_lost") or [])[:3]
                if isinstance(row, dict)
            ],
            "scanner_bias_applied": (
                scanner_reason.get("scanner_bias_applied")
                if scanner_reason.get("scanner_bias_applied") is not None
                else scanner_reasoning.get("scanner_bias_applied")
            ),
            "scanner_bias_summary": _compact_scalar_dict(
                scanner_reason.get("scanner_bias_summary") or scanner_reasoning.get("scanner_bias_summary"),
                max_items=8,
                max_len=120,
            ),
            "candidate_bias_adjustments": [
                {
                    "symbol": _clip((row or {}).get("symbol"), max_len=24),
                    "bias_adjustment": (row or {}).get("bias_adjustment"),
                    "bias_adjustments": _listify(
                        [
                            (
                                str((item or {}).get("reason") or "")
                                if isinstance(item, dict)
                                else str(item or "")
                            )
                            for item in list((row or {}).get("bias_adjustments") or [])
                            if str((item or {}).get("reason") if isinstance(item, dict) else item or "").strip()
                        ],
                        max_items=4,
                        max_len=120,
                    ),
                }
                for row in list(
                    scanner_reason.get("candidate_bias_adjustments")
                    or scanner_reasoning.get("candidate_bias_adjustments")
                    or []
                )[:5]
                if isinstance(row, dict)
            ],
            "selection_trace": {
                "ranked_candidates": _compact_named_rows(
                    (scanner_reason.get("scanner_selection_trace") or {}).get("ranked_candidates")
                    or (scanner_reasoning.get("selection_trace") or {}).get("ranked_candidates"),
                    max_items=5,
                ),
                "selected_symbol": _clip(
                    (scanner_reason.get("scanner_selection_trace") or {}).get("selected_symbol")
                    or (scanner_reasoning.get("selection_trace") or {}).get("selected_symbol"),
                    max_len=24,
                ),
                "selected_rank": (scanner_reason.get("scanner_selection_trace") or {}).get("selected_rank")
                or (scanner_reasoning.get("selection_trace") or {}).get("selected_rank"),
                "selection_reason": _clip(
                    (scanner_reason.get("scanner_selection_trace") or {}).get("selection_reason")
                    or (scanner_reasoning.get("selection_trace") or {}).get("selection_reason"),
                    max_len=280,
                ),
                "selected_symbol_score_drivers": _compact_scalar_dict(
                    (scanner_reason.get("scanner_selection_trace") or {}).get("selected_symbol_score_drivers")
                    or (scanner_reasoning.get("selection_trace") or {}).get("selected_symbol_score_drivers"),
                    max_items=6,
                    max_len=120,
                ),
            },
            "summary": scanner_summary,
            "comparison": _clip(scanner_reason.get("comparison"), max_len=240),
            "bullets": scanner_bullets,
        },
        "filters_human": {
            "summary": filters_summary,
            "bullets": filters_bullets,
        },
        "monitor_reason_human": {
            **_compact_monitor_snapshot(monitor_reason),
            "summary": monitor_summary,
            "bullets": monitor_bullets,
            "threshold_shortfalls": _listify(
                monitor_reason.get("threshold_shortfalls")
                or (monitor_reasoning.get("monitor_blocker_trace") or {}).get("threshold_shortfalls"),
                max_items=4,
                max_len=160,
            ),
            "monitor_stop_policy_trace": _compact_scalar_dict(
                monitor_reason.get("monitor_stop_policy_trace")
                or monitor_reasoning.get("monitor_stop_policy_trace"),
                max_items=8,
                max_len=120,
            ),
            "entry_candidate_cascade": _as_dict(
                entry_execution_visibility.get("monitor_entry_candidate_cascade")
            )
            or _compact_entry_candidate_cascade(monitor_reason.get("entry_candidate_cascade")),
        },
        "guard_reason_human": {
            "summary": guard_summary,
            "status": _clip(guard_reason.get("status"), max_len=32),
            "bullets": guard_bullets,
        },
        "execution_outcome_human": {
            "summary": execution_summary,
            "status": _clip(execution_outcome.get("status"), max_len=32),
            "bullets": execution_bullets,
        },
        "reporter_status_human": {
            "summary": reporter_summary,
            "status": _clip(reporter_status.get("status"), max_len=32) or _clip((_as_dict(report_section_seeds.get("reporter_evaluation"))).get("status"), max_len=32),
            "grade": _clip(reporter_status.get("grade"), max_len=16) or _clip((_as_dict(report_section_seeds.get("reporter_evaluation"))).get("grade"), max_len=16),
            "bullets": reporter_bullets,
        },
        "operator_conclusion_human": {
            "summary": conclusion_summary,
            "current_action": conclusion_current_action,
            "watch_next": conclusion_watch_next,
            "thesis_invalidation": conclusion_thesis_invalidation,
        },
        "report_section_seeds": {
            key: {
                "summary": _clip((_as_dict(value)).get("summary"), max_len=280),
                "bullets": _listify((_as_dict(value)).get("bullets"), max_items=4, max_len=180),
                "status": _clip((_as_dict(value)).get("status"), max_len=48),
                "grade": _clip((_as_dict(value)).get("grade"), max_len=24),
                "current_action": _clip((_as_dict(value)).get("current_action"), max_len=24),
                "watch_next": _listify((_as_dict(value)).get("watch_next"), max_items=4, max_len=140),
                "thesis_invalidation": _listify((_as_dict(value)).get("thesis_invalidation"), max_items=4, max_len=140),
            }
            for key, value in ({**report_section_seeds, "execution_quality": execution_quality_seed}).items()
            if isinstance(value, dict)
        },
        "timeline": _compact_timeline_rows(story_input.get("timeline")),
        "warnings": _listify(story_input.get("warnings"), max_items=8, max_len=180),
        "improvement_points": _listify(story_input.get("improvement_points"), max_items=6, max_len=180),
        "strategist_evidence": strategist_evidence,
        "scanner_selection_trace": _as_dict(story_input.get("scanner_selection_trace")),
        "monitor_stop_policy_trace": _as_dict(story_input.get("monitor_stop_policy_trace")),
        "monitor_blocker_trace": _as_dict(story_input.get("monitor_blocker_trace")),
        "entry_execution_visibility": entry_execution_visibility,
        "evidence_digest": {
            "strategist": _evidence_digest(
                story_input.get("strategist_evidence"),
                ["market_context_snapshots", "global_sentiment_breakdowns", "news_evidence_ranked", "decision_frames", "llm_response_saved"],
            ),
            "scanner": _evidence_digest(
                story_input.get("scanner_evidence"),
                ["candidate_pool_snapshots", "candidate_ranking_tables", "candidate_selection_reasons", "selection_outputs"],
            ),
            "monitor": _evidence_digest(
                story_input.get("monitor_timeline"),
                ["threshold_snapshots", "state_transitions", "exit_decision_details", "cycle_summaries"],
            ),
        },
        "ai_report_diagnostics": {
            "report_status": _clip(diagnostics.get("report_status"), max_len=24),
            "report_reason_code": _clip(diagnostics.get("report_reason_code"), max_len=48),
            "report_reason_human": _clip(diagnostics.get("report_reason_human"), max_len=220),
            "next_expected_step": _clip(diagnostics.get("next_expected_step"), max_len=220),
        },
    }



