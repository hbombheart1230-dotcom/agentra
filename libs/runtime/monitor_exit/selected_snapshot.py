from __future__ import annotations

from typing import Any, Dict

from graphs.nodes.skill_contracts import extract_market_quotes
from libs.core.symbols import normalize_symbol
from libs.runtime.feature_engine import build_feature_row
from libs.runtime.monitor_exit.numeric import to_float
from libs.runtime.monitor_exit.price_resolution import quote_observed_epoch, resolve_price_with_source


import sys as _monitor_view_sys
import libs.agents.monitor.projections.feature_context_views as _monitor_views

def feature_alias_map(feature_row: Dict[str, Any], *, quote: Dict[str, Any] | None=None) -> Dict[str, Any]:
    return _monitor_views.feature_alias_map(feature_row, quote=quote, facade=_monitor_view_sys.modules[__name__])


def feature_context_from_state(state: Dict[str, Any]) -> Dict[str, Any]:
    return _monitor_views.feature_context_from_state(state, facade=_monitor_view_sys.modules[__name__])


def feature_row_for_symbol(state: Dict[str, Any], symbol: str) -> tuple[Dict[str, Any], str]:
    sym = normalize_symbol(symbol)
    if not sym:
        return {}, "none"

    feature_engine = state.get("feature_engine") if isinstance(state.get("feature_engine"), dict) else {}
    by_symbol = feature_engine.get("by_symbol") if isinstance(feature_engine.get("by_symbol"), dict) else {}
    direct = by_symbol.get(sym)
    if isinstance(direct, dict) and direct:
        return dict(direct), "feature_engine.by_symbol"

    ohlcv_by_symbol = state.get("ohlcv_by_symbol") if isinstance(state.get("ohlcv_by_symbol"), dict) else {}
    rows = ohlcv_by_symbol.get(sym)
    if isinstance(rows, list) and rows:
        try:
            return build_feature_row(rows, **feature_context_from_state(state)), "ohlcv_by_symbol"
        except Exception:
            return {}, "ohlcv_build_failed"

    return {}, "none"


def prior_bar_low_for_symbol(state: Dict[str, Any], symbol: str) -> float | None:
    sym = normalize_symbol(symbol)
    if not sym:
        return None
    ohlcv_by_symbol = state.get("ohlcv_by_symbol") if isinstance(state.get("ohlcv_by_symbol"), dict) else {}
    rows = ohlcv_by_symbol.get(sym)
    if not isinstance(rows, list) or len(rows) < 2:
        return None
    prior = rows[-2] if isinstance(rows[-2], dict) else {}
    low = to_float(prior.get("low"))
    if low > 0.0:
        return float(low)
    return None


def monitor_selected_snapshot_for_symbol(
    state: Dict[str, Any],
    symbol: str,
    selected: Dict[str, Any] | None,
    *,
    position: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    sym = normalize_symbol(symbol)
    selected_symbol = normalize_symbol((selected or {}).get("symbol")) if isinstance(selected, dict) else ""
    selected_matches = bool(selected_symbol and selected_symbol == sym)
    base = dict(selected or {}) if selected_matches else {}
    base["symbol"] = sym

    quotes, _meta = extract_market_quotes(state)
    quote = quotes.get(sym) if isinstance(quotes.get(sym), dict) else {}

    price, price_source = resolve_price_with_source(state, sym, selected, position=position)
    if price is not None and to_float(price) > 0.0:
        base["price"] = float(price)

    features = base.get("features") if isinstance(base.get("features"), dict) else {}
    feature_source = "selected.features" if features else "none"
    if not features:
        feature_row, feature_source = feature_row_for_symbol(state, sym)
        if feature_row:
            features = feature_alias_map(feature_row, quote=quote)
    elif quote:
        enriched = dict(features)
        quote_alias = feature_alias_map({}, quote=quote)
        for key, value in quote_alias.items():
            if value in (None, ""):
                continue
            if key in {"skill_quote_price", "intraday_change_pct", "quote_volume", "quote_trading_value"}:
                enriched[key] = value
            elif enriched.get(key) in (None, ""):
                enriched[key] = value
        features = enriched

    if features:
        base["features"] = dict(features)
    base["_monitor_price_source"] = str(price_source)
    base["_monitor_quote_observed_epoch"] = quote_observed_epoch(quote)
    base["_monitor_feature_source"] = str(feature_source)
    prior_bar_low = prior_bar_low_for_symbol(state, sym)
    if prior_bar_low is not None and prior_bar_low > 0.0:
        base["_monitor_prior_bar_low"] = float(prior_bar_low)
    return base
