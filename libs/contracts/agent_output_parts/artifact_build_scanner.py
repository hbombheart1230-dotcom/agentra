from __future__ import annotations
from typing import Any, Dict, List


def build_scanner_output_artifact(state: Dict[str, Any], facade) -> Dict[str, Any]:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    scanner_output = _dict(state.get("scanner_output"))
    selected = _dict(state.get("selected"))
    selected_candidate = _dict(selected.get("candidate"))
    selected_features = _dict(selected.get("features"))
    ranked = [row for row in list(state.get("ranked_candidates") or []) if isinstance(row, dict)]
    candidate_visibility_limit = _scanner_candidate_visibility_limit(scanner_output)
    visible_ranked = ranked[:candidate_visibility_limit]
    top_ranked_symbols = [str(row.get("symbol") or "") for row in visible_ranked if str(row.get("symbol") or "").strip()]
    pool_meta = _dict(state.get("scanner_candidate_pool"))
    candidate_preview: List[Dict[str, Any]] = []
    for rank, row in enumerate(visible_ranked, start=1):
        compact_features, row_breakdown, row_sources = scanner_row_feature_sources(row=row, candidate_preview=candidate_preview, rank=rank)
    applied_policy_present, critical_negative_factors, critical_positive_factors, margin_vs_second, monitor_entry_policy_summary, playbook, policy_provenance_ref, policy_source, selected_rank, selected_score_breakdown, selected_score_total, selection_summary, symbol = scanner_applied_policy_evidence(selected=selected, scanner_output=scanner_output, top_ranked_symbols=top_ranked_symbols, ranked=ranked, state=state)
    rejection_rows = [row for row in list(state.get("scanner_runner_up_reasons") or []) if isinstance(row, dict)]
    bias_scale, candidate_bias_adjustments, candidate_memory_bias_adjustments, candidate_ranking_table, candidate_selection_reason, commander_memory_application_trace, compatibility_bias, compatibility_components, compatibility_score_post_penalty, compatibility_score_pre_penalty, compatibility_trace, dominant_block_reason, dominant_block_reason_ratio, entry_compatibility_score, expected_monitor_block_reason, pre_adjust_score_total, scanner_bias_applied, scanner_bias_summary, scanner_memory_bias, scanner_memory_bias_applied, scanner_memory_bias_summary, selection_reason_detail, selection_reason_with_bias, soft_penalty = scanner_policy_bias_evidence(symbol=symbol, selected_rank=selected_rank, selected_score_total=selected_score_total, margin_vs_second=margin_vs_second, critical_positive_factors=critical_positive_factors, critical_negative_factors=critical_negative_factors, selection_summary=selection_summary, state=state, candidate_preview=candidate_preview, rejection_rows=rejection_rows, selected=selected, scanner_output=scanner_output, policy_provenance_ref=policy_provenance_ref, candidate_visibility_limit=candidate_visibility_limit, selected_candidate=selected_candidate, facade=facade)
    post_adjust_score_total = _safe_float(
        scanner_output.get("post_adjust_score_total")
        if scanner_output.get("post_adjust_score_total") not in (None, "")
        else candidate_selection_reason.get("post_adjust_score_total"),
        selected_score_total,
    )
    quote_data_diagnostic = _dict(scanner_output.get("quote_data_diagnostic") or state.get("scanner_quote_diagnostic"))
    runner_up_symbol = ""
    ranking_rows = [row for row in list(candidate_ranking_table.get("rows") or []) if isinstance(row, dict)]
    if len(ranking_rows) > 1:
        runner_up_symbol = str(ranking_rows[1].get("symbol") or "").strip()
    score_breakdown_by_symbol = {
        str(row.get("symbol") or "").strip(): _dict(row.get("score_breakdown"))
        for row in ranking_rows
        if str(row.get("symbol") or "").strip()
    }
    confidence_by_symbol = {
        str(row.get("symbol") or "").strip(): row.get("confidence")
        for row in ranking_rows
        if str(row.get("symbol") or "").strip()
    }
    risk_score_by_symbol = {
        str(row.get("symbol") or "").strip(): row.get("risk_score")
        for row in ranking_rows
        if str(row.get("symbol") or "").strip()
    }
    fallback_reason = _clip(
        pool_meta.get("fallback_reason")
        or scanner_output.get("fallback_reason")
        or ("backfill_used" if bool(pool_meta.get("backfill_used")) else ""),
        max_len=180,
    )
    fallback_used = bool(fallback_reason)
    trace_summary = _build_scanner_trace_summary(
        symbol=symbol,
        selected_rank=selected_rank,
        universe_size=_safe_int(scanner_output.get("candidate_pool_size") or scanner_output.get("candidate_count")) or _safe_int(pool_meta.get("candidate_pool_after_filter") or len(ranked)),
        selected_score_total=selected_score_total,
        margin_vs_second=margin_vs_second,
        selected_score_breakdown=selected_score_breakdown,
        selected=selected,
        candidate_preview=candidate_preview,
        selection_summary=selection_summary,
        scanner_bias_applied=scanner_bias_applied,
        scanner_bias_summary=scanner_bias_summary,
    )
    artifact = _base_output(state, agent="scanner", symbol=symbol)
    artifact.update(
        {
            **scanner_artifact_pool_ranking_fields(candidate_preview=candidate_preview, candidate_ranking_table=candidate_ranking_table, candidate_selection_reason=candidate_selection_reason, pool_meta=pool_meta, ranked=ranked, scanner_output=scanner_output, selected_rank=selected_rank, selected_score_breakdown=selected_score_breakdown, selected_score_total=selected_score_total, symbol=symbol),
            **scanner_artifact_policy_compatibility_fields(applied_policy_present=applied_policy_present, bias_scale=bias_scale, compatibility_bias=compatibility_bias, compatibility_components=compatibility_components, compatibility_score_post_penalty=compatibility_score_post_penalty, compatibility_score_pre_penalty=compatibility_score_pre_penalty, dominant_block_reason=dominant_block_reason, dominant_block_reason_ratio=dominant_block_reason_ratio, entry_compatibility_score=entry_compatibility_score, expected_monitor_block_reason=expected_monitor_block_reason, monitor_entry_policy_summary=monitor_entry_policy_summary, playbook=playbook, policy_source=policy_source, runner_up_symbol=runner_up_symbol, soft_penalty=soft_penalty),
            **scanner_artifact_bias_trace_fields(candidate_bias_adjustments=candidate_bias_adjustments, candidate_memory_bias_adjustments=candidate_memory_bias_adjustments, commander_memory_application_trace=commander_memory_application_trace, compatibility_trace=compatibility_trace, post_adjust_score_total=post_adjust_score_total, pre_adjust_score_total=pre_adjust_score_total, scanner_bias_applied=scanner_bias_applied, scanner_bias_summary=scanner_bias_summary, scanner_memory_bias=scanner_memory_bias, scanner_memory_bias_applied=scanner_memory_bias_applied, scanner_memory_bias_summary=scanner_memory_bias_summary, scanner_output=scanner_output),
            **scanner_artifact_selection_trace_fields(confidence_by_symbol=confidence_by_symbol, fallback_reason=fallback_reason, fallback_used=fallback_used, quote_data_diagnostic=quote_data_diagnostic, ranking_rows=ranking_rows, rejection_rows=rejection_rows, risk_score_by_symbol=risk_score_by_symbol, scanner_output=scanner_output, score_breakdown_by_symbol=score_breakdown_by_symbol, selection_reason_detail=selection_reason_detail, selection_reason_with_bias=selection_reason_with_bias, selection_summary=selection_summary, state=state, trace_summary=trace_summary),
            **scanner_artifact_policy_guard_fields(scanner_output=scanner_output),
            **scanner_artifact_refs_preview_fields(candidate_preview=candidate_preview, scanner_output=scanner_output, selected=selected, selected_candidate=selected_candidate, selected_features=selected_features, symbol=symbol, top_ranked_symbols=top_ranked_symbols),
        }
    )
    artifact["validation"] = validate_artifact(artifact)
    return artifact
