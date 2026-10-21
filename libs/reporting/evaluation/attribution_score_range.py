from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from . import fast08_cumulative_projection as _cp
from . import fast08_qwindow_projection as _qw
from .attribution_score_window import SCORE_KEYS, _read_json, _score_value


def _parse_date(value: str) -> date:
    return date.fromisoformat(str(value))


def _date_range(start: str, end: str) -> list[str]:
    cursor = _parse_date(start)
    final = _parse_date(end)
    if cursor > final:
        raise ValueError("start must be before or equal to end")
    days: list[str] = []
    while cursor <= final:
        days.append(cursor.isoformat())
        cursor += timedelta(days=1)
    return days


def _trade_dir_count(reports_root: Path, day: str) -> int:
    trade_dir = reports_root / "trades" / day
    if not trade_dir.exists():
        return 0
    return sum(1 for path in trade_dir.rglob("TRD_*") if path.is_dir())


def _has_source_artifact(reports_root: Path, day: str) -> bool:
    return any(
        path.exists()
        for path in (
            reports_root / "trades" / day,
            reports_root / "operator_summary" / "daily" / day,
            reports_root / "evaluation" / "daily" / day,
        )
    )


def _day_payload(reports_root: Path, day: str) -> dict[str, Any]:
    return _read_json(reports_root / "evaluation" / "daily" / day / "attribution_score_v0.json")


def _day_trade_count(reports_root: Path, day: str) -> int:
    scorecard_count = (
        _read_json(reports_root / "evaluation" / "daily" / day / "daily_scorecard.json")
        .get("artifact_integrity", {})
        .get("trade_count")
    )
    if scorecard_count is not None:
        try:
            return int(scorecard_count)
        except (TypeError, ValueError):
            pass
    return _trade_dir_count(reports_root, day)


def build_attribution_score_range(
    *,
    reports_root: Path = Path("reports"),
    start: str,
    end: str,
    include_empty_days: bool = False,
) -> dict[str, Any]:
    reports_root = Path(reports_root)
    day_rows: list[dict[str, Any]] = []
    for day in _date_range(start, end):
        if not include_empty_days and not _has_source_artifact(reports_root, day):
            continue
        day_rows.append(
            _cp.range_score_row(
                day,
                payload=_day_payload(reports_root, day),
                trade_count=_day_trade_count(reports_root, day),
                axis_score_of=_score_value,
                score_keys=SCORE_KEYS,
            )
        )

    scored_rows = [row for row in day_rows if row.get("scored")]
    axis_summary = _cp.range_axis_summary(day_rows, SCORE_KEYS, _score_value)
    weakest_counts = _qw.weakest_axis_counts(scored_rows)
    daily_table = _cp.range_day_table(day_rows, SCORE_KEYS, _score_value)
    weakest_average = _qw.weakest_average_axis(axis_summary)
    return {
        "schema_version": "attribution_score_range.v1",
        "evaluation_program_id": "Q13_ATTRIBUTION_SCORE_RANGE",
        "behavior_effect": "observation_only",
        "start": start,
        "end": end,
        "include_empty_days": include_empty_days,
        "day_count": len(day_rows),
        "available_day_count": sum(1 for row in day_rows if row.get("available")),
        "scored_day_count": len(scored_rows),
        "trade_day_count": sum(1 for row in day_rows if int(row.get("trade_count") or 0) > 0),
        "total_trade_count": sum(int(row.get("trade_count") or 0) for row in day_rows),
        "scored_trade_count": sum(int(row.get("trade_count") or 0) for row in scored_rows),
        "axis_summary": axis_summary,
        "weakest_axis_distribution": dict(weakest_counts),
        "weakest_axis_by_average_score": weakest_average,
        "daily_rows": daily_table,
        "interpretation_rule": (
            "Use scored days for attribution conclusions. Missing or insufficient days are "
            "shown for audit but excluded from average score and weakest-axis distribution."
        ),
    }


render_attribution_score_range = _cp.render_attribution_score_range


def write_attribution_score_range(
    *,
    reports_root: Path = Path("reports"),
    start: str,
    end: str,
    include_empty_days: bool = False,
) -> dict[str, str]:
    reports_root = Path(reports_root)
    payload = build_attribution_score_range(
        reports_root=reports_root,
        start=start,
        end=end,
        include_empty_days=include_empty_days,
    )
    out_dir = reports_root / "evaluation" / "range" / f"{start}_{end}"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "attribution_score_range.json"
    md_path = out_dir / "attribution_score_range.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_attribution_score_range(payload), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


__all__ = [
    "build_attribution_score_range",
    "render_attribution_score_range",
    "write_attribution_score_range",
]
