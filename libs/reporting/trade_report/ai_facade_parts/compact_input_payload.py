"""Stable ordered compact LLM payload assembly (key order and shape unchanged).

Second Pass (P1.5) intra-function extraction from `libs/reporting/trade_report_ai_compact_input.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def cp_payload_value_result(strategist_evidence, entry_execution_visibility, _compact_strategist_report_context, story_input, _build_report_strategist_refresh_trace, _compact_entry_or_exit_summary, _compact_holding_summary, scanner_bias_summary, market_context_summary, market_context_bullets, scanner_summary, scanner_bullets, filters_summary, filters_bullets, monitor_summary, monitor_bullets, guard_summary, guard_bullets, execution_summary, execution_bullets, reporter_summary, reporter_bullets, conclusion_summary, conclusion_current_action, conclusion_watch_next, conclusion_thesis_invalidation, _compact_timeline_rows, _listify, _as_dict, _clip, _compact_scalar_dict, _compact_named_rows, _compact_monitor_snapshot, monitor_reason, _evidence_digest, market_context, commander_route, scanner_reason, _compact_entry_candidate_cascade, lifecycle_summary, policy_ref_context, scanner_reasoning, guard_reason, execution_outcome, diagnostics, strategist_context, monitor_reasoning, reporter_status, report_section_seeds, execution_quality_seed, *, facade):
    return (
{
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
    )
