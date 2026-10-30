from __future__ import annotations
from typing import Any, Dict


def pre_strategist_snapshot(
    *,
    state: Dict[str, Any],
    observations: Dict[str, Any],
    context_delta_summary: Dict[str, Any],
    strategist_action_recommendation: str,
    llm_call_advice: str,
    facade,
) -> Dict[str, Any]:
    prior = facade._dict(facade._dict(state.get("commander_shadow_runtime")).get("prior_context"))
    return {
        "market_changed": observations.get("market_changed"),
        "repeated_same_context": observations.get("repeated_same_context"),
        "last_llm_status": observations.get("last_llm_status"),
        "prior_symbol": facade._clip(prior.get("selected_symbol"), max_len=24),
        "prior_playbook": facade._clip(prior.get("playbook"), max_len=40),
        "strategist_action_recommendation": strategist_action_recommendation,
        "llm_call_advice": llm_call_advice,
        "reason": facade._clip(
            f"context_delta={context_delta_summary.get('signal_changed')} market_changed={observations.get('market_changed')} repeated={observations.get('repeated_same_context')}",
            max_len=180,
        ),
    }



def post_strategist_assessment(
    *,
    state: Dict[str, Any],
    actual_runtime: Dict[str, Any],
    context_delta_summary: Dict[str, Any],
    recommendation_gap: str,
    facade,
) -> Dict[str, Any]:
    strategist_output = facade._dict(state.get("strategist_output"))
    strategist_llm = facade._dict(state.get("strategist_llm"))
    return {
        "strategist_executed": actual_runtime.get("strategist_executed"),
        "llm_called_by_strategist": actual_runtime.get("llm_called_by_strategist"),
        "used_cached_strategist": actual_runtime.get("used_cached_strategist"),
        "llm_status": facade._clip(strategist_llm.get("status") or strategist_output.get("llm_frame_status"), max_len=40),
        "playbook": facade._clip(strategist_output.get("playbook"), max_len=40),
        "market_regime": facade._clip(strategist_output.get("market_regime"), max_len=40),
        "market_sentiment": facade._clip(strategist_output.get("market_sentiment"), max_len=40),
        "recommendation_gap": recommendation_gap,
        "context_delta_summary": context_delta_summary,
    }



def post_monitor_assessment(
    *,
    actual_runtime: Dict[str, Any],
    monitor_gate_details: Dict[str, Any],
    facade,
) -> Dict[str, Any]:
    return {
        "monitor_decision": facade._clip(actual_runtime.get("monitor_decision"), max_len=24),
        "entry_block_reason": facade._clip(monitor_gate_details.get("entry_block_reason"), max_len=180),
        "failed_gates": list(monitor_gate_details.get("failed_gates") or [])[:8],
        "passed_gates": list(monitor_gate_details.get("passed_gates") or [])[:8],
        "primary_failure_axis": facade._clip(monitor_gate_details.get("primary_failure_axis"), max_len=80),
        "monitor_gate_details": monitor_gate_details,
    }
