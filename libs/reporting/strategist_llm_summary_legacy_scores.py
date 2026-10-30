"""Strategist LLM summary legacy (non-clean) score label and score lines (moved verbatim from strategist_llm_summary).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def score_label(value: Any, *, facade: Any) -> str:
    numeric = facade._score_value(value)
    if numeric != float("-inf"):
        return f"{numeric:.2f}".rstrip("0").rstrip(".")
    return facade._text(value)


def strategy_score_lines(scores: Dict[str, Any], *, selected: str, facade: Any) -> List[str]:
    if not scores:
        return ["- -"]
    rows = sorted(scores.items(), key=lambda row: (facade._score_value(row[1]), str(row[0])), reverse=True)
    lines: List[str] = []
    for name, score in rows:
        marker = " (선택)" if str(name) == selected else ""
        lines.append(f"- {name}: {facade._score_label(score)}{marker}")
    return lines


def score_value(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("-inf")
