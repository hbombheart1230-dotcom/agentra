"""profitability_recovery_day1 projections (moved verbatim from profitability_recovery_day1).

Module globals and helpers are resolved on ``facade`` (the profitability_recovery_day1 module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def build_daily_profitability_scorecard(reports_root: Path, day: str, *, facade: Any) -> Dict[str, Any]:
    audit = facade.audit_profitability_recovery_day(reports_root, day)
    rows = list(audit.get("rows") or [])
    return {
        "schema_version": "daily_profitability_scorecard.v1",
        "day": str(day),
        "total_trades": int(audit.get("trade_count") or 0),
        "closed_trades": int(audit.get("closed_trade_count") or 0),
        "loss_trades": sum(1 for row in rows if bool(row.get("loss_trade"))),
        "lifecycle_linkage_missing_count": int(audit.get("same_day_linkage_missing_count") or 0),
        "holding_evidence_thin_count": int(audit.get("holding_evidence_thin_count") or 0),
        "execution_fields_missing_count": int(audit.get("execution_fields_missing_count") or 0),
        "closed_trade_report_generation_regression_count": int(
            audit.get("closed_trade_report_generation_regression_count") or 0
        ),
        "closed_trade_decision_only_misclassification_count": int(
            audit.get("closed_trade_decision_only_misclassification_count") or 0
        ),
        "top_recurring_diagnostic_weakness": str(
            audit.get("top_recurring_diagnostic_weakness") or "none"
        ),
        "rows": rows,
    }
