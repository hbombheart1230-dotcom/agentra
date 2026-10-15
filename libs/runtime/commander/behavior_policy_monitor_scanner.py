"""Commander behavior policy: scanner memory-bias, source, candidate, Kiwoom and fallback fields.

T4-A (P1.5 Third Pass): contiguous statement run / value expression of `graphs/commander_runtime.py::_resolve_commander_behavior_policy` moved verbatim into a
scanner projection Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
Scanner node are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def build_scanner_behavior_policy(kiwoom_condition_limit, memory_bias_observation_only, scanner_block_static_when_empty, scanner_include_change_rate, scanner_live_fetch, scanner_source_type, scanner_strict_only, top_candidate_pool, *, facade):
    return (
        {
            "memory_bias": {
                "observation_only": bool(memory_bias_observation_only),
                "policy_source": "commander_applied_policy",
            },
            "source": {
                "type": facade.normalize_scanner_source_type(scanner_source_type),
                "policy_source": "commander_applied_policy",
            },
            "candidate": {
                "top_pool": max(1, facade._coerce_int(top_candidate_pool, 30)),
                "policy_source": "commander_applied_policy",
            },
            "kiwoom": {
                "condition_limit": max(0, facade._coerce_int(kiwoom_condition_limit, 200)),
                "strict_only": bool(scanner_strict_only),
                "live_fetch": bool(scanner_live_fetch),
                "include_change_rate": bool(scanner_include_change_rate),
                "policy_source": "commander_applied_policy",
            },
            "fallback": {
                "block_static_when_empty": bool(scanner_block_static_when_empty),
                "policy_source": "commander_applied_policy",
            },
        }
    )

def build_monitor_behavior_policy(block_buy_when_open_position, buy_closeout_cutoff_min, carry_exit_policy_overrides, carry_policy_adjustments, carry_risk_bias, carry_risk_reason, carry_state, eod_flat_cutoff_min, exit_confirm_ticks, exit_policy_enabled, exit_policy_use_eod_flat, memory_bias_observation_only, min_hold_seconds, monitor_scoring_enabled, monitor_scoring_shadow_mode, monitor_scoring_threshold, position_sizing_enabled, position_sizing_lot_size, position_sizing_max_notional, position_sizing_max_qty, position_sizing_min_qty, position_sizing_notional_ratio, position_sizing_risk_per_trade_ratio, risk_max_positions, *, facade):
    return (
        {
            "memory_bias": {
                "observation_only": bool(memory_bias_observation_only),
                "policy_source": "commander_applied_policy",
            },
            "hold": {
                "min_hold_seconds": max(0, facade._coerce_int(min_hold_seconds, 600)),
                "policy_source": "commander_applied_policy",
            },
            "exit": {
                "enabled": bool(exit_policy_enabled),
                "confirm_ticks": max(1, facade._coerce_int(exit_confirm_ticks, 2)),
                "eod_flat": {
                    "enabled": bool(exit_policy_use_eod_flat),
                    "cutoff_min": max(0, facade._coerce_int(eod_flat_cutoff_min, 10)),
                },
                "policy_overrides": dict(carry_exit_policy_overrides),
                "policy_adjustments": list(carry_policy_adjustments),
                "carry_state": carry_state,
                "carry_risk_bias": carry_risk_bias,
                "carry_risk_reason": carry_risk_reason,
                "policy_source": "commander_applied_policy",
            },
            "entry": {
                "block_buy_when_open_position": bool(block_buy_when_open_position),
                "multi_position": {
                    "enabled": bool(risk_max_positions > 1),
                    "max_positions": int(risk_max_positions),
                    "same_symbol_reentry_allowed": False,
                    "pending_buy_same_symbol_allowed": False,
                    "open_position_gate_mode": "max_positions",
                    "policy_source": "commander_applied_policy",
                },
                "buy_closeout_cutoff_min": max(
                    facade._coerce_int(eod_flat_cutoff_min, 10),
                    facade._coerce_int(buy_closeout_cutoff_min, facade._DEFAULT_BUY_CLOSEOUT_CUTOFF_MIN),
                ),
                "position_sizing": {
                    "enabled": bool(position_sizing_enabled),
                    "risk_per_trade_ratio": max(
                        0.0,
                        float(facade._runtime_float(position_sizing_risk_per_trade_ratio, 0.01)),
                    ),
                    "position_notional_ratio": max(
                        0.0,
                        float(facade._runtime_float(position_sizing_notional_ratio, 0.50)),
                    ),
                    "max_position_qty": max(1, facade._coerce_int(position_sizing_max_qty, 10)),
                    "max_position_notional": max(
                        0.0,
                        float(facade._runtime_float(position_sizing_max_notional, 0.0)),
                    ),
                    "min_position_qty": max(1, facade._coerce_int(position_sizing_min_qty, 1)),
                    "lot_size": max(1, facade._coerce_int(position_sizing_lot_size, 1)),
                    "policy_source": "commander_applied_policy",
                },
                "scoring": {
                    "enabled": bool(monitor_scoring_enabled),
                    "shadow_mode": bool(monitor_scoring_shadow_mode),
                    "threshold": max(0.0, float(facade._runtime_float(monitor_scoring_threshold, 3.0))),
                    "entry_threshold": max(0.0, float(facade._runtime_float(monitor_scoring_threshold, 3.0))),
                    "policy_source": "commander_applied_policy",
                },
            },
        }
    )
