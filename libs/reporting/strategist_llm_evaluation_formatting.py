"""Strategist LLM evaluation performance formatting (moved verbatim from strategist_llm_evaluation).

Helpers are resolved on ``facade`` (the strategist_llm_evaluation module) at call time; this module never imports it.
Pure functions; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence


def _format_perf(rows: Sequence[Mapping[str, Any]], *, limit: int = 3, facade: Any) -> str:
    parts: List[str] = []
    for row in list(rows)[:limit]:
        name = facade._text(row.get("name"))
        if not name:
            continue
        parts.append(
            f"{name} ({row.get('count')}, win {float(row.get('win_rate') or 0.0) * 100:.1f}%, avg {float(row.get('avg_return_pct') or 0.0):.2f}%)"
        )
    return ", ".join(parts) if parts else "none"
