"""Strategist LLM summary playbook flow label (moved verbatim from strategist_llm_summary).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict


def playbook_flow_label(detail: Dict[str, Any], *, facade: Any) -> str:
    pre = facade._text(detail.get("pre_llm_playbook"), "")
    requested = facade._text(detail.get("requested_playbook"), "")
    final = facade._text(detail.get("final_playbook"), "")
    parts = [part for part in (pre, requested, final) if part]
    if not parts:
        return "-"
    flow = " -> ".join(parts)
    source = facade._text(detail.get("requested_playbook_source"), "")
    return f"{flow} (source={source})" if source else flow
