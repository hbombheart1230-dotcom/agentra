from __future__ import annotations
from typing import Any, Dict, List


def build_commander_shadow_artifact_summary(
    state: Dict[str, Any],
    *,
    mode: str,
    phase: str,
    path: str,
    status: str,
    reason: str = "",
 facade) -> Dict[str, Any]:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    try:
        return build_commander_shadow_artifact(
            state,
            mode=str(mode or ""),
            phase=str(phase or ""),
            path=str(path or ""),
            status=str(status or "ok"),
            reason=str(reason or ""),
        )
    except Exception:
        return {}


def build_commander_shadow_artifact(
    state: Dict[str, Any],
    *,
    mode: str,
    phase: str,
    path: str,
    status: str,
    reason: str = "",
 facade) -> Dict[str, Any]:
    globals().update({key: getattr(facade, key) for key in dir(facade) if key not in globals()})
    observations = _commander_shadow_observations(state, path=path)
    actual_runtime = _commander_shadow_actual_runtime(state, path=path)
    monitor_gate_details = _commander_shadow_monitor_gate_details(state)
    context_delta_summary = _commander_shadow_context_delta_summary(state, observations=observations)
    no_trade_reason_code = _commander_shadow_no_trade_reason_code(
        state,
        observations=observations,
        actual_runtime=actual_runtime,
        path=path,
    )
    strategist_action_recommendation = _commander_shadow_strategist_recommendation(
        no_trade_reason_code=no_trade_reason_code,
        observations=observations,
    )
    llm_call_advice = _commander_shadow_llm_call_advice(
        strategist_action_recommendation=strategist_action_recommendation,
        observations=observations,
        state=state,
    )
    suggested_action = _commander_shadow_suggested_action(
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
        no_trade_reason_code=no_trade_reason_code,
    )
    next_action_recommendation = _commander_shadow_next_action_recommendation(
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
        no_trade_reason_code=no_trade_reason_code,
        actual_runtime=actual_runtime,
    )
    reason_summary = _commander_shadow_reason_summary(
        no_trade_reason_code=no_trade_reason_code,
        observations=observations,
        actual_runtime=actual_runtime,
    )
    recommendation_gap = _commander_shadow_recommendation_gap(
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
        actual_runtime=actual_runtime,
    )
    pre_strategist_shadow_snapshot = _commander_shadow_pre_strategist_snapshot(
        state=state,
        observations=observations,
        context_delta_summary=context_delta_summary,
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
    )
    post_strategist_assessment = _commander_shadow_post_strategist_assessment(
        state=state,
        actual_runtime=actual_runtime,
        context_delta_summary=context_delta_summary,
        recommendation_gap=recommendation_gap,
    )
    post_monitor_assessment = _commander_shadow_post_monitor_assessment(
        actual_runtime=actual_runtime,
        monitor_gate_details=monitor_gate_details,
    )
    end_of_cycle_summary = _commander_shadow_end_of_cycle_summary(
        no_trade_reason_code=no_trade_reason_code,
        reason_summary=reason_summary,
        actual_runtime=actual_runtime,
        next_action_recommendation=next_action_recommendation,
        recommendation_gap=recommendation_gap,
    )
    symbol = _clip(
        _dict(state.get("selected")).get("symbol")
        or _dict(state.get("monitor_output")).get("selected_symbol")
        or _dict(state.get("monitor_exit")).get("symbol"),
        max_len=24,
    )
    artifact = _base_output(state, agent="commander", symbol=symbol, status=status or "ok")
    artifact.update(
        {
            "schema_version": "commander_shadow.v1",
            "mode": "shadow",
            "cycle_id": _clip(state.get("cycle_id"), max_len=80),
            "observed_runtime_mode": _clip(mode, max_len=40),
            "observed_runtime_path": _clip(path, max_len=80),
            "decision": "OBSERVE_ONLY",
            "strategist_action_recommendation": strategist_action_recommendation,
            "llm_call_advice": llm_call_advice,
            "suggested_action": suggested_action,
            "next_action_recommendation": next_action_recommendation,
            "no_trade_reason_code": no_trade_reason_code,
            "reason_summary": reason_summary,
            "observations": observations,
            "actual_runtime": actual_runtime,
            "monitor_gate_details": monitor_gate_details,
            "context_delta_summary": context_delta_summary,
            "pre_strategist_shadow_snapshot": pre_strategist_shadow_snapshot,
            "post_strategist_assessment": post_strategist_assessment,
            "post_monitor_assessment": post_monitor_assessment,
            "end_of_cycle_summary": end_of_cycle_summary,
            "comparison_summary": (
                f"recommended={strategist_action_recommendation}/{llm_call_advice}, "
                f"next={next_action_recommendation}, "
                f"observed_monitor={actual_runtime.get('monitor_decision') or 'WAIT'}, "
                f"observed_executor={actual_runtime.get('executor_action') or 'NONE'}, "
                f"gap={recommendation_gap}"
            ),
            "integrated_into_commander_decision": True,
            "integration_version": "phase1_2",
            "integration_role": "upstream_assessment",
            "reason": _clip(reason or state.get("runtime_status") or "", max_len=220),
            "shadow_only": True,
            "generated_at": _utc_now_iso(),
        }
    )
    artifact["validation"] = validate_artifact(artifact)
    return artifact
