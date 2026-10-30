"""Strategist LLM summary markdown bullet helpers (moved verbatim from strategist_llm_summary).

Pure functions; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List


def bullet_lines(items: List[Any], *, empty: str = "-") -> List[str]:
    rows = [f"- {item}" for item in items if str(item or "").strip()]
    return rows if rows else [f"- {empty}"]


def monitor_adjustment_lines(value: Dict[str, Any]) -> List[str]:
    if not value:
        return ["- -"]
    return [f"- {key}: {value.get(key)}" for key in sorted(value)]
