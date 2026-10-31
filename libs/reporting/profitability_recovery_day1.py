from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List

from libs.reporting.llm_artifacts import iter_trade_dirs as _iter_trade_dirs
from libs.reporting import profitability_recovery_scalar_projection as _scalar_owner
from libs.reporting import profitability_recovery_trade_projection as _trade_owner
from libs.reporting import profitability_recovery_evidence_projection as _evidence_owner
from libs.reporting import profitability_recovery_status_projection as _status_owner
from libs.reporting import profitability_recovery_weakness_projection as _weakness_owner
from libs.reporting import profitability_recovery_io_projection as _io_owner
from libs.reporting import profitability_recovery_artifact_projection as _artifact_owner
from libs.reporting import profitability_recovery_trade_dirs_projection as _trade_dirs_owner
from libs.reporting import profitability_recovery_hold_projection as _hold_owner
from libs.reporting import profitability_recovery_linkage_projection as _linkage_owner
from libs.reporting import profitability_recovery_row_iteration_projection as _row_iter_owner
from libs.reporting import profitability_recovery_audit_projection as _audit_owner
from libs.reporting import profitability_recovery_scorecard_projection as _scorecard_owner
from libs.reporting import profitability_recovery_execution_projection as _execution_owner
from libs.reporting import profitability_recovery_diagnostic_row_projection as _diag_row_owner


REQUIRED_EXECUTION_FIELDS = (
    "order_status",
    "order_id",
    "execution_mode",
    "broker_env",
    "filled_qty",
    "avg_price",
)


def _read_json(path: Path) -> Dict[str, Any]:
    return _io_owner._read_json(path, facade=sys.modules[__name__])


def iter_trade_dirs(reports_root: Path, day: str) -> List[Path]:
    return _trade_dirs_owner.iter_trade_dirs(reports_root, day, facade=sys.modules[__name__])


def _artifact_path(trade_dir: Path, *candidates: str) -> Path:
    return _artifact_owner._artifact_path(trade_dir, *candidates)


def _safe_float(value: Any) -> float | None:
    return _scalar_owner._safe_float(value)


def _is_closed_trade(lifecycle_bundle: Dict[str, Any]) -> bool:
    return _trade_owner._is_closed_trade(lifecycle_bundle)


def _linkage_surface_present(linkage: Dict[str, Any]) -> bool:
    return _trade_owner._linkage_surface_present(linkage)


def _execution_missing_fields(execution_details: Dict[str, Any]) -> List[str]:
    return _evidence_owner._execution_missing_fields(execution_details, facade=sys.modules[__name__])


def _bundle_artifacts(lifecycle_bundle: Dict[str, Any]) -> Dict[str, Any]:
    return _evidence_owner._bundle_artifacts(lifecycle_bundle)


def _section_provenance(lifecycle_bundle: Dict[str, Any]) -> Dict[str, Any]:
    return _evidence_owner._section_provenance(lifecycle_bundle)


def _read_hold_payload(trade_dir: Path) -> Dict[str, Any]:
    return _hold_owner._read_hold_payload(trade_dir, facade=sys.modules[__name__])


def _resolve_same_day_linkage(lifecycle_bundle: Dict[str, Any], trade_dir: Path) -> Dict[str, Any]:
    return _linkage_owner._resolve_same_day_linkage(lifecycle_bundle, trade_dir, facade=sys.modules[__name__])


def _resolve_holding_evidence(lifecycle_bundle: Dict[str, Any], trade_dir: Path) -> Dict[str, Any]:
    hold_payload = _read_hold_payload(trade_dir)
    monitor_context_snapshots = [
        dict(row)
        for row in list(lifecycle_bundle.get("monitor_context_snapshots") or [])
        if isinstance(row, dict)
    ]
    if not monitor_context_snapshots:
        monitor_context_snapshots = [
            dict((row.get("monitor_context") or {}))
            for row in list(hold_payload.get("holding_events") or [])
            if isinstance(row, dict) and isinstance(row.get("monitor_context"), dict)
        ]

    if not monitor_context_snapshots:
        exit_ctx = lifecycle_bundle.get("exit", {}) if isinstance(lifecycle_bundle.get("exit"), dict) else {}
        entry_ctx = lifecycle_bundle.get("entry", {}) if isinstance(lifecycle_bundle.get("entry"), dict) else {}
        fallback_monitor = exit_ctx.get("monitor_context") or entry_ctx.get("monitor_context")
        if fallback_monitor and isinstance(fallback_monitor, dict):
            monitor_context_snapshots.append(dict(fallback_monitor))
            if not holding_phase_summary:
                holding_phase_summary = "Hold evidence recovered from execution context."

    hold_events_count = int(lifecycle_bundle.get("hold_events_count") or 0)
    if hold_events_count <= 0:
        hold_events_count = len(list(hold_payload.get("holding_events") or []))
    if hold_events_count <= 0:
        hold_events_count = sum(
            1
            for row in list(lifecycle_bundle.get("timeline") or [])
            if isinstance(row, dict) and str(row.get("event") or "").strip().lower() == "holding"
        )

    holding_phase_summary = str(lifecycle_bundle.get("holding_phase_summary") or "").strip()
    if not holding_phase_summary:
        holding_summary = str(hold_payload.get("summary") or "").strip()
        if holding_summary:
            holding_phase_summary = holding_summary
        elif hold_events_count > 0:
            reasons = []
            for row in list(hold_payload.get("holding_events") or []):
                if not isinstance(row, dict):
                    continue
                reason = str(row.get("monitor_reason") or row.get("exit_reason") or "").strip()
                if reason:
                    reasons.append(reason)
            if reasons:
                deduped = ", ".join(dict.fromkeys(reasons))
                holding_phase_summary = f"Holding observed across {hold_events_count} monitor updates: {deduped}."
            else:
                holding_phase_summary = f"Holding observed across {hold_events_count} monitor updates."

    hold_duration = str(lifecycle_bundle.get("hold_duration") or "").strip()
    if not hold_duration:
        hold_duration = str(
            ((lifecycle_bundle.get("trade_outcome") or {}) if isinstance(lifecycle_bundle.get("trade_outcome"), dict) else {}).get("holding_time")
            or ""
        ).strip()

    hold_duration_sec = lifecycle_bundle.get("hold_duration_sec")
    if hold_duration_sec in (None, ""):
        hold_duration_sec = hold_payload.get("hold_duration_sec")

    return {
        "hold_duration": hold_duration,
        "hold_duration_sec": hold_duration_sec,
        "hold_events_count": hold_events_count,
        "monitor_context_snapshots": monitor_context_snapshots,
        "holding_phase_summary": holding_phase_summary,
    }


def _resolve_execution_details(lifecycle_bundle: Dict[str, Any], trade_dir: Path) -> Dict[str, Any]:
    return _execution_owner._resolve_execution_details(lifecycle_bundle, trade_dir, facade=sys.modules[__name__])


def _resolve_ai_trade_report_status(
    lifecycle_bundle: Dict[str, Any],
    ai_component: Dict[str, Any],
    ai_trade_report_llm_exists: bool,
) -> str:
    return _status_owner._resolve_ai_trade_report_status(lifecycle_bundle, ai_component, ai_trade_report_llm_exists)


def _is_closed_trade_report_generation_regression(
    *, closed_trade: bool, ai_trade_report_llm_exists: bool, ai_status: str
) -> bool:
    return _status_owner._is_closed_trade_report_generation_regression(closed_trade=closed_trade, ai_trade_report_llm_exists=ai_trade_report_llm_exists, ai_status=ai_status)


def read_trade_diagnostic_row(trade_dir: Path) -> Dict[str, Any]:
    return _diag_row_owner.read_trade_diagnostic_row(trade_dir, facade=sys.modules[__name__])


def iter_trade_diagnostic_rows(reports_root: Path, day: str) -> List[Dict[str, Any]]:
    return _row_iter_owner.iter_trade_diagnostic_rows(reports_root, day, facade=sys.modules[__name__])


def _top_recurring_weakness(rows: Iterable[Dict[str, Any]]) -> str:
    return _weakness_owner._top_recurring_weakness(rows, facade=sys.modules[__name__])


def audit_profitability_recovery_day(reports_root: Path, day: str) -> Dict[str, Any]:
    return _audit_owner.audit_profitability_recovery_day(reports_root, day, facade=sys.modules[__name__])


def build_daily_profitability_scorecard(reports_root: Path, day: str) -> Dict[str, Any]:
    return _scorecard_owner.build_daily_profitability_scorecard(reports_root, day, facade=sys.modules[__name__])
