"""Pure decision read models; effects and orchestration remain in runtime adapters."""
from __future__ import annotations
from typing import Any, Dict

def decision_context_readout(state, phase_value, status_value, path_value, preflight, runtime_fast_path, strategist_output, resilience, shadow_assessment, open_position_count, max_positions, entry_capacity_available, market_regime, strategist_fallback_used):
    strategist_rail_raw = strategist_output.get("market_regime_rail")
    strategist_rail_shadow = (
        strategist_output.get("market_regime_rail_shadow")
        if isinstance(strategist_output.get("market_regime_rail_shadow"), dict)
        else {}
    )
    strategist_input_quality = (
        strategist_output.get("strategist_input_quality")
        if isinstance(strategist_output.get("strategist_input_quality"), dict)
        else {}
    )
    input_quality_rail = (
        strategist_input_quality.get("market_regime_rail")
        if isinstance(strategist_input_quality.get("market_regime_rail"), dict)
        else {}
    )
    risk_off_policy = (
        strategist_output.get("risk_off_exception_policy")
        if isinstance(strategist_output.get("risk_off_exception_policy"), dict)
        else {}
    )
    if isinstance(strategist_rail_raw, dict):
        market_regime_rail = str(
            strategist_rail_raw.get("market_regime_rail")
            or strategist_rail_raw.get("rail_id")
            or strategist_rail_raw.get("rail")
            or ""
        )
    else:
        market_regime_rail = str(strategist_rail_raw or "")
    market_regime_rail = str(
        market_regime_rail
        or strategist_rail_shadow.get("market_regime_rail")
        or strategist_rail_shadow.get("rail_id")
        or input_quality_rail.get("market_regime_rail")
        or input_quality_rail.get("rail_id")
        or risk_off_policy.get("market_regime_rail")
        or state.get("market_regime_rail")
        or ""
    ).strip()
    rail_l = market_regime_rail.lower()
    rail_risk_off = bool("risk_off" in rail_l or "gap_down" in rail_l or "breadth_collapse" in rail_l)
    if rail_risk_off and market_regime != "risk_off":
        market_regime = "risk_off"
    macro_stress_overlay = (
        strategist_output.get("macro_stress_overlay")
        if isinstance(strategist_output.get("macro_stress_overlay"), dict)
        else {}
    )
    raw_stress_flags = list(macro_stress_overlay.get("stress_flags") or [])
    macro_stress_active = bool(macro_stress_overlay.get("active"))
    stress_flags = raw_stress_flags if macro_stress_active else []
    if str(phase_value or "").strip() == "preopen":
        session_bias = "preopen_context"
    elif str(phase_value or "").strip() == "closeout":
        session_bias = "closeout_control"
    elif open_position_count > 0 and not entry_capacity_available:
        session_bias = "position_management"
    elif open_position_count > 0 and entry_capacity_available:
        session_bias = "multi_position_selection"
    elif "cached" in str(path_value or ""):
        session_bias = "context_reuse"
    else:
        session_bias = "active_selection"

    runtime_status_blocked = str(status_value or "").strip().lower() in {"blocked", "preflight_blocked"}
    hard_runtime_blocked = bool(preflight.get("blocked")) or (
        bool(runtime_status_blocked) and not bool(entry_capacity_available)
    )
    if hard_runtime_blocked:
        risk_mode = "blocked"
    elif market_regime == "risk_off" or rail_risk_off or bool(stress_flags) or str(resilience.get("degrade_mode") or "").strip():
        risk_mode = "defensive"
    elif market_regime == "risk_on":
        risk_mode = "offensive"
    else:
        risk_mode = "balanced"
    return (entry_capacity_available, market_regime, market_regime_rail, max_positions, open_position_count, preflight, rail_risk_off, resilience, risk_mode, runtime_fast_path, session_bias, shadow_assessment, strategist_fallback_used, strategist_output, stress_flags)


def decision_overlay_blocker_counts_monitor_last_states(cache_age_sec_for_state, reuse_sec_for_state, cached_output_for_state, strategist_refresh_requested, state, open_position_count, entry_capacity_available, *, facade):
    is_cache_stale = cache_age_sec_for_state > reuse_sec_for_state

    if not cached_output_for_state:
        strategy_state = "INVALID"
    elif strategist_refresh_requested:
        strategy_state = "REBUILD_REQUIRED"
    elif is_cache_stale:
        strategy_state = "STALE"
    else:
        strategy_state = "ACTIVE"

    if facade._is_trueish(state.get("force_refresh_strategist")):
        strategy_selection_mode = "force_fresh"
    elif strategist_refresh_requested:
        strategy_selection_mode = "prefer_fresh"
    else:
        strategy_selection_mode = "prefer_cache"

    if open_position_count > 0 and not entry_capacity_available:
        strategist_invocation_mode = "SKIP_MONITOR_ONLY"
    elif not cached_output_for_state:
        strategist_invocation_mode = "RUN"
    elif strategist_refresh_requested and is_cache_stale:
        strategist_invocation_mode = "RUN_REFRESH"
    elif strategist_refresh_requested and not is_cache_stale:
        strategist_invocation_mode = "SKIP_USE_CACHE"
    elif open_position_count == 0 and is_cache_stale:
        strategist_invocation_mode = "RUN"
    else:
        strategist_invocation_mode = "SKIP_USE_CACHE"

    # Task 4: Monitor feedback and adaptive policy
    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    monitor_last_states = persisted.get("monitor_last_state_by_symbol") if isinstance(persisted.get("monitor_last_state_by_symbol"), dict) else {}
    
    recent_feedback = state.get("recent_strategy_feedback") if isinstance(state.get("recent_strategy_feedback"), dict) else {}
    recent_monitor_issues = list(recent_feedback.get("recent_monitor_issues") or [])
    
    blocker_counts = {}
    return (blocker_counts, monitor_last_states, recent_monitor_issues, strategist_invocation_mode, strategy_selection_mode, strategy_state)


def decision_rules_adaptive_feedback_allowed_adaptive_polic(blocker_counts, total_wait, avg_distance, near_ready_count, state, market_regime, market_regime_rail, risk_mode, open_position_count, preflight, stress_flags, resilience, applied_policy, max_positions, strategist_output, intraday_performance_circuit, *, facade):
    dominant_blocker = ""
    blocker_count = 0
    if blocker_counts:
        dominant_blocker = max(blocker_counts, key=blocker_counts.get)
        blocker_count = blocker_counts[dominant_blocker]
        
    avg_distance_to_ready = avg_distance / total_wait if total_wait > 0 else 0.0
    near_ready_flag = near_ready_count > 0
    failure_streak = blocker_count
    
    injected_feedback = state.get("mock_monitor_feedback")
    if isinstance(injected_feedback, dict):
        dominant_blocker = injected_feedback.get("dominant_blocker", dominant_blocker)
        blocker_count = injected_feedback.get("blocker_count", blocker_count)
        failure_streak = injected_feedback.get("failure_streak", failure_streak)
        near_ready_flag = injected_feedback.get("near_ready_flag", near_ready_flag)
        avg_distance_to_ready = injected_feedback.get("avg_distance_to_ready", avg_distance_to_ready)

    monitor_feedback = {
        "dominant_blocker": str(dominant_blocker),
        "blocker_count": int(blocker_count),
        "failure_streak": int(failure_streak),
        "near_ready_flag": bool(near_ready_flag),
        "avg_distance_to_ready": float(avg_distance_to_ready),
    }
    entry_control = facade._build_commander_entry_control(
        market_regime=market_regime,
        market_regime_rail=market_regime_rail,
        risk_mode=risk_mode,
        open_position_count=open_position_count,
        preflight=preflight,
        stress_flags=stress_flags,
        resilience=resilience,
        monitor_feedback=monitor_feedback,
        applied_policy=applied_policy,
        max_positions=max_positions,
        strategist_output=strategist_output,
        performance_circuit=intraday_performance_circuit,
    )

    adaptive_policy = {
        "entry_bias_adjustment": 0.0,
        "diversification_adjustment": 0.0,
        "reentry_penalty_adjustment": 0.0,
        "scan_aggressiveness": 0.0,
    }
    policy_adjustment_trace = []
    adaptive_feedback_allowed = str(entry_control.get("mode") or "") not in {
        "blocked_no_entry_expansion",
        "position_management_no_entry_expansion",
        "preserve_defensive_no_trade_ok",
        "preserve_guardrail_no_trade_ok",
        "risk_off_no_entry_expansion",
    }
    return (adaptive_feedback_allowed, adaptive_policy, entry_control, monitor_feedback, policy_adjustment_trace)


