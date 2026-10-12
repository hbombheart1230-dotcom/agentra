"""Monitor entry signal evidence views (minute OHLCV meta, ETF deviation, signal trace and sizing inputs).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def entry_evidence_entry_features_entry_row_source(state, policy, symbol, selected, selected_features, *, facade):
    entry_rows = []
    minute_ohlcv_by_symbol, minute_ohlcv_meta = facade.extract_minute_ohlcv_by_symbol(state)
    entry_row_source = str((minute_ohlcv_meta or {}).get("source") or "")
    minute_fetch_meta = (
        dict(state.get("monitor_minute_ohlcv_fetch") or {})
        if isinstance(state.get("monitor_minute_ohlcv_fetch"), dict)
        else {}
    )
    entry_scoring_policy = facade._resolve_monitor_entry_scoring_config(state, policy)
    if symbol and isinstance(minute_ohlcv_by_symbol.get(symbol), list):
        entry_rows = list(minute_ohlcv_by_symbol.get(symbol) or [])
    quotes_for_entry, _quote_meta_for_entry = facade.extract_market_quotes(state)
    quote_for_entry = (
        quotes_for_entry.get(facade._norm_symbol(symbol))
        if isinstance(quotes_for_entry.get(facade._norm_symbol(symbol)), dict)
        else {}
    )
    deviation_signal = facade.extract_etf_deviation_signal(
        symbol=symbol,
        candidate=selected,
        features=selected_features,
        quote=quote_for_entry,
        state=state,
        asset_class_detected=selected_features.get("asset_class_detected") or selected.get("asset_class_detected"),
    )
    entry_features = dict(selected_features)
    if deviation_signal.get("etf_deviation_pct") is not None:
        entry_features["etf_deviation_pct"] = deviation_signal.get("etf_deviation_pct")
        entry_features["etf_deviation_source"] = deviation_signal.get("etf_deviation_source")
        entry_features["etf_deviation_available"] = bool(deviation_signal.get("available"))
    if deviation_signal.get("asset_class_detected"):
        entry_features["asset_class_detected"] = deviation_signal.get("asset_class_detected")
    entry_features["etf_deviation_entry_score"] = deviation_signal.get("entry_discount_score")
    entry_features["etf_deviation_premium_score"] = deviation_signal.get("exit_premium_score")
    return (entry_features, entry_row_source, entry_rows, entry_scoring_policy, minute_fetch_meta, minute_ohlcv_meta, quote_for_entry)
