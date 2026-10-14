"""Scanner event/trace payload value builders (the emit/log/append calls stay in the orchestrator).

T4-A (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/scanner_node.py::scanner_node` moved verbatim into a
scanner projection Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
Scanner node are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def build_source_universe_snapshot(candidates, full_strategist_control_eligibility, pool_meta, *, facade):
    return (
        {
        "schema_version": "q9_scanner_source_universe.v1",
        "behavior_effect": "evaluation_only",
        "candidate_count": len(candidates),
        "rows": [
            {
                "rank": index,
                "symbol": facade._norm_symbol(item.get("symbol")) if isinstance(item, dict) else facade._norm_symbol(item),
                "sources": list(item.get("sources") or [])[:8] if isinstance(item, dict) else [],
                "source_scores": dict(item.get("source_scores") or {}) if isinstance(item, dict) else {},
                "source_observations": dict(item.get("source_observations") or {}) if isinstance(item, dict) else {},
                "rank_score": facade._to_float(item.get("rank_score")) if isinstance(item, dict) else 0.0,
                "universe_score": facade._to_float(item.get("universe_score")) if isinstance(item, dict) else 0.0,
                "why": str(item.get("why") or "") if isinstance(item, dict) else "",
            }
            for index, item in enumerate(list(candidates)[:50], start=1)
            if (
                facade._norm_symbol(item.get("symbol"))
                if isinstance(item, dict)
                else facade._norm_symbol(item)
            )
        ],
        "candidate_source": str(pool_meta.get("candidate_source") or ""),
        "scanner_candidate_source": str(pool_meta.get("scanner_candidate_source") or ""),
        "full_strategist_control_eligibility": dict(full_strategist_control_eligibility),
        "limitation": (
            "Captured before Scanner asset/practical filters and score overlays; source inclusion "
            "may still reflect the current Strategist-provided source policy."
        ),
    }
    )

def build_scanner_ranking_event_payload(blocker_family_overlay_meta, market_representative_guard_meta, pool_meta, scan_results_sorted, selection_veto_enforced, *, facade):
    return (
        {
            "candidate_source": str(pool_meta.get("candidate_source") or ""),
            "candidate_pool_before_filter": int(pool_meta.get("candidate_pool_before_filter") or 0),
            "candidate_pool_after_filter": int(pool_meta.get("candidate_pool_after_filter") or len(scan_results_sorted)),
            "asset_universe_policy": str(pool_meta.get("asset_universe_policy") or ""),
            "asset_universe_policy_source": str(pool_meta.get("asset_universe_policy_source") or ""),
            "excluded_candidate_count_by_asset_policy": int(pool_meta.get("asset_policy_excluded_count") or 0),
            "excluded_symbols_by_asset_policy": list(pool_meta.get("asset_policy_excluded_symbols") or []),
            "asset_detection_stats": dict(pool_meta.get("asset_detection_stats") or {}),
            "unknown_asset_candidate_count": int(pool_meta.get("unknown_asset_candidate_count") or 0),
            "total_candidates_before_filter": int(pool_meta.get("total_candidates_before_filter") or 0),
            "total_candidates_after_filter": int(pool_meta.get("total_candidates_after_filter") or 0),
            "theme_filter_applied": bool(pool_meta.get("theme_filter_applied")),
            "market_native_bypass_count": int(pool_meta.get("market_native_bypass_count") or 0),
            "market_native_bypass_symbols": list(pool_meta.get("market_native_bypass_symbols") or []),
            "avoid_filter_applied": bool(pool_meta.get("avoid_filter_applied")),
            "avoid_filter_reason": str(pool_meta.get("avoid_filter_reason") or ""),
            "avoid_filter_fallback_used": bool(pool_meta.get("avoid_filter_fallback_used")),
            "source_mix": dict(pool_meta.get("pool_source_mix") or {}),
            "scanner_source_policy": dict(pool_meta.get("scanner_source_policy") or {}),
            "candidate_symbols": [str((row or {}).get("symbol") or "") for row in list(scan_results_sorted or [])[:10] if isinstance(row, dict)],
            "fallback_reason": str(pool_meta.get("fallback_reason") or ""),
            "backfill_used": bool(pool_meta.get("backfill_used")),
            "backfill_count": int(pool_meta.get("backfill_count") or 0),
            "scan_aggressiveness": float(facade._to_float(pool_meta.get("scan_aggressiveness"))),
            "strict_mode_relaxed_by_scan_aggressiveness": bool(pool_meta.get("strict_mode_relaxed_by_scan_aggressiveness")),
            "aggressive_source_expansion_used": bool(pool_meta.get("aggressive_source_expansion_used")),
            "aggressive_source_expansion_sources": list(pool_meta.get("aggressive_source_expansion_sources") or []),
            "market_representative_guard_applied": bool(market_representative_guard_meta.get("applied")),
            "market_representative_guard_symbol": str(market_representative_guard_meta.get("symbol") or ""),
            "market_representative_guard_reason": str(
                market_representative_guard_meta.get("reason")
                or market_representative_guard_meta.get("skipped_reason")
                or ""
            ),
            "blocker_family_concentration_applied": bool(blocker_family_overlay_meta.get("applied")),
            "blocker_family_concentration_family": str(blocker_family_overlay_meta.get("family") or ""),
            "selection_vetoed": bool(blocker_family_overlay_meta.get("selection_vetoed")),
            "selection_veto_enforced": bool(selection_veto_enforced),
            "selection_veto_reason": str(blocker_family_overlay_meta.get("selection_veto_reason") or ""),
        }
    )

def build_scanner_summary_payload(blocker_family_overlay_meta, market_representative_guard_meta, playbook, pool_meta, ranking_table, risk_tone, scan_results_sorted, scanner_bias, scanner_bias_applied, scanner_bias_summary, scanner_memory_bias_applied, scanner_memory_bias_summary, scanner_priority, selected, selected_rank, selected_score_total, selected_symbol, selection_veto_enforced, state, top_score, trade_aggressiveness, visible_ranked_candidates, *, facade):
    return (
        {
            "candidate_source": str(pool_meta.get("candidate_source") or ""),
            "candidate_pool_before_filter": int(pool_meta.get("candidate_pool_before_filter") or 0),
            "candidate_pool_after_filter": int(pool_meta.get("candidate_pool_after_filter") or len(scan_results_sorted)),
            "asset_universe_policy": str(pool_meta.get("asset_universe_policy") or ""),
            "asset_universe_policy_source": str(pool_meta.get("asset_universe_policy_source") or ""),
            "excluded_candidate_count_by_asset_policy": int(pool_meta.get("asset_policy_excluded_count") or 0),
            "asset_detection_stats": dict(pool_meta.get("asset_detection_stats") or {}),
            "unknown_asset_candidate_count": int(pool_meta.get("unknown_asset_candidate_count") or 0),
            "total_candidates_before_filter": int(pool_meta.get("total_candidates_before_filter") or 0),
            "total_candidates_after_filter": int(pool_meta.get("total_candidates_after_filter") or 0),
            "theme_filter_applied": bool(pool_meta.get("theme_filter_applied")),
            "fallback_reason": str(pool_meta.get("fallback_reason") or ""),
            "blocked_static_fallback": bool(pool_meta.get("blocked_static_fallback")),
            "strict_kiwoom_only": bool(pool_meta.get("strict_kiwoom_only")),
            "backfill_used": bool(pool_meta.get("backfill_used")),
            "backfill_count": int(pool_meta.get("backfill_count") or 0),
            "scan_aggressiveness": float(facade._to_float(pool_meta.get("scan_aggressiveness"))),
            "strict_mode_relaxed_by_scan_aggressiveness": bool(pool_meta.get("strict_mode_relaxed_by_scan_aggressiveness")),
            "aggressive_source_expansion_used": bool(pool_meta.get("aggressive_source_expansion_used")),
            "aggressive_source_expansion_sources": list(pool_meta.get("aggressive_source_expansion_sources") or []),
            "top_stock": state.get("top_stock"),
            "top_score": top_score,
            "scanner_selected_symbol": selected_symbol,
            "scanner_rank": int(selected_rank),
            "scanner_score_total": float(selected_score_total),
            "scanner_score_breakdown": dict((selected or {}).get("score_breakdown") or {}) if isinstance(selected, dict) else {},
            "scanner_top_candidates": ranking_table[:3],
            "top_ranked_symbols": [str(x.get("symbol") or "") for x in visible_ranked_candidates],
            "strategist_scanner_priority": list(scanner_priority),
            "strategist_scanner_source_policy": dict(pool_meta.get("scanner_source_policy") or {}),
            "condition_search_status": str(pool_meta.get("condition_search_status") or ""),
            "condition_search_source": str(pool_meta.get("condition_search_source") or ""),
            "condition_search_reason": str(pool_meta.get("condition_search_reason") or ""),
            "strategist_playbook": playbook or "",
            "strategist_scanner_bias": scanner_bias or "",
            "strategist_avoid_themes": list(pool_meta.get("avoid_themes") or []),
            "strategist_trade_aggressiveness": trade_aggressiveness or "",
            "strategist_risk_tone": risk_tone or "",
            "recent_scanner_selected_count": int(len(facade._scanner_recent_selection_history(state))),
            "scanner_bias_applied": bool(scanner_bias_applied),
            "scanner_bias_summary": dict(scanner_bias_summary),
            "scanner_memory_bias_applied": bool(scanner_memory_bias_applied),
            "scanner_memory_bias_summary": dict(scanner_memory_bias_summary),
            "market_representative_guard_applied": bool(market_representative_guard_meta.get("applied")),
            "market_representative_guard_symbol": str(market_representative_guard_meta.get("symbol") or ""),
            "market_representative_guard_reason": str(
                market_representative_guard_meta.get("reason")
                or market_representative_guard_meta.get("skipped_reason")
                or ""
            ),
            "blocker_family_concentration_applied": bool(blocker_family_overlay_meta.get("applied")),
            "blocker_family_concentration_family": str(blocker_family_overlay_meta.get("family") or ""),
            "selection_vetoed": bool(blocker_family_overlay_meta.get("selection_vetoed")),
            "selection_veto_enforced": bool(selection_veto_enforced),
            "selection_veto_reason": str(blocker_family_overlay_meta.get("selection_veto_reason") or ""),
        }
    )

def build_scanner_decision_trace_payload(blocker_family_overlay_meta, candidate_bias_adjustments, candidate_memory_bias_adjustments, commander_memory_application_trace, market_representative_guard_meta, playbook, pool_meta, scan_results_sorted, scanner_bias_applied, scanner_bias_summary, scanner_memory_bias, scanner_memory_bias_applied, scanner_memory_bias_summary, scanner_priority, selected, selection_reason_with_bias, selection_veto_enforced, state, top_candidates_summary, *, facade):
    return (
        {
            "playbook": playbook or "",
            "scanner_priority": list(scanner_priority),
            "scanner_bias_applied": bool(scanner_bias_applied),
            "scanner_bias_summary": dict(scanner_bias_summary),
            "scanner_memory_bias_applied": bool(scanner_memory_bias_applied),
            "scanner_memory_bias": dict(scanner_memory_bias),
            "scanner_memory_bias_summary": dict(scanner_memory_bias_summary),
            "commander_memory_application_trace": dict(commander_memory_application_trace),
            "scanner_memory_application_trace": dict(commander_memory_application_trace),
            "candidate_bias_adjustments": list(candidate_bias_adjustments),
            "candidate_memory_bias_adjustments": list(candidate_memory_bias_adjustments),
            "selection_reason_with_bias": selection_reason_with_bias,
            "candidate_source": str(pool_meta.get("candidate_source") or ""),
            "asset_universe_policy": str(pool_meta.get("asset_universe_policy") or ""),
            "excluded_candidate_count_by_asset_policy": int(pool_meta.get("asset_policy_excluded_count") or 0),
            "asset_detection_stats": dict(pool_meta.get("asset_detection_stats") or {}),
            "unknown_asset_candidate_count": int(pool_meta.get("unknown_asset_candidate_count") or 0),
            "kiwoom_pool_source_mix": dict(pool_meta.get("pool_source_mix") or {}),
            "condition_search_status": str(pool_meta.get("condition_search_status") or ""),
            "condition_search_source": str(pool_meta.get("condition_search_source") or ""),
            "condition_search_reason": str(pool_meta.get("condition_search_reason") or ""),
            "scanner_source_policy": dict(pool_meta.get("scanner_source_policy") or {}),
            "candidate_pool_size": int(len(scan_results_sorted)),
            "recent_scanner_selected_count": int(len(facade._scanner_recent_selection_history(state))),
            "top_candidates": top_candidates_summary,
            "selected_symbol": state.get("top_stock") or None,
            "aggressive_source_expansion_used": bool(pool_meta.get("aggressive_source_expansion_used")),
            "aggressive_source_expansion_sources": list(pool_meta.get("aggressive_source_expansion_sources") or []),
            "market_representative_guard_applied": bool(market_representative_guard_meta.get("applied")),
            "market_representative_guard_symbol": str(market_representative_guard_meta.get("symbol") or ""),
            "market_representative_guard_reason": str(
                market_representative_guard_meta.get("reason")
                or market_representative_guard_meta.get("skipped_reason")
                or ""
            ),
            "blocker_family_concentration_applied": bool(blocker_family_overlay_meta.get("applied")),
            "blocker_family_concentration_family": str(blocker_family_overlay_meta.get("family") or ""),
            "selection_vetoed": bool(blocker_family_overlay_meta.get("selection_vetoed")),
            "selection_veto_enforced": bool(selection_veto_enforced),
            "selection_veto_reason": str(blocker_family_overlay_meta.get("selection_veto_reason") or ""),
            "score_breakdown_summary": (
                dict(selected.get("score_breakdown") or {})
                if isinstance(selected, dict)
                else {}
            ),
            "selected_candidate": facade._compact_selected_snapshot(selected if isinstance(selected, dict) else None),
        }
    )
