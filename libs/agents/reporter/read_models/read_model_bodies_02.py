"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_read_model.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def brief_collect_top_headlines_r4_impl(rows, *, limit, symbol, trim_text, normalize_symbol, facade):
    if not isinstance(rows, list):
        return []
    filtered: List[str] = []
    fallback: List[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        text = facade.brief_headline_text(row, trim_text=trim_text)
        if not text:
            continue
        if text not in fallback:
            fallback.append(text)
        if symbol and facade.brief_headline_matches_symbol(row, symbol, normalize_symbol=normalize_symbol) and (text not in filtered):
            filtered.append(text)
    picked = filtered or fallback
    return picked[:max(1, int(limit))]


def brief_top_numeric_drivers_r4_impl(values, *, limit, facade):
    if not isinstance(values, dict):
        return {}
    scored: List[tuple[float, str, float]] = []
    for key, value in values.items():
        try:
            numeric = float(value)
        except Exception:
            continue
        if numeric == 0.0:
            continue
        scored.append((abs(numeric), str(key), numeric))
    scored.sort(key=lambda row: (-row[0], row[1]))
    out: Dict[str, float] = {}
    for _, key, numeric in scored[:max(1, int(limit))]:
        out[key] = numeric
    return out
