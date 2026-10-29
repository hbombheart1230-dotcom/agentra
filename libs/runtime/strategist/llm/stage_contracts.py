"""Pure stage-specific Strategist LLM response contracts.

The public Strategist facade delegates here so contract ownership remains
independent from node orchestration.
"""

from __future__ import annotations


def build_stage_specific_contract(call_kind, base_contract):
    if call_kind == "selected_symbol_tactical_refresh":
        return {
            "selected_symbol_decision": "watch_rank1|avoid_rank1|watch_rank1_with_tighter_gates|cascade_to_runner_up|no_trade",
            "target_symbol": "005930",
            "target_rank": 1,
            "runner_up_order": ["000660", "035420"],
            "monitor_instruction": {
                "watch_intensity": "normal|strict|aggressive",
                "required_confirmations": ["vwap_reclaim", "net_cost_hurdle_pass", "volume_confirmation"],
                "avoid_if": ["fails_to_hold_vwap", "net_expected_edge_below_cost", "opening_gap_chase_without_pullback"],
            },
            "entry_policy_delta": {
                "tighten_confidence_threshold": False,
                "require_prev_close_context": True,
                "require_cost_hurdle": True,
            },
            "memory_usage": {
                "status": "used|disabled|insufficient|stale",
                "sample_count": 0,
                "confidence": "low|medium|high",
                "data_quality": "ok|stale|insufficient",
                "effect": "neutral|supportive|cautionary",
                "reason": "string",
            },
            "market_regime_rail": "risk_off_breadth_collapse|global_risk_off_pressure|risk_on_supportive|neutral_mixed|macro_packet_unavailable",
            "news_quality": {
                "status": "ok|partial|weak",
                "headline_count": 0,
                "candidate_headline_count": 0,
                "market_headline_count": 0,
                "issues": ["string"],
            },
            "risk_off_exception_conditions": ["cost_floor_pass", "relative_strength_leader", "volume_confirmation"],
            "news_event_intelligence_usage": {
                "status": "used|ignored|insufficient",
                "used_event_ids": ["news_event_001"],
                "theme_watchlist": ["space_aerospace"],
                "symbol_watchlist": ["005930"],
                "reason": "string",
                "observation_only": True,
            },
            "commander_actionability": "advisory_only|policy_delta_allowed|hard_block_recommended",
            "confidence": 0.0,
            "reason": "string",
        }
    if call_kind == "stale_intraday_hold_review":
        return {
            "hold_review_decision": "hold|tighten_exit|exit_now|wait_until_next_check",
            "horizon_action": "maintain|shorten|extend|request_exit",
            "current_horizon": "scalp|intraday|overnight_probe|1_2day_swing",
            "proposed_horizon": "scalp|intraday|overnight_probe|1_2day_swing",
            "revised_hold_window": {"min_sec": 300, "target_sec": 1800, "max_sec": 14400},
            "exit_pressure": "low|medium|high",
            "thesis_status": "intact|weakened|broken",
            "evidence_confidence": "low|medium|high",
            "data_quality": "ok|partial|insufficient|stale",
            "monitor_adjustment": {
                "tighten_stop": True,
                "tighten_time_decay": True,
                "allow_profit_recovery_wait": False,
                "next_check_minutes": 5,
            },
            "priority_exit_triggers": ["vwap_breakdown", "time_decay"],
            "next_check_minutes": 5,
            "reason": "string",
        }
    if call_kind == "end_of_day_carry_review":
        return {
            "carry_review": [
                {
                    "symbol": "005930",
                    "decision": "carry_overnight|flatten_today|reduce_or_flatten",
                    "carry_confidence": "low|medium|high",
                    "required_next_day_plan": {
                        "gap_down_action": "exit_on_open|wait_first_5min|monitor_vwap",
                        "gap_up_action": "take_profit|trail|hold_if_vwap_supports",
                        "flat_open_action": "monitor_vwap_and_volume",
                    },
                    "reason": "string",
                }
            ],
            "portfolio_level_decision": "carry_allowed|flatten_all|carry_only_best_one",
            "risk_note": "string",
        }
    return base_contract
