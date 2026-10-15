"""Commander behavior policy: applied-policy summary surface.

T4-A (P1.5 Third Pass): contiguous statement run / value expression of `graphs/commander_runtime.py::_resolve_commander_behavior_policy` moved verbatim into a
scanner projection Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
Scanner node are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def build_commander_applied_policy_summary(allow_legacy_rule, allow_legacy_strategy_v1, block_buy_when_open_position, buy_closeout_cutoff_min, cached_strategist_when_flat, carry_exit_policy_overrides, carry_policy_adjustments, carry_risk_bias, carry_risk_reason, carry_state, commander_memory_usage_disabled, default_execution_profile, eod_flat_cutoff_min, exit_confirm_ticks, exit_policy_enabled, exit_policy_use_eod_flat, feedback_policy, kiwoom_condition_limit, memory_bias_observation_only, memory_feedback_enabled, min_hold_seconds, monitor_only_when_holding, monitor_scoring_enabled, monitor_scoring_shadow_mode, monitor_scoring_threshold, performance_memory_enabled, phase_text, position_sizing_enabled, position_sizing_max_notional, position_sizing_max_qty, position_sizing_notional_ratio, position_sizing_risk_per_trade_ratio, post_exit_cooldown_sec, post_scanner_refresh_enabled, pre_entry_exit_sweep_enabled, reporter_ai_review_enabled, reporter_daily_execution_profile, reporter_daily_llm, reporter_intraday_execution_profile, reporter_intraday_llm, risk_max_positions, route, scanner_block_static_when_empty, scanner_include_change_rate, scanner_live_fetch, scanner_source_type, scanner_strict_only, sell_cooldown_sec, strategist_execution_profile, strategist_llm, strategist_memory_usage_disabled, strategy_memory_persist_enabled, strategy_memory_recent_runs, strict_mode, top_candidate_pool, trade_report_enabled, trade_report_generate_on_open, universe_asset_type, *, facade):
    return (
        {
            "selected_route": route,
            "runtime_phase": phase_text,
            "reporter_ai_review_enabled": bool(reporter_ai_review_enabled),
            "trade_report_enabled": bool(trade_report_enabled),
            "trade_report_generate_on_open": bool(trade_report_generate_on_open),
            "strategist_strict_mode": bool(strict_mode),
            "allow_legacy_rule": bool(allow_legacy_rule),
            "allow_legacy_strategy_v1": bool(allow_legacy_strategy_v1),
            "strategy_memory_feedback_enabled": bool(memory_feedback_enabled),
            "strategy_performance_memory_enabled": bool(performance_memory_enabled),
            "strategy_memory_persist_enabled": bool(strategy_memory_persist_enabled),
            "commander_memory_usage_disabled": bool(commander_memory_usage_disabled),
            "strategist_memory_usage_disabled": bool(strategist_memory_usage_disabled),
            "memory_bias_observation_only": bool(memory_bias_observation_only),
            "post_scanner_refresh_enabled": bool(post_scanner_refresh_enabled),
            "pre_entry_exit_sweep_enabled": bool(pre_entry_exit_sweep_enabled),
            "monitor_only_when_holding": bool(monitor_only_when_holding),
            "cached_strategist_when_flat": bool(cached_strategist_when_flat),
            "exit_policy_enabled": bool(exit_policy_enabled),
            "exit_policy_use_eod_flat": bool(exit_policy_use_eod_flat),
            "carry_state": carry_state,
            "carry_risk_bias": carry_risk_bias,
            "carry_risk_reason": carry_risk_reason,
            "carry_exit_policy_overrides": dict(carry_exit_policy_overrides),
            "carry_policy_adjustments": list(carry_policy_adjustments),
            "block_buy_when_open_position": bool(block_buy_when_open_position),
            "multi_position_enabled": bool(risk_max_positions > 1),
            "max_positions": int(risk_max_positions),
            "same_symbol_reentry_allowed": False,
            "pending_buy_same_symbol_allowed": False,
            "open_position_gate_mode": "max_positions",
            "buy_closeout_cutoff_min": max(
                facade._coerce_int(eod_flat_cutoff_min, 10),
                facade._coerce_int(buy_closeout_cutoff_min, facade._DEFAULT_BUY_CLOSEOUT_CUTOFF_MIN),
            ),
            "monitor_scoring_enabled": bool(monitor_scoring_enabled),
            "monitor_scoring_shadow_mode": bool(monitor_scoring_shadow_mode),
            "position_sizing_enabled": bool(position_sizing_enabled),
            "position_sizing_risk_per_trade_ratio": max(
                0.0,
                float(facade._runtime_float(position_sizing_risk_per_trade_ratio, 0.01)),
            ),
            "position_sizing_position_notional_ratio": max(
                0.0,
                float(facade._runtime_float(position_sizing_notional_ratio, 0.50)),
            ),
            "position_sizing_max_position_qty": max(1, facade._coerce_int(position_sizing_max_qty, 10)),
            "position_sizing_max_position_notional": max(
                0.0,
                float(facade._runtime_float(position_sizing_max_notional, 0.0)),
            ),
            "reporter_feedback_mode": str(feedback_policy.get("reporter_feedback_mode") or "auto"),
            "universe_fields": {
                "asset_type": str(universe_asset_type or "all_tradable").strip().lower() or "all_tradable",
            },
            "scanner_fields": {
                "source_type": facade.normalize_scanner_source_type(scanner_source_type),
                "strict_only": bool(scanner_strict_only),
                "block_static_when_empty": bool(scanner_block_static_when_empty),
                "live_fetch": bool(scanner_live_fetch),
                "include_change_rate": bool(scanner_include_change_rate),
            },
            "llm_profiles": {
                "strategist": {
                    "profile": str(strategist_llm.get("profile") or "balanced"),
                    "primary": str(strategist_llm.get("primary") or ""),
                    "fallback": str(strategist_llm.get("fallback") or ""),
                },
                "reporter_intraday": {
                    "profile": str(reporter_intraday_llm.get("profile") or "fast_free"),
                    "primary": str(reporter_intraday_llm.get("primary") or ""),
                    "fallback": str(reporter_intraday_llm.get("fallback") or ""),
                },
                "reporter_daily": {
                    "profile": str(reporter_daily_llm.get("profile") or "strong_reasoning"),
                    "primary": str(reporter_daily_llm.get("primary") or ""),
                    "fallback": str(reporter_daily_llm.get("fallback") or ""),
                },
            },
            "llm_execution_profiles": {
                "default": {
                    "profile_name": str(default_execution_profile.get("profile_name") or default_execution_profile.get("name") or "default_intraday"),
                    "temperature": float(facade._runtime_float(default_execution_profile.get("temperature"), 0.2)),
                    "max_tokens": max(256, facade._coerce_int(default_execution_profile.get("max_tokens"), 8192)),
                    "timeout_sec": max(1, facade._coerce_int(default_execution_profile.get("timeout_sec"), 15)),
                    "retry": {
                        "max_attempts": max(0, facade._coerce_int((default_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                        "backoff_sec": max(0.0, float(facade._runtime_float((default_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                    },
                },
                "strategist": {
                    "profile_name": str(strategist_execution_profile.get("profile_name") or strategist_execution_profile.get("name") or "balanced_reasoning"),
                    "temperature": float(facade._runtime_float(strategist_execution_profile.get("temperature"), 0.1)),
                    "max_tokens": max(256, facade._coerce_int(strategist_execution_profile.get("max_tokens"), 8192)),
                    "timeout_sec": max(1, facade._coerce_int(strategist_execution_profile.get("timeout_sec"), 15)),
                    "retry": {
                        "max_attempts": max(0, facade._coerce_int((strategist_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                        "backoff_sec": max(0.0, float(facade._runtime_float((strategist_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                    },
                },
                "reporter_intraday": {
                    "profile_name": str(reporter_intraday_execution_profile.get("profile_name") or reporter_intraday_execution_profile.get("name") or "concise_review"),
                    "temperature": float(facade._runtime_float(reporter_intraday_execution_profile.get("temperature"), 0.2)),
                    "max_tokens": max(256, facade._coerce_int(reporter_intraday_execution_profile.get("max_tokens"), 8192)),
                    "timeout_sec": max(1, facade._coerce_int(reporter_intraday_execution_profile.get("timeout_sec"), 15)),
                    "retry": {
                        "max_attempts": max(0, facade._coerce_int((reporter_intraday_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                        "backoff_sec": max(0.0, float(facade._runtime_float((reporter_intraday_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                    },
                },
                "reporter_daily": {
                    "profile_name": str(reporter_daily_execution_profile.get("profile_name") or reporter_daily_execution_profile.get("name") or "deep_review"),
                    "temperature": float(facade._runtime_float(reporter_daily_execution_profile.get("temperature"), 0.2)),
                    "max_tokens": max(256, facade._coerce_int(reporter_daily_execution_profile.get("max_tokens"), 8192)),
                    "timeout_sec": max(1, facade._coerce_int(reporter_daily_execution_profile.get("timeout_sec"), 15)),
                    "retry": {
                        "max_attempts": max(0, facade._coerce_int((reporter_daily_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                        "backoff_sec": max(0.0, float(facade._runtime_float((reporter_daily_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                    },
                },
            },
            "numeric_fields": {
                "post_exit_cooldown_sec": max(0, facade._coerce_int(post_exit_cooldown_sec, 180)),
                "sell_cooldown_sec": max(0, facade._coerce_int(sell_cooldown_sec, 300)),
                "min_hold_seconds": max(0, facade._coerce_int(min_hold_seconds, 600)),
                "exit_confirm_ticks": max(1, facade._coerce_int(exit_confirm_ticks, 2)),
                "eod_flat_cutoff_min": max(0, facade._coerce_int(eod_flat_cutoff_min, 10)),
                "buy_closeout_cutoff_min": max(
                    facade._coerce_int(eod_flat_cutoff_min, 10),
                    facade._coerce_int(buy_closeout_cutoff_min, facade._DEFAULT_BUY_CLOSEOUT_CUTOFF_MIN),
                ),
                "top_candidate_pool": max(1, facade._coerce_int(top_candidate_pool, 30)),
                "kiwoom_condition_limit": max(0, facade._coerce_int(kiwoom_condition_limit, 200)),
                "monitor_entry_scoring_threshold": max(0.0, float(facade._runtime_float(monitor_scoring_threshold, 3.0))),
                "position_sizing_enabled": bool(position_sizing_enabled),
                "position_sizing_risk_per_trade_ratio": max(
                    0.0,
                    float(facade._runtime_float(position_sizing_risk_per_trade_ratio, 0.01)),
                ),
                "position_sizing_position_notional_ratio": max(
                    0.0,
                    float(facade._runtime_float(position_sizing_notional_ratio, 0.50)),
                ),
                "position_sizing_max_position_qty": max(1, facade._coerce_int(position_sizing_max_qty, 10)),
                "position_sizing_max_position_notional": max(
                    0.0,
                    float(facade._runtime_float(position_sizing_max_notional, 0.0)),
                ),
                "strategy_memory_recent_runs": max(1, facade._coerce_int(strategy_memory_recent_runs, 12)),
            },
        }
    )
