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
