"""Monitor entry signal evidence views (minute OHLCV meta, ETF deviation, signal trace and sizing inputs).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def entry_evidence_effective_policy_trace_entry_applied_pol(state, policy, symbol, selected, selected_features, entry_policy, strategy_frame, entry_policy_contract, closeout_window_guard, max_positions, open_position_count, held_symbols, pending_buy_symbols, selected_already_held, selected_pending_buy, post_exit_cooldown_scope, last_trade_symbol, post_exit_cooldown_symbol_match, commander_entry_control, entry_received_policy, entry_policy_origin, *, facade):
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
    selected["features"] = entry_features
    entry_info = facade.evaluate_intraday_entry_signal(
        entry_rows,
        current_price=selected.get("price") if isinstance(selected, dict) else None,
        features=entry_features,
        policy=entry_policy,
        scoring=entry_scoring_policy,
        frame=strategy_frame,
        policy_contract=entry_policy_contract,
    )
    entry_info["closeout_window_guard"] = dict(closeout_window_guard)
    entry_info["minutes_to_close"] = closeout_window_guard.get("minutes_to_close")
    entry_info["eod_flat_cutoff_min"] = int(closeout_window_guard.get("cutoff_min") or 0)
    entry_info["buy_closeout_cutoff_min"] = int(closeout_window_guard.get("buy_cutoff_min") or 0)
    entry_info["closeout_window_active"] = bool(closeout_window_guard.get("active"))
    entry_info["symbol"] = symbol
    entry_info["selected_symbol"] = symbol
    entry_info["max_positions"] = int(max_positions)
    entry_info["multi_position_capacity_remaining"] = max(0, int(max_positions) - int(open_position_count))
    entry_info["held_symbols"] = sorted(held_symbols)
    entry_info["pending_buy_symbols"] = sorted(pending_buy_symbols)
    entry_info["selected_symbol_already_held"] = bool(selected_already_held)
    entry_info["selected_symbol_pending_buy"] = bool(selected_pending_buy)
    entry_info["post_exit_cooldown_scope"] = str(post_exit_cooldown_scope)
    entry_info["post_exit_cooldown_last_trade_symbol"] = str(last_trade_symbol)
    entry_info["post_exit_cooldown_symbol_match"] = bool(post_exit_cooldown_symbol_match)
    if commander_entry_control:
        entry_info["commander_entry_control"] = dict(commander_entry_control)
    entry_info["applied_policy"] = dict(entry_info.get("applied_policy") or entry_info.get("thresholds") or entry_policy.to_dict())
    entry_applied_policy = dict(entry_info.get("applied_policy") or {})
    effective_policy_trace = facade._build_monitor_effective_policy_trace(
        received_policy=entry_received_policy,
        effective_policy=entry_applied_policy,
        frame=strategy_frame,
        received_policy_source=entry_policy_origin,
    )
    return (effective_policy_trace, entry_applied_policy, entry_info, entry_row_source, entry_rows, minute_fetch_meta, minute_ohlcv_meta, quote_for_entry)


def entry_evidence_effect_free_block_500(effective_policy_trace, *, facade):
    if True:
        source_chain = list(effective_policy_trace.get("effective_policy_source_chain") or [])
        effective_policy_trace["effective_policy_source_chain"] = (
            [source_chain[0], "commander_memory_bias", *source_chain[1:]]
            if source_chain
            else ["commander_memory_bias", "monitor_effective_policy"]
        )
        effective_policy_trace["effective_policy_source"] = "monitor_memory_bias_adjusted"
        policy_adjustment_summary = str(effective_policy_trace.get("policy_adjustment_summary") or "").strip()
        effective_policy_trace["policy_adjustment_summary"] = (
            f"{policy_adjustment_summary} | memory_bias=commander"
            if policy_adjustment_summary
            else "commander memory bias adjusted entry policy"
        )
        policy_adjustment_reasoning = str(effective_policy_trace.get("policy_adjustment_reasoning") or "").strip()
        prefix = "Commander-approved memory bias adjusted the entry baseline before strategy-frame normalization."
        effective_policy_trace["policy_adjustment_reasoning"] = (
            f"{prefix} {policy_adjustment_reasoning}".strip()
        )
    return None


def entry_evidence_effect_free_block_518(entry_info, effective_policy_trace, entry_policy_contract, monitor_memory_bias_result, monitor_memory_bias_observation_only, monitor_memory_bias, monitor_memory_bias_summary, monitor_memory_bias_observed_entry_result, entry_rows, entry_row_source, minute_fetch_meta, minute_ohlcv_meta, *, facade):
    entry_info["received_policy"] = dict(effective_policy_trace.get("received_policy") or {})
    entry_info["received_policy_source"] = str(effective_policy_trace.get("received_policy_source") or "")
    entry_info["policy_contract"] = dict(entry_policy_contract)
    entry_info["effective_policy"] = dict(effective_policy_trace.get("effective_policy") or {})
    entry_info["effective_policy_source"] = str(effective_policy_trace.get("effective_policy_source") or "")
    entry_info["effective_policy_source_chain"] = list(effective_policy_trace.get("effective_policy_source_chain") or [])
    entry_info["policy_adjustments"] = dict(effective_policy_trace.get("policy_adjustments") or {})
    entry_info["policy_adjustment_summary"] = str(effective_policy_trace.get("policy_adjustment_summary") or "")
    entry_info["policy_adjustment_reasoning"] = str(effective_policy_trace.get("policy_adjustment_reasoning") or "")
    entry_info["effective_policy_deltas"] = list(effective_policy_trace.get("effective_policy_deltas") or [])
    entry_info["monitor_memory_bias_applied"] = bool(monitor_memory_bias_result.get("applied"))
    entry_info["monitor_memory_bias_observation_only"] = bool(monitor_memory_bias_observation_only)
    entry_info["monitor_memory_bias"] = dict(monitor_memory_bias)
    entry_info["monitor_memory_bias_summary"] = dict(monitor_memory_bias_summary)
    entry_info["monitor_memory_bias_deltas"] = list(monitor_memory_bias_result.get("deltas") or [])
    entry_info["monitor_memory_bias_observed_deltas"] = list(
        monitor_memory_bias_observed_entry_result.get("deltas") or []
    )
    entry_memory_application_trace = facade.build_monitor_commander_memory_application_trace(
        monitor_memory_bias=monitor_memory_bias,
        entry_result=monitor_memory_bias_result,
        hold_result={"applied": False, "deltas": []},
        exit_result={"applied": False, "deltas": []},
        monitor_memory_bias_summary=monitor_memory_bias_summary,
        effective_policy_source=str(effective_policy_trace.get("effective_policy_source") or ""),
        effective_policy_source_chain=list(effective_policy_trace.get("effective_policy_source_chain") or []),
    )
    entry_info["commander_memory_application_trace"] = dict(entry_memory_application_trace)
    entry_info["monitor_memory_application_trace"] = dict(entry_memory_application_trace)
    entry_metrics = entry_info.get("metrics") if isinstance(entry_info.get("metrics"), dict) else {}
    entry_metrics["minute_source_present"] = bool(entry_rows)
    entry_metrics["minute_source_used"] = entry_row_source or ""
    latest_candle_ts = None
    if entry_rows and isinstance(entry_rows[-1], dict):
        latest_candle_ts = entry_rows[-1].get("ts")
    entry_metrics["latest_candle_ts"] = latest_candle_ts
    entry_metrics["minute_snapshot_age_minutes"] = minute_fetch_meta.get("minute_snapshot_age_minutes")
    entry_metrics["minute_snapshot_was_stale"] = bool(minute_fetch_meta.get("minute_snapshot_was_stale"))
    entry_metrics["minute_refetch_attempted"] = bool(minute_fetch_meta.get("minute_refetch_attempted"))
    entry_metrics["minute_refetch_succeeded"] = bool(minute_fetch_meta.get("minute_refetch_succeeded"))
    entry_metrics["minute_refetch_reason"] = str(minute_fetch_meta.get("minute_refetch_reason") or "")
    entry_metrics["minute_refetch_trigger_reason"] = str(minute_fetch_meta.get("minute_refetch_trigger_reason") or "")
    entry_metrics["minute_refetch_failure_reason"] = str(minute_fetch_meta.get("minute_refetch_failure_reason") or "")
    entry_metrics["minute_refetch_failure_detail"] = str(minute_fetch_meta.get("minute_refetch_failure_detail") or "")
    entry_metrics["minute_refetch_runner_source"] = str(minute_fetch_meta.get("minute_refetch_runner_source") or "")
    entry_metrics["minute_refetch_produced_fresh_snapshot"] = bool(
        minute_fetch_meta.get("minute_refetch_produced_fresh_snapshot")
    )
    entry_metrics["minute_cache_fallback_used"] = bool(minute_fetch_meta.get("minute_cache_fallback_used"))
    entry_metrics["minute_cache_fallback_source"] = str(minute_fetch_meta.get("minute_cache_fallback_source") or "")
    entry_info["metrics"] = entry_metrics
    entry_info["minute_source_meta"] = dict(minute_ohlcv_meta or {})
    entry_info["minute_fetch_meta"] = minute_fetch_meta
    return None
