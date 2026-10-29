"""Read-only Commander shadow evidence projections."""
from __future__ import annotations


def build_monitor_gate_details(state, *, facade):
    monitor_entry = facade._dict(state.get("monitor_entry"))
    monitor_output = facade._dict(state.get("monitor_output"))
    metrics = facade._dict(monitor_entry.get("metrics"))
    thresholds = facade._dict(monitor_entry.get("thresholds"))
    passed_checks = [str(x or "").strip() for x in list(monitor_entry.get("passed_checks") or []) if str(x or "").strip()]
    failed_checks = [str(x or "").strip() for x in list(monitor_entry.get("failed_checks") or []) if str(x or "").strip()]
    pullback_flags = [key for key in ("pullback_ok", "pullback_mature", "pullback_not_too_deep") if key in metrics]
    pullback_values = [bool(metrics.get(key)) for key in pullback_flags if isinstance(metrics.get(key), bool)]
    pullback_passed = None
    if pullback_values:
        pullback_passed = all(pullback_values)
    elif "pullback_ok" in passed_checks:
        pullback_passed = True
    elif "pullback_ok" in failed_checks:
        pullback_passed = False
    entry_block_reason = facade._clip(
        monitor_entry.get("guard_reason") or monitor_entry.get("reason") or monitor_output.get("entry_exit_reason"),
        max_len=180,
    )
    observed_features = {
        "price": metrics.get("price") if metrics.get("price") not in (None, "") else metrics.get("current_price"),
        "current_price": metrics.get("current_price"),
        "minute_source_present": metrics.get("minute_source_present"),
        "minute_source_used": metrics.get("minute_source_used"),
        "latest_candle_ts": metrics.get("latest_candle_ts"),
        "minute_snapshot_age_minutes": metrics.get("minute_snapshot_age_minutes"),
        "minute_snapshot_was_stale": metrics.get("minute_snapshot_was_stale"),
        "minute_refetch_attempted": metrics.get("minute_refetch_attempted"),
        "minute_refetch_succeeded": metrics.get("minute_refetch_succeeded"),
        "minute_refetch_reason": metrics.get("minute_refetch_reason"),
        "minute_refetch_trigger_reason": metrics.get("minute_refetch_trigger_reason"),
        "minute_refetch_failure_reason": metrics.get("minute_refetch_failure_reason"),
        "minute_refetch_produced_fresh_snapshot": metrics.get("minute_refetch_produced_fresh_snapshot"),
        "volume_ratio": metrics.get("volume_ratio"),
        "vwap_distance": metrics.get("vwap_distance") if metrics.get("vwap_distance") not in (None, "") else metrics.get("extended_from_vwap_pct"),
        "extended_from_vwap_pct": metrics.get("extended_from_vwap_pct"),
        "pullback_depth_pct": metrics.get("pullback_depth_pct") if metrics.get("pullback_depth_pct") not in (None, "") else metrics.get("pullback_pct"),
        "pullback_pct": metrics.get("pullback_pct"),
        "recent_high": metrics.get("recent_high"),
        "breakout_level": metrics.get("breakout_level"),
        "bar_count": metrics.get("bar_count"),
        "timeframe_minutes": metrics.get("timeframe_minutes"),
        "inferred_spacing_minutes": metrics.get("inferred_spacing_minutes"),
        "series_class": metrics.get("series_class"),
    }
    return {
        "breakout_passed": facade._gate_pass(metrics, passed_checks, failed_checks, "breakout_ok"),
        "volume_passed": facade._gate_pass(metrics, passed_checks, failed_checks, "volume_ok"),
        "vwap_extension_passed": facade._gate_pass(metrics, passed_checks, failed_checks, "extension_ok"),
        "pullback_passed": pullback_passed,
        "entry_score": facade._score_from_checks(passed_checks=passed_checks, failed_checks=failed_checks, fallback=monitor_entry.get("confidence")),
        "entry_block_reason": entry_block_reason or "",
        "used_thresholds": thresholds,
        "observed_features": {k: v for k, v in observed_features.items() if v not in (None, "")},
        "passed_gates": passed_checks[:8],
        "failed_gates": failed_checks[:8],
        "primary_failure_axis": facade._clip(monitor_entry.get("primary_failure_axis"), max_len=80),
    }


def build_context_delta_summary(state, *, observations, facade):
    shadow_runtime = facade._dict(state.get("commander_shadow_runtime"))
    prior = facade._dict(shadow_runtime.get("prior_context"))
    strategist_output = facade._dict(state.get("strategist_output"))
    selected = facade._dict(state.get("selected"))
    monitor_output = facade._dict(state.get("monitor_output"))
    global_signal = facade._dict(state.get("global_signal"))
    fear_index = facade._dict(global_signal.get("fear_index"))
    overlay = facade._dict(strategist_output.get("macro_stress_overlay"))
    current_symbol = facade._clip(selected.get("symbol") or monitor_output.get("selected_symbol"), max_len=24)
    last_symbol = facade._clip(prior.get("selected_symbol"), max_len=24)
    current_score = selected.get("score_total")
    if current_score in (None, ""): current_score = selected.get("score")
    if current_score in (None, ""): current_score = selected.get("confidence")
    last_score = prior.get("selected_score_total")
    current_playbook = facade._clip(strategist_output.get("playbook"), max_len=40)
    last_playbook = facade._clip(prior.get("playbook"), max_len=40)
    current_regime = facade._clip(strategist_output.get("market_regime"), max_len=40)
    last_regime = facade._clip(prior.get("market_regime"), max_len=40)
    current_sentiment = facade._clip(strategist_output.get("market_sentiment"), max_len=40)
    last_sentiment = facade._clip(prior.get("market_sentiment"), max_len=40)
    current_sentiment_score = strategist_output.get("global_sentiment_score")
    last_sentiment_score = prior.get("global_sentiment_score")
    current_vix = fear_index.get("level") if fear_index.get("level") not in (None, "") else overlay.get("vix_level")
    last_vix = prior.get("vix_level")
    current_stress_flags = [str(x or "").strip() for x in list(overlay.get("stress_flags") or []) if str(x or "").strip()]
    last_stress_flags = [str(x or "").strip() for x in list(prior.get("stress_flags") or []) if str(x or "").strip()]
    symbol_same_as_last = None if not current_symbol or not last_symbol else current_symbol == last_symbol
    playbook_same_as_last = None if not current_playbook or not last_playbook else current_playbook == last_playbook
    market_regime_changed = None if not current_regime or not last_regime else current_regime != last_regime
    sentiment_changed = None
    if current_sentiment and last_sentiment: sentiment_changed = current_sentiment != last_sentiment
    try:
        if current_sentiment_score not in (None, "") and last_sentiment_score not in (None, ""):
            sentiment_changed = abs(float(current_sentiment_score) - float(last_sentiment_score)) >= 0.03
    except Exception: pass
    volatility_changed = None
    try:
        if current_vix not in (None, "") and last_vix not in (None, ""):
            volatility_changed = abs(float(current_vix) - float(last_vix)) >= 1.0
    except Exception: pass
    if volatility_changed is None and current_stress_flags and last_stress_flags:
        volatility_changed = sorted(current_stress_flags) != sorted(last_stress_flags)
    signal_changed = None
    try:
        if current_score not in (None, "") and last_score not in (None, ""):
            signal_changed = abs(float(current_score) - float(last_score)) >= 0.05
    except Exception: signal_changed = None
    if signal_changed is None and symbol_same_as_last is not None: signal_changed = not symbol_same_as_last
    return {
        "symbol_same_as_last": symbol_same_as_last, "playbook_same_as_last": playbook_same_as_last,
        "market_regime_changed": market_regime_changed, "sentiment_changed": sentiment_changed,
        "volatility_changed": volatility_changed, "signal_changed": signal_changed,
        "last_llm_status": facade._clip(prior.get("llm_status") or observations.get("last_llm_status"), max_len=40),
        "repeated_same_context": observations.get("repeated_same_context"), "market_changed": observations.get("market_changed"),
    }
