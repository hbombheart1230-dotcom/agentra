"""``_extract_blocker_totals`` moved verbatim from reporter_feedback.py as ``extract_blocker_totals``.

Helpers are resolved on ``facade`` (the reporter_feedback module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def extract_blocker_totals(payload: Mapping[str, Any] | None, *, facade: Any) -> Dict[str, int]:
    row = dict(payload or {})
    direct = row.get("dominant_blocker_total") if isinstance(row.get("dominant_blocker_total"), dict) else {}
    if direct:
        return {str(k): facade._safe_int(v, 0) for k, v in direct.items()}
    no_trade = row.get("no_trade_summary") if isinstance(row.get("no_trade_summary"), dict) else {}
    topn = list(no_trade.get("dominant_blocker_topN") or [])
    totals: Dict[str, int] = {}
    for item in topn:
        if not isinstance(item, dict):
            continue
        reason = str(item.get("reason") or "").strip()
        if not reason:
            continue
        totals[reason] = facade._safe_int(item.get("count"), 0)
    return totals
