"""Strategist LLM summary clean strategy-score and rejected-strategy lines (moved verbatim).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def strategy_score_lines_clean(scores: Dict[str, Any], *, selected: str, facade: Any) -> List[str]:
    if not scores:
        return ["- -"]
    rows = sorted(scores.items(), key=lambda row: (facade._score_value(row[1]), str(row[0])), reverse=True)
    lines: List[str] = []
    for name, score in rows:
        marker = " (선택)" if str(name) == selected else ""
        lines.append(f"- {name}: {facade._score_label(score)}{marker}")
    return lines


def rejected_strategy_lines(reasons: Dict[str, Any], *, selected: str, facade: Any) -> List[str]:
    if not reasons:
        return ["- -"]
    lines: List[str] = []
    for name in sorted(reasons):
        if str(name) == selected:
            continue
        reason = reasons.get(name)
        if isinstance(reason, (dict, list)):
            reason_text = facade._json_inline(reason)
        else:
            reason_text = facade._text(reason)
        lines.append(f"- {name}: {reason_text}")
    return lines if lines else ["- -"]
