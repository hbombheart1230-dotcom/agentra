"""Commander applied-policy resolution and behavior/reporter-feedback policy attachment (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _resolve_commander_applied_policy_r3_impl(state, *, facade):
    strategist_output = state.get("strategist_output") if isinstance(state.get("strategist_output"), dict) else {}
    strategy_policy = (
        dict(strategist_output.get("strategy_policy") or {})
        if isinstance(strategist_output.get("strategy_policy"), dict)
        else {}
    )
    strategy_monitor_policy = (
        dict(strategy_policy.get("monitor_policy") or {})
        if isinstance(strategy_policy.get("monitor_policy"), dict)
        else {}
    )
    default_policy = facade.build_default_monitor_entry_policy()

    candidate_policy: Dict[str, Any] = {}
    candidate_source = "default"
    if isinstance(strategist_output.get("monitor_entry_policy"), dict) and strategist_output.get("monitor_entry_policy"):
        candidate_policy = dict(strategist_output.get("monitor_entry_policy") or {})
        candidate_source = "strategist"
    elif isinstance(strategy_monitor_policy.get("entry_policy"), dict) and strategy_monitor_policy.get("entry_policy"):
        candidate_policy = dict(strategy_monitor_policy.get("entry_policy") or {})
        candidate_source = "strategy_policy.monitor_policy.entry_policy"
    elif isinstance(state.get("monitor_entry_policy"), dict) and state.get("monitor_entry_policy"):
        candidate_policy = dict(state.get("monitor_entry_policy") or {})
        candidate_source = "state.monitor_entry_policy"

    policy_source_hint = str(candidate_policy.get("policy_source") or "").strip()
    normalized_policy, normalized_meta = facade.normalize_monitor_entry_policy(
        candidate_policy or None,
        fallback_policy=default_policy,
        policy_source=policy_source_hint or ("strategist" if candidate_source == "strategist" else default_policy.policy_source),
    )
    override_reason = ""
    phase_text = str(
        state.get("runtime_phase")
        or state.get("phase")
        or state.get("market_clock_phase")
        or "session"
    ).strip().lower()
    try:
        open_position_count = facade._portfolio_open_position_count(state)
    except Exception:
        open_position_count = facade._coerce_int(state.get("open_position_count"), 0)
    if (
        not bool(normalized_policy.enabled)
        and int(open_position_count) <= 0
        and phase_text in {"", "session", "intraday"}
    ):
        normalized_policy = facade.MonitorEntryPolicy.from_mapping(
            {
                **normalized_policy.to_dict(),
                "enabled": True,
                "policy_source": str(normalized_policy.policy_source or policy_source_hint or candidate_source),
            }
        )
        override_reason = "flat_session_entry_policy_enabled_forced"

    validation_status = str(normalized_meta.get("status") or "ok")
    fallback_used = bool(normalized_meta.get("fallback_used"))
    fallback_reason = str(normalized_meta.get("fallback_reason") or "")
    partial_normalized = bool(normalized_meta.get("partial_normalized"))
    default_filled_fields = list(normalized_meta.get("default_filled_fields") or [])
    validation_missing_fields = list(
        normalized_meta.get("policy_validation_missing_fields")
        or normalized_meta.get("missing_fields")
        or []
    )
    validation_invalid_fields = list(
        normalized_meta.get("policy_validation_invalid_fields")
        or normalized_meta.get("invalid_fields")
        or []
    )
    if candidate_source == "strategist":
        validation_status = str(strategist_output.get("policy_validation_status") or validation_status or "ok")
        fallback_used = bool(
            strategist_output.get("policy_fallback_used")
            if strategist_output.get("policy_fallback_used") is not None
            else fallback_used
        )
        fallback_reason = str(strategist_output.get("policy_fallback_reason") or fallback_reason or "")
        partial_normalized = bool(
            strategist_output.get("policy_partial_normalized")
            if strategist_output.get("policy_partial_normalized") is not None
            else partial_normalized
        )
        default_filled_fields = list(
            strategist_output.get("policy_default_filled_fields")
            or default_filled_fields
            or []
        )
        validation_missing_fields = list(
            strategist_output.get("policy_validation_missing_fields")
            or validation_missing_fields
            or []
        )
        validation_invalid_fields = list(
            strategist_output.get("policy_validation_invalid_fields")
            or validation_invalid_fields
            or []
        )

    applied_policy = facade.build_monitor_entry_policy_bundle(
        threshold_policy=normalized_policy,
        playbook=str(strategist_output.get("playbook") or ""),
        monitor_guidance=str(strategist_output.get("monitor_guidance") or ""),
        risk_tone=str(strategist_output.get("risk_tone") or ""),
        trade_aggressiveness=str(strategist_output.get("trade_aggressiveness") or ""),
        interpretation_policy=(
            dict(candidate_policy.get("interpretation_policy") or {})
            if isinstance(candidate_policy.get("interpretation_policy"), dict)
            else None
        ),
    )
    policy_source = str(applied_policy.get("policy_source") or policy_source_hint or candidate_source or default_policy.policy_source)
    if not candidate_policy:
        policy_source = "default"
        validation_status = str(normalized_meta.get("status") or "ok")
        fallback_used = bool(normalized_meta.get("fallback_used") or True)
        fallback_reason = str(normalized_meta.get("fallback_reason") or "no_strategist_policy_available")
        partial_normalized = bool(normalized_meta.get("partial_normalized"))
        default_filled_fields = list(normalized_meta.get("default_filled_fields") or [])
        validation_missing_fields = list(
            normalized_meta.get("policy_validation_missing_fields")
            or normalized_meta.get("missing_fields")
            or []
        )
        validation_invalid_fields = list(
            normalized_meta.get("policy_validation_invalid_fields")
            or normalized_meta.get("invalid_fields")
            or []
        )

    source_chain = [candidate_source or "default", "validation"]
    if fallback_used:
        source_chain.append("default_fallback")
    if override_reason:
        source_chain.append("commander_entry_enabled_guard")
    source_chain.append("commander_confirmed")
    source_chain = [str(x) for x in source_chain if str(x or "").strip()]

    return {
        "applied_policy": dict(applied_policy),
        "policy_source": policy_source,
        "policy_validation_status": validation_status,
        "policy_fallback_used": bool(fallback_used),
        "policy_fallback_reason": fallback_reason,
        "policy_partial_normalized": bool(partial_normalized),
        "policy_default_filled_fields": list(default_filled_fields),
        "policy_validation_missing_fields": list(validation_missing_fields),
        "policy_validation_invalid_fields": list(validation_invalid_fields),
        "override_reason": override_reason,
        "applied_policy_source_chain": source_chain,
        "monitor_entry_policy_summary": facade._summarize_monitor_entry_policy(applied_policy),
    }


def _attach_commander_behavior_policy_r3_impl(state, *, selected_route, phase, facade):
    behavior_policy = facade._resolve_commander_behavior_policy(
        state,
        selected_route=selected_route,
        phase=phase,
    )
    applied_policy = dict(state.get("applied_policy") or {}) if isinstance(state.get("applied_policy"), dict) else {}
    for section_name in ("execution", "llm", "reporter", "strategist", "commander", "scanner", "monitor", "universe", "policy_sources"):
        section_value = behavior_policy.get(section_name)
        if not isinstance(section_value, dict):
            continue
        existing = dict(applied_policy.get(section_name) or {}) if isinstance(applied_policy.get(section_name), dict) else {}
        applied_policy[section_name] = facade._merge_nested_policy_dict(existing, section_value)
    applied_policy["reporter_feedback_mode"] = str(
        ((behavior_policy.get("strategist") or {}).get("reporter_feedback_mode") or "auto")
    )
    applied_policy["reporter_feedback_mode_source"] = str(
        ((behavior_policy.get("strategist") or {}).get("reporter_feedback_mode_source") or "commander_applied_policy")
    )
    applied_policy["reporter_feedback_mode_reason"] = str(
        ((behavior_policy.get("strategist") or {}).get("reporter_feedback_mode_reason") or "")
    )
    state["applied_policy"] = applied_policy
    state["commander_behavior_policy"] = dict(behavior_policy)
    state["commander_applied_policy_summary"] = dict(behavior_policy.get("commander_applied_policy_summary") or {})
    return state


def _attach_commander_reporter_feedback_policy_r3_impl(state, *, selected_route, phase, facade):
    feedback_policy = facade._resolve_commander_reporter_feedback_policy(
        state,
        selected_route=selected_route,
        phase=phase,
    )
    state = facade._attach_commander_behavior_policy(
        state,
        selected_route=selected_route,
        phase=phase,
    )
    state["commander_reporter_feedback_policy"] = dict(feedback_policy)
    return state


def _extract_commander_policy_vwap_ceiling_r3_impl(applied_policy, *, facade):
    raw_policy = (
        facade.extract_monitor_entry_policy_mapping(applied_policy)
        if isinstance(applied_policy, dict)
        else {}
    )
    raw_value = raw_policy.get(
        "max_extended_from_vwap_pct",
        raw_policy.get("entry_max_extended_from_vwap_pct"),
    )
    value = facade._runtime_float(raw_value, 0.0)
    return float(value if value > 0.0 else 0.08)


def _dedupe_reason_list_r3_impl(value, defaults, *, facade):
    out: list[str] = []
    allowed_defaults = {str(item).strip().lower() for item in defaults if str(item).strip()}
    source = value if isinstance(value, list) else []
    for item in source:
        text = str(item or "").strip().lower()
        if not text:
            continue
        if allowed_defaults and text not in allowed_defaults:
            continue
        if text not in out:
            out.append(text)
    for item in defaults:
        text = str(item or "").strip().lower()
        if text and text not in out:
            out.append(text)
    return out


def _resolve_profit_protection_activation_ratio_r3_impl(state, *, facade):
    for root in (
        state.get("applied_policy") if isinstance(state.get("applied_policy"), dict) else {},
        state.get("policy") if isinstance(state.get("policy"), dict) else {},
    ):
        monitor = root.get("monitor") if isinstance(root.get("monitor"), dict) else {}
        exit_policy = monitor.get("exit") if isinstance(monitor.get("exit"), dict) else {}
        for key in (
            "profit_protection_activation_pct",
            "partial_take_profit_pct",
            "cost_aware_profit_floor_pct",
        ):
            value = facade._runtime_float(exit_policy.get(key), 0.0)
            if value > 0.0:
                return float(value)
    return 0.008


def _position_current_profit_ratio_r3_impl(*, raw_price_ratio, account_pnl_ratio, price_anomaly, facade):
    if raw_price_ratio is not None:
        return float(raw_price_ratio)
    if account_pnl_ratio is not None and not price_anomaly:
        return float(account_pnl_ratio)
    return None
