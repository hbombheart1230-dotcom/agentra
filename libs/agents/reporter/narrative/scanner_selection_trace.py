"""Reporter story-scanner narrative owner (decomposed) (scanner_selection_trace; definitions copied verbatim from libs/reporting/trade_story_pipeline_scanner.py)."""
from __future__ import annotations
from typing import Any, Dict, List, Mapping


def _scanner_candidate_row_from_evidence(
    scanner_evidence: Mapping[str, Any] | None,
    *,
    selected_symbol: str,
) -> Dict[str, Any]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    symbol = str(selected_symbol or "").strip()
    if not symbol:
        return {}
    evidence = dict(scanner_evidence or {})
    for collection_name in ("candidate_ranking_tables", "selection_outputs"):
        for event in list(evidence.get(collection_name) or []):
            payload = event.get("payload") if isinstance(event, dict) and isinstance(event.get("payload"), dict) else {}
            rows: List[Any] = []
            if collection_name == "candidate_ranking_tables":
                rows = list(payload.get("rows") or [])
            else:
                rows = list(payload.get("ranking_top_n") or payload.get("scanner_top_candidates") or [])
                selected_candidate = payload.get("selected_candidate") if isinstance(payload.get("selected_candidate"), dict) else {}
                if selected_candidate:
                    rows.append(selected_candidate)
            for row in rows:
                if not isinstance(row, dict) or str(row.get("symbol") or "").strip() != symbol:
                    continue
                candidate = dict(row)
                score_breakdown = (
                    candidate.get("score_breakdown")
                    if isinstance(candidate.get("score_breakdown"), dict)
                    else {}
                )
                if not isinstance(candidate.get("sources"), list):
                    candidate["sources"] = _facade._candidate_sources_from_score_breakdown(score_breakdown)
                return candidate
    return {}


def _build_scanner_selection_trace(scanner_reason: Dict[str, Any], scanner_artifact: Dict[str, Any]) -> Dict[str, Any]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    reason = scanner_reason if isinstance(scanner_reason, dict) else {}
    artifact = scanner_artifact if isinstance(scanner_artifact, dict) else {}
    selected_symbol = str(
        reason.get("selected_symbol")
        or artifact.get("selected_symbol")
        or ""
    ).strip()
    selected_rank = _facade.safe_int(reason.get("selected_rank"), _facade.safe_int(artifact.get("selected_rank"), 0))
    ranked_candidates = [dict(row) for row in list(reason.get("top_candidates") or []) if isinstance(row, dict)]
    if not ranked_candidates:
        ranked_candidates = [dict(row) for row in list(artifact.get("ranked_candidates") or []) if isinstance(row, dict)]
    if not ranked_candidates:
        ranking_table = artifact.get("candidate_ranking_table") if isinstance(artifact.get("candidate_ranking_table"), dict) else {}
        ranked_candidates = [dict(row) for row in list(ranking_table.get("rows") or []) if isinstance(row, dict)]
    score_drivers = {}
    if isinstance(reason.get("score_breakdown"), dict):
        score_drivers = _facade._top_numeric_drivers(reason.get("score_breakdown"), limit=4)
    if not score_drivers:
        score_breakdown_by_symbol = artifact.get("score_breakdown_by_symbol") if isinstance(artifact.get("score_breakdown_by_symbol"), dict) else {}
        score_drivers = _facade._top_numeric_drivers(score_breakdown_by_symbol.get(selected_symbol), limit=4)
    selection_reason = (
        _facade.clip(reason.get("selection_basis"), max_len=260)
        or _facade.clip(reason.get("selection_reason_with_bias"), max_len=260)
        or _facade.clip(artifact.get("selection_reason_with_bias"), max_len=260)
        or _facade.clip(artifact.get("selection_reason"), max_len=260)
        or _facade.clip((artifact.get("candidate_selection_reason") or {}).get("selection_summary"), max_len=260)
        or _facade.clip(reason.get("summary"), max_len=260)
    )
    chart_feature_coverage = reason.get("feature_coverage") if isinstance(reason.get("feature_coverage"), dict) else {}
    scanner_chart_fit = reason.get("scanner_chart_fit") if isinstance(reason.get("scanner_chart_fit"), dict) else {}
    scanner_macro_chart_fit = (
        reason.get("scanner_macro_chart_fit")
        if isinstance(reason.get("scanner_macro_chart_fit"), dict)
        else {}
    )
    if not chart_feature_coverage:
        selected_row: Dict[str, Any] = {}
        for row in ranked_candidates:
            if str(row.get("symbol") or "").strip() == selected_symbol:
                selected_row = row
                break
        if not selected_row or not isinstance(selected_row.get("feature_coverage"), dict):
            ranking_table = artifact.get("candidate_ranking_table") if isinstance(artifact.get("candidate_ranking_table"), dict) else {}
            for row in list(ranking_table.get("rows") or []):
                if not isinstance(row, dict):
                    continue
                if str(row.get("symbol") or "").strip() == selected_symbol:
                    selected_row = dict(row)
                    break
        if isinstance(selected_row.get("feature_coverage"), dict):
            chart_feature_coverage = dict(selected_row.get("feature_coverage") or {})
        if not scanner_chart_fit:
            scanner_chart_fit = _facade._scanner_chart_fit_payload(selected_row)
        if not scanner_macro_chart_fit:
            scanner_macro_chart_fit = _facade._scanner_macro_chart_fit_payload(selected_row)
    if not scanner_chart_fit:
        scanner_chart_fit = _facade._scanner_chart_fit_payload(artifact)
    if not scanner_macro_chart_fit:
        scanner_macro_chart_fit = _facade._scanner_macro_chart_fit_payload(artifact)
    return {
        "ranked_candidates": ranked_candidates[:5],
        "selected_symbol": selected_symbol,
        "selected_rank": selected_rank,
        "selection_reason": selection_reason,
        "selected_symbol_score_drivers": score_drivers,
        "chart_feature_coverage": chart_feature_coverage,
        "scanner_chart_fit": scanner_chart_fit,
        "scanner_macro_chart_fit": scanner_macro_chart_fit,
    }
