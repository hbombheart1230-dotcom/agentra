"""Operator brief input: commander block.

T4-A (P1.5 Third Pass): contiguous statement run / value expression of `apps/operator_ui/data_access_core.py::_build_operator_brief_input` moved verbatim into a
scanner projection Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
Scanner node are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def build_brief_input_commander(commander, commander_applied_policy, commander_artifact, commander_decision):
    return (
        {
            "mode": commander.get("mode"),
            "phase": commander.get("phase"),
            "path": commander.get("path"),
            "status": commander.get("status"),
            "command_intent": commander_decision.get("command_intent"),
            "strategist_invocation": commander_decision.get("strategist_invocation"),
            "llm_policy": commander_decision.get("llm_policy") or commander_decision.get("llm_invocation_policy"),
            "selected_route": commander_artifact.get("selected_route"),
            "route_reason_text": commander_artifact.get("route_reason_text"),
            "strategist_cache_used": commander_artifact.get("strategist_cache_used"),
            "strategist_called": commander_artifact.get("strategist_called"),
            "cooldown_applied": commander_artifact.get("cooldown_applied"),
            "applied_policy": commander_applied_policy,
            "policy_source": commander_artifact.get("policy_source") or commander_decision.get("policy_source"),
            "policy_validation_status": commander_artifact.get("policy_validation_status")
            or commander_decision.get("policy_validation_status"),
            "policy_fallback_used": commander_artifact.get("policy_fallback_used")
            if commander_artifact.get("policy_fallback_used") is not None
            else commander_decision.get("policy_fallback_used"),
            "policy_fallback_reason": commander_artifact.get("policy_fallback_reason")
            or commander_decision.get("policy_fallback_reason"),
            "policy_partial_normalized": commander_artifact.get("policy_partial_normalized")
            if commander_artifact.get("policy_partial_normalized") is not None
            else commander_decision.get("policy_partial_normalized"),
            "policy_default_filled_fields": list(
                commander_artifact.get("policy_default_filled_fields")
                or commander_decision.get("policy_default_filled_fields")
                or []
            )[:12],
            "policy_validation_missing_fields": list(
                commander_artifact.get("policy_validation_missing_fields")
                or commander_decision.get("policy_validation_missing_fields")
                or []
            )[:12],
            "policy_validation_invalid_fields": list(
                commander_artifact.get("policy_validation_invalid_fields")
                or commander_decision.get("policy_validation_invalid_fields")
                or []
            )[:12],
            "override_reason": commander_artifact.get("override_reason") or commander_decision.get("override_reason"),
            "applied_policy_source_chain": list(
                commander_artifact.get("applied_policy_source_chain")
                or commander_decision.get("applied_policy_source_chain")
                or []
            )[:6],
        }
    )

def build_brief_input_strategist(candidate_hints, canonical_trade, market_headlines, raw_input, strategist_artifact, strategist_summary, symbol_headlines, trade_story_input, *, facade):
    return (
        {
            "market_regime": strategist_summary.get("market_regime") or canonical_trade.get("market_regime"),
            "market_sentiment": strategist_summary.get("market_sentiment") or canonical_trade.get("market_sentiment"),
            "themes": list(strategist_summary.get("themes") or canonical_trade.get("themes") or [])[:5],
            "playbook": strategist_summary.get("playbook") or canonical_trade.get("playbook"),
            "scanner_bias": strategist_summary.get("scanner_bias"),
            "risk_tone": facade._strategist_risk_tone(strategist_summary)
            or facade._strategist_risk_tone(strategist_artifact)
            or facade._strategist_risk_tone(trade_story_input)
            or facade._strategist_risk_tone(canonical_trade),
            "monitor_guidance": facade._strategist_monitor_guidance(strategist_summary)
            or facade._strategist_monitor_guidance(strategist_artifact)
            or facade._strategist_monitor_guidance(trade_story_input)
            or facade._strategist_monitor_guidance(canonical_trade),
            "news_query_targets": list(strategist_summary.get("news_query_targets") or canonical_trade.get("news_query_targets") or [])[:8],
            "news_query_reasoning": strategist_summary.get("news_query_reasoning"),
            "global_sentiment_inputs": raw_input.get("global_sentiment_inputs") if isinstance(raw_input.get("global_sentiment_inputs"), dict) else {},
            "candidate_hints": [str(x or "") for x in candidate_hints if str(x or "").strip()],
            "market_headlines": [str(x or "") for x in market_headlines if str(x or "").strip()][:3],
            "symbol_headlines": [str(x or "") for x in symbol_headlines if str(x or "").strip()][:3],
            "market_news_titles": [str((x or {}).get("title") or "") for x in list(raw_input.get("collected_market_news") or [])[:4] if isinstance(x, dict)] or list(canonical_trade.get("market_news_titles") or [])[:4],
            "candidate_news_titles": [str((x or {}).get("title") or "") for x in list(raw_input.get("collected_candidate_news") or [])[:4] if isinstance(x, dict)] or list(canonical_trade.get("candidate_news_titles") or [])[:4],
            "llm_status": strategist_summary.get("llm_frame_status"),
            "llm_low_confidence": strategist_summary.get("llm_frame_low_confidence"),
            "canonical_summary": canonical_trade.get("market_context_summary"),
            "canonical_bullets": list(canonical_trade.get("market_context_bullets") or [])[:6],
        }
    )

def build_brief_input_scanner(canonical_filter_bullets, canonical_filters_summary, canonical_selection_bullets, canonical_trade, component_snapshot, feature_coverage, feature_snapshot, scanner, scanner_selection_trace, scanner_trace, score_breakdown, selected):
    return (
        {
            "candidate_source": scanner.get("summary", {}).get("candidate_source") if isinstance(scanner.get("summary"), dict) else "",
            "candidate_pool_before_filter": (scanner.get("summary") or {}).get("candidate_pool_before_filter") if isinstance(scanner.get("summary"), dict) else None,
            "candidate_pool_after_filter": (scanner.get("summary") or {}).get("candidate_pool_after_filter") if isinstance(scanner.get("summary"), dict) else None,
            "top_ranked_symbols": list(canonical_trade.get("top_candidates") or [])[:5]
            or (
                list((scanner.get("summary") or {}).get("top_ranked_symbols") or [])[:5]
                if isinstance(scanner.get("summary"), dict)
                else []
            ),
            "source_mix": scanner_trace.get("kiwoom_pool_source_mix") if isinstance(scanner_trace.get("kiwoom_pool_source_mix"), dict) else {},
            "selected_symbol": scanner_trace.get("selected_symbol") or selected.get("symbol"),
            "selected_reason": canonical_trade.get("selection_basis")
            or canonical_trade.get("selection_summary")
            or selected.get("why"),
            "source_scores": selected.get("source_scores") if isinstance(selected.get("source_scores"), dict) else {},
            "score_total": selected.get("score_total"),
            "confidence": selected.get("confidence"),
            "feature_coverage": feature_coverage,
            "quote_metrics": scanner.get("quote_metrics") if isinstance(scanner.get("quote_metrics"), dict) else {},
            "score_breakdown": score_breakdown,
            "component_snapshot": component_snapshot,
            "feature_snapshot": feature_snapshot,
            "why_selected": list(canonical_trade.get("why_selected") or [])[:4],
            "selection_trace": dict(scanner_selection_trace or {}),
            "selected_symbol_score_drivers": dict(scanner_selection_trace.get("selected_symbol_score_drivers") or {}),
            "tie_break_rule": canonical_trade.get("tie_break_rule"),
            "runner_ups": list(canonical_trade.get("runner_ups") or [])[:3],
            "runner_ups_lost": list(canonical_trade.get("runner_ups_lost") or [])[:3],
            "playbook": scanner_trace.get("playbook") or canonical_trade.get("playbook"),
            "policy_source": scanner_trace.get("policy_source") or canonical_trade.get("policy_source"),
            "applied_policy_present": (
                scanner_trace.get("applied_policy_present")
                if scanner_trace.get("applied_policy_present") is not None
                else canonical_trade.get("applied_policy_present")
            ),
            "monitor_entry_policy_summary": (
                scanner_trace.get("monitor_entry_policy_summary")
                if isinstance(scanner_trace.get("monitor_entry_policy_summary"), dict)
                else (
                    canonical_trade.get("monitor_entry_policy_summary")
                    if isinstance(canonical_trade.get("monitor_entry_policy_summary"), dict)
                    else {}
                )
            ),
            "scanner_bias_applied": scanner_trace.get("scanner_bias_applied"),
            "scanner_bias_summary": scanner_trace.get("scanner_bias_summary") if isinstance(scanner_trace.get("scanner_bias_summary"), dict) else {},
            "candidate_bias_adjustments": list(scanner_trace.get("candidate_bias_adjustments") or [])[:5],
            "selection_reason_with_bias": scanner_trace.get("selection_reason_with_bias") or selected.get("why"),
            "canonical_bullets": canonical_selection_bullets,
            "canonical_filters_summary": canonical_filters_summary,
            "canonical_filter_bullets": canonical_filter_bullets,
        }
    )

def build_brief_input_monitor(canonical_trade, monitor_applied_policy, monitor_effective_policy, monitor_entry_metrics, monitor_entry_thresholds, monitor_policy_ref, monitor_received_policy, monitor_stop_policy_trace, monitor_summary, monitor_thresholds_used, monitor_timing_assessment, monitor_trace, *, facade):
    return (
        {
            "monitor_reason": monitor_summary.get("monitor_reason") or monitor_trace.get("monitor_reason") or canonical_trade.get("monitor_summary"),
            "exit_reason": monitor_summary.get("exit_reason") or monitor_trace.get("exit_reason") or canonical_trade.get("exit_reason"),
            "position_age_seconds": monitor_summary.get("position_age_seconds"),
            "entry_evaluated": monitor_summary.get("entry_evaluated"),
            "entry_triggered": monitor_summary.get("entry_triggered"),
            "entry_reason": monitor_summary.get("entry_reason") or monitor_trace.get("entry_reason"),
            "entry_pattern": monitor_summary.get("entry_pattern") or monitor_trace.get("entry_pattern"),
            "entry_guard_reason": monitor_summary.get("entry_guard_reason") or monitor_trace.get("entry_guard_reason"),
            "entry_intent_submitted": monitor_summary.get("entry_intent_submitted"),
            "entry_metrics": monitor_summary.get("entry_metrics") if isinstance(monitor_summary.get("entry_metrics"), dict) else {},
            "entry_thresholds": monitor_summary.get("entry_thresholds") if isinstance(monitor_summary.get("entry_thresholds"), dict) else {},
            "thresholds": monitor_trace.get("thresholds") if isinstance(monitor_trace.get("thresholds"), dict) else {},
            "entry_check_summary": monitor_trace.get("entry_check_summary"),
            "entry_blockers": list(monitor_trace.get("entry_blockers") or [])[:8],
            "policy_ref": monitor_policy_ref,
            "timing_assessment": monitor_timing_assessment,
            "thresholds_guards_used": monitor_thresholds_used,
            "threshold_shortfalls": facade._monitor_threshold_shortfall_notes(monitor_entry_metrics, monitor_entry_thresholds),
            "stop_policy_trace": dict(monitor_stop_policy_trace or {}),
            "received_policy": monitor_received_policy,
            "received_policy_source": monitor_trace.get("received_policy_source") or monitor_policy_ref.get("received_policy_source"),
            "effective_policy": monitor_effective_policy,
            "effective_policy_source": monitor_trace.get("effective_policy_source") or monitor_policy_ref.get("effective_policy_source"),
            "effective_policy_source_chain": list(
                monitor_trace.get("effective_policy_source_chain")
                or monitor_policy_ref.get("effective_policy_source_chain")
                or []
            )[:6],
            "policy_adjustments": monitor_trace.get("policy_adjustments")
            if isinstance(monitor_trace.get("policy_adjustments"), dict)
            else (monitor_policy_ref.get("policy_adjustments") if isinstance(monitor_policy_ref.get("policy_adjustments"), dict) else {}),
            "policy_adjustment_summary": monitor_trace.get("policy_adjustment_summary") or monitor_policy_ref.get("policy_adjustment_summary"),
            "policy_adjustment_reasoning": monitor_trace.get("policy_adjustment_reasoning") or monitor_policy_ref.get("policy_adjustment_reasoning"),
            "effective_policy_deltas": list(
                monitor_trace.get("effective_policy_deltas")
                or monitor_policy_ref.get("effective_policy_deltas")
                or []
            )[:8],
            "applied_policy": monitor_applied_policy,
            "policy_source": monitor_trace.get("policy_source") or monitor_policy_ref.get("policy_source"),
            "policy_validation_status": monitor_trace.get("policy_validation_status")
            or monitor_policy_ref.get("policy_validation_status"),
            "policy_fallback_used": monitor_trace.get("policy_fallback_used")
            if monitor_trace.get("policy_fallback_used") is not None
            else monitor_policy_ref.get("policy_fallback_used"),
            "policy_fallback_reason": monitor_trace.get("policy_fallback_reason")
            or monitor_policy_ref.get("policy_fallback_reason"),
            "policy_partial_normalized": monitor_trace.get("policy_partial_normalized")
            if monitor_trace.get("policy_partial_normalized") is not None
            else monitor_policy_ref.get("policy_partial_normalized"),
            "policy_default_filled_fields": list(
                monitor_trace.get("policy_default_filled_fields")
                or monitor_policy_ref.get("policy_default_filled_fields")
                or []
            )[:12],
            "policy_validation_missing_fields": list(
                monitor_trace.get("policy_validation_missing_fields")
                or monitor_policy_ref.get("policy_validation_missing_fields")
                or []
            )[:12],
            "policy_validation_invalid_fields": list(
                monitor_trace.get("policy_validation_invalid_fields")
                or monitor_policy_ref.get("policy_validation_invalid_fields")
                or []
            )[:12],
            "override_reason": monitor_trace.get("override_reason") or monitor_policy_ref.get("override_reason"),
            "applied_policy_source_chain": list(
                monitor_trace.get("applied_policy_source_chain")
                or monitor_policy_ref.get("applied_policy_source_chain")
                or []
            )[:6],
            "strategy_frame_adjustments": list(monitor_trace.get("strategy_frame_adjustments") or [])[:6],
            "exit_policy_guard_adjustments": list(monitor_trace.get("exit_policy_guard_adjustments") or [])[:6],
            "canonical_bullets": list(canonical_trade.get("monitor_bullets") or [])[:6],
            "canonical_snapshot": dict(canonical_trade.get("monitor_snapshot") or {}),
        }
    )

def build_brief_input_trade_report(trade_report):
    return (
        {
            "report_available": trade_report.get("report_available"),
            "trade_id": trade_report.get("trade_id"),
            "lifecycle_status": trade_report.get("lifecycle_status"),
            "lifecycle_summary": trade_report.get("lifecycle_summary"),
            "story_type": trade_report.get("story_type_label") or trade_report.get("story_type"),
            "execution_mode_label": trade_report.get("execution_mode_label"),
            "summary": trade_report.get("report_summary"),
            "reporter_status_human": trade_report.get("reporter_status_human"),
        }
    )
