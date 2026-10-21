"""Commander deterministic strategy-choice and monitor-feedback projections (same rule order).

Second Pass (P1.5) intra-function extraction from `graphs/commander_runtime.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


from libs.agents.commander.projections.decision_context_read_model import decision_rules_adaptive_feedback_allowed_adaptive_polic


def decision_rules_decision_summary_observations(policy_adjustment_trace, entry_control, adaptive_policy, adaptive_feedback_allowed, observations, open_position_count, max_positions, source_refs, source_priority, decision_summary, *, facade):
    if str(entry_control.get("mode") or "") != "baseline":
        policy_adjustment_trace.append(
            f"entry_control={entry_control.get('mode')} -> {entry_control.get('reason')}"
        )

    scanner_policy = {
        "avoid_recent_symbol": False,
        "recent_symbol_penalty": round(max(0.0, 0.05 + adaptive_policy["reentry_penalty_adjustment"]), 6),
        "diversification_bias": round(
            max(0.0, (0.02 if adaptive_feedback_allowed else 0.0) + adaptive_policy["diversification_adjustment"]),
            6,
        ),
        "entry_bias_cap": round(max(0.0, 0.0 + adaptive_policy["entry_bias_adjustment"]), 6),
        "scan_aggressiveness": round(max(0.0, adaptive_policy["scan_aggressiveness"]), 6),
        "allow_same_symbol_reentry": True,
        "reentry_score_gap_threshold": 0.03,
        "market_representative_guard": {
            "enabled": True,
            "symbols": ["005930", "000660"],
            "penalty": 0.04,
            "max_penalty": 0.12,
            "near_tie_gap": 0.06,
            "top_value_dominance_min": 0.55,
            "weak_confirmation_max": 1,
            "strong_confirmation_min": 2,
            "bypass_when_strong_confirmation": True,
            "apply_when_top_value_only": True,
            "policy_source": "commander_default",
        },
        "max_priority_rank": int(entry_control.get("max_priority_rank") if entry_control.get("max_priority_rank") not in (None, "") else 10),
        "max_runner_ups": int(entry_control.get("max_runner_ups") if entry_control.get("max_runner_ups") not in (None, "") else 9),
        "entry_control": dict(entry_control),
    }
    observations = {
        **observations,
        "entry_control_mode": str(entry_control.get("mode") or ""),
        "entry_control_decision": str(entry_control.get("decision") or ""),
        "entry_control_reason": str(entry_control.get("reason") or ""),
        "entry_control_max_priority_rank": int(entry_control.get("max_priority_rank") if entry_control.get("max_priority_rank") not in (None, "") else 10),
        "entry_control_dynamic_band": bool(entry_control.get("allow_dynamic_entry_band")),
        "open_position_count": int(open_position_count),
        "max_positions": int(max_positions),
        "multi_position_capacity_remaining": max(0, int(max_positions) - int(open_position_count)),
    }
    source_refs = {
        **source_refs,
        "entry_control": {
            "source": "commander_decision.monitor_feedback",
            "dominant_blocker": str(entry_control.get("dominant_blocker") or ""),
            "failure_streak": int(entry_control.get("failure_streak") or 0),
            "market_supportive": bool(entry_control.get("market_supportive")),
            "mode": str(entry_control.get("mode") or ""),
        },
    }
    if "commander_entry_control" not in list(source_priority or []):
        source_priority = [*list(source_priority or []), "commander_entry_control"]
    if str(entry_control.get("mode") or "") not in {"", "baseline"}:
        decision_summary = (
            f"{decision_summary} Entry control {entry_control.get('mode')} "
            f"because {entry_control.get('reason')}."
        )
    return (decision_summary, observations, scanner_policy, source_priority, source_refs)


def decision_rules_current_monitor_entry_policy_summary_pri(shadow_runtime, applied_policy, applied_policy_meta, strategist_refresh_requested, open_position_refresh_context, strategist_invocation, commander_override, commander_carry_state, commander_carry_risk_bias, commander_carry_risk_reason, commander_session_open_recovery, strategist_refresh_context, *, facade):
    prior_context = dict(shadow_runtime.get("prior_context") or {}) if isinstance(shadow_runtime.get("prior_context"), dict) else {}
    prior_monitor_entry_policy_summary = (
        dict(prior_context.get("monitor_entry_policy_summary") or {})
        if isinstance(prior_context.get("monitor_entry_policy_summary"), dict)
        else {}
    )
    current_monitor_entry_policy_summary = dict(
        applied_policy_meta.get("monitor_entry_policy_summary")
        or facade._summarize_monitor_entry_policy(applied_policy)
        or {}
    )
    if (
        strategist_refresh_requested
        and open_position_refresh_context
        and not current_monitor_entry_policy_summary
        and prior_monitor_entry_policy_summary
    ):
        current_monitor_entry_policy_summary = dict(prior_monitor_entry_policy_summary)
    strategist_refresh_evaluated = bool(
        str(commander_override.get("override_action") or "").strip().lower() == "strategist_refresh"
        or strategist_invocation == "RUN_REFRESH"
    )
    strategist_refresh_policy_delta_fields = (
        facade._monitor_entry_policy_delta_fields(
            prior_monitor_entry_policy_summary,
            current_monitor_entry_policy_summary,
        )
        if strategist_refresh_evaluated
        else []
    )
    if strategist_refresh_requested:
        strategist_refresh_context = {
            **dict(strategist_refresh_context or {}),
            "prior_monitor_entry_policy_summary": dict(prior_monitor_entry_policy_summary),
            "current_monitor_entry_policy_summary": dict(current_monitor_entry_policy_summary),
            "carry_state": commander_carry_state,
            "carry_risk_bias": commander_carry_risk_bias,
            "carry_risk_reason": commander_carry_risk_reason,
            "session_open_recovery_assessment": dict(commander_session_open_recovery),
        }
    strategist_refresh_effective = bool(
        strategist_refresh_evaluated and bool(strategist_refresh_policy_delta_fields)
    )
    return (current_monitor_entry_policy_summary, prior_monitor_entry_policy_summary, strategist_refresh_context, strategist_refresh_effective, strategist_refresh_evaluated, strategist_refresh_policy_delta_fields)
