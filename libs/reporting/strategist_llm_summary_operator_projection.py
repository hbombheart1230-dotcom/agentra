"""Strategist LLM summary compact operator projection (moved verbatim from strategist_llm_summary).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict


def compact_operator_summary(value: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    return {
        "available": bool(value.get("available")),
        "status": facade._text(value.get("status"), ""),
        "artifact_path": facade._text(value.get("artifact_path"), ""),
        "trade_count": value.get("trade_count"),
        "closed_trade_count": value.get("closed_trade_count"),
        "win_rate": value.get("win_rate"),
        "avg_return_pct": value.get("avg_return_pct"),
    }
