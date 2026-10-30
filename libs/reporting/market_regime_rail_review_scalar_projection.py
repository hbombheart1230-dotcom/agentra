"""Market regime rail review scalar/indicator projections (moved verbatim from market_regime_rail_review).

``Mapping`` and helper functions are resolved on ``facade`` (the market_regime_rail_review module) at call time where used; this module never imports it.
Pure functions; no IO.
"""
from __future__ import annotations

from typing import Any, Mapping


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _indicator(snapshot: Mapping[str, Any], key: str, *, facade: Any) -> Mapping[str, Any]:
    macro = snapshot.get("macro_indicators") if isinstance(snapshot.get("macro_indicators"), facade.Mapping) else {}
    indicators = macro.get("indicators") if isinstance(macro.get("indicators"), facade.Mapping) else {}
    row = indicators.get(key) if isinstance(indicators.get(key), facade.Mapping) else {}
    return row


def _change_pct(snapshot: Mapping[str, Any], key: str, *, facade: Any) -> float:
    index_moves = snapshot.get("index_moves") if isinstance(snapshot.get("index_moves"), facade.Mapping) else {}
    move_key = f"{key}_pct"
    if move_key in index_moves:
        return facade._to_float(index_moves.get(move_key), 0.0)
    return facade._to_float(facade._indicator(snapshot, key).get("change_pct"), 0.0)
