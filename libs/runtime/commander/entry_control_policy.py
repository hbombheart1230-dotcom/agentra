"""Commander entry-control construction (pure policy over strategist/monitor/portfolio state).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _build_commander_entry_control_r3_impl(
    *,
    market_regime,
    market_regime_rail,
    risk_mode,
    open_position_count,
    preflight,
    stress_flags,
    resilience,
    monitor_feedback,
    applied_policy,
    max_positions,
    strategist_output,
    performance_circuit,
    facade,
):
    blocker = str(monitor_feedback.get("dominant_blocker") or "").strip().lower()
    failure_streak = max(0, facade._coerce_int(monitor_feedback.get("failure_streak"), 0))
    near_ready = bool(monitor_feedback.get("near_ready_flag"))
    avg_distance = facade._runtime_float(monitor_feedback.get("avg_distance_to_ready"), 0.0)
    regime = str(market_regime or "").strip().lower()
    rail = str(market_regime_rail or "").strip().lower()
    mode = str(risk_mode or "").strip().lower()
    rail_risk_off = bool("risk_off" in rail or "gap_down" in rail or "breadth_collapse" in rail)
    market_supportive = (
        mode in {"balanced", "offensive"}
        and regime in {"", "neutral", "risk_on"}
        and not rail_risk_off
        and not bool(stress_flags)
        and not str(resilience.get("degrade_mode") or "").strip()
        and not bool(preflight.get("blocked"))
    )
    no_entry_expansion = bool(
        regime == "risk_off"
        or rail_risk_off
        or mode in {"defensive", "blocked"}
        or bool(stress_flags)
        or str(resilience.get("degrade_mode") or "").strip()
        or bool(preflight.get("blocked"))
    )
    expandable_blocker = blocker in facade._ENTRY_CONTROL_POOL_EXPAND_BLOCKERS
    repeated_block = bool(blocker and failure_streak >= 3)
    max_positions = max(1, int(max_positions or 1))
    capacity_remaining = max(0, int(max_positions) - int(open_position_count))
    strategist_data = strategist_output if isinstance(strategist_output, dict) else {}
    raw_watch_policy = facade._extract_strategist_candidate_watch_policy(strategist_data)
    candidate_watch_proposal = facade._normalize_candidate_watch_proposal_for_commander(
        raw_watch_policy,
        playbook=str(strategist_data.get("final_playbook") or strategist_data.get("playbook") or ""),
        tactical_strategy=str(strategist_data.get("tactical_strategy") or ""),
    )
    perf_circuit = dict(performance_circuit or {})
    base: Dict[str, Any] = {
        "schema_version": "commander_entry_control.v1",
        "source": "commander_decision",
        "mode": "baseline",
        "decision": "preserve_default_entry_scope",
        "market_regime": regime or str(market_regime or ""),
        "market_regime_rail": rail or str(market_regime_rail or ""),
        "risk_mode": mode or str(risk_mode or ""),
        "market_supportive": bool(market_supportive),
        "dominant_blocker": blocker,
        "failure_streak": int(failure_streak),
        "near_ready_flag": bool(near_ready),
        "avg_distance_to_ready": float(avg_distance),
        "max_priority_rank": 10,
        "max_runner_ups": 9,
        "allow_dynamic_entry_band": False,
        "adaptive_max_extended_from_vwap_pct": None,
        "max_extended_from_vwap_pct_cap": 0.10,
        "scan_aggressiveness_floor": 0.0,
        "reason": "baseline_entry_scope",
        "open_position_count": int(open_position_count),
        "max_positions": int(max_positions),
        "capacity_remaining": int(capacity_remaining),
        "open_position_gate_mode": "max_positions",
        "performance_circuit": perf_circuit,
    }
    if candidate_watch_proposal:
        base["candidate_watch_policy_detected"] = True
        base["candidate_watch_policy_source"] = str(candidate_watch_proposal.get("source") or "")
        base["mode"] = "strategy_watch_policy"
        base["decision"] = "apply_strategy_candidate_watch_policy"
        base["reason"] = str(candidate_watch_proposal.get("reason") or "strategy_candidate_watch_policy")
    if int(open_position_count) >= int(max_positions):
        base.update(
            {
                "mode": "max_positions_no_entry_expansion",
                "decision": "preserve_existing_position_focus",
                "reason": "max_positions_reached",
            }
        )
        if candidate_watch_proposal:
            base = facade._apply_candidate_watch_proposal_to_entry_control(
                base,
                candidate_watch_proposal,
                rank_cap=1,
                force_disable_cascade=True,
                clamp_reason="max_positions_reached",
            )
        return base
    hard_entry_blocked = bool(preflight.get("blocked")) or (mode == "blocked" and capacity_remaining <= 0)
    if hard_entry_blocked:
        base.update(
            {
                "mode": "blocked_no_entry_expansion",
                "decision": "preserve_blocked_entry_scope",
                "reason": "preflight_or_runtime_blocked",
            }
        )
        if candidate_watch_proposal:
            base = facade._apply_candidate_watch_proposal_to_entry_control(
                base,
                candidate_watch_proposal,
                rank_cap=1,
                force_disable_cascade=True,
                clamp_reason="preflight_or_runtime_blocked",
            )
        return base
    if bool(perf_circuit.get("active")):
        base.update(
            {
                "mode": "intraday_performance_circuit",
                "decision": "degrade_new_entries_after_intraday_losses",
                "max_priority_rank": 1,
                "max_runner_ups": 0,
                "cascade_enabled": False,
                "allow_dynamic_entry_band": False,
                "reason": str(perf_circuit.get("reason") or "intraday_performance_circuit_active"),
                "candidate_watch_policy_effect": "commander_intraday_performance_circuit",
                "candidate_watch_policy_clamp_reason": str(
                    perf_circuit.get("reason") or "intraday_performance_circuit_active"
                ),
            }
        )
        return base
    if candidate_watch_proposal:
        rank_cap = facade._candidate_watch_rank_cap(
            proposal=candidate_watch_proposal,
            market_regime=regime or str(market_regime or ""),
            market_regime_rail=rail or str(market_regime_rail or ""),
            risk_mode=mode or str(risk_mode or ""),
            stress_flags=list(stress_flags or []),
            resilience=dict(resilience or {}),
        )
        base = facade._apply_candidate_watch_proposal_to_entry_control(
            base,
            candidate_watch_proposal,
            rank_cap=rank_cap,
            force_disable_cascade=rank_cap <= 1,
            clamp_reason=f"market_regime={regime or str(market_regime or '')}:risk_mode={mode or str(risk_mode or '')}",
        )
    if repeated_block and no_entry_expansion:
        base.update(
            {
                "mode": "risk_off_no_entry_expansion",
                "decision": "preserve_conservative_entry_scope",
                "max_priority_rank": 1,
                "max_runner_ups": 0,
                "cascade_enabled": False,
                "allow_dynamic_entry_band": False,
                "reason": f"risk_off_or_defensive_repeated_blocker_no_expansion:{blocker}:streak={failure_streak}",
                "candidate_watch_policy_effect": "commander_risk_off_no_entry_expansion",
                "candidate_watch_policy_clamp_reason": (
                    f"risk_off_or_defensive_repeated_blocker_no_expansion:{blocker}:streak={failure_streak}"
                ),
            }
        )
        if candidate_watch_proposal:
            base = facade._apply_candidate_watch_proposal_to_entry_control(
                base,
                candidate_watch_proposal,
                rank_cap=1,
                force_disable_cascade=True,
                clamp_reason="risk_off_or_defensive_no_entry_expansion",
            )
            base.update(
                {
                    "max_priority_rank": 1,
                    "max_runner_ups": 0,
                    "cascade_enabled": False,
                    "allow_dynamic_entry_band": False,
                    "decision": "preserve_conservative_entry_scope",
                    "reason": f"risk_off_or_defensive_repeated_blocker_no_expansion:{blocker}:streak={failure_streak}",
                }
            )
        return base
    if repeated_block and not market_supportive:
        base.update(
            {
                "mode": "preserve_defensive_no_trade_ok",
                "decision": "preserve_conservative_entry_scope",
                "reason": "market_or_risk_mode_not_supportive_for_entry_expansion",
            }
        )
        defensive_top3_ok = bool(expandable_blocker and capacity_remaining > 0 and failure_streak >= 3)
        if candidate_watch_proposal:
            base = facade._apply_candidate_watch_proposal_to_entry_control(
                base,
                candidate_watch_proposal,
                rank_cap=3,
                force_disable_cascade=not defensive_top3_ok,
                clamp_reason="market_or_risk_mode_not_supportive_for_entry_expansion",
            )
        if defensive_top3_ok:
            base.update(
                {
                    "decision": "defensive_top3_candidate_cascade",
                    "max_priority_rank": max(3, facade._clamp_int(base.get("max_priority_rank"), 3, 1, 10)),
                    "max_runner_ups": 2,
                    "cascade_enabled": True,
                    "reason": f"defensive_repeated_expandable_blocker_top3:{blocker}:streak={failure_streak}",
                    "candidate_watch_policy_effect": (
                        "commander_defensive_top3_repeated_blocker"
                        if candidate_watch_proposal
                        else str(base.get("candidate_watch_policy_effect") or "")
                    ),
                    "candidate_watch_policy_clamp_reason": (
                        f"defensive_repeated_expandable_blocker_top3:{blocker}:streak={failure_streak}"
                    ),
                }
            )
        return base
    if repeated_block and not expandable_blocker:
        base.update(
            {
                "mode": "preserve_guardrail_no_trade_ok",
                "decision": "preserve_non_expandable_guardrail",
                "reason": f"dominant_blocker_not_expandable:{blocker}",
            }
        )
        return base
    if repeated_block and market_supportive and expandable_blocker:
        max_priority_rank = 10 if failure_streak >= 5 else 8
        scan_floor = 0.10 if failure_streak >= 5 else 0.05
        if candidate_watch_proposal and str(candidate_watch_proposal.get("tactical_strategy") or "").strip().lower() != "defensive_observe":
            current_rank = facade._clamp_int(base.get("max_priority_rank"), max_priority_rank, 1, 10)
            max_priority_rank = max(int(current_rank), int(max_priority_rank))
        base.update(
            {
                "mode": "expand_when_market_ok",
                "decision": "expand_candidate_pool",
                "max_priority_rank": int(max_priority_rank),
                "max_runner_ups": int(max_priority_rank - 1),
                "cascade_enabled": bool(max_priority_rank > 1),
                "scan_aggressiveness_floor": float(scan_floor),
                "reason": (
                    f"market_supportive_repeated_blocker:{blocker}:"
                    f"streak={failure_streak}"
                ),
            }
        )
        if candidate_watch_proposal:
            base["candidate_watch_policy_clamp_reason"] = (
                f"market_supportive_repeated_blocker:{blocker}:streak={failure_streak}"
            )
            base["candidate_watch_policy_effect"] = "commander_expanded_repeated_blocker"
        if blocker in facade._ENTRY_CONTROL_DYNAMIC_BAND_BLOCKERS:
            received_ceiling = facade._extract_commander_policy_vwap_ceiling(applied_policy)
            target_floor = 0.10 if failure_streak >= 5 and (near_ready or avg_distance >= 0.70) else 0.08
            target = min(0.10, max(0.05, target_floor))
            base.update(
                {
                    "decision": "expand_candidate_pool_and_dynamic_entry_band",
                    "allow_dynamic_entry_band": True,
                    "adaptive_max_extended_from_vwap_pct": round(float(target), 6),
                    "received_max_extended_from_vwap_pct": round(float(received_ceiling), 6),
                }
            )
        return base
    if repeated_block:
        base.update(
            {
                "mode": "observe_repeated_blocker",
                "decision": "preserve_default_entry_scope",
                "reason": f"repeated_blocker_observed:{blocker}",
            }
        )
    return base
