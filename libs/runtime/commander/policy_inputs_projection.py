"""Commander behavior-policy input resolution (source precedence and fallbacks unchanged; env/default reads stay in the caller).

Second Pass (P1.5) intra-function extraction from `graphs/commander_runtime.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def behavior_input_allow_legacy_rule_allow_legacy_strategy(selected_route, state, phase, _existing_value, *, facade):
    route = str(selected_route or facade._derive_commander_selected_route(state) or "").strip().lower() or "unknown"
    phase_text = str(phase or state.get("runtime_phase") or "session").strip().lower() or "session"
    feedback_policy = facade._resolve_commander_reporter_feedback_policy(
        state,
        selected_route=route,
        phase=phase_text,
    )
    reporter_ai_review_enabled = _existing_value("reporter", "ai_review", "enabled")
    if reporter_ai_review_enabled is None:
        reporter_ai_review_enabled = False
    trade_report_enabled = _existing_value("reporter", "trade_report", "enabled")
    if trade_report_enabled is None:
        trade_report_enabled = True
    trade_report_generate_on_open = _existing_value("reporter", "trade_report", "generate_on_open")
    if trade_report_generate_on_open is None:
        trade_report_generate_on_open = False
    strict_mode = _existing_value("strategist", "runtime", "strict_mode")
    if strict_mode is None:
        strict_mode = True
    allow_legacy_rule = _existing_value("strategist", "runtime", "allow_legacy_rule")
    if allow_legacy_rule is None:
        allow_legacy_rule = False
    allow_legacy_strategy_v1 = _existing_value("strategist", "runtime", "allow_legacy_strategy_v1")
    if allow_legacy_strategy_v1 is None:
        allow_legacy_strategy_v1 = False
    memory_feedback_enabled = _existing_value("strategist", "memory_feedback", "enabled")
    return (allow_legacy_rule, allow_legacy_strategy_v1, feedback_policy, memory_feedback_enabled, phase_text, reporter_ai_review_enabled, route, strict_mode, trade_report_enabled, trade_report_generate_on_open)


def behavior_input_block_buy_when_open_position_buy_closeou(_existing_value, risk_max_positions, *, facade):
    monitor_only_when_holding = _existing_value("commander", "route", "monitor_only_when_holding")
    if monitor_only_when_holding is None:
        monitor_only_when_holding = True
    cached_strategist_when_flat = _existing_value("commander", "route", "cached_strategist_when_flat")
    if cached_strategist_when_flat is None:
        cached_strategist_when_flat = False
    exit_policy_enabled = _existing_value("monitor", "exit", "enabled")
    if exit_policy_enabled is None:
        exit_policy_enabled = True
    exit_policy_use_eod_flat = _existing_value("monitor", "exit", "eod_flat", "enabled")
    if exit_policy_use_eod_flat is None:
        exit_policy_use_eod_flat = True
    block_buy_when_open_position = _existing_value("monitor", "entry", "block_buy_when_open_position")
    if block_buy_when_open_position is None:
        block_buy_when_open_position = risk_max_positions <= 1
    monitor_scoring_enabled = _existing_value("monitor", "entry", "scoring", "enabled")
    if monitor_scoring_enabled is None:
        monitor_scoring_enabled = False
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
    return (block_buy_when_open_position, buy_closeout_cutoff_min, cached_strategist_when_flat, eod_flat_cutoff_min, exit_confirm_ticks, exit_policy_enabled, exit_policy_use_eod_flat, kiwoom_condition_limit, min_hold_seconds, monitor_only_when_holding, monitor_scoring_enabled, monitor_scoring_shadow_mode, monitor_scoring_threshold, position_sizing_enabled, position_sizing_risk_per_trade_ratio, post_exit_cooldown_sec, scanner_block_static_when_empty, scanner_include_change_rate, scanner_live_fetch, scanner_source_type, scanner_strict_only, sell_cooldown_sec, top_candidate_pool, universe_asset_type)
