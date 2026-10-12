"""Strategist monitor-entry policy summaries, adjustment deltas and strategy policy assembly (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _summarize_monitor_entry_policy_for_adjustment_r3_impl(policy, *, facade):
    src = dict(policy or {}) if isinstance(policy, dict) else {}
    threshold_policy = (
        dict(src.get("threshold_policy") or {})
        if isinstance(src.get("threshold_policy"), dict)
        else dict(src)
    )
    return {
        key: threshold_policy.get(key)
        for key in facade._POLICY_ADJUSTMENT_COMPARE_FIELDS
        if key in threshold_policy
    }


def _monitor_entry_policy_adjustment_delta_fields_r3_impl(baseline_summary, current_summary, *, facade):
    baseline = dict(baseline_summary or {}) if isinstance(baseline_summary, dict) else {}
    current = dict(current_summary or {}) if isinstance(current_summary, dict) else {}
    compare_keys = list(facade._POLICY_ADJUSTMENT_COMPARE_FIELDS)
    if baseline:
        compare_keys = [key for key in compare_keys if key in baseline and key in current]
    fields: List[str] = []
    for key in compare_keys:
        if key not in baseline and key not in current:
            continue
        if baseline.get(key) != current.get(key):
            fields.append(str(key))
    return fields


def _focus_axes_from_strings_r3_impl(*values, facade):
    joined = " ".join(str(v or "").strip().lower() for v in values if str(v or "").strip())
    axes: List[str] = []
    mapping = (
        ("reclaim", ("reclaim", "vwap_reclaim")),
        ("pullback", ("pullback",)),
        ("volume", ("volume",)),
        ("breakout", ("breakout",)),
        ("extension", ("extended", "extension", "vwap")),
        ("exit_axis", ("drawdown", "exit_axis", "stop", "take_profit")),
    )
    for axis, needles in mapping:
        if any(token in joined for token in needles):
            axes.append(axis)
    seen: set[str] = set()
    out: List[str] = []
    for axis in axes:
        if axis in seen:
            continue
        seen.add(axis)
        out.append(axis)
    return out[:4]


def _compact_monitor_entry_policy_baseline_for_llm_r3_impl(policy, *, facade):
    src = policy if isinstance(policy, dict) else {}
    keep = (
        "enabled",
        "timeframe_minutes",
        "volume_ratio_min",
        "min_extended_from_vwap_pct",
        "max_extended_from_vwap_pct",
        "pullback_min_pct",
        "pullback_max_pct",
        "reclaim_tolerance_pct",
        "intent_cooldown_sec",
        "require_vwap_reclaim",
        "require_rebound",
    )
    return {key: src.get(key) for key in keep if key in src}


def _monitor_policy_r3_impl(*, state, policy, monitor_guidance, trade_aggressiveness, risk_tone, facade):
    applied_policy = state.get("applied_policy") if isinstance(state, dict) and isinstance(state.get("applied_policy"), dict) else {}
    monitor_applied = applied_policy.get("monitor") if isinstance(applied_policy.get("monitor"), dict) else {}
    execution_applied = applied_policy.get("execution") if isinstance(applied_policy.get("execution"), dict) else {}
    policy_row = dict(policy or {}) if isinstance(policy, dict) else {}

    raw_min_hold = (
        facade._nested_mapping_value(monitor_applied, "hold", "min_hold_seconds")
        if facade._nested_mapping_value(monitor_applied, "hold", "min_hold_seconds") is not None
        else facade._nested_mapping_value(policy_row, "monitor", "hold", "min_hold_seconds")
    )
    if raw_min_hold is None:
        raw_min_hold = policy_row.get("min_hold_seconds")
    min_hold_sec = facade._to_int(raw_min_hold, 600)

    raw_sell_cooldown = (
        facade._nested_mapping_value(execution_applied, "cooldowns", "sell_sec")
        if facade._nested_mapping_value(execution_applied, "cooldowns", "sell_sec") is not None
        else facade._nested_mapping_value(policy_row, "execution", "cooldowns", "sell_sec")
    )
    if raw_sell_cooldown is None:
        raw_sell_cooldown = policy_row.get("sell_cooldown_seconds")
    if raw_sell_cooldown is None:
        raw_sell_cooldown = policy_row.get("sell_cooldown_sec")
    sell_cooldown = facade._to_int(raw_sell_cooldown, 300)

    raw_confirm_ticks = (
        facade._nested_mapping_value(monitor_applied, "exit", "confirm_ticks")
        if facade._nested_mapping_value(monitor_applied, "exit", "confirm_ticks") is not None
        else facade._nested_mapping_value(policy_row, "monitor", "exit", "confirm_ticks")
    )
    if raw_confirm_ticks is None:
        raw_confirm_ticks = policy_row.get("exit_confirm_ticks")
    confirm_ticks = facade._to_int(raw_confirm_ticks, 2)
    adjustments: List[str] = []

    mode = str(monitor_guidance or "").strip().lower()
    if mode == "hold_through_noise":
        min_hold_sec += 300
        confirm_ticks += 1
        sell_cooldown += 60
        adjustments.append("mode:hold_through_noise")
    elif mode == "defensive_exit":
        confirm_ticks = max(1, confirm_ticks - 1)
        min_hold_sec = max(0, min_hold_sec - 120)
        adjustments.append("mode:defensive_exit")
    elif mode == "quick_take_profit":
        confirm_ticks = 1
        min_hold_sec = max(0, min_hold_sec - 300)
        sell_cooldown = max(60, min(sell_cooldown, 180))
        adjustments.append("mode:quick_take_profit")

    tone = str(risk_tone or "").strip().lower()
    if tone == "conservative":
        confirm_ticks += 1
        min_hold_sec += 120
        adjustments.append("risk_tone:conservative")
    elif tone == "aggressive":
        confirm_ticks = max(1, confirm_ticks - 1)
        min_hold_sec = max(0, min_hold_sec - 60)
        adjustments.append("risk_tone:aggressive")

    aggr = str(trade_aggressiveness or "").strip().lower()
    if aggr == "low":
        confirm_ticks = max(confirm_ticks, 3)
        adjustments.append("trade_aggressiveness:low")
    elif aggr == "high":
        confirm_ticks = max(1, confirm_ticks - 1)
        adjustments.append("trade_aggressiveness:high")

    return {
        "min_hold_seconds": max(0, int(min_hold_sec)),
        "sell_cooldown_seconds": max(0, int(sell_cooldown)),
        "exit_confirm_ticks": max(1, min(6, int(confirm_ticks))),
        "adjustments": list(adjustments),
        "note": "monitor_manages_entry_exit_only",
    }


def _strategy_policy_score_weights_r3_impl(*, facade):
    return {
        "trading_value": facade._to_float(facade.os.getenv("SCORE_WEIGHTS_TRADING_VALUE", "0.20"), 0.20),
        "momentum": facade._to_float(facade.os.getenv("SCORE_WEIGHTS_MOMENTUM", "0.22"), 0.22),
        "trend": facade._to_float(facade.os.getenv("SCORE_WEIGHTS_TREND", "0.20"), 0.20),
        "volume_surge": facade._to_float(facade.os.getenv("SCORE_WEIGHTS_VOLUME_SURGE", "0.14"), 0.14),
        "intraday_strength": facade._to_float(facade.os.getenv("SCORE_WEIGHTS_INTRADAY_STRENGTH", "0.12"), 0.12),
        "theme_boost": facade._to_float(facade.os.getenv("SCORE_WEIGHTS_THEME_BOOST", "0.06"), 0.06),
        "sentiment": facade._to_float(facade.os.getenv("SCORE_WEIGHTS_SENTIMENT", "0.06"), 0.06),
        "volatility_penalty": facade._to_float(facade.os.getenv("SCORE_WEIGHTS_VOLATILITY_PENALTY", "0.10"), 0.10),
        "gap_penalty": facade._to_float(facade.os.getenv("SCORE_WEIGHTS_GAP_PENALTY", "0.07"), 0.07),
        "open_order_penalty": facade._to_float(facade.os.getenv("SCORE_WEIGHTS_OPEN_ORDER_PENALTY", "0.04"), 0.04),
    }


def _strategy_policy_entry_policy_r3_impl(*, facade):
    return {
        "buy_score_threshold": facade._to_float(facade.os.getenv("STRATEGY_V1_BUY_COMPOSITE_THRESHOLD", "0.20"), 0.20),
        "sell_score_threshold": facade._to_float(facade.os.getenv("STRATEGY_V1_SELL_COMPOSITE_THRESHOLD", "-0.12"), -0.12),
        "min_signal_for_entry": facade._to_float(facade.os.getenv("STRATEGY_V1_MIN_SIGNAL_FOR_ENTRY", "0.15"), 0.15),
        "min_news_for_entry": facade._to_float(facade.os.getenv("STRATEGY_V1_MIN_NEWS_FOR_ENTRY", "0.00"), 0.00),
        "max_volatility_for_entry": facade._to_float(facade.os.getenv("STRATEGY_V1_MAX_VOLATILITY_FOR_ENTRY", "0.12"), 0.12),
        "invalidation_signal_floor": facade._to_float(facade.os.getenv("STRATEGY_V1_INVALIDATION_SIGNAL_FLOOR", "-0.08"), -0.08),
        "base_risk_per_trade_ratio": facade._to_float(facade.os.getenv("STRATEGY_V1_BASE_RISK_PER_TRADE_RATIO", "0.01"), 0.01),
        "base_position_notional_ratio": facade._to_float(
            facade.os.getenv("STRATEGY_V1_BASE_POSITION_NOTIONAL_RATIO", "0.10"),
            0.10,
        ),
        "min_confidence_for_entry": facade._to_float(facade.os.getenv("STRATEGY_V1_MIN_CONFIDENCE_FOR_ENTRY", "0.35"), 0.35),
        "max_position_qty": max(1, facade._to_int(facade.os.getenv("STRATEGY_V1_MAX_POSITION_QTY", "10"), 10)),
        "min_position_qty": max(1, facade._to_int(facade.os.getenv("STRATEGY_V1_MIN_POSITION_QTY", "1"), 1)),
        "lot_size": max(1, facade._to_int(facade.os.getenv("STRATEGY_V1_LOT_SIZE", "1"), 1)),
    }


def _build_strategy_policy_r3_impl(
    *,
    market_regime,
    market_sentiment,
    playbook,
    trade_aggressiveness,
    risk_tone,
    monitor_guidance,
    global_signal,
    market_context_inputs,
    themes,
    avoid_themes,
    theme_strength,
    scanner_priority,
    scanner_source_policy,
    scanner_bias_context,
    monitor_entry_policy,
    monitor_policy,
    exit_policy,
    macro_stress_overlay,
    news_ctx,
    facade,
):
    fear_index = dict(global_signal.get("fear_index") or {}) if isinstance(global_signal.get("fear_index"), dict) else {}
    market_news_count = facade._to_int(news_ctx.get("headline_count"), 0)
    candidate_news_count = facade._to_int(news_ctx.get("candidate_signal_total"), 0)
    entry_policy = facade._strategy_policy_entry_policy()
    effective_use_eod_flat = exit_policy.get("use_eod_flat") if isinstance(exit_policy, dict) else None
    if effective_use_eod_flat is None and isinstance(monitor_policy, dict):
        effective_use_eod_flat = (
            (((monitor_policy.get("exit") or {}).get("eod_flat") or {}).get("enabled"))
            if isinstance((monitor_policy.get("exit") or {}).get("eod_flat"), dict)
            else None
        )
    if effective_use_eod_flat is None:
        effective_use_eod_flat = True
    return {
        "schema_version": "strategy_policy.v1",
        "market_policy": {
            "market_regime": str(market_regime or "neutral"),
            "market_sentiment": str(market_sentiment or "neutral"),
            "playbook": str(playbook or "defensive"),
            "trade_aggressiveness": str(trade_aggressiveness or "medium"),
            "risk_tone": str(risk_tone or "normal"),
            "monitor_guidance": str(monitor_guidance or "defensive_exit"),
            "defensive_mode": bool(macro_stress_overlay.get("active")),
            "global_sentiment_score": facade._to_float(global_signal.get("score"), 0.0),
            "fear_index": {
                "vix_level": facade._to_float(fear_index.get("level"), 0.0),
                "vix_pressure": facade._to_float(fear_index.get("level_pressure"), 0.0),
                "elevated": bool(
                    facade._to_float(fear_index.get("level"), 0.0) >= 25.0
                    or facade._to_float(fear_index.get("level_pressure"), 0.0) >= 0.25
                ),
            },
            "macro_stress_score": facade._to_float(market_context_inputs.get("macro_risk"), 0.0),
            "macro_stress_flags": [str(x) for x in list(macro_stress_overlay.get("flags") or [])],
            "market_context_inputs": dict(market_context_inputs or {}),
            "theme_policy": {
                "preferred_themes": [str(x) for x in list(themes or [])],
                "avoid_themes": [str(x) for x in list(avoid_themes or [])],
                "theme_strength": dict(theme_strength or {}),
            },
            "news_policy": {
                "market_news_count": int(market_news_count),
                "candidate_news_count": int(candidate_news_count),
                "average_news_score": facade._to_float(news_ctx.get("avg_score"), 0.0),
            },
        },
        "scanner_policy": {
            "candidate_sources": dict(scanner_source_policy or {}),
            "scanner_bias": dict(scanner_bias_context or {}),
            "priority_tilts": [str(x) for x in list(scanner_priority or [])],
            "score_weights": facade._strategy_policy_score_weights(),
            "filters": {
                "max_volatility_for_entry": facade._to_float(entry_policy.get("max_volatility_for_entry"), 0.12),
                "min_feature_coverage": 0,
                "min_confidence_for_entry": facade._to_float(entry_policy.get("min_confidence_for_entry"), 0.35),
            },
            "ranking_rules": {
                "allow_repeat_symbol": True,
                "repeat_symbol_penalty": facade._to_float(facade.os.getenv("SCANNER_REPEAT_SYMBOL_PENALTY", "0.0"), 0.0),
            },
        },
        "entry_policy": dict(entry_policy),
        "monitor_policy": {
            "entry_policy": dict(monitor_entry_policy or {}),
            "position_guards": dict(monitor_policy or {}),
            "adaptive_exit": dict(exit_policy or {}),
            "hard_risk_rails": {
                "hard_stop_pct": facade._to_float(facade.os.getenv("EXIT_POLICY_STOP_LOSS_PCT", "0.03"), 0.03),
                "max_stop_pct_cap": facade._to_float(facade.os.getenv("STRATEGY_POLICY_MAX_STOP_PCT_CAP", "0.10"), 0.10),
                "use_eod_flat": facade._is_trueish(effective_use_eod_flat),
            },
        },
        "decision_policy": {
            "use_strategy_v1_engine": False,
            "allow_score_override": False,
            "score_override_scope": "disabled",
            "strategy_v1_name": "",
            "strategy_variant_hint": "unified_ai_strategist",
        },
        "operator_explain": {
            "why_this_playbook": (
                f"playbook={str(playbook or 'defensive')} regime={str(market_regime or 'neutral')} "
                f"sentiment={str(market_sentiment or 'neutral')}"
            ),
            "why_this_risk_tone": (
                f"risk_tone={str(risk_tone or 'normal')} guidance={str(monitor_guidance or 'defensive_exit')}"
            ),
            "what_changes_next": str(macro_stress_overlay.get("reason") or ""),
        },
    }
