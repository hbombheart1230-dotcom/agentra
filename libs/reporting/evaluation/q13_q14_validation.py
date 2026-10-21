from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import fast08_qwindow_projection as _qw


TRACKED_ROOT_CAUSES = (
    "Scanner Ranking Failure",
    "Candidate Filtering",
    "Strategist Override",
    "Exit Horizon",
    "Missing Evidence",
)

ACTIONABLE_ROOT_CAUSES = (
    "Scanner Ranking Failure",
    "Candidate Filtering",
    "Strategist Override",
    "Exit Horizon",
)

REQUIRED_VALIDATION_DAYS = 5
MISSING_EVIDENCE_MAX_RATIO = 0.20
MISSING_EVIDENCE_MAX_DAILY_RATIO = 0.40


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


_mapping = _qw.mapping
_rows = _qw.rows_of


def _date_range(start: str, end: str) -> list[str]:
    cursor = date.fromisoformat(start)
    final = date.fromisoformat(end)
    if cursor > final:
        raise ValueError("start must be before or equal to end")
    rows: list[str] = []
    while cursor <= final:
        rows.append(cursor.isoformat())
        cursor += timedelta(days=1)
    return rows


_cause_trade_count = _qw.cause_trade_count
_exit_horizon_count = _qw.exit_horizon_count


def _q13_score(q13: Mapping[str, Any], key: str) -> int | None:
    return _qw.axis_score(_mapping(q13.get("scores")), key)


def _daily_row(reports_root: Path, day: str) -> dict[str, Any]:
    daily = reports_root / "evaluation" / "daily" / day
    q13_path = daily / "attribution_score_v0.json"
    q14_path = daily / "scanner_alignment_root_cause_report.json"
    horizon_path = daily / "horizon_compliance_report.json"
    return _qw.validation_day_row(
        day,
        q13=_read_json(q13_path),
        q14=_read_json(q14_path),
        horizon=_read_json(horizon_path),
        actionable_causes=ACTIONABLE_ROOT_CAUSES,
    )


def _validation_days_from_range(reports_root: Path, start: str, end: str) -> list[str]:
    days: list[str] = []
    for day in _date_range(start, end):
        daily = reports_root / "evaluation" / "daily" / day
        if daily.exists():
            days.append(day)
    return days


def build_q13_q14_validation_report(
    *,
    reports_root: Path = Path("reports"),
    days: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
) -> dict[str, Any]:
    reports_root = Path(reports_root)
    if days is None:
        if not start or not end:
            raise ValueError("Either days or start/end must be provided")
        days = _validation_days_from_range(reports_root, start, end)
    selected_days = [str(day) for day in days]
    daily_rows = [_daily_row(reports_root, day) for day in selected_days]
    completed_rows = [row for row in daily_rows if row.get("report_complete")]
    totals = _qw.validation_totals(daily_rows, max_daily_missing_ratio=MISSING_EVIDENCE_MAX_DAILY_RATIO)
    total_trade_count = totals["total_trade_count"]
    root_totals = totals["root_totals"]
    largest_counts = totals["largest_counts"]
    daily_missing_ratio_failures = totals["daily_missing_ratio_failures"]
    missing_ratio = totals["missing_ratio"]
    scanner_failure_days = largest_counts.get("Scanner Ranking Failure", 0)
    report_ok = len(completed_rows) == len(daily_rows) and len(daily_rows) >= REQUIRED_VALIDATION_DAYS
    enough_days = len(daily_rows) >= REQUIRED_VALIDATION_DAYS
    missing_ok = (
        missing_ratio <= MISSING_EVIDENCE_MAX_RATIO
        and daily_missing_ratio_failures == 0
    )
    stable_ok = scanner_failure_days >= 4
    if not enough_days:
        decision = "IN_PROGRESS"
        decision_reasons = [f"needs_{REQUIRED_VALIDATION_DAYS}_trading_days"]
    elif report_ok and missing_ok and stable_ok:
        decision = "GO"
        decision_reasons = ["scanner_ranking_failure_stable", "missing_evidence_within_threshold", "reports_complete"]
    else:
        decision = "NO_GO"
        decision_reasons = []
        if not report_ok:
            decision_reasons.append("q13_q14_reports_incomplete")
        if not missing_ok:
            decision_reasons.append("missing_evidence_above_threshold")
        if not stable_ok:
            decision_reasons.append("scanner_ranking_failure_not_stable_4_of_5")

    return {
        "schema_version": "q13_q14_validation.v1",
        "measurement_contract_version": "q13_q14_diagnostic_stability.v2",
        "evaluation_program_id": "Q13_Q14_VALIDATION_RUN",
        "behavior_effect": "observation_only",
        "days": selected_days,
        "required_validation_days": REQUIRED_VALIDATION_DAYS,
        "day_count": len(daily_rows),
        "completed_report_day_count": len(completed_rows),
        "total_trade_count": total_trade_count,
        "root_cause_totals": {cause: int(root_totals.get(cause, 0)) for cause in TRACKED_ROOT_CAUSES},
        "largest_behavior_root_cause_day_counts": dict(largest_counts),
        "missing_evidence_ratio": missing_ratio,
        "missing_evidence_thresholds": {
            "max_total_ratio": MISSING_EVIDENCE_MAX_RATIO,
            "max_daily_ratio": MISSING_EVIDENCE_MAX_DAILY_RATIO,
        },
        "decision": decision,
        "decision_scope": "diagnostic_stability_only",
        "behavior_patch_authorized": False,
        "decision_reasons": decision_reasons,
        "daily_rows": daily_rows,
        "validation_rules": [
            "Q13/Q14 axes and score formulas are frozen.",
            "Only instrumentation and artifact bugs may be fixed during validation.",
            "GO requires Scanner Ranking Failure to be the largest behavior root cause on at least 4 of 5 trading days.",
            "GO requires Missing Evidence to remain within the configured thresholds.",
            "GO requires Q13/Q14 reports to be generated without schema/report errors.",
            "A diagnostic GO does not authorize a behavior patch; Q14 structural evidence is required.",
        ],
    }


def render_q13_q14_validation_report(payload: Mapping[str, Any]) -> str:
    return _qw.render_q13_q14_validation_report(payload, tracked_causes=TRACKED_ROOT_CAUSES)


def write_q13_q14_validation_report(
    *,
    reports_root: Path = Path("reports"),
    validation_id: str,
    days: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
) -> dict[str, str]:
    reports_root = Path(reports_root)
    payload = build_q13_q14_validation_report(
        reports_root=reports_root,
        days=days,
        start=start,
        end=end,
    )
    out_dir = reports_root / "evaluation" / "validation" / validation_id
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "q13_q14_validation_report.json"
    md_path = out_dir / "q13_q14_validation_report.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_q13_q14_validation_report(payload), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


__all__ = [
    "build_q13_q14_validation_report",
    "render_q13_q14_validation_report",
    "write_q13_q14_validation_report",
]
