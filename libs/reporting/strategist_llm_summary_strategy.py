"""Strategist LLM summary strategy-detail precedence (moved verbatim).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict


def strategy_detail_from_sources(payload: Dict[str, Any], canonical: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    canonical_detail = facade._as_dict(canonical.get("strategy_detail"))
    strategy_policy = facade._as_dict(canonical.get("strategy_policy"))
    market_policy = facade._as_dict(strategy_policy.get("market_policy"))
    scanner_policy = facade._as_dict(strategy_policy.get("scanner_policy"))
    return {
        "pre_llm_playbook": facade._first_text(
            "",
            canonical_detail.get("pre_llm_playbook"),
            canonical.get("pre_llm_playbook"),
            market_policy.get("pre_llm_playbook"),
            payload.get("pre_llm_playbook"),
        ),
        "llm_requested_playbook": facade._first_text(
            "",
            canonical_detail.get("llm_requested_playbook"),
            canonical.get("llm_requested_playbook"),
            market_policy.get("llm_requested_playbook"),
            payload.get("llm_requested_playbook"),
        ),
        "requested_playbook": facade._first_text(
            "",
            canonical_detail.get("requested_playbook"),
            canonical.get("requested_playbook"),
            market_policy.get("requested_playbook"),
            payload.get("requested_playbook"),
        ),
        "requested_playbook_source": facade._first_text(
            "",
            canonical_detail.get("requested_playbook_source"),
            canonical.get("requested_playbook_source"),
            market_policy.get("requested_playbook_source"),
            payload.get("requested_playbook_source"),
        ),
        "final_playbook": facade._first_text(
            "",
            canonical_detail.get("final_playbook"),
            canonical.get("final_playbook"),
            market_policy.get("final_playbook"),
            canonical.get("playbook"),
            payload.get("final_playbook"),
            payload.get("playbook"),
        ),
        "tactical_strategy": facade._first_text(
            "",
            canonical_detail.get("tactical_strategy"),
            canonical.get("tactical_strategy"),
            market_policy.get("tactical_strategy"),
            payload.get("tactical_strategy"),
        ),
        "tactical_subtype": facade._first_text(
            "",
            canonical_detail.get("tactical_subtype"),
            canonical.get("tactical_subtype"),
            market_policy.get("tactical_subtype"),
            payload.get("tactical_subtype"),
        ),
        "strategy_scores": facade._first_dict(
            canonical_detail.get("strategy_scores"),
            canonical.get("strategy_scores"),
            market_policy.get("strategy_scores"),
            payload.get("strategy_scores"),
        ),
        "rejected_strategy_reasons": facade._first_dict(
            canonical_detail.get("rejected_strategy_reasons"),
            canonical.get("rejected_strategy_reasons"),
            market_policy.get("rejected_strategy_reasons"),
            payload.get("rejected_strategy_reasons"),
        ),
        "candidate_watch_policy": facade._first_dict(
            canonical_detail.get("candidate_watch_policy"),
            canonical.get("candidate_watch_policy"),
            scanner_policy.get("candidate_watch_policy"),
            payload.get("candidate_watch_policy"),
        ),
    }
