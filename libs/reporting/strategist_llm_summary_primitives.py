"""Strategist LLM summary primitive coercions (moved verbatim from strategist_llm_summary).

Pure functions; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List


def as_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def as_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


def text(value: Any, default: str = "-") -> str:
    raw = str(value or "").strip()
    return raw if raw else default
