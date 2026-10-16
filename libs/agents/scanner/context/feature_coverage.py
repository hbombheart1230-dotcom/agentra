"""Scanner quote-metric coverage summary and feature refresh decision (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _summarize_quote_metric_coverage_r3_impl(candidates, *, skill_quotes, state, facade):
    live_equity_candidates = 0
    quote_rows_present = 0
    quote_rows_with_price = 0
    quote_rows_with_activity = 0
    zero_quote_metric_symbols: List[str] = []

    for item in list(candidates or []):
        symbol = facade._norm_symbol(item.get("symbol") if isinstance(item, dict) else item)
        if not facade._is_live_equity_symbol(symbol):
            continue
        live_equity_candidates += 1
        quote = skill_quotes.get(symbol) if isinstance(skill_quotes.get(symbol), dict) else {}
        if quote:
            quote_rows_present += 1
            if facade._to_float(quote.get("price") or quote.get("cur")) > 0.0:
                quote_rows_with_price += 1
        metrics = facade._candidate_quote_metrics(symbol, skill_quotes=skill_quotes, state=state)
        if (
            facade._to_float(metrics.get("volume")) > 0.0
            or facade._to_float(metrics.get("trading_value")) > 0.0
            or abs(facade._to_float(metrics.get("change_pct"))) > 1e-9
        ):
            quote_rows_with_activity += 1
        else:
            zero_quote_metric_symbols.append(symbol)

    return {
        "live_equity_candidates": int(live_equity_candidates),
        "quote_rows_present": int(quote_rows_present),
        "quote_rows_with_price": int(quote_rows_with_price),
        "quote_rows_with_activity": int(quote_rows_with_activity),
        "zero_quote_metric_symbols": list(zero_quote_metric_symbols)[:10],
    }


def _should_refresh_scanner_features_r3_impl(*, state, candidates, quote_metric_coverage, facade):
    live_equity_candidates = facade._to_int(quote_metric_coverage.get("live_equity_candidates"), 0)
    if live_equity_candidates <= 0:
        return False, ""
    if facade._to_int(quote_metric_coverage.get("quote_rows_with_activity"), 0) > 0:
        return False, ""

    fe_root = state.get("feature_engine") if isinstance(state.get("feature_engine"), dict) else {}
    fe_by_symbol = fe_root.get("by_symbol") if isinstance(fe_root.get("by_symbol"), dict) else {}
    if not isinstance(fe_by_symbol, dict) or not fe_by_symbol:
        return False, ""

    stale_symbols: List[str] = []
    for item in list(candidates or []):
        symbol = facade._norm_symbol(item.get("symbol") if isinstance(item, dict) else item)
        if not facade._is_live_equity_symbol(symbol):
            continue
        value = fe_by_symbol.get(symbol)
        if isinstance(value, dict) and value:
            stale_symbols.append(symbol)
    if not stale_symbols:
        return False, ""
    return True, "quote_metrics_missing_rebuild_feature_engine"
