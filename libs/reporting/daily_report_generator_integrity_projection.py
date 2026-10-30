"""Daily report generator trade report integrity projection (moved verbatim from daily_report_generator).

Helpers are resolved on ``facade`` (the daily_report_generator module) at call time; this module never imports it.
Read-only filesystem existence checks only.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def _build_trade_report_integrity(
    reports_root: Path,
    day: str,
    trade_index: List[Dict[str, Any]],
    broker_alignment: Dict[str, Any] | None = None,
    *,
    facade: Any,
) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []
    broker_closed_symbols = facade._broker_closed_symbols_from_alignment(broker_alignment)
    broker_closed_report_open: List[Dict[str, Any]] = []
    for item in trade_index:
        if not isinstance(item, dict):
            continue
        trade_id = str(item.get("trade_id") or "").strip()
        if not trade_id:
            continue
        symbol = facade.normalize_symbol(item.get("symbol"), allow_test_symbols=True)
        lifecycle_status = str(
            item.get("status")
            or item.get("trade_lifecycle_status")
            or item.get("lifecycle_status")
            or ""
        ).strip().lower()
        trade_dir = facade._find_trade_dir(reports_root, day, trade_id)
        reports_dir = trade_dir / "reports" if trade_dir else None
        checks = {
            "ai_trade_summary_input_json": bool(reports_dir and (reports_dir / "ai_trade_summary_input.json").exists()),
            "ai_trade_summary_json": bool(reports_dir and (reports_dir / "ai_trade_summary.json").exists()),
            "ai_trade_summary_md": bool(reports_dir and (reports_dir / "ai_trade_summary.md").exists()),
        }
        row = {
            "trade_id": trade_id,
            "symbol": symbol or str(item.get("symbol") or ""),
            "lifecycle_status": lifecycle_status,
            "trade_dir": str(trade_dir) if trade_dir else "",
            **checks,
        }
        rows.append(row)
        if symbol and symbol in broker_closed_symbols and lifecycle_status not in ("closed", "done", "completed"):
            broker_closed_report_open.append(
                {
                    "trade_id": trade_id,
                    "symbol": symbol,
                    "lifecycle_status": lifecycle_status or "unknown",
                    "issue": "broker_day_trade_closed_but_report_open",
                }
            )
        if not all(checks.values()):
            missing.append(
                {
                    "trade_id": trade_id,
                    "symbol": row["symbol"],
                    "missing": [key for key, value in checks.items() if not value],
                }
            )
    status = "ok"
    if missing:
        status = "missing_reports"
    if broker_closed_report_open:
        status = "broker_lifecycle_mismatch" if not missing else "missing_reports_and_broker_lifecycle_mismatch"
    return {
        "schema_version": "trade_report_integrity.v1",
        "expected_trade_count": len([x for x in trade_index if isinstance(x, dict) and str(x.get("trade_id") or "").strip()]),
        "checked_trade_count": len(rows),
        "summary_md_count": sum(1 for row in rows if row.get("ai_trade_summary_md")),
        "summary_json_count": sum(1 for row in rows if row.get("ai_trade_summary_json")),
        "summary_input_count": sum(1 for row in rows if row.get("ai_trade_summary_input_json")),
        "missing_count": len(missing),
        "broker_closed_report_open_count": len(broker_closed_report_open),
        "status": status,
        "missing": missing,
        "broker_closed_report_open": broker_closed_report_open,
    }
