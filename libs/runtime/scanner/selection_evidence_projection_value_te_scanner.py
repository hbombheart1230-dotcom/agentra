"""Scanner selected/scan-output and rank-evidence projections (state-write order stays in the node; canonical ranking owner untouched).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/scanner_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def scan_select_value_te_scanner_selection_reason(selected_symbol, selection_summary, selection_reason_with_bias, selected_rank, selected_score_total, margin_vs_second, critical_positive_factors, critical_negative_factors, selection_veto_enforced, scanner_bias_applied, scanner_bias_summary, scanner_memory_bias_applied, scanner_memory_bias, scanner_memory_bias_summary, commander_memory_application_trace, candidate_bias_adjustments, candidate_memory_bias_adjustments, candidate_symbol_prior_adjustments, playbook, selected, scanner_policy_trace, market_representative_guard_meta, blocker_family_overlay_meta, compatibility_bias_context, *, facade):
    return (
{
        "selected_symbol": selected_symbol,
        "selected_rank": int(selected_rank),
        "selected_score_total": float(selected_score_total),
        "margin_vs_second": float(margin_vs_second),
        "critical_positive_factors": list(critical_positive_factors),
        "critical_negative_factors": list(critical_negative_factors),
        "selection_summary": selection_summary,
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
        "scanner_macro_chart_fit_score": float(facade._to_float((selected or {}).get("scanner_macro_chart_fit_score"), 0.5)) if isinstance(selected, dict) else 0.5,
        "scanner_macro_chart_fit_bias": float(facade._to_float((selected or {}).get("scanner_macro_chart_fit_bias"))) if isinstance(selected, dict) else 0.0,
        "scanner_macro_chart_fit_authority": str((selected or {}).get("scanner_macro_chart_fit_authority") or "") if isinstance(selected, dict) else "",
        "scanner_macro_chart_fit_components": dict((selected or {}).get("scanner_macro_chart_fit_components") or {}) if isinstance(selected, dict) else {},
        "expected_monitor_block_reason": str((selected or {}).get("expected_monitor_block_reason") or "") if isinstance(selected, dict) else "",
        "dominant_block_reason": str((selected or {}).get("dominant_block_reason") or compatibility_bias_context.get("dominant_block_reason") or "") if isinstance(selected, dict) else str(compatibility_bias_context.get("dominant_block_reason") or ""),
        "dominant_block_reason_ratio": float(facade._to_float((selected or {}).get("dominant_block_reason_ratio") or compatibility_bias_context.get("dominant_block_reason_ratio"))),
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
        "blocker_family_concentration_applied": bool(blocker_family_overlay_meta.get("applied")),
        "blocker_family_concentration_family": str(blocker_family_overlay_meta.get("family") or ""),
        "blocker_family_concentration_penalty": float(facade._to_float(blocker_family_overlay_meta.get("penalty"))),
        "blocker_family_concentration_top3_before": list(blocker_family_overlay_meta.get("top3_symbols_before") or []),
        "blocker_family_concentration_top3_after": list(blocker_family_overlay_meta.get("top3_symbols_after") or []),
        "blocker_family_concentration_alternative_symbols": list(blocker_family_overlay_meta.get("alternative_symbols") or []),
        "selection_vetoed": bool(blocker_family_overlay_meta.get("selection_vetoed")),
        "selection_veto_enforced": bool(selection_veto_enforced),
        "selection_veto_reason": str(blocker_family_overlay_meta.get("selection_veto_reason") or ""),
        "bias_scale": float(facade._to_float((selected or {}).get("bias_scale") or compatibility_bias_context.get("bias_scale"))),
        "soft_penalty": float(facade._to_float((selected or {}).get("soft_penalty"))) if isinstance(selected, dict) else 0.0,
        "compatibility_score_pre_penalty": float(facade._to_float((selected or {}).get("compatibility_score_pre_penalty"))) if isinstance(selected, dict) else 0.0,
        "compatibility_score_post_penalty": float(facade._to_float((selected or {}).get("compatibility_score_post_penalty"))) if isinstance(selected, dict) else 0.0,
        "compatibility_trace": dict((selected or {}).get("compatibility_trace") or {}) if isinstance(selected, dict) else {},
        "pre_adjust_score_total": float(facade._to_float((selected or {}).get("pre_adjust_score_total"))) if isinstance(selected, dict) else 0.0,
        "post_adjust_score_total": float(facade._to_float((selected or {}).get("post_adjust_score_total") or (selected or {}).get("score_total") or (selected or {}).get("score"))) if isinstance(selected, dict) else 0.0,
        "scanner_bias_applied": bool(scanner_bias_applied),
        "scanner_bias_summary": dict(scanner_bias_summary),
        "scanner_memory_bias_applied": bool(scanner_memory_bias_applied),
        "scanner_memory_bias": dict(scanner_memory_bias),
        "scanner_memory_bias_summary": dict(scanner_memory_bias_summary),
        "commander_memory_application_trace": dict(commander_memory_application_trace),
        "scanner_memory_application_trace": dict(commander_memory_application_trace),
        "candidate_bias_adjustments": list(candidate_bias_adjustments),
        "candidate_memory_bias_adjustments": list(candidate_memory_bias_adjustments),
        "candidate_symbol_prior_adjustments": list(candidate_symbol_prior_adjustments),
        "selection_reason_with_bias": selection_reason_with_bias,
        "shadow_used": bool(scanner_policy_trace.get("shadow_used")),
        "strategist_fallback_used": bool(scanner_policy_trace.get("strategist_fallback_used")),
        "policy_provenance_ref": dict(scanner_policy_trace.get("policy_provenance_ref") or {}),
        "selected_asset_class_detected": str((selected or {}).get("asset_class_detected") or "") if isinstance(selected, dict) else "",
        "selected_asset_detection_source": str((selected or {}).get("detection_source") or "") if isinstance(selected, dict) else "",
        "selected_asset_detection_field": str((selected or {}).get("detection_field") or "") if isinstance(selected, dict) else "",
    }
    )


def scan_select_candidate_selection_reason_payload(selected_symbol, selected_rank, selected_score_total, margin_vs_second, critical_positive_factors, critical_negative_factors, selection_summary, scanner_policy_trace, playbook, compatibility_bias_context, market_representative_guard_meta, blocker_family_overlay_meta, selection_veto_enforced, scanner_bias_applied, scanner_memory_bias_applied, scanner_memory_bias, commander_memory_application_trace, candidate_bias_adjustments, candidate_memory_bias_adjustments, candidate_symbol_prior_adjustments, selection_reason_with_bias, runner_up_reasons, selected, *, facade):
    candidate_selection_reason_payload = facade._build_candidate_selection_reason_payload(
        selected=selected if isinstance(selected, dict) else None,
        selected_symbol=selected_symbol,
        selected_rank=selected_rank,
        selected_score_total=selected_score_total,
        margin_vs_second=margin_vs_second,
        critical_positive_factors=critical_positive_factors,
        critical_negative_factors=critical_negative_factors,
        selection_summary=selection_summary,
        scanner_policy_trace=scanner_policy_trace,
        playbook=playbook,
        compatibility_bias_context=compatibility_bias_context,
        market_representative_guard_meta=market_representative_guard_meta,
        blocker_family_overlay_meta=blocker_family_overlay_meta,
        selection_veto_enforced=selection_veto_enforced,
        scanner_bias_applied=scanner_bias_applied,
        scanner_memory_bias_applied=scanner_memory_bias_applied,
        scanner_memory_bias=scanner_memory_bias,
        commander_memory_application_trace=commander_memory_application_trace,
        candidate_bias_adjustments=candidate_bias_adjustments,
        candidate_memory_bias_adjustments=candidate_memory_bias_adjustments,
        candidate_symbol_prior_adjustments=candidate_symbol_prior_adjustments,
        selection_reason_with_bias=selection_reason_with_bias,
        runner_up_reasons=runner_up_reasons,
    )
    return (candidate_selection_reason_payload,)
