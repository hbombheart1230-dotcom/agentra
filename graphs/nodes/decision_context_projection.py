"""Deterministic in-memory decision context projection; no clock, env or IO."""
from __future__ import annotations


def cache_inputs(state, symbol, *, facade):
    cache_root = state.get("_decision_context_cache")
    if not isinstance(cache_root, dict):
        cache_root = {}
    cache_row = cache_root.get(symbol) if isinstance(cache_root.get(symbol), dict) else {}
    last_epoch = facade._to_int(cache_row.get("refreshed_epoch"), 0) if isinstance(cache_row, dict) else 0

    return cache_root, cache_row, last_epoch


def apply_cached(state, *, symbol, cache_root, cache_row, last_epoch, refresh_sec, feature_regime, feature_signal, facade):
    gs_cached = facade._to_float(cache_row.get("global_sentiment_score"), 0.0)
    ns_cached = facade._to_float(cache_row.get("news_sentiment_score"), 0.0)
    gs_signal_cached = (
        dict(cache_row.get("global_sentiment_signal"))
        if isinstance(cache_row.get("global_sentiment_signal"), dict)
        else facade.make_signal(
            score=gs_cached,
            status=facade.SIGNAL_STATUS_FALLBACK,
            source="decision_context_cache",
            reason="legacy_cache_missing_signal",
            ts=last_epoch,
        )
    )
    ns_signal_cached = (
        dict(cache_row.get("news_sentiment_signal"))
        if isinstance(cache_row.get("news_sentiment_signal"), dict)
        else facade.make_signal(
            score=ns_cached,
            status=facade.SIGNAL_STATUS_FALLBACK,
            source="decision_context_cache",
            reason="legacy_cache_missing_signal",
            ts=last_epoch,
        )
    )
    state["global_sentiment"] = {"score": float(gs_cached)}
    state["global_sentiment_signal"] = gs_signal_cached

    ns_map = dict(state.get("news_sentiment") or {}) if isinstance(state.get("news_sentiment"), dict) else {}
    ns_map[symbol] = float(ns_cached)
    state["news_sentiment"] = ns_map

    ns_signal_map = (
        dict(state.get("news_sentiment_signal") or {})
        if isinstance(state.get("news_sentiment_signal"), dict)
        else {}
    )
    ns_signal_map[symbol] = ns_signal_cached
    state["news_sentiment_signal"] = ns_signal_map

    ni_map = dict(state.get("news_items") or {}) if isinstance(state.get("news_items"), dict) else {}
    if isinstance(cache_row.get("news_items"), list):
        ni_map[symbol] = list(cache_row.get("news_items") or [])
        state["news_items"] = ni_map

    state["decision_context_meta"] = {
        "symbol": symbol,
        "cached": True,
        "refresh_sec": int(refresh_sec),
        "last_refreshed_epoch": int(last_epoch),
        "global_sentiment_score": float(gs_cached),
        "news_sentiment_score": float(ns_cached),
        "global_sentiment_status": str(gs_signal_cached.get("status") or ""),
        "global_sentiment_source": str(gs_signal_cached.get("source") or ""),
        "global_sentiment_reason": str(gs_signal_cached.get("reason") or ""),
        "news_sentiment_status": str(ns_signal_cached.get("status") or ""),
        "news_sentiment_source": str(ns_signal_cached.get("source") or ""),
        "news_sentiment_reason": str(ns_signal_cached.get("reason") or ""),
        "feature_regime": feature_regime,
        "feature_signal_score": float(feature_signal),
    }
    state["_decision_context_cache"] = cache_root
    return state


def apply_refreshed(state, *, symbol, cache_root, now, refresh_sec, gs, global_signal, news_score, news_signal, news_items, feature_regime, feature_signal):
    ns_map = dict(state.get("news_sentiment") or {}) if isinstance(state.get("news_sentiment"), dict) else {}
    ns_map[symbol] = float(news_score)
    state["news_sentiment"] = ns_map
    ns_signal_map = (
        dict(state.get("news_sentiment_signal") or {})
        if isinstance(state.get("news_sentiment_signal"), dict)
        else {}
    )
    ns_signal_map[symbol] = news_signal
    state["news_sentiment_signal"] = ns_signal_map

    ni_map = dict(state.get("news_items") or {}) if isinstance(state.get("news_items"), dict) else {}
    ni_map[symbol] = list(news_items)
    state["news_items"] = ni_map

    cache_root[symbol] = {
        "refreshed_epoch": int(now),
        "global_sentiment_score": float(gs),
        "news_sentiment_score": float(news_score),
        "global_sentiment_signal": dict(global_signal),
        "news_sentiment_signal": dict(news_signal),
        "news_items": list(news_items),
        "feature_regime": feature_regime,
        "feature_signal_score": float(feature_signal),
    }
    state["_decision_context_cache"] = cache_root
    state["decision_context_meta"] = {
        "symbol": symbol,
        "cached": False,
        "refresh_sec": int(refresh_sec),
        "last_refreshed_epoch": int(now),
        "global_sentiment_score": float(gs),
        "news_sentiment_score": float(news_score),
        "global_sentiment_status": str(global_signal.get("status") or ""),
        "global_sentiment_source": str(global_signal.get("source") or ""),
        "global_sentiment_reason": str(global_signal.get("reason") or ""),
        "news_sentiment_status": str(news_signal.get("status") or ""),
        "news_sentiment_source": str(news_signal.get("source") or ""),
        "news_sentiment_reason": str(news_signal.get("reason") or ""),
        "feature_regime": feature_regime,
        "feature_signal_score": float(feature_signal),
    }
    return state
