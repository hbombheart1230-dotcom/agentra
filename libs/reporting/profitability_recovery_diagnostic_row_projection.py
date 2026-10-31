"""profitability_recovery_day1 projections (moved verbatim from profitability_recovery_day1).

Module globals and helpers are resolved on ``facade`` (the profitability_recovery_day1 module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def read_trade_diagnostic_row(trade_dir: Path, *, facade: Any) -> Dict[str, Any]:
    lifecycle_path = facade._artifact_path(
        trade_dir,
        "lifecycle_bundle.json",
        "lifecycle/trade_lifecycle.json",
        "trade_lifecycle.json",
    )
    generation_state_path = trade_dir / "reports" / "report_generation_state.json"
    ai_trade_report_llm_path = facade._artifact_path(
        trade_dir,
        "reports/ai_trade_report_llm_response.json",
        "ai_trade_report/ai_trade_report_llm_response.json",
    )
    lifecycle_bundle = facade._read_json(lifecycle_path)
    generation_state = facade._read_json(generation_state_path)
    components = generation_state.get("components") if isinstance(generation_state.get("components"), dict) else {}
    ai_component = components.get("ai_trade_report") if isinstance(components.get("ai_trade_report"), dict) else {}
    ai_trade_report_llm_exists = ai_trade_report_llm_path.exists()
    same_day_linkage = facade._resolve_same_day_linkage(lifecycle_bundle, trade_dir)
    holding_evidence = facade._resolve_holding_evidence(lifecycle_bundle, trade_dir)
    holding_phase_summary = str(holding_evidence.get("holding_phase_summary") or "").strip()
    hold_events_count = int(holding_evidence.get("hold_events_count") or 0)
    monitor_context_snapshots = [
        dict(row)
        for row in list(holding_evidence.get("monitor_context_snapshots") or [])
        if isinstance(row, dict)
    ]
    execution_details = facade._resolve_execution_details(lifecycle_bundle, trade_dir)
    closed_trade = facade._is_closed_trade(lifecycle_bundle)
    story_type = str(
        lifecycle_bundle.get("story_type")
        or ((lifecycle_bundle.get("story_contract") or {}) if isinstance(lifecycle_bundle.get("story_contract"), dict) else {}).get("story_type")
        or ""
    ).strip().lower()
    ai_status = facade._resolve_ai_trade_report_status(lifecycle_bundle, ai_component, ai_trade_report_llm_exists)
    return_pct = facade._safe_float(((lifecycle_bundle.get("trade_outcome") or {}) if isinstance(lifecycle_bundle.get("trade_outcome"), dict) else {}).get("return_pct"))
    same_day_linkage_missing = not facade._linkage_surface_present(same_day_linkage)
    holding_evidence_thin = bool(
        lifecycle_bundle.get("hold_evidence_thin")
        or hold_events_count <= 0
        or (not monitor_context_snapshots and not holding_phase_summary)
    )
    execution_missing_fields = facade._execution_missing_fields(execution_details)
    row = {
        "trade_id": str(lifecycle_bundle.get("trade_id") or trade_dir.name),
        "day": str(lifecycle_bundle.get("day") or trade_dir.parent.name),
        "symbol": str(lifecycle_bundle.get("symbol") or ""),
        "story_type": story_type,
        "lifecycle_status": str(lifecycle_bundle.get("trade_lifecycle_status") or lifecycle_bundle.get("status") or ""),
        "closed_trade": closed_trade,
        "loss_trade": bool(return_pct is not None and return_pct < 0),
        "return_pct": return_pct,
        "hold_duration": str(holding_evidence.get("hold_duration") or ""),
        "hold_duration_sec": holding_evidence.get("hold_duration_sec"),
        "holding_evidence_thin": holding_evidence_thin,
        "holding_phase_summary": holding_phase_summary,
        "hold_events_count": hold_events_count,
        "monitor_context_snapshots_count": len(monitor_context_snapshots),
        "same_day_linkage_status": str(same_day_linkage.get("status") or ""),
        "same_day_linkage_reason": str(same_day_linkage.get("linkage_reason") or ""),
        "same_day_linkage_missing": same_day_linkage_missing,
        "execution_fields_missing": execution_missing_fields,
        "execution_missing_fields_count": len(execution_missing_fields),
        "ai_trade_report_llm_response_exists": ai_trade_report_llm_exists,
        "ai_trade_report_status": ai_status,
        "closed_trade_report_generation_regression": facade._is_closed_trade_report_generation_regression(
            closed_trade=closed_trade,
            ai_trade_report_llm_exists=ai_trade_report_llm_exists,
            ai_status=ai_status,
        ),
        "closed_trade_decision_only_misclassification": bool(closed_trade and story_type == "decision_only"),
        "report_generation_state_path": str(generation_state_path),
        "lifecycle_bundle_path": str(lifecycle_path),
    }
    return row
