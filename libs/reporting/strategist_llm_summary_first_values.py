"""Strategist LLM summary first-value selectors (moved verbatim from strategist_llm_summary).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict


def first_text(default: str, *values: Any, facade: Any) -> str:
    for value in values:
        text = facade._text(value, "")
        if text:
            return text
    return default


def first_dict(*values: Any, facade: Any) -> Dict[str, Any]:
    for value in values:
        row = facade._as_dict(value)
        if row:
            return row
    return {}
