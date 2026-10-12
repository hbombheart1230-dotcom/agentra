"""Commander behavior-policy route/execution/stop/size normalization (same fallbacks).

Second Pass (P1.5) intra-function extraction from `graphs/commander_runtime.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def behavior_norm_buy_closeout_cutoff_min_eod_flat_cutoff(_existing_value, *, facade):
    monitor_scoring_shadow_mode = _existing_value("monitor", "entry", "scoring", "shadow_mode")
    if monitor_scoring_shadow_mode is None:
        monitor_scoring_shadow_mode = True
    post_exit_cooldown_sec = _existing_value("execution", "cooldowns", "post_exit_sec")
    if post_exit_cooldown_sec is None:
        post_exit_cooldown_sec = 180
    sell_cooldown_sec = _existing_value("execution", "cooldowns", "sell_sec")
    if sell_cooldown_sec is None:
        sell_cooldown_sec = 300
    min_hold_seconds = _existing_value("monitor", "hold", "min_hold_seconds")
    if min_hold_seconds is None:
        min_hold_seconds = 600
    exit_confirm_ticks = _existing_value("monitor", "exit", "confirm_ticks")
    if exit_confirm_ticks is None:
        exit_confirm_ticks = 2
    eod_flat_cutoff_min = _existing_value("monitor", "exit", "eod_flat", "cutoff_min")
    if eod_flat_cutoff_min is None:
        eod_flat_cutoff_min = 10
    buy_closeout_cutoff_min = _existing_value("monitor", "entry", "buy_closeout_cutoff_min")
    if buy_closeout_cutoff_min is None:
        buy_closeout_cutoff_min = max(
            facade._DEFAULT_BUY_CLOSEOUT_CUTOFF_MIN,
            facade._coerce_int(eod_flat_cutoff_min, 10),
        )
    top_candidate_pool = _existing_value("scanner", "candidate", "top_pool")
    if top_candidate_pool is None:
        top_candidate_pool = 30
    kiwoom_condition_limit = _existing_value("scanner", "kiwoom", "condition_limit")
    if kiwoom_condition_limit is None:
        kiwoom_condition_limit = 200
    scanner_source_type = _existing_value("scanner", "source", "type")
    if scanner_source_type in (None, ""):
        scanner_source_type = "kiwoom"
    scanner_strict_only = _existing_value("scanner", "kiwoom", "strict_only")
    if scanner_strict_only is None:
        scanner_strict_only = True
    scanner_strict_only = facade._is_trueish(scanner_strict_only)
    scanner_block_static_when_empty = _existing_value("scanner", "fallback", "block_static_when_empty")
    if scanner_block_static_when_empty is None:
        scanner_block_static_when_empty = True
    scanner_block_static_when_empty = facade._is_trueish(scanner_block_static_when_empty)
    scanner_live_fetch = _existing_value("scanner", "kiwoom", "live_fetch")
    if scanner_live_fetch is None:
        scanner_live_fetch = True
    scanner_live_fetch = facade._is_trueish(scanner_live_fetch)
    scanner_include_change_rate = _existing_value("scanner", "kiwoom", "include_change_rate")
    if scanner_include_change_rate is None:
        scanner_include_change_rate = True
    scanner_include_change_rate = facade._is_trueish(scanner_include_change_rate)
    universe_asset_type = _existing_value("universe", "asset_type")
    if universe_asset_type in (None, ""):
        universe_asset_type = "all_tradable"
    monitor_scoring_threshold = _existing_value("monitor", "entry", "scoring", "threshold")
    if monitor_scoring_threshold is None:
        monitor_scoring_threshold = 3
    position_sizing_enabled = _existing_value("monitor", "entry", "position_sizing", "enabled")
    if position_sizing_enabled is None:
        position_sizing_enabled = True
    position_sizing_risk_per_trade_ratio = _existing_value(
        "monitor",
        "entry",
        "position_sizing",
        "risk_per_trade_ratio",
    )
    if position_sizing_risk_per_trade_ratio is None:
        position_sizing_risk_per_trade_ratio = 0.01
    position_sizing_notional_ratio = _existing_value(
        "monitor",
        "entry",
        "position_sizing",
        "position_notional_ratio",
    )
    if position_sizing_notional_ratio is None:
        position_sizing_notional_ratio = 0.50
    position_sizing_max_qty = _existing_value("monitor", "entry", "position_sizing", "max_position_qty")
    if position_sizing_max_qty is None:
        position_sizing_max_qty = facade._coerce_int(facade.os.getenv("MAX_ORDER_QTY") or facade.os.getenv("MAX_QTY"), 10)
    position_sizing_max_notional = _existing_value("monitor", "entry", "position_sizing", "max_position_notional")
    if position_sizing_max_notional is None:
        position_sizing_max_notional = facade._runtime_float(
            facade.os.getenv("MAX_ORDER_NOTIONAL") or facade.os.getenv("MAX_NOTIONAL"),
            1_000_000.0,
        )
    position_sizing_min_qty = _existing_value("monitor", "entry", "position_sizing", "min_position_qty")
    if position_sizing_min_qty is None:
        position_sizing_min_qty = 1
    position_sizing_lot_size = _existing_value("monitor", "entry", "position_sizing", "lot_size")
    if position_sizing_lot_size is None:
        position_sizing_lot_size = 1
    strategy_memory_recent_runs = _existing_value("strategist", "memory_feedback", "recent_runs")
    if strategy_memory_recent_runs is None:
        strategy_memory_recent_runs = 12
    return (buy_closeout_cutoff_min, eod_flat_cutoff_min, exit_confirm_ticks, kiwoom_condition_limit, min_hold_seconds, monitor_scoring_shadow_mode, monitor_scoring_threshold, position_sizing_enabled, position_sizing_lot_size, position_sizing_max_notional, position_sizing_max_qty, position_sizing_min_qty, position_sizing_notional_ratio, position_sizing_risk_per_trade_ratio, post_exit_cooldown_sec, scanner_block_static_when_empty, scanner_include_change_rate, scanner_live_fetch, scanner_source_type, scanner_strict_only, sell_cooldown_sec, strategy_memory_recent_runs, top_candidate_pool, universe_asset_type)


def behavior_norm_carry_exit_policy_overrides_carry_policy(_existing_value, commander_override, state, *, facade):
    strategist_llm_profile = str(_existing_value("llm", "strategist", "profile") or "balanced").strip().lower() or "balanced"
    reporter_intraday_profile = str(_existing_value("llm", "reporter", "intraday", "profile") or "fast_free").strip().lower() or "fast_free"
    reporter_daily_profile = str(_existing_value("llm", "reporter", "daily", "profile") or "strong_reasoning").strip().lower() or "strong_reasoning"
    strategist_llm = facade.resolve_model_profile(strategist_llm_profile, default_profile="balanced")
    reporter_intraday_llm = facade.resolve_model_profile(reporter_intraday_profile, default_profile="fast_free")
    reporter_daily_llm = facade.resolve_model_profile(reporter_daily_profile, default_profile="strong_reasoning")
    default_execution_profile_name = (
        str(
            _existing_value("llm", "execution_profile", "profile_name")
            or _existing_value("llm", "execution_profile", "name")
            or "default_intraday"
        ).strip().lower()
        or "default_intraday"
    )
    default_execution_profile = facade.resolve_execution_profile(
        default_execution_profile_name,
        default_profile="default_intraday",
        defaults={
            "profile_name": "default_intraday",
            "name": "default_intraday",
            "temperature": 0.2,
            "max_tokens": 8192,
            "timeout_sec": 15,
            "retry": {"max_attempts": 2, "backoff_sec": 0.0},
            "retry_max": 2,
            "retry_backoff_sec": 0.0,
        },
    )
    strategist_execution_profile_name = (
        str(_existing_value("llm", "strategist", "execution_profile", "name") or "balanced_reasoning").strip().lower()
        or "balanced_reasoning"
    )
    reporter_intraday_execution_profile_name = (
        str(_existing_value("llm", "reporter", "intraday", "execution_profile", "name") or "concise_review").strip().lower()
        or "concise_review"
    )
    reporter_daily_execution_profile_name = (
        str(_existing_value("llm", "reporter", "daily", "execution_profile", "name") or "deep_review").strip().lower()
        or "deep_review"
    )
    strategist_execution_profile = facade.resolve_execution_profile(
        strategist_execution_profile_name,
        default_profile="balanced_reasoning",
        defaults={
            "profile_name": "balanced_reasoning",
            "name": "balanced_reasoning",
            "temperature": 0.1,
            "max_tokens": 8192,
            "timeout_sec": 15,
            "retry": {
                "max_attempts": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
                "backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
            },
            "retry_max": 2,
            "retry_backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
        },
    )
    reporter_intraday_execution_profile = facade.resolve_execution_profile(
        reporter_intraday_execution_profile_name,
        default_profile="concise_review",
        defaults={
            "profile_name": "concise_review",
            "name": "concise_review",
            "temperature": 0.2,
            "max_tokens": 8192,
            "timeout_sec": max(1, facade._coerce_int(default_execution_profile.get("timeout_sec"), 15)),
            "retry": {
                "max_attempts": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
                "backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
            },
            "retry_max": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
            "retry_backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
        },
    )
    reporter_daily_execution_profile = facade.resolve_execution_profile(
        reporter_daily_execution_profile_name,
        default_profile="deep_review",
        defaults={
            "profile_name": "deep_review",
            "name": "deep_review",
            "temperature": 0.2,
            "max_tokens": 8192,
            "timeout_sec": max(1, facade._coerce_int(default_execution_profile.get("timeout_sec"), 15)),
            "retry": {
                "max_attempts": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
                "backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
            },
            "retry_max": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
            "retry_backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
        },
    )
    carry_state = str(commander_override.get("carry_state") or "").strip().lower()
    carry_risk_bias = str(commander_override.get("carry_risk_bias") or "").strip().lower()
    carry_risk_reason = str(commander_override.get("carry_risk_reason") or "")
    override_reason = str(commander_override.get("override_reason") or "").strip().lower()
    hold_repeat_count_max = max(0, facade._coerce_int(commander_override.get("hold_repeat_count_max"), 0))
    effective_loss_ratio_min = float(facade._runtime_float(commander_override.get("effective_loss_ratio_min"), 0.0))
    session_open_recovery = (
        dict(commander_override.get("session_open_recovery_assessment") or {})
        if isinstance(commander_override.get("session_open_recovery_assessment"), dict)
        else {}
    )
    market_context = state.get("market_context") if isinstance(state.get("market_context"), dict) else {}
    raw_minutes_to_close = market_context.get("minutes_to_close")
    minutes_to_close = None if raw_minutes_to_close in (None, "") else float(facade._runtime_float(raw_minutes_to_close, 0.0))
    carry_exit_policy_overrides: facade.Dict[str, facade.Any] = {}
    carry_policy_adjustments: list[str] = []
    return (carry_exit_policy_overrides, carry_policy_adjustments, carry_risk_bias, carry_risk_reason, carry_state, default_execution_profile, effective_loss_ratio_min, hold_repeat_count_max, minutes_to_close, override_reason, reporter_daily_execution_profile, reporter_daily_llm, reporter_intraday_execution_profile, reporter_intraday_llm, session_open_recovery, strategist_execution_profile, strategist_llm)
