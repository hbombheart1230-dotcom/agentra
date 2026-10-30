from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Mapping, Sequence

import sys as _p15_sys
from libs.reporting import strategist_llm_evaluation_projection as projection


def _text(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text.lower() in {"", "-", "none", "null", "unknown", "not_captured"} else text


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _row_closed(row: Mapping[str, Any]) -> bool:
    status = str(row.get("status") or row.get("last_status") or "").strip().lower()
    action = str(row.get("last_action") or row.get("action") or "").strip().upper()
    return bool(row.get("is_closed_trade") or row.get("is_realized_nonclosed_exit") or status == "closed" or action == "SELL")


def _result_pct(row: Mapping[str, Any]) -> float:
    for key in ("truth_net_return_pct", "result_pct", "pnl_pct", "return_pct"):
        if row.get(key) not in (None, ""):
            return _float(row.get(key), 0.0)
    return 0.0


def _tactic(row: Mapping[str, Any]) -> str:
    return _text(row.get("quant_tactic_id") or row.get("tactical_strategy"))


def _shape_from_reason(reason: str, axis: str = "") -> str:
    reason = _text(reason)
    axis = _text(axis)
    if reason in {"pullback_not_mature", "pullback_below_vwap_reclaim_not_ready"} or axis == "pullback_structure":
        return "pullback"
    if reason == "below_vwap_reclaim_not_ready" or axis == "vwap_relationship":
        return "vwap_reclaim"
    if reason.startswith("breakout_") or axis == "breakout_readiness":
        return "breakout"
    if reason in {"volume_confirmation_missing", "volume_insufficient"} or axis == "volume_confirmation":
        return "volume_confirmation"
    return "other"


def _shape_from_tactic(tactic: str) -> str:
    tactic = _text(tactic)
    if tactic in {"vwap_reclaim_pullback", "leader_vwap_reclaim_pullback", "theme_leader_pullback"}:
        return "vwap_reclaim"
    if tactic in {"opening_largecap_surge", "opening_gap_momentum"}:
        return "opening"
    if tactic in {"breakout_continuation", "opening_range_breakout"}:
        return "breakout"
    if tactic in {"lower_vwap_rebound_probe"}:
        return "lower_rebound"
    if tactic in {"defensive_observe"}:
        return "defensive"
    return tactic or "unavailable"


def _top_counter(counter: Counter[str], *, limit: int = 6) -> List[Dict[str, Any]]:
    return [{"name": name, "count": count} for name, count in counter.most_common(limit) if name]


def _closed_rows(rows: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return [dict(row) for row in rows if isinstance(row, Mapping) and _row_closed(row)]


def _shadow_rows(payloads: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for payload in payloads:
        if not isinstance(payload, Mapping):
            continue
        for row in list(payload.get("candidates") or []):
            if isinstance(row, Mapping):
                out.append(dict(row))
    return out


def _tactic_performance(rows: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return projection._tactic_performance(rows, facade=_p15_sys.modules[__name__])


def _shadow_shape_diagnostics(rows: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return projection._shadow_shape_diagnostics(rows, facade=_p15_sys.modules[__name__])


def _quality_label(*, rows: Sequence[Mapping[str, Any]], primary_tactic: str, shadow: Dict[str, Any]) -> str:
    if not rows:
        return "insufficient_trade_samples"
    primary_rows = [row for row in rows if _tactic(row) == primary_tactic] if primary_tactic else []
    target_rows = primary_rows or rows
    losses = sum(1 for row in target_rows if _result_pct(row) < 0.0)
    avg_return = sum(_result_pct(row) for row in target_rows) / float(len(target_rows)) if target_rows else 0.0
    if len(target_rows) >= 3 and losses == len(target_rows) and avg_return <= -0.8:
        return "poor_lane_selection"
    if len(target_rows) >= 3 and avg_return < 0.0:
        return "weak_lane_selection"
    if len(target_rows) >= 3 and avg_return > 0.0:
        return "aligned_lane_selection"
    if int(shadow.get("opening_would_enter_count") or 0) > 0 and _shape_from_tactic(primary_tactic) in {"vwap_reclaim", "pullback"}:
        return "missed_opening_momentum_possible"
    return "review_sample_building"


def build_strategist_llm_evaluation(
    rows: Iterable[Mapping[str, Any]],
    shadow_payloads: Iterable[Mapping[str, Any]] = (),
) -> Dict[str, Any]:
    closed = _closed_rows(rows)
    tactic_rows = _tactic_performance(closed)
    primary = str(tactic_rows[0]["name"]) if tactic_rows else ""
    shadow_rows = _shadow_rows(shadow_payloads)
    shadow_diag = _shadow_shape_diagnostics(shadow_rows)
    overused = ""
    if tactic_rows and int(tactic_rows[0].get("count") or 0) >= 3 and float(tactic_rows[0].get("avg_return_pct") or 0.0) < 0.0:
        overused = str(tactic_rows[0].get("name") or "")
    underused = ""
    would_shapes = list(shadow_diag.get("would_enter_by_shape") or [])
    if would_shapes:
        underused = str(would_shapes[0].get("name") or "")
    elif int(shadow_diag.get("opening_would_enter_count") or 0) > 0:
        underused = "opening"
    return {
        "schema_version": "strategist_llm_evaluation.v1",
        "behavior_effect": "evaluation_only",
        "closed_or_realized_sample_count": len(closed),
        "selected_primary_tactic": primary,
        "selected_primary_lane": _shape_from_tactic(primary),
        "tactic_performance": tactic_rows[:8],
        "shadow_shape_diagnostics": shadow_diag,
        "lane_selection_quality": _quality_label(rows=closed, primary_tactic=primary, shadow=shadow_diag),
        "overused_lane_or_tactic": overused,
        "underused_shadow_lane": underused,
        "call_effectiveness": {
            "status": "not_available",
            "reason": "strategist_llm_call_trace_not_linked_to_operator_summary",
        },
    }


def _format_perf(rows: Sequence[Mapping[str, Any]], *, limit: int = 3) -> str:
    parts: List[str] = []
    for row in list(rows)[:limit]:
        name = _text(row.get("name"))
        if not name:
            continue
        parts.append(
            f"{name} ({row.get('count')}, win {float(row.get('win_rate') or 0.0) * 100:.1f}%, avg {float(row.get('avg_return_pct') or 0.0):.2f}%)"
        )
    return ", ".join(parts) if parts else "none"


def render_strategist_llm_evaluation_lines(payload: Mapping[str, Any] | None) -> List[str]:
    evaluation = dict(payload or {})
    if not evaluation:
        return []
    shadow = evaluation.get("shadow_shape_diagnostics") if isinstance(evaluation.get("shadow_shape_diagnostics"), Mapping) else {}
    lines = [
        "",
        "## Strategist LLM Evaluation",
        "",
        "- Strategist lane quality: "
        f"`{evaluation.get('lane_selection_quality') or 'not_available'}` / "
        f"primary `{evaluation.get('selected_primary_tactic') or 'none'}` "
        f"({evaluation.get('selected_primary_lane') or 'unavailable'}) / "
        f"samples {evaluation.get('closed_or_realized_sample_count') or 0}",
        f"- Strategist tactic performance: {_format_perf(list(evaluation.get('tactic_performance') or []))}",
        "- Strategist shadow contrast: "
        f"candidates {shadow.get('candidate_count') or 0}, "
        f"opening would-enter {shadow.get('opening_would_enter_count') or 0}",
        f"- Strategist overused: {evaluation.get('overused_lane_or_tactic') or 'none'} / underused shadow lane: {evaluation.get('underused_shadow_lane') or 'none'}",
        "- Strategist call effectiveness: "
        f"{(evaluation.get('call_effectiveness') or {}).get('status') if isinstance(evaluation.get('call_effectiveness'), Mapping) else 'not_available'}",
    ]
    return lines
