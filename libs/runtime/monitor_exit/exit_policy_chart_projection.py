"""Exit-policy chart/pnl/candidate condition projections (pure; trigger precedence stays in evaluate_exit_policy).

Second Pass (P1.5) intra-function extraction from `libs/runtime/exit_policy.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def exit_chart_out(chart_context_summary, p, *, facade):
    out: facade.Dict[str, facade.Any] = {
        "evaluated": True,
        "triggered": False,
        "reason": "",
        "hold_block_reason": "",
        "max_runup_pct": None,
        "peak_drawdown_from_peak": None,
        "peak_drawdown_armed": False,
        "peak_drawdown_mode": "",
        "peak_drawdown_blocked": False,
        "peak_drawdown_block_reason": "",
        "peak_drawdown_profit_floor_required_pct": None,
        "peak_drawdown_profit_floor_met": False,
        "peak_drawdown_profit_protection_urgent": False,
        "peak_drawdown_profit_protection_reason": "",
        "final_peak_drawdown_ratio": None,
        "peak_drawdown_source": "",
        "risk_reward_take_profit_target_pct": None,
        "resistance_price": None,
        "resistance_price_source": "",
        "resistance_distance_pct": None,
        "profit_time_stop_peak_giveback_pct": None,
        "partial_exit": False,
        "exit_qty": None,
        "exit_qty_fraction": None,
        "partial_take_profit_taken": False,
        "profit_ladder_level_pct": None,
        "profit_ladder_level_index": None,
        "risk_reward_take_profit_rung": None,
        "volume_ratio": None,
        "execution_strength": None,
        "trade_strength": None,
        "opening_gap_chase_observed": False,
        "etf_deviation_pct": None,
        "etf_deviation_source": "",
        "etf_premium_take_profit_score": 0.0,
        "etf_premium_take_profit_armed": False,
        "exit_trigger_metric_name": "",
        "exit_trigger_metric_value": None,
        "exit_trigger_metric_source": "",
        "vwap_breakdown_confirmation_required": False,
        "vwap_breakdown_confirmed": False,
        "vwap_breakdown_confirmation_pending": False,
        "vwap_breakdown_confirmation_reason": "",
        "vwap_breakdown_consecutive_bars": 0,
        "vwap_breakdown_low_break_confirmed": False,
        "vwap_breakdown_volume_confirmed": False,
        "intraday_low_break_confirmation_required": False,
        "intraday_low_break_confirmed": False,
        "intraday_low_break_confirmation_pending": False,
        "intraday_low_break_confirmation_reason": "",
        "intraday_low_break_consecutive_bars": 0,
        "intraday_low_break_low_break_confirmed": False,
        "intraday_low_break_volume_confirmed": False,
        "intraday_low_break_min_hold_blocked": False,
        "protective_exit_floor_blocked": False,
        "protective_exit_floor_blocked_reason": "",
        "protective_exit_hard_invalidation": False,
        "protective_exit_hard_invalidation_reason": "",
        "protective_exit_hard_invalidation_suppressed_by_cost_floor": False,
        "protective_exit_hard_invalidation_suppressed_reason": "",
        "pnl_ratio": None,
        "raw_pnl_ratio": None,
        "gross_pnl_ratio": None,
        "technical_pnl_ratio": None,
        "effective_pnl_ratio": None,
        "stop_pnl_ratio": None,
        "stop_pnl_ratio_source": "",
        "hard_stop_pnl_ratio": None,
        "hard_stop_pnl_ratio_source": "",
        "cost_drag_pressure": False,
        "cost_drag_pressure_pct": None,
        "cost_drag_pressure_reason": "",
        "stop_loss_cost_drag_blocked": False,
        "stop_loss_cost_drag_blocked_reason": "",
        "expected_exit_price": None,
        "expected_exit_price_source": "",
        "expected_exit_price_fallback_used": False,
        "expected_exit_quote_rejected": bool(p.get("expected_exit_quote_rejected")),
        "expected_exit_quote_rejected_reason": str(p.get("expected_exit_quote_rejected_reason") or ""),
        "expected_exit_quote_observed_epoch": p.get("expected_exit_quote_observed_epoch"),
        "expected_exit_quote_age_sec": p.get("expected_exit_quote_age_sec"),
        "expected_exit_quote_price_divergence_pct": p.get("expected_exit_quote_price_divergence_pct"),
        "expected_exit_slippage_buffer_pct": None,
        "expected_exit_pnl_ratio": None,
        "expected_exit_net_pnl_ratio": None,
        "expected_exit_profit_floor_met": False,
        "expected_exit_profit_floor_gap_pct": None,
        "expected_exit_profit_floor_blocked": False,
        "expected_exit_profit_floor_blocked_reason": "",
        "raw_price": None,
        "technical_price": None,
        "technical_price_source": "",
        "effective_price": None,
        "effective_price_source": "",
        "account_current_price": None,
        "account_current_price_source": "",
        "account_unrealized_pnl": None,
        "account_mark_price": None,
        "account_mark_price_source": "",
        "account_pnl_ratio": None,
        "account_pnl_ratio_source": "",
        "pnl_crosscheck_gap": None,
        "price_crosscheck_gap": None,
        "pnl_crosscheck_applied": False,
        "pnl_crosscheck_reason": "",
        "price_anomaly_flag": False,
        "price_anomaly_reason": "",
        "pnl_fallback_applied": False,
        "fallback_price_source": "",
        "account_crosscheck": {},
        "chart_context_available": bool(chart_context_summary.get("available")),
        "chart_context_summary": dict(chart_context_summary),
        "structure_breakdown_signal": str(chart_context_summary.get("structure_breakdown_signal") or ""),
        "exit_threshold_source": str(
            p.get("final_exit_threshold_source")
            or p.get("policy_source")
            or p.get("effective_policy_source")
            or "effective_policy"
        ),
        "thresholds": {
            "hard_stop_pct": facade._clamp_non_negative(facade._to_float(p.get("hard_stop_pct"), 0.0)),
            "stop_loss_pct": facade._clamp_non_negative(facade._to_float(p.get("stop_loss_pct"), 0.03)),
            "take_profit_pct": facade._clamp_non_negative(facade._to_float(p.get("take_profit_pct"), 0.05)),
            "partial_take_profit_pct": facade._clamp_non_negative(facade._to_float(p.get("partial_take_profit_pct"), 0.0)),
            "partial_take_profit_fraction": facade._clamp_non_negative(
                facade._to_float(p.get("partial_take_profit_fraction"), 0.0)
            ),
            "profit_ladder_levels_pct": facade._to_float_list(p.get("profit_ladder_levels_pct")),
            "profit_ladder_fraction": facade._clamp_non_negative(facade._to_float(p.get("profit_ladder_fraction"), 0.0)),
            "risk_reward_take_profit_r": facade._clamp_non_negative(facade._to_float(p.get("risk_reward_take_profit_r"), 0.0)),
            "risk_reward_take_profit_rungs": facade._to_float_list(p.get("risk_reward_take_profit_rungs")),
            "risk_reward_take_profit_fraction": facade._clamp_non_negative(
                facade._to_float(p.get("risk_reward_take_profit_fraction"), 0.0)
            ),
            "risk_reward_take_profit_min_pct": facade._clamp_non_negative(
                facade._to_float(p.get("risk_reward_take_profit_min_pct"), 0.0)
            ),
            "vwap_extension_take_profit_pct": facade._clamp_non_negative(
                facade._to_float(p.get("vwap_extension_take_profit_pct"), 0.0)
            ),
            "vwap_extension_take_profit_min_pct": facade._clamp_non_negative(
                facade._to_float(p.get("vwap_extension_take_profit_min_pct"), 0.0)
            ),
            "resistance_take_profit_near_pct": facade._clamp_non_negative(
                facade._to_float(p.get("resistance_take_profit_near_pct"), 0.0)
            ),
            "resistance_take_profit_min_pct": facade._clamp_non_negative(
                facade._to_float(p.get("resistance_take_profit_min_pct"), 0.0)
            ),
            "profit_time_stop_sec": max(0, int(facade._to_float(p.get("profit_time_stop_sec"), 0.0))),
            "profit_time_stop_min_pct": facade._clamp_non_negative(facade._to_float(p.get("profit_time_stop_min_pct"), 0.0)),
            "profit_time_stop_peak_giveback_pct": facade._clamp_non_negative(
                facade._to_float(p.get("profit_time_stop_peak_giveback_pct"), 0.0)
            ),
            "volume_exhaustion_take_profit_min_pct": facade._clamp_non_negative(
                facade._to_float(p.get("volume_exhaustion_take_profit_min_pct"), 0.0)
            ),
            "volume_exhaustion_volume_ratio_max": facade._clamp_non_negative(
                facade._to_float(p.get("volume_exhaustion_volume_ratio_max"), 0.0)
            ),
            "volume_exhaustion_strength_max": facade._clamp_non_negative(
                facade._to_float(p.get("volume_exhaustion_strength_max"), 0.0)
            ),
            "opening_gap_profit_take_min_pct": facade._clamp_non_negative(
                facade._to_float(p.get("opening_gap_profit_take_min_pct"), 0.0)
            ),
            "opening_gap_profit_take_window_sec": max(
                0,
                int(facade._to_float(p.get("opening_gap_profit_take_window_sec"), 0.0)),
            ),
            "opening_gap_profit_take_fraction": facade._clamp_non_negative(
                facade._to_float(p.get("opening_gap_profit_take_fraction"), 0.0)
            ),
            "etf_premium_take_profit_enabled": facade._to_bool(
                p.get("etf_premium_take_profit_enabled"),
                True,
            ),
            "etf_premium_take_profit_pct": facade._clamp_non_negative(
                facade._to_float(p.get("etf_premium_take_profit_pct"), facade.DEFAULT_PREMIUM_TRIGGER_PCT)
            ),
            "etf_premium_take_profit_min_pct": facade._clamp_non_negative(
                facade._to_float(p.get("etf_premium_take_profit_min_pct"), 0.0)
            ),
            "cost_aware_profit_floor_enabled": facade._to_bool(p.get("cost_aware_profit_floor_enabled"), False),
            "round_trip_cost_floor_pct": facade._clamp_non_negative(facade._to_float(p.get("round_trip_cost_floor_pct"), 0.0)),
            "min_net_profit_buffer_pct": facade._clamp_non_negative(facade._to_float(p.get("min_net_profit_buffer_pct"), 0.0)),
            "cost_aware_profit_floor_pct": facade._clamp_non_negative(
                facade._to_float(p.get("cost_aware_profit_floor_pct"), 0.0)
            ),
            "cost_aware_profit_floor_use_expected_exit": facade._to_bool(
                p.get("cost_aware_profit_floor_use_expected_exit"),
                True,
            ),
        "sell_slippage_buffer_pct": facade._clamp_non_negative(
            facade._to_float(p.get("sell_slippage_buffer_pct"), 0.0)
        ),
            "min_expected_net_profit_pct": facade._clamp_non_negative(
                facade._to_float(
                    p.get("min_expected_net_profit_pct"),
                    facade._to_float(p.get("min_net_profit_buffer_pct"), 0.0),
                )
            ),
            "max_hold_sec": max(0, int(facade._to_float(p.get("max_hold_sec"), 0))),
            "time_stop_sec": max(
                0,
                int(
                    facade._to_float(
                        p.get("time_stop_sec"),
                        facade._to_float(p.get("max_hold_sec"), 0.0),
                    )
                ),
            ),
            "trailing_stop_pct": facade._clamp_non_negative(facade._to_float(p.get("trailing_stop_pct"), 0.0)),
            "vol_expansion_ratio": facade._clamp_non_negative(facade._to_float(p.get("vol_expansion_ratio"), 0.0)),
            "news_shock_threshold": facade._clamp_non_negative(facade._to_float(p.get("news_shock_threshold"), 0.0)),
            "peak_drawdown_exit_pct": facade._clamp_non_negative(facade._to_float(p.get("peak_drawdown_exit_pct"), 0.0)),
            "profit_protection_activation_pct": facade._clamp_non_negative(
                facade._to_float(
                    p.get(
                        "profit_protection_activation_pct",
                        p.get("peak_drawdown_activation_pct", 0.008),
                    ),
                    0.008,
                )
            ),
            "peak_drawdown_mode": str(p.get("peak_drawdown_mode") or "profit_protection").strip().lower(),
            "confirm_required_for_peak_drawdown": max(
                1,
                int(
                    facade._to_float(
                        p.get("confirm_required_for_peak_drawdown"),
                        2.0,
                    )
                ),
            ),
            "vwap_breakdown_pct": facade._clamp_non_negative(facade._to_float(p.get("vwap_breakdown_pct"), 0.0)),
            "vwap_breakdown_confirm_bars": max(
                1,
                int(facade._to_float(p.get("vwap_breakdown_confirm_bars"), 2.0)),
            ),
            "vwap_breakdown_min_hold_sec": max(
                0,
                int(facade._to_float(p.get("vwap_breakdown_min_hold_sec"), 120.0)),
            ),
            "intraday_low_break_pct": facade._clamp_non_negative(facade._to_float(p.get("intraday_low_break_pct"), 0.0)),
            "intraday_low_break_min_hold_sec": max(
                0,
                int(facade._to_float(p.get("intraday_low_break_min_hold_sec"), 60.0)),
            ),
            "intraday_low_break_confirm_bars": max(
                1,
                int(facade._to_float(p.get("intraday_low_break_confirm_bars"), 2.0)),
            ),
            "trend_strength_floor": facade._to_float(p.get("trend_strength_floor"), 0.0),
            "eod_flat_cutoff_min": max(0, int(facade._to_float(p.get("eod_flat_cutoff_min"), 10))),
        },
    }
    out["peak_drawdown_mode"] = str(out["thresholds"].get("peak_drawdown_mode") or "profit_protection")
    return (out,)
