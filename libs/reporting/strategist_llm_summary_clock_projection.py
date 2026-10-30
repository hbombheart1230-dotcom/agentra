"""Strategist LLM summary clock projection (moved verbatim from strategist_llm_summary).

``datetime`` and ``timezone`` are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _utc_now_iso(*, facade: Any) -> str:
    return facade.datetime.now(facade.timezone.utc).isoformat()
