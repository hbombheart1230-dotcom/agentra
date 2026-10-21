from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from . import fast08_qwindow_projection as _qw


SCORE_KEYS = (
    "selection_integrity_score",
    "scanner_alignment_score",
    "entry_timing_score",
    "exit_horizon_score",
    "evidence_quality_score",
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


_mapping = _qw.mapping


def _score_value(row: Mapping[str, Any], key: str) -> int | None:
    return _qw.axis_score(row.get("scores"), key)


def _ledger_days(freeze_root: Path) -> list[dict[str, Any]]:
    ledger = _read_json(freeze_root / "daily_ledger.json")
    return [dict(row) for row in ledger.get("days") or [] if isinstance(row, dict)]


def _day_payload(reports_root: Path, day: str) -> dict[str, Any]:
    return _read_json(reports_root / "evaluation" / "daily" / day / "attribution_score_v0.json")


def build_attribution_score_window(
    *,
    reports_root: Path = Path("reports"),
    window_id: str = "q9_q10_q11_q12_5d_20260629",
) -> dict[str, Any]:
    reports_root = Path(reports_root)
    freeze_root = reports_root / "evaluation" / "freeze_window" / window_id
    ledger_rows = _ledger_days(freeze_root)
    day_rows: list[dict[str, Any]] = []
    for ledger in ledger_rows:
        day = str(ledger.get("day") or "")
        payload = _day_payload(reports_root, day)
        day_rows.append(
            _qw.score_day_row(
                day,
                valid=bool(ledger.get("counts_as_valid_day")),
                payload=payload,
                trade_count=(
                    _read_json(reports_root / "evaluation" / "daily" / day / "daily_scorecard.json")
                    .get("artifact_integrity", {})
                    .get("trade_count", 0)
                    if payload
                    else 0
                ),
            )
        )

    valid_rows = [row for row in day_rows if row.get("counts_as_valid_day")]
    axis_summary = _qw.axis_summary(valid_rows, SCORE_KEYS)
    weakest_counts = _qw.weakest_axis_counts(valid_rows)
    daily_table = _qw.score_day_table(day_rows, SCORE_KEYS)
    weakest_average = _qw.weakest_average_axis(axis_summary)
    return {
        "schema_version": "attribution_score_window.v1",
        "evaluation_program_id": "Q13_ATTRIBUTION_SCORE_WINDOW",
        "behavior_effect": "observation_only",
        "window_id": window_id,
        "day_count": len(day_rows),
        "valid_day_count": len(valid_rows),
        "available_day_count": sum(1 for row in day_rows if row.get("available")),
        "total_trade_count_valid_days": sum(int(row.get("trade_count") or 0) for row in valid_rows),
        "axis_summary": axis_summary,
        "weakest_axis_distribution": dict(weakest_counts),
        "weakest_axis_by_average_score": weakest_average,
        "daily_rows": daily_table,
        "interpretation_rule": (
            "Use valid days for aggregate conclusions. Invalid days are shown for audit "
            "but excluded from average score and weakest-axis distribution."
        ),
    }


render_attribution_score_window = _qw.render_attribution_score_window


def write_attribution_score_window(
    *,
    reports_root: Path = Path("reports"),
    window_id: str = "q9_q10_q11_q12_5d_20260629",
) -> dict[str, str]:
    reports_root = Path(reports_root)
    payload = build_attribution_score_window(reports_root=reports_root, window_id=window_id)
    out_dir = reports_root / "evaluation" / "freeze_window" / window_id
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "attribution_score_window.json"
    md_path = out_dir / "attribution_score_window.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_attribution_score_window(payload), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


__all__ = [
    "build_attribution_score_window",
    "render_attribution_score_window",
    "write_attribution_score_window",
]
