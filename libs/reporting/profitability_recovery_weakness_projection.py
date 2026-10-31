"""profitability_recovery_day1 projections (moved verbatim from profitability_recovery_day1).

Module globals and helpers are resolved on ``facade`` (the profitability_recovery_day1 module) at call time; this module never imports it.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable


def _top_recurring_weakness(rows: Iterable[Dict[str, Any]], *, facade: Any) -> str:
    counter: Counter[str] = facade.Counter()
    for row in rows:
        if bool(row.get("closed_trade_report_generation_regression")):
            counter["closed_trade_report_generation_regression"] += 1
        if bool(row.get("closed_trade_decision_only_misclassification")):
            counter["closed_trade_decision_only_misclassification"] += 1
        if bool(row.get("holding_evidence_thin")):
            counter["holding_evidence_thin"] += 1
        if bool(row.get("same_day_linkage_missing")):
            counter["same_day_linkage_missing"] += 1
        if int(row.get("execution_missing_fields_count") or 0) > 0:
            counter["execution_fields_missing"] += 1
    if not counter:
        return "none"
    return str(counter.most_common(1)[0][0])
