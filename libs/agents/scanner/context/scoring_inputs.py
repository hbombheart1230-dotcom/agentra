"""Scanner score-weight, live-equity filter and compatibility-bias inputs (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _memory_bias_observation_only_r3_impl(state, *, facade):
    if isinstance(state, dict):
        for key in ("memory_bias_observation_only", "commander_memory_bias_observation_only"):
            if state.get(key) not in (None, ""):
                return facade._is_trueish(state.get(key))
    for name in ("MEMORY_BIAS_OBSERVATION_ONLY", "COMMANDER_MEMORY_BIAS_OBSERVATION_ONLY"):
        raw = str(facade.os.getenv(name, "") or "").strip()
        if raw:
            return facade._is_trueish(raw)
    return False


def _enforce_live_equity_symbols_r3_impl(state, policy, *, facade):
    for raw in (
        policy.get("enforce_live_equity_symbols") if isinstance(policy, dict) else None,
        state.get("enforce_live_equity_symbols") if isinstance(state, dict) else None,
        facade.os.getenv("SCANNER_ENFORCE_LIVE_EQUITY_SYMBOLS", ""),
    ):
        if raw not in (None, ""):
            return facade._is_trueish(raw)
    return not bool(facade.os.getenv("PYTEST_CURRENT_TEST"))


def _filter_live_equity_candidates_r3_impl(candidates, *, facade):
    kept: List[Any] = []
    excluded: List[str] = []
    for item in list(candidates or []):
        raw_symbol = item.get("symbol") if isinstance(item, dict) else item
        symbol = facade._norm_symbol(raw_symbol)
        if not facade._is_live_equity_symbol(symbol):
            if symbol:
                excluded.append(symbol)
            continue
        if isinstance(item, dict):
            row = dict(item)
            row["symbol"] = symbol
            kept.append(row)
        else:
            kept.append(symbol)
    return kept, {
        "live_equity_symbol_filter_enabled": True,
        "live_equity_symbol_excluded_count": int(len(excluded)),
        "live_equity_symbol_excluded_symbols": excluded[:20],
        "candidate_pool_after_live_equity_symbol_filter": int(len(kept)),
    }


def _get_scanner_weights_r3_impl(policy, *, facade):
    """Scanner weighting policy for M18-4.

    Defaults are conservative (small influence), and should not change behavior
    when sentiments are missing (both default to 0.0).
    """
    pol = policy if isinstance(policy, dict) else {}
    return {
        "weight_news": float(pol.get("weight_news", 0.20)),
        "weight_global": float(pol.get("weight_global", 0.10)),
        "risk_news_penalty": float(pol.get("risk_news_penalty", 0.30)),
        "risk_global_penalty": float(pol.get("risk_global_penalty", 0.20)),
        "confidence_news_boost": float(pol.get("confidence_news_boost", 0.05)),
        "feature_score_weight": float(pol.get("feature_score_weight", 0.0)),
        "feature_risk_penalty": float(pol.get("feature_risk_penalty", 0.0)),
        "high_vol_risk_penalty": float(pol.get("high_vol_risk_penalty", 0.0)),
    }


def _stable_unit_hash_r3_impl(text, *, facade):
    """Return a deterministic pseudo-random float in [0, 1).

    We avoid Python's built-in hash() because it is salted per-process.
    """
    # A tiny, deterministic rolling hash
    h = 0
    for ch in text:
        h = (h * 131 + ord(ch)) % 10_000
    return (h % 10_000) / 10_000.0


def _resolve_scanner_score_weights_r3_impl(policy, *, facade):
    def pf(key: str, env_key: str, default: float) -> float:
        raw = policy.get(key)
        if raw in (None, ""):
            raw = facade.os.getenv(env_key, str(default))
        return facade._to_float(raw)

    return {
        "trading_value": pf("score_weight_trading_value", "SCORE_WEIGHTS_TRADING_VALUE", 0.20),
        "momentum": pf("score_weight_momentum", "SCORE_WEIGHTS_MOMENTUM", 0.22),
        "trend": pf("score_weight_trend", "SCORE_WEIGHTS_TREND", 0.20),
        "volume_surge": pf("score_weight_volume_surge", "SCORE_WEIGHTS_VOLUME_SURGE", 0.14),
        "intraday_strength": pf("score_weight_intraday_strength", "SCORE_WEIGHTS_INTRADAY_STRENGTH", 0.12),
        "theme_boost": pf("score_weight_theme_boost", "SCORE_WEIGHTS_THEME_BOOST", 0.06),
        "sentiment": pf("score_weight_sentiment", "SCORE_WEIGHTS_SENTIMENT", 0.06),
        "volatility_penalty": pf("score_weight_volatility_penalty", "SCORE_WEIGHTS_VOLATILITY_PENALTY", 0.10),
        "gap_penalty": pf("score_weight_gap_penalty", "SCORE_WEIGHTS_GAP_PENALTY", 0.07),
        "open_order_penalty": pf("score_weight_open_order_penalty", "SCORE_WEIGHTS_OPEN_ORDER_PENALTY", 0.04),
    }


def _normalize_priority_list_r3_impl(values, *, facade):
    out: List[str] = []
    seen = set()
    if not isinstance(values, list):
        return out
    for row in values:
        s = str(row or "").strip().lower()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def _resolve_compatibility_bias_context_r3_impl(state, *, limit, facade):
    root = facade.Path.cwd() / "reports" / "canonical" / facade._resolve_canonical_day(state)
    if not root.exists():
        return {
            "dominant_block_reason": "mixed",
            "dominant_block_reason_ratio": 0.0,
            "bias_scale": 0.10,
            "sample_size": 0,
        }

    monitor_paths = sorted(
        [
            p / "monitor.json"
            for p in root.iterdir()
            if p.is_dir()
            and len(str(p.name)) == 32
            and all(ch in "0123456789abcdefABCDEF" for ch in str(p.name))
            and (p / "monitor.json").exists()
        ],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[: max(1, int(limit))]
    reasons: List[str] = []
    for path in monitor_paths:
        try:
            import json

            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        reason = facade._extract_monitor_entry_block_reason(payload)
        if reason:
            reasons.append(reason)

    if not reasons:
        return {
            "dominant_block_reason": "mixed",
            "dominant_block_reason_ratio": 0.0,
            "bias_scale": 0.10,
            "sample_size": 0,
        }

    counter = facade.Counter(reasons)
    top_reason, top_count = counter.most_common(1)[0]
    top_ratio = float(top_count) / float(len(reasons))
    dominant_block_reason = top_reason if top_ratio >= 0.40 else "mixed"
    if dominant_block_reason in {"volume_confirmation_missing", "volume_insufficient"}:
        bias_scale = 0.18 if top_ratio >= 0.60 else 0.15
    elif dominant_block_reason in {"below_vwap_reclaim_not_ready", "pullback_below_vwap_reclaim_not_ready"}:
        bias_scale = 0.16 if top_ratio >= 0.45 else 0.12
    elif dominant_block_reason in {"pullback_not_mature", "breakout_not_ready"}:
        bias_scale = 0.14 if top_ratio >= 0.45 else 0.11
    else:
        bias_scale = 0.10
    return {
        "dominant_block_reason": str(dominant_block_reason),
        "dominant_block_reason_ratio": float(top_ratio if dominant_block_reason != "mixed" else 0.0),
        "bias_scale": float(bias_scale),
        "sample_size": int(len(reasons)),
    }
