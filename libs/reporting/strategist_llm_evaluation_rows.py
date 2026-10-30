"""Strategist LLM evaluation shape/row projections (moved verbatim from strategist_llm_evaluation).

Helpers are resolved on ``facade`` (the strategist_llm_evaluation module) at call time; this module never imports it.
Pure functions; no IO.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Mapping


def _shape_from_reason(reason: str, axis: str = "", *, facade: Any) -> str:
    reason = facade._text(reason)
    axis = facade._text(axis)
    if reason in {"pullback_not_mature", "pullback_below_vwap_reclaim_not_ready"} or axis == "pullback_structure":
        return "pullback"
    if reason == "below_vwap_reclaim_not_ready" or axis == "vwap_relationship":
        return "vwap_reclaim"
    if reason.startswith("breakout_") or axis == "breakout_readiness":
        return "breakout"
    if reason in {"volume_confirmation_missing", "volume_insufficient"} or axis == "volume_confirmation":
        return "volume_confirmation"
    return "other"


def _shape_from_tactic(tactic: str, *, facade: Any) -> str:
    tactic = facade._text(tactic)
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


def _closed_rows(rows: Iterable[Mapping[str, Any]], *, facade: Any) -> List[Dict[str, Any]]:
    return [dict(row) for row in rows if isinstance(row, facade.Mapping) and facade._row_closed(row)]


def _shadow_rows(payloads: Iterable[Mapping[str, Any]], *, facade: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for payload in payloads:
        if not isinstance(payload, facade.Mapping):
            continue
        for row in list(payload.get("candidates") or []):
            if isinstance(row, facade.Mapping):
                out.append(dict(row))
    return out
