"""Strategist LLM summary directive Markdown line (moved verbatim from strategist_llm_summary).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict


def directive_line(label: str, value: Dict[str, Any], *, facade: Any) -> str:
    if not value:
        return f"- {label}: -"
    action = facade._text(value.get("action"))
    target = value.get("target")
    if target is None:
        target = value.get("target_fields") or value.get("target_axes")
    reason = facade._text(value.get("reason"), "")
    target_text = ", ".join(str(x) for x in target) if isinstance(target, list) else facade._text(target, "")
    if target_text and reason:
        return f"- {label}: **{action}** -> {target_text}; {reason}"
    if target_text:
        return f"- {label}: **{action}** -> {target_text}"
    if reason:
        return f"- {label}: **{action}**; {reason}"
    return f"- {label}: **{action}**"
