"""Scanner selected / runner-up rank, margin, factor, bias and veto evidence projection (rank-1 and tie-break order are computed upstream and untouched).

T4-A (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/scanner_node.py::scanner_node` moved verbatim into a
scanner projection Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
Scanner node are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class ScannerSelectionEvidence(NamedTuple):
    """Result of `project_scanner_selection_evidence` (positional order = sorted output names)."""

    candidate_bias_adjustments: Any
    candidate_memory_bias_adjustments: Any
    candidate_symbol_prior_adjustments: Any
    commander_memory_application_trace: Any
    critical_negative_factors: Any
    critical_positive_factors: Any
    margin_vs_second: Any
    ranking_table: Any
    runner_up_reasons: Any
    scanner_bias_applied: Any
    scanner_bias_summary: Any
    scanner_memory_bias_applied: Any
    scanner_memory_bias_summary: Any
    selected_rank: Any
    selected_score_total: Any
    selected_snapshot: Any
    selected_symbol: Any
    selection_reason_with_bias: Any
    selection_summary: Any

def project_scanner_selection_evidence(blocker_family_overlay_meta, candidate_visibility_limit, scan_results_sorted, scanner_memory_bias, scanner_policy_trace, score_adjustment_trace, selected, selection_veto_enforced, *, facade):
    ranking_table = facade._ranking_table_rows(
        scan_results_sorted,
        max_rows=max(20, candidate_visibility_limit),
    )
    selected_snapshot = facade._compact_selected_snapshot(selected if isinstance(selected, dict) else None)
    selected_symbol = str((selected or {}).get("symbol") or "") if isinstance(selected, dict) else ""
    selected_rank = 0
    if selected_symbol:
        ranked_symbols = [str((row or {}).get("symbol") or "") for row in list(scan_results_sorted) if isinstance(row, dict)]
        if selected_symbol in ranked_symbols:
            selected_rank = int(ranked_symbols.index(selected_symbol) + 1)
    if isinstance(selected, dict) and selected_rank > 0:
        # 2026-09-04 Scanner rank plumbing fix: propagate the same canonical
        # rank that lands in scanner.json (via selected_rank above) onto the
        # state["selected"] candidate dict itself -- `selected` and
        # `state["selected"]` are the same object (state["selected"] =
        # selected was assigned earlier, by reference), so this mutation is
        # visible to every downstream reader of state["selected"], notably
        # libs/runtime/opening_rank1_controlled_probe.py::selected_rank(),
        # which checks a "scanner_rank" key with top priority. Purely
        # additive (new dict keys only); does not touch scoring, ranking,
        # or cascade logic.
        # 2026-09-05: direct assignment, not setdefault -- this value IS the
        # canonical truth freshly computed this cycle, so it must never be
        # shadowed by a stale/contaminated "scanner_rank" the candidate dict
        # happened to already carry (e.g. reused across cycles upstream).
        selected["scanner_rank"] = int(selected_rank)
        selected["scanner_rank_source"] = "canonical"
    selected_score_total = float(facade._to_float((selected or {}).get("score_total") or (selected or {}).get("score"))) if isinstance(selected, dict) else 0.0
    second_score_total = float(facade._to_float((scan_results_sorted[1] or {}).get("score_total") or (scan_results_sorted[1] or {}).get("score"))) if len(scan_results_sorted) > 1 and isinstance(scan_results_sorted[1], dict) else 0.0
    margin_vs_second = float(selected_score_total - second_score_total) if isinstance(selected, dict) else 0.0
    selected_score_breakdown = dict((selected or {}).get("score_breakdown") or {}) if isinstance(selected, dict) else {}
    critical_positive_factors = [f"{str(k)}:{float(facade._to_float(v)):.3f}" for k, v in selected_score_breakdown.items() if float(facade._to_float(v)) > 0][:4]
    critical_negative_factors = [f"{str(k)}:{float(facade._to_float(v)):.3f}" for k, v in selected_score_breakdown.items() if float(facade._to_float(v)) < 0][:4]
    selection_summary = str((selected or {}).get("why") or "").strip() if isinstance(selected, dict) else ""
    if bool(blocker_family_overlay_meta.get("selection_vetoed")):
        selection_summary = str(blocker_family_overlay_meta.get("selection_veto_reason") or "blocker_family_concentration_veto")
    scanner_bias_summary = dict(scanner_policy_trace.get("scanner_bias_summary") or {})
    scanner_memory_bias_summary = dict(scanner_policy_trace.get("scanner_memory_bias_summary") or {})
    candidate_bias_adjustments = [
        {
            "symbol": str(row.get("symbol") or ""),
            "bias_adjustment": float(facade._to_float(row.get("bias_adjustment"))),
            "bias_adjustments": list(row.get("bias_adjustments") or []),
        }
        for row in list(scan_results_sorted)[:candidate_visibility_limit]
        if isinstance(row, dict) and str(row.get("symbol") or "").strip()
    ]
    candidate_memory_bias_adjustments = [
        {
            "symbol": str(row.get("symbol") or ""),
            "memory_bias_adjustment": float(facade._to_float(row.get("memory_bias_adjustment"))),
            "memory_bias_observed_adjustment": float(facade._to_float(row.get("memory_bias_observed_adjustment"))),
            "memory_bias_observation_only": bool(row.get("memory_bias_observation_only")),
            "memory_bias_source_delta": float(facade._to_float(row.get("memory_bias_source_delta"))),
            "memory_bias_symbol_delta": float(facade._to_float(row.get("memory_bias_symbol_delta"))),
            "memory_bias_adjustments": list(row.get("memory_bias_adjustments") or []),
            "memory_bias_summary": dict(row.get("memory_bias_summary") or {}),
        }
        for row in list(scan_results_sorted)[:candidate_visibility_limit]
        if isinstance(row, dict) and str(row.get("symbol") or "").strip()
    ]
    candidate_symbol_prior_adjustments = [
        {
            "symbol": str(row.get("symbol") or ""),
            "symbol_prior_adjustment": float(facade._to_float(row.get("symbol_prior_adjustment"))),
            "symbol_prior_reasons": list(row.get("symbol_prior_reasons") or []),
            "symbol_prior_summary": dict(row.get("symbol_prior_summary") or {}),
        }
        for row in list(scan_results_sorted)[:candidate_visibility_limit]
        if isinstance(row, dict) and str(row.get("symbol") or "").strip()
    ]
    scanner_bias_applied = any(abs(float(facade._to_float(row.get("bias_adjustment")))) > 1e-9 for row in list(scan_results_sorted))
    scanner_memory_bias_applied = any(
        abs(float(facade._to_float(row.get("memory_bias_adjustment")))) > 1e-9 for row in list(scan_results_sorted)
    )
    commander_memory_application_trace, selection_reason_with_bias = facade.scan_select_commander_memory_application_trace_selec(selected=selected, scanner_memory_bias=scanner_memory_bias, selected_symbol=selected_symbol, candidate_memory_bias_adjustments=candidate_memory_bias_adjustments, scanner_memory_bias_summary=scanner_memory_bias_summary, scanner_memory_bias_applied=scanner_memory_bias_applied, selection_summary=selection_summary, facade=facade)
    if scanner_bias_applied:
        bias_text = str(scanner_bias_summary.get("summary") or "scanner_bias").strip() or "scanner_bias"
        selection_reason_with_bias = (
            f"{selection_summary} | bias: {bias_text}" if selection_summary else f"bias applied: {bias_text}"
        )
    if scanner_memory_bias_applied:
        memory_bias_text = "memory_bias=commander"
        selection_reason_with_bias = (
            f"{selection_reason_with_bias} | {memory_bias_text}"
            if selection_reason_with_bias
            else memory_bias_text
        )
    selected_compatibility_bias = float(facade._to_float((selected or {}).get("compatibility_bias"))) if isinstance(selected, dict) else 0.0
    selected_expected_block = str((selected or {}).get("expected_monitor_block_reason") or "") if isinstance(selected, dict) else ""
    if abs(selected_compatibility_bias) > 1e-9:
        compatibility_text = (
            f"compatibility_bias={selected_compatibility_bias:+.3f}"
            + (f", monitor_risk={selected_expected_block}" if selected_expected_block else "")
        )
        selection_reason_with_bias = (
            f"{selection_reason_with_bias} | {compatibility_text}"
            if selection_reason_with_bias
            else compatibility_text
        )
    if score_adjustment_trace:
        selection_reason_with_bias += f" | overlay: {', '.join(score_adjustment_trace)}"
    if bool(blocker_family_overlay_meta.get("selection_vetoed")):
        veto_text = (
            (
                "selection veto enforced due to blocker family concentration"
                if selection_veto_enforced
                else "selection veto observed but not enforced due to blocker family concentration"
            )
            + (
                f" ({str(blocker_family_overlay_meta.get('family') or '')})"
                if str(blocker_family_overlay_meta.get("family") or "").strip()
                else ""
            )
        )
        selection_reason_with_bias = (
            f"{selection_reason_with_bias} | {veto_text}"
            if selection_reason_with_bias
            else veto_text
        )
    runner_up_reasons: facade.List[facade.Dict[str, facade.Any]] = []
    if len(scan_results_sorted) > 1 and isinstance(selected, dict):
        selected_score = float(facade._to_float(selected.get("score_total") or selected.get("score")))
        selected_confidence = float(facade._to_float(selected.get("confidence")))
        selected_risk = float(facade._to_float(selected.get("risk_score")))
        for row in list(scan_results_sorted[1:3]):
            if not isinstance(row, dict):
                continue
            reasons, row_conf, row_risk, row_score = facade.scan_select_reasons_row_conf(row=row, selected_score=selected_score, selected_confidence=selected_confidence, selected_risk=selected_risk, runner_up_reasons=runner_up_reasons, facade=facade)
    return ScannerSelectionEvidence(candidate_bias_adjustments, candidate_memory_bias_adjustments, candidate_symbol_prior_adjustments, commander_memory_application_trace, critical_negative_factors, critical_positive_factors, margin_vs_second, ranking_table, runner_up_reasons, scanner_bias_applied, scanner_bias_summary, scanner_memory_bias_applied, scanner_memory_bias_summary, selected_rank, selected_score_total, selected_snapshot, selected_symbol, selection_reason_with_bias, selection_summary)

def build_ranked_candidate_rows(scan_results_sorted, *, facade):
    return (
        [
        {
            "symbol": str(r.get("symbol") or ""),
            "asset_class_detected": str(r.get("asset_class_detected") or ""),
            "detection_source": str(r.get("detection_source") or ""),
            "detection_field": str(r.get("detection_field") or ""),
            "score_total": float(r.get("score_total") if r.get("score_total") is not None else facade._to_float(r.get("score"))),
            "score_breakdown": dict(r.get("score_breakdown") or {}),
            "risk_score": float(facade._to_float(r.get("risk_score"))),
            "confidence": float(facade._to_float(r.get("confidence"))),
            "bias_adjustment": float(facade._to_float(r.get("bias_adjustment"))),
            "bias_adjustments": list(r.get("bias_adjustments") or []),
            "bias_summary": dict(r.get("bias_summary") or {}),
            "entry_compatibility_score": float(facade._to_float(r.get("entry_compatibility_score"))),
            "compatibility_bias": float(facade._to_float(r.get("compatibility_bias"))),
            "compatibility_components": dict(r.get("compatibility_components") or {}),
            "scanner_chart_fit_score": float(facade._to_float(r.get("scanner_chart_fit_score"))),
            "scanner_chart_fit_authority": str(r.get("scanner_chart_fit_authority") or ""),
            "scanner_chart_fit_components": dict(r.get("scanner_chart_fit_components") or {}),
            "scanner_macro_chart_fit_score": float(facade._to_float(r.get("scanner_macro_chart_fit_score"), 0.5)),
            "scanner_macro_chart_fit_bias": float(facade._to_float(r.get("scanner_macro_chart_fit_bias"))),
            "scanner_macro_chart_fit_authority": str(r.get("scanner_macro_chart_fit_authority") or ""),
            "scanner_macro_chart_fit_components": dict(r.get("scanner_macro_chart_fit_components") or {}),
            "expected_monitor_block_reason": str(r.get("expected_monitor_block_reason") or ""),
            "dominant_block_reason": str(r.get("dominant_block_reason") or ""),
            "dominant_block_reason_ratio": float(facade._to_float(r.get("dominant_block_reason_ratio"))),
            "blocker_families": list(facade._candidate_blocker_families(r)),
            "bias_scale": float(facade._to_float(r.get("bias_scale"))),
            "soft_penalty": float(facade._to_float(r.get("soft_penalty"))),
            "compatibility_score_pre_penalty": float(facade._to_float(r.get("compatibility_score_pre_penalty"))),
            "compatibility_score_post_penalty": float(facade._to_float(r.get("compatibility_score_post_penalty"))),
            "compatibility_trace": dict(r.get("compatibility_trace") or {}),
            "pre_adjust_score_total": float(facade._to_float(r.get("pre_adjust_score_total"))),
            "post_adjust_score_total": float(facade._to_float(r.get("post_adjust_score_total") or r.get("score_total") or r.get("score"))),
            "scanner_intrinsic_control_score_total": float(
                facade._to_float(r.get("scanner_intrinsic_control_score_total"))
            ),
            "market_representative_guard_applied": bool(r.get("market_representative_guard_applied")),
            "market_representative_guard_penalty": float(facade._to_float(r.get("market_representative_guard_penalty"))),
            "market_representative_guard_reason": str(r.get("market_representative_guard_reason") or ""),
            "market_representative_confirmation_sources": list(r.get("market_representative_confirmation_sources") or []),
        }
        for r in scan_results_sorted
        if isinstance(r, dict)
    ]
    )
