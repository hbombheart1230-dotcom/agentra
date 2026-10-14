"""Scanner output artifact candidate row, applied-policy and bias evidence facts.

T3.5 (P1.5 Third Pass): contiguous statement runs / dict item ranges of `libs/contracts/agent_outputs.py::build_scanner_output_artifact` moved verbatim into
contract-owned projection stages. Locals enter as explicit parameters and leave as the returned record or dict; value
helpers are imported from `libs.contracts.agent_output_values`; remaining module globals of the public facade are
resolved at use time as `facade.NAME`. Final artifact assembly and `validate_artifact` stay in the public builder.
"""
from __future__ import annotations

from typing import Any, NamedTuple

from libs.contracts.agent_output_values import (
    _clip,
    _dict,
    _dict_list,
    _safe_float,
)


class ScannerRowFeatureSources(NamedTuple):
    """Result of `scanner_row_feature_sources` (positional order is the pre-T3.5 tuple order)."""

    compact_features: Any
    row_breakdown: Any
    row_sources: Any

class ScannerAppliedPolicyEvidence(NamedTuple):
    """Result of `scanner_applied_policy_evidence` (positional order is the pre-T3.5 tuple order)."""

    applied_policy_present: Any
    critical_negative_factors: Any
    critical_positive_factors: Any
    margin_vs_second: Any
    monitor_entry_policy_summary: Any
    playbook: Any
    policy_provenance_ref: Any
    policy_source: Any
    selected_rank: Any
    selected_score_breakdown: Any
    selected_score_total: Any
    selection_summary: Any
    symbol: Any

class ScannerPolicyBiasEvidence(NamedTuple):
    """Result of `scanner_policy_bias_evidence` (positional order is the pre-T3.5 tuple order)."""

    bias_scale: Any
    candidate_bias_adjustments: Any
    candidate_memory_bias_adjustments: Any
    candidate_ranking_table: Any
    candidate_selection_reason: Any
    commander_memory_application_trace: Any
    compatibility_bias: Any
    compatibility_components: Any
    compatibility_score_post_penalty: Any
    compatibility_score_pre_penalty: Any
    compatibility_trace: Any
    dominant_block_reason: Any
    dominant_block_reason_ratio: Any
    entry_compatibility_score: Any
    expected_monitor_block_reason: Any
    pre_adjust_score_total: Any
    scanner_bias_applied: Any
    scanner_bias_summary: Any
    scanner_memory_bias: Any
    scanner_memory_bias_applied: Any
    scanner_memory_bias_summary: Any
    selection_reason_detail: Any
    selection_reason_with_bias: Any
    soft_penalty: Any

def scanner_row_feature_sources(row, candidate_preview, rank):
    row_breakdown = _dict(row.get("score_breakdown"))
    row_sources = _dict((row.get("candidate") or {}).get("source_scores")) if isinstance(row.get("candidate"), dict) else {}
    compact_features = _dict((row.get("features") or row.get("feature_snapshot") or {}))
    candidate_preview.append(
        {
            "rank": rank,
            "symbol": str(row.get("symbol") or ""),
            "score_total": _safe_float(row.get("score_total") or row.get("score")),
            "score_breakdown": row_breakdown,
            "source_scores": row_sources,
            "risk_score": _safe_float(row.get("risk_score")),
            "confidence": _safe_float(row.get("confidence")),
            "theme_match": _safe_float(row.get("theme_match")),
            "feature_coverage": _safe_float(row.get("feature_coverage")),
            "status": _clip(row.get("status"), max_len=40) or "active",
            "market_representative_guard_applied": bool(row.get("market_representative_guard_applied")),
            "market_representative_guard_penalty": _safe_float(row.get("market_representative_guard_penalty"), 0.0),
            "market_representative_guard_reason": _clip(row.get("market_representative_guard_reason"), max_len=160),
            "asset_class_detected": _clip(row.get("asset_class_detected"), max_len=80),
            "detection_source": _clip(row.get("detection_source"), max_len=40),
            "excluded_by_asset_policy": bool(row.get("excluded_by_asset_policy")),
            "exclusion_reason": _clip(row.get("exclusion_reason"), max_len=160),
            "compact_feature_snapshot": {
                "engine_trend_strength": compact_features.get("engine_trend_strength"),
                "engine_volume_spike20": compact_features.get("engine_volume_spike20"),
                "engine_volatility20": compact_features.get("engine_volatility20"),
                "engine_vwap_distance": compact_features.get("engine_vwap_distance"),
                "intraday_change_pct": compact_features.get("intraday_change_pct"),
            },
            "why": _clip(row.get("why"), max_len=180),
        }
    )
    return ScannerRowFeatureSources(compact_features, row_breakdown, row_sources)


def scanner_applied_policy_evidence(selected, scanner_output, top_ranked_symbols, ranked, state):
    symbol = str(selected.get("symbol") or scanner_output.get("top_stock") or "").strip()
    selected_rank = int(top_ranked_symbols.index(symbol) + 1) if symbol in top_ranked_symbols else (1 if symbol else 0)
    selected_score_total = _safe_float(selected.get("score_total") if selected.get("score_total") is not None else selected.get("score"))
    second_score = _safe_float((ranked[1].get("score_total") if len(ranked) > 1 else None) if len(ranked) > 1 else None)
    margin_vs_second = (selected_score_total - second_score) if len(ranked) > 1 else selected_score_total
    selected_score_breakdown = _dict(selected.get("score_breakdown"))
    critical_positive_factors = [f"{k}:{_safe_float(v, 0.0):.3f}" for k, v in selected_score_breakdown.items() if _safe_float(v, 0.0) > 0][:4]
    critical_negative_factors = [f"{k}:{_safe_float(v, 0.0):.3f}" for k, v in selected_score_breakdown.items() if _safe_float(v, 0.0) < 0][:4]
    selection_summary = _clip(selected.get("why"), max_len=240) or _clip(scanner_output.get("selection_summary"), max_len=240)
    playbook = _clip(
        scanner_output.get("playbook")
        or scanner_output.get("strategist_playbook")
        or _dict(state.get("strategist_output")).get("playbook"),
        max_len=80,
    )
    policy_provenance_ref = _dict(scanner_output.get("policy_provenance_ref"))
    policy_source = _clip(
        scanner_output.get("policy_source")
        or policy_provenance_ref.get("policy_source")
        or _dict(scanner_output.get("policy_provenance")).get("applied_policy_source")
        or _dict(scanner_output.get("policy_provenance")).get("monitor_entry_policy_source"),
        max_len=120,
    )
    applied_policy_present = bool(
        scanner_output.get("applied_policy_present")
        if scanner_output.get("applied_policy_present") is not None
        else policy_provenance_ref.get("applied_policy_present")
    )
    monitor_entry_policy_summary = _dict(
        scanner_output.get("monitor_entry_policy_summary")
        or policy_provenance_ref.get("monitor_entry_policy_summary")
    )
    return ScannerAppliedPolicyEvidence(applied_policy_present, critical_negative_factors, critical_positive_factors, margin_vs_second, monitor_entry_policy_summary, playbook, policy_provenance_ref, policy_source, selected_rank, selected_score_breakdown, selected_score_total, selection_summary, symbol)


def scanner_policy_bias_evidence(symbol, selected_rank, selected_score_total, margin_vs_second, critical_positive_factors, critical_negative_factors, selection_summary, state, candidate_preview, rejection_rows, selected, scanner_output, policy_provenance_ref, candidate_visibility_limit, selected_candidate, *, facade):
    selection_reason_detail = {
        "selected_symbol": symbol,
        "selected_rank": selected_rank,
        "selected_score_total": selected_score_total,
        "margin_vs_second": margin_vs_second,
        "critical_positive_factors": critical_positive_factors,
        "critical_negative_factors": critical_negative_factors,
        "selection_summary": selection_summary,
    }
    candidate_ranking_table = facade._build_scanner_candidate_ranking_table(
        state=state,
        candidate_preview=candidate_preview,
    )
    candidate_selection_reason = facade._build_scanner_candidate_selection_reason(
        state=state,
        selected_symbol=symbol,
        selected_rank=selected_rank,
        selected_score_total=selected_score_total,
        margin_vs_second=margin_vs_second,
        critical_positive_factors=critical_positive_factors,
        critical_negative_factors=critical_negative_factors,
        selection_summary=selection_summary,
        runner_ups=rejection_rows,
        selected=selected,
    )
    scanner_bias_summary = _dict(
        scanner_output.get("scanner_bias_summary")
        or policy_provenance_ref.get("scanner_bias_summary")
        or candidate_selection_reason.get("scanner_bias_summary")
    )
    scanner_bias_applied = bool(
        scanner_output.get("scanner_bias_applied")
        if scanner_output.get("scanner_bias_applied") is not None
        else candidate_selection_reason.get("scanner_bias_applied")
    )
    candidate_bias_adjustments = _dict_list(
        scanner_output.get("candidate_bias_adjustments")
        or candidate_selection_reason.get("candidate_bias_adjustments"),
        limit=candidate_visibility_limit,
    )
    scanner_memory_bias = _dict(
        scanner_output.get("scanner_memory_bias")
        or candidate_selection_reason.get("scanner_memory_bias")
    )
    scanner_memory_bias_summary = _dict(
        scanner_output.get("scanner_memory_bias_summary")
        or candidate_selection_reason.get("scanner_memory_bias_summary")
    )
    scanner_memory_bias_applied = bool(
        scanner_output.get("scanner_memory_bias_applied")
        if scanner_output.get("scanner_memory_bias_applied") is not None
        else candidate_selection_reason.get("scanner_memory_bias_applied")
    )
    candidate_memory_bias_adjustments = _dict_list(
        scanner_output.get("candidate_memory_bias_adjustments")
        or candidate_selection_reason.get("candidate_memory_bias_adjustments"),
        limit=candidate_visibility_limit,
    )
    selected_memory_bias_result = {
        "bias_adjustment": selected.get("memory_bias_adjustment"),
        "source_delta": selected.get("memory_bias_source_delta"),
        "symbol_delta": selected.get("memory_bias_symbol_delta"),
        "adjustments": list(selected.get("memory_bias_adjustments") or []),
    }
    commander_memory_application_trace = _dict(
        scanner_output.get("commander_memory_application_trace")
        or scanner_output.get("scanner_memory_application_trace")
        or candidate_selection_reason.get("commander_memory_application_trace")
        or candidate_selection_reason.get("scanner_memory_application_trace")
    )
    if not commander_memory_application_trace:
        commander_memory_application_trace = facade.build_scanner_commander_memory_application_trace(
            scanner_memory_bias=scanner_memory_bias,
            selected_symbol=symbol,
            candidate_sources=list(selected_candidate.get("sources") or []),
            selected_memory_bias_result=selected_memory_bias_result,
            candidate_memory_bias_adjustments=candidate_memory_bias_adjustments,
            scanner_memory_bias_summary=scanner_memory_bias_summary,
            scanner_memory_bias_applied=bool(scanner_memory_bias_applied),
        )
    selection_reason_with_bias = _clip(
        scanner_output.get("selection_reason_with_bias")
        or candidate_selection_reason.get("selection_reason_with_bias")
        or selection_summary,
        max_len=320,
    )
    entry_compatibility_score = _safe_float(
        scanner_output.get("entry_compatibility_score")
        if scanner_output.get("entry_compatibility_score") not in (None, "")
        else candidate_selection_reason.get("entry_compatibility_score"),
        0.0,
    )
    compatibility_bias = _safe_float(
        scanner_output.get("compatibility_bias")
        if scanner_output.get("compatibility_bias") not in (None, "")
        else candidate_selection_reason.get("compatibility_bias"),
        0.0,
    )
    expected_monitor_block_reason = _clip(
        scanner_output.get("expected_monitor_block_reason")
        or candidate_selection_reason.get("expected_monitor_block_reason"),
        max_len=120,
    )
    dominant_block_reason = _clip(
        scanner_output.get("dominant_block_reason")
        or candidate_selection_reason.get("dominant_block_reason"),
        max_len=120,
    )
    dominant_block_reason_ratio = _safe_float(
        scanner_output.get("dominant_block_reason_ratio")
        if scanner_output.get("dominant_block_reason_ratio") not in (None, "")
        else candidate_selection_reason.get("dominant_block_reason_ratio"),
        0.0,
    )
    bias_scale = _safe_float(
        scanner_output.get("bias_scale")
        if scanner_output.get("bias_scale") not in (None, "")
        else candidate_selection_reason.get("bias_scale"),
        0.0,
    )
    soft_penalty = _safe_float(
        scanner_output.get("soft_penalty")
        if scanner_output.get("soft_penalty") not in (None, "")
        else candidate_selection_reason.get("soft_penalty"),
        0.0,
    )
    compatibility_score_pre_penalty = _safe_float(
        scanner_output.get("compatibility_score_pre_penalty")
        if scanner_output.get("compatibility_score_pre_penalty") not in (None, "")
        else candidate_selection_reason.get("compatibility_score_pre_penalty"),
        entry_compatibility_score,
    )
    compatibility_score_post_penalty = _safe_float(
        scanner_output.get("compatibility_score_post_penalty")
        if scanner_output.get("compatibility_score_post_penalty") not in (None, "")
        else candidate_selection_reason.get("compatibility_score_post_penalty"),
        entry_compatibility_score,
    )
    compatibility_trace = _dict(
        scanner_output.get("compatibility_trace")
        or candidate_selection_reason.get("compatibility_trace")
    )
    compatibility_components = _dict(
        scanner_output.get("compatibility_components")
        or candidate_selection_reason.get("compatibility_components")
        or compatibility_trace.get("compatibility_components")
    )
    pre_adjust_score_total = _safe_float(
        scanner_output.get("pre_adjust_score_total")
        if scanner_output.get("pre_adjust_score_total") not in (None, "")
        else candidate_selection_reason.get("pre_adjust_score_total"),
        selected_score_total,
    )
    return ScannerPolicyBiasEvidence(bias_scale, candidate_bias_adjustments, candidate_memory_bias_adjustments, candidate_ranking_table, candidate_selection_reason, commander_memory_application_trace, compatibility_bias, compatibility_components, compatibility_score_post_penalty, compatibility_score_pre_penalty, compatibility_trace, dominant_block_reason, dominant_block_reason_ratio, entry_compatibility_score, expected_monitor_block_reason, pre_adjust_score_total, scanner_bias_applied, scanner_bias_summary, scanner_memory_bias, scanner_memory_bias_applied, scanner_memory_bias_summary, selection_reason_detail, selection_reason_with_bias, soft_penalty)
