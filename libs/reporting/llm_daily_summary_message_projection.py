"""LLM daily summary prompt message construction (moved verbatim from llm_daily_summary).

Pure function; no LLM call.
"""
from __future__ import annotations

from typing import Any, Dict, List


def _build_messages(state: Dict[str, Any], policy: Dict[str, Any]) -> List[Dict[str, Any]]:
    day = str(state.get("eod_day") or policy.get("day") or "")
    report = dict(state.get("daily_report") or {})
    approvals = report.get("approvals")
    denials = report.get("denials")
    runs = report.get("runs")

    # Keep prompt compact; we only need a short manager-friendly summary.
    sys = {
        "role": "system",
        "content": (
            "You are a trading system reporter. "
            "Summarize the day's automated decisions succinctly in Korean. "
            "No financial advice. Use bullet points." 
        ),
    }
    user = {
        "role": "user",
        "content": (
            f"Day: {day}\n"
            f"approvals: {approvals}\n"
            f"denials: {denials}\n"
            f"runs: {runs}\n\n"
            "Write a short summary (max 6 bullets) and a one-line takeaway."
        ),
    }
    return [sys, user]
