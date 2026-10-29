from __future__ import annotations

from typing import Any, Dict, List


def _build_scanner_trace_summary(
    *,
    facade: Any,
    symbol: str,
    selected_rank: int,
    universe_size: int,
    selected_score_total: float,
    margin_vs_second: float,
    selected_score_breakdown: Dict[str, Any],
    selected: Dict[str, Any],
    candidate_preview: List[Dict[str, Any]],
    selection_summary: str,
    scanner_bias_applied: bool = False,
    scanner_bias_summary: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    selected_candidate = facade._dict(selected.get("candidate"))
    selected_sources = facade._listify(selected_candidate.get("sources"), limit=6, max_len=60)
    positive_factors = [f"{k}:{facade._safe_float(v, 0.0):.3f}" for k, v in selected_score_breakdown.items() if facade._safe_float(v, 0.0) > 0][:4]
    negative_factors = [f"{k}:{facade._safe_float(v, 0.0):.3f}" for k, v in selected_score_breakdown.items() if facade._safe_float(v, 0.0) < 0][:4]
    runner_ups = [
        {
            "symbol": str(row.get("symbol") or ""),
            "rank": facade._safe_int(row.get("rank")),
            "score_total": facade._safe_float(row.get("score_total")),
            "why": facade._clip(row.get("why"), max_len=160),
        }
        for row in candidate_preview[1:3]
        if isinstance(row, dict) and str(row.get("symbol") or "").strip()
    ]
    missing_flags: List[str] = []
    if not symbol:
        missing_flags.append("selected_symbol_missing")
    if universe_size <= 0:
        missing_flags.append("candidate_pool_missing")
    if not positive_factors and not negative_factors:
        missing_flags.append("score_breakdown_missing")
    bias_summary_dict = facade._dict(scanner_bias_summary)
    summary = (
        f"Scanner selected {symbol or 'not_captured'} rank #{selected_rank or 0}/{universe_size or 0} "
        f"with score={selected_score_total:.3f} and margin_vs_second={margin_vs_second:.3f}."
    )
    highlights = facade._dedupe_text(
        [
            f"Selected {symbol or 'not_captured'} rank #{selected_rank or 0} out of {universe_size or 0}",
            f"Score {selected_score_total:.3f} with margin {margin_vs_second:.3f} vs runner-up",
            f"Source mix: {', '.join(selected_sources) if selected_sources else 'not_captured'}",
            (
                "Positive factors: " + ", ".join(positive_factors)
                if positive_factors
                else "Positive factors were not captured"
            ),
            (
                "Negative factors: " + ", ".join(negative_factors)
                if negative_factors
                else "Negative factors were not captured"
            ),
            (
                "Bias: " + str(bias_summary_dict.get("summary") or "")
                if scanner_bias_applied and str(bias_summary_dict.get("summary") or "").strip()
                else ""
            ),
        ],
        limit=6,
        max_len=220,
    )
    return {
        "summary": facade._clip(selection_summary or summary, max_len=320),
        "highlights": highlights,
        "selected_symbol": symbol,
        "runner_up_symbol": str(runner_ups[0].get("symbol") or "") if runner_ups else "",
        "selected_rank": selected_rank,
        "universe_size": universe_size,
        "candidate_count": universe_size,
        "selected_score_total": selected_score_total,
        "margin_vs_second": margin_vs_second,
        "selected_sources": selected_sources,
        "critical_positive_factors": positive_factors,
        "critical_negative_factors": negative_factors,
        "top_candidates": candidate_preview[:3],
        "runner_ups": runner_ups,
        "scanner_bias_applied": bool(scanner_bias_applied),
        "scanner_bias_summary": bias_summary_dict,
        "missing_flags": missing_flags,
    }



def _build_scanner_candidate_ranking_table(
    *,
    facade: Any,
    state: Dict[str, Any],
    candidate_preview: List[Dict[str, Any]],
) -> Dict[str, Any]:
    event_payload = facade._dict(state.get("scanner_candidate_ranking_table"))
    if event_payload:
        rows = list(event_payload.get("rows") or [])
        return {
            "tie_break_rule": facade._clip(event_payload.get("tie_break_rule"), max_len=120),
            "rows": [dict(row) for row in rows if isinstance(row, dict)],
        }
    return {
        "tie_break_rule": "score_total desc -> confidence desc -> risk_score asc",
        "rows": [dict(row) for row in candidate_preview],
    }



def _build_scanner_candidate_selection_reason(
    *,
    facade: Any,
    state: Dict[str, Any],
    selected_symbol: str,
    selected_rank: int,
    selected_score_total: float,
    margin_vs_second: float,
    critical_positive_factors: List[str],
    critical_negative_factors: List[str],
    selection_summary: str,
    runner_ups: List[Dict[str, Any]],
    selected: Dict[str, Any],
) -> Dict[str, Any]:
    event_payload = facade._dict(state.get("scanner_candidate_selection_reason"))
    if event_payload:
        return dict(event_payload)
    selected_candidate = facade._dict(selected.get("candidate"))
    why_selected = facade._listify(selected.get("top_reasons"), limit=6, max_len=180)
    if not why_selected:
        why_selected = facade._dedupe_text(
            [
                f"highest total score ({selected_score_total:.3f})" if selected_score_total else "",
                f"confidence {facade._safe_float(selected.get('confidence')):.2f} and risk {facade._safe_float(selected.get('risk_score')):.2f}",
                f"source mix: {', '.join(facade._listify(selected_candidate.get('sources'), limit=4, max_len=40))}",
            ],
            limit=4,
            max_len=180,
        )
    return {
        "selected_symbol": selected_symbol,
        "selected_rank": selected_rank,
        "selected_score_total": selected_score_total,
        "margin_vs_second": margin_vs_second,
        "critical_positive_factors": list(critical_positive_factors),
        "critical_negative_factors": list(critical_negative_factors),
        "selection_summary": selection_summary,
        "why_selected": why_selected,
        "runner_ups_lost": list(runner_ups),
        "entry_compatibility_score": facade._safe_float(selected.get("entry_compatibility_score"), 0.0),
        "compatibility_bias": facade._safe_float(selected.get("compatibility_bias"), 0.0),
        "expected_monitor_block_reason": facade._clip(selected.get("expected_monitor_block_reason"), max_len=120),
        "compatibility_trace": facade._dict(selected.get("compatibility_trace")),
        "tie_break_rule": "score_total desc -> confidence desc -> risk_score asc",
        "final_decision_basis": "Scanner selected the highest-ranked candidate after strategist-guided weighting, source scoring, and risk penalties.",
    }



