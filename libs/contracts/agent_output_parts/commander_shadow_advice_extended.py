from __future__ import annotations
from typing import Any, Dict


def llm_call_advice(
    *,
    strategist_action_recommendation: str,
    observations: Dict[str, Any],
    state: Dict[str, Any],
    facade,
) -> str:
    strategist_llm = facade._dict(state.get("strategist_llm"))
    llm_status = str(observations.get("last_llm_status") or strategist_llm.get("status") or "").strip().lower()
    if strategist_action_recommendation == "SKIP" and observations.get("market_changed") is False:
        return "SKIP"
    if strategist_action_recommendation == "SKIP" and observations.get("repeated_same_context") is True:
        return "SKIP"
    if bool(strategist_llm.get("blocked")) or llm_status in {"error", "fallback"}:
        return "RETRY_MINIMAL"
    if llm_status in {"partial", "salvaged", "repaired"}:
        return "RETRY_COMPACT"
    if strategist_action_recommendation == "SKIP":
        return "SKIP"
    return "ALLOW"
