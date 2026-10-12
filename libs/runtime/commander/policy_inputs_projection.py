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
    if memory_feedback_enabled is None:
        memory_feedback_enabled = facade._env_bool(
            "USE_STRATEGY_MEMORY_FEEDBACK",
            facade._commander_default_bool("USE_STRATEGY_MEMORY_FEEDBACK", True),
        )
    performance_memory_enabled = _existing_value("strategist", "performance_memory", "enabled")
    if performance_memory_enabled is None:
        performance_memory_enabled = facade._env_bool(
            "USE_STRATEGY_PERFORMANCE_MEMORY",
            facade._commander_default_bool("USE_STRATEGY_PERFORMANCE_MEMORY", True),
        )
    strategy_memory_persist_enabled = _existing_value("strategist", "performance_memory", "persist_enabled")
    if strategy_memory_persist_enabled is None:
        strategy_memory_persist_enabled = facade._env_bool(
            "STRATEGY_MEMORY_PERSIST_ENABLED",
            facade._commander_default_bool("STRATEGY_MEMORY_PERSIST_ENABLED", True),
        )
    commander_memory_usage_disabled = _existing_value("commander", "memory_usage", "disabled")
    if commander_memory_usage_disabled is None:
        commander_memory_usage_disabled = facade._env_bool(
            "COMMANDER_MEMORY_USAGE_DISABLED",
            facade._commander_default_bool("COMMANDER_MEMORY_USAGE_DISABLED", False),
        )
    strategist_memory_usage_disabled = _existing_value("strategist", "memory_usage", "disabled")
    if strategist_memory_usage_disabled is None:
        strategist_memory_usage_disabled = facade._env_bool(
            "STRATEGIST_MEMORY_USAGE_DISABLED",
            facade._commander_default_bool("STRATEGIST_MEMORY_USAGE_DISABLED", False),
        )
    post_scanner_refresh_enabled = _existing_value("commander", "route", "post_scanner_refresh_enabled")
    if post_scanner_refresh_enabled is None:
        post_scanner_refresh_enabled = facade._env_bool(
            "COMMANDER_POST_SCANNER_REFRESH_ENABLED",
            facade._commander_default_bool("COMMANDER_POST_SCANNER_REFRESH_ENABLED", True),
        )
    pre_entry_exit_sweep_enabled = _existing_value("commander", "route", "pre_entry_exit_sweep_enabled")
    if pre_entry_exit_sweep_enabled is None:
        pre_entry_exit_sweep_enabled = True
    risk_max_positions = facade._resolve_risk_max_positions(state)
    memory_bias_observation_only = facade._env_bool(
        "MEMORY_BIAS_OBSERVATION_ONLY",
        facade._commander_default_bool("MEMORY_BIAS_OBSERVATION_ONLY", True),
    )
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
    return (allow_legacy_rule, allow_legacy_strategy_v1, block_buy_when_open_position, cached_strategist_when_flat, commander_memory_usage_disabled, exit_policy_enabled, exit_policy_use_eod_flat, feedback_policy, memory_bias_observation_only, memory_feedback_enabled, monitor_only_when_holding, monitor_scoring_enabled, performance_memory_enabled, phase_text, post_scanner_refresh_enabled, pre_entry_exit_sweep_enabled, reporter_ai_review_enabled, risk_max_positions, route, strategist_memory_usage_disabled, strategy_memory_persist_enabled, strict_mode, trade_report_enabled, trade_report_generate_on_open)
