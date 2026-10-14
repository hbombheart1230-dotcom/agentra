"""Scanner output artifact: candidate pool, ranking and selection fields (key order unchanged).

T3.5 (P1.5 Third Pass): contiguous statement runs / dict item ranges of `libs/contracts/agent_outputs.py::build_scanner_output_artifact` moved verbatim into
contract-owned projection stages. Locals enter as explicit parameters and leave as the returned record or dict; value
helpers are imported from `libs.contracts.agent_output_values`; remaining module globals of the public facade are
resolved at use time as `facade.NAME`. Final artifact assembly and `validate_artifact` stay in the public builder.
"""
from __future__ import annotations

from libs.contracts.agent_output_values import (
    _clip,
    _dict,
    _dict_list,
    _safe_float,
    _safe_int,
)


def scanner_artifact_pool_ranking_fields(candidate_preview, candidate_ranking_table, candidate_selection_reason, pool_meta, ranked, scanner_output, selected_rank, selected_score_breakdown, selected_score_total, symbol):
    return {
            "candidate_pool_snapshot": {
                "candidate_source": _clip(pool_meta.get("candidate_source"), max_len=80),
                "scanner_candidate_source": _clip(pool_meta.get("scanner_candidate_source"), max_len=40),
                "scanner_policy_source": _clip(pool_meta.get("scanner_policy_source"), max_len=80),
                "scanner_fallback_mode": _clip(pool_meta.get("scanner_fallback_mode"), max_len=80),
                "scanner_strict_mode": bool(pool_meta.get("scanner_strict_mode")),
                "asset_universe_policy": _clip(scanner_output.get("asset_universe_policy") or pool_meta.get("asset_universe_policy"), max_len=80),
                "asset_universe_policy_source": _clip(scanner_output.get("asset_universe_policy_source") or pool_meta.get("asset_universe_policy_source"), max_len=80),
                "excluded_candidate_count_by_asset_policy": _safe_int(scanner_output.get("excluded_candidate_count_by_asset_policy") or pool_meta.get("asset_policy_excluded_count")),
                "excluded_candidates_by_asset_policy": _dict_list(scanner_output.get("excluded_candidates_by_asset_policy") or pool_meta.get("asset_policy_exclusions"), limit=20),
                "excluded_candidate_count_by_mock_broker_restricted": _safe_int(
                    scanner_output.get("excluded_candidate_count_by_mock_broker_restricted")
                    or pool_meta.get("mock_broker_restricted_excluded_count")
                ),
                "excluded_candidates_by_mock_broker_restricted": _dict_list(
                    scanner_output.get("excluded_candidates_by_mock_broker_restricted")
                    or pool_meta.get("mock_broker_restricted_exclusions"),
                    limit=20,
                ),
                "asset_detection_stats": _dict(scanner_output.get("asset_detection_stats") or pool_meta.get("asset_detection_stats")),
                "unknown_asset_candidate_count": _safe_int(scanner_output.get("unknown_asset_candidate_count") or pool_meta.get("unknown_asset_candidate_count")),
                "total_candidates_before_filter": _safe_int(scanner_output.get("total_candidates_before_filter") or pool_meta.get("total_candidates_before_filter")),
                "total_candidates_after_filter": _safe_int(scanner_output.get("total_candidates_after_filter") or pool_meta.get("total_candidates_after_filter")),
                "candidate_pool_before_filter": _safe_int(pool_meta.get("candidate_pool_before_filter")),
                "candidate_pool_after_filter": _safe_int(pool_meta.get("candidate_pool_after_filter") or len(ranked)),
                "source_mix": _dict(pool_meta.get("pool_source_mix")),
                "fallback_reason": _clip(pool_meta.get("fallback_reason"), max_len=160),
            },
            "filter_funnel": {
                "before": _safe_int(pool_meta.get("candidate_pool_before_filter")),
                "after": _safe_int(pool_meta.get("candidate_pool_after_filter") or len(ranked)),
                "excluded_by_asset_policy": _safe_int(scanner_output.get("excluded_candidate_count_by_asset_policy") or pool_meta.get("asset_policy_excluded_count")),
                "theme_filter_applied": bool(pool_meta.get("theme_filter_applied")),
                "avoid_filter_applied": bool(pool_meta.get("avoid_filter_applied")),
                "blocked_static_fallback": bool(pool_meta.get("blocked_static_fallback")),
                "strict_kiwoom_only": bool(pool_meta.get("strict_kiwoom_only")),
            },
            "universe_size": _safe_int(scanner_output.get("candidate_pool_size") or scanner_output.get("candidate_count")),
            "candidate_list_summary": {
                "candidate_source": _clip(scanner_output.get("candidate_source"), max_len=80),
                "scanner_candidate_source": _clip(scanner_output.get("scanner_candidate_source"), max_len=40),
                "scanner_policy_source": _clip(scanner_output.get("scanner_policy_source"), max_len=80),
                "scanner_fallback_mode": _clip(scanner_output.get("scanner_fallback_mode"), max_len=80),
                "scanner_strict_mode": bool(scanner_output.get("scanner_strict_mode")),
                "asset_universe_policy": _clip(scanner_output.get("asset_universe_policy"), max_len=80),
                "asset_universe_policy_source": _clip(scanner_output.get("asset_universe_policy_source"), max_len=80),
                "excluded_candidate_count_by_asset_policy": _safe_int(scanner_output.get("excluded_candidate_count_by_asset_policy")),
                "excluded_candidate_count_by_mock_broker_restricted": _safe_int(scanner_output.get("excluded_candidate_count_by_mock_broker_restricted")),
                "asset_detection_stats": _dict(scanner_output.get("asset_detection_stats")),
                "unknown_asset_candidate_count": _safe_int(scanner_output.get("unknown_asset_candidate_count")),
                "total_candidates_before_filter": _safe_int(scanner_output.get("total_candidates_before_filter")),
                "total_candidates_after_filter": _safe_int(scanner_output.get("total_candidates_after_filter")),
                "source_mix": _dict(scanner_output.get("source_mix")),
                "candidate_count": _safe_int(scanner_output.get("candidate_count")),
            },
            "candidate_ranking_table": candidate_ranking_table,
            "candidate_selection_reason": candidate_selection_reason,
            "ranking_table": candidate_preview,
            "ranked_candidates": candidate_preview,
            "selected_symbol": symbol,
            "selected_rank": selected_rank,
            "scanner_selected_symbol": symbol,
            "scanner_rank": selected_rank,
            "scanner_score_total": selected_score_total,
            "scanner_score_breakdown": selected_score_breakdown,
            "scanner_top_candidates": candidate_preview[:3]
    }


def scanner_artifact_policy_compatibility_fields(applied_policy_present, bias_scale, compatibility_bias, compatibility_components, compatibility_score_post_penalty, compatibility_score_pre_penalty, dominant_block_reason, dominant_block_reason_ratio, entry_compatibility_score, expected_monitor_block_reason, monitor_entry_policy_summary, playbook, policy_source, runner_up_symbol, soft_penalty):
    return {
            "runner_up_symbol": runner_up_symbol,
            "playbook": playbook,
            "policy_source": policy_source,
            "applied_policy_present": applied_policy_present,
            "monitor_entry_policy_summary": monitor_entry_policy_summary,
            "entry_compatibility_score": entry_compatibility_score,
            "compatibility_bias": compatibility_bias,
            "compatibility_components": compatibility_components,
            "expected_monitor_block_reason": expected_monitor_block_reason,
            "dominant_block_reason": dominant_block_reason,
            "dominant_block_reason_ratio": dominant_block_reason_ratio,
            "bias_scale": bias_scale,
            "soft_penalty": soft_penalty,
            "compatibility_score_pre_penalty": compatibility_score_pre_penalty,
            "compatibility_score_post_penalty": compatibility_score_post_penalty
    }


def scanner_artifact_bias_trace_fields(candidate_bias_adjustments, candidate_memory_bias_adjustments, commander_memory_application_trace, compatibility_trace, post_adjust_score_total, pre_adjust_score_total, scanner_bias_applied, scanner_bias_summary, scanner_memory_bias, scanner_memory_bias_applied, scanner_memory_bias_summary, scanner_output):
    return {
            "compatibility_trace": compatibility_trace,
            "pre_adjust_score_total": pre_adjust_score_total,
            "post_adjust_score_total": post_adjust_score_total,
            "scanner_bias_context": _dict(scanner_output.get("scanner_bias_context")),
            "scanner_bias_applied": scanner_bias_applied,
            "scanner_bias_summary": scanner_bias_summary,
            "scanner_memory_bias_applied": scanner_memory_bias_applied,
            "scanner_memory_bias": scanner_memory_bias,
            "scanner_memory_bias_summary": scanner_memory_bias_summary,
            "candidate_memory_bias_adjustments": candidate_memory_bias_adjustments,
            "commander_memory_application_trace": commander_memory_application_trace,
            "scanner_memory_application_trace": commander_memory_application_trace,
            "candidate_bias_adjustments": candidate_bias_adjustments
    }


def scanner_artifact_selection_trace_fields(confidence_by_symbol, fallback_reason, fallback_used, quote_data_diagnostic, ranking_rows, rejection_rows, risk_score_by_symbol, scanner_output, score_breakdown_by_symbol, selection_reason_detail, selection_reason_with_bias, selection_summary, state, trace_summary):
    return {
            "selection_reason_with_bias": selection_reason_with_bias,
            "selection_reason": selection_summary,
            "selection_reason_detail": selection_reason_detail,
            "score_breakdown_by_symbol": score_breakdown_by_symbol,
            "confidence_by_symbol": confidence_by_symbol,
            "risk_score_by_symbol": risk_score_by_symbol,
            "ranking_table_missing": not bool(ranking_rows),
            "fallback_used": bool(fallback_used),
            "fallback_reason": fallback_reason,
            "trace_summary": trace_summary,
            "rejection_summary": rejection_rows,
            "filter_feature_summary": {
                "feature_source": _clip(state.get("scanner_feature", {}).get("source") if isinstance(state.get("scanner_feature"), dict) else "", max_len=80),
                "feature_symbol_count": _safe_int(_dict(state.get("scanner_feature")).get("symbol_count")),
                "condition_search_status": _clip(scanner_output.get("condition_search_status"), max_len=80),
                "condition_search_reason": _clip(scanner_output.get("condition_search_reason"), max_len=160),
            },
            "quote_data_diagnostic": quote_data_diagnostic
    }


def scanner_artifact_policy_guard_fields(scanner_output):
    return {
            "applied_scanner_policy": _dict(scanner_output.get("applied_scanner_policy")),
            "score_adjustment_trace": list(scanner_output.get("score_adjustment_trace") or []),
            "reentry_penalty_applied": bool(scanner_output.get("reentry_penalty_applied")),
            "reentry_penalty_value": float(scanner_output.get("reentry_penalty_value") or 0.0),
            "diversification_applied": bool(scanner_output.get("diversification_applied")),
            "diversification_bonus_value": float(scanner_output.get("diversification_bonus_value") or 0.0),
            "entry_bias_cap_applied": bool(scanner_output.get("entry_bias_cap_applied")),
            "market_representative_guard_enabled": bool(scanner_output.get("market_representative_guard_enabled")),
            "market_representative_guard_applied": bool(scanner_output.get("market_representative_guard_applied")),
            "market_representative_guard_policy": _dict(scanner_output.get("market_representative_guard_policy")),
            "market_representative_guard_symbol": _clip(scanner_output.get("market_representative_guard_symbol"), max_len=16),
            "market_representative_guard_penalty": float(scanner_output.get("market_representative_guard_penalty") or 0.0),
            "market_representative_guard_score_gap": float(scanner_output.get("market_representative_guard_score_gap") or 0.0),
            "market_representative_guard_reason": _clip(scanner_output.get("market_representative_guard_reason"), max_len=200),
            "market_representative_guard_confirmation_sources": list(scanner_output.get("market_representative_guard_confirmation_sources") or []),
            "market_representative_guard_before_top": list(scanner_output.get("market_representative_guard_before_top") or []),
            "market_representative_guard_after_top": list(scanner_output.get("market_representative_guard_after_top") or [])
    }


def scanner_artifact_refs_preview_fields(candidate_preview, scanner_output, selected, selected_candidate, selected_features, symbol, top_ranked_symbols):
    return {
            "raw_entry_compatibility_bias": float(scanner_output.get("raw_entry_compatibility_bias") or 0.0),
            "effective_entry_compatibility_bias": float(scanner_output.get("effective_entry_compatibility_bias") or 0.0),
            "adjusted_score_total": float(scanner_output.get("adjusted_score_total") or 0.0),
            "ranking_before_policy": list(scanner_output.get("ranking_before_policy") or []),
            "ranking_after_policy": list(scanner_output.get("ranking_after_policy") or []),
            "scanner_policy_source": "commander",
            "scanner_policy_version": "1.0",
            "evidence_refs": {
                "event_names": [
                    "scanner.candidate_pool_snapshot",
                    "scanner.candidate_ranking_table",
                    "scanner.candidate_selection_reason",
                    "scanner.selection_output",
                ],
                "top_ranked_symbols": top_ranked_symbols,
            },
            "source_refs": {
                "scanner_source_policy": _dict(scanner_output.get("scanner_source_policy")),
                "strategist_playbook": _clip(scanner_output.get("strategist_playbook"), max_len=80),
            },
            # compatibility-rich fields for downstream readers
            "top_stock": scanner_output.get("top_stock"),
            "top_score": scanner_output.get("top_score"),
            "candidate_pool_after_filter": _safe_int(scanner_output.get("candidate_pool_size") or scanner_output.get("candidate_count")),
            "top_ranked_symbols": top_ranked_symbols,
            "selected_candidate": {
                "symbol": symbol,
                "why": _clip(selected.get("why"), max_len=180),
                "asset_class_detected": _clip(selected.get("asset_class_detected") or scanner_output.get("selected_asset_class_detected"), max_len=80),
                "detection_source": _clip(selected.get("detection_source") or scanner_output.get("selected_asset_detection_source"), max_len=40),
                "detection_field": _clip(selected.get("detection_field") or scanner_output.get("selected_asset_detection_field"), max_len=80),
                "sources": list(selected_candidate.get("sources") or [])[:8],
                "source_scores": _dict(selected_candidate.get("source_scores")),
                "score_total": _safe_float(selected.get("score_total") or selected.get("score")),
                "risk_score": _safe_float(selected.get("risk_score")),
                "confidence": _safe_float(selected.get("confidence")),
                "score_breakdown": _dict(selected.get("score_breakdown")),
                "component_snapshot": _dict(selected.get("components")),
                "feature_snapshot": {
                    "skill_quote_price": selected_features.get("skill_quote_price"),
                    "quote_volume": selected_features.get("quote_volume"),
                    "quote_trading_value": selected_features.get("quote_trading_value"),
                    "intraday_change_pct": selected_features.get("intraday_change_pct"),
                    "engine_trend_strength": selected_features.get("engine_trend_strength"),
                    "engine_volume_spike20": selected_features.get("engine_volume_spike20"),
                    "engine_volatility20": selected_features.get("engine_volatility20"),
                    "engine_vwap_distance": selected_features.get("engine_vwap_distance"),
                    "engine_sector_relative_strength": selected_features.get("engine_sector_relative_strength"),
                    "engine_cross_section_rank": selected_features.get("engine_cross_section_rank"),
                },
            },
            "candidate_preview": candidate_preview
    }
