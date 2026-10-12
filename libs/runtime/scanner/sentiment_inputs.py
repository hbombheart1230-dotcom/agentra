"""Scanner global/news sentiment score and signal-map accessors (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _get_global_sentiment_score_r3_impl(state, *, facade):
    """Return global sentiment score in [-1, +1].

    Priority:
      1) state['global_sentiment_signal']['score'] (normalized signal)
      2) state['mock_global_sentiment'] (tests)
      3) state['global_sentiment']['score'] (precomputed)
      4) state['policy']['global_sentiment']['score'] (set by strategist)
      5) default 0.0
    """
    gsig = state.get("global_sentiment_signal")
    if isinstance(gsig, dict):
        try:
            return facade._clamp(float(gsig.get("score") or 0.0), -1.0, 1.0)
        except Exception:
            return 0.0

    if "mock_global_sentiment" in state:
        try:
            return facade._clamp(float(state.get("mock_global_sentiment") or 0.0), -1.0, 1.0)
        except Exception:
            return 0.0

    gs = state.get("global_sentiment")
    if isinstance(gs, dict) and "score" in gs:
        try:
            return facade._clamp(float(gs.get("score") or 0.0), -1.0, 1.0)
        except Exception:
            return 0.0
    if isinstance(gs, (int, float, str)):
        try:
            return facade._clamp(float(gs), -1.0, 1.0)
        except Exception:
            return 0.0

    pol = state.get("policy")
    if isinstance(pol, dict):
        pgs = pol.get("global_sentiment")
        if isinstance(pgs, dict) and "score" in pgs:
            try:
                return facade._clamp(float(pgs.get("score") or 0.0), -1.0, 1.0)
            except Exception:
                return 0.0
        if isinstance(pgs, (int, float, str)):
            try:
                return facade._clamp(float(pgs), -1.0, 1.0)
            except Exception:
                return 0.0

    return 0.0


def _get_news_sentiment_map_r3_impl(state, *, facade):
    """Return per-symbol news sentiment map in [-1, +1].

    Priority:
      1) state['news_sentiment_signal'][symbol]['score']
      2) state['news_sentiment'][symbol]
      3) state['mock_news_sentiment'][symbol]
    """
    raw_sig = state.get("news_sentiment_signal")
    if isinstance(raw_sig, dict):
        out_sig: Dict[str, float] = {}
        for k, v in raw_sig.items():
            if isinstance(v, dict):
                try:
                    out_sig[str(k)] = facade._clamp(float(v.get("score") or 0.0), -1.0, 1.0)
                except Exception:
                    out_sig[str(k)] = 0.0
        if out_sig:
            return out_sig

    raw = state.get("news_sentiment")
    if not isinstance(raw, dict):
        raw = state.get("mock_news_sentiment") if isinstance(state.get("mock_news_sentiment"), dict) else {}
    out: Dict[str, float] = {}
    for k, v in (raw or {}).items():
        try:
            out[str(k)] = facade._clamp(float(v), -1.0, 1.0)
        except Exception:
            out[str(k)] = 0.0
    return out


def _get_global_sentiment_signal_r3_impl(state, *, facade):
    sig = state.get("global_sentiment_signal")
    if isinstance(sig, dict):
        return dict(sig)
    if "mock_global_sentiment" in state:
        return {"status": "ok", "source": "mock_global_sentiment", "reason": ""}
    gs = state.get("global_sentiment")
    if isinstance(gs, dict) and gs.get("score") is not None:
        return {"status": "fallback", "source": "legacy_global_sentiment", "reason": "signal_missing"}
    return {"status": "fallback", "source": "scanner_node", "reason": "missing_global_signal"}


def _get_news_sentiment_signal_map_r3_impl(state, *, facade):
    raw = state.get("news_sentiment_signal")
    if not isinstance(raw, dict):
        raw_scores = state.get("news_sentiment")
        if not isinstance(raw_scores, dict):
            raw_scores = state.get("mock_news_sentiment") if isinstance(state.get("mock_news_sentiment"), dict) else {}
        out_legacy: Dict[str, Dict[str, Any]] = {}
        for k, _v in (raw_scores or {}).items():
            source = "legacy_news_sentiment"
            status = "fallback"
            if isinstance(state.get("mock_news_sentiment"), dict) and str(k) in state.get("mock_news_sentiment", {}):
                source = "mock_news_sentiment"
                status = "ok"
            out_legacy[str(k)] = {"status": status, "source": source, "reason": "signal_missing"}
        return out_legacy
    out: Dict[str, Dict[str, Any]] = {}
    for k, v in raw.items():
        if isinstance(v, dict):
            out[str(k)] = dict(v)
    return out
