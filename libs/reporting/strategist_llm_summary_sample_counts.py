"""Strategist LLM summary headline-count projection (moved verbatim from strategist_llm_summary).

Pure function; no IO.
"""
from __future__ import annotations

from typing import Any


def headline_count_from_sample_map(value: Any) -> int:
    total = 0
    if not isinstance(value, dict):
        return total
    for row in value.values():
        if not isinstance(row, dict):
            continue
        try:
            total += int(row.get("count") or 0)
        except Exception:
            pass
    return total
