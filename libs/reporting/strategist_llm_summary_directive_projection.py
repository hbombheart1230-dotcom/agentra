"""Strategist LLM summary directive projection (moved verbatim from strategist_llm_summary).

``_as_dict`` is resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict


def directive(payload: Dict[str, Any], key: str, *, facade: Any) -> Dict[str, Any]:
    directives = facade._as_dict(payload.get("strategy_adjustment_directives"))
    return facade._as_dict(directives.get(key))
