"""Strategist LLM evaluation bool/row/tactic/quality projections (moved verbatim from strategist_llm_evaluation).

Helpers are resolved on ``facade`` (the strategist_llm_evaluation module) at call time; this module never imports it.
Pure functions; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence


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


def _result_pct(row: Mapping[str, Any], *, facade: Any) -> float:
    for key in ("truth_net_return_pct", "result_pct", "pnl_pct", "return_pct"):
        if row.get(key) not in (None, ""):
            return facade._float(row.get(key), 0.0)
    return 0.0


def _tactic(row: Mapping[str, Any], *, facade: Any) -> str:
    return facade._text(row.get("quant_tactic_id") or row.get("tactical_strategy"))


def _quality_label(*, rows: Sequence[Mapping[str, Any]], primary_tactic: str, shadow: Dict[str, Any], facade: Any) -> str:
    if not rows:
        return "insufficient_trade_samples"
    primary_rows = [row for row in rows if facade._tactic(row) == primary_tactic] if primary_tactic else []
    target_rows = primary_rows or rows
    losses = sum(1 for row in target_rows if facade._result_pct(row) < 0.0)
    avg_return = sum(facade._result_pct(row) for row in target_rows) / float(len(target_rows)) if target_rows else 0.0
    if len(target_rows) >= 3 and losses == len(target_rows) and avg_return <= -0.8:
        return "poor_lane_selection"
    if len(target_rows) >= 3 and avg_return < 0.0:
        return "weak_lane_selection"
    if len(target_rows) >= 3 and avg_return > 0.0:
        return "aligned_lane_selection"
    if int(shadow.get("opening_would_enter_count") or 0) > 0 and facade._shape_from_tactic(primary_tactic) in {"vwap_reclaim", "pullback"}:
        return "missed_opening_momentum_possible"
    return "review_sample_building"
