"""Symbol trade report text projections (moved verbatim from symbol_trade_report).

Pure functions; no IO.
"""
from __future__ import annotations

from typing import Any, List


def _contains_any(text: str, needles: List[str]) -> bool:
    lowered = str(text or "").strip().lower()
    return any(needle in lowered for needle in needles)


def _clean_symbol_code(value: Any) -> str:
    text = str(value or "").strip()
    if text.lower() in {"", "unknown", "none", "null", "-"}:
        return ""
    return text
