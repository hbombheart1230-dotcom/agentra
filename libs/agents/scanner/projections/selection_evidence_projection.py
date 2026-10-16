"""Scanner selected/scan-output and rank-evidence projections (state-write order stays in the node; canonical ranking owner untouched).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/scanner_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def scan_select_value_state_scanner_output(top_score, visible_ranked_candidates, ranking_before_policy, ranking_after_policy, practical_w, scanner_priority, playbook, scanner_bias, trade_aggressiveness, risk_tone, policy, policy_provenance, commander_scanner_policy, score_adjustment_trace, reentry_penalty_applied, reentry_penalty_value, diversification_applied, diversification_bonus_value, selection_veto_enforced, state, scan_results_sorted, selected, pool_meta, scanner_policy_trace, market_representative_guard_meta, blocker_family_overlay_meta, scanner_guidance, compatibility_bias_context, *, facade):
    return (
{
        "top_stock": state["top_stock"] or None,
        "primary_watch_symbol": state["top_stock"] or None,
        "score": (
            float(selected.get("raw_score"))
            if isinstance(selected, dict) and selected.get("raw_score") is not None
            else float(selected.get("score"))
            if isinstance(selected, dict) and selected.get("score") is not None
            else None
        ),
        "top_score": top_score,
        "risk_score": (
            float(selected.get("risk_score"))
            if isinstance(selected, dict) and selected.get("risk_score") is not None
            else None
        ),
        "confidence": (
            float(selected.get("confidence"))
            if isinstance(selected, dict) and selected.get("confidence") is not None
            else None
        ),
        "candidate_count": int(len(scan_results_sorted)),
        "candidate_pool_size": int(len(scan_results_sorted)),
        "ranked_candidates": visible_ranked_candidates,
        "watch_candidates": visible_ranked_candidates,
        "candidate_source": str(pool_meta.get("candidate_source") or ""),
        "scanner_candidate_source": str(pool_meta.get("scanner_candidate_source") or ""),
        "scanner_policy_source": str(pool_meta.get("scanner_policy_source") or ""),
        "scanner_fallback_mode": str(pool_meta.get("scanner_fallback_mode") or ""),
        "scanner_strict_mode": bool(pool_meta.get("scanner_strict_mode")),
        "fallback_reason": str(pool_meta.get("fallback_reason") or ""),
        "blocked_static_fallback": bool(pool_meta.get("blocked_static_fallback")),
        "strict_kiwoom_only": bool(pool_meta.get("strict_kiwoom_only")),
        "theme_filter_applied": bool(pool_meta.get("theme_filter_applied")),
        "market_native_bypass_count": int(pool_meta.get("market_native_bypass_count") or 0),
        "market_native_bypass_symbols": list(pool_meta.get("market_native_bypass_symbols") or []),
        "avoid_filter_applied": bool(pool_meta.get("avoid_filter_applied")),
        "avoid_filter_reason": str(pool_meta.get("avoid_filter_reason") or ""),
        "avoid_filter_fallback_used": bool(pool_meta.get("avoid_filter_fallback_used")),
        "backfill_used": bool(pool_meta.get("backfill_used")),
        "backfill_count": int(pool_meta.get("backfill_count") or 0),
        "backfill_skipped_reason": str(pool_meta.get("backfill_skipped_reason") or ""),
        "scan_aggressiveness": float(facade._to_float(pool_meta.get("scan_aggressiveness"))),
        "strict_mode_relaxed_by_scan_aggressiveness": bool(pool_meta.get("strict_mode_relaxed_by_scan_aggressiveness")),
        "candidate_limit_base": int(pool_meta.get("candidate_limit_base") or 0),
        "candidate_limit_effective": int(pool_meta.get("candidate_limit_effective") or 0),
        "aggressive_source_expansion_used": bool(pool_meta.get("aggressive_source_expansion_used")),
        "aggressive_source_expansion_slots": int(pool_meta.get("aggressive_source_expansion_slots") or 0),
        "aggressive_source_expansion_sources": list(pool_meta.get("aggressive_source_expansion_sources") or []),
        "score_weights": dict(practical_w),
        "source_mix": dict(pool_meta.get("pool_source_mix") or {}),
        "theme_source": str(scanner_guidance.get("theme_source") or ""),
        "theme_source_status": str(scanner_guidance.get("theme_source_status") or ""),
        "selected_themes": list(pool_meta.get("selected_themes") or []),
        "selected_theme_source": str(pool_meta.get("selected_theme_source") or ""),
        "available_themes": list(scanner_guidance.get("available_themes") or [])[:8],
        "theme_strategy": dict(scanner_guidance.get("theme_strategy") or {})
        if isinstance(scanner_guidance.get("theme_strategy"), dict)
        else {},
        "theme_strength_packet": dict(scanner_guidance.get("theme_strength_packet") or {})
        if isinstance(scanner_guidance.get("theme_strength_packet"), dict)
        else {},
        "asset_universe_policy": str(pool_meta.get("asset_universe_policy") or ""),
        "asset_universe_policy_source": str(pool_meta.get("asset_universe_policy_source") or ""),
        "excluded_candidate_count_by_asset_policy": int(pool_meta.get("asset_policy_excluded_count") or 0),
        "excluded_candidates_by_asset_policy": list(pool_meta.get("asset_policy_exclusions") or []),
        "excluded_candidate_count_by_mock_broker_restricted": int(pool_meta.get("mock_broker_restricted_excluded_count") or 0),
        "excluded_candidates_by_mock_broker_restricted": list(pool_meta.get("mock_broker_restricted_exclusions") or []),
        "mock_broker_restricted_filter_applied": bool(pool_meta.get("mock_broker_restricted_filter_applied")),
        "asset_detection_stats": dict(pool_meta.get("asset_detection_stats") or {}),
        "unknown_asset_candidate_count": int(pool_meta.get("unknown_asset_candidate_count") or 0),
        "total_candidates_before_filter": int(pool_meta.get("total_candidates_before_filter") or 0),
        "total_candidates_after_filter": int(pool_meta.get("total_candidates_after_filter") or 0),
        "condition_search_status": str(pool_meta.get("condition_search_status") or ""),
        "condition_search_source": str(pool_meta.get("condition_search_source") or ""),
        "condition_search_reason": str(pool_meta.get("condition_search_reason") or ""),
        "scanner_source_policy": dict(pool_meta.get("scanner_source_policy") or {}),
        "strategist_scanner_priority": list(scanner_priority),
        "strategist_playbook": playbook or None,
        "strategist_scanner_bias": scanner_bias or None,
        "strategist_avoid_themes": list(pool_meta.get("avoid_themes") or []),
        "strategist_trade_aggressiveness": trade_aggressiveness or None,
        "strategist_risk_tone": risk_tone or None,
        "repeat_guard": facade._resolve_scanner_repeat_guard_policy(policy),
        "recent_scanner_selected_count": int(len(facade._scanner_recent_selection_history(state))),
        "commander_context_consumed": bool(scanner_policy_trace.get("commander_context_consumed")),
        "consumed_fields": list(scanner_policy_trace.get("consumed_fields") or []),
        "commander_priority_ref": dict(scanner_policy_trace.get("commander_priority_ref") or {}),
        "strategist_constraints_ref": dict(scanner_policy_trace.get("strategist_constraints_ref") or {}),
        "selection_basis": dict(scanner_policy_trace.get("selection_basis") or {}),
        "ranking_factors": list(scanner_policy_trace.get("ranking_factors") or []),
        "playbook": str(scanner_policy_trace.get("playbook") or playbook or ""),
        "policy_source": str(scanner_policy_trace.get("policy_source") or ""),
        "applied_policy_present": bool(scanner_policy_trace.get("applied_policy_present")),
        "monitor_entry_policy_summary": dict(scanner_policy_trace.get("monitor_entry_policy_summary") or {}),
        "entry_compatibility_score": float(facade._to_float((selected or {}).get("entry_compatibility_score"))) if isinstance(selected, dict) else 0.0,
        "compatibility_bias": float(facade._to_float((selected or {}).get("compatibility_bias"))) if isinstance(selected, dict) else 0.0,
        "compatibility_components": dict((selected or {}).get("compatibility_components") or {}) if isinstance(selected, dict) else {},
        "scanner_chart_fit_score": float(facade._to_float((selected or {}).get("scanner_chart_fit_score"))) if isinstance(selected, dict) else 0.0,
        "scanner_chart_fit_authority": str((selected or {}).get("scanner_chart_fit_authority") or "") if isinstance(selected, dict) else "",
        "scanner_chart_fit_components": dict((selected or {}).get("scanner_chart_fit_components") or {}) if isinstance(selected, dict) else {},
        "tactic_suitability": dict((selected or {}).get("tactic_suitability") or {}) if isinstance(selected, dict) else {},
        "scanner_macro_chart_fit_score": float(facade._to_float((selected or {}).get("scanner_macro_chart_fit_score"), 0.5)) if isinstance(selected, dict) else 0.5,
        "scanner_macro_chart_fit_bias": float(facade._to_float((selected or {}).get("scanner_macro_chart_fit_bias"))) if isinstance(selected, dict) else 0.0,
        "scanner_macro_chart_fit_authority": str((selected or {}).get("scanner_macro_chart_fit_authority") or "") if isinstance(selected, dict) else "",
        "scanner_macro_chart_fit_components": dict((selected or {}).get("scanner_macro_chart_fit_components") or {}) if isinstance(selected, dict) else {},
        "expected_monitor_block_reason": str((selected or {}).get("expected_monitor_block_reason") or "") if isinstance(selected, dict) else "",
        "dominant_block_reason": str((selected or {}).get("dominant_block_reason") or compatibility_bias_context.get("dominant_block_reason") or "") if isinstance(selected, dict) else str(compatibility_bias_context.get("dominant_block_reason") or ""),
        "dominant_block_reason_ratio": float(facade._to_float((selected or {}).get("dominant_block_reason_ratio") or compatibility_bias_context.get("dominant_block_reason_ratio"))),
        "bias_scale": float(facade._to_float((selected or {}).get("bias_scale") or compatibility_bias_context.get("bias_scale"))),
        "soft_penalty": float(facade._to_float((selected or {}).get("soft_penalty"))) if isinstance(selected, dict) else 0.0,
        "compatibility_score_pre_penalty": float(facade._to_float((selected or {}).get("compatibility_score_pre_penalty"))) if isinstance(selected, dict) else 0.0,
        "compatibility_score_post_penalty": float(facade._to_float((selected or {}).get("compatibility_score_post_penalty"))) if isinstance(selected, dict) else 0.0,
        "compatibility_trace": dict((selected or {}).get("compatibility_trace") or {}) if isinstance(selected, dict) else {},
        "pre_adjust_score_total": float(facade._to_float((selected or {}).get("pre_adjust_score_total"))) if isinstance(selected, dict) else 0.0,
        "post_adjust_score_total": float(facade._to_float((selected or {}).get("post_adjust_score_total") or (selected or {}).get("score_total") or (selected or {}).get("score"))) if isinstance(selected, dict) else 0.0,
        "quote_data_diagnostic": dict(state.get("scanner_quote_diagnostic") or {}),
        "scanner_bias_applied": False,
        "scanner_bias_summary": dict(scanner_policy_trace.get("scanner_bias_summary") or {}),
        "scanner_memory_bias_applied": False,
        "scanner_memory_bias_summary": dict(scanner_policy_trace.get("scanner_memory_bias_summary") or {}),
        "candidate_bias_adjustments": [],
        "candidate_memory_bias_adjustments": [],
        "candidate_symbol_prior_adjustments": [],
        "selection_reason_with_bias": "",
        "shadow_used": bool(scanner_policy_trace.get("shadow_used")),
        "strategist_fallback_used": bool(scanner_policy_trace.get("strategist_fallback_used")),
        "policy_provenance": dict(policy_provenance),
        "policy_provenance_ref": dict(scanner_policy_trace.get("policy_provenance_ref") or {}),
        "applied_scanner_policy": dict(commander_scanner_policy),
        "score_adjustment_trace": list(score_adjustment_trace),
        "reentry_penalty_applied": bool(reentry_penalty_applied),
        "reentry_penalty_value": float(reentry_penalty_value),
        "diversification_applied": bool(diversification_applied),
        "diversification_bonus_value": float(diversification_bonus_value),
        "entry_bias_cap_applied": bool((selected or {}).get("entry_bias_cap_applied") if isinstance(selected, dict) else False),
        "market_representative_guard_enabled": bool(market_representative_guard_meta.get("enabled")),
        "market_representative_guard_applied": bool(market_representative_guard_meta.get("applied")),
        "market_representative_guard_policy": dict(market_representative_guard_meta.get("policy") or {}),
        "market_representative_guard_symbol": str(market_representative_guard_meta.get("symbol") or ""),
        "market_representative_guard_penalty": float(facade._to_float(market_representative_guard_meta.get("penalty"))),
        "market_representative_guard_score_gap": float(facade._to_float(market_representative_guard_meta.get("score_gap"))),
        "market_representative_guard_reason": str(
            market_representative_guard_meta.get("reason")
            or market_representative_guard_meta.get("skipped_reason")
            or ""
        ),
        "market_representative_guard_top_value_dominance": bool(market_representative_guard_meta.get("top_value_dominance")),
        "market_representative_guard_confirmation_sources": list(market_representative_guard_meta.get("confirmation_sources") or []),
        "market_representative_guard_before_top": list(market_representative_guard_meta.get("before_top") or []),
        "market_representative_guard_after_top": list(market_representative_guard_meta.get("after_top") or []),
        "raw_entry_compatibility_bias": float(
            facade._to_float((selected or {}).get("raw_entry_compatibility_bias")) if isinstance(selected, dict) else 0.0
        ),
        "effective_entry_compatibility_bias": float(
            facade._to_float((selected or {}).get("effective_entry_compatibility_bias")) if isinstance(selected, dict) else 0.0
        ),
        "adjusted_score_total": float(facade._to_float((selected or {}).get("score_total"))) if isinstance(selected, dict) else 0.0,
        "ranking_before_policy": ranking_before_policy,
        "ranking_after_policy": ranking_after_policy,
        "blocker_family_concentration_applied": bool(blocker_family_overlay_meta.get("applied")),
        "blocker_family_concentration_family": str(blocker_family_overlay_meta.get("family") or ""),
        "blocker_family_concentration_penalty": float(facade._to_float(blocker_family_overlay_meta.get("penalty"))),
        "blocker_family_concentration_candidate_count": int(blocker_family_overlay_meta.get("candidate_count") or 0),
        "blocker_family_concentration_top3_before": list(blocker_family_overlay_meta.get("top3_symbols_before") or []),
        "blocker_family_concentration_top3_after": list(blocker_family_overlay_meta.get("top3_symbols_after") or []),
        "blocker_family_concentration_alternative_symbols": list(blocker_family_overlay_meta.get("alternative_symbols") or []),
        "selection_vetoed": bool(blocker_family_overlay_meta.get("selection_vetoed")),
        "selection_veto_enforced": bool(selection_veto_enforced),
        "selection_veto_reason": str(blocker_family_overlay_meta.get("selection_veto_reason") or ""),
    }
    )


def scan_select_value_state_scanner_skill(fallback_reasons, skill_quotes, skill_order_counts, skill_order_rows, quote_meta, order_meta, *, facade):
    return (
{
        "contract_version": facade.SKILL_CONTRACT_VERSION,
        "used": bool(skill_quotes) or bool(skill_order_counts),
        "quote_symbols": len(skill_quotes),
        "account_open_order_symbols": len(skill_order_counts),
        "account_order_rows": int(skill_order_rows),
        "quote_present": bool(quote_meta.get("present")),
        "account_orders_present": bool(order_meta.get("present")),
        "fallback": bool(fallback_reasons),
        "fallback_reasons": fallback_reasons,
        "error_count": len(fallback_reasons),
    }
    )


def scan_select_commander_memory_application_trace_selec(selected, scanner_memory_bias, selected_symbol, candidate_memory_bias_adjustments, scanner_memory_bias_summary, scanner_memory_bias_applied, selection_summary, *, facade):
    selected_memory_bias_result = {
        "bias_adjustment": float(facade._to_float((selected or {}).get("memory_bias_adjustment"))) if isinstance(selected, dict) else 0.0,
        "observed_bias_adjustment": float(facade._to_float((selected or {}).get("memory_bias_observed_adjustment"))) if isinstance(selected, dict) else 0.0,
        "observation_only": bool((selected or {}).get("memory_bias_observation_only")) if isinstance(selected, dict) else False,
        "source_delta": float(facade._to_float((selected or {}).get("memory_bias_source_delta"))) if isinstance(selected, dict) else 0.0,
        "symbol_delta": float(facade._to_float((selected or {}).get("memory_bias_symbol_delta"))) if isinstance(selected, dict) else 0.0,
        "adjustments": list((selected or {}).get("memory_bias_adjustments") or []) if isinstance(selected, dict) else [],
    }
    commander_memory_application_trace = facade.build_scanner_commander_memory_application_trace(
        scanner_memory_bias=scanner_memory_bias,
        selected_symbol=selected_symbol,
        candidate_sources=(
            list(((selected or {}).get("candidate") or {}).get("sources") or [])
            if isinstance(selected, dict) and isinstance((selected or {}).get("candidate"), dict)
            else []
        ),
        selected_memory_bias_result=selected_memory_bias_result,
        candidate_memory_bias_adjustments=candidate_memory_bias_adjustments,
        scanner_memory_bias_summary=scanner_memory_bias_summary,
        scanner_memory_bias_applied=bool(scanner_memory_bias_applied),
    )
    selection_reason_with_bias = selection_summary
    return (commander_memory_application_trace, selection_reason_with_bias)


def scan_select_reasons_row_conf(row, selected_score, selected_confidence, selected_risk, runner_up_reasons, *, facade):
    if True:
            reasons: facade.List[str] = []
            row_score = float(facade._to_float(row.get("score_total") or row.get("score")))
            row_conf = float(facade._to_float(row.get("confidence")))
            row_risk = float(facade._to_float(row.get("risk_score")))
            if row_score < selected_score:
                reasons.append(f"lower total score ({row_score:.3f} vs {selected_score:.3f})")
            if row_conf < selected_confidence:
                reasons.append(f"lower confidence ({row_conf:.2f} vs {selected_confidence:.2f})")
            if row_risk > selected_risk:
                reasons.append(f"higher risk ({row_risk:.2f} vs {selected_risk:.2f})")
            if not reasons:
                reasons.append("lost on tie-break after score, confidence, and risk comparison")
            runner_up_reasons.append(
                {
                    "symbol": str(row.get("symbol") or ""),
                    "why_lost": reasons,
                }
            )
    return (reasons, row_conf, row_risk, row_score)
