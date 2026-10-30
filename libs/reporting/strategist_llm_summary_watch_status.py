"""Strategist LLM summary clean watch-scope label and strategy-patch status (moved verbatim from strategist_llm_summary).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def watch_scope_label_clean(value: Dict[str, Any], *, facade: Any) -> str:
    if not value:
        return ""
    rank = value.get("max_priority_rank")
    runner_ups = value.get("max_runner_ups")
    parts: List[str] = []
    if rank not in (None, ""):
        parts.append(f"{rank}위까지")
    if runner_ups not in (None, ""):
        parts.append(f"차순위 {runner_ups}개")
    if value.get("cascade_enabled") not in (None, ""):
        parts.append(f"cascade {'활성' if bool(value.get('cascade_enabled')) else '비활성'}")
    return " / ".join(parts)


def strategy_patch_status_clean(detail: Dict[str, Any], *, facade: Any) -> str:
    required_keys = (
        "pre_llm_playbook",
        "llm_requested_playbook",
        "requested_playbook",
        "requested_playbook_source",
        "final_playbook",
        "tactical_strategy",
        "strategy_scores",
        "rejected_strategy_reasons",
        "candidate_watch_policy",
    )
    missing = [key for key in required_keys if not detail.get(key)]
    if not missing:
        return "적용됨"
    return f"일부 누락 ({', '.join(missing)})"
