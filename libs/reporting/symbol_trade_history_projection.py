"""symbol_trade_report _build_history_index (moved verbatim from symbol_trade_report).

Module globals and helpers are resolved on ``facade`` (the symbol_trade_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def _build_history_index(reports_root: Path, symbol: str, *, facade: Any) -> List[Dict[str, Any]]:
    history: List[Dict[str, Any]] = []
    normalized_symbol = str(symbol or "").strip().upper()
    for path, obj in facade._iter_trade_lifecycles(reports_root):
        if str(obj.get("symbol") or "").strip().upper() != normalized_symbol:
            continue
        summary = obj.get("summary") if isinstance(obj.get("summary"), dict) else {}
        entry = obj.get("entry") if isinstance(obj.get("entry"), dict) else {}
        exit_row = obj.get("exit") if isinstance(obj.get("exit"), dict) else {}
        artifacts = obj.get("artifacts") if isinstance(obj.get("artifacts"), dict) else {}
        trade_id = str(obj.get("trade_id") or "")
        trade_day = str(obj.get("day") or "")
        trade_root = (
            path.parent
            if path.name == "lifecycle_bundle.json"
            else path.parent.parent
        )
        expected_report_path = trade_root / "reports" / "ai_trade_report.json"
        expected_operator_brief_path = trade_root / "reports" / "operator_brief.json"
        lifecycle_bundle_path = trade_root / "lifecycle_bundle.json"
        artifact_snapshot = facade._extract_trade_artifact_snapshot(
            report_path=facade.Path(str(artifacts.get("ai_trade_report_json") or expected_report_path)),
            operator_brief_path=facade.Path(str(artifacts.get("operator_brief_json") or expected_operator_brief_path)),
            lifecycle_bundle_path=facade.Path(str(artifacts.get("lifecycle_bundle_json") or lifecycle_bundle_path)),
        )
        trade_status = str(obj.get("status") or "").strip()
        if exit_row:
            last_action = "SELL"
        elif trade_status.lower() == "open":
            last_action = "HOLD"
        elif entry:
            last_action = "BUY"
        else:
            last_action = ""
        run_id = (
            str(entry.get("run_id") or "").strip()
            or str(exit_row.get("run_id") or "").strip()
            or str(obj.get("entry_strategist_run_id") or "").strip()
        )
        result_pct = facade._result_pct_from_lifecycle(obj)
        if result_pct is None:
            result_pct = facade._safe_float(artifact_snapshot.get("artifact_result_pct"))
        raw_entry_reason = str(summary.get("entry_reason_human") or "")
        artifact_entry_reason = str(artifact_snapshot.get("actual_entry_reason") or "")
        entry_reason_raw = (
            artifact_entry_reason
            if facade._should_prefer_artifact_entry_reason(raw_entry_reason, artifact_entry_reason)
            else raw_entry_reason
        )
        entry_reason = facade._clean_symbol_reason(entry_reason_raw, axis="entry")
        exit_reason = facade._clean_symbol_reason(summary.get("exit_reason_human"), axis="exit")
        entry_pattern_type = facade._clean_symbol_pattern(
            artifact_snapshot.get("entry_pattern_type"),
            axis="entry",
            fallback_reason=entry_reason,
        )
        exit_pattern_type = facade._clean_symbol_pattern(
            artifact_snapshot.get("exit_pattern_type"),
            axis="exit",
            fallback_reason=exit_reason,
        )
        history.append(
            {
                "trade_id": trade_id,
                "date": trade_day,
                "run_id": run_id,
                "status": trade_status,
                "last_status": trade_status,
                "last_action": last_action,
                "entry_reason": entry_reason,
                "exit_reason": exit_reason,
                "lifecycle_summary": facade._clean_lifecycle_summary(
                    trade_id=trade_id,
                    status=trade_status,
                    entry_reason=entry_reason,
                    exit_reason=exit_reason,
                ),
                "operator_conclusion": str(summary.get("operator_conclusion_human") or ""),
                "playbook": str((((entry.get("strategist_context") or {}) if isinstance(entry.get("strategist_context"), dict) else {}).get("playbook")) or ""),
                "hold_seconds": facade._hold_seconds_from_lifecycle(obj),
                "result_pct": result_pct,
                "trade_origin": str(obj.get("trade_origin") or ""),
                "lifecycle_completeness": str(obj.get("lifecycle_completeness") or ""),
                "evidence_recovery_used": bool(obj.get("evidence_recovery_used")),
                "report_path": str(artifacts.get("ai_trade_report_json") or expected_report_path),
                "operator_brief_path": str(artifacts.get("operator_brief_json") or expected_operator_brief_path),
                "lifecycle_bundle_path": str(artifacts.get("lifecycle_bundle_json") or lifecycle_bundle_path),
                "trade_root_path": str(trade_root),
                "report_headline": str(artifact_snapshot.get("report_headline") or ""),
                "report_executive_summary": str(artifact_snapshot.get("report_executive_summary") or ""),
                "report_market_summary": str(artifact_snapshot.get("report_market_summary") or ""),
                "report_entry_summary": str(artifact_snapshot.get("report_entry_summary") or entry_reason or ""),
                "report_final_conclusion": str(artifact_snapshot.get("report_final_conclusion") or ""),
                "brief_headline": str(artifact_snapshot.get("brief_headline") or ""),
                "brief_executive_summary": str(artifact_snapshot.get("brief_executive_summary") or ""),
                "brief_risk_summary": str(artifact_snapshot.get("brief_risk_summary") or ""),
                "brief_next_checkpoints": list(artifact_snapshot.get("brief_next_checkpoints") or []),
                "entry_pattern_type": entry_pattern_type,
                "exit_pattern_type": exit_pattern_type,
                "thesis_invalidation_code": facade._clean_symbol_code(artifact_snapshot.get("thesis_invalidation_code")),
                "improvement_tags": list(artifact_snapshot.get("improvement_tags") or []),
                "review_flags": list(artifact_snapshot.get("review_flags") or []),
            }
        )
    history.sort(key=lambda row: (str(row.get("date") or ""), str(row.get("trade_id") or "")))
    return history
