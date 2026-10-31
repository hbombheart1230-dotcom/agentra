"""profitability_recovery_day1 projections (moved verbatim from profitability_recovery_day1).

Module globals and helpers are resolved on ``facade`` (the profitability_recovery_day1 module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def audit_profitability_recovery_day(reports_root: Path, day: str, *, facade: Any) -> Dict[str, Any]:
    rows = facade.iter_trade_diagnostic_rows(reports_root, day)
    return {
        "schema_version": "profitability_recovery_day1_audit.v1",
        "day": str(day),
        "trade_count": len(rows),
        "closed_trade_count": sum(1 for row in rows if bool(row.get("closed_trade"))),
        "closed_trade_report_generation_regression_count": sum(
            1 for row in rows if bool(row.get("closed_trade_report_generation_regression"))
        ),
        "closed_trade_decision_only_misclassification_count": sum(
            1 for row in rows if bool(row.get("closed_trade_decision_only_misclassification"))
        ),
        "holding_evidence_thin_count": sum(1 for row in rows if bool(row.get("holding_evidence_thin"))),
        "same_day_linkage_missing_count": sum(1 for row in rows if bool(row.get("same_day_linkage_missing"))),
        "execution_fields_missing_count": sum(
            int(row.get("execution_missing_fields_count") or 0) for row in rows
        ),
        "top_recurring_diagnostic_weakness": facade._top_recurring_weakness(rows),
        "rows": rows,
    }
